from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Dict, Any, List
import logging
import json

from ..services.competenceTree import CompetenceTreeService
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
    max_depth: int = Query(6, gt=0, le=10, description="Maximum depth of skill tree traversal"),
    max_nodes: int = Query(30, gt=5, le=50, description="Maximum total nodes in the tree"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate a new competence tree for a user following palmier specification.
    
    Flow:
    1. Infer 5 anchor skills from user profile using LLM
    2. Format skills using ESCO templates
    3. Build tree structure using GraphSAGE traversal
    4. Apply gamification rules (70% hidden nodes)
    5. Save tree with competenceTree JSONB column
    6. Return graph_id for retrieval
    
    Args:
        max_depth: Maximum depth of the tree (1-10, default 6)
        max_nodes: Maximum total nodes in tree (5-50, default 30)
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Dict with graph_id for accessing the generated tree
    """
    logger.info(f"Request received to generate competence tree for user {current_user.id}")
    try:
        # Create the competence tree
        logger.info(f"Creating competence tree for user {current_user.id}")
        tree_data = competence_tree_service.create_skill_tree(
            db, 
            current_user.id,
            max_depth=max_depth,
            max_nodes_per_level=max(3, max_nodes // max_depth)  # Calculate nodes per level from total
        )
        
        if not tree_data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create competence tree"
            )
        
        # Log tree data structure before saving
        logger.info(f"Tree data structure before saving: nodes={len(tree_data.get('nodes', []))}, "
                   f"anchors={len(tree_data.get('anchors', []))}, "
                   f"anchor_metadata={len(tree_data.get('anchor_metadata', []))}")
        
        # Save the tree in the database
        graph_id = competence_tree_service.save_skill_tree(db, current_user.id, tree_data)
        
        if not graph_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save competence tree"
            )
        
        logger.info(f"Competence tree saved successfully with graph_id: {graph_id}")
        
        return {"graph_id": graph_id, "message": "Competence tree generated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating competence tree: {str(e)}"
        )

@router.get("/anchor-skills", response_model=Dict[str, Any])
def get_user_anchor_skills(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's anchor skills from their latest competence tree.
    
    Returns anchor skills without regenerating the tree if one exists.
    """
    logger.info(f"Request received to get anchor skills for user {current_user.id}")
    try:
        # Get the user's latest skill tree
        skill_tree = db.query(UserSkillTree).filter(
            UserSkillTree.user_id == current_user.id
        ).order_by(UserSkillTree.created_at.desc()).first()
        
        if not skill_tree:
            return {
                "anchor_skills": [],
                "message": "No competence tree found. Generate one first."
            }
        
        # Parse tree data
        tree_data = skill_tree.tree_data
        if isinstance(tree_data, str):
            tree_data = json.loads(tree_data)
        
        logger.info(f"Retrieved tree data for user {current_user.id}: "
                   f"nodes={len(tree_data.get('nodes', []))}, "
                   f"anchors={len(tree_data.get('anchors', []))}, "
                   f"anchor_metadata={len(tree_data.get('anchor_metadata', []))}")
        
        anchor_metadata = tree_data.get("anchor_metadata", [])
        
        return {
            "anchor_skills": anchor_metadata,
            "graph_id": skill_tree.graph_id,
            "message": f"Found {len(anchor_metadata)} anchor skills"
        }
        
    except Exception as e:
        logger.error(f"Error retrieving anchor skills: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving anchor skills: {str(e)}"
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
    node_id: str,  # Changed to string to match ESCO node IDs
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark a node challenge as completed following palmier specification.
    
    Flow:
    1. Mark node state as completed
    2. Update user_progress.total_xp
    3. Add completion timestamp
    4. Reveal children nodes (set visible=true)
    5. Update user skill tree in database
    
    Args:
        node_id: ESCO node ID to mark as completed
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Success status and updated node information
    """
    logger.info(f"Request received to complete challenge {node_id} for user {current_user.id}")
    try:
        # Complete the challenge using the new service method
        logger.info(f"Marking challenge {node_id} as completed for user {current_user.id}")
        result = competence_tree_service.complete_challenge(db, node_id, current_user.id)
        
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", f"Could not complete challenge for node {node_id}")
            )
        
        # Log the completion
        logger.info(f"Challenge {node_id} completed successfully for user {current_user.id}: "
                   f"+{result.get('xp_earned', 0)} XP, {result.get('children_revealed', 0)} children revealed")
        
        return {
            "success": True, 
            "message": "Challenge completed successfully",
            "xp_earned": result.get("xp_earned", 0),
            "total_xp": result.get("total_xp", 0),
            "level": result.get("level", 1),
            "children_revealed": result.get("children_revealed", 0)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error completing challenge: {str(e)}"
        )