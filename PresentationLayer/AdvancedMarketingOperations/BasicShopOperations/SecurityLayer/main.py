from fastapi import FastAPI, Depends, HTTPException, status
from DataAccessLayer import crud, models, schemas, database

from sqlalchemy.orm import Session
from typing import List

import handling_users
import handling_passwords
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta, datetime

from jose import JWTError, jwt
from passlib.context import CryptContext

models.Base.metadata.create_all(bind=database.engine)

app=FastAPI()

oauth2_scheme= OAuth2PasswordBearer(tokenUrl="token")

def get_db():
    db=database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_user(email: str, password: str, db: Session=Depends(get_db)):
    return crud.get_user_by_mail(db, email)
    

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserBase, db: Session= Depends(get_db)):
    user=handling_users.register_new_user(user)
    return crud.create_user(db=db, user=user)

@app.post("/admin/products/", response_model=schemas.Product)
def create_product(product: schemas.Product, db:Session=Depends(get_db)):
    return crud.create_product(db=db,product=product,shop_id=1)

@app.get("/users/{user_id}", response_model=schemas.User)
def get_user_by_id(user_id: int, db: Session= Depends(get_db)):
    db_user= crud.get_user(db, user_id= user_id)
    return db_user

@app.get("/products/", response_model=List[schemas.Product])
def get_all_products(db:Session= Depends(get_db)):
    return crud.get_all_products(db)

@app.get("/admin/users/", response_model=List[schemas.User])
def get_all_users(db:Session=Depends(get_db)):
    db_users=crud.get_users(db)
    return db_users

@app.post("/token", response_model=handling_passwords.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session=Depends(get_db)):
    #user = handling_users.authenticate_user(form_data.username, form_data.password)
    user=crud.get_user_by_mail(db, form_data.username)

    if not user:
        return False
    if not handling_passwords.verify_hashed_password(user.password, form_data.password):
        return False

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=handling_passwords.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = handling_passwords.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

#i have it there just to have an option to autorize using swagger UI
@app.get("/nothing/")
async def nothing(token: str = Depends(oauth2_scheme)):
    pass
