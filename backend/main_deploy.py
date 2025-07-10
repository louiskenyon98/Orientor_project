from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os

app = FastAPI(title="Navigo API - Production")

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://navigoproject-lluvse7tj-philippe-beliveaus-projects.vercel.app",
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
    return {"message": "Navigo API is running!", "status": "success"}

@app.get("/health")
def health():
    return {"status": "ok", "service": "navigo-backend"}

@app.post("/api/auth/login")
def login():
    return {"message": "Login endpoint working", "token": "test-token"}

@app.get("/api/auth/me")
def get_me():
    return {"id": 1, "name": "Test User", "email": "test@example.com"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)