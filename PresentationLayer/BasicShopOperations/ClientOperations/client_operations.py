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
    
def decrease_number_of_product_in_shop(database, product_id: int, substract_this_number:int):
    product= crud.get_product(database,product_id)
    new_number=product.number-substract_this_number
    return crud.change_number_of_product(database,product, new_number)

def take_money_from_client_to_the_shop(database, client_id:int, shop_id:int, money:float):
    if (substract_credits_from_the_wallet(database,client_id,money)!=False):
        add_credits_to_the_wallet(database,shop_id,money)

def check_product_availability(database, cookie_product:tuple):
    product=crud.get_product(database,cookie_product[0])
    return [cookie_product[0],product.number-cookie_product[1], cookie_product[1]*product.price]

def check_user_wallet(database, user_id:int, money:float):
    user=crud.get_user(database,user_id)
    return user.wallet-money

def realese_order(database, user_id:int, cookie: dict,shop_id:int):
    total_price=0.0
    for i in cookie:
        result=check_product_availability(database, i)
        if result[1]<0:
            return result
        total_price+=result[2]
    money_in_user_waller_after_buying=check_user_wallet(database,user_id,total_price)
    if money_in_user_waller_after_buying<0.0:
        return money_in_user_waller_after_buying
    take_money_from_client_to_the_shop(database,user_id,shop_id, total_price)
    for i in cookie.items():
        decrease_number_of_product_in_shop(database,cookie[0],cookie[1])
    create_and_save_order(database,user_id,cookie)
    
    









