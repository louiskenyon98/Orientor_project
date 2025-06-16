#!/usr/bin/env python3
"""
Test the enhanced skill tree generation to ensure no infinite loops
"""
import asyncio
import logging
from sqlalchemy.orm import Session
from app.utils.database import get_db
from app.services.competenceTree import CompetenceTreeService
from app.models import User

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_enhanced_tree():
    """Test the enhanced skill tree generation"""
    try:
        # Initialize service
        service = CompetenceTreeService()
        logger.info("CompetenceTreeService initialized")
        
        # Get database session
        db = next(get_db())
        
        # Get a test user
        user = db.query(User).first()
        if not user:
            logger.error("No users found in database")
            return
        
        logger.info(f"Testing with user ID: {user.id}")
        
        # Test anchor skill inference
        logger.info("Step 1: Testing anchor skill inference...")
        anchor_skills = service.infer_anchor_skills(db, user.id)
        logger.info(f"Inferred {len(anchor_skills)} anchor skills")
        
        for i, skill in enumerate(anchor_skills):
            logger.info(f"  Anchor {i+1}: {skill.get('esco_label', skill.get('original_label', 'Unknown'))}")
        
        if not anchor_skills:
            logger.error("No anchor skills inferred, cannot continue")
            return
        
        # Test enhanced skill tree creation
        logger.info("\nStep 2: Testing enhanced skill tree creation...")
        graph_id = "test-graph-123"
        user_age = 25
        
        tree_data = service._create_enhanced_skill_tree(anchor_skills, user_age, graph_id, db)
        
        logger.info(f"\nTree created successfully!")
        logger.info(f"  Total nodes: {len(tree_data.get('nodes', []))}")
        logger.info(f"  Total edges: {len(tree_data.get('edges', []))}")
        logger.info(f"  Anchor nodes: {len(tree_data.get('anchors', []))}")
        
        # Count visible nodes
        visible_nodes = [n for n in tree_data.get('nodes', []) if n.get('visible', False)]
        logger.info(f"  Visible nodes: {len(visible_nodes)}")
        
        # Check for challenges
        nodes_with_challenges = [n for n in tree_data.get('nodes', []) if n.get('challenge')]
        logger.info(f"  Nodes with challenges: {len(nodes_with_challenges)}")
        
        logger.info("\nTest completed successfully! No infinite loops detected.")
        
    except Exception as e:
        logger.error(f"Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    test_enhanced_tree()