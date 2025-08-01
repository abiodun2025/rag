#!/usr/bin/env python3
"""
Test Content Generation
======================

Test the new ChatGPT-like content generation feature.
"""

import sys
import os
import asyncio

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.smart_master_agent import smart_master_agent

async def test_content_generation():
    """Test the content generation feature."""
    
    print("🧠 Testing ChatGPT-like Content Generation")
    print("=" * 60)
    
    # Test cases
    test_cases = [
        "write about artificial intelligence and its impact on society",
        "generate content about climate change and sustainability",
        "create a professional article about digital marketing strategies",
        "write a creative story about time travel",
        "generate an analytical report about blockchain technology",
        "write about personal development and growth mindset",
        "create content about renewable energy sources",
        "write a blog post about healthy eating habits",
        "generate a comprehensive report about cybersecurity threats",
        "write about the future of remote work"
    ]
    
    for i, test_message in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}: {test_message}")
        print("-" * 50)
        
        try:
            # Process the message
            result = await smart_master_agent.process_message(
                message=test_message,
                session_id=f"test_session_{i}",
                user_id="test_user"
            )
            
            # Display results
            intent = result.get("intent_analysis", {}).get("intent", "unknown")
            confidence = result.get("intent_analysis", {}).get("confidence", 0)
            execution_result = result.get("execution_result", {})
            
            print(f"🎯 Intent: {intent} (confidence: {confidence:.2f})")
            print(f"✅ Success: {execution_result.get('success', False)}")
            
            if execution_result.get('success'):
                result_data = execution_result.get('result', {})
                action = result_data.get('action', 'unknown')
                
                if action == 'content_generated':
                    topic = result_data.get('topic', 'Unknown topic')
                    style = result_data.get('style', 'informative')
                    length = result_data.get('length', 'medium')
                    paragraph_count = result_data.get('paragraph_count', 0)
                    word_count = result_data.get('word_count', 0)
                    content = result_data.get('content', '')
                    
                    print(f"📄 Topic: {topic}")
                    print(f"🎭 Style: {style}")
                    print(f"📏 Length: {length}")
                    print(f"📊 Stats: {paragraph_count} paragraphs, {word_count} words")
                    print(f"📝 Content Preview:")
                    print("-" * 30)
                    
                    # Show first 200 characters of content
                    preview = content[:200] + "..." if len(content) > 200 else content
                    print(preview)
                    print("-" * 30)
                    
                else:
                    print(f"📋 Action: {action}")
                    print(f"📄 Note: {result_data.get('note', 'No note')}")
            else:
                print(f"❌ Error: {execution_result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
        
        print("\n" + "=" * 60)

async def test_specific_styles():
    """Test different content styles."""
    
    print("\n🎨 Testing Different Content Styles")
    print("=" * 60)
    
    style_tests = [
        ("write a professional article about business strategy", "professional"),
        ("create a creative story about space exploration", "creative"),
        ("generate an analytical report about data science trends", "analytical"),
        ("write a conversational blog about travel experiences", "conversational"),
        ("write about machine learning algorithms", "informative")
    ]
    
    for topic, expected_style in style_tests:
        print(f"\n📝 Topic: {topic}")
        print(f"🎭 Expected Style: {expected_style}")
        print("-" * 40)
        
        try:
            result = await smart_master_agent.process_message(
                message=topic,
                session_id="style_test",
                user_id="test_user"
            )
            
            execution_result = result.get("execution_result", {})
            if execution_result.get('success'):
                result_data = execution_result.get('result', {})
                actual_style = result_data.get('style', 'unknown')
                content = result_data.get('content', '')
                
                print(f"🎭 Actual Style: {actual_style}")
                print(f"📝 Content Preview:")
                print("-" * 30)
                
                # Show first 300 characters
                preview = content[:300] + "..." if len(content) > 300 else content
                print(preview)
                print("-" * 30)
            else:
                print(f"❌ Error: {execution_result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")

async def main():
    """Main test function."""
    
    print("🚀 Starting Content Generation Tests")
    print("=" * 60)
    
    # Test basic content generation
    await test_content_generation()
    
    # Test different styles
    await test_specific_styles()
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    asyncio.run(main()) 