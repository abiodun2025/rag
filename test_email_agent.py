#!/usr/bin/env python3
"""
Email Agent Test Script
=======================

This script tests the email agent functionality with various scenarios.
"""

import asyncio
import aiohttp
import json

async def test_email_agent():
    """Test the email agent with different scenarios."""
    
    # Test scenarios
    test_cases = [
        {
            "name": "Basic Email Request",
            "message": "Send an email to test@example.com with subject 'Test Email' and body 'This is a test email from the agent.'"
        },
        {
            "name": "Email with Business Context",
            "message": "Compose an email to john@company.com about the AI project update. Subject should be 'Project Update' and include information about our progress."
        },
        {
            "name": "Email with Tech Context",
            "message": "Send an email to tech@startup.com with subject 'AI Integration Discussion' and body 'I would like to discuss potential AI integration opportunities for our platform.'"
        }
    ]
    
    async with aiohttp.ClientSession() as session:
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n{'='*50}")
            print(f"Test Case {i}: {test_case['name']}")
            print(f"{'='*50}")
            
            # Send request to API
            payload = {
                "message": test_case["message"],
                "session_id": None,
                "user_id": "test_user",
                "search_type": "hybrid"
            }
            
            try:
                async with session.post(
                    "http://localhost:8058/chat/stream",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 200:
                        print(f"✅ Request sent successfully")
                        print(f"📧 Test message: {test_case['message']}")
                        print(f"🤖 Agent should respond with email composition capabilities")
                    else:
                        print(f"❌ Request failed with status {response.status}")
                        
            except Exception as e:
                print(f"❌ Connection error: {e}")

def test_email_tools_directly():
    """Test email tools directly without API."""
    print("\n" + "="*50)
    print("Testing Email Tools Directly")
    print("="*50)
    
    try:
        from agent.tools import compose_email_tool, EmailComposeInput
        
        # Test the email tool function
        test_input = EmailComposeInput(
            to="test@example.com",
            subject="Test Email",
            body="This is a test email from the agent."
        )
        
        print("✅ EmailComposeInput model works")
        print(f"📧 Test input: {test_input}")
        
        # Note: This will fail without credentials, but shows the tool is properly integrated
        print("ℹ️  compose_email_tool is available (requires Gmail credentials to actually send)")
        
    except Exception as e:
        print(f"❌ Error testing email tools: {e}")

if __name__ == "__main__":
    print("Email Agent Test Suite")
    print("=" * 50)
    
    # Test email tools directly
    test_email_tools_directly()
    
    # Test via API
    print("\nTesting via API...")
    asyncio.run(test_email_agent())
    
    print("\n" + "="*50)
    print("Test Complete!")
    print("="*50)
    print("\nTo test manually:")
    print("1. Run: python3 cli.py")
    print("2. Try: 'Send an email to test@example.com with subject Test and body Hello'")
    print("3. The agent should respond with email composition capabilities") 