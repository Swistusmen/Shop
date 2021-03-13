# Shop
Learnig web development

main purpose of this project wat to learn FastAPI and webdevelopment.

Program runs on hypercorn server so to activate it use:
hypercorn main:app --reload

as fast api has swagger ui embedeed in itself, it's quite easy to test this app

Functionalities:
-basic client operations (add product, remove, create user, login, see history of orders, get all products, get products but with pagination, change password)
-basic admin operations (add products, see everything in the system, change permissions, change prices and number of products, export data from db into xlsx)
- authentication with oauth2
-database: sqllite



What can be improved:
-write tests
-clean code
-advisory basing on categories and other purchases
-api responses in case of incorrectness

+ Write a front end for website
