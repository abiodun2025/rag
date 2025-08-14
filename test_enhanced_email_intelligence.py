#!/usr/bin/env python3
"""
Enhanced Intelligent Email Composition Test
==========================================

This script demonstrates the advanced intelligent email composition features
including context awareness, personalization, and sophisticated intent detection.
"""

import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.email_composer import email_composer

def test_enhanced_intent_detection():
    """Test the enhanced intent detection with various patterns."""
    
    print("🧠 Testing Enhanced Intent Detection")
    print("=" * 50)
    
    # Test cases for different intents
    test_cases = [
        {
            "description": "Meeting Request (various patterns)",
            "messages": [
                "send an email to john@company.com about scheduling a meeting",
                "email sarah@company.com to set up a meeting",
                "send a meeting request to mike@company.com",
                "arrange a meeting with lisa@company.com",
                "book a meeting with david@company.com"
            ],
            "expected_intent": "meeting_request"
        },
        {
            "description": "Thank You Messages",
            "messages": [
                "send a thank you email to jane@company.com for their help",
                "email bob@company.com thanking them for support",
                "send appreciation email to alice@company.com",
                "thank carol@company.com for their assistance"
            ],
            "expected_intent": "thank_you"
        },
        {
            "description": "Inquiries and Questions",
            "messages": [
                "send an inquiry to tom@company.com about the project",
                "email jerry@company.com with questions",
                "ask linda@company.com for information",
                "send questions to frank@company.com"
            ],
            "expected_intent": "inquiry"
        },
        {
            "description": "Updates and Status",
            "messages": [
                "send an update to paul@company.com about progress",
                "email mary@company.com with status report",
                "update steve@company.com on current status",
                "send progress report to karen@company.com"
            ],
            "expected_intent": "update"
        },
        {
            "description": "Urgent Communications",
            "messages": [
                "send urgent email to rick@company.com about critical issue",
                "email urgent matter to diane@company.com asap",
                "send emergency email to kevin@company.com",
                "urgent message to laura@company.com"
            ],
            "expected_intent": "urgent"
        },
        {
            "description": "Follow-ups",
            "messages": [
                "follow up with mark@company.com about our conversation",
                "send followup email to nancy@company.com",
                "checking in with peter@company.com",
                "touch base with susan@company.com"
            ],
            "expected_intent": "followup"
        },
        {
            "description": "Collaboration Proposals",
            "messages": [
                "send collaboration proposal to alex@company.com",
                "email partnership opportunity to rachel@company.com",
                "propose collaboration with chris@company.com",
                "send partnership offer to emma@company.com"
            ],
            "expected_intent": "collaboration"
        },
        {
            "description": "Feedback Requests",
            "messages": [
                "send feedback request to dan@company.com",
                "email jessica@company.com for review",
                "ask for feedback from ryan@company.com",
                "request opinion from ashley@company.com"
            ],
            "expected_intent": "feedback"
        }
    ]
    
    for test_case in test_cases:
        print(f"\n📧 {test_case['description']}")
        print("-" * 40)
        
        for i, message in enumerate(test_case['messages'], 1):
            # Extract email (simplified)
            email = "test@company.com"  # Placeholder
            if "@" in message:
                email = message.split()[-1]  # Get last word as email
            
            composed_email = email_composer.compose_email(message, email)
            
            print(f"  {i}. Original: {message[:50]}...")
            print(f"     Intent: {composed_email['intent']}")
            print(f"     Tone: {composed_email['tone']}")
            print(f"     Urgency: {composed_email['urgency']}")
            print(f"     Formality: {composed_email['formality']}")
            
            if composed_email['intent'] == test_case['expected_intent']:
                print(f"     ✅ Correct intent detected!")
            else:
                print(f"     ⚠️  Expected {test_case['expected_intent']}, got {composed_email['intent']}")

def test_recipient_name_extraction():
    """Test recipient name extraction from email addresses."""
    
    print("\n👤 Testing Recipient Name Extraction")
    print("=" * 50)
    
    test_emails = [
        "john.doe@company.com",
        "sarah_smith@company.com", 
        "mike@company.com",
        "lisa.johnson@company.com",
        "david_wilson@company.com",
        "jane.brown@company.com"
    ]
    
    for email in test_emails:
        composed_email = email_composer.compose_email("test message", email)
        print(f"📧 {email} → {composed_email['recipient_name']}")

def test_tone_and_formality_detection():
    """Test tone and formality detection."""
    
    print("\n🎭 Testing Tone and Formality Detection")
    print("=" * 50)
    
    tone_test_cases = [
        {
            "message": "send a friendly email to john@company.com",
            "expected_tone": "friendly",
            "expected_formality": "casual"
        },
        {
            "message": "send a professional business email to sarah@company.com",
            "expected_tone": "professional", 
            "expected_formality": "formal"
        },
        {
            "message": "send urgent email to mike@company.com",
            "expected_tone": "urgent",
            "expected_formality": "casual"
        },
        {
            "message": "send formal corporate email to lisa@company.com",
            "expected_tone": "professional",
            "expected_formality": "formal"
        }
    ]
    
    for test_case in tone_test_cases:
        composed_email = email_composer.compose_email(test_case['message'], "test@company.com")
        
        print(f"📝 Message: {test_case['message']}")
        print(f"   Detected tone: {composed_email['tone']}")
        print(f"   Detected formality: {composed_email['formality']}")
        print(f"   Expected tone: {test_case['expected_tone']}")
        print(f"   Expected formality: {test_case['expected_formality']}")
        
        tone_match = composed_email['tone'] == test_case['expected_tone']
        formality_match = composed_email['formality'] == test_case['expected_formality']
        
        if tone_match and formality_match:
            print("   ✅ Both tone and formality correctly detected!")
        else:
            print("   ⚠️  Some detection issues")
        print()

def test_email_variety():
    """Test that emails have variety and don't repeat the same template."""
    
    print("\n🎲 Testing Email Variety")
    print("=" * 50)
    
    # Send multiple emails with the same intent to see variety
    test_message = "send a meeting request to john@company.com"
    email = "john@company.com"
    
    print("Sending 3 meeting request emails to test variety:")
    print()
    
    for i in range(3):
        composed_email = email_composer.compose_email(test_message, email)
        
        print(f"📧 Email {i+1}:")
        print(f"Subject: {composed_email['subject']}")
        print(f"Body preview: {composed_email['body'][:100]}...")
        print(f"Intent: {composed_email['intent']}")
        print(f"Tone: {composed_email['tone']}")
        print()

def test_complex_scenarios():
    """Test complex real-world scenarios."""
    
    print("\n🌍 Testing Complex Real-World Scenarios")
    print("=" * 50)
    
    complex_scenarios = [
        {
            "description": "Urgent Business Meeting Request",
            "message": "send an urgent professional email to ceo@company.com about scheduling a critical business meeting asap",
            "email": "ceo@company.com"
        },
        {
            "description": "Friendly Follow-up with Feedback",
            "message": "send a friendly followup email to colleague@company.com asking for feedback on our recent project",
            "email": "colleague@company.com"
        },
        {
            "description": "Formal Collaboration Proposal",
            "message": "send a formal business email to partner@company.com proposing a strategic collaboration opportunity",
            "email": "partner@company.com"
        },
        {
            "description": "Grateful Thank You with Introduction",
            "message": "send a grateful thank you email to mentor@company.com and introduce our new team member",
            "email": "mentor@company.com"
        }
    ]
    
    for scenario in complex_scenarios:
        print(f"\n📧 {scenario['description']}")
        print("-" * 40)
        
        composed_email = email_composer.compose_email(scenario['message'], scenario['email'])
        
        print(f"Original: {scenario['message']}")
        print(f"Subject: {composed_email['subject']}")
        print(f"Recipient: {composed_email['recipient_name']}")
        print(f"Intent: {composed_email['intent']}")
        print(f"Tone: {composed_email['tone']}")
        print(f"Urgency: {composed_email['urgency']}")
        print(f"Formality: {composed_email['formality']}")
        print(f"Body preview: {composed_email['body'][:150]}...")

def main():
    """Main function to run all tests."""
    
    print("🧠 Enhanced Intelligent Email Composition Demo")
    print("=" * 60)
    print("This demonstrates the advanced features of the smart agent's")
    print("intelligent email composition system.")
    print()
    
    # Run all tests
    test_enhanced_intent_detection()
    test_recipient_name_extraction()
    test_tone_and_formality_detection()
    test_email_variety()
    test_complex_scenarios()
    
    print("\n🎉 Enhanced Demo completed!")
    print("\n💡 Advanced Features Demonstrated:")
    print("   • Enhanced intent detection with regex patterns")
    print("   • Intelligent recipient name extraction")
    print("   • Sophisticated tone and formality detection")
    print("   • Email variety with multiple templates per intent")
    print("   • Context-aware urgency and action detection")
    print("   • Professional signature generation")
    print("   • Complex scenario handling")

if __name__ == "__main__":
    main() 