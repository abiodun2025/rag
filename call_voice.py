#!/usr/bin/env python3
"""
Simple Google Voice Call - Just input number and call
"""

import sys
import asyncio
from agent.smart_master_agent import smart_master_agent

async def call_number(phone_number: str):
    """Call a number using Google Voice."""
    result = await smart_master_agent.process_message(f"call {phone_number}", "quick_call", "user")
    print(result['execution_result']['message'])

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("📞 Google Voice Call")
        print("Usage: python call_voice.py <number>")
        print("Example: python call_voice.py 4782313954")
        sys.exit(1)
    
    asyncio.run(call_number(sys.argv[1])) 