from fastapi import APIRouter
from .apis import users

user_router = APIRouter()

user_router.include_router(users.router, prefix="/api", tags=["user"])
