from fastapi import APIRouter, Depends
from .login import get_current_user

user_router = APIRouter(
    prefix="/customer",
    tags=["customer"],
    dependencies=[Depends(get_current_user)],
    responses={403: {"description": "Forbidden"}},
)

# Protected route that requires authentication
@user_router.get("/secure-route/")
async def secure_route(current_user: dict):
    return {"message": "This is a secure route!", "user": current_user}