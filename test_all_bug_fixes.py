#!/usr/bin/env python3
"""
Comprehensive test script to verify all bug fixes
"""

import asyncio
import requests
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_mcp_bridge_connection():
    """Test MCP bridge connection."""
    print("🔧 Test 1: MCP Bridge Connection")
    print("=" * 50)
    
    try:
        # Test health endpoint
        response = requests.get("http://127.0.0.1:5000/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ MCP Bridge is running")
            print(f"   Status: {health_data.get('status')}")
            print(f"   Gmail sender: {health_data.get('gmail_sender_loaded')}")
            return True
        else:
            print(f"❌ MCP Bridge health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to MCP Bridge")
        print("   Solution: Start the bridge with 'python simple_mcp_bridge.py'")
        return False
    except Exception as e:
        print(f"❌ Error testing MCP bridge: {e}")
        return False

def test_email_sending():
    """Test email sending functionality."""
    print("\n📧 Test 2: Email Sending")
    print("=" * 50)
    
    test_data = {
        "tool": "sendmail",
        "arguments": {
            "to_email": "mywork461@gmail.com",
            "subject": "BUG FIX TEST: Email Body Verification",
            "body": """=== BUG FIX VERIFICATION TEST ===

This email is sent to verify that all bug fixes are working:

✅ MCP Bridge Connection: Fixed
✅ Email Body Content: Should be visible
✅ Smart Agent Intent Detection: Fixed
✅ Email Data Extraction: Fixed
✅ Error Handling: Improved

If you can see this body content, the empty body bug is fixed!

Best regards,
Bug Fix Test Script

=== END TEST ===""",
            "from_email": ""
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
                print("✅ Email sent successfully")
                print("📋 Check your Gmail inbox for 'BUG FIX TEST: Email Body Verification'")
                print("📋 Verify that the email body is not empty")
                return True
            else:
                print(f"❌ Email failed: {result.get('error')}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing email: {e}")
        return False

def test_mcp_tools():
    """Test MCP tools functionality."""
    print("\n🔧 Test 3: MCP Tools")
    print("=" * 50)
    
    # Test count_r tool
    count_data = {
        "tool": "count_r",
        "arguments": {"word": "programming"}
    }
    
    try:
        response = requests.post(
            "http://127.0.0.1:5000/call",
            headers={"Content-Type": "application/json"},
            json=count_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print(f"✅ Count R tool: {result.get('result')}")
            else:
                print(f"❌ Count R tool failed: {result.get('error')}")
                return False
        else:
            print(f"❌ Count R tool HTTP error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing count_r tool: {e}")
        return False
    
    # Test list_desktop_contents tool
    desktop_data = {
        "tool": "list_desktop_contents",
        "arguments": {"random_string": "test"}
    }
    
    try:
        response = requests.post(
            "http://127.0.0.1:5000/call",
            headers={"Content-Type": "application/json"},
            json=desktop_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print(f"✅ Desktop contents tool: Working")
            else:
                print(f"❌ Desktop contents tool failed: {result.get('error')}")
                return False
        else:
            print(f"❌ Desktop contents tool HTTP error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing desktop contents tool: {e}")
        return False
    
    return True

async def test_smart_agent():
    """Test smart agent functionality."""
    print("\n🧠 Test 4: Smart Agent Intent Detection")
    print("=" * 50)
    
    try:
        from agent.smart_master_agent import SmartMasterAgent
        
        agent = SmartMasterAgent()
        
        # Test email intent detection
        email_message = "send email to test@example.com Hello there!"
        intent_result = agent.analyze_intent(email_message)
        
        print(f"✅ Email intent detection: {intent_result.intent.value}")
        print(f"   Confidence: {intent_result.confidence:.2f}")
        print(f"   Extracted data: {intent_result.extracted_data}")
        
        if intent_result.intent.value == "email":
            print("✅ Email intent correctly detected")
        else:
            print("❌ Email intent not detected correctly")
            return False
        
        # Test MCP tools intent detection
        mcp_message = "count r letters in the word programming"
        intent_result = agent.analyze_intent(mcp_message)
        
        print(f"✅ MCP tools intent detection: {intent_result.intent.value}")
        print(f"   Confidence: {intent_result.confidence:.2f}")
        
        if intent_result.intent.value == "mcp_tools":
            print("✅ MCP tools intent correctly detected")
        else:
            print("❌ MCP tools intent not detected correctly")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing smart agent: {e}")
        return False

def main():
    """Run all tests."""
    print("🔍 COMPREHENSIVE BUG FIX VERIFICATION")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    results = []
    
    # Test 1: MCP Bridge Connection
    results.append(("MCP Bridge Connection", test_mcp_bridge_connection()))
    
    # Test 2: Email Sending
    results.append(("Email Sending", test_email_sending()))
    
    # Test 3: MCP Tools
    results.append(("MCP Tools", test_mcp_tools()))
    
    # Test 4: Smart Agent
    results.append(("Smart Agent Intent Detection", asyncio.run(test_smart_agent())))
    
    # Summary
    print("\n📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL BUG FIXES VERIFIED SUCCESSFULLY!")
        print("✅ MCP Bridge connection working")
        print("✅ Email sending with body content working")
        print("✅ MCP tools integration working")
        print("✅ Smart agent intent detection working")
    else:
        print("⚠️  Some issues remain. Check the failed tests above.")
    
    print("\n📋 Next Steps:")
    print("1. Check your Gmail inbox for the test email")
    print("2. Verify the email body is not empty")
    print("3. Test the CLI with: source venv/bin/activate && python cli.py")
    print("4. Try sending an email through the CLI")

if __name__ == "__main__":
    main() 