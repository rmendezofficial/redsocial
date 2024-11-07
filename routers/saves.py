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


router=APIRouter(prefix='/saves',responses={404:{'message':'No encontrado'}})

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

class SavedBase(BaseModel):
    user_id:int
    post_id:int 

@router.post('/create_saved',status_code=status.HTTP_201_CREATED)
async def create_saved(request:Request,saved:SavedBase,db:Session=Depends(get_db),user:User=Depends(current_user)):
    saved_db=models.Saved(**saved.model_dump())
    user=db.query(Users).filter(Users.id==saved_db.user_id).first()
    csrf_token_db=user.token
    csrf_token_req=request.cookies.get('csrf_token')
    if csrf_token_db==csrf_token_req:
        db.add(saved_db)
        db.commit()
    return {'message':'CSRF FAILED'}
    
@router.delete('/delete_saved/{saved_id}',status_code=status.HTTP_200_OK)
async def delete_saved(request:Request,saved_id:int,db:Session=Depends(get_db),user:User=Depends(current_user)):
    saved_db=db.query(models.Saved).filter(models.Saved.id==saved_id).first()
    user=db.query(Users).filter(Users.id==saved_db.user_id).first()
    csrf_token_db=user.token
    csrf_token_req=request.cookies.get('csrf_token')
    if csrf_token_db==csrf_token_req:    
        db.delete(saved_db)
        db.commit()
    return {'message':'CSRF FAILED'}