#!/usr/bin/env python3
"""
Proper email delivery solution using Gmail SMTP.
This will actually deliver emails to external domains like Gmail.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from datetime import datetime

def send_email_via_gmail(to_email: str, subject: str, message: str, from_email: str = None):
    """
    Send email via Gmail SMTP for reliable delivery.
    
    To use this:
    1. Enable 2-factor authentication on your Gmail account
    2. Generate an App Password: https://myaccount.google.com/apppasswords
    3. Set environment variables:
       export GMAIL_USER="your-email@gmail.com"
       export GMAIL_APP_PASSWORD="your-app-password"
    """
    
    # Get Gmail credentials from environment
    gmail_user = os.getenv('GMAIL_USER')
    gmail_password = os.getenv('GMAIL_APP_PASSWORD')
    
    if not gmail_user or not gmail_password:
        print("❌ Gmail credentials not configured!")
        print("📧 To configure Gmail SMTP:")
        print("1. Enable 2-factor authentication on your Gmail account")
        print("2. Generate an App Password: https://myaccount.google.com/apppasswords")
        print("3. Set environment variables:")
        print("   export GMAIL_USER='your-email@gmail.com'")
        print("   export GMAIL_APP_PASSWORD='your-app-password'")
        return False
    
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = gmail_user
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Add body to email
        msg.attach(MIMEText(message, 'plain'))
        
        # Connect to Gmail SMTP
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        
        # Login
        server.login(gmail_user, gmail_password)
        
        # Send email
        text = msg.as_string()
        server.sendmail(gmail_user, to_email, text)
        server.quit()
        
        print(f"✅ Email sent successfully to {to_email}")
        print(f"📧 From: {gmail_user}")
        print(f"📧 Subject: {subject}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False

def test_email_delivery():
    """Test email delivery to mywork461@gmail.com"""
    
    print("📧 Testing Email Delivery to mywork461@gmail.com")
    print("=" * 60)
    
    # Test email
    to_email = "mywork461@gmail.com"
    subject = "Meeting Tonight - Test Email"
    message = "We have a meeting tonight let me know if you coming thanks!"
    
    print(f"📝 Sending email:")
    print(f"   To: {to_email}")
    print(f"   Subject: {subject}")
    print(f"   Message: {message}")
    print()
    
    success = send_email_via_gmail(to_email, subject, message)
    
    if success:
        print("\n🎉 Email delivery test successful!")
        print("📧 Check your email at mywork461@gmail.com")
    else:
        print("\n❌ Email delivery test failed!")
        print("🔧 Please configure Gmail credentials as shown above")

if __name__ == "__main__":
    test_email_delivery() 