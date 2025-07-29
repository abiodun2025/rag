#!/usr/bin/env python3
"""
Test Dynamic Email Composer - LLM-Powered Email Generation
"""

import asyncio
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.dynamic_email_composer import analyze_and_compose_email, compose_dynamic_email

async def test_dynamic_email():
    """Test dynamic email composition."""
    print("🚀 Testing Dynamic Email Composer")
    print("=" * 50)
    
    # Test 1: Simple email request
    print("\n📧 Test 1: Simple email request")
    message1 = "send email to test@example.com asking about the project status"
    
    try:
        result1 = await analyze_and_compose_email(message1)
        if result1.get("status") == "success":
            print("✅ Email composed successfully!")
            print(f"📧 To: {result1.get('to_email')}")
            print(f"📝 Subject: {result1.get('subject')}")
            print(f"📄 Body: {result1.get('body_preview')}")
        else:
            print(f"❌ Failed: {result1.get('error')}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Different tones
    print("\n🎭 Test 2: Different tones")
    tones = ["professional", "casual", "formal"]
    
    for tone in tones:
        try:
            result2 = await compose_dynamic_email(
                to_email="test@example.com",
                context="asking about meeting schedule",
                tone=tone,
                urgency="normal"
            )
            if result2.get("status") == "success":
                print(f"✅ {tone.title()} tone: {result2.get('subject')}")
            else:
                print(f"❌ {tone.title()} tone failed: {result2.get('error')}")
        except Exception as e:
            print(f"❌ {tone.title()} tone error: {e}")
    
    print("\n🎉 Dynamic Email Tests Completed!")

if __name__ == "__main__":
    asyncio.run(test_dynamic_email()) 