#!/usr/bin/env python3
"""
Direct email body debug test
"""

import os
import sys

# Add the MCP server path
sys.path.append("/Users/ola/Desktop/working-mcp-server/count-r-server")

def test_email_body_direct():
    """Test email body directly with Gmail sender"""
    
    print("🔍 Direct Email Body Debug Test")
    print("=" * 50)
    
    try:
        from gmail_email_sender import GmailEmailSender
        
        # Create email sender
        email_sender = GmailEmailSender()
        email_sender.config_file = "/Users/ola/Desktop/working-mcp-server/count-r-server/gmail_config.json"
        
        # Test email data
        to_email = "mywork461@gmail.com"
        subject = "DIRECT TEST: Email Body Debug"
        body = """=== DIRECT EMAIL BODY TEST ===

This is a direct test email sent from the Gmail sender.

The body should contain:
- Line 1: This text
- Line 2: This text too
- Line 3: And this line

If you can see this body, the issue is in the MCP bridge.
If you cannot see this body, the issue is in the Gmail sender.

Best regards,
Direct Test Script

=== END TEST ==="""
        
        print(f"📧 Sending direct email:")
        print(f"   To: {to_email}")
        print(f"   Subject: {subject}")
        print(f"   Body length: {len(body)} characters")
        print(f"   Body preview: {body[:100]}...")
        
        # Change to the config directory
        original_cwd = os.getcwd()
        os.chdir("/Users/ola/Desktop/working-mcp-server/count-r-server")
        
        try:
            result = email_sender.send_email(to_email, subject, body)
            print(f"📧 Result: {result}")
        finally:
            os.chdir(original_cwd)
            
        if result.startswith("✅"):
            print("✅ Direct email sent successfully")
            print("📋 Check your Gmail inbox for 'DIRECT TEST: Email Body Debug'")
            print("📋 If this email has a body, the issue is in the MCP bridge")
            print("📋 If this email has no body, the issue is in the Gmail sender")
        else:
            print(f"❌ Direct email failed: {result}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_email_body_direct() 