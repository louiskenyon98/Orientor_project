from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os

# Ultra-simple FastAPI app for testing
app = FastAPI(
    title="Orientor API - Simple Test",
    description="Basic backend for testing Railway deployment",
    version="3.0.0"
)

# CORS configuration for Vercel
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://navigo-explorer.vercel.app",
        "https://*.vercel.app",
        "http://localhost:3000",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "🚀 Orientor API v3.0 - WORKING ON RAILWAY!",
        "status": "healthy",
        "version": "3.0.0",
        "deployed": "2025-07-10",
        "database": "not connected (testing mode)"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "orientor-simple-api",
        "version": "3.0.0",
        "timestamp": "2025-07-10"
    }

@app.get("/api/health")
async def api_health():
    return {
        "api": "v3", 
        "status": "running",
        "endpoints_available": True,
        "database": "not required for this endpoint"
    }

# Auth endpoints for Vercel connection
@app.post("/api/auth/login")
async def login():
    return {
        "success": True,
        "message": "Login successful",
        "token": "test-token-v3",
        "user": {"id": 1, "name": "Test User", "email": "test@orientor.com"}
    }

@app.get("/api/auth/me")
async def get_current_user():
    return {
        "id": 1,
        "name": "Test User",
        "email": "test@orientor.com",
        "role": "user",
        "created": "2025-07-10"
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    print(f"Starting simple server on port {port}")
    uvicorn.run("main_simple:app", host="0.0.0.0", port=port)