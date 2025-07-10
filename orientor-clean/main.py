from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import psycopg2
from sqlalchemy import create_engine

# Brand new Orientor API
app = FastAPI(
    title="Orientor API - Fresh Start",
    description="New clean backend for Orientor platform",
    version="3.0.0"
)

# Database connection test - non-blocking
@app.on_event("startup")
async def startup_event():
    # Try DATABASE_URL first, then fall back to DATABASE_PUBLIC_URL
    database_url = os.environ.get("DATABASE_URL")
    database_public_url = os.environ.get("DATABASE_PUBLIC_URL")
    
    if database_url or database_public_url:
        for url_name, url in [("DATABASE_URL", database_url), ("DATABASE_PUBLIC_URL", database_public_url)]:
            if not url:
                continue
                
            try:
                # Fix Railway's malformed PostgreSQL URL
                if "postgres.railway.i" in url:
                    # Handle various formatting issues with Railway URLs
                    url = url.replace("postgres.railway.i\n  nternal", "postgres.railway.internal")
                    url = url.replace("postgres.railway.i", "postgres.railway.internal")
                    # Remove any extra whitespace/newlines
                    url = ' '.join(url.split())
                    print(f"🔧 Fixed Railway database URL")
                
                engine = create_engine(url)
                connection = engine.connect()
                connection.close()
                print(f"✅ Database connected successfully using {url_name}!")
                break
            except Exception as e:
                print(f"❌ Database connection failed with {url_name}: {e}")
                print(f"🔍 {url_name}: {url[:50]}...")
                if url_name == "DATABASE_PUBLIC_URL":
                    print("⚠️ All database URLs failed - continuing without database connection")
    else:
        print("⚠️ No DATABASE_URL or DATABASE_PUBLIC_URL found - running without database")

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
        "message": "🚀 Orientor API v3.0 - Fresh Railway Deployment!",
        "status": "healthy",
        "version": "3.0.0",
        "deployed": "2025-07-10"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "orientor-fresh-api",
        "version": "3.0.0"
    }

@app.get("/api/health")
async def api_health():
    return {
        "api": "v3", 
        "status": "running",
        "endpoints_available": True
    }

# Auth endpoints for Vercel connection
@app.post("/api/auth/login")
async def login():
    return {
        "success": True,
        "message": "Login successful",
        "token": "fresh-token-v3",
        "user": {"id": 1, "name": "Fresh User", "email": "fresh@orientor.com"}
    }

@app.get("/api/auth/me")
async def get_current_user():
    return {
        "id": 1,
        "name": "Fresh User",
        "email": "fresh@orientor.com",
        "role": "user",
        "created": "2025-07-10"
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))  # Ensure string default
    print(f"Starting server on port {port}")
    uvicorn.run("main:app", host="0.0.0.0", port=port)