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
# from app.routers.resume import router as resume_router  # Commented out resume router

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create FastAPI app
app = FastAPI(title="Orientor API")

# Configure CORS
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "https://localhost:3000",
    "https://localhost:5173",
    "https://navigoproject.vercel.app",
    "https://orientor-project.vercel.app",
    "https://orientor.vercel.app",
    "https://*.vercel.app"  # Allow all Vercel subdomains
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
# app.include_router(resume_router)  # Commented out resume router inclusion
logger.info("All routers included successfully")

# Explicitly capture route after including it
logger.info("=== Available Routes ===")
for route in app.routes:
    logger.info(f"Route: {route.path}, Methods: {route.methods}")
logger.info("======================")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Orientor API"}

@app.get("/api/health")
def health_check():
    try:
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {"status": "error", "detail": str(e)}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000) #, reload=True)