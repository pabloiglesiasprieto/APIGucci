from fastapi import FastAPI
from routers import users, products, auth_users, users_db
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Routers
app.include_router(users.router)
app.include_router(products.router)
app.include_router(auth_users.router)
app.include_router(users_db.router)
# app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def root():
    return {"Hello": "World"}
