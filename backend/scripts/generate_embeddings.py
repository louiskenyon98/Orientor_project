#!/usr/bin/env python3

import sys
import os
import argparse
import logging
from pathlib import Path
from typing import List, Optional
import numpy as np
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

# Add the parent directory to sys.path
current_dir = Path(__file__).resolve().parent
parent_dir = current_dir.parent
sys.path.append(str(parent_dir))

from app.utils.database import SessionLocal
from app.utils.embeddings import (
    generate_and_store_embeddings,
    find_and_store_similar_peers,
    refresh_all_embeddings_and_peers
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_user_profiles(db):
    """Get all user profiles that need embeddings"""
    query = text("""
        SELECT user_id, name, age, sex, major, year, gpa, hobbies, 
               country, state_province, unique_quality, story
        FROM user_profiles
        WHERE embedding IS NULL
    """)
    return db.execute(query).fetchall()

def generate_embedding(text: str, model) -> List[float]:
    """Generate embedding for a given text using the model"""
    if not text:
        return None
    return model.encode([text])[0].tolist()

def update_user_embedding(db, user_id: int, embedding: List[float]):
    """Update the embedding for a user"""
    # Convert the embedding to a PostgreSQL vector string
    vector_str = "[" + ",".join(str(x) for x in embedding) + "]"
    query = text("""
        UPDATE user_profiles
        SET embedding = :embedding
        WHERE user_id = :user_id
    """)
    db.execute(query, {"embedding": vector_str, "user_id": user_id})
    db.commit()

def main(model_name: str = 'sentence-transformers/all-MiniLM-L6-v2'):
    """Main function to generate and store embeddings"""
    try:
        # Initialize the model
        logger.info(f"Loading model: {model_name}")
        model = SentenceTransformer(model_name)
        
        # Create database session
        db = SessionLocal()
        
        # Get user profiles
        profiles = get_user_profiles(db)
        logger.info(f"Found {len(profiles)} profiles to process")
        
        # Process each profile
        for profile in profiles:
            try:
                # Combine all available text fields
                text_fields = []
                
                # Add basic profile information
                if profile.name:
                    text_fields.append(f"Name: {profile.name}")
                if profile.major:
                    text_fields.append(f"Major: {profile.major}")
                if profile.year:
                    text_fields.append(f"Year: {profile.year}")
                if profile.gpa:
                    text_fields.append(f"GPA: {profile.gpa}")
                
                # Add interests and hobbies
                if profile.hobbies:
                    text_fields.append(f"Hobbies: {profile.hobbies}")
                
                # Add location information
                if profile.country:
                    text_fields.append(f"Country: {profile.country}")
                if profile.state_province:
                    text_fields.append(f"State/Province: {profile.state_province}")
                
                # Add personal information
                if profile.unique_quality:
                    text_fields.append(f"Unique Quality: {profile.unique_quality}")
                if profile.story:
                    text_fields.append(f"Story: {profile.story}")
                
                # Combine all text fields
                text = " ".join(text_fields)
                
                if not text.strip():
                    logger.warning(f"No data available for user {profile.user_id}")
                    continue
                
                # Generate embedding
                embedding = generate_embedding(text, model)
                if embedding:
                    # Update database
                    update_user_embedding(db, profile.user_id, embedding)
                    logger.info(f"Updated embedding for user {profile.user_id} with text: {text[:100]}...")
                else:
                    logger.warning(f"Could not generate embedding for user {profile.user_id}")
                    
            except Exception as e:
                logger.error(f"Error processing user {profile.user_id}: {str(e)}")
                logger.error(f"Text fields: {text_fields}")
                continue
        
        logger.info("Embedding generation completed")
        
    except Exception as e:
        logger.error(f"Error in main function: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate embeddings for user profiles')
    parser.add_argument('--model', type=str, default='sentence-transformers/all-MiniLM-L6-v2',
                      help='Sentence transformer model to use')
    args = parser.parse_args()
    
    main(args.model) 