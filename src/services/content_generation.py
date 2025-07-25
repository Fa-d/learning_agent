"""
Content generation service using local LLM
"""
import json
import asyncio
import logging
from typing import List, Optional, AsyncGenerator

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam

from ..core.config import settings
from ..core.models import (
    QuestionType,
    PlaygroundItem,
    FillInTheBlankContent,
    TrueFalseContent,
    TrueFalseQuestionContent,
    TrueFalseOptionContent,
    OrderingTaskContent,
    PlaygroundResponse
)
from ..utils.web_search import web_search

logger = logging.getLogger(__name__)


class ContentGenerationService:
    """Service for generating learning content using local LLM"""
    
    def __init__(self):
        self.llm: Optional[AsyncOpenAI] = None
        self._is_ready = False
        
    async def initialize(self) -> None:
        """Initialize the LLM service"""
        try:
            logger.info(f"Initializing LLM with base URL: {settings.llm_base_url}")
            
            self.llm = AsyncOpenAI(
                base_url=settings.llm_base_url,
                api_key=settings.llm_api_key,
                timeout=settings.llm_timeout,
                max_retries=settings.llm_max_retries
            )
            
            # Test connection
            await self._test_connection()
            
            # Retry once if initial test failed
            if not self._is_ready:
                logger.info("Initial connection failed, retrying after delay...")
                await asyncio.sleep(2)
                await self._test_connection()
            
            logger.info("Content generation service initialization completed")
            
        except Exception as e:
            logger.error(f"Failed to initialize content generation service: {e}")
            self._is_ready = False
    
    async def _test_connection(self) -> None:
        """Test LLM connection"""
        try:
            logger.info("Testing LLM connection...")
            if self.llm is None:
                logger.error("LLM client is not initialized.")
                self._is_ready = False
                return
                
            response = await self.llm.chat.completions.create(
                model=settings.llm_model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=100
            )
            
            content = response.choices[0].message.content
            if content is not None:
                logger.info(f"LLM connection test successful. Response: {content[:50]}...")
            else:
                logger.info("LLM connection test successful, but response content is None.")
            
            self._is_ready = True
            
        except Exception as e:
            logger.error(f"LLM connection test failed: {e}")
            self._is_ready = False
    
    def is_ready(self) -> bool:
        """Check if service is ready"""
        return self._is_ready and self.llm is not None
    
    async def ensure_connection(self) -> bool:
        """Ensure LLM connection is working, retry if needed"""
        if self._is_ready and self.llm is not None:
            return True
            
        if self.llm is not None:
            try:
                logger.info("Retrying LLM connection...")
                await self._test_connection()
                return self._is_ready
            except Exception as e:
                logger.error(f"Connection retry failed: {e}")
                return False
        
        return False
    
    async def cleanup(self) -> None:
        """Cleanup resources"""
        self._is_ready = False
        logger.info("Content generation service cleaned up")
    
    def _create_system_prompt(self, title: str, description: str, question_types: List[QuestionType]) -> str:
        """Create system prompt for content generation"""
        types_description = {
            QuestionType.FILL_IN_THE_BLANK: "Fill in the blank questions with a template containing placeholders and a list of correct answers for the gaps",
            QuestionType.TRUE_FALSE: "True/False questions with multiple choice options where only one is correct",
            QuestionType.ORDERING_TASK: "Ordering questions where users must arrange sequences in the correct order"
        }
        
        selected_types = [types_description[t] for t in question_types]
        
        return f"""You are an expert educational content creator. Generate high-quality learning questions based on the given topic.

Topic: {title}
Description: {description}

Generate questions of these types:
{chr(10).join(f"- {t}" for t in selected_types)}

Requirements:
1. Each question must be educational and relevant to the topic
2. Questions should progressively build understanding
3. Include helpful hints when appropriate
4. Ensure correct answers are accurate
5. For True/False questions, provide 2-4 options with only one correct
6. For Fill in the blank, create meaningful gaps that test understanding
7. For Ordering tasks, provide sequences that have a logical order

Return ONLY valid JSON in this exact format for each question:
{{
    "type": "question_type",
    "title": "Question title",
    "description": "Brief description of what this question tests",
    "content": {{
        // Content varies by type - see examples below
    }},
    "correct_response": {{
        "text": "Explanation of correct answer",
        "image": null
    }},
    "incorrect_response": {{
        "text": "Explanation for wrong answers",
        "image": null
    }},
    "hints": "Helpful hint for the user"
}}

Content format examples:
- fill_in_the_blank: {{"template": "The ____ is responsible for ____", "gaps": ["CPU", "processing"]}}
- true_false: {{"question": {{"text": "Question text", "image": null}}, "options": [{{"id": "1", "text": "Option 1", "image": null, "is_correct": true}}, {{"id": "2", "text": "Option 2", "image": null, "is_correct": false}}]}}
- ordering_task: {{"sequences": ["First step", "Second step", "Third step"]}}

Generate one question at a time when streaming is enabled."""
    
    def _parse_llm_response(self, response_text: str, question_type: QuestionType, order: int) -> Optional[PlaygroundItem]:
        """Parse LLM response and create PlaygroundItem"""
        try:
            # Clean response text
            response_text = response_text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            data = json.loads(response_text)
            
            # Create content based on type
            if question_type == QuestionType.FILL_IN_THE_BLANK:
                content = FillInTheBlankContent(**data['content'])
            elif question_type == QuestionType.TRUE_FALSE:
                question_data = data['content']['question']
                options_data = data['content']['options']
                
                question = TrueFalseQuestionContent(**question_data)
                options = [TrueFalseOptionContent(**opt) for opt in options_data]
                content = TrueFalseContent(question=question, options=options)
            elif question_type == QuestionType.ORDERING_TASK:
                content = OrderingTaskContent(**data['content'])
            else:
                logger.error(f"Unknown question type: {question_type}")
                return None
            
            # Create responses
            correct_response = PlaygroundResponse(**data['correct_response']) if data.get('correct_response') else None
            incorrect_response = PlaygroundResponse(**data['incorrect_response']) if data.get('incorrect_response') else None
            
            # Create PlaygroundItem
            item = PlaygroundItem(
                title=data.get('title', 'Generated Question'),
                description=data.get('description', ''),
                type=question_type,
                content=content,
                correct_response=correct_response,
                incorrect_response=incorrect_response,
                hints=data.get('hints'),
                order=order
            )
            
            return item
            
        except Exception as e:
            logger.error(f"Failed to parse LLM response: {e}")
            logger.debug(f"Response text: {response_text}")
            return None
    
    async def generate_content_batch(
        self,
        title: str,
        description: str,
        num_questions: int = 5,
        question_types: Optional[List[QuestionType]] = None
    ) -> List[PlaygroundItem]:
        """Generate learning content in batch mode"""
        if not self.is_ready():
            raise RuntimeError("Content generation service is not ready")
        
        if question_types is None:
            question_types = list(QuestionType)
        
        # Get context for content generation via web search
        search_query = f"{title} {description}"
        additional_context = web_search.search(search_query)
        
        system_prompt = self._create_system_prompt(title, description, question_types)
        user_prompt = f"""Generate {num_questions} educational questions about: {title}

Description: {description}

Additional context from web search:
{additional_context}

Distribute questions across the specified types: {[t.value for t in question_types]}

Generate all questions now."""
        
        try:
            messages = [
                ChatCompletionSystemMessageParam(role="system", content=system_prompt),
                ChatCompletionUserMessageParam(role="user", content=user_prompt)
            ]
            
            if self.llm is None:
                raise RuntimeError("LLM client is not initialized. Please call initialize() first.")
                
            response = await self.llm.chat.completions.create(
                model=settings.llm_model,
                messages=messages,
                max_tokens=2000
            )
            
            # Parse response and create PlaygroundItems
            playground_items = []
            
            response_content = response.choices[0].message.content
            if not response_content:
                response_content = ""
            
            # Split response by questions and parse each
            response_parts = response_content.split('\n\n')
            
            for i, part in enumerate(response_parts):
                if part.strip():
                    question_type = question_types[i % len(question_types)]
                    item = self._parse_llm_response(part, question_type, i + 1)
                    if item:
                        playground_items.append(item)
            
            return playground_items
            
        except Exception as e:
            logger.error(f"Failed to generate content: {e}")
            raise
    
    async def generate_content_stream(
        self,
        title: str,
        description: str,
        num_questions: int = 5,
        question_types: Optional[List[QuestionType]] = None
    ) -> AsyncGenerator[PlaygroundItem, None]:
        """Generate learning content with streaming"""
        if not self.is_ready():
            raise RuntimeError("Content generation service is not ready")
        
        if question_types is None:
            question_types = list(QuestionType)
        
        # Get context for content generation via web search
        search_query = f"{title} {description}"
        additional_context = web_search.search(search_query)
        
        system_prompt = self._create_system_prompt(title, description, question_types)
        
        # Generate questions one by one
        for i in range(num_questions):
            question_type = question_types[i % len(question_types)]
            
            user_prompt = f"""Generate question {i+1} of {num_questions} about: {title}

Description: {description}

Additional context from web search:
{additional_context}

Question type: {question_type.value}
Question number: {i+1}

Generate a single, well-crafted question of type {question_type.value}."""
            
            try:
                messages = [
                    ChatCompletionSystemMessageParam(role="system", content=system_prompt),
                    ChatCompletionUserMessageParam(role="user", content=user_prompt)
                ]
                
                if self.llm is None:
                    raise RuntimeError("LLM client is not initialized")
                    
                response = await self.llm.chat.completions.create(
                    model=settings.llm_model,
                    messages=messages,
                    max_tokens=1000
                )
                
                full_response = response.choices[0].message.content
                if not full_response:
                    full_response = ""
                
                # Parse and yield the item
                item = self._parse_llm_response(full_response, question_type, i + 1)
                if item:
                    yield item
                else:
                    # Generate a fallback question if parsing fails
                    fallback_item = self._create_fallback_question(title, question_type, i + 1)
                    yield fallback_item
                
                # Small delay between questions
                await asyncio.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Failed to generate question {i+1}: {e}")
                # Yield fallback question
                fallback_item = self._create_fallback_question(title, question_type, i + 1)
                yield fallback_item
    
    def _create_fallback_question(self, title: str, question_type: QuestionType, order: int) -> PlaygroundItem:
        """Create a fallback question when LLM generation fails"""
        if question_type == QuestionType.FILL_IN_THE_BLANK:
            content = FillInTheBlankContent(
                template=f"The topic of ____ involves ____.",
                gaps=[title, "learning"]
            )
        elif question_type == QuestionType.TRUE_FALSE:
            content = TrueFalseContent(
                question=TrueFalseQuestionContent(
                    text=f"Is {title} an important topic to learn?",
                    image=None
                ),
                options=[
                    TrueFalseOptionContent(id="1", text="True", image=None, is_correct=True),
                    TrueFalseOptionContent(id="2", text="False", image=None, is_correct=False)
                ]
            )
        else:  # ordering_task
            content = OrderingTaskContent(
                sequences=[f"Learn about {title}", "Practice the concepts", "Apply the knowledge"]
            )
        
        return PlaygroundItem(
            title=f"Question about {title}",
            description=f"A {question_type.value} question about {title}",
            type=question_type,
            content=content,
            correct_response=PlaygroundResponse(
                text="This is the correct approach to this topic.",
                image=None
            ),
            incorrect_response=PlaygroundResponse(
                text="This approach needs more consideration.",
                image=None
            ),
            hints=f"Think about the key concepts of {title}",
            order=order
        )
