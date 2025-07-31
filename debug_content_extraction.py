#!/usr/bin/env python3
"""
Debug Content Extraction
=======================

This script tests the content extraction to see what's being removed.
"""

import sys
import os
import re

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.email_composer import email_composer

def test_content_extraction():
    """Test the content extraction function."""
    
    print("🔍 Testing Content Extraction")
    print("=" * 50)
    
    # Test cases
    test_cases = [
        "send an email scheduling a meeting for 1pm with olaoluwa@multiplatformservices.com",
        "send email to john@company.com about meeting at 2pm tomorrow",
        "email sarah@company.com scheduling meeting 3pm friday",
        "send meeting request to mike@company.com for 4pm today",
        "email lisa@company.com about project update",
        "send thank you email to david@company.com for help",
    ]
    
    for i, test_message in enumerate(test_cases, 1):
        print(f"\n📧 Test {i}: {test_message}")
        print("-" * 40)
        
        # Extract email (simplified)
        email = "test@company.com"
        if "@" in test_message:
            # Find the email address
            email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', test_message)
            if email_match:
                email = email_match.group(0)
        
        # Test the extraction
        extracted_content = email_composer._extract_specific_content(test_message, email)
        
        print(f"📧 Email: {email}")
        print(f"📝 Extracted: '{extracted_content}'")
        
        # Test the full composition
        composed_email = email_composer.compose_email(test_message, email)
        
        print(f"📄 Subject: {composed_email['subject']}")
        print(f"📄 Body: {composed_email['body']}")
        print(f"🎭 Intent: {composed_email['intent']}")

if __name__ == "__main__":
    test_content_extraction() 