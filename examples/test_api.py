#!/usr/bin/env python3
"""
Example usage of VizLearn API
Demonstrates how to use the streaming and batch endpoints
"""

import asyncio
import aiohttp
import json
import time

# Configuration
API_BASE_URL = "http://localhost:8000"
API_KEY = "vizlearn-static-key-2025"

async def test_health_check():
    """Test the health check endpoint"""
    print("🏥 Testing health check...")
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{API_BASE_URL}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Health check passed: {data}")
                else:
                    print(f"❌ Health check failed: {response.status}")
        except Exception as e:
            print(f"❌ Health check error: {e}")

async def test_batch_generation():
    """Test batch content generation"""
    print("\n📚 Testing batch content generation...")
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "title": "Introduction to Machine Learning",
        "description": "Basic concepts of machine learning including supervised and unsupervised learning",
        "num_questions": 3,
        "question_types": ["fill_in_the_blank", "true_false", "ordering_task"]
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            start_time = time.time()
            async with session.post(
                f"{API_BASE_URL}/generate-content",
                headers=headers,
                json=payload
            ) as response:
                end_time = time.time()
                
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Batch generation completed in {end_time - start_time:.2f}s")
                    print(f"Generated {data['total_questions']} questions")
                    
                    # Display first question as example
                    if data['playground_items']:
                        first_question = data['playground_items'][0]
                        print(f"\nExample question:")
                        print(f"  Title: {first_question['title']}")
                        print(f"  Type: {first_question['type']}")
                        print(f"  Content: {json.dumps(first_question['content'], indent=2)}")
                else:
                    error_text = await response.text()
                    print(f"❌ Batch generation failed: {response.status} - {error_text}")
                    
        except Exception as e:
            print(f"❌ Batch generation error: {e}")

async def test_streaming_generation():
    """Test streaming content generation"""
    print("\n🌊 Testing streaming content generation...")
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "title": "Python Programming Basics",
        "description": "Variables, data types, control structures, and functions in Python",
        "num_questions": 3,
        "question_types": ["fill_in_the_blank", "true_false"]
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            start_time = time.time()
            async with session.post(
                f"{API_BASE_URL}/generate-content/stream",
                headers=headers,
                json=payload
            ) as response:
                
                if response.status == 200:
                    print("✅ Streaming started...")
                    question_count = 0
                    
                    # Read Server-Sent Events
                    async for line in response.content:
                        line_text = line.decode('utf-8').strip()
                        
                        if line_text.startswith('data: '):
                            try:
                                data = json.loads(line_text[6:])  # Remove 'data: ' prefix
                                
                                if data['status'] == 'started':
                                    print(f"📝 {data['message']}")
                                elif data['status'] == 'progress':
                                    question_count += 1
                                    item = data['item']
                                    print(f"✨ Question {question_count}: {item['title']} ({item['type']})")
                                elif data['status'] == 'completed':
                                    end_time = time.time()
                                    print(f"🎉 {data['message']} in {end_time - start_time:.2f}s")
                                    break
                                elif data['status'] == 'error':
                                    print(f"❌ Error: {data['message']}")
                                    break
                                    
                            except json.JSONDecodeError:
                                continue  # Skip invalid JSON lines
                else:
                    error_text = await response.text()
                    print(f"❌ Streaming failed: {response.status} - {error_text}")
                    
        except Exception as e:
            print(f"❌ Streaming error: {e}")

async def test_content_types():
    """Test getting supported content types"""
    print("\n📋 Testing content types endpoint...")
    
    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(
                f"{API_BASE_URL}/content-types",
                headers=headers
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    print("✅ Supported content types:")
                    for content_type in data['supported_types']:
                        description = data['descriptions'].get(content_type, 'No description')
                        print(f"  - {content_type}: {description}")
                else:
                    error_text = await response.text()
                    print(f"❌ Content types request failed: {response.status} - {error_text}")
                    
        except Exception as e:
            print(f"❌ Content types error: {e}")

async def main():
    """Run all tests"""
    print("🚀 VizLearn API Test Suite")
    print("=" * 50)
    
    await test_health_check()
    await test_content_types()
    await test_batch_generation()
    await test_streaming_generation()
    
    print("\n" + "=" * 50)
    print("🎯 Test suite completed!")

if __name__ == "__main__":
    asyncio.run(main())
