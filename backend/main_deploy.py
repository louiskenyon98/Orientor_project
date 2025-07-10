from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
import logging
from datetime import datetime
from pathlib import Path

# Configure logging for Railway
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Railway captures stdout/stderr
    ]
)
logger = logging.getLogger(__name__)

# Create a production-ready FastAPI app
app = FastAPI(
    title="Orientor Backend - Railway Deploy",
    description="Production FastAPI backend for Orientor career platform",
    version="2.0.0",
    docs_url="/docs" if os.getenv("ENV") != "production" else None,  # Disable docs in production
    redoc_url="/redoc" if os.getenv("ENV") != "production" else None
)

# Configure static files safely
static_path = Path(__file__).parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")
    logger.info(f"Static files mounted from {static_path}")
else:
    logger.warning(f"Static directory not found at {static_path}")

# Configure CORS with Railway-specific origins
origins = [
    "https://navigo-explorer.vercel.app",
    "https://*.vercel.app",
    "https://*.up.railway.app",
    "https://*.railway.app",
    "http://localhost:3000",
    "http://localhost:8000",
    "https://localhost:3000",
]

# Add wildcard for Railway domains if in production
if os.getenv("RAILWAY_ENVIRONMENT") == "production":
    origins.append("*")  # Allow all origins in Railway production for now

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600,
)

# Health check endpoints for Railway
@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {
        "message": "Orientor Backend is running on Railway!",
        "status": "success",
        "version": "2.0.0",
        "environment": os.getenv("RAILWAY_ENVIRONMENT", "unknown"),
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for Railway monitoring"""
    try:
        # Basic health check
        return {
            "status": "healthy",
            "service": "orientor-backend",
            "environment": os.getenv("RAILWAY_ENVIRONMENT", "development"),
            "port": os.getenv("PORT", "8000"),
            "timestamp": datetime.utcnow().isoformat(),
            "uptime": "Railway managed"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

@app.get("/api/health")
async def api_health():
    """API-specific health check with database status"""
    try:
        # Check database health
        database_status = "not_connected"
        try:
            # Import database health check function
            from app.utils.database import check_database_health, database_connected
            if check_database_health():
                database_status = "connected"
            elif database_connected:
                database_status = "connected_but_unstable"
            else:
                database_status = "not_connected"
        except ImportError:
            database_status = "not_configured"
        except Exception as db_e:
            database_status = f"error: {str(db_e)[:50]}"
        
        return {
            "status": "ok", 
            "api_version": "v1",
            "endpoints": ["health", "auth", "status"],
            "database": database_status,
            "environment": os.getenv("RAILWAY_ENVIRONMENT", "development"),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"API health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail=f"API unhealthy: {str(e)}")

# Authentication endpoints for frontend compatibility
@app.post("/api/auth/login")
async def login():
    """Mock login endpoint for frontend testing"""
    logger.info("Login endpoint accessed")
    return {
        "message": "Login endpoint working on Railway",
        "token": "railway-test-token-12345",
        "user": {
            "id": 1, 
            "name": "Railway Test User",
            "email": "test@orientor-railway.com"
        },
        "environment": os.getenv("RAILWAY_ENVIRONMENT", "development")
    }

@app.get("/api/auth/me")
async def get_me():
    """Mock user profile endpoint"""
    logger.info("User profile endpoint accessed")
    return {
        "id": 1,
        "name": "Railway Test User", 
        "email": "test@orientor-railway.com",
        "role": "user",
        "platform": "railway",
        "timestamp": datetime.utcnow().isoformat()
    }

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    logger.warning(f"404 error for path: {request.url.path}")
    return {
        "error": "Not Found",
        "path": str(request.url.path),
        "message": "The requested endpoint was not found",
        "status_code": 404
    }

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"500 error for path: {request.url.path}, error: {str(exc)}")
    return {
        "error": "Internal Server Error",
        "path": str(request.url.path),
        "message": "An internal server error occurred",
        "status_code": 500
    }

# Startup event
@app.on_event("startup")
async def startup_event():
    """Application startup configuration"""
    try:
        logger.info("🚀 Starting Orientor Backend on Railway")
        logger.info(f"Environment: {os.getenv('RAILWAY_ENVIRONMENT', 'development')}")
        logger.info(f"Port: {os.getenv('PORT', '8000')}")
        logger.info(f"Railway Service ID: {os.getenv('RAILWAY_SERVICE_ID', 'unknown')}")
        logger.info("✅ Application startup completed successfully")
    except Exception as e:
        logger.error(f"❌ Error during startup: {str(e)}")
        # Don't fail startup - let Railway handle the error

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown cleanup"""
    logger.info("🛑 Shutting down Orientor Backend")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0"
    
    logger.info(f"🚀 Starting Orientor Backend on {host}:{port}")
    logger.info(f"Railway Environment: {os.getenv('RAILWAY_ENVIRONMENT', 'development')}")
    
    uvicorn.run(
        app, 
        host=host, 
        port=port,
        log_level="info",
        access_log=True
    )