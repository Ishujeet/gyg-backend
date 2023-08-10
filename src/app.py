from fastapi import FastAPI
from .customer.customer import user_router
from .customer.login import login_router
from .models.base import create_tables


app = FastAPI()

app.include_router(user_router)
app.include_router(login_router)

@app.on_event("startup")
def init_db():
    create_tables()