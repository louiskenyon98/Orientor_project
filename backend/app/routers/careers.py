from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from ..utils.database import get_db
from ..routers.user import get_current_user
from ..models import User
from ..services.career_swipe.career_recommendation_service import (
    get_career_recommendations,
    save_career_recommendation,
    get_saved_careers
)
import logging

router = APIRouter(prefix="/careers", tags=["careers"])
logger = logging.getLogger(__name__)

@router.get("/recommendations", response_model=List[Dict[str, Any]])
def read_career_recommendations(
    limit: int = Query(30, gt=0, le=30),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get personalized career recommendations for the current user.
    These are swipeable recommendations in the "Find Your Way" tab.
    """
    try:
        recommendations = get_career_recommendations(db, current_user.id, limit)
        return recommendations
    except Exception as e:
        logger.error(f"Error retrieving career recommendations: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve career recommendations: {str(e)}"
        )

@router.post("/save/{career_id}", response_model=Dict[str, Any])
def save_career(
    career_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Save a career recommendation for the current user.
    This happens when the user swipes right on a career in the "Find Your Way" tab.
    """
    try:
        success = save_career_recommendation(db, current_user.id, career_id)
        
        if not success:
            raise HTTPException(
                status_code=400,
                detail="Failed to save career recommendation"
            )
        
        return {"success": True, "message": "Career saved successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving career recommendation: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save career recommendation: {str(e)}"
        )

@router.get("/saved", response_model=List[Dict[str, Any]])
def read_saved_careers(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get saved career recommendations for the current user.
    These appear in the "My Space" section.
    This endpoint retrieves recommendations saved from both 
    the "Find Your Way" tab and the traditional career recommendation tab.
    """
    try:
        saved_careers = get_saved_careers(db, current_user.id)
        return saved_careers
    except Exception as e:
        logger.error(f"Error retrieving saved careers: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve saved careers: {str(e)}"
        ) 