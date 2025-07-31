#!/usr/bin/env python3
"""
Gmail SMTP Setup Script
=======================

This script helps you set up Gmail SMTP credentials for email delivery.
"""

import os
import getpass
import subprocess
import sys

def setup_gmail_credentials():
    """Interactive setup for Gmail SMTP credentials."""
    
    print("📧 Gmail SMTP Setup")
    print("=" * 50)
    print("This will help you set up Gmail SMTP for email delivery.")
    print()
    
    # Check if credentials are already set
    current_user = os.getenv('GMAIL_USER')
    current_password = os.getenv('GMAIL_APP_PASSWORD')
    
    if current_user and current_password:
        print(f"✅ Gmail credentials already configured:")
        print(f"   User: {current_user}")
        print(f"   Password: {'*' * len(current_password)}")
        print()
        
        response = input("Do you want to update these credentials? (y/N): ").strip().lower()
        if response != 'y':
            print("Keeping existing credentials.")
            return True
    
    print("📋 Prerequisites:")
    print("1. Enable 2-Factor Authentication on your Gmail account")
    print("   → Go to: https://myaccount.google.com/security")
    print("   → Enable '2-Step Verification'")
    print()
    print("2. Generate an App Password")
    print("   → Go to: https://myaccount.google.com/apppasswords")
    print("   → Select 'Mail' and your device")
    print("   → Copy the 16-character app password")
    print()
    
    input("Press Enter when you have completed the prerequisites...")
    print()
    
    # Get Gmail credentials
    print("🔐 Enter your Gmail credentials:")
    gmail_user = input("Gmail address: ").strip()
    
    if not gmail_user or '@gmail.com' not in gmail_user:
        print("❌ Please enter a valid Gmail address")
        return False
    
    gmail_password = getpass.getpass("App Password (16 characters): ").strip()
    
    if not gmail_password or len(gmail_password.replace(' ', '')) != 16:
        print("❌ App password should be 16 characters (spaces are OK)")
        return False
    
    # Test the credentials
    print("\n🧪 Testing Gmail SMTP connection...")
    if test_gmail_smtp(gmail_user, gmail_password):
        print("✅ Gmail SMTP test successful!")
        
        # Save to environment
        save_credentials(gmail_user, gmail_password)
        
        print("\n🎉 Gmail SMTP setup complete!")
        print("📧 Your smart agent can now send emails to external addresses.")
        return True
    else:
        print("❌ Gmail SMTP test failed!")
        print("🔧 Please check your credentials and try again.")
        return False

def test_gmail_smtp(gmail_user: str, gmail_password: str) -> bool:
    """Test Gmail SMTP connection."""
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        # Create test message
        msg = MIMEMultipart()
        msg['From'] = gmail_user
        msg['To'] = gmail_user  # Send to yourself for testing
        msg['Subject'] = "Gmail SMTP Test"
        
        test_body = "This is a test email to verify Gmail SMTP setup."
        msg.attach(MIMEText(test_body, 'plain'))
        
        # Connect to Gmail SMTP
        print("   Connecting to smtp.gmail.com:587...")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        
        print("   Authenticating...")
        server.login(gmail_user, gmail_password)
        
        print("   Sending test email...")
        text = msg.as_string()
        server.sendmail(gmail_user, gmail_user, text)
        server.quit()
        
        print("   ✅ Test email sent successfully!")
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def save_credentials(gmail_user: str, gmail_password: str):
    """Save credentials to environment and shell profile."""
    
    # Set environment variables for current session
    os.environ['GMAIL_USER'] = gmail_user
    os.environ['GMAIL_APP_PASSWORD'] = gmail_password
    
    # Create a shell script to set environment variables
    shell_script = f"""#!/bin/bash
# Gmail SMTP Configuration
export GMAIL_USER="{gmail_user}"
export GMAIL_APP_PASSWORD="{gmail_password}"
echo "✅ Gmail SMTP credentials loaded"
"""
    
    # Write to a file
    with open('gmail_smtp_config.sh', 'w') as f:
        f.write(shell_script)
    
    # Make it executable
    os.chmod('gmail_smtp_config.sh', 0o755)
    
    print("\n📁 Credentials saved to 'gmail_smtp_config.sh'")
    print("💡 To load credentials in future sessions, run:")
    print("   source gmail_smtp_config.sh")

def test_email_delivery():
    """Test email delivery with configured credentials."""
    
    gmail_user = os.getenv('GMAIL_USER')
    gmail_password = os.getenv('GMAIL_APP_PASSWORD')
    
    if not gmail_user or not gmail_password:
        print("❌ Gmail credentials not configured!")
        print("💡 Run this script first to set up credentials.")
        return False
    
    print("📧 Testing Email Delivery")
    print("=" * 30)
    
    test_email = input("Enter test email address: ").strip()
    if not test_email:
        test_email = gmail_user  # Send to yourself if no email provided
    
    subject = "Smart Agent Email Test"
    message = f"""Hello!

This is a test email from your Smart Agent system.

If you receive this email, the Gmail SMTP setup is working correctly!

Best regards,
Smart Agent System
"""
    
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        msg = MIMEMultipart()
        msg['From'] = gmail_user
        msg['To'] = test_email
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'plain'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(gmail_user, gmail_password)
        
        text = msg.as_string()
        server.sendmail(gmail_user, test_email, text)
        server.quit()
        
        print(f"✅ Test email sent successfully to {test_email}")
        print("📧 Check your inbox!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send test email: {e}")
        return False

def main():
    """Main function."""
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        test_email_delivery()
    else:
        setup_gmail_credentials()

if __name__ == "__main__":
    main() 