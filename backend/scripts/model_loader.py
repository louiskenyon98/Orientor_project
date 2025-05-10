import os
import logging
import boto3
import tempfile
from pathlib import Path
import pickle
import shutil
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants from environment variables
MODEL_BUCKET = os.environ.get("MODEL_BUCKET", "navigo-finetune-embedder-prod")
EMBEDDING_S3_PATH = os.environ.get("EMBEDDING_S3_PATH", "sentence_transformers/")
OHE_MODEL_PATH = os.environ.get("OHE_MODEL_PATH", "siamese_models/ohe_Siamese.pkl")
PCA_MODEL_PATH = os.environ.get("PCA_MODEL_PATH", "siamese_models/pca384_Siamese.pkl")
SCALER_MODEL_PATH = os.environ.get("SCALER_MODEL_PATH", "siamese_models/scaler_Siamese.pkl")

# Global model storage
models = {}

def download_directory_from_s3(bucket, s3_path, local_dir):
    """
    Download entire directory structure from S3 to a local directory
    """
    s3_client = boto3.client('s3')
    logger.info(f"Downloading directory from s3://{bucket}/{s3_path} to {local_dir}")
    
    try:
        # List objects in the directory
        paginator = s3_client.get_paginator('list_objects_v2')
        result = paginator.paginate(Bucket=bucket, Prefix=s3_path)
        
        # Create local directory if it doesn't exist
        os.makedirs(local_dir, exist_ok=True)
        
        # Download each file while preserving directory structure
        download_count = 0
        for page in result:
            if "Contents" in page:
                for obj in page["Contents"]:
                    # Get relative path
                    rel_path = obj["Key"][len(s3_path):].lstrip('/')
                    if not rel_path:  # Skip the directory itself
                        continue
                    
                    # Create local subdirectories if needed
                    local_file_path = os.path.join(local_dir, rel_path)
                    os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
                    
                    # Download the file
                    s3_client.download_file(bucket, obj["Key"], local_file_path)
                    download_count += 1
        
        logger.info(f"Successfully downloaded {download_count} files from S3 to {local_dir}")
        return True
    except Exception as e:
        logger.error(f"Error downloading directory from S3: {str(e)}")
        return False

def download_pickle_from_s3(bucket, s3_path, local_path):
    """
    Download a pickle file from S3
    """
    s3_client = boto3.client('s3')
    logger.info(f"Downloading pickle file from s3://{bucket}/{s3_path} to {local_path}")
    
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        
        # Download file
        s3_client.download_file(bucket, s3_path, local_path)
        logger.info(f"Successfully downloaded {s3_path}")
        return True
    except Exception as e:
        logger.error(f"Error downloading pickle from S3: {str(e)}")
        return False

def load_models():
    """Load all required models from S3 at runtime"""
    start_time = time.time()
    logger.info("Starting model loading from S3...")
    
    try:
        # Create /tmp directory structure
        tmp_model_dir = "/tmp/finetuned_model"
        tmp_pkl_dir = "/tmp/pkl_models"
        os.makedirs(tmp_model_dir, exist_ok=True)
        os.makedirs(tmp_pkl_dir, exist_ok=True)
        
        # Record model loading started
        Path("/tmp/.model_loading").touch()
        
        # 1. Download SentenceTransformer model folder from S3
        if download_directory_from_s3(MODEL_BUCKET, EMBEDDING_S3_PATH, tmp_model_dir):
            logger.info(f"SentenceTransformer model downloaded to {tmp_model_dir}")
            try:
                # Import here to avoid loading before models are ready
                from sentence_transformers import SentenceTransformer
                models['sentence_transformer'] = SentenceTransformer(tmp_model_dir)
                logger.info("SentenceTransformer model loaded successfully")
            except Exception as e:
                logger.error(f"Error loading SentenceTransformer model: {str(e)}")
        
        # 2. Download and load pickle models
        pkl_files = {
            'ohe': OHE_MODEL_PATH,
            'pca': PCA_MODEL_PATH,
            'scaler': SCALER_MODEL_PATH
        }
        
        for model_name, s3_path in pkl_files.items():
            local_path = f"/tmp/pkl_models/{os.path.basename(s3_path)}"
            if download_pickle_from_s3(MODEL_BUCKET, s3_path, local_path):
                try:
                    with open(local_path, 'rb') as f:
                        models[model_name] = pickle.load(f)
                    logger.info(f"Successfully loaded {model_name} model")
                except Exception as e:
                    logger.error(f"Error loading {model_name} model: {str(e)}")
        
        # Remove loading flag
        loading_flag = Path("/tmp/.model_loading")
        if loading_flag.exists():
            loading_flag.unlink()
        
        logger.info(f"Model loading completed in {time.time() - start_time:.2f} seconds")
        return models
    except Exception as e:
        logger.error(f"Error in load_models: {str(e)}")
        # Don't raise the exception, just log it
        return {}

def get_model(model_name):
    """Get a loaded model by name"""
    return models.get(model_name)

if __name__ == "__main__":
    load_models() 