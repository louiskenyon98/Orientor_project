from fastapi import APIRouter
from app.api.endpoints import trees, job_recommendations

api_router = APIRouter()
api_router.include_router(trees.router, prefix="/trees", tags=["trees"])
api_router.include_router(job_recommendations.router, prefix="/jobs", tags=["jobs"])