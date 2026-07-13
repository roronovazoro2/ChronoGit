"""
ChronoGit Main Application
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from structlog import get_logger
import time

from .core.config import settings
from .db.database import db
from .routers import repositories, commits, files, analytics, ai, search, timeline
from .services.git_service import git_service

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=getattr(logging, settings.log_level.upper()),
)

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting ChronoGit API")
    
    # Initialize database
    await db.connect()
    
    logger.info(f"ChronoGit API started on {settings.host}:{settings.port}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down ChronoGit API")
    await db.disconnect()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="AI-powered Git repository explorer",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Request logging middleware
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start_time = time.time()
        
        response = await call_next(request)
        
        duration = time.time() - start_time
        logger.info(
            "Request processed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=round(duration * 1000, 2),
        )
        
        return response
    
    # Exception handlers
    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        return JSONResponse(
            status_code=400,
            content={"error": {"code": "INVALID_INPUT", "message": str(exc)}},
        )
    
    @app.exception_handler(FileNotFoundError)
    async def not_found_handler(request: Request, exc: FileNotFoundError):
        return JSONResponse(
            status_code=404,
            content={"error": {"code": "NOT_FOUND", "message": "Resource not found"}},
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error("Unhandled exception", exc_info=exc)
        return JSONResponse(
            status_code=500,
            content={"error": {"code": "INTERNAL_ERROR", "message": "An unexpected error occurred"}},
        )
    
    # Include routers
    app.include_router(repositories.router, prefix="/api/v1/repositories", tags=["Repositories"])
    app.include_router(commits.router, prefix="/api/v1", tags=["Commits"])
    app.include_router(files.router, prefix="/api/v1", tags=["Files"])
    app.include_router(analytics.router, prefix="/api/v1", tags=["Analytics"])
    app.include_router(ai.router, prefix="/api/v1", tags=["AI"])
    app.include_router(search.router, prefix="/api/v1", tags=["Search"])
    app.include_router(timeline.router, prefix="/api/v1", tags=["Timeline"])
    
    # Health check endpoint
    @app.get("/health", tags=["Health"])
    async def health_check():
        db_healthy = await db.health_check()
        return {
            "status": "healthy" if db_healthy else "unhealthy",
            "version": settings.app_version,
            "database": db_healthy,
        }
    
    # Root endpoint
    @app.get("/")
    async def root():
        return {
            "name": settings.app_name,
            "version": settings.app_version,
            "docs": "/docs",
        }
    
    return app


# Create application instance
app = create_app()
