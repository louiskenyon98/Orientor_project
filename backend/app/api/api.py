from fastapi import APIRouter
from app.api.endpoints import trees

api_router = APIRouter()
api_router.include_router(trees.router, prefix="/v1/trees", tags=["trees"]) 