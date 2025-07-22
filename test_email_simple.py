#!/usr/bin/env python3
"""
Simple Email Test Script
========================

This script tests the email functionality with proper error handling.
"""

import os
import asyncio
from agent.email_tools import compose_and_send_email
from agent.tools import compose_email_tool, EmailComposeInput

def test_email_tools():
    """Test email tools directly."""
    print("🧪 Testing Email Tools...")
    
    # Test 1: Check if credentials exist
    if not os.path.exists('credentials.json'):
        print("❌ credentials.json not found")
        print("📋 Please follow the Gmail API setup guide:")
        print("   1. Go to https://console.cloud.google.com/")
        print("   2. Create a project and enable Gmail API")
        print("   3. Create OAuth 2.0 credentials")
        print("   4. Download as credentials.json")
        print("   5. Place in this directory")
        return False
    
    print("✅ credentials.json found")
    
    # Test 2: Test email composition
    try:
        test_input = EmailComposeInput(
            to="test@example.com",
            subject="Test Email from Agent",
            body="This is a test email sent by the AI agent."
        )
        print("✅ EmailComposeInput model works")
        
        # Test 3: Try to send email
        print("📤 Attempting to send test email...")
        result = asyncio.run(compose_email_tool(test_input))
        print(f"📧 Result: {result}")
        
        if result.get("status") == "sent":
            print("✅ Email sent successfully!")
            return True
        else:
            print(f"❌ Email failed: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing email: {e}")
        return False

def test_agent_email():
    """Test email via agent."""
    print("\n🤖 Testing Email via Agent...")
    
    try:
        from agent.agent import rag_agent
        from agent.agent import AgentDependencies
        from pydantic_ai import RunContext
        
        # Create test context
        deps = AgentDependencies(
            session_id="test_session",
            user_id="test_user"
        )
        ctx = RunContext(deps=deps)
        
        # Test email composition
        result = asyncio.run(rag_agent.compose_email(
            ctx=ctx,
            to="test@example.com",
            subject="Agent Test Email",
            body="This email was sent by the AI agent."
        ))
        
        print(f"📧 Agent email result: {result}")
        return True
        
    except Exception as e:
        print(f"❌ Error testing agent email: {e}")
        return False

def main():
    """Main test function."""
    print("📧 Email Functionality Test")
    print("=" * 50)
    
    # Test email tools
    tools_ok = test_email_tools()
    
    if tools_ok:
        # Test agent email
        agent_ok = test_agent_email()
        
        if agent_ok:
            print("\n✅ All email tests passed!")
            print("🎉 Your agent can now send emails!")
        else:
            print("\n❌ Agent email test failed")
    else:
        print("\n❌ Email tools test failed")
        print("💡 Please set up Gmail API credentials first")
    
    print("\n" + "="*50)
    print("📝 Next Steps:")
    if not os.path.exists('credentials.json'):
        print("1. Set up Gmail API credentials (see GMAIL_SETUP_GUIDE.md)")
    else:
        print("1. Test via CLI: python3 cli.py")
        print("2. Try: 'Send an email to test@example.com with subject Test and body Hello'")
        print("3. Your agent should now send real emails!")

if __name__ == "__main__":
    main() 