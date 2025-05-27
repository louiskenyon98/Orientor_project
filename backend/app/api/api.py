from fastapi import APIRouter
from app.api.endpoints import trees, job_recommendations
from app.routers import competence_tree
from app.routers.users import router as users_router

api_router = APIRouter()
api_router.include_router(trees.router, prefix="/trees", tags=["trees"])
api_router.include_router(job_recommendations.router, prefix="/jobs", tags=["jobs"])
api_router.include_router(competence_tree.router, prefix="/competence-tree", tags=["competence-tree"])
api_router.include_router(users_router, prefix="/users", tags=["users"])