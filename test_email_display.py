#!/usr/bin/env python3
"""
Comprehensive email body display test
"""

import requests
import json
import time

def test_email_display():
    """Test email body display comprehensively"""
    
    print("🔍 Comprehensive Email Body Display Test")
    print("=" * 60)
    
    # Test 1: Simple email with clear body
    print("📧 Test 1: Simple email with clear body")
    test_data_1 = {
        "tool": "sendmail",
        "arguments": {
            "to_email": "mywork461@gmail.com",
            "subject": "TEST 1: Simple Body Test",
            "body": "This is a simple test email.\n\nThe body should be visible.\n\nCan you see this text?",
            "from_email": ""
        }
    }
    
    print(f"   Sending: {test_data_1['arguments']['body']}")
    
    try:
        response = requests.post(
            "http://127.0.0.1:5000/call",
            headers={"Content-Type": "application/json"},
            json=test_data_1,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("   ✅ Email 1 sent successfully")
            else:
                print(f"   ❌ Email 1 failed: {result.get('error')}")
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print()
    time.sleep(2)
    
    # Test 2: Email with HTML-like formatting
    print("📧 Test 2: Email with formatted body")
    test_data_2 = {
        "tool": "sendmail",
        "arguments": {
            "to_email": "mywork461@gmail.com",
            "subject": "TEST 2: Formatted Body Test",
            "body": """=== EMAIL BODY TEST ===

This is a formatted test email.

* Line 1: This should be visible
* Line 2: This should also be visible  
* Line 3: And this line too

The email body should contain all this text.

Best regards,
Test Script

=== END TEST ===""",
            "from_email": ""
        }
    }
    
    print(f"   Sending: {test_data_2['arguments']['body']}")
    
    try:
        response = requests.post(
            "http://127.0.0.1:5000/call",
            headers={"Content-Type": "application/json"},
            json=test_data_2,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("   ✅ Email 2 sent successfully")
            else:
                print(f"   ❌ Email 2 failed: {result.get('error')}")
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print()
    time.sleep(2)
    
    # Test 3: Email with special characters
    print("📧 Test 3: Email with special characters")
    test_data_3 = {
        "tool": "sendmail",
        "arguments": {
            "to_email": "mywork461@gmail.com",
            "subject": "TEST 3: Special Characters Test",
            "body": "Hello! 👋\n\nThis email contains special characters:\n\n• Bullet point 1\n• Bullet point 2\n• Bullet point 3\n\nEmojis: 😊 🎉 📧\n\nNumbers: 123 456 789\n\nSymbols: @#$%^&*()\n\nCan you see all of this?",
            "from_email": ""
        }
    }
    
    print(f"   Sending: {test_data_3['arguments']['body']}")
    
    try:
        response = requests.post(
            "http://127.0.0.1:5000/call",
            headers={"Content-Type": "application/json"},
            json=test_data_3,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("   ✅ Email 3 sent successfully")
            else:
                print(f"   ❌ Email 3 failed: {result.get('error')}")
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print()
    print("📋 Instructions:")
    print("1. Check your Gmail inbox for emails with subjects:")
    print("   - 'TEST 1: Simple Body Test'")
    print("   - 'TEST 2: Formatted Body Test'")
    print("   - 'TEST 3: Special Characters Test'")
    print("2. Open each email (don't just look at preview)")
    print("3. Tell me which emails show the body content")
    print("4. If any show empty body, let me know which ones")

if __name__ == "__main__":
    test_email_display() 