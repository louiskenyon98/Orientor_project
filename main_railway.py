# Railway-optimized entry point for Orientor Backend
import sys
import os
import logging
from pathlib import Path

# Configure logging for Railway
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Add backend to Python path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

try:
    # Try to import the minimal deployment app first
    logger.info("🔍 Attempting to import minimal deployment app...")
    from main_deploy import app
    logger.info("✅ Successfully imported minimal FastAPI app from main_deploy")
except ImportError as e:
    logger.warning(f"⚠️ Could not import main_deploy: {e}")
    try:
        # Fallback to backend main app
        logger.info("🔍 Attempting to import full backend app...")
        from app.main import app
        logger.info("✅ Successfully imported full FastAPI app from backend")
    except ImportError as e2:
        logger.error(f"❌ Could not import backend app: {e2}")
        # Create a basic working app
        from fastapi import FastAPI
        from fastapi.middleware.cors import CORSMiddleware
        
        app = FastAPI(title="Orientor Railway Fallback")
        
        # Configure CORS
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE"],
            allow_headers=["*"],
        )
        
        @app.get("/")
        def fallback_root():
            return {
                "message": "Orientor Backend Fallback - Import Error",
                "error": str(e2),
                "status": "fallback_active"
            }
        
        @app.get("/health")
        def fallback_health():
            return {"status": "healthy", "mode": "fallback"}
        
        @app.get("/api/health")
        def fallback_api_health():
            return {"status": "ok", "mode": "fallback"}
        
        logger.info("✅ Created fallback FastAPI app")

if __name__ == "__main__":
    import uvicorn
    
    # Get Railway configuration
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0"
    
    logger.info(f"🚀 Railway Main Entry - Starting on {host}:{port}")
    logger.info(f"Environment: {os.environ.get('RAILWAY_ENVIRONMENT', 'development')}")
    logger.info(f"Service ID: {os.environ.get('RAILWAY_SERVICE_ID', 'unknown')}")
    
    # Start the server
    uvicorn.run(
        app, 
        host=host, 
        port=port,
        log_level="info",
        access_log=True
    )