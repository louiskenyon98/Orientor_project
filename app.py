from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os

# Simple, clean FastAPI app for new Railway project
app = FastAPI(
    title="Orientor API - Clean Deploy",
    description="Streamlined backend for Orientor platform",
    version="2.0.0"
)

# CORS configuration
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
        "message": "Orientor API v2.0 - Clean Deployment",
        "status": "healthy",
        "version": "2.0.0"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "orientor-api",
        "version": "2.0.0"
    }

@app.get("/api/health")
async def api_health():
    return {"api": "v2", "status": "running"}

# Basic auth endpoints for Vercel connection
@app.post("/api/auth/login")
async def login():
    return {
        "success": True,
        "token": "demo-token-v2",
        "user": {"id": 1, "name": "Demo User"}
    }

@app.get("/api/auth/me")
async def get_current_user():
    return {
        "id": 1,
        "name": "Demo User",
        "email": "demo@orientor.com"
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port)