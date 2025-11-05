# -*- coding: utf-8 -*-
"""
Module: Main Application
Description: FastAPI application entry point with routers, middleware, and lifespan events.
"""
import uuid
import time
from contextlib import asynccontextmanager
from typing import Callable
from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from core.config import get_settings
from core.database import init_db, init_database
from core.redis_client import init_redis
from core.logger import APILogger, ErrorCategory
from core.security import add_security_headers, default_rate_limiter
from services.rag_service import rag_service
from api import auth_api, chat_api, rag_api, analytics_api, files_api, search_api, user_api

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events: startup and shutdown"""
    # Startup
    APILogger.log_request("/startup", "INIT", None, None, None, log_message="Application starting")
    
    # Initialize database
    try:
        init_database()
        if settings.DATABASE_URL:
            await init_db()
            APILogger.log_request("/startup", "INIT", None, None, None, log_message="Database initialized")
        else:
            APILogger.log_request("/startup", "INIT", None, None, None, log_message="Database not configured (DATABASE_URL not set)")
    except Exception as e:
        APILogger.log_error("/startup", e, None, ErrorCategory.DATABASE_ERROR)
    
    # Initialize Redis
    try:
        init_redis()
        if settings.REDIS_HOST:
            APILogger.log_request("/startup", "INIT", None, None, None, log_message="Redis initialized")
        else:
            APILogger.log_request("/startup", "INIT", None, None, None, log_message="Redis not configured (REDIS_HOST not set)")
    except Exception as e:
        APILogger.log_error("/startup", e, None, ErrorCategory.NETWORK_ERROR)
    
    # Initialize RAG service (load FAISS)
    try:
        await rag_service.initialize(force_rebuild=False)
        APILogger.log_request("/startup", "INIT", None, None, None, log_message="RAG service initialized")
    except Exception as e:
        APILogger.log_error("/startup", e, None, ErrorCategory.AI_ERROR)
    
    yield
    
    # Shutdown
    APILogger.log_request("/shutdown", "INIT", None, None, None, log_message="Application shutting down")


app = FastAPI(
    title=settings.APP_NAME,
    description="Enterprise-grade RAG-based AI assistant API",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)


# CORS Middleware
ALLOWED_ORIGINS = settings.ALLOWED_ORIGINS.split(",") if settings.ALLOWED_ORIGINS else []

# Validate CORS origins (no wildcard in production with credentials)
if settings.ENVIRONMENT == "production":
    if "*" in ALLOWED_ORIGINS:
        raise ValueError("Wildcard CORS origins not allowed in production with credentials")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-RateLimit-Remaining", "X-Request-ID"]
)


# Request ID Middleware
@app.middleware("http")
async def request_id_middleware(request: Request, call_next: Callable):
    """Inject request ID into request context"""
    request_id = str(uuid.uuid4())
    APILogger.set_request_id(request_id)
    
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    
    return response


# Logging Middleware
@app.middleware("http")
async def logging_middleware(request: Request, call_next: Callable):
    """Log requests and responses"""
    start_time = time.time()
    
    # Log request start
    APILogger.log_request(
        request.url.path,
        request.method,
        None,
        None,
        None,
        log_message="Request started"
    )
    
    try:
        response = await call_next(request)
        
        # Calculate latency
        latency_ms = (time.time() - start_time) * 1000
        
        # Log request completion
        APILogger.log_request(
            request.url.path,
            request.method,
            None,
            latency_ms / 1000,
            response.status_code
        )
        
        # Record metrics
        from api.analytics_api import record_request
        record_request(latency_ms)
        
        return response
    
    except Exception as e:
        latency_ms = (time.time() - start_time) * 1000
        
        APILogger.log_error(
            request.url.path,
            e,
            None,
            ErrorCategory.UNKNOWN_ERROR
        )
        
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )


# Security Headers Middleware
@app.middleware("http")
async def security_headers_middleware(request: Request, call_next: Callable):
    """Add security headers to all responses"""
    response = await call_next(request)
    return add_security_headers(response)


# Rate Limiting Middleware (optional, can be per-endpoint)
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next: Callable):
    """Global rate limiting"""
    # Skip rate limiting for health checks and metrics
    if request.url.path in ["/api/status", "/metrics"]:
        return await call_next(request)
    
    ip_address = request.client.host if request.client else "unknown"
    identifier = f"{ip_address}"
    
    is_allowed, remaining = await default_rate_limiter.is_allowed(identifier, request.url.path)
    
    if not is_allowed:
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded"},
            headers={"X-RateLimit-Remaining": "0", "Retry-After": "60"}
        )
    
    response = await call_next(request)
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    
    return response


# Include routers
app.include_router(auth_api.router)  # Already has /api prefix
app.include_router(chat_api.router)  # Already has /api prefix
app.include_router(rag_api.router)  # Already has /api prefix
app.include_router(analytics_api.router)  # Already has /api prefix
app.include_router(analytics_api.v2_router)  # Already has /api/v2 prefix
app.include_router(files_api.router)  # Already has /api/v2 prefix
app.include_router(search_api.router)  # Already has /api/v2 prefix
app.include_router(user_api.router)  # Already has /api/v2 prefix


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.APP_NAME,
        "version": "2.0.0",
        "status": "running",
        "environment": settings.ENVIRONMENT
    }


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """404 handler"""
    return JSONResponse(
        status_code=404,
        content={"detail": "Not found"}
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """500 handler"""
    APILogger.log_error(
        request.url.path,
        exc,
        None,
        ErrorCategory.UNKNOWN_ERROR
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
