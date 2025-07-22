#!/usr/bin/env python3
"""
Email Setup and Test Script
===========================

This script helps you set up and test the email functionality.
"""

import os
import sys
import asyncio
import aiohttp
import json
from pathlib import Path

def check_gmail_setup():
    """Check if Gmail API is properly set up."""
    print("🔍 Checking Gmail API Setup...")
    
    # Check for credentials file
    credentials_file = "credentials.json"
    if not os.path.exists(credentials_file):
        print(f"❌ Missing {credentials_file}")
        print("\n📋 To set up Gmail API:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Create a new project or select existing one")
        print("3. Enable Gmail API")
        print("4. Create OAuth 2.0 credentials")
        print("5. Download credentials as 'credentials.json'")
        print("6. Place the file in this directory")
        return False
    
    print(f"✅ Found {credentials_file}")
    
    # Check for required packages
    try:
        import googleapiclient.discovery
        import google_auth_oauthlib.flow
        import google.auth.transport.requests
        print("✅ Gmail API packages installed")
    except ImportError as e:
        print(f"❌ Missing Gmail API packages: {e}")
        print("Run: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
        return False
    
    return True

def test_email_tools_directly():
    """Test email tools directly."""
    print("\n🧪 Testing Email Tools Directly...")
    
    try:
        from agent.tools import compose_email_tool, EmailComposeInput
        
        # Test the email tool function
        test_input = EmailComposeInput(
            to="test@example.com",
            subject="Test Email",
            body="This is a test email from the agent."
        )
        
        print("✅ EmailComposeInput model works")
        print(f"📧 Test input: {test_input}")
        
        # Try to call the compose function (will fail without proper credentials)
        print("ℹ️  Testing compose_email_tool...")
        result = asyncio.run(compose_email_tool(test_input))
        print(f"📤 Result: {result}")
        
    except Exception as e:
        print(f"❌ Error testing email tools: {e}")
        if "credentials.json" in str(e):
            print("💡 This is expected - you need to set up Gmail credentials first")

async def test_email_via_api():
    """Test email functionality via API."""
    print("\n🌐 Testing Email via API...")
    
    test_cases = [
        {
            "name": "Simple Email Request",
            "message": "Send an email to test@example.com with subject 'Test Email' and body 'This is a test email from the agent.'"
        },
        {
            "name": "Email with Context",
            "message": "Compose an email to john@company.com about AI project updates. Subject should be 'AI Project Update' and include information about our progress."
        }
    ]
    
    async with aiohttp.ClientSession() as session:
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📧 Test Case {i}: {test_case['name']}")
            print("-" * 50)
            
            payload = {
                "message": test_case["message"],
                "session_id": None,
                "user_id": "test_user",
                "search_type": "hybrid"
            }
            
            try:
                async with session.post(
                    "http://localhost:8058/chat/stream",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 200:
                        print(f"✅ Request sent successfully")
                        print(f"📝 Test message: {test_case['message']}")
                        print(f"🤖 Agent should respond with email composition")
                    else:
                        print(f"❌ Request failed with status {response.status}")
                        
            except Exception as e:
                print(f"❌ Connection error: {e}")

def test_cli_interaction():
    """Test CLI interaction for email."""
    print("\n💻 Testing CLI Interaction...")
    print("To test email via CLI:")
    print("1. Run: python3 cli.py")
    print("2. Try these commands:")
    print("   - 'Send an email to test@example.com with subject Test and body Hello'")
    print("   - 'Compose an email to john@company.com about AI updates'")
    print("   - 'Send an email to tech@startup.com with subject Meeting Request'")

def create_sample_credentials_template():
    """Create a sample credentials template."""
    template = {
        "installed": {
            "client_id": "your-client-id.apps.googleusercontent.com",
            "project_id": "your-project-id",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": "your-client-secret",
            "redirect_uris": ["http://localhost"]
        }
    }
    
    with open("credentials_template.json", "w") as f:
        json.dump(template, f, indent=2)
    
    print("📄 Created credentials_template.json")
    print("💡 Use this as a reference for the structure of your credentials.json")

def main():
    """Main test function."""
    print("🚀 Email Agent Test Suite")
    print("=" * 50)
    
    # Check Gmail setup
    gmail_ready = check_gmail_setup()
    
    if not gmail_ready:
        print("\n📋 Setup Instructions:")
        print("1. Install Gmail API packages:")
        print("   pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
        print("\n2. Set up Gmail API credentials:")
        print("   - Go to https://console.cloud.google.com/")
        print("   - Create a project and enable Gmail API")
        print("   - Create OAuth 2.0 credentials")
        print("   - Download as 'credentials.json'")
        print("   - Place in this directory")
        print("\n3. Run this script again after setup")
        
        # Create template
        create_sample_credentials_template()
        return
    
    # Test email tools
    test_email_tools_directly()
    
    # Test via API
    print("\n🌐 Testing via API...")
    try:
        asyncio.run(test_email_via_api())
    except Exception as e:
        print(f"❌ API test failed: {e}")
        print("💡 Make sure the API server is running: python3 -m uvicorn agent.api:app --host 0.0.0.0 --port 8058")
    
    # CLI instructions
    test_cli_interaction()
    
    print("\n" + "="*50)
    print("✅ Test Complete!")
    print("="*50)
    print("\n📝 Next Steps:")
    print("1. Set up Gmail credentials if not done")
    print("2. Start API server: python3 -m uvicorn agent.api:app --host 0.0.0.0 --port 8058")
    print("3. Test via CLI: python3 cli.py")
    print("4. Try email commands in the CLI")

if __name__ == "__main__":
    main() 