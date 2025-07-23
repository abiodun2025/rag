#!/usr/bin/env python3
"""
Test email body issue
"""

import requests
import json

def test_email_body():
    """Test email body issue"""
    
    print("📧 Testing Email Body Issue")
    print("=" * 40)
    
    # Test data with proper body
    test_data = {
        "tool": "sendmail",
        "arguments": {
            "to_email": "mywork461@gmail.com",
            "subject": "Test Email Body - Debug Issue",
            "body": "Hi there!\n\nThis is a test email to debug the body issue.\n\nThe email should have this content in the body.\n\nBest regards,\nTest Script",
            "from_email": ""
        }
    }
    
    print(f"📝 Sending test email:")
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
                print("\n🎉 Email sent successfully!")
                print("📧 Check your email at mywork461@gmail.com")
                print("🔍 Look for the email body content")
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
    test_email_body() 