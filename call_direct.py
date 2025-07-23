#!/usr/bin/env python3
"""
Direct Call - Just input number and make direct call via MCP server
"""

import sys
import asyncio
from agent.smart_master_agent import smart_master_agent

async def call_direct(phone_number: str):
    """Make a direct call using MCP server."""
    result = await smart_master_agent.process_message(f"call {phone_number}", "direct_call", "user")
    print(result['execution_result']['message'])

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("📞 Direct Call via MCP Server")
        print("Usage: python call_direct.py <number>")
        print("Example: python call_direct.py 4782313954")
        print("\nMake sure MCP server is running: python simple_mcp_bridge.py")
        sys.exit(1)
    
    asyncio.run(call_direct(sys.argv[1])) 