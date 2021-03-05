from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import Depends

from DataAccessLayer.models import User as mUser
from DataAccessLayer.schemas import User as User
from DataAccessLayer import crud

from . import handling_passwords

oauth2_scheme= OAuth2PasswordBearer(tokenUrl="token")

def authenticate_user(database, username: str, password: str):
    print(password)
    user=crud.get_user_by_mail(database, username)
    print(user.password)
    if not user:
        return False
    if not handling_passwords.verify_hashed_password(user.password, password):
        return False
    return user

async def get_current_user(token: str=Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user_by_mail( username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

def register_new_user(user):
    user.password= handling_passwords.hash_password(user.password)
    print(user.password)
    return user
