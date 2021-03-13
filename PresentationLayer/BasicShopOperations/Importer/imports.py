from openpyxl import Workbook, load_workbook
import os

from DataAccessLayer import crud
from DataAccessLayer import database
from DataAccessLayer import  models, schemas

def get_db():
    db=database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

def start_db_with_users(db):
    dirs=os.listdir()
    '''if "users.xlxs" not in dirs:
        print("a")
        return
    '''
    wb= load_workbook("users.xlsx")
    ws= wb.active

    my_users=[]
    current_row=2
    while ws.cell(row=current_row, column=1).value!=None:
        my_users.append(schemas.UserCreate(
            id=ws.cell(row=current_row, column=1).value,
            name=ws.cell(row=current_row, column=2).value,
            surname=ws.cell(row=current_row, column=3).value,
            email=ws.cell(row=current_row, column=4).value,
            wallet=ws.cell(row=current_row, column=5).value,
            password=ws.cell(row=current_row, column=6).value,
            is_admin=ws.cell(row=current_row, column=7).value,
            is_disabled=ws.cell(row=current_row, column=8).value,
            ))
        current_row+=1

    print(len(my_users))
    for i in my_users:
        crud.create_user(db=db,user=i)
    db.close()
    return
