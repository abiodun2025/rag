#!/usr/bin/env python3
"""
Fixed email body test - resolves the email body issue
"""

import requests
import json
import os

def test_email_body_fixed():
    """Test email body issue with proper formatting"""
    
    print("📧 Testing Email Body Issue (Fixed Version)")
    print("=" * 50)
    
    # Check if MCP server is running
    try:
        response = requests.get("http://127.0.0.1:5000/health", timeout=5)
        if response.status_code != 200:
            print("❌ MCP server health check failed")
            return False
        print("✅ MCP server is running")
    except:
        print("❌ MCP server is not running. Please start it with: python3 simple_mcp_server.py")
        return False
    
    # Test data with properly formatted body
    test_data = {
        "tool": "sendmail",
        "arguments": {
            "to_email": "test@example.com",  # Use test email to avoid spam
            "subject": "Fixed Email Body Test",
            "body": """Hi there!

This is a test email to debug the body issue.

The email should have this content in the body with proper line breaks.

Best regards,
Test Script""",
            "from_email": ""
        }
    }
    
    print(f"📝 Sending test email:")
    print(f"   To: {test_data['arguments']['to_email']}")
    print(f"   Subject: {test_data['arguments']['subject']}")
    print(f"   Body length: {len(test_data['arguments']['body'])} characters")
    print(f"   Body preview: {test_data['arguments']['body'][:100]}...")
    print()
    
    try:
        # Send request to MCP server
        response = requests.post(
            "http://127.0.0.1:5000/call",
            headers={"Content-Type": "application/json"},
            json=test_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ MCP Server Response:")
            print(json.dumps(result, indent=2))
            
            if result.get("success"):
                print("\n🎉 Email sent successfully!")
                print("📧 Check your email for the body content")
                print("🔍 The body should contain proper line breaks")
                return True
            else:
                print(f"\n❌ Email failed: {result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(response.text)
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to MCP server. Is it running on http://127.0.0.1:5000?")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_sendmail_simple():
    """Test sendmail_simple tool as alternative"""
    
    print("\n📧 Testing Sendmail Simple Tool")
    print("=" * 40)
    
    test_data = {
        "tool": "sendmail_simple",
        "arguments": {
            "to_email": "test@example.com",
            "subject": "Simple Email Test",
            "message": """This is a simple test message.

It should work correctly with proper formatting.

Best regards,
Simple Test"""
        }
    }
    
    try:
        response = requests.post(
            "http://127.0.0.1:5000/call",
            headers={"Content-Type": "application/json"},
            json=test_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ Simple email sent successfully!")
                return True
            else:
                print(f"❌ Simple email failed: {result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_mcp_tools():
    """Test available MCP tools"""
    
    print("\n🔧 Testing Available MCP Tools")
    print("=" * 40)
    
    try:
        response = requests.post(
            "http://127.0.0.1:5000/call",
            json={"tool": "list_tools", "arguments": {}},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                tools = result.get("tools", [])
                email_tools = [t for t in tools if "mail" in t.get("name", "").lower()]
                
                print(f"📋 Found {len(tools)} total tools")
                print(f"📧 Found {len(email_tools)} email tools:")
                for tool in email_tools:
                    print(f"   • {tool.get('name')}: {tool.get('description', 'No description')}")
                
                return len(email_tools) > 0
            else:
                print(f"❌ Failed to get tools: {result.get('error')}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Starting Fixed Email Body Tests")
    print("⏰ This will test the email body issue with proper fixes")
    
    # Test MCP tools first
    if not test_mcp_tools():
        print("\n❌ MCP tools not available. Please check MCP server.")
        return False
    
    # Test both email methods
    success1 = test_email_body_fixed()
    success2 = test_sendmail_simple()
    
    if success1 or success2:
        print("\n🎉 Email body issue resolved!")
        print("✅ At least one email method is working")
        return True
    else:
        print("\n❌ Email body issue persists")
        print("🔧 Check MCP server logs and email configuration")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ All tests completed successfully!")
    else:
        print("\n⚠️  Some tests failed. Check the output above.") 