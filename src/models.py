"""
Pydantic models for VizLearn API
Based on TypeScript interfaces from sample.ts
"""

from datetime import datetime
from typing import List, Optional, Union, Literal
from pydantic import BaseModel, Field
from enum import Enum
import uuid

# Enums
class QuestionType(str, Enum):
    FILL_IN_THE_BLANK = "fill_in_the_blank"
    TRUE_FALSE = "true_false"
    ORDERING_TASK = "ordering_task"

class GenerationStatus(str, Enum):
    STARTED = "started"
    PROGRESS = "progress"
    COMPLETED = "completed"
    ERROR = "error"

# Base models matching TypeScript interfaces
class PlaygroundResponse(BaseModel):
    text: str
    image: Optional[str] = None

class FillInTheBlankContent(BaseModel):
    template: str
    gaps: List[str]

class TrueFalseQuestionContent(BaseModel):
    text: str
    image: Optional[str] = None

class TrueFalseOptionContent(BaseModel):
    id: str
    text: str
    image: Optional[str] = None
    is_correct: bool

class TrueFalseContent(BaseModel):
    question: TrueFalseQuestionContent
    options: List[TrueFalseOptionContent]

class OrderingTaskContent(BaseModel):
    sequences: List[str]

# Union type for content
PlaygroundContent = Union[
    FillInTheBlankContent,
    TrueFalseContent,
    OrderingTaskContent
]

class PlaygroundItem(BaseModel):
    slug: str
    title: str
    description: str
    type: QuestionType
    content: PlaygroundContent
    response: Optional[List[PlaygroundResponse]] = None
    correct_response: Optional[PlaygroundResponse] = None
    incorrect_response: Optional[PlaygroundResponse] = None
    hints: Optional[str] = None
    order: int
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def __init__(self, **data):
        # Auto-generate timestamps if not provided
        if not data.get('created_at'):
            data['created_at'] = datetime.utcnow().isoformat()
        if not data.get('updated_at'):
            data['updated_at'] = datetime.utcnow().isoformat()
        # Auto-generate slug if not provided
        if not data.get('slug'):
            data['slug'] = str(uuid.uuid4())
        super().__init__(**data)

# Request/Response models for API
class ContentGenerationRequest(BaseModel):
    title: str = Field(..., description="Title of the learning content")
    description: str = Field(..., description="Brief description of the content")
    num_questions: int = Field(default=5, ge=1, le=20, description="Number of questions to generate")
    question_types: Optional[List[QuestionType]] = Field(
        default=None,
        description="Specific question types to generate. If not provided, all types will be used"
    )

class ContentGenerationResponse(BaseModel):
    status: GenerationStatus
    playground_items: List[PlaygroundItem]
    total_questions: int
    message: Optional[str] = None

# Streaming response models
class StreamingStatusUpdate(BaseModel):
    status: GenerationStatus
    message: Optional[str] = None
    item: Optional[PlaygroundItem] = None
    progress: Optional[int] = None
    total: Optional[int] = None
