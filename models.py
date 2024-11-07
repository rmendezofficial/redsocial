from sqlalchemy import Boolean,Column,Integer,String,DateTime,Text
from database import Base
from sqlalchemy.sql import func

class Users(Base):
    __tablename__='users'
    
    id=Column(Integer,primary_key=True,index=True)
    username=Column(String(50),unique=True)
    password=Column(String(200))
    email=Column(String(100))
    disabled=Column(Boolean,default=False)
    token=Column(String(200),default=None)
    
class Posts(Base):
    __tablename__='posts'
    
    id=Column(Integer,primary_key=True,index=True)
    name=Column(String(50))
    description=Column(String(200))
    user_id=Column(Integer)
    photo=Column(Text) 
    date=Column(DateTime, server_default=func.now())
    
class Comments(Base):
    __tablename__='comments'
    
    id=Column(Integer,primary_key=True,index=True)
    user_id=Column(Integer)
    post_id=Column(Integer)
    comment=Column(String(200))
    
class Likes(Base):
    __tablename__='likes'
    
    id=Column(Integer,primary_key=True,index=True)
    user_id=Column(Integer)
    post_id=Column(Integer)
    
class Saved(Base):
    __tablename__='saved'
    
    id=Column(Integer,primary_key=True,index=True)
    user_id=Column(Integer)
    post_id=Column(Integer)
    
class Followers(Base):
    __tablename__='followers'
    
    id=Column(Integer,primary_key=True,index=True)
    follower_id=Column(Integer)
    followed_id=Column(Integer)