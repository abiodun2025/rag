#!/usr/bin/env python3
"""
Simple Email Agent Test
=======================

This script tests the agent's ability to understand and respond to email requests
without requiring Gmail credentials.
"""

import asyncio
import aiohttp
import json

async def test_email_understanding():
    """Test if the agent understands email requests."""
    print("🧠 Testing Agent Email Understanding...")
    
    test_cases = [
        {
            "name": "Direct Email Request",
            "message": "Send an email to test@example.com with subject 'Test Email' and body 'This is a test email.'"
        },
        {
            "name": "Email with Context",
            "message": "Compose an email to john@company.com about AI project updates. Subject should be 'AI Project Update' and include information about our progress."
        },
        {
            "name": "Email with Business Context",
            "message": "Send an email to tech@startup.com with subject 'Meeting Request' and body 'I would like to schedule a meeting to discuss AI integration opportunities.'"
        }
    ]
    
    async with aiohttp.ClientSession() as session:
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📧 Test Case {i}: {test_case['name']}")
            print("-" * 50)
            
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
                        print(f"📝 Test message: {test_case['message']}")
                        print(f"🤖 Agent should understand and respond to email request")
                        
                        # Read the response
                        response_text = await response.text()
                        print(f"📄 Response length: {len(response_text)} characters")
                        
                        # Check if response mentions email
                        if "email" in response_text.lower() or "compose" in response_text.lower():
                            print("✅ Agent appears to understand email request")
                        else:
                            print("⚠️  Agent response doesn't mention email - may need prompt adjustment")
                            
                    else:
                        print(f"❌ Request failed with status {response.status}")
                        
            except Exception as e:
                print(f"❌ Connection error: {e}")

def test_cli_instructions():
    """Provide CLI testing instructions."""
    print("\n💻 CLI Testing Instructions:")
    print("1. Start the API server:")
    print("   python3 -m uvicorn agent.api:app --host 0.0.0.0 --port 8058")
    print("\n2. In another terminal, start the CLI:")
    print("   python3 cli.py")
    print("\n3. Try these email commands:")
    print("   - 'Send an email to test@example.com with subject Test and body Hello'")
    print("   - 'Compose an email to john@company.com about AI updates'")
    print("   - 'Send an email to tech@startup.com with subject Meeting Request'")
    print("\n4. The agent should:")
    print("   - Understand the email request")
    print("   - Ask for missing information if needed")
    print("   - Attempt to use the email tool")
    print("   - Show an error about missing credentials (expected)")

def main():
    """Main test function."""
    print("🧠 Email Agent Understanding Test")
    print("=" * 50)
    
    print("This test checks if the agent understands email requests")
    print("without requiring Gmail credentials.")
    
    # Test via API
    try:
        asyncio.run(test_email_understanding())
    except Exception as e:
        print(f"❌ API test failed: {e}")
        print("💡 Make sure the API server is running:")
        print("   python3 -m uvicorn agent.api:app --host 0.0.0.0 --port 8058")
    
    # CLI instructions
    test_cli_instructions()
    
    print("\n" + "="*50)
    print("📋 Next Steps for Full Email Functionality:")
    print("1. Set up Gmail API credentials (see test_email_setup.py)")
    print("2. Install Gmail packages: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
    print("3. Test with real email sending capability")

if __name__ == "__main__":
    main() 