#!/usr/bin/env python3
"""
Verification script for S3 model access and loading
This script checks if we can:
1. Connect to S3
2. List objects in the model bucket
3. Download model files
4. Load a small portion of the models to verify they're valid
"""

import os
import sys
import time
import boto3
import logging
from pathlib import Path
import pickle
import tempfile
import shutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("verify_s3_models")

# Environment variables
MODEL_BUCKET = os.environ.get("MODEL_BUCKET", "navigo-finetune-embedder-prod")
EMBEDDING_S3_PATH = os.environ.get("EMBEDDING_S3_PATH", "sentence_transformers/")
OHE_MODEL_PATH = os.environ.get("OHE_MODEL_PATH", "siamese_models/ohe_Siamese.pkl")
PCA_MODEL_PATH = os.environ.get("PCA_MODEL_PATH", "siamese_models/pca384_Siamese.pkl")
SCALER_MODEL_PATH = os.environ.get("SCALER_MODEL_PATH", "siamese_models/scaler_Siamese.pkl")

def check_s3_connection():
    """Check if we can connect to S3 and list objects in the bucket"""
    try:
        logger.info(f"Checking S3 connection to bucket: {MODEL_BUCKET}")
        s3_client = boto3.client('s3')
        response = s3_client.list_objects_v2(
            Bucket=MODEL_BUCKET,
            MaxKeys=1
        )
        if 'Contents' in response:
            logger.info(f"Successfully connected to S3 bucket {MODEL_BUCKET}")
            return True
        else:
            logger.warning(f"Connected to S3 bucket {MODEL_BUCKET}, but it appears to be empty")
            return False
    except Exception as e:
        logger.error(f"Failed to connect to S3: {str(e)}")
        return False

def check_model_files():
    """Check if we can access the model files in S3"""
    try:
        logger.info(f"Checking S3 access to model files")
        s3_client = boto3.client('s3')
        
        # Check SentenceTransformer directory
        st_path = EMBEDDING_S3_PATH
        logger.info(f"Checking SentenceTransformer directory: {st_path}")
        st_response = s3_client.list_objects_v2(
            Bucket=MODEL_BUCKET,
            Prefix=st_path,
            MaxKeys=5
        )
        
        if 'Contents' in st_response:
            logger.info(f"Found {len(st_response['Contents'])} objects in SentenceTransformer directory")
            for item in st_response['Contents'][:3]:  # Show first 3 only
                logger.info(f"  - {item['Key']} ({item['Size']} bytes)")
        else:
            logger.error(f"No objects found in SentenceTransformer directory: {st_path}")
            return False
        
        # Check each pickle file
        pickle_files = [OHE_MODEL_PATH, PCA_MODEL_PATH, SCALER_MODEL_PATH]
        for pkl_path in pickle_files:
            logger.info(f"Checking pickle file: {pkl_path}")
            try:
                # Check if file exists
                s3_client.head_object(Bucket=MODEL_BUCKET, Key=pkl_path)
                logger.info(f"  - File exists: {pkl_path}")
            except Exception as e:
                logger.error(f"  - Error accessing {pkl_path}: {str(e)}")
                return False
        
        logger.info("All model files appear to be accessible")
        return True
    except Exception as e:
        logger.error(f"Error checking model files: {str(e)}")
        return False

def test_download_model():
    """Try to download a small sample file to verify access"""
    try:
        logger.info("Testing model download capability")
        s3_client = boto3.client('s3')
        
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Try to download a single pickle file (smallest one if known)
            target_file = OHE_MODEL_PATH
            target_path = temp_path / "test_model.pkl"
            
            logger.info(f"Downloading {target_file} to {target_path}")
            start_time = time.time()
            s3_client.download_file(MODEL_BUCKET, target_file, str(target_path))
            download_time = time.time() - start_time
            
            # Check file size
            file_size = target_path.stat().st_size
            logger.info(f"Downloaded file size: {file_size} bytes in {download_time:.2f} seconds")
            
            # Try to load the model to verify integrity
            if target_path.exists() and file_size > 0:
                logger.info("Testing if file can be loaded with pickle...")
                try:
                    with open(target_path, 'rb') as f:
                        model = pickle.load(f)
                    logger.info(f"Successfully loaded pickle file")
                    logger.info(f"Model type: {type(model)}")
                    return True
                except Exception as e:
                    logger.error(f"Error loading pickle file: {str(e)}")
                    return False
            else:
                logger.error(f"Downloaded file is empty or missing")
                return False
    except Exception as e:
        logger.error(f"Error during model download test: {str(e)}")
        return False

def main():
    """Run all verification checks"""
    logger.info("Starting S3 model verification")
    
    # Check environment variables
    logger.info("Checking environment variables...")
    for var_name in ["MODEL_BUCKET", "EMBEDDING_S3_PATH", "OHE_MODEL_PATH", "PCA_MODEL_PATH", "SCALER_MODEL_PATH"]:
        value = os.environ.get(var_name)
        if value:
            logger.info(f"  {var_name} = {value}")
        else:
            logger.warning(f"  {var_name} is not set, using default value")
    
    # Run verification steps
    steps = [
        ("S3 Connection", check_s3_connection),
        ("Model Files Check", check_model_files),
        ("Model Download Test", test_download_model),
    ]
    
    success = True
    for step_name, step_func in steps:
        logger.info(f"\n=== {step_name} ===")
        if step_func():
            logger.info(f"✓ {step_name} - PASSED")
        else:
            logger.error(f"✗ {step_name} - FAILED")
            success = False
    
    # Overall result
    logger.info("\n=== Verification Results ===")
    if success:
        logger.info("✅ All verification steps PASSED. S3 model access appears to be working correctly.")
        return 0
    else:
        logger.error("❌ Some verification steps FAILED. Please check the logs for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 