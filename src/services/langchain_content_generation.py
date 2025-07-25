"""
Enhanced content generation service using LangChain agents
"""
import json
import asyncio
import logging
from typing import List, Optional, AsyncGenerator

from langchain_openai import ChatOpenAI
from langchain.tools import Tool
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain import hub
from pydantic import SecretStr

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


class LangChainContentGenerationService:
    """Enhanced content generation service using LangChain agents"""
    
    def __init__(self):
        self.llm: Optional[ChatOpenAI] = None
        self.agent_executor: Optional[AgentExecutor] = None
        self._is_ready = False
        
    async def initialize(self) -> None:
        """Initialize the LangChain-based content generation service"""
        try:
            logger.info(f"Initializing LangChain LLM with base URL: {settings.llm_base_url}")
            
            # Initialize ChatOpenAI with local LLM
            self.llm = ChatOpenAI(
                streaming=True,
                base_url=settings.llm_base_url,
                api_key=SecretStr(settings.llm_api_key),
                model=settings.llm_model,
                timeout=settings.llm_timeout,
                max_retries=settings.llm_max_retries
            )
            
            # Get web search tools
            tools = web_search.get_tools()
            
            # Try to set up the agent with tools (optional)
            try:
                # Get the prompt from LangChain hub (optional)
                prompt = hub.pull("hwchase17/openai-tools-agent")
                
                # Create the agent
                agent = create_tool_calling_agent(self.llm, tools, prompt)
                
                # Create agent executor
                self.agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
                
                logger.info("LangChain agent created successfully")
                
            except Exception as e:
                logger.warning(f"Failed to create LangChain agent: {e}. Will use direct LLM with web search.")
                # Continue without agent but with LLM and web search
                self.agent_executor = None
            
            # Test connection
            await self._test_connection()
            
            # Retry once if initial test failed
            if not self._is_ready:
                logger.info("Initial connection failed, retrying after delay...")
                await asyncio.sleep(2)
                await self._test_connection()
            
            logger.info("LangChain content generation service initialization completed")
            
        except Exception as e:
            logger.error(f"Failed to initialize LangChain content generation service: {e}")
            self._is_ready = False
    
    async def _test_connection(self) -> None:
        """Test LLM connection"""
        try:
            logger.info("Testing LangChain LLM connection...")
            
            if self.llm is None:
                logger.error("LLM client is not initialized.")
                self._is_ready = False
                return
            
            # Test with a simple query
            test_query = "Hello, can you confirm you're working?"
            
            if self.agent_executor:
                # Test with agent
                result = await self.agent_executor.ainvoke({"input": test_query})
                content = result.get("output", "")
            else:
                # Test with direct LLM
                from langchain.schema import HumanMessage
                response = await self.llm.ainvoke([HumanMessage(content=test_query)])
                content = response.content
            
            if content:
                logger.info(f"LangChain LLM connection test successful. Response: {content[:50]}...")
                self._is_ready = True
            else:
                logger.warning("LLM connection test returned empty response.")
                self._is_ready = False
                
        except Exception as e:
            logger.error(f"LangChain LLM connection test failed: {e}")
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
                logger.info("Retrying LangChain LLM connection...")
                await self._test_connection()
                return self._is_ready
            except Exception as e:
                logger.error(f"Connection retry failed: {e}")
                return False
        
        return False
    
    async def cleanup(self) -> None:
        """Cleanup resources"""
        self._is_ready = False
        logger.info("LangChain content generation service cleaned up")
    
    def _create_content_generation_prompt(self, title: str, description: str, question_types: List[QuestionType]) -> str:
        """Create enhanced prompt for content generation using web search context"""
        types_description = {
            QuestionType.FILL_IN_THE_BLANK: "Fill in the blank questions with a template containing placeholders and a list of correct answers for the gaps",
            QuestionType.TRUE_FALSE: "True/False questions with multiple choice options where only one is correct",
            QuestionType.ORDERING_TASK: "Ordering questions where users must arrange sequences in the correct order"
        }
        
        selected_types = [types_description[t] for t in question_types]
        
        return f"""You are an expert educational content creator with access to web search tools. 

TASK: Generate high-quality learning questions about: "{title}"
DESCRIPTION: {description}

INSTRUCTIONS:
1. FIRST: Use the duckduckgo_search tool to search for current information about "{title}"
2. THEN: If you find relevant URLs, use the scrape_website tool to get detailed content
3. FINALLY: Generate educational questions based on both your knowledge and the web research

Generate questions of these types:
{chr(10).join(f"- {t}" for t in selected_types)}

REQUIREMENTS:
- Each question must be educational and relevant to the topic
- Use current, up-to-date information from your web search
- Questions should progressively build understanding
- Include helpful hints when appropriate
- Ensure correct answers are accurate
- For True/False questions, provide 2-4 options with only one correct
- For Fill in the blank, create meaningful gaps that test understanding
- For Ordering tasks, provide sequences that have a logical order

RESPONSE FORMAT:
Return your response as a JSON object with this structure:
{{
    "questions": [
        {{
            "type": "question_type",
            "title": "Question title",
            "description": "Brief description of what this question tests",
            "content": {{
                // Content varies by type
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
    ],
    "research_summary": "Brief summary of the web research conducted"
}}

Content format examples:
- fill_in_the_blank: {{"template": "The ____ is responsible for ____", "gaps": ["CPU", "processing"]}}
- true_false: {{"question": {{"text": "Question text", "image": null}}, "options": [{{"id": "1", "text": "Option 1", "image": null, "is_correct": true}}, {{"id": "2", "text": "Option 2", "image": null, "is_correct": false}}]}}
- ordering_task: {{"sequences": ["First step", "Second step", "Third step"]}}

Begin by searching for information about "{title}" using the available tools."""
    
    async def generate_content_with_research(
        self,
        title: str,
        description: str,
        num_questions: int = 5,
        question_types: Optional[List[QuestionType]] = None
    ) -> List[PlaygroundItem]:
        """Generate learning content using LangChain agent with web research"""
        if not self.is_ready():
            raise RuntimeError("LangChain content generation service is not ready")
        
        if question_types is None:
            question_types = list(QuestionType)
        
        try:
            # Create enhanced prompt for agent
            prompt = self._create_content_generation_prompt(title, description, question_types)
            
            if self.agent_executor:
                # Use agent with tools for enhanced research
                logger.info(f"Generating content with LangChain agent for: {title}")
                result = await self.agent_executor.ainvoke({"input": prompt})
                response_text = result.get("output", "")
            else:
                # Fallback to direct LLM with simple web search
                logger.info(f"Using fallback method for content generation: {title}")
                search_context = web_search.search(f"{title} {description}")
                
                simple_prompt = f"""Generate {num_questions} educational questions about: {title}

Description: {description}

Web search context:
{search_context}

{prompt.split('RESPONSE FORMAT:')[1]}"""
                
                if self.llm is not None:
                    from langchain.schema import HumanMessage
                    response = await self.llm.ainvoke([HumanMessage(content=simple_prompt)])
                    response_text = str(response.content) if response.content else ""
                else:
                    response_text = ""
            
            # Parse the response and create PlaygroundItems
            playground_items = self._parse_agent_response(response_text, question_types)
            
            if not playground_items:
                # Generate fallback questions if parsing fails
                logger.warning("Agent response parsing failed, generating fallback questions")
                playground_items = [
                    self._create_fallback_question(title, question_types[i % len(question_types)], i + 1)
                    for i in range(num_questions)
                ]
            
            return playground_items[:num_questions]
            
        except Exception as e:
            logger.error(f"Failed to generate content with LangChain: {e}")
            # Return fallback questions
            return [
                self._create_fallback_question(title, question_types[i % len(question_types)], i + 1)
                for i in range(num_questions)
            ]
    
    def _parse_agent_response(self, response_text: str, question_types: List[QuestionType]) -> List[PlaygroundItem]:
        """Parse LangChain agent response and create PlaygroundItems"""
        try:
            # Clean response text
            response_text = response_text.strip()
            
            # Try to extract JSON from response
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            # Find JSON object in response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_text = response_text[start_idx:end_idx]
                data = json.loads(json_text)
            else:
                data = json.loads(response_text)
            
            # Extract questions from response
            questions_data = data.get('questions', [])
            if not questions_data:
                logger.warning(f"No questions found in response: {data}")
                return []
                
            playground_items = []
            
            for i, q_data in enumerate(questions_data):
                if isinstance(q_data, dict):
                    item = self._create_playground_item_from_data(q_data, i + 1)
                    if item:
                        playground_items.append(item)
                else:
                    logger.warning(f"Invalid question data format: {q_data}")
            
            return playground_items
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.debug(f"Response text: {response_text}")
            return []
        except Exception as e:
            logger.error(f"Failed to parse agent response: {e}")
            logger.debug(f"Response text: {response_text}")
            return []
    
    def _create_playground_item_from_data(self, data: dict, order: int) -> Optional[PlaygroundItem]:
        """Create PlaygroundItem from parsed question data"""
        try:
            question_type = QuestionType(data['type'])
            
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
            logger.error(f"Failed to create playground item from data: {e}")
            return None
    
    def _create_fallback_question(self, title: str, question_type: QuestionType, order: int) -> PlaygroundItem:
        """Create a fallback question when agent generation fails"""
        if question_type == QuestionType.FILL_IN_THE_BLANK:
            content = FillInTheBlankContent(
                template=f"The topic of ____ involves understanding ____.",
                gaps=[title, "key concepts"]
            )
        elif question_type == QuestionType.TRUE_FALSE:
            content = TrueFalseContent(
                question=TrueFalseQuestionContent(
                    text=f"Is {title} an important subject to study?",
                    image=None
                ),
                options=[
                    TrueFalseOptionContent(id="1", text="True", image=None, is_correct=True),
                    TrueFalseOptionContent(id="2", text="False", image=None, is_correct=False)
                ]
            )
        else:  # ordering_task
            content = OrderingTaskContent(
                sequences=[f"Learn about {title}", "Practice the concepts", "Apply the knowledge", "Master the skills"]
            )
        
        return PlaygroundItem(
            title=f"Question about {title}",
            description=f"A {question_type.value} question about {title}",
            type=question_type,
            content=content,
            correct_response=PlaygroundResponse(
                text=f"This demonstrates understanding of {title} concepts.",
                image=None
            ),
            incorrect_response=PlaygroundResponse(
                text=f"Review the key concepts of {title} for better understanding.",
                image=None
            ),
            hints=f"Think about the fundamental principles of {title}",
            order=order
        )
