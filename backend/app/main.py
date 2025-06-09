from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app
from structlog import get_logger

from app.api.v1 import api_router
from app.core.config import settings
from app.core.logging import configure_logging
from app.db.session import engine

logger = get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    configure_logging()
    logger.info("Starting up Meeting AI Backend", environment=settings.ENVIRONMENT)
    
    # Initialize database connection
    async with engine.begin() as conn:
        logger.info("Database connection established")
    
    yield
    
    # Cleanup
    await engine.dispose()
    logger.info("Shutting down Meeting AI Backend")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
app.include_router(api_router, prefix=settings.API_V1_STR)

# Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "version": settings.APP_VERSION,
    }


@app.get("/")
async def root():
    return {
        "message": "Meeting AI Backend API",
        "version": settings.APP_VERSION,
        "docs": "/docs" if settings.DEBUG else None,
    }