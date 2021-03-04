from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float
from sqlalchemy.orm import relationship

from .database import Base

class User(Base):
    __tablename__="users"

    id= Column(Integer, unique=True, primary_key=True)
    name= Column(String, index=True)
    surname= Column(String, index=True)
    email= Column(String, unique=True, index=True) #username
    wallet= Column(Float, index=True)
    #I've added this
    password=Column(String,index=True)

    user= relationship("Product", back_populates="products")
    owner= relationship("Order", back_populates="orders")

class Product(Base):
    __tablename__="products"

    id= Column(Integer, unique=True, primary_key=True)
    name= Column(String, unique=True, index=True)
    description= Column(String, index=True)
    number=Column(Integer)
    price= Column(Float)

    user_id= Column(Integer, ForeignKey("users.id"))

    products= relationship("User", back_populates="user")

class Order(Base):
    __tablename__="orders"

    id=Column(Integer, unique=True, primary_key=True)

    isFinished=Column(Boolean, index=True)
    items=Column(String,index=True) #it is JSON product.id: number

    user_id= Column(Integer, ForeignKey("users.id"))

    orders= relationship("User", back_populates="owner")





