from DataAccessLayer.models import User as mUser
from DataAccessLayer.schemas import User as User
from DataAccessLayer import crud

import json

def increment_number_of_products(product_id: int, cookie:dict):
    if product_id not in cookie.keys():
        cookie[product_id]=1
    else:
        cookie[product_id]+=1
    return cookie

def decrement_number_of_products(product_id:int, cookie: dict):
    if product_id not in cookie.keys():
        return cookie
    if cookie[product_id]==1:
        cookie.pop(product_id)
        return cookie
    cookie[product_id]-=1
    return cookie

def add_credits_to_the_wallet(database, user_id:int, amount_of_money:float):
    user=crud.get_user(database,user_id)
    new_value=user.wallet+amount_of_money
    return crud.update_wallet(database,user_id,new_value)

def substract_credits_from_the_wallet(database, user_id:int, amount_of_money:float):
    user=crud.get_user(database,user_id)
    if(user.wallet<amount_of_money):
        return False
    new_value=user.wallet-amount_of_money
    return crud.update_wallet(database,user_id,new_value)

def create_and_save_order(database, user_id:int, cookie:dict):
    bucket=schemas.Order(isFinished=True, products=json.dumps(cookie),owner_id=user_id)
    return crud.create_order(database,bucket)
    
def pay_for_the_bucket(database, user_id:int, order_id:int):




def get_my_orders()

