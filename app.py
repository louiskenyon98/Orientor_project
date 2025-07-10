# Minimal Railway-compatible FastAPI app
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the FastAPI app
app = FastAPI(
    title="Orientor Backend - Railway",
    description="Minimal FastAPI backend for Railway deployment",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://navigo-explorer.vercel.app",
        "https://*.vercel.app", 
        "https://*.railway.app",
        "http://localhost:3000",
        "http://localhost:8000"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    logger.info("Root endpoint called")
    return {
        "message": "✅ Orientor Backend is running on Railway!",
        "status": "success",
        "version": "1.0.0",
        "environment": os.getenv("RAILWAY_ENVIRONMENT", "development"),
        "timestamp": datetime.utcnow().isoformat(),
        "port": os.getenv("PORT", "8000")
    }

@app.get("/health")
async def health_check():
    logger.info("Health check called")
    return {
        "status": "healthy",
        "service": "orientor-backend",
        "environment": os.getenv("RAILWAY_ENVIRONMENT", "development"),
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/health")
async def api_health():
    logger.info("API health check called")
    return {
        "status": "ok",
        "api_version": "v1",
        "timestamp": datetime.utcnow().isoformat(),
        "endpoints": ["health", "auth", "status"]
    }

@app.post("/api/auth/login")
async def login():
    logger.info("Login endpoint called")
    return {
        "message": "Login endpoint working",
        "token": "test-token-12345",
        "user": {"id": 1, "name": "Test User", "email": "test@orientor.com"}
    }

@app.get("/api/auth/me")
async def get_me():
    logger.info("User profile endpoint called")
    return {
        "id": 1,
        "name": "Test User",
        "email": "test@orientor.com",
        "role": "user"
    }

# Startup logging
@app.on_event("startup")
async def startup_event():
    port = os.getenv('PORT', '8000')
    logger.info("🚀 Orientor Backend starting up on Railway")
    logger.info(f"Environment: {os.getenv('RAILWAY_ENVIRONMENT', 'development')}")
    logger.info(f"Port from env: {port}")
    logger.info(f"Railway Service: {os.getenv('RAILWAY_SERVICE_NAME', 'unknown')}")
    logger.info(f"Railway Domain: {os.getenv('RAILWAY_PUBLIC_DOMAIN', 'unknown')}")
    logger.info("✅ App should be accessible at Railway domain")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)