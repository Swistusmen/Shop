from fastapi import FastAPI, Depends, HTTPException, status, Response, Cookie
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.requests import Request
from DataAccessLayer import crud, models, schemas, database


from sqlalchemy.orm import Session
from typing import List, Optional


from SecurityLayer import handling_passwords as hp
from SecurityLayer import handling_users as hs

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta, datetime

from jose import JWTError, jwt
from passlib.context import CryptContext

from starlette.requests import Request
from starlette.responses import Response

import json

from ClientOperations.client_operations import add_credits_to_the_wallet, realese_order

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
def create_user(user: schemas.UserCreate, db: Session= Depends(get_db)):
    user=hs.register_new_user(user)
    return crud.create_user(db=db, user=user)
'''
@app.get("/users/{user_id}", response_model=schemas.User)
def get_user_by_id(user_id: int, db: Session= Depends(get_db)):
    db_user= crud.get_user(db, user_id= user_id)
    return db_user
'''
@app.get("/products/", response_model=List[schemas.Product])
def get_all_products(db:Session= Depends(get_db)):
    return crud.get_all_products(db)

@app.post("/token", response_model=hp.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session=Depends(get_db)):
    user=crud.get_user_by_mail(db, form_data.username)

    if not user:
        return False
    if not hp.verify_hashed_password(user.password, form_data.password):
        return False
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=hp.ACCESS_TOKEN_EXPIRE_MINUTES)
   
    access_token = hp.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/product/{product_id}")
async def add_product_to_the_basket(response: Response, request: Request,product_id:int, db: Session=Depends(get_db)):
    bucket=request.cookies.get("bucket")
    if bucket is None:
        new_item={}
        new_item[product_id]=1
        response.set_cookie(key="bucket", value=new_item)
    else:
        bucket=transform_string_to_dictionary(bucket)
        if product_id in bucket.keys():
            bucket[product_id]+=1
        else:
            bucket[product_id]=1
        #print(bucket)
        response.set_cookie(key="bucket", value=bucket)

@app.post("/product/bucket/{product_id}")
async def remove_product_to_the_basket(response: Response, request: Request,product_id:int, db: Session=Depends(get_db)):
    bucket=request.cookies.get("bucket")
    if bucket is None:
        pass
    bucket=transform_string_to_dictionary(bucket)
    if product_id in bucket.keys():
        bucket[product_id]-=1
        if bucket[product_id]==0:
            bucket.pop(product_id)
        response.set_cookie(key="bucket", value=bucket)

@app.post("/account/wallet/")
async def add_money_to_account(income:float,db:Session=Depends(get_db), current_user: schemas.User=Depends(hs.get_current_user)):
    add_credits_to_the_wallet(db,current_user.id,income)
    my_user=crud.get_user(db,current_user.id)
    print(my_user.wallet)

def transform_string_to_dictionary(cookie:str):
    cookie=cookie[:-1]
    cookie=cookie[1:]
    new_dictionary=cookie.split(",")
    my_dict={}
    for i in new_dictionary:
        a=i.split(":")
        a[0]=int(a[0])
        a[1]=int(a[1])
        my_dict[a[0]]=a[1]
    return my_dict
'''
@app.get("/users/me/", response_model=schemas.User)
async def get_me(current_user: schemas.User=Depends(hs.get_current_user)):
    return current_user
'''
@app.post("/bucket/payment/")
async def make_a_payment(response: Response,request: Request,db:Session=Depends(get_db),current_user: schemas.User=Depends(hs.get_current_user)):
    cookie=request.cookies.get("bucket")
    cookie=transform_string_to_dictionary(cookie)
    realese_order(db, current_user.id,cookie,1)
    response.set_cookie(key="bucket", value="")

@app.post("/admin/accounts/modify/{user_id}/is_administrator")
async def change_account_admin_settings(user_id:int,admin_priviliges: bool,db:Session=Depends(get_db),current_user: schemas.User=Depends(hs.get_current_user)):
    if current_user.is_admin==True:
        print(admin_priviliges)
        user=crud.update_admin(db,user_id,admin_priviliges)

@app.get("/admin/users/", response_model=List[schemas.UserCreate])
def get_all_users(db:Session=Depends(get_db),current_user: schemas.UserCreate=Depends(hs.get_current_user_admin)):
    if current_user.is_admin==True:
        db_users=crud.get_users(db)
        return db_users

@app.post("/admin/products/", response_model=schemas.Product)
def create_product(product: schemas.Product, db:Session=Depends(get_db),current_user: schemas.UserCreate=Depends(hs.get_current_user_admin)):
    if current_user.is_admin==True:
        return crud.create_product(db=db,product=product,shop_id=1)

@app.post("/admin/products/change_number", response_model=schemas.Product)
def create_product(product_id: int, number:int,db:Session=Depends(get_db),current_user: schemas.UserCreate=Depends(hs.get_current_user_admin)):
    if current_user.is_admin==True:
        product=crud.get_product(db,product_id)
        if product is None:
            return None
        return crud.change_number_of_product(db, product,number)

@app.post("/admin/products/change_price", response_model=schemas.Product)
def create_product(product_id: int, price:float,db:Session=Depends(get_db),current_user: schemas.UserCreate=Depends(hs.get_current_user_admin)):
    if current_user.is_admin==True:
        product=crud.get_product(db,product_id)
        if product is None:
            return None
        return crud.change_price_of_product(db, product,price)

#TODO- add function which return current user after login -#DONE
#TODO- create function for payment #DONE
#TODO- admin module DONE
#- change prive DONE
#- change number of product DONE
#- authenticate if it is admin DONE
#- add product DONE
#TODO- better locations of every endpoint #DONE
#TODO- add pagination
#- all products
#- a few products
#TODO- add advisory basing on other purchases
#TODO- story of purchases
#- get stroy of purchases
#- parse it to the proper form
#- process it
# backend over
#TODO- add frontend

        

    


