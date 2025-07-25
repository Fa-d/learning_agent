"""
LLM Service for VizLearn
Integrates with existing local LLM setup and generates learning content
"""

import os
import json
import asyncio
import logging
from typing import List, Optional, AsyncGenerator, Dict, Any
from datetime import datetime

# Set USER_AGENT before any other imports to suppress warnings
if not os.getenv("USER_AGENT"):
    os.environ["USER_AGENT"] = "VizLearn/1.0 (https://github.com/Fa-d/learning_agent)"

from dotenv import load_dotenv
from openai import AsyncOpenAI
from pydantic import SecretStr
import requests
from bs4 import BeautifulSoup
import urllib.parse

from src.models import (
    PlaygroundItem,
    QuestionType,
    FillInTheBlankContent,
    TrueFalseContent,
    TrueFalseQuestionContent,
    TrueFalseOptionContent,
    OrderingTaskContent,
    PlaygroundResponse
)

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class LLMService:
    """Service for generating learning content using local LLM"""
    
    def __init__(self):
        self.llm = None
        self.tools = []
        self._is_ready = False
        
    async def initialize(self):
        """Initialize the LLM service"""
        try:
            # Get LLM configuration from environment variables
            llm_base_url = os.getenv("LLM_BASE_URL", "http://localhost:1234/v1")
            llm_api_key = os.getenv("LLM_API_KEY", "sk-not-needed")
            
            logger.info(f"Initializing LLM with base URL: {llm_base_url}")
            
            # Initialize OpenAI client with configuration from environment
            self.llm = AsyncOpenAI(
                base_url=llm_base_url,
                api_key=llm_api_key,
                timeout=30.0,
                max_retries=2
            )
            
            # Initialize tools
            self._setup_tools()
            
            # Test connection (but don't fail if it doesn't work initially)
            await self._test_connection()
            
            # If initial test failed, try once more after a short delay
            if not self._is_ready:
                logger.info("Initial connection failed, retrying after delay...")
                await asyncio.sleep(2)
                await self._test_connection()
            
            logger.info("LLM Service initialization completed")
            
        except Exception as e:
            logger.error(f"Failed to initialize LLM service: {e}")
            self._is_ready = False
            # Don't raise - allow service to start in degraded mode
    
    def _setup_tools(self):
        """Setup tools for web search and content enrichment"""
        def search_web(query: str) -> str:
            """Search the web using simple HTTP requests for additional information"""
            try:
                # Use a simple search approach with requests
                search_url = "https://duckduckgo.com/lite/"
                
                params = {
                    'q': query,
                    'kl': 'us-en'
                }
                
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                
                response = requests.get(search_url, params=params, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Extract some text content for context
                    text_content = soup.get_text()
                    
                    # Clean and limit the content
                    lines = [line.strip() for line in text_content.split('\n') if line.strip()]
                    relevant_lines = [line for line in lines if query.lower() in line.lower()][:5]
                    
                    if relevant_lines:
                        return f"Web search context for '{query}':\n" + "\n".join(relevant_lines)
                    else:
                        return f"Limited search results found for '{query}'. Generating content based on internal knowledge."
                else:
                    return "Web search temporarily unavailable. Generating content based on internal knowledge."
                    
            except Exception as e:
                return f"Web search temporarily unavailable ({str(e)}). Generating content based on internal knowledge."
        
        # Store search function for direct use
        self.search_func = search_web
    
    async def _test_connection(self):
        """Test LLM connection"""
        try:
            logger.info("Testing LLM connection...")
            response = await self.llm.chat.completions.create(
                model="local-model",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=50
            )
            logger.info(f"LLM connection test successful. Response: {response.choices[0].message.content[:50]}...")
            self._is_ready = True
        except Exception as e:
            logger.error(f"LLM connection test failed: {e}")
            logger.error(f"Error type: {type(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            logger.warning("LLM service will be marked as unavailable")
            # Don't raise the error - allow service to start without LLM
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
    
    async def cleanup(self):
        """Cleanup resources"""
        self._is_ready = False
        logger.info("LLM Service cleaned up")
    
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
            # Try to extract JSON from response
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
                # Parse true/false content
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
    
    async def generate_learning_content(
        self,
        title: str,
        description: str,
        num_questions: int = 5,
        question_types: Optional[List[QuestionType]] = None
    ) -> List[PlaygroundItem]:
        """Generate learning content (batch mode)"""
        if not self.is_ready():
            raise RuntimeError("LLM service is not ready")
        
        if question_types is None:
            question_types = list(QuestionType)
        
        # Get context for content generation via web search
        search_query = f"{title} {description}"
        additional_context = self.search_tool.func(search_query)
        
        system_prompt = self._create_system_prompt(title, description, question_types)
        user_prompt = f"""Generate {num_questions} educational questions about: {title}

Description: {description}

Additional context from web search:
{additional_context}

Distribute questions across the specified types: {[t.value for t in question_types]}

Generate all questions now."""
        
        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = await self.llm.ainvoke(messages)
            
            # Parse response and create PlaygroundItems
            playground_items = []
            
            # Split response by questions and parse each
            response_parts = response.content.split('\n\n')
            
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
    
    async def generate_learning_content_stream(
        self,
        title: str,
        description: str,
        num_questions: int = 5,
        question_types: Optional[List[QuestionType]] = None
    ) -> AsyncGenerator[PlaygroundItem, None]:
        """Generate learning content with streaming"""
        if not self.is_ready():
            raise RuntimeError("LLM service is not ready")
        
        if question_types is None:
            question_types = list(QuestionType)
        
        # Get context for content generation via web search
        search_query = f"{title} {description}"
        additional_context = self.search_tool.func(search_query)
        
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
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=user_prompt)
                ]
                
                # Stream response
                response_chunks = []
                async for chunk in self.llm.astream(messages):
                    if chunk.content:
                        response_chunks.append(chunk.content)
                
                full_response = ''.join(response_chunks)
                
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
