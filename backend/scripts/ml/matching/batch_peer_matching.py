import os
import logging
from typing import List, Optional
import argparse
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import numpy as np
from dotenv import load_dotenv
import ast

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

import ast

def parse_embedding(embedding_data) -> List[float]:
    """Handle both stored lists and stored strings."""
    if isinstance(embedding_data, (list, np.ndarray)):
        return list(embedding_data)
    elif isinstance(embedding_data, str):
        try:
            # Parse string safely
            return ast.literal_eval(embedding_data)
        except Exception as e:
            logger.error(f"Error parsing embedding string: {str(e)}")
            return []
    else:
        logger.error(f"Invalid embedding type: {type(embedding_data)}")
        return []

def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Calculate cosine similarity between two vectors"""
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def get_users_with_embeddings(db):
    """Get all users with embeddings"""
    query = text("""
        SELECT user_id, embedding
        FROM user_profiles
        WHERE embedding IS NOT NULL
    """)
    return db.execute(query).fetchall()

def find_similar_peers(db, user_id: int, embedding: List[float], top_n: int = 5) -> List[tuple]:
    """Find similar peers for a given user"""
    # Get all other users with embeddings
    query = text("""
        SELECT user_id, embedding
        FROM user_profiles
        WHERE user_id != :user_id AND embedding IS NOT NULL
    """)
    other_users = db.execute(query, {"user_id": user_id}).fetchall()
    
    # Calculate similarities
    similarities = []
    for other_user in other_users:
        try:
            # Parse the embedding string into a float array
            other_embedding = parse_embedding(other_user.embedding)
            if not other_embedding:
                continue
                
            # Ensure both embeddings are numpy arrays
            user_embedding = np.array(embedding, dtype=float)
            other_embedding = np.array(other_embedding, dtype=float)
            similarity = cosine_similarity(user_embedding, other_embedding)
            similarities.append((other_user.user_id, similarity))
        except Exception as e:
            logger.error(f"Error calculating similarity for user {other_user.user_id}: {str(e)}")
            continue
    
    # Sort by similarity and get top N
    similarities.sort(key=lambda x: x[1], reverse=True)
    return similarities[:top_n]

def update_suggested_peers(db, user_id: int, similar_peers: List[tuple]):
    """Update the suggested_peers table"""
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

def main(batch_size: int = 100, top_n: int = 5):
    """Main function to find and store similar peers"""
    try:
        # Create database session
        db = SessionLocal()
        
        # Get users with embeddings
        users = get_users_with_embeddings(db)
        logger.info(f"Found {len(users)} users with embeddings")
        
        # Process in batches
        for i in range(0, len(users), batch_size):
            batch = users[i:i + batch_size]
            logger.info(f"Processing batch {i//batch_size + 1}/{(len(users) + batch_size - 1)//batch_size}")
            
            for user in batch:
                try:
                    # Parse the embedding string into a float array
                    embedding = parse_embedding(user.embedding)
                    if not embedding:
                        logger.warning(f"Skipping user {user.user_id} due to invalid embedding")
                        continue
                        
                    # Find similar peers
                    similar_peers = find_similar_peers(db, user.user_id, embedding, top_n)
                    
                    # Update database
                    update_suggested_peers(db, user.user_id, similar_peers)
                    logger.info(f"Updated similar peers for user {user.user_id}")
                    
                except Exception as e:
                    logger.error(f"Error processing user {user.user_id}: {str(e)}")
                    continue
        
        logger.info("Similar peers generation completed")
        
    except Exception as e:
        logger.error(f"Error in main function: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Find similar peers based on embeddings')
    parser.add_argument('--batch-size', type=int, default=100,
                      help='Batch size for processing')
    parser.add_argument('--top-n', type=int, default=5,
                      help='Number of similar peers to find for each user')
    args = parser.parse_args()
    
    main(args.batch_size, args.top_n) 