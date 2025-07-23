#!/usr/bin/env python3
"""
Real Call - Make REAL calls directly without MCP server
"""

import sys
import asyncio
from agent.smart_master_agent import smart_master_agent

async def make_real_call(phone_number: str):
    """Make a REAL call using the smart agent."""
    print("🧠 Smart Agent - REAL Call")
    print("=" * 50)
    print(f"📞 Making REAL call to: {phone_number}")
    print("-" * 50)
    
    # Process the call request
    result = await smart_master_agent.process_message(f"call {phone_number}", "real_call", "user")
    
    # Display results
    print(f"🎯 Intent: {result['intent_analysis']['intent']}")
    print(f"📊 Confidence: {result['intent_analysis']['confidence']:.2f}")
    print(f"📱 Phone Number: {result['intent_analysis']['extracted_data'].get('phone_number')}")
    print(f"✅ Success: {result['execution_result']['success']}")
    print(f"📞 Method: {result['execution_result']['result'].get('method')}")
    print(f"💬 Message: {result['execution_result']['message']}")
    
    # Show detailed result
    execution_result = result['execution_result']['result']
    if 'instructions' in execution_result and execution_result['instructions']:
        print(f"\n📋 Instructions:")
        for i, instruction in enumerate(execution_result['instructions'], 1):
            print(f"   {i}. {instruction}")
    
    print("\n" + "=" * 50)
    print("🎉 REAL call initiated!")
    print("📞 Check your system dialer - select Google Voice to make the call!")

def main():
    """Main function."""
    if len(sys.argv) != 2:
        print("📞 Real Call - Make REAL calls")
        print("Usage: python real_call.py <phone_number>")
        print("Example: python real_call.py 4782313954")
        print("\nThis will:")
        print("1. Open system dialer")
        print("2. Pre-fill the number")
        print("3. Let you select Google Voice")
        print("4. Make a REAL call!")
        sys.exit(1)
    
    phone_number = sys.argv[1]
    
    # Run the real call
    asyncio.run(make_real_call(phone_number))

if __name__ == "__main__":
    main() 