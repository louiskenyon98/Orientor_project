import os
import time
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_models():
    """Load all required models and mark completion."""
    try:
        # Create loading flag
        loading_flag = Path("/app/.model_loading")
        loading_flag.touch()
        
        logger.info("Starting model loading...")
        
        # Load SentenceTransformer models
        from sentence_transformers import SentenceTransformer
        logger.info("Loading SentenceTransformer models...")
        model_path = Path("/app/models/sentence_transformer")
        if not model_path.exists():
            logger.error("Model directory not found!")
            return False
            
        # Load quantized model
        quantized_model = SentenceTransformer(str(model_path / "quantized"))
        logger.info("Loaded quantized model")
        
        # Load normal model
        normal_model = SentenceTransformer(str(model_path / "normal"))
        logger.info("Loaded normal model")
        
        # Load other models
        import joblib
        logger.info("Loading PCA, OHE, and Scaler models...")
        pca = joblib.load(str(model_path / "pca.pkl"))
        ohe = joblib.load(str(model_path / "ohe.pkl"))
        scaler = joblib.load(str(model_path / "scaler.pkl"))
        
        logger.info("All models loaded successfully!")
        
        # Remove loading flag
        loading_flag.unlink()
        return True
        
    except Exception as e:
        logger.error(f"Error loading models: {str(e)}")
        return False

if __name__ == "__main__":
    load_models() 