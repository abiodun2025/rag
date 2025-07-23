#!/usr/bin/env python3
"""
Test Google Voice Calling
"""

import asyncio
import sys
from agent.smart_master_agent import smart_master_agent

async def test_call(phone_number: str):
    """Test calling with the smart agent."""
    print("🧠 Smart Agent - Google Voice Calling Test")
    print("=" * 50)
    print(f"📞 Testing call to: {phone_number}")
    print("-" * 50)
    
    # Process the call request
    result = await smart_master_agent.process_message(f"call {phone_number}", "test_session", "test_user")
    
    # Display results
    print(f"🎯 Intent: {result['intent_analysis']['intent']}")
    print(f"📊 Confidence: {result['intent_analysis']['confidence']:.2f}")
    print(f"📱 Phone Number: {result['intent_analysis']['extracted_data'].get('phone_number')}")
    print(f"✅ Success: {result['execution_result']['success']}")
    print(f"📞 Method: {result['execution_result']['result'].get('method')}")
    print(f"💬 Message: {result['execution_result']['message']}")
    
    print("\n" + "=" * 50)
    print("🎉 Test completed! Check your browser for Google Voice.")

def main():
    """Main function."""
    if len(sys.argv) != 2:
        print("Usage: python test_google_voice_call.py <phone_number>")
        print("Example: python test_google_voice_call.py 4782313954")
        sys.exit(1)
    
    phone_number = sys.argv[1]
    
    # Run the test
    asyncio.run(test_call(phone_number))

if __name__ == "__main__":
    main() 