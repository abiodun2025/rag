#!/usr/bin/env python3
"""
Test Intelligent Email Composition
=================================

This script demonstrates how the smart agent now composes emails intelligently
instead of just copying your exact words.
"""

import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.smart_master_agent import SmartMasterAgent
from agent.email_composer import email_composer

async def test_intelligent_email_composition():
    """Test the intelligent email composition feature."""
    
    print("🧠 Testing Intelligent Email Composition")
    print("=" * 50)
    
    # Test cases with different intents
    test_cases = [
        {
            "description": "Simple greeting",
            "message": "send an email to olaoluwa@multiplatformservices.com saying hello",
            "expected_intent": "greeting"
        },
        {
            "description": "Meeting request",
            "message": "send an email to olaoluwa@multiplatformservices.com about scheduling a meeting",
            "expected_intent": "meeting_request"
        },
        {
            "description": "Thank you message",
            "message": "send an email to olaoluwa@multiplatformservices.com thanking them for their help",
            "expected_intent": "thank_you"
        },
        {
            "description": "Urgent inquiry",
            "message": "send an urgent email to olaoluwa@multiplatformservices.com asking about the project status",
            "expected_intent": "urgent"
        },
        {
            "description": "Business inquiry",
            "message": "send a professional email to olaoluwa@multiplatformservices.com asking about collaboration opportunities",
            "expected_intent": "inquiry"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📧 Test {i}: {test_case['description']}")
        print("-" * 40)
        
        # Test the email composer directly
        user_message = test_case['message']
        to_email = "olaoluwa@multiplatformservices.com"
        
        # Extract email from message (simplified)
        if "olaoluwa@multiplatformservices.com" in user_message:
            composed_email = email_composer.compose_email(user_message, to_email)
            
            print(f"🎯 Original message: {user_message}")
            print(f"📝 Composed subject: {composed_email['subject']}")
            print(f"📄 Composed body:\n{composed_email['body']}")
            print(f"🎭 Intent: {composed_email['intent']}")
            print(f"🎨 Tone: {composed_email['tone']}")
            
            # Check if intent matches expectation
            if composed_email['intent'] == test_case['expected_intent']:
                print("✅ Intent correctly identified!")
            else:
                print(f"⚠️  Intent mismatch: expected {test_case['expected_intent']}, got {composed_email['intent']}")
        
        print()

async def test_smart_agent_email():
    """Test the smart agent's email handling."""
    
    print("\n🤖 Testing Smart Agent Email Processing")
    print("=" * 50)
    
    # Initialize the smart agent
    agent = SmartMasterAgent()
    
    # Test message
    test_message = "send an email to olaoluwa@multiplatformservices.com about scheduling a meeting next week"
    
    print(f"🎯 Test message: {test_message}")
    
    # Analyze intent
    intent_result = agent.analyze_intent(test_message)
    print(f"🎭 Detected intent: {intent_result.intent.value} (confidence: {intent_result.confidence:.2f})")
    
    # Extract data
    extracted_data = intent_result.extracted_data
    print(f"📧 Extracted email: {extracted_data.get('to_email', 'Not found')}")
    print(f"📝 Original message: {extracted_data.get('message', 'Not found')}")
    
    # Test email composition
    if extracted_data.get('to_email'):
        composed_email = email_composer.compose_email(
            user_message=extracted_data.get('message', ''),
            to_email=extracted_data.get('to_email', ''),
            context={"test": True}
        )
        
        print(f"\n📧 Composed Email:")
        print(f"Subject: {composed_email['subject']}")
        print(f"Body:\n{composed_email['body']}")
        print(f"Intent: {composed_email['intent']}")
        print(f"Tone: {composed_email['tone']}")

def main():
    """Main function to run the tests."""
    
    print("🧠 Intelligent Email Composition Demo")
    print("=" * 60)
    print("This demonstrates how the smart agent now writes emails in its own words")
    print("instead of just copying your exact message.")
    print()
    
    # Run the tests
    asyncio.run(test_intelligent_email_composition())
    asyncio.run(test_smart_agent_email())
    
    print("\n🎉 Demo completed!")
    print("\n💡 Key improvements:")
    print("   • Emails are now composed intelligently based on intent")
    print("   • Professional tone and structure are automatically applied")
    print("   • Different email types (meeting, thank you, inquiry, etc.) are handled appropriately")
    print("   • The agent understands context and writes naturally")

if __name__ == "__main__":
    main() 