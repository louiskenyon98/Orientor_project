import os
import pickle
import logging
from typing import Optional, Dict, Any
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import text
from sentence_transformers import SentenceTransformer
import joblib
import boto3
from pathlib import Path

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment detection
IS_PRODUCTION = os.getenv('ENVIRONMENT', 'development').lower() == 'production'
S3_BUCKET = os.getenv("S3_BUCKET_NAME", "navigo-finetune-embedder-prod")

# Define model paths based on environment
if IS_PRODUCTION:
    # Production paths (AWS EB)
    MODELS_DIR = "/tmp/models"
    FINETUNED_MODEL_DIR = os.path.join(MODELS_DIR, "finetuned_model")
    PCA_MODEL_PATH = os.path.join(MODELS_DIR, "pca384_Siamese.pkl")
    SCALER_MODEL_PATH = os.path.join(MODELS_DIR, "scaler_Siamese.pkl")
    OHE_MODEL_PATH = os.path.join(MODELS_DIR, "ohe_Siamese.pkl")
else:
    # Development paths (local)
    MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 
                             "data_n_notebook", "siamese_pipeline", "mlruns", "models")
    FINETUNED_MODEL_DIR = os.path.join(MODELS_DIR, "finetuned_model")
    PCA_MODEL_PATH = os.path.join(MODELS_DIR, "pca384_Siamese.pkl")
    SCALER_MODEL_PATH = os.path.join(MODELS_DIR, "scaler_Siamese.pkl")
    OHE_MODEL_PATH = os.path.join(MODELS_DIR, "ohe_Siamese.pkl")

def ensure_model_directory():
    """Ensure the model directory exists in production."""
    if IS_PRODUCTION:
        Path(MODELS_DIR).mkdir(parents=True, exist_ok=True)
        Path(FINETUNED_MODEL_DIR).mkdir(parents=True, exist_ok=True)

def download_from_s3(s3_key: str, local_path: str):
    """Download a file from S3 to local path."""
    try:
        s3 = boto3.client('s3')
        s3.download_file(S3_BUCKET, s3_key, local_path)
        logger.info(f"Downloaded {s3_key} to {local_path}")
    except Exception as e:
        logger.error(f"Error downloading {s3_key}: {str(e)}")
        raise

def download_folder_from_s3(s3_prefix: str, local_dir: str):
    """Download a folder from S3 to local directory."""
    try:
        s3 = boto3.client('s3')
        paginator = s3.get_paginator('list_objects_v2')
        for page in paginator.paginate(Bucket=S3_BUCKET, Prefix=s3_prefix):
            for obj in page.get('Contents', []):
                key = obj['Key']
                filename = key.split('/')[-1]
                if filename:  # Avoid empty keys
                    local_file_path = os.path.join(local_dir, filename)
                    s3.download_file(S3_BUCKET, key, local_file_path)
        logger.info(f"Downloaded folder {s3_prefix} to {local_dir}")
    except Exception as e:
        logger.error(f"Error downloading folder {s3_prefix}: {str(e)}")
        raise

def load_models():
    """Load all models, downloading from S3 if in production."""
    global EMBEDDING_MODEL, PCA_MODEL, SCALER_MODEL, OHE_MODEL, MODELS_LOADED
    
    try:
        if IS_PRODUCTION:
            ensure_model_directory()
            # Download models from S3
            download_folder_from_s3("sentence_transformers/", FINETUNED_MODEL_DIR)
            download_from_s3("siamese_models/pca384_Siamese.pkl", PCA_MODEL_PATH)
            download_from_s3("siamese_models/scaler_Siamese.pkl", SCALER_MODEL_PATH)
            download_from_s3("siamese_models/ohe_Siamese.pkl", OHE_MODEL_PATH)

        # Load models
        EMBEDDING_MODEL = SentenceTransformer(FINETUNED_MODEL_DIR)
        logger.info("Embedding model loaded successfully")
        
        PCA_MODEL = joblib.load(PCA_MODEL_PATH)
        logger.info("PCA model loaded successfully")
        
        SCALER_MODEL = joblib.load(SCALER_MODEL_PATH)
        logger.info("Scaler model loaded successfully")
        
        OHE_MODEL = joblib.load(OHE_MODEL_PATH)
        logger.info("OHE model loaded successfully")
        
        MODELS_LOADED = True
        logger.info("All models loaded successfully")
        
    except Exception as e:
        logger.error(f"Error loading models: {str(e)}")
        EMBEDDING_MODEL = None
        PCA_MODEL = None
        SCALER_MODEL = None
        OHE_MODEL = None
        MODELS_LOADED = False

# Initialize models
EMBEDDING_MODEL = None
PCA_MODEL = None
SCALER_MODEL = None
OHE_MODEL = None
MODELS_LOADED = False

# Load models on module import
load_models()

# Load models locally
try:
    EMBEDDING_MODEL = SentenceTransformer(FINETUNED_MODEL_DIR)
    logger.info("Embedding model loaded successfully from local directory.")
except Exception as e:
    logger.error(f"Error loading embedding model: {str(e)}")
    EMBEDDING_MODEL = None

try:
    PCA_MODEL = joblib.load(PCA_MODEL_PATH)
    logger.info("PCA model loaded successfully from local directory.")
except Exception as e:
    logger.error(f"Error loading PCA model: {str(e)}")
    PCA_MODEL = None

try:
    SCALER_MODEL = joblib.load(SCALER_MODEL_PATH)
    logger.info("Scaler model loaded successfully from local directory.")
except Exception as e:
    logger.error(f"Error loading scaler model: {str(e)}")
    SCALER_MODEL = None

try:
    OHE_MODEL = joblib.load(OHE_MODEL_PATH)
    logger.info("OHE model loaded successfully from local directory.")
    # Print the expected feature names
    if hasattr(OHE_MODEL, 'get_feature_names_out'):
        feature_names = OHE_MODEL.get_feature_names_out()
        logger.info(f"OHE model expects features: {feature_names}")
        # Extract original column names
        original_cols = set()
        for feature in feature_names:
            col_name = feature.split('_')[0]
            original_cols.add(col_name)
        logger.info(f"Original columns needed: {original_cols}")
except Exception as e:
    logger.error(f"Error loading OHE model: {str(e)}")
    OHE_MODEL = None

# Flag to check if models loaded
MODELS_LOADED = all([EMBEDDING_MODEL, PCA_MODEL, OHE_MODEL, SCALER_MODEL])
logger.info(f"All models loaded: {MODELS_LOADED}")

# --- Core Functions ---

def preprocess_user_profile(profile_data: Dict[str, Any]) -> Optional[pd.DataFrame]:
    """
    Preprocess user profile data for embedding generation.
    Only uses career-related fields for embedding generation.
    """
    try:
        # Debug logging
        logger.info(f"Received profile data keys: {list(profile_data.keys())}")
        
        # Create DataFrame with only career-related fields
        user_df = pd.DataFrame([{
            "Job Title": profile_data.get("job_title", "Unknown"),
            "Industry": profile_data.get("industry", "Unknown"),
            "Years Experience": profile_data.get("years_experience", 0),
            "Education Level": profile_data.get("education_level", "Unknown"),
            "Career Goals": profile_data.get("career_goals", ""),
            "Skills": ",".join(profile_data.get("skills", [])),
            "Interests": ",".join(profile_data.get("interests", []))
        }])
        
        # Debug logging
        logger.info(f"Created DataFrame with columns: {list(user_df.columns)}")
        return user_df
    except Exception as e:
        logger.error(f"Error preprocessing user profile data: {str(e)}")
        return None

def generate_embedding(profile_data: Dict[str, Any]) -> Optional[np.ndarray]:
    """
    Generate embedding for a user profile.
    Returns a 384-dimensional embedding from SentenceTransformer.
    """
    if not MODELS_LOADED:
        logger.error("Models not loaded, cannot generate embedding.")
        return None

    try:
        processed_data = preprocess_user_profile(profile_data)
        if processed_data is None:
            return None

        # Convert DataFrame to text for SentenceTransformer
        text_data = " ".join([
            f"Job Title: {processed_data['Job Title'].iloc[0]}",
            f"Industry: {processed_data['Industry'].iloc[0]}",
            f"Years Experience: {processed_data['Years Experience'].iloc[0]}",
            f"Education Level: {processed_data['Education Level'].iloc[0]}",
            f"Career Goals: {processed_data['Career Goals'].iloc[0]}",
            f"Skills: {processed_data['Skills'].iloc[0]}",
            f"Interests: {processed_data['Interests'].iloc[0]}"
        ])

        # Generate embedding using SentenceTransformer's encode method
        embedding = EMBEDDING_MODEL.encode(text_data)
        return embedding

    except Exception as e:
        logger.error(f"Error generating embedding: {str(e)}")
        return None

def store_embedding(db: Session, user_id: int, embedding: np.ndarray) -> bool:
    """
    Store user embedding in the database.
    """
    try:
        # Convert numpy array to list for storage
        embedding_list = embedding.tolist()
        
        # Update the user's profile with the embedding
        db.execute(
            text("""
                UPDATE user_profiles 
                SET embedding = :embedding 
                WHERE user_id = :user_id
            """),
            {"embedding": embedding_list, "user_id": user_id}
        )
        db.commit()
        
        logger.info(f"Successfully stored embedding for user {user_id}")
        return True
    except Exception as e:
        logger.error(f"Error storing embedding: {str(e)}")
        db.rollback()
        return False

def process_user_embedding(db: Session, user_id: int, profile_data: Dict[str, Any]) -> bool:
    """
    Process user embedding generation and storage.
    """
    try:
        embedding = generate_embedding(profile_data)
        if embedding is None:
            return False

        # Store the embedding in the database
        return store_embedding(db, user_id, embedding)
    except Exception as e:
        logger.error(f"Error processing user embedding: {str(e)}")
        return False