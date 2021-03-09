from datetime import timedelta, datetime
from passlib.context import CryptContext
from jose import JWTError, jwt
from pydantic import BaseModel
from typing import Optional

from DataAccessLayer.schemas import User

SECRET_KEY="df9f9a50d72c72b24bc8fd5af24fb70d0ad090c84070b9410ae32eb3fb75b285"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES= 15 

pwd_context=CryptContext(schemes=["bcrypt"], deprecated="auto")

class Token(BaseModel):
    token_type: str
    access_token: str

class TokenData(BaseModel):
    username: Optional[str] = None

def hash_password(password):
    return pwd_context.hash(password)

async def verify_hashed_password(password, hashed_password):
    print(password)
    print(hashed_password)
    return pwd_context.verify(password, hashed_password)

def create_access_token(data:dict, expires_delta: Optional[timedelta]= None):
    to_encode= data.copy()
    if expires_delta:
        expire=datetime.utcnow()+ expires_delta
    else:
        expire=datetime.utcnow()+timedelta(minutes=15)
    to_encode.update({"exp":expire})
    encode_jwt=jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encode_jwt
