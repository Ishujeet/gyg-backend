from fastapi import FastAPI
from .customer.customer import user_router
from .customer.login import login_router
from .orders.order import order_router
from .gym.gym_slot import gym_router
from .vendor.login import vendor_router
from .models.base import create_tables


app = FastAPI()

app.include_router(user_router)
app.include_router(login_router)
app.include_router(order_router)
app.include_router(gym_router)
app.include_router(vendor_router)

@app.on_event("startup")
def init_db():
    create_tables()