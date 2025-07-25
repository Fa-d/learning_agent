"""
API routes for VizLearn
"""
import json
from datetime import datetime
from typing import AsyncGenerator, Optional

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import StreamingResponse

from ..core.models import (
    ContentGenerationRequest,
    ContentGenerationResponse,
    HealthCheckResponse,
    ContentTypesResponse,
    GenerationStatus,
    QuestionType
)
from ..services.auth import verify_api_key
from ..services.content_generation import ContentGenerationService

router = APIRouter()

# Global service instance - will be set by main app
# Global service instance - will be set by main app
content_service: Optional[ContentGenerationService] = None


def set_content_service(service: ContentGenerationService):
    """Set the global content service instance"""
    global content_service
    content_service = service


@router.get("/", tags=["health"])
async def root():
    """Root endpoint with basic info"""
    return {"message": "VizLearn API is running", "version": "1.0.0"}


@router.get("/health", response_model=HealthCheckResponse, tags=["health"])
async def health_check():
    """Detailed health check"""
    global content_service
    llm_status = "healthy" if content_service and content_service.is_ready() else "unhealthy"
    
    return HealthCheckResponse(
        status="healthy",
        llm_service=llm_status,
        timestamp=datetime.utcnow().isoformat()
    )


@router.post("/generate-content", response_model=ContentGenerationResponse, tags=["content"])
async def generate_content(
    request: ContentGenerationRequest,
    _: str = Depends(verify_api_key)
) -> ContentGenerationResponse:
    """Generate learning content without streaming (batch mode)"""
    global content_service
    
    if not content_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Content generation service is not available"
        )
    
    # Try to ensure connection is working
    if not await content_service.ensure_connection():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Content generation service is not available"
        )
    
    try:
        # Generate all content at once
        playground_items = await content_service.generate_content_batch(
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


@router.post("/generate-content/stream", tags=["content"])
async def generate_content_stream(
    request: ContentGenerationRequest,
    _: str = Depends(verify_api_key)
):
    """Generate learning content with streaming support"""
    global content_service
    
    if not content_service or not content_service.is_ready():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Content generation service is not available"
        )

    # Ensure content_service is not None for type checking
    service = content_service

    async def generate_stream() -> AsyncGenerator[str, None]:
        """Stream generator for Server-Sent Events"""
        try:
            # Send initial status
            yield f"data: {json.dumps({'status': 'started', 'message': 'Starting content generation...'})}\n\n"
            
            # Generate content with streaming
            async for item in service.generate_content_stream(
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


@router.get("/content-types", response_model=ContentTypesResponse, tags=["content"])
async def get_supported_content_types(_: str = Depends(verify_api_key)):
    """Get supported question types"""
    return ContentTypesResponse(
        supported_types=[t.value for t in QuestionType],
        descriptions={
            QuestionType.FILL_IN_THE_BLANK.value: "Questions with blanks to be filled by the user",
            QuestionType.TRUE_FALSE.value: "True/False questions with multiple options",
            QuestionType.ORDERING_TASK.value: "Questions requiring arranging items in correct order"
        }
    )
