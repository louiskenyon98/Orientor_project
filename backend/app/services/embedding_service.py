import os
import logging
import numpy as np
import pandas as pd
import pickle
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Path to ML models
MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")
EMBEDDING_MODEL_PATH = os.path.join(MODEL_DIR, "finetuned_model_quantized")
PCA_MODEL_PATH = os.path.join(MODEL_DIR, "pca_model.pkl")
OHE_MODEL_PATH = os.path.join(MODEL_DIR, "ohe_model.pkl")
SCALER_MODEL_PATH = os.path.join(MODEL_DIR, "scaler_model.pkl")

# Load models if they exist
try:
    with open(EMBEDDING_MODEL_PATH, 'rb') as f:
        EMBEDDING_MODEL = pickle.load(f)
    with open(PCA_MODEL_PATH, 'rb') as f:
        PCA_MODEL = pickle.load(f)
    with open(OHE_MODEL_PATH, 'rb') as f:
        OHE_MODEL = pickle.load(f)
    with open(SCALER_MODEL_PATH, 'rb') as f:
        SCALER_MODEL = pickle.load(f)
    
    logger.info("All embedding models loaded successfully")
    MODELS_LOADED = True
except Exception as e:
    logger.error(f"Error loading embedding models: {str(e)}")
    MODELS_LOADED = False

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