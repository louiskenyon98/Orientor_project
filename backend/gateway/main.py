"""
API Gateway for Orientor Microservices

This module provides the main entry point for the API Gateway,
routing requests to appropriate microservices and handling
cross-cutting concerns like authentication, rate limiting, and logging.
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import httpx
import os
import logging
from datetime import datetime
from typing import Optional
import asyncio

# Import service routers
from backend.services.career.api.routes import router as career_router
# Future imports for other services
# from backend.services.skills.api.routes import router as skills_router
# from backend.services.assessment.api.routes import router as assessment_router
# from backend.services.user.api.routes import router as user_router
# from backend.services.matching.api.routes import router as matching_router

# Import shared middleware
from backend.shared.api.middleware import (
    RateLimitMiddleware,
    LoggingMiddleware,
    AuthenticationMiddleware,
    MetricsMiddleware
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Orientor API Gateway",
    description="Unified API Gateway for Orientor Career Guidance Platform",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configure CORS
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "https://localhost:3000",
    "https://localhost:5173",
    os.getenv("FRONTEND_URL", "https://orientor.app"),
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

# Add security middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure based on environment
)

# Add custom middleware
app.add_middleware(RateLimitMiddleware, calls=100, period=60)  # 100 calls per minute
app.add_middleware(LoggingMiddleware)
app.add_middleware(AuthenticationMiddleware)
app.add_middleware(MetricsMiddleware)

# Service discovery configuration
SERVICE_REGISTRY = {
    "career": os.getenv("CAREER_SERVICE_URL", "http://localhost:8001"),
    "skills": os.getenv("SKILLS_SERVICE_URL", "http://localhost:8002"),
    "assessment": os.getenv("ASSESSMENT_SERVICE_URL", "http://localhost:8003"),
    "user": os.getenv("USER_SERVICE_URL", "http://localhost:8004"),
    "matching": os.getenv("MATCHING_SERVICE_URL", "http://localhost:8005"),
}

# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Gateway health check endpoint.
    
    Checks the health of the gateway and all registered services.
    """
    health_status = {
        "gateway": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {}
    }
    
    # Check health of each service
    async with httpx.AsyncClient(timeout=5.0) as client:
        tasks = []
        for service_name, service_url in SERVICE_REGISTRY.items():
            tasks.append(_check_service_health(client, service_name, service_url))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for service_name, result in zip(SERVICE_REGISTRY.keys(), results):
            if isinstance(result, Exception):
                health_status["services"][service_name] = {
                    "status": "unhealthy",
                    "error": str(result)
                }
            else:
                health_status["services"][service_name] = result
    
    # Determine overall health
    all_healthy = all(
        service.get("status") == "healthy" 
        for service in health_status["services"].values()
    )
    
    if not all_healthy:
        health_status["gateway"] = "degraded"
    
    return health_status


async def _check_service_health(client: httpx.AsyncClient, name: str, url: str) -> dict:
    """Check health of individual service"""
    try:
        response = await client.get(f"{url}/health")
        if response.status_code == 200:
            return {"status": "healthy", "response_time_ms": response.elapsed.total_seconds() * 1000}
        else:
            return {"status": "unhealthy", "status_code": response.status_code}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


# Root endpoint
@app.get("/")
async def root():
    """Gateway root endpoint"""
    return {
        "service": "Orientor API Gateway",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/health",
        "services": list(SERVICE_REGISTRY.keys())
    }


# Service routing with circuit breaker pattern
class CircuitBreaker:
    """Simple circuit breaker implementation"""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open
    
    async def call(self, func, *args, **kwargs):
        if self.state == "open":
            if datetime.utcnow().timestamp() - self.last_failure_time > self.recovery_timeout:
                self.state = "half-open"
            else:
                raise HTTPException(status_code=503, detail="Service temporarily unavailable")
        
        try:
            result = await func(*args, **kwargs)
            if self.state == "half-open":
                self.state = "closed"
                self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = datetime.utcnow().timestamp()
            
            if self.failure_count >= self.failure_threshold:
                self.state = "open"
            
            raise e


# Service proxies
circuit_breakers = {
    service: CircuitBreaker() for service in SERVICE_REGISTRY
}


@app.api_route("/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_request(service: str, path: str, request: Request):
    """
    Proxy requests to appropriate microservices.
    
    This is a fallback for services not yet migrated to direct routing.
    """
    if service not in SERVICE_REGISTRY:
        raise HTTPException(status_code=404, detail=f"Service '{service}' not found")
    
    service_url = SERVICE_REGISTRY[service]
    circuit_breaker = circuit_breakers[service]
    
    try:
        async def make_request():
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Forward the request
                headers = dict(request.headers)
                headers.pop("host", None)  # Remove host header
                
                response = await client.request(
                    method=request.method,
                    url=f"{service_url}/{path}",
                    headers=headers,
                    params=request.query_params,
                    content=await request.body()
                )
                
                return JSONResponse(
                    content=response.json() if response.content else {},
                    status_code=response.status_code,
                    headers=dict(response.headers)
                )
        
        return await circuit_breaker.call(make_request)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error proxying request to {service}: {str(e)}")
        raise HTTPException(status_code=502, detail="Bad gateway")


# Include service routers directly (for migrated services)
app.include_router(career_router, prefix="/api/v1/careers", tags=["careers"])
# app.include_router(skills_router, prefix="/api/v1/skills", tags=["skills"])
# app.include_router(assessment_router, prefix="/api/v1/assessments", tags=["assessments"])
# app.include_router(user_router, prefix="/api/v1/users", tags=["users"])
# app.include_router(matching_router, prefix="/api/v1/matching", tags=["matching"])


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle uncaught exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_server_error",
            "message": "An unexpected error occurred",
            "timestamp": datetime.utcnow().isoformat()
        }
    )


# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize gateway on startup"""
    logger.info("API Gateway starting up...")
    logger.info(f"Service registry: {SERVICE_REGISTRY}")
    
    # Initialize connections, caches, etc.
    # await init_cache()
    # await init_metrics()
    
    logger.info("API Gateway started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown"""
    logger.info("API Gateway shutting down...")
    
    # Close connections, flush metrics, etc.
    # await close_cache()
    # await flush_metrics()
    
    logger.info("API Gateway shut down successfully")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.gateway.main:app",
        host="0.0.0.0",
        port=int(os.getenv("GATEWAY_PORT", 8000)),
        reload=os.getenv("ENV", "development") == "development"
    )