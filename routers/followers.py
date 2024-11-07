from fastapi import FastAPI,HTTPException,Depends,status, APIRouter,Request
from pydantic import BaseModel, EmailStr
from typing import Annotated
import models
from database import engine,SessionLocal,Base
from sqlalchemy.orm import Session
import os
from database import database_db
from models import Users,Posts,Saved,Likes,Comments,Followers
from .authentication import User,current_user

router=APIRouter(prefix='/followers',responses={404:{'message':'No encontrado'}})

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

class FollowBase(BaseModel):
    follower_id:int
    followed_id:int 

@router.post('/create_follow',status_code=status.HTTP_201_CREATED)
async def create_follow(request:Request,follow:FollowBase,db:Session=Depends(get_db),user_auth:User=Depends(current_user)):
    user=db.query(Users).filter(Users.id==follow.follower_id).first()
    csrf_token_db=user.token
    csrf_token_req=request.cookies.get('csrf_token')
    if csrf_token_db==csrf_token_req:
        follow_db=models.Followers(**follow.model_dump())
        db.add(follow_db)
        db.commit()
    return {'message':'CSRF FAILED'}
        
@router.post('/delete_follow',status_code=status.HTTP_200_OK)
async def delete_follow(request:Request,follow:FollowBase,db:Session=Depends(get_db),user_auth:User=Depends(current_user)):
    follow_db=db.query(models.Followers).filter(models.Followers.follower_id==follow.follower_id,Followers.followed_id==follow.followed_id).first()
    user=db.query(Users).filter(Users.id==follow.follower_id).first()
    csrf_token_db=user.token
    csrf_token_req=request.cookies.get('csrf_token')
    if csrf_token_db==csrf_token_req:
        db.delete(follow_db)
        db.commit()
    return {'message':'CSRF FAILED'}