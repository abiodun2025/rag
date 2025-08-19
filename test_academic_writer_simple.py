#!/usr/bin/env python3
"""
Test Academic Writer (Simple)
============================

Test the enhanced academic writing capabilities directly.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.academic_writer import academic_writer

def test_academic_writer_enhanced():
    """Test the enhanced academic writer with comprehensive content."""
    
    print("🎓 Testing Enhanced Academic Writer")
    print("=" * 60)
    
    # Test different types of academic content with enhanced word counts
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
            for line in content_lines[:15]:  # Show first 15 lines
                if line.strip():
                    print(line)
            if len(content_lines) > 15:
                print("... (content continues)")
            
            print(f"\n📊 Total Content Length: {len(result['content'])} characters")
            print(f"📝 Number of Paragraphs: {len([line for line in content_lines if line.strip() and not line.startswith('=')])}")

def test_detailed_paragraphs():
    """Test the detailed paragraph generation specifically."""
    
    print("\n\n📝 Testing Detailed Paragraph Generation")
    print("=" * 60)
    
    # Test a specific case to show detailed paragraphs
    test_case = {
        "topic": "machine learning applications in business",
        "content_type": "essay",
        "style": "analytical",
        "length": "medium",
        "academic_level": "undergraduate"
    }
    
    print(f"🎯 Testing: {test_case['content_type']} about {test_case['topic']}")
    print(f"📏 Length: {test_case['length']}")
    print(f"🎓 Level: {test_case['academic_level']}")
    print("-" * 50)
    
    result = academic_writer.write_academic_content(**test_case)
    
    if "error" not in result:
        content_lines = result['content'].split('\n')
        
        # Find and display main body paragraphs
        main_body_start = None
        for i, line in enumerate(content_lines):
            if "MAIN BODY" in line:
                main_body_start = i + 1
                break
        
        if main_body_start:
            print("📝 Main Body Paragraphs:")
            print("-" * 30)
            
            paragraph_count = 0
            for line in content_lines[main_body_start:]:
                if line.strip() and not line.startswith('=') and not line.startswith('CONCLUSION'):
                    if paragraph_count < 3:  # Show first 3 paragraphs
                        print(f"\n📄 Paragraph {paragraph_count + 1}:")
                        print(line)
                        paragraph_count += 1
                    else:
                        break
            
            print(f"\n📊 Total Word Count: {result['word_count']}")
            print(f"📄 Estimated Pages: {result['estimated_pages']}")

def main():
    """Main test function."""
    
    print("🚀 Starting Enhanced Academic Writer Tests")
    print("=" * 60)
    
    # Test enhanced academic writer
    test_academic_writer_enhanced()
    
    # Test detailed paragraphs
    test_detailed_paragraphs()
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    main() 