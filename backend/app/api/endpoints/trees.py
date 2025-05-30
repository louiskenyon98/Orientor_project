from fastapi import APIRouter, HTTPException, Depends, Body, Header
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging
from sqlalchemy.orm import Session
from app.services.LLM.skills_tree_service import TreeService
from app.services.LLM.career_tree_service import CareerTreeService
from app.routers.user import get_current_user
from app.models.user import User
from app.utils.database import get_db

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize services
tree_service = TreeService()
career_tree_service = CareerTreeService()

class ProfileRequest(BaseModel):
    profile: str

async def get_optional_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    if authorization:
        try:
            # Remove "Bearer " prefix if present
            token = authorization.replace("Bearer ", "") if authorization.startswith("Bearer ") else authorization
            return get_current_user(token=token, db=db)
        except HTTPException:
            return None
    return None

@router.post("/generate-tree")
async def generate_tree(
    request: ProfileRequest = Body(...),
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    try:
        user_id = str(current_user.id) if current_user else None
        logger.info(f"Generating tree for user_id: {user_id if user_id else 'anonymous'}")
        
        tree = await tree_service.generate_tree(request.profile, user_id)
        logger.info("Tree generation successful")
        
        # Convert to dict for JSON response
        return tree.dict()
    except Exception as e:
        logger.error(f"Error generating tree: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating tree: {str(e)}")

@router.post("/generate-career-tree")
async def generate_career_tree(
    request: ProfileRequest = Body(...),
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    try:
        user_id = str(current_user.id) if current_user else None
        logger.info(f"Generating career tree for user_id: {user_id if user_id else 'anonymous'}")
        
        tree = await career_tree_service.generate_career_tree(request.profile, user_id)
        logger.info("Career tree generation successful")
        
        # Convert to dict for JSON response
        return tree.dict()
    except Exception as e:
        logger.error(f"Error generating career tree: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating career tree: {str(e)}") 