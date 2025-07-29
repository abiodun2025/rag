#!/usr/bin/env python3
"""Simple test for dynamic email composer."""

import asyncio
import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_email():
    """Test email functionality."""
    print("🚀 Testing Dynamic Email Composer")
    
    try:
        # Test 1: Import the module
        print("📦 Testing imports...")
        from agent.dynamic_email_composer import analyze_and_compose_email
        print("✅ Imports successful")
        
        # Test 2: Test with a simple message
        print("\n📧 Testing email composition...")
        message = "send email to test@example.com asking about project status"
        print(f"Message: {message}")
        
        result = await analyze_and_compose_email(message)
        print(f"Result: {result}")
        
        if result.get("status") == "success":
            print("✅ Email composed successfully!")
            print(f"📧 To: {result.get('to_email')}")
            print(f"📝 Subject: {result.get('subject')}")
            print(f"📄 Body: {result.get('body_preview')}")
        else:
            print(f"❌ Failed: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_email()) 