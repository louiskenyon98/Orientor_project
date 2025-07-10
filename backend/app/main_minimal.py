from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
import logging

# Import only essential routers that exist
from app.routers.user import router as auth_router, get_current_user
from app.routers.test import router as test_router

from fastapi import FastAPI, HTTPException
from pathlib import Path
from logging.handlers import RotatingFileHandler

# Set up basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Navigo API",
    description="API for the Navigo Career and Skill Tree Explorer",
    version="0.1.0",
)

# Configure CORS
origins = [
    "http://localhost:3000",
    "http://localhost:8000",
    "https://navigoproject-lluvse7tj-philippe-beliveaus-projects.vercel.app",
    "https://*.up.railway.app",
    "https://*.railway.app",
    "https://*.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600,
)

# Include minimal routers
app.include_router(auth_router)
app.include_router(test_router)

@app.get("/")
async def root():
    logger.info("Root endpoint called")
    return {"message": "Welcome to the Navigo API. Go to /docs for API documentation."}

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Backend is running"}

# For Railway deployment
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)