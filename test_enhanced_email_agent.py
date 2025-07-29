#!/usr/bin/env python3
"""
Test script for enhanced email composition capabilities of the Smart Agent
"""

import asyncio
import sys
import os
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.getcwd())

from agent.smart_master_agent import SmartMasterAgent

async def test_email_composition():
    """Test various email composition scenarios."""
    
    agent = SmartMasterAgent()
    session_id = f"email_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Test cases for different email composition scenarios
    test_cases = [
        {
            "name": "Basic email with address",
            "message": "send email to test@example.com asking about the meeting tomorrow"
        },
        {
            "name": "Email with natural language",
            "message": "write to john@gmail.com regarding the project deadline and ask for an update"
        },
        {
            "name": "Email with subject and body",
            "message": "compose email to sarah@company.com about budget approval. Please review the quarterly budget and let me know if you approve the new spending plan."
        },
        {
            "name": "Email with just address",
            "message": "email to admin@website.com"
        },
        {
            "name": "Complex email instruction",
            "message": "send an email to mywork461@gmail.com asking John about the interview schedule for next week and if he can confirm the time slots"
        }
    ]
    
    print("🧪 Testing Enhanced Email Composition Capabilities")
    print("=" * 60)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📧 Test {i}: {test_case['name']}")
        print(f"💬 Input: {test_case['message']}")
        print("-" * 40)
        
        try:
            # Analyze intent
            intent_result = agent.analyze_intent(test_case['message'])
            print(f"🧠 Intent: {intent_result.intent.value}")
            print(f"🎯 Confidence: {intent_result.confidence:.2f}")
            print(f"📋 Extracted Data: {intent_result.extracted_data}")
            
            # Execute intent
            if intent_result.intent.value == "email":
                result = await agent.execute_intent(intent_result, session_id)
                print(f"⚡ Action: {result.get('action', 'unknown')}")
                print(f"💭 Result: {result.get('note', 'No message')}")
                
                # Show details if available
                if 'details' in result:
                    print(f"📊 Details: {result['details']}")
            else:
                print(f"⚠️  Intent not recognized as email: {intent_result.intent.value}")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        print("-" * 40)

async def main():
    """Main test function."""
    print("🚀 Starting Enhanced Email Agent Test")
    print("=" * 60)
    
    await test_email_composition()
    
    print("\n✅ Email composition testing completed!")

if __name__ == "__main__":
    asyncio.run(main()) 