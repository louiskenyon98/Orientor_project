import os
import logging
import numpy as np
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import text
import ast
import subprocess
from app.models.user_profile import UserProfile
from app.services.embeddings.embedding_service import generate_embedding

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def parse_embedding(embedding_data: Any) -> Optional[List[float]]:
    """
    Parse embedding data into a list of floats
    
    Args:
        embedding_data: Embedding data from the database
        
    Returns:
        List of floats or None if parsing fails
    """
    try:
        if isinstance(embedding_data, (list, np.ndarray)):
            return list(embedding_data)
        elif isinstance(embedding_data, str):
            # Handle string representation of list
            embedding_data = embedding_data.strip()
            if embedding_data.startswith('[') and embedding_data.endswith(']'):
                return [float(x) for x in embedding_data[1:-1].split(',')]
            else:
                # Try using ast.literal_eval for safer parsing
                return ast.literal_eval(embedding_data)
        else:
            logger.error(f"Unexpected embedding type: {type(embedding_data)}")
            return None
    except Exception as e:
        logger.error(f"Error parsing embedding: {str(e)}")
        return None

def cosine_similarity(a: List[float], b: List[float]) -> float:
    """
    Calculate cosine similarity between two vectors
    
    Args:
        a: First vector
        b: Second vector
        
    Returns:
        Cosine similarity score (between -1 and 1)
    """
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def get_users_with_embeddings(db: Session) -> List[Dict[str, Any]]:
    """
    Get all users and generate their embeddings on-the-fly
    
    Args:
        db: Database session
        
    Returns:
        List of user data including embeddings
    """
    try:
        # Get all user profiles
        profiles = db.query(UserProfile).all()
        users = []
        
        for profile in profiles:
            # Generate embedding for this profile
            profile_data = {
                "job_title": profile.job_title,
                "industry": profile.industry,
                "years_experience": profile.years_experience,
                "education_level": profile.education_level,
                "career_goals": profile.career_goals,
                "skills": profile.skills if profile.skills else [],
                "interests": profile.interests if isinstance(profile.interests, str) else " ".join(profile.interests) if profile.interests else ""
            }
            
            embedding = generate_embedding(profile_data)
            if embedding is not None:
                users.append({
                    "user_id": profile.user_id,
                    "embedding": embedding
                })
        
        logger.info(f"Generated embeddings for {len(users)} users")
        return users
    except Exception as e:
        logger.error(f"Error getting users with embeddings: {str(e)}")
        return []

def find_similar_peers(db: Session, user_id: int, embedding: List[float], top_n: int = 5) -> List[Tuple[int, float]]:
    """
    Find similar peers for a given user
    
    Args:
        db: Database session
        user_id: ID of the user
        embedding: User's embedding
        top_n: Number of similar peers to find
        
    Returns:
        List of tuples (peer_id, similarity_score)
    """
    try:
        # Get all other users
        other_profiles = db.query(UserProfile).filter(UserProfile.user_id != user_id).all()
        
        # Calculate similarities
        similarities = []
        for profile in other_profiles:
            try:
                # Generate embedding for this profile
                profile_data = {
                    "job_title": profile.job_title,
                    "industry": profile.industry,
                    "years_experience": profile.years_experience,
                    "education_level": profile.education_level,
                    "career_goals": profile.career_goals,
                    "skills": profile.skills if profile.skills else [],
                    "interests": profile.interests if isinstance(profile.interests, str) else " ".join(profile.interests) if profile.interests else ""
                }
                
                other_embedding = generate_embedding(profile_data)
                if other_embedding is not None:
                    other_embedding = np.array(other_embedding, dtype=float)
                    user_embedding = np.array(embedding, dtype=float)
                    similarity = cosine_similarity(user_embedding, other_embedding)
                    similarities.append((profile.user_id, similarity))
            except Exception as e:
                logger.error(f"Error calculating similarity for user {profile.user_id}: {str(e)}")
                continue
        
        # Sort by similarity and get top N
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_n]
    except Exception as e:
        logger.error(f"Error finding similar peers: {str(e)}")
        return []

def update_suggested_peers(db: Session, user_id: int, similar_peers: List[Tuple[int, float]]) -> bool:
    """
    Update the suggested_peers table for a user
    
    Args:
        db: Database session
        user_id: ID of the user
        similar_peers: List of tuples (peer_id, similarity_score)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Delete existing suggestions
        query = text("""
            DELETE FROM suggested_peers
            WHERE user_id = :user_id
        """)
        
        db.execute(query, {"user_id": user_id})
        
        # Insert new suggestions
        for peer_id, similarity in similar_peers:
            query = text("""
                INSERT INTO suggested_peers (user_id, suggested_id, similarity)
                VALUES (:user_id, :peer_id, :similarity)
            """)
            
            db.execute(query, {
                "user_id": user_id,
                "peer_id": peer_id,
                "similarity": float(similarity)
            })
        
        db.commit()
        logger.info(f"Updated suggested peers for user {user_id}")
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating suggested peers: {str(e)}")
        return False

def generate_peer_suggestions(db: Session, user_id: int, top_n: int = 5) -> bool:
    """
    Generate peer suggestions for a user
    
    Args:
        db: Database session
        user_id: ID of the user
        top_n: Number of similar peers to find
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Get user's embedding
        query = text("""
            SELECT embedding
            FROM user_profiles
            WHERE user_id = :user_id
        """)
        
        result = db.execute(query, {"user_id": user_id}).fetchone()
        
        if not result or not result.embedding:
            logger.error(f"No embedding found for user {user_id}")
            return False
        
        # Parse embedding
        embedding = parse_embedding(result.embedding)
        if not embedding:
            logger.error(f"Failed to parse embedding for user {user_id}")
            return False
        
        # Find similar peers
        similar_peers = find_similar_peers(db, user_id, embedding, top_n)
        
        if not similar_peers:
            logger.warning(f"No similar peers found for user {user_id}")
            return False
        
        # Update suggested_peers table
        success = update_suggested_peers(db, user_id, similar_peers)
        
        return success
    except Exception as e:
        logger.error(f"Error generating peer suggestions: {str(e)}")
        return False

def run_peer_matching_script() -> bool:
    """
    Run the peer matching script to update suggested peers for all users
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Get the path to the script
        script_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts", "find_similar_peers.py")
        
        # Run the script using subprocess
        result = subprocess.run(["python", script_path], capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"Error running peer matching script: {result.stderr}")
            return False
        
        logger.info("Peer matching script completed successfully")
        return True
    except Exception as e:
        logger.error(f"Error running peer matching script: {str(e)}")
        return False 