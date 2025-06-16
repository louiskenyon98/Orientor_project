#!/usr/bin/env python3
"""
Education API Server
Run this to start the backend server for education program search
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend_education_api import router

# Create FastAPI app
app = FastAPI(
    title="Orientor Education API",
    description="API for searching Quebec CEGEP and university programs",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the education router
app.include_router(router)

# Health check endpoint
@app.get("/")
async def root():
    return {
        "message": "Orientor Education API is running",
        "endpoints": {
            "search": "/api/v1/education/programs/search",
            "program_details": "/api/v1/education/programs/{program_id}",
            "institutions": "/api/v1/education/institutions",
            "metadata": "/api/v1/education/metadata"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "education-api"}

if __name__ == "__main__":
    print("🚀 Starting Orientor Education API Server")
    print("=" * 50)
    print("📍 Server will run at: http://localhost:8000")
    print("🔍 Search endpoint: http://localhost:8000/api/v1/education/programs/search")
    print("📚 API docs: http://localhost:8000/docs")
    print("=" * 50)
    
    uvicorn.run(
        "run_education_server:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )