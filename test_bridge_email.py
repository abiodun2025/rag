#!/usr/bin/env python3
"""
Test the MCP HTTP Bridge email functionality
"""

import requests
import json

def test_bridge_email():
    """Test email sending through the bridge"""
    
    print("📧 Testing MCP HTTP Bridge Email Functionality")
    print("=" * 60)
    
    # Test data
    test_data = {
        "tool": "sendmail",
        "arguments": {
            "to_email": "mywork461@gmail.com",
            "subject": "Meeting Tonight - Test from Bridge",
            "body": "We have a meeting tonight let me know if you coming thanks!",
            "from_email": ""
        }
    }
    
    print(f"📝 Sending email via bridge:")
    print(f"   To: {test_data['arguments']['to_email']}")
    print(f"   Subject: {test_data['arguments']['subject']}")
    print(f"   Body: {test_data['arguments']['body']}")
    print()
    
    try:
        # Send request to bridge
        response = requests.post(
            "http://127.0.0.1:5000/call",
            headers={"Content-Type": "application/json"},
            json=test_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Bridge Response:")
            print(json.dumps(result, indent=2))
            
            if result.get("success"):
                print("\n🎉 Email sent successfully via your SMTP configuration!")
                print("📧 Check your email at mywork461@gmail.com")
            else:
                print(f"\n❌ Email failed: {result.get('error', 'Unknown error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to bridge. Is it running on http://127.0.0.1:5000?")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_bridge_email() 