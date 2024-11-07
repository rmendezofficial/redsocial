from fastapi import FastAPI,HTTPException,Depends,status
from pydantic import BaseModel
from typing import Annotated
import models
from database import engine,SessionLocal,Base
from sqlalchemy.orm import Session
import os
from database import database_db
from routers import comments,likes,posts,saves,users,followers,authentication
from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost:3000",  # origen de tu frontend
]

app=FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Permite solicitudes desde los orígenes especificados
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permite todos los encabezados
)


app.include_router(users.router)
app.include_router(comments.router)
app.include_router(likes.router)
app.include_router(posts.router)
app.include_router(saves.router)
app.include_router(followers.router)
app.include_router(authentication.router)


Base.metadata.create_all(bind=engine)
    

    

