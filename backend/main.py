"""
PneumoVision AI - Main Application Entry Point
FastAPI Application with comprehensive middleware and routing
"""

import os
import logging
from datetime import datetime
from pathlib import Path

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

from database.connection import get_db, init_db
from database.seed import seed_admin_user
from api.routers import auth, predictions, admin, reports, users
from utils.logger import setup_logging

# Load environment variables
load_dotenv()

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="PneumoVision AI",
    description="AI-Powered Pneumonia Detection System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    contact={
        "name": "PneumoVision AI Team",
        "email": "support@pneumovision.ai",
        "url": "https://pneumovision.ai",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001,http://localhost:3002,http://localhost:3003").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth, prefix="/auth", tags=["Authentication"])
app.include_router(users, prefix="/users", tags=["Users"])
app.include_router(predictions, prefix="/predict", tags=["Predictions"])
app.include_router(reports, prefix="/reports", tags=["Reports"])
app.include_router(admin, prefix="/admin", tags=["Admin"])

# Mount static files
static_dir = Path(__file__).parent.parent / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Mount uploads
uploads_dir = Path(__file__).parent.parent / "uploads"
uploads_dir.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")


@app.on_event("startup")
async def startup_event():
    """Initialize database tables and seed admin user on startup."""
    try:
        logger.info("Initializing database...")
        engine = init_db()
        logger.info("Database tables created successfully")

        db = next(get_db())
        try:
            seed_admin_user(db)
            logger.info("Admin user seeded successfully")
        except Exception as e:
            logger.warning(f"Seed error (may already exist): {e}")
        finally:
            db.close()

        logger.info("PneumoVision AI started successfully")
    except Exception as e:
        logger.error(f"Startup error: {str(e)}")
        raise


@app.get("/")
async def root():
    """Root endpoint - API health check."""
    return {
        "name": "PneumoVision AI",
        "version": "1.0.0",
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat(),
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "health": "/health",
        },
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "database": "connected",
        "model": "loaded",
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "message": str(exc) if os.getenv("DEBUG") else "An unexpected error occurred",
        },
    )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("DEBUG", "True").lower() == "true",
        log_level="info",
    )
