#!/usr/bin/env python3
"""
Test Real Google Voice Calling
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent.real_google_voice_calling import real_google_voice_caller

def test_real_call():
    """Test real calling functionality."""
    print("🧠 Testing Real Google Voice Calling")
    print("=" * 50)
    
    phone_number = "4782313954"
    print(f"📞 Testing real call to: {phone_number}")
    print("-" * 50)
    
    # Test the real calling
    result = real_google_voice_caller.make_real_call(phone_number, "Test Caller")
    
    print(f"✅ Success: {result['success']}")
    print(f"📱 Phone Number: {result['phone_number']}")
    print(f"📞 Method: {result['method']}")
    print(f"💬 Message: {result['message']}")
    print(f"📝 Note: {result['note']}")
    
    if result.get('instructions'):
        print(f"\n📋 Instructions:")
        for i, instruction in enumerate(result['instructions'], 1):
            print(f"   {i}. {instruction}")
    
    print("\n" + "=" * 50)
    print("🎉 Real call test completed!")

if __name__ == "__main__":
    test_real_call() 