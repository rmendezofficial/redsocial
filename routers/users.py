from fastapi import FastAPI,HTTPException,Depends,status, APIRouter,Request
from pydantic import BaseModel
from typing import Annotated
import models
from database import engine,SessionLocal,Base
from sqlalchemy.orm import Session
import os
from database import database_db
from models import Users,Posts,Saved,Likes,Comments,Followers
from .authentication import current_user, User
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from jose import jwt,JWTError
from passlib.context import CryptContext
from datetime import datetime,timedelta

ALGORITHM='HS256'
ACCESS_TOKEN_DURATION=1
SECRET='201d573bd73bd7d1344d3a3bfce1550b69102fd11be3db6d379508b6cccc58ea230b'
crypt = CryptContext(schemes=['bcrypt'])


router=APIRouter(prefix='/users',responses={404:{'message':'No encontrado'}})

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

class UserBase(BaseModel):
    username:str
    password:str
    email:str

class UserBasePut(BaseModel):
    username:str
    password:str
    email:str
    id:int

@router.post('/create_user',status_code=status.HTTP_201_CREATED)
async def create_user(user:UserBase,db:Session=Depends(get_db)):
    hashed_password = crypt.hash(user.password)
    user.password = hashed_password
    db_user = Users(**user.model_dump())
    db.add(db_user)
    db.commit()
    return {'message':'Success'}

@router.put('/update_user/',status_code=status.HTTP_200_OK)
async def update_user(request:Request,user:UserBasePut,db:Session=Depends(get_db),user_auth:User=Depends(current_user)):
    user_id=user.id
    user=db.query(models.Users).filter(models.Users.id==user_id).first()
    csrf_token_db=user.token
    csrf_token_req=request.cookies.get('csrf_token')
    if csrf_token_db==csrf_token_req:
        new_user_db=UserBase(**user.model_dump())
        user_db_old=db.query(models.Users).filter(models.Users.id==user_id).first()
        user_db_old.username=new_user_db.username
        user_db_old.password=new_user_db.password
        user_db_old.email=new_user_db.email
        db.commit()
    return {'message':'CSRF FAILED'}
    

@router.delete('/delete_user/{user_id}',status_code=status.HTTP_200_OK)
async def delete_user(request:Request,user_id:int,db:Session=Depends(get_db),user_auth:User=Depends(current_user)):
    user=db.query(models.Users).filter(models.Users.id==user_id).first()
    csrf_token_db=user.token
    csrf_token_req=request.cookies.get('csrf_token')
    if csrf_token_db==csrf_token_req:
        db.delete(user)
        db.commit()
    return {'message':'CSRF FAILED'}

@router.get('/get_user/{user_id}',status_code=status.HTTP_200_OK)
async def get_user(user_id:int,db:Session=Depends(get_db)):
    user=db.query(models.Users).filter(models.Users.id==user_id).first()
    posts=list(db.query(Posts).filter(Posts.user_id==user.id))
    following=list(db.query(Followers).filter(Followers.follower_id==user.id))
    followers=list(db.query(Followers).filter(Followers.followed_id==user.id))
    followers_final=[]
    for f in followers:
        userdb=db.query(Users).filter(Users.id==f.follower_id).first()
        new_follower={
            'follower_id':f.follower_id,
            'followed_id':f.followed_id,
            'follower_username':userdb.username
        }
        followers_final.append(new_follower)
    follows_final=[]
    for f in following:
        userdb=db.query(Users).filter(Users.id==f.followed_id).first()
        new_follow={
            'follower_id':f.follower_id,
            'followed_id':f.followed_id,
            'followed_username':userdb.username
        }
        follows_final.append(new_follow)
        
    
    user_final={
        'username':user.username,
        'user_id':user.id,
        'posts':posts,
        'followers':followers_final,
        'follows':follows_final,
        'followers_num':len(followers),
        'follows_num':len(following)
    }
    
    return user_final

@router.get('/search/{query}',status_code=status.HTTP_200_OK)
async def search_user(query:str,db:Session=Depends(get_db)):
    results=list(db.query(models.Users).filter(Users.username.ilike(f"%{query}%")))
    users_final=[]
    for user in results:
        new_user={
            'username':user.username,
            'user_id':user.id
        }
        users_final.append(new_user)
    return users_final


@router.post('/get_me',status_code=status.HTTP_200_OK)
async def get_me(user_id:int,request:Request,user_auth:User=Depends(current_user),db:Session=Depends(get_db)):
    user=db.query(Users).filter(Users.id==user_id).first()
    csrf_token_db=user.token
    csrf_token_req=request.cookies.get('csrf_token')
    if csrf_token_db==csrf_token_req:
        
        posts=list(db.query(Posts).filter(Posts.user_id==user.id))
        following=list(db.query(Followers).filter(Followers.follower_id==user.id))
        followers=list(db.query(Followers).filter(Followers.followed_id==user.id))
        followers_final=[]
        for f in followers:
            userdb=db.query(Users).filter(Users.id==f.follower_id).first()
            new_follower={
                'follower_id':f.follower_id,
                'followed_id':f.followed_id,
                'follower_username':userdb.username
            }
            followers_final.append(new_follower)
        follows_final=[]
        for f in following:
            userdb=db.query(Users).filter(Users.id==f.followed_id).first()
            new_follow={
                'follower_id':f.follower_id,
                'followed_id':f.followed_id,
                'followed_username':userdb.username
            }
            follows_final.append(new_follow)
            
        
        user_final={
            'username':user.username,
            'user_id':user.id,
            'posts':posts,
            'followers':followers_final,
            'follows':follows_final,
            'followers_num':len(followers),
            'follows_num':len(following)
        }
        
        return user_final
    return {'message':'CSRF FAILED'}

