#!/usr/bin/env python3
import os
import shutil
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def copy_models():
    """Copy fine-tuned models to the backend directory"""
    # Define source and destination paths
    src_base_path = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
                                            "data_n_notebook", "siamese_pipeline", "mlruns", "models"))
    dest_base_path = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models"))
    
    # Create destination directory if it doesn't exist
    os.makedirs(dest_base_path, exist_ok=True)
    
    # Copy individual model files
    model_files = {
        "pca384_Siamese.pkl": "pca384_Siamese.pkl",
        "scaler_Siamese.pkl": "scaler_Siamese.pkl",
        "ohe_Siamese.pkl": "ohe_Siamese.pkl"
    }
    
    for src_name, dest_name in model_files.items():
        src_path = os.path.join(src_base_path, src_name)
        dest_path = os.path.join(dest_base_path, dest_name)
        
        if os.path.exists(src_path):
            logger.info(f"Copying {src_name} to {dest_path}")
            shutil.copy2(src_path, dest_path)
        else:
            logger.error(f"Source file not found: {src_path}")
    
    # Copy finetuned model directory
    src_model_path = os.path.join(src_base_path, "finetuned_model")
    dest_model_path = os.path.join(dest_base_path, "finetuned_model")
    
    if os.path.exists(src_model_path):
        if os.path.exists(dest_model_path):
            logger.info(f"Removing existing destination directory: {dest_model_path}")
            shutil.rmtree(dest_model_path)
        
        logger.info(f"Copying finetuned_model directory to {dest_model_path}")
        shutil.copytree(src_model_path, dest_model_path)
    else:
        logger.error(f"Source directory not found: {src_model_path}")
    
    logger.info("Model copying completed.")

if __name__ == "__main__":
    copy_models() 