"""
FastAPI application factory for VizLearn
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import settings
from src.services.content_generation import ContentGenerationService
from src.api.routes import router, set_content_service

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Initialize content generation service on startup
    logger.info("Initializing VizLearn services...")
    content_service = ContentGenerationService()
    await content_service.initialize()
    
    # Set the service in the routes module
    set_content_service(content_service)
    logger.info("VizLearn services initialized successfully")
    
    yield
    
    # Cleanup on shutdown
    logger.info("Shutting down VizLearn services...")
    await content_service.cleanup()
    logger.info("VizLearn services shut down successfully")


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    app = FastAPI(
        title=settings.app_name,
        description="AI-powered learning content generation with streaming support",
        version=settings.app_version,
        lifespan=lifespan,
        debug=settings.debug
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.get_allowed_origins(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include API routes
    app.include_router(router)

    return app


# Create the app instance for development
app = create_app()
