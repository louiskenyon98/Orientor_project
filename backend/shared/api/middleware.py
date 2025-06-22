"""
Shared Middleware Components

This module provides common middleware for authentication, rate limiting,
logging, and other cross-cutting concerns across all microservices.
"""

from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import time
import logging
import json
from datetime import datetime
from typing import Optional, Dict, Any
import jwt
from collections import defaultdict
import asyncio

logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware to prevent API abuse.
    
    Uses a simple in-memory store for demonstration.
    In production, use Redis or similar.
    """
    
    def __init__(self, app, calls: int = 100, period: int = 60):
        super().__init__(app)
        self.calls = calls
        self.period = period
        self.clients: Dict[str, list] = defaultdict(list)
        
        # Start cleanup task
        asyncio.create_task(self._cleanup_old_requests())
    
    async def dispatch(self, request: Request, call_next):
        # Get client identifier (IP address or user ID)
        client_id = request.client.host
        
        # Get current timestamp
        now = time.time()
        
        # Clean old requests and check rate limit
        self.clients[client_id] = [
            req_time for req_time in self.clients[client_id]
            if now - req_time < self.period
        ]
        
        if len(self.clients[client_id]) >= self.calls:
            return Response(
                content=json.dumps({
                    "error": "rate_limit_exceeded",
                    "message": f"Rate limit exceeded. Maximum {self.calls} requests per {self.period} seconds."
                }),
                status_code=429,
                headers={"Retry-After": str(self.period)}
            )
        
        # Record this request
        self.clients[client_id].append(now)
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.calls)
        response.headers["X-RateLimit-Remaining"] = str(self.calls - len(self.clients[client_id]))
        response.headers["X-RateLimit-Reset"] = str(int(now + self.period))
        
        return response
    
    async def _cleanup_old_requests(self):
        """Periodically clean up old request records"""
        while True:
            await asyncio.sleep(self.period)
            now = time.time()
            
            for client_id in list(self.clients.keys()):
                self.clients[client_id] = [
                    req_time for req_time in self.clients[client_id]
                    if now - req_time < self.period
                ]
                
                if not self.clients[client_id]:
                    del self.clients[client_id]


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Logging middleware for request/response tracking.
    """
    
    async def dispatch(self, request: Request, call_next):
        # Generate request ID
        request_id = f"{time.time()}-{request.client.host}"
        
        # Log request
        logger.info(f"Request {request_id}: {request.method} {request.url.path}")
        
        # Add request ID to headers
        request.state.request_id = request_id
        
        # Time the request
        start_time = time.time()
        
        try:
            response = await call_next(request)
            
            # Calculate response time
            response_time = time.time() - start_time
            
            # Log response
            logger.info(
                f"Response {request_id}: "
                f"status={response.status_code} "
                f"time={response_time:.3f}s"
            )
            
            # Add headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Response-Time"] = f"{response_time:.3f}"
            
            return response
            
        except Exception as e:
            response_time = time.time() - start_time
            logger.error(
                f"Error {request_id}: "
                f"{str(e)} "
                f"time={response_time:.3f}s"
            )
            raise


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """
    Authentication middleware for JWT token validation.
    """
    
    # Paths that don't require authentication
    PUBLIC_PATHS = [
        "/",
        "/health",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/api/v1/auth/login",
        "/api/v1/auth/register",
    ]
    
    async def dispatch(self, request: Request, call_next):
        # Skip authentication for public paths
        if any(request.url.path.startswith(path) for path in self.PUBLIC_PATHS):
            return await call_next(request)
        
        # Extract token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return Response(
                content=json.dumps({
                    "error": "unauthorized",
                    "message": "Missing or invalid authorization header"
                }),
                status_code=401,
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        token = auth_header.split(" ")[1]
        
        try:
            # Verify token (simplified - use proper secret management)
            payload = jwt.decode(
                token,
                "your-secret-key",  # Use environment variable in production
                algorithms=["HS256"]
            )
            
            # Add user info to request state
            request.state.user_id = payload.get("user_id")
            request.state.user_email = payload.get("email")
            
        except jwt.ExpiredSignatureError:
            return Response(
                content=json.dumps({
                    "error": "token_expired",
                    "message": "Token has expired"
                }),
                status_code=401,
                headers={"WWW-Authenticate": "Bearer"}
            )
        except jwt.InvalidTokenError:
            return Response(
                content=json.dumps({
                    "error": "invalid_token",
                    "message": "Invalid token"
                }),
                status_code=401,
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        return await call_next(request)


class MetricsMiddleware(BaseHTTPMiddleware):
    """
    Metrics collection middleware for monitoring.
    """
    
    def __init__(self, app):
        super().__init__(app)
        self.request_count = defaultdict(int)
        self.response_times = defaultdict(list)
        self.error_count = defaultdict(int)
    
    async def dispatch(self, request: Request, call_next):
        # Start timing
        start_time = time.time()
        
        # Create metric key
        method = request.method
        path = self._normalize_path(request.url.path)
        metric_key = f"{method}:{path}"
        
        try:
            # Process request
            response = await call_next(request)
            
            # Record metrics
            response_time = time.time() - start_time
            self.request_count[metric_key] += 1
            self.response_times[metric_key].append(response_time)
            
            # Keep only last 1000 response times
            if len(self.response_times[metric_key]) > 1000:
                self.response_times[metric_key] = self.response_times[metric_key][-1000:]
            
            if response.status_code >= 400:
                self.error_count[metric_key] += 1
            
            return response
            
        except Exception as e:
            # Record error
            self.error_count[metric_key] += 1
            raise
    
    def _normalize_path(self, path: str) -> str:
        """Normalize path for metrics (replace IDs with placeholders)"""
        import re
        
        # Replace UUIDs
        path = re.sub(
            r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}',
            '{id}',
            path
        )
        
        # Replace numeric IDs
        path = re.sub(r'/\d+', '/{id}', path)
        
        return path
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get collected metrics"""
        metrics = {}
        
        for key in self.request_count:
            response_times = self.response_times.get(key, [])
            
            metrics[key] = {
                "count": self.request_count[key],
                "errors": self.error_count.get(key, 0),
                "response_time": {
                    "avg": sum(response_times) / len(response_times) if response_times else 0,
                    "min": min(response_times) if response_times else 0,
                    "max": max(response_times) if response_times else 0,
                }
            }
        
        return metrics


# Dependency functions for route-level auth
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Get current user from JWT token.
    
    This is a dependency that can be used in individual routes.
    """
    token = credentials.credentials
    
    try:
        payload = jwt.decode(
            token,
            "your-secret-key",  # Use environment variable
            algorithms=["HS256"]
        )
        
        return {
            "id": payload.get("user_id"),
            "email": payload.get("email"),
            "roles": payload.get("roles", [])
        }
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def require_auth(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Require authentication for a route.
    
    Usage:
        @router.get("/protected")
        async def protected_route(user = Depends(require_auth)):
            return {"user": user}
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return current_user


async def require_role(role: str):
    """
    Require a specific role for a route.
    
    Usage:
        @router.get("/admin")
        async def admin_route(user = Depends(require_role("admin"))):
            return {"message": "Admin access granted"}
    """
    async def role_checker(current_user: dict = Depends(get_current_user)) -> dict:
        if role not in current_user.get("roles", []):
            raise HTTPException(
                status_code=403,
                detail=f"Role '{role}' required"
            )
        return current_user
    
    return role_checker