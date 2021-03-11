from openpyxl import Workbook

from DataAccessLayer import crud
from DataAccessLayer import database

def get_db():
    db=database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

wb= Workbook()

ws= wb.active

ws["A1"]=1

wb.save("sample.xlsx")

