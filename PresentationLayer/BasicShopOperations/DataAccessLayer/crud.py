from sqlalchemy.orm import Session
from .schemas import User, Product, Order, UserCreate
from .models import User as mUser
from .models import Product as mProduct
from .models import Order as mOrder

def get_user(db: Session, user_id:int):
    return db.query(mUser).filter(mUser.id==user_id).first()

def get_users(db:Session):
    return db.query(mUser).all()

def get_user_by_mail(db: Session, user_email: str):
    return db.query(mUser).filter(mUser.email==user_email).first()

def get_users_by_name(db: Session, user_name: str):
    return db.query(mUser).filter(mUser.name==user_name).all()

def get_users_by_surname(db: Session, user_surname: str):
    return db.query(mUser).filer(mUser.surname==user_surname).all()

def get_product_by_name(db: Session, product_name: str):
    return db.query(mProduct).filter(mProduct.name==product_name).first()

def get_product(db: Session, product_id: int):
    return db.query(mProduct).filter(mProduct.id==product_id).first()

def get_all_products(db:Session):
    return db.query(mProduct).all()

def get_orders_by_user(db: Session, owner_id: int):
    return db.query(mOrder).filter(mOrder.user_id==owner_id).all()

def get_basket(db:Session, user_id: int):
    orders=db.query(mOrder).filter(mOrder.user_id==user_id).all()
    for i in orders:
        if i.isFinished== False:
            return i
    return False

def create_user(db: Session, user: UserCreate):
    db_user=mUser(name=user.name, email=user.email, surname=user.surname, wallet=0.0,password=user.password, is_admin=False,is_disabled=True)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_product(db:Session, product: Product, shop_id: int):
    db_product=mProduct(name=product.name, description=product.description, number=product.number, price=product.price, user_id=1)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def create_order(db: Session, order: Order):
    db_order= mOrder(user_id=order.owner_id, items=order.products, isFinished=order.isFinished)
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

def change_number_of_product(db: Session, product: mProduct, number: int):
    product.number=number
    db.commit()
    db.refresh(product)
    return product

def change_price_of_product(db: Session, product: mProduct, price: float):
    product.price=price
    db.commit()
    db.refresh(product)
    return product

def change_state_of_order(db: Session, order: mOrder, state: bool):
    order.isFinished=state
    db.query(mOrder).filter(mOrder.id==order.id).delete()
    db.add(order)
    db.commit()
    db.refresh(order)

def switch_user_activity(db:Session, user_id:int):
    user=db.query(mUser).filter(mUser.id==user_id).first()
    db.query(mUser).filter(mUser.id==user_id).delete()
    user.is_disabled= not user.is_disabled
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def update_wallet(db:Session, user_id: int, new_wallet:float):
    user=db.query(mUser).filter(mUser.id==user_id).first()
    user.wallet= new_wallet
    db.commit()
    db.refresh(user)
    return user

def update_admin(db:Session, user_id: int, admin_priviliges:bool):
    user=db.query(mUser).filter(mUser.id==user_id).first()
    user.is_admin= admin_priviliges
    db.commit()
    db.refresh(user)
    return user

def update_password(db:Session, user_id: int, password:str):
    user=db.query(mUser).filter(mUser.id==user_id).first()
    user.password= password
    db.commit()
    db.refresh(user)
    return user

def update_mail(db:Session, user_id: int, username:str):
    user=db.query(mUser).filter(mUser.id==user_id).first()
    user.email= username
    db.commit()
    db.refresh(user)
    return user




