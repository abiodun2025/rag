#!/usr/bin/env python3
"""
Test Academic Writer
==================

Test the new academic writing capabilities.
"""

import sys
import os
import asyncio

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.academic_writer import academic_writer
from agent.smart_master_agent import smart_master_agent

async def test_academic_writer_direct():
    """Test the academic writer directly."""
    
    print("🎓 Testing Academic Writer Directly")
    print("=" * 60)
    
    # Test different types of academic content
    test_cases = [
        {
            "topic": "artificial intelligence in healthcare",
            "content_type": "research_paper",
            "style": "analytical",
            "length": "medium",
            "academic_level": "graduate"
        },
        {
            "topic": "climate change and renewable energy",
            "content_type": "essay",
            "style": "argumentative",
            "length": "short",
            "academic_level": "undergraduate"
        },
        {
            "topic": "traditional vs online education",
            "content_type": "essay",
            "style": "compare_contrast",
            "length": "medium",
            "academic_level": "high_school"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test Case {i}: {test_case['content_type']} about {test_case['topic']}")
        print("-" * 50)
        
        result = academic_writer.write_academic_content(**test_case)
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"✅ Success!")
            print(f"📊 Word Count: {result['word_count']}")
            print(f"📄 Estimated Pages: {result['estimated_pages']}")
            print(f"🎨 Style: {result['style']}")
            print(f"🎓 Level: {result['academic_level']}")
            
            # Show first few lines of content
            content_lines = result['content'].split('\n')
            print(f"\n📝 Content Preview:")
            print("-" * 30)
            for line in content_lines[:10]:  # Show first 10 lines
                if line.strip():
                    print(line)
            if len(content_lines) > 10:
                print("... (content continues)")

async def test_smart_agent_academic():
    """Test academic writing through the smart agent."""
    
    print("\n🧠 Testing Academic Writing Through Smart Agent")
    print("=" * 60)
    
    # Test different academic writing commands
    test_commands = [
        "write academic essay about machine learning applications",
        "write research paper on renewable energy technologies",
        "write argumentative essay about remote work policies",
        "write analytical essay about social media impact",
        "write compare contrast essay about traditional vs online shopping"
    ]
    
    for i, command in enumerate(test_commands, 1):
        print(f"\n🎯 Test Command {i}: {command}")
        print("-" * 50)
        
        try:
            result = await smart_master_agent.process_message(
                message=command,
                session_id=f"test_session_{i}",
                user_id="test_user"
            )
            
            print(f"🎯 Intent: {result.get('intent', 'unknown')}")
            print(f"✅ Success: {result.get('success', False)}")
            print(f"📝 Note: {result.get('note', 'No note')}")
            
            # Show content preview if available
            if 'content' in result:
                content_lines = result['content'].split('\n')
                print(f"\n📝 Content Preview:")
                print("-" * 30)
                for line in content_lines[:8]:  # Show first 8 lines
                    if line.strip():
                        print(line)
                if len(content_lines) > 8:
                    print("... (content continues)")
            
        except Exception as e:
            print(f"❌ Error: {e}")

async def main():
    """Main test function."""
    
    print("🚀 Starting Academic Writer Tests")
    print("=" * 60)
    
    # Test direct academic writer
    await test_academic_writer_direct()
    
    # Test through smart agent
    await test_smart_agent_academic()
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    asyncio.run(main()) 