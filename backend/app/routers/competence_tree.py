from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Dict, Any, List
import logging
import json

from ..services.competence_tree_service import CompetenceTreeService
from ..utils.database import get_db
from ..routers.user import get_current_user
from ..models import User, UserSkillTree

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/competence-tree",
    tags=["competence-tree"],
    dependencies=[Depends(get_current_user)],
)

# Initialize service
competence_tree_service = CompetenceTreeService()

@router.post("/generate", response_model=Dict[str, Any])
def generate_competence_tree(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate a new competence tree for a user.
    """
    logger.info(f"Request received to generate competence tree for user {current_user.id}")
    try:
        # Create the competence tree
        logger.info(f"Creating competence tree for user {current_user.id}")
        tree_data = competence_tree_service.create_skill_tree(db, current_user.id)
        
        if not tree_data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create competence tree"
            )
        
        # Save the tree in the database
        graph_id = competence_tree_service.save_skill_tree(db, current_user.id, tree_data)
        
        if not graph_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save competence tree"
            )
        
        return {"graph_id": graph_id, "message": "Competence tree generated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating competence tree: {str(e)}"
        )

@router.get("/{graph_id}")
def get_competence_tree(
    graph_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get an existing competence tree.
    """
    logger.info(f"Request received to get competence tree with ID {graph_id}")
    try:
        # Get the competence tree from the database
        logger.info(f"Retrieving competence tree {graph_id} from database")
        skill_tree = db.query(UserSkillTree).filter(
            UserSkillTree.graph_id == graph_id,
            UserSkillTree.user_id == current_user.id
        ).first()
        
        if not skill_tree:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Competence tree with ID {graph_id} not found"
            )
        
        # Log the type and content of tree_data for debugging
        logger.debug(f"Type of tree_data: {type(skill_tree.tree_data)}")
        logger.debug(f"Content of tree_data: {skill_tree.tree_data}")
        
        try:
            # Handle different types of tree_data
            if isinstance(skill_tree.tree_data, str):
                # If it's a string, parse it as JSON
                tree_data = json.loads(skill_tree.tree_data)
            else:
                # If it's already a dict (JSONB), use it directly
                tree_data = skill_tree.tree_data
            
            # Return as JSONResponse to ensure proper serialization
            return JSONResponse(content=tree_data)
            
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON from tree_data: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error decoding competence tree data: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Error processing tree data: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error processing competence tree data: {str(e)}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving competence tree: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving competence tree: {str(e)}"
        )

@router.patch("/node/{node_id}/complete", response_model=Dict[str, Any])
def complete_challenge(
    node_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark a challenge as completed and award XP.
    """
    logger.info(f"Request received to complete challenge {node_id} for user {current_user.id}")
    try:
        # Mark the challenge as completed
        logger.info(f"Marking challenge {node_id} as completed for user {current_user.id}")
        success = competence_tree_service.complete_challenge(db, node_id, current_user.id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Could not complete challenge for node {node_id}"
            )
        
        # Emit a public event
        competence_tree_service.emit_public_event(db, current_user.id, "challenge_completed")
        
        return {"success": True, "message": "Challenge completed successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error completing challenge: {str(e)}"
        )