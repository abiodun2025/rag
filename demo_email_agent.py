#!/usr/bin/env python3
"""
Email Agent Demo Script
=======================

This script demonstrates how to test the email agent functionality
with example conversations and expected responses.
"""

import asyncio
import aiohttp
import json
import time

async def demo_email_conversation():
    """Demo email conversation with the agent."""
    print("🎭 Email Agent Demo")
    print("=" * 50)
    
    # Example conversation flow
    conversation = [
        {
            "user": "Hello! Can you help me send an email?",
            "expected": "Agent should greet and offer to help with email"
        },
        {
            "user": "Send an email to test@example.com with subject 'Test Email' and body 'This is a test email from the agent.'",
            "expected": "Agent should understand and attempt to send email"
        },
        {
            "user": "Compose an email to john@company.com about AI project updates. Subject should be 'AI Project Update' and include information about our progress.",
            "expected": "Agent should compose email with business context"
        },
        {
            "user": "Send an email to tech@startup.com with subject 'Meeting Request' and body 'I would like to schedule a meeting to discuss AI integration opportunities.'",
            "expected": "Agent should send email with meeting request"
        }
    ]
    
    async with aiohttp.ClientSession() as session:
        for i, turn in enumerate(conversation, 1):
            print(f"\n💬 Turn {i}:")
            print(f"👤 User: {turn['user']}")
            print(f"🎯 Expected: {turn['expected']}")
            print("-" * 50)
            
            payload = {
                "message": turn["user"],
                "session_id": None,
                "user_id": "demo_user",
                "search_type": "hybrid"
            }
            
            try:
                async with session.post(
                    "http://localhost:8058/chat/stream",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 200:
                        response_text = await response.text()
                        print(f"🤖 Agent Response: {response_text[:200]}...")
                        
                        # Check for email-related keywords
                        email_keywords = ["email", "compose", "send", "gmail", "recipient", "subject", "body"]
                        found_keywords = [kw for kw in email_keywords if kw in response_text.lower()]
                        
                        if found_keywords:
                            print(f"✅ Agent mentioned email: {found_keywords}")
                        else:
                            print("⚠️  Agent didn't mention email in response")
                            
                    else:
                        print(f"❌ Request failed with status {response.status}")
                        
            except Exception as e:
                print(f"❌ Connection error: {e}")
            
            # Small delay between requests
            await asyncio.sleep(1)

def show_cli_demo():
    """Show CLI demo instructions."""
    print("\n💻 CLI Demo Instructions:")
    print("=" * 50)
    
    print("1. Start the API server:")
    print("   python3 -m uvicorn agent.api:app --host 0.0.0.0 --port 8058")
    print("\n2. In another terminal, start the CLI:")
    print("   python3 cli.py")
    print("\n3. Try this conversation:")
    print("   You: Hello! Can you help me send an email?")
    print("   Agent: [Should greet and offer help]")
    print("\n   You: Send an email to test@example.com with subject 'Test Email' and body 'This is a test email.'")
    print("   Agent: [Should understand and attempt to send]")
    print("\n   You: Compose an email to john@company.com about AI updates")
    print("   Agent: [Should compose email with context]")

def show_expected_behavior():
    """Show expected behavior for different scenarios."""
    print("\n📋 Expected Behavior:")
    print("=" * 50)
    
    scenarios = [
        {
            "scenario": "Without Gmail Credentials",
            "behavior": [
                "Agent understands email requests",
                "Agent attempts to use email tool",
                "Tool returns error about missing credentials",
                "Agent explains the issue to user"
            ]
        },
        {
            "scenario": "With Gmail Credentials",
            "behavior": [
                "Agent composes and sends emails",
                "First run opens browser for OAuth",
                "Subsequent runs use cached token",
                "Emails sent via Gmail API"
            ]
        },
        {
            "scenario": "Interactive CLI",
            "behavior": [
                "Agent responds to email commands",
                "Agent asks for missing information",
                "Agent provides helpful feedback",
                "Agent handles errors gracefully"
            ]
        }
    ]
    
    for scenario in scenarios:
        print(f"\n🎯 {scenario['scenario']}:")
        for behavior in scenario['behavior']:
            print(f"   • {behavior}")

def main():
    """Main demo function."""
    print("🎭 Email Agent Demo")
    print("=" * 50)
    
    print("This demo shows how to test the email agent functionality.")
    print("The agent should understand and respond to email requests.")
    
    # Show expected behavior
    show_expected_behavior()
    
    # Show CLI demo
    show_cli_demo()
    
    # Run API demo if server is available
    print("\n🌐 Running API Demo...")
    try:
        asyncio.run(demo_email_conversation())
    except Exception as e:
        print(f"❌ API demo failed: {e}")
        print("💡 Make sure the API server is running:")
        print("   python3 -m uvicorn agent.api:app --host 0.0.0.0 --port 8058")
    
    print("\n" + "="*50)
    print("✅ Demo Complete!")
    print("="*50)
    print("\n📝 Next Steps:")
    print("1. Set up Gmail credentials for full functionality")
    print("2. Test interactively with CLI")
    print("3. Try different email scenarios")

if __name__ == "__main__":
    main() 