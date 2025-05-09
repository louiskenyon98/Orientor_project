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
from app.services.embedding_service import generate_embedding, store_embedding
from app.models import UserProfile

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

def generate_embeddings_for_all_users():
    """Generate embeddings for all users in the database."""
    try:
        db = SessionLocal()
        profiles = db.query(UserProfile).all()
        
        logger.info(f"Found {len(profiles)} profiles to process")
        
        for profile in profiles:
            try:
                # Create profile data dictionary
                profile_data = {
                    "name": profile.name,
                    "age": profile.age,
                    "sex": profile.sex,
                    "major": profile.major,
                    "year": profile.year,
                    "gpa": profile.gpa,
                    "hobbies": profile.hobbies,
                    "country": profile.country,
                    "state_province": profile.state_province,
                    "unique_quality": profile.unique_quality,
                    "story": profile.story,
                    "favorite_movie": profile.favorite_movie,
                    "favorite_book": profile.favorite_book,
                    "favorite_celebrities": profile.favorite_celebrities,
                    "learning_style": profile.learning_style,
                    "interests": profile.interests,
                    "job_title": profile.job_title,
                    "industry": profile.industry,
                    "years_experience": profile.years_experience,
                    "education_level": profile.education_level,
                    "career_goals": profile.career_goals,
                    "skills": profile.skills
                }
                
                # Generate embedding
                embedding = generate_embedding(profile_data)
                if embedding is not None:
                    # Store embedding
                    success = store_embedding(db, profile.user_id, embedding)
                    if success:
                        logger.info(f"Successfully generated and stored embedding for user {profile.user_id}")
                    else:
                        logger.error(f"Failed to store embedding for user {profile.user_id}")
                else:
                    logger.error(f"Failed to generate embedding for user {profile.user_id}")
                    
            except Exception as e:
                logger.error(f"Error processing profile for user {profile.user_id}: {str(e)}")
                continue
        
        logger.info("Finished processing all profiles")
        
    except Exception as e:
        logger.error(f"Error in generate_embeddings_for_all_users: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    generate_embeddings_for_all_users() 