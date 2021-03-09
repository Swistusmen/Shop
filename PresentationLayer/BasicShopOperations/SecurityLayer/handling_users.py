from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import Depends, HTTPException

from DataAccessLayer.models import User as mUser
from DataAccessLayer.schemas import User as User
from DataAccessLayer import crud

from jose import JWTError, jwt
from sqlalchemy.orm import Session

from . import handling_passwords as hp
from DataAccessLayer import database

oauth2_scheme= OAuth2PasswordBearer(tokenUrl="token")

def get_db():
    db=database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

def authenticate_user(database, username: str, password: str):
    print(password)
    user=crud.get_user_by_mail(database, username)
    print(user.password)
    if not user:
        return False
    if not hp.verify_hashed_password(user.password, password):
        return False
    return user

async def get_current_user(db:Session=Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, hp.SECRET_KEY, algorithms=[hp.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = hp.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_mail( db,user_email=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_user_admin(db:Session=Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, hp.SECRET_KEY, algorithms=[hp.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = hp.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_mail_admin( db,user_email=token_data.username)
    if user is None:
        raise credentials_exception
    return user

def register_new_user(user):
    user.password= hp.hash_password(user.password)
    print(user.password)
    return user
