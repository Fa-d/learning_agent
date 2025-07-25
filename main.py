"""
VizLearn FastAPI Application
Production-ready learning content generation with streaming support
"""

import os
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import asyncio

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import existing LLM setup
from src.llm_service import LLMService
from src.models import (
    PlaygroundItem, 
    ContentGenerationRequest, 
    ContentGenerationResponse,
    GenerationStatus
)

# Global LLM service instance
llm_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global llm_service
    # Initialize LLM service on startup
    llm_service = LLMService()
    await llm_service.initialize()
    yield
    # Cleanup on shutdown
    await llm_service.cleanup()

# Initialize FastAPI app
app = FastAPI(
    title="VizLearn API",
    description="AI-powered learning content generation with streaming support",
    version="1.0.0",
    lifespan=lifespan
)

# Get CORS origins from environment
cors_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173,http://localhost:8080").split(",")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in cors_origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authentication setup (static for now)
security = HTTPBearer()
STATIC_API_KEY = os.getenv("STATIC_API_KEY", "vizlearn-static-key-2025")

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify the authentication token"""
    if credentials.credentials != STATIC_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials

# API Routes

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "VizLearn API is running", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Detailed health check"""
    global llm_service
    llm_status = "healthy" if llm_service and llm_service.is_ready() else "unhealthy"
    
    return {
        "status": "healthy",
        "llm_service": llm_status,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/generate-content")
async def generate_content(
    request: ContentGenerationRequest,
    _: str = Depends(verify_token)
) -> ContentGenerationResponse:
    """Generate learning content without streaming (batch mode)"""
    global llm_service
    
    if not llm_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LLM service is not available"
        )
    
    # Try to ensure connection is working
    if not await llm_service.ensure_connection():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LLM service is not available"
        )
    
    try:
        # Generate all content at once
        playground_items = await llm_service.generate_learning_content(
            title=request.title,
            description=request.description,
            num_questions=request.num_questions,
            question_types=request.question_types
        )
        
        return ContentGenerationResponse(
            status=GenerationStatus.COMPLETED,
            playground_items=playground_items,
            total_questions=len(playground_items)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Content generation failed: {str(e)}"
        )

@app.post("/generate-content/stream")
async def generate_content_stream(
    request: ContentGenerationRequest,
    _: str = Depends(verify_token)
):
    """Generate learning content with streaming support"""
    global llm_service
    
    if not llm_service or not llm_service.is_ready():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LLM service is not available"
        )
    
    # Ensure llm_service is not None and is ready before streaming
    service = llm_service
    if service is None or not service.is_ready():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LLM service is not available"
        )

    async def generate_stream() -> AsyncGenerator[str, None]:
        """Stream generator for Server-Sent Events"""
        try:
            # Send initial status
            yield f"data: {json.dumps({'status': 'started', 'message': 'Starting content generation...'})}\n\n"
            
            # Generate content with streaming
            async for item in service.generate_learning_content_stream(
                title=request.title,
                description=request.description,
                num_questions=request.num_questions,
                question_types=request.question_types
            ):
                # Convert PlaygroundItem to dict for JSON serialization
                item_dict = item.model_dump()
                
                # Send the generated item
                yield f"data: {json.dumps({'status': 'progress', 'item': item_dict})}\n\n"
            
            # Send completion status
            yield f"data: {json.dumps({'status': 'completed', 'message': 'Content generation completed'})}\n\n"
            
        except Exception as e:
            # Send error status
            yield f"data: {json.dumps({'status': 'error', 'message': str(e)})}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream",
        }
    )

@app.get("/content-types")
async def get_supported_content_types(_: str = Depends(verify_token)):
    """Get supported question types"""
    return {
        "supported_types": [
            "fill_in_the_blank",
            "true_false", 
            "ordering_task"
        ],
        "descriptions": {
            "fill_in_the_blank": "Questions with blanks to be filled by the user",
            "true_false": "True/False questions with multiple options",
            "ordering_task": "Questions requiring arranging items in correct order"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
