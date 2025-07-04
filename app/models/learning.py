from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

class Paragraph(BaseModel):
    content: str
    id: int

class Section(BaseModel):
    title: str
    paragraphs: List[Paragraph]
    id: int

class Chapter(BaseModel):
    title: str
    sections: List[Section]
    id: int

class Course(BaseModel):
    title: str
    chapters: List[Chapter]
    id: int

class QuestionType(str, Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    SHORT_ANSWER = "short_answer"
    FILL_IN_THE_BLANK = "fill_in_the_blank"

class Question(BaseModel):
    question_text: str
    question_type: QuestionType
    options: Optional[List[str]] = None
    correct_answer: Optional[str] = None
    # For short_answer or fill_in_the_blank, correct_answer might be a string or a list of acceptable answers.
    # For simplicity, we'll keep it as Optional[str] for now, and the LLM will provide the best fit.

class Exam(BaseModel):
    questions: List[Question]
