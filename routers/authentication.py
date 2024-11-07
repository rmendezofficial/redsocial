from fastapi import FastAPI,Depends,HTTPException,status,APIRouter
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from jose import jwt,JWTError
from passlib.context import CryptContext
from datetime import datetime,timedelta,timezone
from database import engine,SessionLocal,Base
from database import database_db
from sqlalchemy.orm import Session
from models import Users,Posts,Saved,Likes,Comments,Followers
from fastapi.responses import JSONResponse
import secrets


ALGORITHM='HS256'
ACCESS_TOKEN_DURATION=180
SECRET='201d573bd73bd7d1344d3a3bfce1550b69102fd11be3db6d379508b6cccc58ea230b'
crypt = CryptContext(schemes=['bcrypt'])


router=APIRouter(prefix='/auth',responses={404:{'message':'No encontrado'}})

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()
        

oauth2=OAuth2PasswordBearer(tokenUrl='login')

crypt=CryptContext(schemes=['bcrypt'])

class User(BaseModel):
    username:str
    email:str
    disabled:bool
    
class UserDB(User):
    password:str
    

#funciones de search user

def create_csrf_token():
    # Genera un token seguro aleatorio de 32 bytes (256 bits)
    return secrets.token_urlsafe(32)

async def auth_user(token: str = Depends(oauth2), db: Session = Depends(get_db)):
    exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
    )
    try:
        # Decodifica el token
        usernamedeco = jwt.decode(token, SECRET, algorithms=[ALGORITHM]).get('sub')
        if usernamedeco is None:
            raise exception
        # Busca al usuario en la base de datos
        user_dbdeco=db.query(Users).filter(Users.username==usernamedeco).first()
        if user_dbdeco is None:
            raise exception
        return user_dbdeco
    except JWTError:
        raise exception


# Verifica si el usuario está activo
async def current_user(user: Users = Depends(auth_user)):
    if user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Inactive user',
        )
    return user

@router.post('/login')
async def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user_db = db.query(Users).filter(Users.username == form.username).first()
    if not user_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='Incorrect user'
        )
    if not crypt.verify(form.password, user_db.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='Incorrect password'
        )
    
    # Genera el token con expiración
    expiration_time = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_DURATION)  # Usando timezone.utc
    access_token = {
        'sub': user_db.username,
        'exp': expiration_time  # Establecer 'exp' en el payload del token
    }
    access_token_final = jwt.encode(access_token, SECRET, algorithm=ALGORITHM)
    csrf_token_final = create_csrf_token()
    user_info={"username":user_db.username,"email":user_db.email,"id":user_db.id}

    response = JSONResponse(content={"message": "Login successful",'access_token': access_token_final, 'token_type': 'bearer','csrf_token':csrf_token_final,'user_info':user_info})

    user_db.token=csrf_token_final
    db.commit()
    # Establecer la cookie del token CSRF con las configuraciones de seguridad necesarias
    response.set_cookie(
        key="csrf_token",
        value=csrf_token_final,
        httponly=True,       # Permitir acceso desde JavaScript
        secure=True,          # Requiere HTTPS    # Solo permite solicitudes desde el mismo sitio
                                # Tiempo de vida de la cookie en segundos (ej. 30 min)
    )
    
    
    return response




@router.get('/me')
async def me(user:User=Depends(current_user)):
    
    return user

@router.get("/logout")
async def logout(response: JSONResponse):
    # Elimina las cookies del access token y refresh token
    response.delete_cookie("access_token")
    response.delete_cookie("csrf_token")
    
    return {"message": "Logout successful"}