from fastapi import FastAPI,HTTPException,Depends,status, APIRouter,Request
from pydantic import BaseModel
from typing import Annotated
import models
from database import engine,SessionLocal,Base
from sqlalchemy.orm import Session
import os
from database import database_db
from models import Users,Posts,Saved,Likes,Comments,Followers
from .authentication import User,current_user

router=APIRouter(prefix='/likes',responses={404:{'message':'No encontrado'}})

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
class LikeBase(BaseModel):
    user_id:int
    post_id:int 

@router.post('/create_like',status_code=status.HTTP_201_CREATED)
async def create_like(request:Request,like:LikeBase,db:Session=Depends(get_db),user_auth:User=Depends(current_user)):
    like_db=models.Likes(**like.model_dump())
    user=db.query(Users).filter(Users.id==like_db.user_id).first()
    csrf_token_db=user.token
    csrf_token_req=request.cookies.get('csrf_token')
    if csrf_token_db==csrf_token_req:
        db.add(like_db)
        db.commit()
    return {'message':'CSRF FAILED'}
    
@router.post('/delete_like',status_code=status.HTTP_200_OK)
async def delete_like(request:Request,like:LikeBase,db:Session=Depends(get_db),user_auth:User=Depends(current_user)):
    like_db=db.query(models.Likes).filter(models.Likes.user_id==like.user_id,Likes.post_id==like.post_id).first()
    user=db.query(Users).filter(Users.id==like_db.user_id).first()
    csrf_token_db=user.token
    csrf_token_req=request.cookies.get('csrf_token')
    if csrf_token_db==csrf_token_req:
        db.delete(like_db)
        db.commit()
    return {'message':'CSRF FAILED'}