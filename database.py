from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
from databases import Database


#URL_DATABASE=os.getenv("DATABASE_URL") al desplegar, para q se conecte a la base postgre
URL_DATABASE='mysql+pymysql://root:111ricardo mendez@localhost:3306/redsocialdb8'

engine=create_engine(URL_DATABASE)

SessionLocal=sessionmaker(autocommit=False,autoflush=False,bind=engine)

Base=declarative_base()

database_db = Database(URL_DATABASE)
