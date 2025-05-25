from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import logging

# Import routers directly
from app.routers.user import router as auth_router, get_current_user
from app.routers.users import router as users_router
from app.routers.chat import router as chat_router
from app.routers.peers import router as peers_router
from app.routers.messages import router as messages_router
from app.routers.profiles import router as profiles_router
from app.routers.test import router as test_router
from app.routers.space import router as space_router
from app.routers.vector_search import router as vector_router
from app.routers.recommendations import router as recommendations_router
from app.routers.careers import router as careers_router
from app.routers.tree import router as tree_router  # Import the new tree router
from app.routers.tree_paths import router as tree_paths_router  # Import tree paths router
from app.routers.node_notes import router as node_notes_router  # Import node notes router
from app.routers.user_progress import router as user_progress_router  # Import user progress router
from app.routers.holland_test import router as holland_test_router  # Import Holland test router
from app.routers.insight_router import router as insight_router  # Import insight router
from fastapi import FastAPI, HTTPException
from pathlib import Path
from scripts.model_loader import load_models
from logging.handlers import RotatingFileHandler
from app.api.api import api_router
from .utils.logging_config import setup_logging


# from app.routers.resume import router as resume_router  # Commented out resume router

# Set up logging
logger = setup_logging()

# Create FastAPI app
app = FastAPI(
    title="Navigo API",
    description="API for the Navigo Career and Skill Tree Explorer",
    version="0.1.0",
)

# Configure CORS
origins = [
    "http://localhost:3000",  # Frontend development server
    "http://localhost:8000",  # Backend when served 
    "https://navigo-explorer.vercel.app",  # Production frontend
    "http://localhost:5173",  # Vite development server
    "https://localhost:3000",  # HTTPS local development
    "https://localhost:5173",  # HTTPS Vite development
    "https://*.up.railway.app",  # Railway domains
    "https://*.railway.app",    # Railway domains
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

# Print debug information about routers
try:
    logger.info("======= ROUTER REGISTRATION DETAILS =======")
    logger.info(f"auth_router import path: {auth_router.__module__}")
    logger.info(f"get_current_user import path: {get_current_user.__module__}")
    logger.info(f"profiles_router import path: {profiles_router.__module__}")
    
    logger.info(f"Registering auth_router routes: {[f'{route.path} [{route.methods}]' for route in auth_router.routes]}")
    logger.info(f"Registering profiles_router routes: {[f'{route.path} [{route.methods}]' for route in profiles_router.routes]}")
    logger.info(f"Registering users_router routes: {[f'{route.path} [{route.methods}]' for route in users_router.routes]}")
    logger.info(f"Registering chat_router routes: {[f'{route.path} [{route.methods}]' for route in chat_router.routes]}")
    logger.info(f"Registering peers_router routes: {[f'{route.path} [{route.methods}]' for route in peers_router.routes]}")
    logger.info(f"Registering messages_router routes: {[f'{route.path} [{route.methods}]' for route in messages_router.routes]}")
    logger.info(f"Registering test_router routes: {[f'{route.path} [{route.methods}]' for route in test_router.routes]}")
    logger.info(f"Registering space_router routes: {[f'{route.path} [{route.methods}]' for route in space_router.routes]}")
    logger.info(f"Registering vector_router routes: {[f'{route.path} [{route.methods}]' for route in vector_router.routes]}")
    logger.info(f"Registering recommendations_router routes: {[f'{route.path} [{route.methods}]' for route in recommendations_router.routes]}")
    logger.info(f"Registering careers_router routes: {[f'{route.path} [{route.methods}]' for route in careers_router.routes]}")
    logger.info(f"Registering tree_router routes: {[f'{route.path} [{route.methods}]' for route in tree_router.routes]}")  # Log tree router
    logger.info(f"Registering tree_paths_router routes: {[f'{route.path} [{route.methods}]' for route in tree_paths_router.routes]}")  # Log tree paths router
    logger.info(f"Registering node_notes_router routes: {[f'{route.path} [{route.methods}]' for route in node_notes_router.routes]}")  # Log node notes router
    logger.info(f"Registering user_progress_router routes: {[f'{route.path} [{route.methods}]' for route in user_progress_router.routes]}")  # Log user progress router
    logger.info(f"Registering holland_test_router routes: {[f'{route.path} [{route.methods}]' for route in holland_test_router.routes]}")  # Log Holland test router
    logger.info(f"Registering insight_router routes: {[f'{route.path} [{route.methods}]' for route in insight_router.routes]}")  # Log insight router
    # logger.info(f"Registering resume_router routes: {[f'{route.path} [{route.methods}]' for route in resume_router.routes]}")  # Commented out resume router logging
    logger.info("============================================")
except Exception as e:
    logger.error(f"Error while logging router details: {str(e)}")

# Include routers in the correct order
logger.info("Including routers in the FastAPI app")
# Include auth router first - it defines dependencies
app.include_router(auth_router)
logger.info("Auth router included successfully")
# Include profiles router after auth router
app.include_router(profiles_router)
logger.info("Profiles router included successfully")
# Include remaining routers
app.include_router(test_router)
app.include_router(users_router)
app.include_router(chat_router)
app.include_router(peers_router)
app.include_router(messages_router)
app.include_router(space_router)
app.include_router(vector_router)
app.include_router(recommendations_router)
app.include_router(careers_router)
app.include_router(tree_router)  # Include the tree router
app.include_router(tree_paths_router)  # Include the tree paths router
app.include_router(node_notes_router)  # Include the node notes router
app.include_router(user_progress_router)  # Include the user progress router
app.include_router(holland_test_router)  # Include the Holland test router
app.include_router(insight_router)  # Include the insight router
# app.include_router(resume_router)  # Commented out resume router inclusion
logger.info("All routers included successfully")

# Explicitly capture route after including it
logger.info("=== Available Routes ===")
for route in app.routes:
    logger.info(f"Route: {route.path}, Methods: {route.methods}")
logger.info("======================")

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    logger.info("Root endpoint called")
    return {"message": "Welcome to the Navigo API. Go to /docs for API documentation."}

# @app.get("/api/health") # /api/health
# def health_check():
#     try:
#         return {"status": "ok"}
#     except Exception as e:
#         logger.error(f"Health check failed: {str(e)}")
#         return {"status": "error", "detail": str(e)}

@app.get("/health")
async def health_check():
    try:
        # Basic health check without model dependency
        return {"status": "healthy", "message": "Service is running"}
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {"status": "error", "detail": str(e)}

# In your startup event
@app.on_event("startup")
async def startup_event():
    try:
        logger.info("Application startup initiated")
        load_models()
        logger.info("Application startup completed successfully")
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        # Don't fail startup if models fail to load
        pass

def load_models():
    #     global ready
    # # Load your big models here
    # ready = True
    try:
        # Load your big models here
        logger.info("Loading models...")
        # Your model loading code here
        logger.info("Models loaded successfully")
    except Exception as e:
        logger.error(f"Error in load_models: {str(e)}")
        # Don't raise the exception, just log it
        pass

# if __name__ == "__main__":
#     uvicorn.run("app.main:app", host="0.0.0.0", port=8000) #, reload=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # Use Railway-assigned port
    print(f"🚀 Starting app on port {port}")
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)
