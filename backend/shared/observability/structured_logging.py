"""Structured logging implementation with correlation IDs"""
import logging
import json
import sys
from datetime import datetime
from typing import Dict, Any, Optional, Union
from contextvars import ContextVar
from pythonjsonlogger import jsonlogger
import traceback
from functools import wraps
import asyncio
import uuid

# Context variables for correlation
correlation_id: ContextVar[Optional[str]] = ContextVar('correlation_id', default=None)
user_context: ContextVar[Optional[Dict[str, Any]]] = ContextVar('user_context', default=None)
request_context: ContextVar[Optional[Dict[str, Any]]] = ContextVar('request_context', default=None)


class CorrelationIDFilter(logging.Filter):
    """Add correlation ID and context to log records"""
    
    def filter(self, record):
        # Add correlation ID
        record.correlation_id = correlation_id.get() or "no-correlation-id"
        
        # Add user context
        user_ctx = user_context.get()
        if user_ctx:
            record.user_id = user_ctx.get("user_id")
            record.user_email = user_ctx.get("email")
            record.user_roles = user_ctx.get("roles", [])
        
        # Add request context
        req_ctx = request_context.get()
        if req_ctx:
            record.request_method = req_ctx.get("method")
            record.request_path = req_ctx.get("path")
            record.request_ip = req_ctx.get("ip")
        
        # Add trace context if available
        from .tracing import trace_context
        trace_ctx = trace_context.get()
        if trace_ctx:
            record.trace_id = trace_ctx.get("trace_id")
            record.span_id = trace_ctx.get("span_id")
        
        return True


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter with additional fields"""
    
    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        
        # Add timestamp
        log_record['timestamp'] = datetime.utcnow().isoformat()
        
        # Add service metadata
        log_record['service'] = {
            'name': getattr(record, 'service_name', 'unknown'),
            'version': getattr(record, 'service_version', '1.0.0'),
            'environment': getattr(record, 'environment', 'development'),
        }
        
        # Add error details if exception
        if record.exc_info:
            log_record['error'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'stacktrace': traceback.format_exception(*record.exc_info)
            }
        
        # Rename level
        log_record['level'] = record.levelname
        
        # Add additional context
        if hasattr(record, 'extra_data'):
            log_record['data'] = record.extra_data


class StructuredLogger:
    """Structured logger with context management"""
    
    def __init__(
        self,
        name: str,
        service_name: str,
        service_version: str = "1.0.0",
        environment: str = "development",
        log_level: str = "INFO"
    ):
        self.logger = logging.getLogger(name)
        self.service_name = service_name
        self.service_version = service_version
        self.environment = environment
        
        # Configure logger if not already configured
        if not self.logger.handlers:
            self._configure_logger(log_level)
    
    def _configure_logger(self, log_level: str):
        """Configure structured logging"""
        # Set log level
        self.logger.setLevel(getattr(logging, log_level))
        
        # Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        
        # Create formatter
        formatter = CustomJsonFormatter(
            '%(timestamp)s %(level)s %(name)s %(message)s'
        )
        console_handler.setFormatter(formatter)
        
        # Add correlation ID filter
        correlation_filter = CorrelationIDFilter()
        console_handler.addFilter(correlation_filter)
        
        # Add handler to logger
        self.logger.addHandler(console_handler)
    
    def _log(self, level: str, message: str, **kwargs):
        """Internal log method with context"""
        extra = {
            'service_name': self.service_name,
            'service_version': self.service_version,
            'environment': self.environment,
        }
        
        # Add any additional data
        if kwargs:
            extra['extra_data'] = kwargs
        
        getattr(self.logger, level)(message, extra=extra)
    
    def debug(self, message: str, **kwargs):
        """Debug level logging"""
        self._log('debug', message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """Info level logging"""
        self._log('info', message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Warning level logging"""
        self._log('warning', message, **kwargs)
    
    def error(self, message: str, error: Optional[Exception] = None, **kwargs):
        """Error level logging"""
        if error:
            kwargs['error_type'] = type(error).__name__
            kwargs['error_message'] = str(error)
            kwargs['error_traceback'] = traceback.format_tb(error.__traceback__)
        
        self._log('error', message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Critical level logging"""
        self._log('critical', message, **kwargs)
    
    def log_request(self, method: str, path: str, status_code: int, duration_ms: float, **kwargs):
        """Log HTTP request"""
        self.info(
            f"{method} {path} - {status_code}",
            request_method=method,
            request_path=path,
            response_status=status_code,
            duration_ms=duration_ms,
            **kwargs
        )
    
    def log_database_query(self, query: str, duration_ms: float, **kwargs):
        """Log database query"""
        self.debug(
            "Database query executed",
            query=query,
            duration_ms=duration_ms,
            **kwargs
        )
    
    def log_cache_operation(self, operation: str, key: str, hit: bool, **kwargs):
        """Log cache operation"""
        self.debug(
            f"Cache {operation}",
            cache_operation=operation,
            cache_key=key,
            cache_hit=hit,
            **kwargs
        )
    
    def log_external_api_call(self, service: str, endpoint: str, status_code: int, duration_ms: float, **kwargs):
        """Log external API call"""
        self.info(
            f"External API call to {service}",
            external_service=service,
            endpoint=endpoint,
            status_code=status_code,
            duration_ms=duration_ms,
            **kwargs
        )


def with_correlation_id(func):
    """Decorator to add correlation ID to function execution"""
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        # Generate new correlation ID if not present
        if not correlation_id.get():
            correlation_id.set(str(uuid.uuid4()))
        
        return await func(*args, **kwargs)
    
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        # Generate new correlation ID if not present
        if not correlation_id.get():
            correlation_id.set(str(uuid.uuid4()))
        
        return func(*args, **kwargs)
    
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper


class LoggingMiddleware:
    """FastAPI middleware for structured logging"""
    
    def __init__(self, app, logger: StructuredLogger):
        self.app = app
        self.logger = logger
    
    async def __call__(self, request, call_next):
        # Generate correlation ID
        req_correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        correlation_id.set(req_correlation_id)
        
        # Set request context
        request_context.set({
            "method": request.method,
            "path": request.url.path,
            "ip": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
        })
        
        # Log request start
        self.logger.info(
            f"Request started: {request.method} {request.url.path}",
            request_id=req_correlation_id
        )
        
        # Track timing
        import time
        start_time = time.time()
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000
            
            # Log request completion
            self.logger.log_request(
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_ms=duration_ms,
                request_id=req_correlation_id
            )
            
            # Add correlation ID to response headers
            response.headers["X-Correlation-ID"] = req_correlation_id
            
            return response
            
        except Exception as e:
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000
            
            # Log error
            self.logger.error(
                f"Request failed: {request.method} {request.url.path}",
                error=e,
                request_id=req_correlation_id,
                duration_ms=duration_ms
            )
            
            raise
        finally:
            # Clear context
            correlation_id.set(None)
            request_context.set(None)


# Service-specific logger factory
def create_service_logger(service_name: str, log_level: str = "INFO") -> StructuredLogger:
    """Create structured logger for a service"""
    return StructuredLogger(
        name=f"orientor.{service_name}",
        service_name=service_name,
        service_version="1.0.0",
        environment="production",
        log_level=log_level
    )


# Pre-configured loggers for each service
career_logger = create_service_logger("career")
skills_logger = create_service_logger("skills")
user_logger = create_service_logger("user")
assessment_logger = create_service_logger("assessment")
matching_logger = create_service_logger("matching")
gateway_logger = create_service_logger("gateway")