import os
import pickle
import logging
from typing import Optional, Dict, Any
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import text
from sentence_transformers import SentenceTransformer

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Paths
MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")
FINETUNED_MODEL_PATH = os.path.join(MODEL_DIR, "finetuned_model_quantized")
PCA_MODEL_PATH = os.path.join(MODEL_DIR, "pca384_Siamese.pkl")
OHE_MODEL_PATH = os.path.join(MODEL_DIR, "ohe_Siamese.pkl")
SCALER_MODEL_PATH = os.path.join(MODEL_DIR, "scaler_Siamese.pkl")

# Load models properly
try:
    EMBEDDING_MODEL = SentenceTransformer(FINETUNED_MODEL_PATH)
    logger.info("Embedding model loaded successfully.")
except Exception as e:
    logger.error(f"Error loading embedding model: {str(e)}")
    EMBEDDING_MODEL = None

def load_pickle_model(path: str):
    try:
        with open(path, "rb") as f:
            return pickle.load(f)
    except Exception as e:
        logger.error(f"Error loading pickle model {path}: {str(e)}")
        return None

PCA_MODEL = load_pickle_model(PCA_MODEL_PATH)
OHE_MODEL = load_pickle_model(OHE_MODEL_PATH)
SCALER_MODEL = load_pickle_model(SCALER_MODEL_PATH)

# Preprocess, embed, etc. (your existing code can stay)


def preprocess_user_profile(profile_data: Dict[str, Any]) -> Optional[pd.DataFrame]:
    """
    Preprocess user profile data for embedding generation
    
    Args:
        profile_data: Dictionary containing user profile data
        
    Returns:
        Preprocessed DataFrame ready for embedding generation or None if preprocessing fails
    """
    try:
        # Create a DataFrame from user profile data
        # Adjust field names as needed based on your schema
        user_df = pd.DataFrame([{
            "job_title": profile_data.get("job_title", ""),
            "industry": profile_data.get("industry", ""),
            "skills": ",".join(profile_data.get("skills", [])),
            "years_experience": profile_data.get("years_experience", 0),
            "education_level": profile_data.get("education_level", ""),
            "interests": ",".join(profile_data.get("interests", [])),
            "career_goals": profile_data.get("career_goals", "")
        }])
        
        # Apply One-Hot Encoding
        if OHE_MODEL is not None:
            categorical_cols = ["job_title", "industry", "education_level"]
            for col in categorical_cols:
                if col in user_df.columns:
                    encoded_cols = OHE_MODEL.transform(user_df[[col]])
                    feature_names = OHE_MODEL.get_feature_names_out([col])
                    encoded_df = pd.DataFrame(encoded_cols, columns=feature_names)
                    user_df = pd.concat([user_df, encoded_df], axis=1)
                    user_df = user_df.drop(col, axis=1)
        
        # Apply scaling to numerical features
        if SCALER_MODEL is not None:
            numerical_cols = ["years_experience"]
            for col in numerical_cols:
                if col in user_df.columns:
                    user_df[col] = SCALER_MODEL.transform(user_df[[col]])
        
        return user_df
    except Exception as e:
        logger.error(f"Error preprocessing user profile data: {str(e)}")
        return None

def generate_embedding(profile_data: Dict[str, Any]) -> Optional[np.ndarray]:
    """
    Generate embedding for a user profile
    
    Args:
        profile_data: Dictionary containing user profile data
        
    Returns:
        Embedding vector or None if generation fails
    """
    if not MODELS_LOADED:
        logger.error("Models not loaded, cannot generate embedding")
        return None
    
    try:
        # Preprocess the profile data
        processed_data = preprocess_user_profile(profile_data)
        if processed_data is None:
            return None
        
        # Generate embedding with your fine-tuned model
        embedding = EMBEDDING_MODEL.predict(processed_data)
        
        # Apply PCA if needed
        if PCA_MODEL is not None:
            embedding = PCA_MODEL.transform(embedding.reshape(1, -1))
        
        return embedding.flatten()
    except Exception as e:
        logger.error(f"Error generating embedding: {str(e)}")
        return None

def store_embedding(db: Session, user_id: int, embedding: np.ndarray) -> bool:
    """
    Store user embedding in the database
    
    Args:
        db: Database session
        user_id: ID of the user
        embedding: Embedding vector
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Convert embedding to string for storage
        embedding_str = str(embedding.tolist())
        
        # Update user profile with embedding
        query = text("""
            UPDATE user_profiles
            SET embedding = :embedding
            WHERE user_id = :user_id
        """)
        
        db.execute(query, {"user_id": user_id, "embedding": embedding_str})
        db.commit()
        
        logger.info(f"Stored embedding for user {user_id}")
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"Error storing embedding: {str(e)}")
        return False

def process_user_embedding(db: Session, user_id: int, profile_data: Dict[str, Any]) -> bool:
    """
    Process user embedding generation and storage
    
    Args:
        db: Database session
        user_id: ID of the user
        profile_data: Dictionary containing user profile data
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Generate embedding
        embedding = generate_embedding(profile_data)
        if embedding is None:
            return False
        
        # Store embedding
        success = store_embedding(db, user_id, embedding)
        
        return success
    except Exception as e:
        logger.error(f"Error processing user embedding: {str(e)}")
        return False 