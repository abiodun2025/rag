#!/usr/bin/env python3
"""
Test email body issue
"""

import sys
import os
sys.path.append("/Users/ola/Desktop/working-mcp-server/count-r-server")

from gmail_email_sender import GmailEmailSender

def test_email_body():
    """Test email with proper body"""
    
    print("📧 Testing Email Body Issue")
    print("=" * 40)
    
    sender = GmailEmailSender()
    
    # Test email with proper body
    to_email = "mywork461@gmail.com"
    subject = "Test Email Body - Debug"
    body = """Hi there!

This is a test email to debug the body issue.

The email should have this content in the body.

Best regards,
Test Script
"""
    
    print(f"📝 Sending test email:")
    print(f"   To: {to_email}")
    print(f"   Subject: {subject}")
    print(f"   Body: {body}")
    print()
    
    result = sender.send_email(to_email, subject, body)
    print(f"Result: {result}")
    
    if "✅" in result:
        print("\n🎉 Email sent successfully!")
        print("📧 Check your email to see if the body appears correctly")
    else:
        print(f"\n❌ Email failed: {result}")

if __name__ == "__main__":
    test_email_body() 