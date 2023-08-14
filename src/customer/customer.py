from fastapi import APIRouter, Depends
from .login import get_current_user
from src.models.customer import Customer

user_router = APIRouter(
    prefix="/customer",
    tags=["customer"],
    dependencies=[Depends(get_current_user)],
    responses={403: {"description": "Forbidden"}},
)

# Protected route that requires authentication
@user_router.get("/secure-route/")
async def secure_route(current_user: Customer = Depends(get_current_user)):
    return {"message": "This is a secure route!", "user": current_user}