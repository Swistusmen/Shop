from fastapi import FastAPI, Depends, HTTPException, status, Response, Cookie
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.requests import Request
from DataAccessLayer import crud, models, schemas, database

from sqlalchemy.orm import Session
from typing import List, Optional

from Importer import export

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
import os

files= os.listdir()
isDatabaseEmpty=False
if database.db_name not in files:
    isDatabaseEmpty=True

models.Base.metadata.create_all(bind=database.engine)

if isDatabaseEmpty== True:
    user=schemas.UserCreate(email="root", password="password", name="name", surname="surname", is_admin=True, is_disabled=True, wallet=0)
    user=hs.register_new_user(user)
    db=database.SessionLocal()
    crud.create_user(db=db, user=user)
    crud.update_admin(db,1,True)
    db.close()

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

@app.get("/export/users")
def test(db: Session= Depends(get_db)):
    export.export_users(db)

@app.get("/export/products")
def test(db: Session= Depends(get_db)):
    export.export_products(db)

@app.get("/export/orders")
def test(db: Session= Depends(get_db)):
    export.export_orders(db)

@app.get("/products/all/", response_model=List[schemas.Product])
def get_all_products(db:Session= Depends(get_db)):
    return crud.get_all_products(db)

@app.get("/products/", response_model=List[schemas.Product])
def get_products(no_prod_on_site:int, page:int,db:Session= Depends(get_db)):
    list_of_products=crud.get_all_products(db)
    my_list=[]
    for i in range ((page-1)*no_prod_on_site,no_prod_on_site*page):
        try:
            my_list.append(list_of_products[i]) 
        except:
            break
    return my_list

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

@app.get("/account/me/")
async def check_myself(db:Session=Depends(get_db), current_user: schemas.User=Depends(hs.get_current_user)):
    if current_user is not None:
        return crud.get_user(db,current_user.id)

@app.get("/account/me/change_password")
async def change_password(password:str,db:Session=Depends(get_db), current_user: schemas.User=Depends(hs.get_current_user)):
    if current_user is not None:
        return crud.update_password(db,current_user.id, password)

@app.get("/account/me/change_username")
async def change_mail(username:str,db:Session=Depends(get_db), current_user: schemas.User=Depends(hs.get_current_user)):
    if current_user is not None:
        return crud.update_mail(db,current_user.id, username)

@app.get("/account/orders/")
async def get_all_orders(db:Session=Depends(get_db),current_user: schemas.User=Depends(hs.get_current_user)):
    if current_user is not None:
        return crud.get_orders_by_user(db,current_user.id)

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
def get_all_users(db:Session=Depends(get_db),current_user: schemas.UserCreate=Depends(hs.get_current_user)):
    if current_user.is_admin==True:
        db_users=crud.get_users(db)
        return db_users

@app.post("/admin/products/", response_model=schemas.Product)
def create_product(product: schemas.Product, db:Session=Depends(get_db),current_user: schemas.UserCreate=Depends(hs.get_current_user)):
    if current_user.is_admin==True:
        return crud.create_product(db=db,product=product,shop_id=1)

@app.post("/admin/products/change_number", response_model=schemas.Product)
def create_product(product_id: int, number:int,db:Session=Depends(get_db),current_user: schemas.UserCreate=Depends(hs.get_current_user)):
    if current_user.is_admin==True:
        product=crud.get_product(db,product_id)
        if product is None:
            return None
        return crud.change_number_of_product(db, product,number)

@app.post("/admin/products/change_price", response_model=schemas.Product)
def create_product(product_id: int, price:float,db:Session=Depends(get_db),current_user: schemas.UserCreate=Depends(hs.get_current_user)):
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
#TODO- add pagination DONE
#- all products DONE
#- a few products DONE
#TODO available products
#TODO- change username and password DONE
#TODO- add starting admin account -DONE
#TODO- add advisory basing on other purchases
#TODO- story of purchases
#- get stroy of purchases #DONE
#- parse it to the proper form #DONE
#- process it
#- add categories in database
#TODO - import export- excel- database
#TODO - tests
# backend over
#TODO- add frontend

        

    


