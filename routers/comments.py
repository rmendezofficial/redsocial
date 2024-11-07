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

router=APIRouter(prefix='/comments',responses={404:{'message':'No encontrado'}})

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()
        

class CommentBase(BaseModel):
    user_id:int
    post_id:int
    comment:str
    
class CommentBasePut(BaseModel):
    comment:str

@router.post('/create_comment',status_code=status.HTTP_201_CREATED)
async def create_comment(request:Request,comment:CommentBase,db:Session=Depends(get_db),user_auth:User=Depends(current_user)):
    user=db.query(Users).filter(Users.id==comment.user_id).first()
    csrf_token_db=user.token
    csrf_token_req=request.cookies.get('csrf_token')
    if csrf_token_db==csrf_token_req:
        comment_db=models.Comments(**comment.model_dump())
        db.add(comment_db)
        db.commit()
    else:
        return {'message':'CSRF FAILED'}
    
@router.delete('/delete_comment/{comment_id}',status_code=status.HTTP_200_OK)
async def delete_comment(request:Request,comment_id:int,db:Session=Depends(get_db),user_auth:User=Depends(current_user)):
    comment_db=db.query(models.Comments).filter(models.Comments.id==comment_id).first()    
    user=db.query(Users).filter(Users.id==comment_db.user_id).first()
    csrf_token_db=user.token
    csrf_token_req=request.cookies.get('csrf_token')
    if csrf_token_db==csrf_token_req:
        db.delete(comment_db)
        db.commit()
    return {'message':'CSRF FAILED'}
    
@router.put('/update_comment/',status_code=status.HTTP_200_OK)
async def update_comment(request:Request,comment:CommentBasePut,db:Session=Depends(get_db),user_auth:User=Depends(current_user)):
    user=db.query(Users).filter(Users.id==comment.user_id).first()
    csrf_token_db=user.token
    csrf_token_req=request.cookies.get('csrf_token')
    if csrf_token_db==csrf_token_req:
        comment_id=comment.id
        new_comment_db=CommentBase(comment.model_dump())
        comment_db_old=db.query(models.Comments).filter(models.Comments.id==comment_id).first()
        comment_db_old.comment=new_comment_db.comment
        db.commit()
    return {'message':'CSRF FAILED'}