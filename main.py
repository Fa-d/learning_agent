"""
VizLearn FastAPI Application Entry Point
Production-ready learning content generation with streaming support
"""

import uvicorn
from app import create_app
from src.core.config import settings

# Create the FastAPI application
app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )
