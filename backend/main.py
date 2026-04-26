"""Main FastAPI application"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from datetime import datetime

from backend.config import settings
from backend.database import engine, Base
from backend.models import PipelineMetric, Anomaly, Recommendation, Alert

# Import route modules
from backend.routes import metrics, anomalies, recommendations, health

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    logger.info("Starting Data Pipeline Monitor")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized")
    yield
    # Shutdown
    logger.info("Shutting down Data Pipeline Monitor")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Real-time monitoring and optimization system for data pipelines",
    lifespan=lifespan,
)

# Middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.example.com"],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "operational",
        "version": settings.app_version,
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/", tags=["Info"])
async def root():
    """Root endpoint with API information"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "description": "Real-time monitoring and optimization for data pipelines",
        "docs": "/docs",
        "endpoints": {
            "health": "/health",
            "metrics": "/api/metrics",
            "anomalies": "/api/anomalies",
            "recommendations": "/api/recommendations",
            "pipelines": "/api/pipelines",
        },
    }


# Exception handlers
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)},
    )


# Routes
app.include_router(metrics.router, prefix="/api/metrics", tags=["Metrics"])
app.include_router(anomalies.router, prefix="/api/anomalies", tags=["Anomalies"])
app.include_router(recommendations.router, prefix="/api/recommendations", tags=["Recommendations"])
app.include_router(health.router, prefix="/api", tags=["Health"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=settings.api_port)
