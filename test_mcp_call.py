#!/usr/bin/env python3
"""
Test MCP Call to see which method is being used
"""

import requests
import json

def test_mcp_call():
    """Test MCP call to see which method is being used."""
    url = "http://127.0.0.1:5000/call"
    
    data = {
        "tool": "call_phone",
        "arguments": {
            "phone_number": "4782313954",
            "caller_name": "Debug Test",
            "service": "google_voice"
        }
    }
    
    print("🧠 Testing MCP Call Method")
    print("=" * 50)
    print(f"📞 Calling: {data['arguments']['phone_number']}")
    print(f"🔧 Service: {data['arguments']['service']}")
    print("-" * 50)
    
    try:
        response = requests.post(url, json=data, timeout=10)
        result = response.json()
        
        print(f"✅ Success: {result.get('success')}")
        print(f"📞 Result: {result.get('result')}")
        print(f"📱 Phone: {result.get('phone_number')}")
        print(f"🆔 Call ID: {result.get('call_id')}")
        print(f"📊 Status: {result.get('status')}")
        print(f"📝 Note: {result.get('note')}")
        print(f"🔧 Service: {result.get('service')}")
        print(f"📋 Method: {result.get('method')}")
        
        if result.get('instructions'):
            print(f"\n📋 Instructions:")
            for i, instruction in enumerate(result['instructions'], 1):
                print(f"   {i}. {instruction}")
        
        print("\n" + "=" * 50)
        print("🎉 MCP call test completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_mcp_call() 