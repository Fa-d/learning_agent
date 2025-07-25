"""
Pydantic models for VizLearn API
"""

from datetime import datetime
from typing import List, Optional, Union
from pydantic import BaseModel, Field
from enum import Enum
import uuid


# Enums
class QuestionType(str, Enum):
    """Types of questions that can be generated"""
    FILL_IN_THE_BLANK = "fill_in_the_blank"
    TRUE_FALSE = "true_false"
    ORDERING_TASK = "ordering_task"


class GenerationStatus(str, Enum):
    """Status of content generation process"""
    STARTED = "started"
    PROGRESS = "progress"
    COMPLETED = "completed"
    ERROR = "error"


# Content models
class PlaygroundResponse(BaseModel):
    """Response content for correct/incorrect answers"""
    text: str
    image: Optional[str] = None


class FillInTheBlankContent(BaseModel):
    """Content for fill-in-the-blank questions"""
    template: str = Field(..., description="Template with gaps marked as ____")
    gaps: List[str] = Field(..., description="Correct answers for the gaps")


class TrueFalseQuestionContent(BaseModel):
    """Question content for true/false questions"""
    text: str
    image: Optional[str] = None


class TrueFalseOptionContent(BaseModel):
    """Option content for true/false questions"""
    id: str
    text: str
    image: Optional[str] = None
    is_correct: bool


class TrueFalseContent(BaseModel):
    """Content for true/false questions"""
    question: TrueFalseQuestionContent
    options: List[TrueFalseOptionContent]


class OrderingTaskContent(BaseModel):
    """Content for ordering task questions"""
    sequences: List[str] = Field(..., description="Items to be ordered")


# Union type for content
PlaygroundContent = Union[
    FillInTheBlankContent,
    TrueFalseContent,
    OrderingTaskContent
]


class PlaygroundItem(BaseModel):
    """A single learning question/task"""
    slug: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    type: QuestionType
    content: PlaygroundContent
    response: Optional[List[PlaygroundResponse]] = None
    correct_response: Optional[PlaygroundResponse] = None
    incorrect_response: Optional[PlaygroundResponse] = None
    hints: Optional[str] = None
    order: int
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


# API Request/Response models
class ContentGenerationRequest(BaseModel):
    """Request model for content generation"""
    title: str = Field(..., description="Title of the learning content")
    description: str = Field(..., description="Brief description of the content")
    num_questions: int = Field(
        default=5, 
        ge=1, 
        le=20, 
        description="Number of questions to generate"
    )
    question_types: Optional[List[QuestionType]] = Field(
        default=None,
        description="Specific question types to generate. If not provided, all types will be used"
    )


class ContentGenerationResponse(BaseModel):
    """Response model for content generation"""
    status: GenerationStatus
    playground_items: List[PlaygroundItem]
    total_questions: int
    message: Optional[str] = None


class StreamingStatusUpdate(BaseModel):
    """Status update for streaming responses"""
    status: GenerationStatus
    message: Optional[str] = None
    item: Optional[PlaygroundItem] = None


class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str
    llm_service: str
    timestamp: str


class ContentTypesResponse(BaseModel):
    """Supported content types response"""
    supported_types: List[str]
    descriptions: dict[str, str]
