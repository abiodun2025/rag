#!/usr/bin/env python3
"""
Debug Call - Test calling directly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from simple_mcp_bridge import SimpleMCPBridge

def debug_call():
    """Debug the calling functionality."""
    print("🧠 Debugging Call Functionality")
    print("=" * 50)
    
    # Create bridge instance
    bridge = SimpleMCPBridge()
    
    # Test the call
    arguments = {
        "phone_number": "4782313954",
        "caller_name": "Debug Test",
        "service": "google_voice"
    }
    
    print(f"📞 Testing call with arguments: {arguments}")
    print("-" * 50)
    
    try:
        result = bridge._make_phone_call(arguments)
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
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 50)
    print("🎉 Debug test completed!")

if __name__ == "__main__":
    debug_call() 