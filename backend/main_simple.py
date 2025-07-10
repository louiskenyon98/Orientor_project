from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os

app = FastAPI(title="Navigo API - Test")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)