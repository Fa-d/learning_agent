"""
Content generation service using LangChain with web search capabilities
"""
import asyncio
import logging
from typing import List, Optional

from ..core.models import QuestionType, PlaygroundItem
from .langchain_content_generation import LangChainContentGenerationService

logger = logging.getLogger(__name__)


class ContentGenerationService:
    """Enhanced content generation service using LangChain"""
    
    def __init__(self):
        self.langchain_service = LangChainContentGenerationService()
    
    async def initialize(self) -> None:
        """Initialize the content generation service"""
        await self.langchain_service.initialize()
    
    def is_ready(self) -> bool:
        """Check if service is ready"""
        return self.langchain_service.is_ready()
    
    async def ensure_connection(self) -> bool:
        """Ensure LLM connection is working"""
        return await self.langchain_service.ensure_connection()
    
    async def cleanup(self) -> None:
        """Cleanup resources"""
        await self.langchain_service.cleanup()
    
    async def generate_content(
        self,
        title: str,
        description: str,
        num_questions: int = 5,
        question_types: Optional[List[QuestionType]] = None
    ) -> List[PlaygroundItem]:
        """Generate learning content with web research"""
        if not self.is_ready():
            raise RuntimeError("Content generation service is not ready")
        
        try:
            return await self.langchain_service.generate_content_with_research(
                title=title,
                description=description,
                num_questions=num_questions,
                question_types=question_types
            )
        except Exception as e:
            logger.error(f"Content generation failed: {e}")
            raise
    
    async def generate_content_batch(
        self,
        title: str,
        description: str,
        num_questions: int = 5,
        question_types: Optional[List[QuestionType]] = None
    ) -> List[PlaygroundItem]:
        """Generate learning content in batch mode (alias for generate_content)"""
        return await self.generate_content(title, description, num_questions, question_types)
    
    async def generate_content_stream(
        self,
        title: str,
        description: str,
        num_questions: int = 5,
        question_types: Optional[List[QuestionType]] = None
    ):
        """Generate content with streaming updates"""
        if not self.is_ready():
            raise RuntimeError("Content generation service is not ready")
        
        try:
            # For streaming, we'll generate all content at once and yield updates
            items = await self.langchain_service.generate_content_with_research(
                title=title,
                description=description,
                num_questions=num_questions,
                question_types=question_types
            )
            
            # Yield items one by one with small delays for streaming effect
            for i, item in enumerate(items):
                yield {
                    "type": "question_generated",
                    "data": item.model_dump(),
                    "progress": {
                        "current": i + 1,
                        "total": len(items),
                        "percentage": round((i + 1) / len(items) * 100, 1)
                    }
                }
                if i < len(items) - 1:  # Don't sleep after the last item
                    await asyncio.sleep(0.5)
            
            yield {
                "type": "generation_complete",
                "data": {"message": "Content generation completed successfully"},
                "progress": {
                    "current": len(items),
                    "total": len(items),
                    "percentage": 100.0
                }
            }
            
        except Exception as e:
            logger.error(f"Streaming content generation failed: {e}")
            yield {
                "type": "error",
                "data": {"error": str(e)},
                "progress": {
                    "current": 0,
                    "total": num_questions,
                    "percentage": 0.0
                }
            }


# Global instance
content_generation_service = ContentGenerationService()
