#!/usr/bin/env python3
"""
Debug MCP Bridge Email Processing
"""

import requests
import json

def debug_mcp_bridge_email():
    """Debug email processing in MCP bridge"""
    
    print("🔍 MCP Bridge Email Processing Debug")
    print("=" * 50)
    
    # Test email data
    test_data = {
        "tool": "sendmail",
        "arguments": {
            "to_email": "mywork461@gmail.com",
            "subject": "MCP BRIDGE DEBUG: Email Body Test",
            "body": """=== MCP BRIDGE EMAIL BODY TEST ===

This is a test email sent through the MCP bridge.

The body should contain:
- Line 1: This text
- Line 2: This text too  
- Line 3: And this line

If you can see this body, the MCP bridge is working.
If you cannot see this body, there's an issue in the bridge.

Best regards,
MCP Bridge Test Script

=== END TEST ===""",
            "from_email": ""
        }
    }
    
    print(f"📧 Sending via MCP bridge:")
    print(f"   To: {test_data['arguments']['to_email']}")
    print(f"   Subject: {test_data['arguments']['subject']}")
    print(f"   Body length: {len(test_data['arguments']['body'])} characters")
    print(f"   Body preview: {test_data['arguments']['body'][:100]}...")
    
    try:
        response = requests.post(
            "http://127.0.0.1:5000/call",
            headers={"Content-Type": "application/json"},
            json=test_data,
            timeout=30
        )
        
        print(f"📧 HTTP Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"📧 Response: {json.dumps(result, indent=2)}")
            
            if result.get("success"):
                print("✅ MCP bridge email sent successfully")
                print("📋 Check your Gmail inbox for 'MCP BRIDGE DEBUG: Email Body Test'")
                print("📋 Compare this with the direct test email")
            else:
                print(f"❌ MCP bridge email failed: {result.get('error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"📧 Response text: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_mcp_bridge_email() 