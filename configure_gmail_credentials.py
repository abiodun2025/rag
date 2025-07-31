#!/usr/bin/env python3
"""
Configure Gmail SMTP credentials with provided information
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def configure_gmail_credentials():
    """Configure Gmail SMTP credentials."""
    
    # Your provided credentials
    gmail_user = "olaoluwagureje1@gmail.com"
    gmail_password = "tcvv cmxg itdw babp"
    
    print("📧 Configuring Gmail SMTP Credentials")
    print("=" * 50)
    print(f"Email: {gmail_user}")
    print(f"App Password: {'*' * len(gmail_password.replace(' ', ''))}")
    print()
    
    # Test the credentials
    print("🧪 Testing Gmail SMTP connection...")
    if test_gmail_smtp(gmail_user, gmail_password):
        print("✅ Gmail SMTP test successful!")
        
        # Save credentials
        save_credentials(gmail_user, gmail_password)
        
        print("\n🎉 Gmail SMTP configuration complete!")
        print("📧 Your smart agent can now send emails to external addresses.")
        return True
    else:
        print("❌ Gmail SMTP test failed!")
        print("🔧 Please check your credentials and try again.")
        return False

def test_gmail_smtp(gmail_user: str, gmail_password: str) -> bool:
    """Test Gmail SMTP connection."""
    try:
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
    """Test email delivery to olaoluwa@multiplatformservices.com"""
    
    gmail_user = "olaoluwagureje1@gmail.com"
    gmail_password = "tcvv cmxg itdw babp"
    
    print("📧 Testing Email Delivery to olaoluwa@multiplatformservices.com")
    print("=" * 60)
    
    test_email = "olaoluwa@multiplatformservices.com"
    subject = "Smart Agent Email Test"
    message = f"""Hello!

This is a test email from your Smart Agent system.

If you receive this email, the Gmail SMTP setup is working correctly!

Best regards,
Smart Agent System
"""
    
    try:
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
        print("📧 Check your inbox at olaoluwa@multiplatformservices.com!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send test email: {e}")
        return False

if __name__ == "__main__":
    # Configure credentials
    if configure_gmail_credentials():
        print("\n" + "="*50)
        print("🧪 Now testing email delivery...")
        print("="*50)
        test_email_delivery() 