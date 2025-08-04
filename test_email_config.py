#!/usr/bin/env python3
"""
Test Email Configuration
Tests your existing email settings with the alert system.
"""

import os
import asyncio
import sys
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from alert_system import AlertSystem

async def test_email_config():
    """Test your email configuration."""
    print("📧 Testing Email Configuration")
    print("=" * 50)
    
    # Check environment variables
    print("1. Checking environment variables...")
    
    google_email = os.getenv('GOOGLE_EMAIL')
    google_password = os.getenv('GOOGLE_PASSWORD')
    alert_email = os.getenv('ALERT_EMAIL')
    
    print(f"   GOOGLE_EMAIL: {google_email}")
    print(f"   GOOGLE_PASSWORD: {'***' if google_password else 'Not set'}")
    print(f"   ALERT_EMAIL: {alert_email}")
    
    if not google_email or google_email == 'your-email@gmail.com':
        print("   ❌ GOOGLE_EMAIL not properly configured")
        return False
    
    if not google_password or google_password == 'your-app-password':
        print("   ❌ GOOGLE_PASSWORD not properly configured")
        return False
    
    print("   ✅ Email credentials found")
    
    # Test alert system
    print("\n2. Testing alert system...")
    try:
        alert_system = AlertSystem()
        print("   ✅ Alert system initialized")
        
        # Test MCP connection
        connected = await alert_system.mcp_client.connect()
        if connected:
            print("   ✅ MCP server connected")
        else:
            print("   ⚠️  MCP server not connected")
        
        # Test email alert
        print("\n3. Sending test email alert...")
        await alert_system.trigger_alert(
            "pr_creation_success",
            "Test email alert from your configured email settings",
            {
                "test_type": "email_config_test",
                "timestamp": datetime.now().isoformat(),
                "message": "This is a test to verify your email configuration is working correctly"
            }
        )
        print("   ✅ Test email alert sent")
        
        # Check storage
        recent_alerts = alert_system.storage.get_recent_alerts("pr_creation_success", 5)
        print(f"   ✅ {len(recent_alerts)} recent alerts found in storage")
        
        print("\n🎉 Email configuration test completed!")
        print("Check your email for the test alert.")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        return False

async def test_mcp_email_directly():
    """Test MCP email tool directly."""
    print("\n4. Testing MCP email tool directly...")
    
    try:
        import httpx
        
        # Test the MCP sendmail_simple tool
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://127.0.0.1:5000/call",
                json={
                    "tool": "sendmail_simple",
                    "arguments": {
                        "to_email": os.getenv('GOOGLE_EMAIL', 'test@example.com'),
                        "subject": "Direct MCP Email Test",
                        "message": "This is a direct test of the MCP email tool using your credentials."
                    }
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ MCP email tool response: {result.get('result', 'Success')}")
                if result.get('note'):
                    print(f"   📝 Note: {result['note']}")
                return True
            else:
                print(f"   ❌ MCP email tool failed: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"   ❌ MCP email test failed: {e}")
        return False

async def main():
    """Main test function."""
    print("🚀 Starting Email Configuration Tests")
    print("=" * 60)
    
    # Test 1: Email configuration
    config_ok = await test_email_config()
    
    # Test 2: MCP email tool
    mcp_ok = await test_mcp_email_directly()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    if config_ok and mcp_ok:
        print("🎉 All email tests passed!")
        print("Your email configuration is working correctly.")
        print("\nNext steps:")
        print("1. Check your email for test messages")
        print("2. Run the full alert system test: python test_alert_system.py")
        print("3. Start using the alert system in production")
    else:
        print("❌ Some tests failed.")
        print("\nTroubleshooting:")
        print("1. Ensure GOOGLE_EMAIL and GOOGLE_PASSWORD are set correctly")
        print("2. Make sure your Gmail app password is valid")
        print("3. Check that MCP server is running on port 5000")
        print("4. Verify your Gmail account has 2FA enabled")

if __name__ == "__main__":
    asyncio.run(main()) 