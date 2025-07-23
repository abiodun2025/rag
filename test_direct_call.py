#!/usr/bin/env python3
"""
Test Direct Calling via MCP Server
"""

import asyncio
import sys
from agent.smart_master_agent import smart_master_agent

async def test_direct_call(phone_number: str):
    """Test direct calling with the smart agent."""
    print("🧠 Smart Agent - Direct Calling Test")
    print("=" * 50)
    print(f"📞 Testing direct call to: {phone_number}")
    print(f"🔧 Using MCP server at: http://127.0.0.1:5000")
    print("-" * 50)
    
    # Process the call request
    result = await smart_master_agent.process_message(f"call {phone_number}", "test_session", "test_user")
    
    # Display results
    print(f"🎯 Intent: {result['intent_analysis']['intent']}")
    print(f"📊 Confidence: {result['intent_analysis']['confidence']:.2f}")
    print(f"📱 Phone Number: {result['intent_analysis']['extracted_data'].get('phone_number')}")
    print(f"✅ Success: {result['execution_result']['success']}")
    print(f"📞 Method: {result['execution_result']['result'].get('method')}")
    print(f"🆔 Call ID: {result['execution_result']['result'].get('call_id', 'N/A')}")
    print(f"📊 Status: {result['execution_result']['result'].get('status', 'N/A')}")
    print(f"💬 Message: {result['execution_result']['message']}")
    
    # Show detailed result
    execution_result = result['execution_result']['result']
    if 'instructions' in execution_result and execution_result['instructions']:
        print(f"\n📋 Instructions:")
        for i, instruction in enumerate(execution_result['instructions'], 1):
            print(f"   {i}. {instruction}")
    
    print("\n" + "=" * 50)
    print("🎉 Direct call test completed!")
    print("📞 Check your MCP server logs for call details")

def main():
    """Main function."""
    if len(sys.argv) != 2:
        print("Usage: python test_direct_call.py <phone_number>")
        print("Example: python test_direct_call.py 4782313954")
        print("\nMake sure your MCP server is running:")
        print("python simple_mcp_bridge.py")
        sys.exit(1)
    
    phone_number = sys.argv[1]
    
    # Run the test
    asyncio.run(test_direct_call(phone_number))

if __name__ == "__main__":
    main() 