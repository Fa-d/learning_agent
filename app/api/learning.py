from fastapi import APIRouter, Body, Query, HTTPException
from typing import Union
from ..services.learning_service import LearningService
from ..models.learning import Course, Exam, Chapter, Section, Paragraph

router = APIRouter()

learning_service = LearningService()

@router.get("/course/{subject}", response_model=Course)
def get_course(
    subject: str,
    llm_provider_name: str = Query("llama", description="Name of the LLM provider to use (e.g., 'llama', 'openai', 'gemini', 'anthropic', 'deepseek')")
) -> Course:
    return learning_service.generate_course(subject, llm_provider_name)

@router.post("/exam", response_model=Exam)
def get_exam(
    paragraph: str = Body(..., embed=True),
    llm_provider_name: str = Query("llama", description="Name of the LLM provider to use (e.g., 'llama', 'openai', 'gemini', 'anthropic', 'deepseek')")
) -> Exam:
    return learning_service.generate_exam(paragraph, llm_provider_name) # type: ignore

@router.get("/course/{subject}/part", response_model=Union[Chapter, Section, Paragraph])
def get_course_part(
    subject: str,
    chapter_id: int = Query(..., description="ID of the chapter"),
    section_id: int = Query(None, description="ID of the section (optional)"),
    paragraph_id: int = Query(None, description="ID of the paragraph (optional)"),
    llm_provider_name: str = Query("llama", description="Name of the LLM provider to use (e.g., 'llama', 'openai', 'gemini', 'anthropic', 'deepseek')")
) -> Union[Chapter, Section, Paragraph]:
    course = learning_service.generate_course(subject, llm_provider_name) # Regenerate course for simplicity
    part = learning_service.get_course_part(course, chapter_id, section_id, paragraph_id)
    if not part:
        raise HTTPException(status_code=404, detail="Course part not found")
    return part
