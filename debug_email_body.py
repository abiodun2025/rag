#!/usr/bin/env python3
"""
Debug email body issue
"""

import sys
import os
sys.path.append("/Users/ola/Desktop/working-mcp-server/count-r-server")

from gmail_email_sender import GmailEmailSender
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json

def debug_email_body():
    """Debug email body issue"""
    
    print("🔍 Debugging Email Body Issue")
    print("=" * 50)
    
    sender = GmailEmailSender()
    
    # Test email with very clear body
    to_email = "mywork461@gmail.com"
    subject = "DEBUG: Email Body Test"
    body = """=== EMAIL BODY TEST ===

This is a test email to debug the body issue.

Line 1: This should be visible
Line 2: This should also be visible  
Line 3: And this line too

The email body should contain all this text.

Best regards,
Debug Script

=== END TEST ===
"""
    
    print(f"📝 Test email details:")
    print(f"   To: {to_email}")
    print(f"   Subject: {subject}")
    print(f"   Body length: {len(body)} characters")
    print(f"   Body content:")
    print("   " + "-" * 40)
    print(body)
    print("   " + "-" * 40)
    print()
    
    # Test 1: Use the GmailEmailSender directly
    print("🧪 Test 1: Using GmailEmailSender directly")
    result1 = sender.send_email(to_email, subject, body)
    print(f"Result: {result1}")
    print()
    
    # Test 2: Create email manually to see what's being sent
    print("🧪 Test 2: Manual email creation")
    try:
        config = sender.load_config()
        if config:
            # Create message manually
            msg = MIMEMultipart()
            msg['From'] = config["email"]
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add body with explicit encoding
            text_part = MIMEText(body, 'plain', 'utf-8')
            msg.attach(text_part)
            
            print(f"Email object created:")
            print(f"   From: {msg['From']}")
            print(f"   To: {msg['To']}")
            print(f"   Subject: {msg['Subject']}")
            print(f"   Body part: {text_part}")
            print(f"   Body content: {text_part.get_payload()}")
            print()
            
            # Don't actually send this one, just show the structure
            print("✅ Email structure looks correct")
        else:
            print("❌ No config found")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n📧 Check your email at mywork461@gmail.com")
    print("🔍 Look for the email with subject 'DEBUG: Email Body Test'")
    print("📝 The body should contain the test message above")

if __name__ == "__main__":
    debug_email_body() 