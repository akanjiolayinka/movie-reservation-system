"""
Main FastAPI application entry point.
"""
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from apscheduler.schedulers.background import BackgroundScheduler
import logging

from src.config.settings import settings
from src.config.database import get_db
from src.api import (
    auth_router,
    movies_router,
    showtimes_router,
    reservations_router,
    admin_router,
)
from src.middleware.error_handler import (
    api_exception_handler,
    validation_exception_handler,
    database_exception_handler,
    general_exception_handler,
)
from src.utils.exceptions import APIException
from src.services.reservation_service import reservation_service

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.DEBUG else logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Backend API for movie reservation system with seat booking and management",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register exception handlers
app.add_exception_handler(APIException, api_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, database_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Register API routers
app.include_router(auth_router, prefix=settings.API_V1_PREFIX)
app.include_router(movies_router, prefix=settings.API_V1_PREFIX)
app.include_router(showtimes_router, prefix=settings.API_V1_PREFIX)
app.include_router(reservations_router, prefix=settings.API_V1_PREFIX)
app.include_router(admin_router, prefix=settings.API_V1_PREFIX)


# Background task scheduler for seat lock cleanup
scheduler = BackgroundScheduler()


def cleanup_expired_locks():
    """Periodic task to clean up expired seat locks."""
    try:
        from src.config.database import SessionLocal
        db = SessionLocal()
        try:
            deleted_count = reservation_service.cleanup_expired_locks(db)
            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} expired seat locks")
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Error cleaning up expired locks: {e}")


@app.on_event("startup")
async def startup_event():
    """Application startup event."""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    
    # Start background scheduler for seat lock cleanup
    scheduler.add_job(
        cleanup_expired_locks,
        'interval',
        seconds=settings.SEAT_LOCK_CLEANUP_INTERVAL_SECONDS,
        id='cleanup_expired_locks',
        replace_existing=True
    )
    scheduler.start()
    logger.info("Background scheduler started for seat lock cleanup")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event."""
    logger.info("Shutting down application...")
    scheduler.shutdown()
    logger.info("Background scheduler stopped")


@app.get(
    "/",
    tags=["Health"],
    summary="Root endpoint",
    description="Check if API is running"
)
async def root():
    """Root endpoint - health check."""
    return {
        "message": "Movie Reservation System API",
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs"
    }


@app.get(
    "/health",
    tags=["Health"],
    summary="Health check",
    description="Check API and database health"
)
async def health_check():
    """Health check endpoint."""
    try:
        # Test database connection
        from src.config.database import SessionLocal
        db = SessionLocal()
        try:
            db.execute("SELECT 1")
            db_status = "healthy"
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "unhealthy"
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "database": db_status,
                "error": str(e)
            }
        )
    
    return {
        "status": "healthy",
        "database": db_status,
        "version": settings.APP_VERSION
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
