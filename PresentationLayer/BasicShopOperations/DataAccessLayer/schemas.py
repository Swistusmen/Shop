from typing import List, Optional
from pydantic import BaseModel

class ProductBase(BaseModel):
    name: str
    description: str
    number: int
    price: float

class Product(ProductBase):
    id: int

    class Config:
        orm_mode= True

class OrderBase(BaseModel):
    isFinished: bool
    products: str

class Order(BaseModel):
    owner_id: int

    class Config:
        orm_mode=True

class UserBase(BaseModel):
    name: str
    surname: str
    email: str
    is_disabled: bool
    wallet: float
    
class UserCreate(UserBase):
    password: str
    is_admin: bool
  

class User(UserBase):
    id: int
    items: List[Product]=[]

    class Config:
        orm_mode=True

class UserHistory(UserBase):
    id: int
    orders: List[Order]=[]

    