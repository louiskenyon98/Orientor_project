from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Dict, Any, List
import logging
import json
import traceback

from ..services.occupation_tree.job_recommendation_service import JobRecommendationService
from ..utils.database import get_db
from ..routers.user import get_current_user
from ..models import User

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/job-recommendation",
    tags=["job-recommendation"],
    dependencies=[Depends(get_current_user)],
)

# Initialize service as singleton
job_recommendation_service = JobRecommendationService()

@router.post("/generate", response_model=Dict[str, Any])
def generate_job_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate job recommendations for a user.
    """
    logger.info(f"Request received to generate job recommendations for user {current_user.id}")
    try:
        # Get job recommendations
        logger.info(f"Getting job recommendations for user {current_user.id}")
        recommendations = job_recommendation_service.get_job_recommendations(db, current_user.id)
        
        if not recommendations:
            logger.error(f"No job recommendations found for user {current_user.id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No job recommendations found"
            )
        
        # Generate skill tree for each recommendation
        skill_trees = []
        for recommendation in recommendations:
            try:
                job_id = recommendation["id"]
                logger.info(f"Generating skill tree for job {job_id} for user {current_user.id}")
                skill_tree = job_recommendation_service.generate_skill_tree_for_job(job_id)
                
                if skill_tree:
                    # Get the graph_id from the skill tree
                    graph_id = skill_tree.get("graph_id")
                    if not graph_id:
                        logger.error(f"No graph_id found in skill tree for job {job_id}")
                        continue
                        
                    skill_trees.append({
                        "job_id": job_id,
                        "graph_id": graph_id,
                        "skill_tree": skill_tree
                    })
                    logger.info(f"Skill tree generated successfully for job {job_id} with graph_id {graph_id}")
            except Exception as e:
                logger.error(f"Error generating skill tree for job {job_id}: {str(e)}")
                continue
        
        if not skill_trees:
            logger.error(f"No skill trees generated for user {current_user.id}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate skill trees"
            )
        
        logger.info(f"Successfully generated {len(skill_trees)} skill trees for user {current_user.id}")
        return {
            "recommendations": recommendations,
            "skill_trees": skill_trees
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating job recommendations for user {current_user.id}: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating job recommendations: {str(e)}"
        )

@router.get("/{graph_id}")
def get_job_skill_tree(
    graph_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a job skill tree by graph_id.
    """
    logger.info(f"Request received to get job skill tree with ID {graph_id} for user {current_user.id}")
    try:
        # Get the stored recommendations
        recommendations = job_recommendation_service.get_stored_recommendations(db, current_user.id)
        
        if not recommendations:
            logger.error(f"No stored recommendations found for user {current_user.id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No job recommendations found"
            )
        
        # Find the skill tree with the matching graph_id
        for recommendation in recommendations:
            job_id = recommendation["id"]
            skill_tree = job_recommendation_service.generate_skill_tree_for_job(job_id)
            
            if skill_tree and skill_tree.get("graph_id") == graph_id:
                logger.info(f"Found skill tree with graph_id {graph_id} for user {current_user.id}")
                return JSONResponse(content=skill_tree)
        
        logger.error(f"Skill tree with graph_id {graph_id} not found for user {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Skill tree with ID {graph_id} not found"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving job skill tree for user {current_user.id}: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving job skill tree: {str(e)}"
        ) 