from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Dict, Any, List
import logging
import json
import traceback

from ..services.competence_tree.competence_tree_service import CompetenceTreeService
from ..utils.database import get_db
from ..routers.user import get_current_user
from ..models import User, UserSkillTree

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/competence-tree",
    tags=["competence-tree"],
    dependencies=[Depends(get_current_user)],
)

# Initialize service as singleton
competence_tree_service = CompetenceTreeService()

@router.post("/generate", response_model=Dict[str, Any])
def generate_competence_tree(
    max_depth: int = Query(10, gt=0, le=20),
    max_nodes_per_level: int = Query(5, gt=0, le=10),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate a new competence tree for a user.
    
    Args:
        max_depth: Maximum depth of the tree (1-20)
        max_nodes_per_level: Maximum number of nodes per level (1-10)
        current_user: Current authenticated user
        db: Database session
    """
    logger.info(f"Request received to generate competence tree for user {current_user.id}")
    try:
        # Create the competence tree
        logger.info(f"Creating competence tree for user {current_user.id}")
        tree_data = competence_tree_service.create_skill_tree(
            db, 
            current_user.id,
            max_depth=max_depth,
            max_nodes_per_level=max_nodes_per_level
        )
        
        if not tree_data:
            logger.error(f"Failed to create competence tree for user {current_user.id}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create competence tree"
            )
        
        # Get the graph_id from the tree data
        graph_id = tree_data.get("graph_id")
        if not graph_id:
            logger.error(f"No graph_id found in tree data for user {current_user.id}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate graph_id"
            )
        
        # Save the tree in the database
        logger.info(f"Saving competence tree for user {current_user.id} with graph_id {graph_id}")
        saved_graph_id = competence_tree_service.save_skill_tree(db, current_user.id, tree_data)
        
        if not saved_graph_id:
            logger.error(f"Failed to save competence tree for user {current_user.id}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save competence tree"
            )
        
        logger.info(f"Competence tree generated and saved successfully for user {current_user.id} with graph_id {saved_graph_id}")
        return {"graph_id": saved_graph_id, "message": "Competence tree generated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating competence tree for user {current_user.id}: {str(e)}")
        logger.error(traceback.format_exc())
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
    logger.info(f"Request received to get competence tree with ID {graph_id} for user {current_user.id}")
    try:
        # Get the competence tree from the database
        logger.info(f"Retrieving competence tree {graph_id} from database for user {current_user.id}")
        skill_tree = db.query(UserSkillTree).filter(
            UserSkillTree.graph_id == graph_id,
            UserSkillTree.user_id == current_user.id
        ).first()
        
        if not skill_tree:
            logger.error(f"Competence tree with ID {graph_id} not found for user {current_user.id}")
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
            
            logger.info(f"Successfully retrieved competence tree {graph_id} for user {current_user.id}")
            # Return as JSONResponse to ensure proper serialization
            return JSONResponse(content=tree_data)
            
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON from tree_data for user {current_user.id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error decoding competence tree data: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Error processing tree data for user {current_user.id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error processing competence tree data: {str(e)}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving competence tree for user {current_user.id}: {str(e)}")
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