from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os

# Create a minimal working FastAPI app
app = FastAPI(title="Orientor Backend - New Project", version="1.0.0")

# Configure CORS
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
def root():
    return {
        "message": "Orientor Backend is running!",
        "status": "success",
        "version": "1.0.0",
        "project": "new-orientor-backend"
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "orientor-backend",
        "timestamp": "2025-07-10"
    }

@app.get("/api/health")
def api_health():
    return {
        "status": "ok", 
        "api": "v1",
        "endpoints": ["health", "status"]
    }

@app.post("/api/auth/login")
def login():
    return {
        "message": "Login endpoint working",
        "token": "test-token-12345",
        "user": {"id": 1, "name": "Test User"}
    }

@app.get("/api/auth/me")
def get_me():
    return {
        "id": 1,
        "name": "Test User", 
        "email": "test@orientor.com",
        "role": "user"
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)