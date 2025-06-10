#!/usr/bin/env python3
"""
Test the enhanced competence tree implementation with proper graph traversal.
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

def test_enhanced_competence_tree():
    """Test the enhanced competence tree with graph traversal"""
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
        
        # Test complete skill tree creation with new enhanced method
        logger.info("\n" + "="*60)
        logger.info("TESTING ENHANCED COMPETENCE TREE GENERATION")
        logger.info("="*60)
        
        tree_data = service.create_skill_tree(
            db, 
            user.id,
            max_depth=3,
            max_nodes_per_level=4
        )
        
        if not tree_data:
            logger.error("Failed to create skill tree")
            return
        
        logger.info(f"\n🌳 ENHANCED SKILL TREE CREATED SUCCESSFULLY!")
        logger.info(f"📊 Total nodes: {len(tree_data.get('nodes', []))}")
        logger.info(f"🔗 Total edges: {len(tree_data.get('edges', []))}")
        logger.info(f"⭐ Anchor nodes: {len(tree_data.get('anchors', []))}")
        logger.info(f"📋 Tree type: {tree_data.get('tree_type', 'unknown')}")
        logger.info(f"🛠️ Generation method: {tree_data.get('generation_method', 'unknown')}")
        
        # Analyze nodes by type and depth
        nodes = tree_data.get('nodes', [])
        
        # Count by type
        skill_nodes = [n for n in nodes if n.get('type') == 'skill']
        occupation_nodes = [n for n in nodes if n.get('type') == 'occupation']
        anchor_nodes = [n for n in nodes if n.get('is_anchor', False)]
        
        logger.info(f"\n📈 NODE ANALYSIS:")
        logger.info(f"   💪 Skills: {len(skill_nodes)}")
        logger.info(f"   💼 Occupations: {len(occupation_nodes)}")
        logger.info(f"   ⭐ Anchors: {len(anchor_nodes)}")
        
        # Count by depth
        depth_counts = {}
        for node in nodes:
            depth = node.get('depth', 0)
            depth_counts[depth] = depth_counts.get(depth, 0) + 1
        
        logger.info(f"\n🏗️ DEPTH DISTRIBUTION:")
        for depth in sorted(depth_counts.keys()):
            logger.info(f"   Depth {depth}: {depth_counts[depth]} nodes")
        
        # Count by visibility
        visible_nodes = [n for n in nodes if n.get('visible', False)]
        revealed_nodes = [n for n in nodes if n.get('revealed', False)]
        
        logger.info(f"\n👁️ VISIBILITY ANALYSIS:")
        logger.info(f"   Visible: {len(visible_nodes)}/{len(nodes)} ({len(visible_nodes)/len(nodes)*100:.1f}%)")
        logger.info(f"   Revealed: {len(revealed_nodes)}/{len(nodes)} ({len(revealed_nodes)/len(nodes)*100:.1f}%)")
        
        # Show anchor skills details
        logger.info(f"\n⭐ ANCHOR SKILLS DETAILS:")
        anchor_metadata = tree_data.get('anchor_metadata', [])
        for i, anchor in enumerate(anchor_metadata):
            logger.info(f"   {i+1}. {anchor.get('esco_label', anchor.get('original_label', 'Unknown'))}")
            logger.info(f"      Category: {anchor.get('category', 'general')}")
            logger.info(f"      Confidence: {anchor.get('confidence', 0):.2f}")
        
        # Show edges details
        edges = tree_data.get('edges', [])
        edge_types = {}
        for edge in edges:
            edge_type = edge.get('type', 'unknown')
            edge_types[edge_type] = edge_types.get(edge_type, 0) + 1
        
        logger.info(f"\n🔗 EDGE ANALYSIS:")
        for edge_type, count in edge_types.items():
            logger.info(f"   {edge_type}: {count} connections")
        
        # Test graph structure connectivity
        logger.info(f"\n🕸️ CONNECTIVITY ANALYSIS:")
        connected_nodes = set()
        for edge in edges:
            connected_nodes.add(edge['source'])
            connected_nodes.add(edge['target'])
        
        isolated_nodes = [n['id'] for n in nodes if n['id'] not in connected_nodes]
        logger.info(f"   Connected nodes: {len(connected_nodes)}/{len(nodes)}")
        logger.info(f"   Isolated nodes: {len(isolated_nodes)}")
        
        if isolated_nodes:
            logger.warning(f"   Isolated node IDs: {isolated_nodes[:5]}...")  # Show first 5
        
        # Test saving the tree
        logger.info(f"\n💾 TESTING TREE PERSISTENCE:")
        graph_id = service.save_skill_tree(db, user.id, tree_data)
        if graph_id:
            logger.info(f"   ✅ Tree saved successfully with graph_id: {graph_id}")
        else:
            logger.error(f"   ❌ Failed to save tree")
        
        logger.info(f"\n" + "="*60)
        logger.info("✅ ENHANCED COMPETENCE TREE TEST COMPLETED SUCCESSFULLY!")
        logger.info("="*60)
        
    except Exception as e:
        logger.error(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    test_enhanced_competence_tree()