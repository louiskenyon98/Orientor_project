"""Distributed tracing implementation with OpenTelemetry"""
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.aioredis import AioRedisInstrumentor
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.trace import Status, StatusCode
from opentelemetry.propagate import set_global_textmap
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from contextvars import ContextVar
from functools import wraps
from typing import Optional, Dict, Any, Callable
import logging
from fastapi import Request
import time

logger = logging.getLogger(__name__)

# Context variable for trace context
trace_context: ContextVar[Optional[Dict[str, Any]]] = ContextVar('trace_context', default=None)


class TracingConfig:
    """Configuration for distributed tracing"""
    
    def __init__(
        self,
        service_name: str,
        service_version: str = "1.0.0",
        otlp_endpoint: str = "localhost:4317",
        enable_console_exporter: bool = False,
        trace_all_sql: bool = False,
        trace_redis: bool = True,
        trace_http_client: bool = True,
        sampling_rate: float = 1.0,
    ):
        self.service_name = service_name
        self.service_version = service_version
        self.otlp_endpoint = otlp_endpoint
        self.enable_console_exporter = enable_console_exporter
        self.trace_all_sql = trace_all_sql
        self.trace_redis = trace_redis
        self.trace_http_client = trace_http_client
        self.sampling_rate = sampling_rate


class DistributedTracing:
    """Manages distributed tracing setup and instrumentation"""
    
    def __init__(self, config: TracingConfig):
        self.config = config
        self.tracer_provider: Optional[TracerProvider] = None
        self.tracer: Optional[trace.Tracer] = None
    
    def initialize(self):
        """Initialize tracing with OpenTelemetry"""
        # Create resource identifying the service
        resource = Resource.create({
            SERVICE_NAME: self.config.service_name,
            SERVICE_VERSION: self.config.service_version,
            "environment": "production",
            "service.namespace": "orientor",
        })
        
        # Create tracer provider
        self.tracer_provider = TracerProvider(resource=resource)
        
        # Add OTLP exporter
        otlp_exporter = OTLPSpanExporter(
            endpoint=self.config.otlp_endpoint,
            insecure=True,  # Use secure=False for local development
        )
        self.tracer_provider.add_span_processor(
            BatchSpanProcessor(otlp_exporter)
        )
        
        # Add console exporter for debugging
        if self.config.enable_console_exporter:
            console_exporter = ConsoleSpanExporter()
            self.tracer_provider.add_span_processor(
                BatchSpanProcessor(console_exporter)
            )
        
        # Set as global tracer provider
        trace.set_tracer_provider(self.tracer_provider)
        
        # Set propagator for distributed context
        set_global_textmap(TraceContextTextMapPropagator())
        
        # Get tracer
        self.tracer = trace.get_tracer(
            self.config.service_name,
            self.config.service_version
        )
        
        logger.info(f"Initialized tracing for {self.config.service_name}")
    
    def instrument_fastapi(self, app):
        """Instrument FastAPI application"""
        FastAPIInstrumentor.instrument_app(
            app,
            tracer_provider=self.tracer_provider,
            excluded_urls="health,metrics,docs,openapi.json",
        )
    
    def instrument_sqlalchemy(self, engine):
        """Instrument SQLAlchemy engine"""
        SQLAlchemyInstrumentor().instrument(
            engine=engine,
            tracer_provider=self.tracer_provider,
            enable_commenter=True,
        )
    
    def instrument_redis(self, redis_client):
        """Instrument Redis client"""
        if self.config.trace_redis:
            RedisInstrumentor().instrument(
                tracer_provider=self.tracer_provider,
            )
    
    def instrument_http_client(self):
        """Instrument HTTP client (httpx)"""
        if self.config.trace_http_client:
            HTTPXClientInstrumentor().instrument(
                tracer_provider=self.tracer_provider,
            )
    
    def create_span(
        self,
        name: str,
        kind: trace.SpanKind = trace.SpanKind.INTERNAL,
        attributes: Optional[Dict[str, Any]] = None,
    ):
        """Create a new span"""
        if not self.tracer:
            return trace.INVALID_SPAN
        
        return self.tracer.start_as_current_span(
            name,
            kind=kind,
            attributes=attributes or {},
        )
    
    def get_current_span(self) -> trace.Span:
        """Get current active span"""
        return trace.get_current_span()
    
    def add_span_attributes(self, attributes: Dict[str, Any]):
        """Add attributes to current span"""
        span = self.get_current_span()
        if span and span.is_recording():
            for key, value in attributes.items():
                span.set_attribute(key, value)
    
    def add_span_event(self, name: str, attributes: Optional[Dict[str, Any]] = None):
        """Add event to current span"""
        span = self.get_current_span()
        if span and span.is_recording():
            span.add_event(name, attributes=attributes or {})
    
    def record_exception(self, exception: Exception):
        """Record exception in current span"""
        span = self.get_current_span()
        if span and span.is_recording():
            span.record_exception(exception)
            span.set_status(Status(StatusCode.ERROR, str(exception)))


def trace_method(
    name: Optional[str] = None,
    kind: trace.SpanKind = trace.SpanKind.INTERNAL,
    attributes: Optional[Dict[str, Any]] = None,
):
    """Decorator to trace methods"""
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            span_name = name or f"{func.__module__}.{func.__name__}"
            tracer = trace.get_tracer(__name__)
            
            with tracer.start_as_current_span(
                span_name,
                kind=kind,
                attributes=attributes or {},
            ) as span:
                try:
                    # Add function arguments as span attributes
                    span.set_attribute("function.args", str(args))
                    span.set_attribute("function.kwargs", str(kwargs))
                    
                    # Execute function
                    start_time = time.time()
                    result = await func(*args, **kwargs)
                    duration = time.time() - start_time
                    
                    # Add duration
                    span.set_attribute("duration_ms", duration * 1000)
                    
                    return result
                except Exception as e:
                    span.record_exception(e)
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            span_name = name or f"{func.__module__}.{func.__name__}"
            tracer = trace.get_tracer(__name__)
            
            with tracer.start_as_current_span(
                span_name,
                kind=kind,
                attributes=attributes or {},
            ) as span:
                try:
                    # Add function arguments as span attributes
                    span.set_attribute("function.args", str(args))
                    span.set_attribute("function.kwargs", str(kwargs))
                    
                    # Execute function
                    start_time = time.time()
                    result = func(*args, **kwargs)
                    duration = time.time() - start_time
                    
                    # Add duration
                    span.set_attribute("duration_ms", duration * 1000)
                    
                    return result
                except Exception as e:
                    span.record_exception(e)
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    raise
        
        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


class TracingMiddleware:
    """FastAPI middleware to add trace context to requests"""
    
    def __init__(self, app, service_name: str):
        self.app = app
        self.service_name = service_name
    
    async def __call__(self, request: Request, call_next):
        # Extract trace context from headers
        trace_id = request.headers.get("X-Trace-Id")
        parent_span_id = request.headers.get("X-Parent-Span-Id")
        
        # Create or get tracer
        tracer = trace.get_tracer(self.service_name)
        
        # Start span for this request
        with tracer.start_as_current_span(
            f"{request.method} {request.url.path}",
            kind=trace.SpanKind.SERVER,
            attributes={
                "http.method": request.method,
                "http.url": str(request.url),
                "http.scheme": request.url.scheme,
                "http.host": request.url.hostname,
                "http.target": request.url.path,
                "http.user_agent": request.headers.get("user-agent", ""),
                "http.remote_addr": request.client.host if request.client else "",
            }
        ) as span:
            # Store trace context
            ctx = {
                "trace_id": format(span.get_span_context().trace_id, '032x'),
                "span_id": format(span.get_span_context().span_id, '016x'),
                "service": self.service_name,
            }
            trace_context.set(ctx)
            
            try:
                # Process request
                response = await call_next(request)
                
                # Add response attributes
                span.set_attribute("http.status_code", response.status_code)
                
                # Add trace headers to response
                response.headers["X-Trace-Id"] = ctx["trace_id"]
                response.headers["X-Span-Id"] = ctx["span_id"]
                
                return response
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise
            finally:
                trace_context.set(None)


# Service-specific tracing configurations
def create_service_tracing(service_name: str) -> DistributedTracing:
    """Create tracing for a specific service"""
    config = TracingConfig(
        service_name=service_name,
        service_version="1.0.0",
        otlp_endpoint="localhost:4317",  # Jaeger or other OTLP collector
        enable_console_exporter=False,
        trace_all_sql=True,
        trace_redis=True,
        trace_http_client=True,
        sampling_rate=1.0,  # 100% sampling for development
    )
    
    tracing = DistributedTracing(config)
    tracing.initialize()
    
    return tracing