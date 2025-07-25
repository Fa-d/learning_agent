#!/usr/bin/env python3
"""
Test script to verify the LangChain integration
"""
import asyncio
import sys
import os

# Add the src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.services.content_generation import ContentGenerationService
from src.core.models import QuestionType

async def test_content_generation():
    """Test the enhanced LangChain content generation"""
    print("🧪 Testing Enhanced LangChain Content Generation...")
    
    service = ContentGenerationService()
    
    try:
        # Initialize the service
        print("📡 Initializing service...")
        await service.initialize()
        
        if not service.is_ready():
            print("❌ Service not ready")
            return False
        
        print("✅ Service ready!")
        
        # Test content generation
        print("🔍 Generating content with web search...")
        items = await service.generate_content(
            title="Python Programming", 
            description="Basic Python concepts",
            num_questions=1,
            question_types=[QuestionType.FILL_IN_THE_BLANK]
        )
        
        print(f"✅ Generated {len(items)} items")
        if items:
            item = items[0]
            print(f"📝 Sample question: {item.title}")
            print(f"🔤 Type: {item.type}")
            print(f"📖 Description: {item.description}")
            
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        await service.cleanup()

if __name__ == "__main__":
    success = asyncio.run(test_content_generation())
    if success:
        print("🎉 LangChain integration test PASSED!")
    else:
        print("💥 LangChain integration test FAILED!")
        sys.exit(1)
