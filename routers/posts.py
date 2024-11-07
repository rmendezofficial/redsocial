from fastapi import FastAPI,HTTPException,Depends,status, APIRouter,Request
from pydantic import BaseModel
from typing import Annotated
import models
from database import engine,SessionLocal,Base
from sqlalchemy.orm import Session
import os
from database import database_db
from models import Users,Posts,Saved,Likes,Comments,Followers
from sqlalchemy import func
import random
from .authentication import current_user, User
from io import BytesIO
from PIL import Image


router=APIRouter(prefix='/posts',responses={404:{'message':'No encontrado'}})

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
#crear post y eliminar post
def getlastpost(user_id,db):
    latest_post = db.query(models.Posts).filter(models.Posts.user_id == user_id).order_by(models.Posts.date.desc()).first()
    return latest_post



class PostBase(BaseModel):
    name:str
    description:str
    user_id:int
    photo:str


@router.post('/create_post',status_code=status.HTTP_201_CREATED)
async def create_post(request:Request,post:PostBase,db:Session=Depends(get_db),user:User=Depends(current_user)):
    post_db=models.Posts(**post.model_dump())
    user=db.query(Users).filter(Users.id==post_db.user_id).first()
    csrf_token_db=user.token
    csrf_token_req=request.cookies.get('csrf_token')
    if csrf_token_db==csrf_token_req:
        
            
        db.add(post_db)
        db.commit()
    return {'message':'CSRF FAILED'}
    
@router.delete('/delete_post/{post_id}',status_code=status.HTTP_200_OK)
async def delete_post(request:Request,post_id:int,db:Session=Depends(get_db),user:User=Depends(current_user)):
    post_db=db.query(models.Posts).filter(Posts.id==post_id).first()
    user=db.query(Users).filter(Users.id==post_db.user_id).first()
    csrf_token_db=user.token
    csrf_token_req=request.cookies.get('csrf_token')
    if csrf_token_db==csrf_token_req:  
        db.delete(post_db)
        db.commit()
    return {'message':'CSRF FAILED'}
    
@router.get('/get_post/{post_id}',status_code=status.HTTP_200_OK)
async def get_post(post_id:int,db:Session=Depends(get_db)):
    post_db=db.query(Posts).filter(Posts.id==post_id).first()
    user=db.query(Users).filter(Users.id==post_db.user_id).first()
    comments=list(db.query(Comments).filter(Comments.post_id==post_db.id))
    likes=list(db.query(Likes).filter(Likes.post_id==post_db.id))
    likes_num=len(likes)
    
    comments_final=[]
    for c in comments:
        user=db.query(Users).filter(Users.id==c.user_id).first()
        new_comment={'comment':c.comment,'id':c.id,'user_id':c.user_id,'username':user.username}
        comments_final.append(new_comment)
    post_req={
        'name':post_db.name,
        'description':post_db.description,
        'photo':post_db.photo,
        'user_id':post_db.user_id,
        'username':user.username,
        'comments':comments_final,
        'comments_num':len(comments),
        'likes':likes_num,
        'likes_db':likes
    }
    return post_req

def getlastpost(user_id, db):
    latest_post = db.query(models.Posts).filter(models.Posts.user_id == user_id).order_by(models.Posts.date.desc()).first()
    return latest_post     

@router.post('/home', status_code=status.HTTP_200_OK)
async def get_posts_home(user_id: int, db: Session = Depends(get_db)):
    followed_by_user = list(db.query(Followers).filter(Followers.follower_id == user_id))  # ids de quienes el user sigue
    posts = []
    users = []
    
    if len(followed_by_user) == 0:
        random_posts = db.query(models.Posts).order_by(func.random()).limit(20).all()
        posts_final = []
        for p in random_posts:
            user = db.query(Users).filter(Users.id == p.user_id).first()
            new_post = {
                'name': p.name,
                'description': p.description,
                'photo': p.photo,
                'username': user.username,
                'user_id': user.id,
                'id': p.id
            }
            posts_final.append(new_post)
        return posts_final
    
    if len(followed_by_user) >= 20:
        followed_by_user_limited = random.sample(followed_by_user, 20)
        for i in followed_by_user_limited:
            user = i.followed_id
            users.append(user)
        for x in users:
            post = getlastpost(x, db)
            if post:  # Asegurarse de que el post no es None
                posts.append(post)
                
        posts_final = []
        for p in posts:
            user = db.query(Users).filter(Users.id == p.user_id).first()
            new_post = {
                'name': p.name,
                'description': p.description,
                'photo': p.photo,
                'username': user.username,
                'user_id': user.id,
                'id': p.id
            }
            posts_final.append(new_post)
        
        return posts_final
    
    for i in followed_by_user:
        user = i.followed_id
        users.append(user)
    for x in users:
        post = getlastpost(x, db)
        if post:  # Asegurarse de que el post no es None
            posts.append(post)
            
    posts_final = []
    for p in posts:
        user = db.query(Users).filter(Users.id == p.user_id).first()
        new_post = {
            'name': p.name,
            'description': p.description,
            'photo': p.photo,
            'username': user.username,
            'user_id': user.id,
            'id': p.id
        }
        posts_final.append(new_post)
    
    return posts_final

    
@router.get('/search_home',status_code=status.HTTP_200_OK)
async def get_random_posts(db: Session = Depends(get_db)):
    random_posts = db.query(models.Posts).order_by(func.random()).limit(20).all()
    return random_posts

