from fastapi import APIRouter

from src.api.routes import home

api_router = APIRouter()
api_router.include_router(home.router, tags=["login"])
# api_router.include_router(users.router, prefix="/users", tags=["users"])

