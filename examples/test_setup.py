#!/usr/bin/env python3
"""
Quick test to verify VizLearn setup without LLM dependency
"""

import sys
import json
from pathlib import Path

# Add parent directory to path to access src
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))

def test_models():
    """Test that models can be imported and created"""
    print("🧪 Testing Pydantic models...")
    
    try:
        from src.models import (
            PlaygroundItem,
            QuestionType,
            FillInTheBlankContent,
            TrueFalseContent,
            TrueFalseQuestionContent,
            TrueFalseOptionContent,
            OrderingTaskContent,
            ContentGenerationRequest,
            PlaygroundResponse
        )
        
        # Test FillInTheBlankContent
        fill_content = FillInTheBlankContent(
            template="Python is a ____ language that supports ____.",
            gaps=["high-level", "multiple paradigms"]
        )
        
        # Test TrueFalseContent
        true_false_content = TrueFalseContent(
            question=TrueFalseQuestionContent(
                text="Python is interpreted?",
                image=None
            ),
            options=[
                TrueFalseOptionContent(
                    id="1",
                    text="True",
                    image=None,
                    is_correct=True
                ),
                TrueFalseOptionContent(
                    id="2", 
                    text="False",
                    image=None,
                    is_correct=False
                )
            ]
        )
        
        # Test OrderingTaskContent
        ordering_content = OrderingTaskContent(
            sequences=["Write code", "Test code", "Deploy code"]
        )
        
        # Test PlaygroundItem with different content types
        items = []
        
        # Fill in the blank item
        item1 = PlaygroundItem(
            title="Python Basics",
            description="Test fill in the blank",
            type=QuestionType.FILL_IN_THE_BLANK,
            content=fill_content,
            correct_response=PlaygroundResponse(text="Correct!", image=None),
            hints="Think about Python's characteristics",
            order=1
        )
        items.append(item1)
        
        # True/False item
        item2 = PlaygroundItem(
            title="Python Nature",
            description="Test true/false question",
            type=QuestionType.TRUE_FALSE,
            content=true_false_content,
            correct_response=PlaygroundResponse(text="Yes, Python is interpreted!", image=None),
            hints="Consider how Python code is executed",
            order=2
        )
        items.append(item2)
        
        # Ordering item
        item3 = PlaygroundItem(
            title="Development Process",
            description="Test ordering question",
            type=QuestionType.ORDERING_TASK,
            content=ordering_content,
            correct_response=PlaygroundResponse(text="Good job!", image=None),
            hints="Think about the software development lifecycle",
            order=3
        )
        items.append(item3)
        
        # Test ContentGenerationRequest
        request = ContentGenerationRequest(
            title="Test Topic",
            description="Test description",
            num_questions=3,
            question_types=[
                QuestionType.FILL_IN_THE_BLANK,
                QuestionType.TRUE_FALSE,
                QuestionType.ORDERING_TASK
            ]
        )
        
        print(f"✅ Created {len(items)} test playground items")
        print(f"✅ Created content generation request")
        
        # Test JSON serialization
        for i, item in enumerate(items, 1):
            item_dict = item.model_dump()
            item_json = json.dumps(item_dict, indent=2)
            print(f"✅ Item {i} JSON serialization successful")
        
        request_dict = request.model_dump()
        request_json = json.dumps(request_dict, indent=2)
        print("✅ Request JSON serialization successful")
        
        print("✅ All model tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Model test failed: {e}")
        return False

def test_fastapi_import():
    """Test that FastAPI can be imported"""
    print("🚀 Testing FastAPI imports...")
    
    try:
        from fastapi import FastAPI, HTTPException, Depends
        from fastapi.security import HTTPBearer
        from fastapi.responses import StreamingResponse
        from fastapi.middleware.cors import CORSMiddleware
        import uvicorn
        
        print("✅ FastAPI imports successful")
        return True
        
    except Exception as e:
        print(f"❌ FastAPI import failed: {e}")
        return False

def test_langchain_imports():
    """Test that LangChain components can be imported"""
    print("🔗 Testing LangChain imports...")
    
    try:
        from langchain_openai import ChatOpenAI
        from langchain.schema import HumanMessage, SystemMessage
        from langchain.tools import Tool
        from ddgs import DDGS
        
        print("✅ LangChain imports successful")
        return True
        
    except Exception as e:
        print(f"❌ LangChain import failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 VizLearn Setup Test Suite")
    print("=" * 40)
    
    tests = [
        test_fastapi_import,
        test_langchain_imports,
        test_models
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print()  # Add spacing between tests
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            print()
    
    print("=" * 40)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! VizLearn is ready to run.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the errors above.")
        return 1

if __name__ == "__main__":
    exit(main())
