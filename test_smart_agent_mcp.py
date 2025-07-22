#!/usr/bin/env python3
"""
Test script to test the smart agent's MCP tools integration.
"""

import asyncio
import json
from agent.smart_master_agent import smart_master_agent

async def test_smart_agent_mcp():
    """Test the smart agent's MCP tools integration."""
    
    print("🧪 Testing Smart Agent MCP Tools Integration")
    print("=" * 60)
    
    # Test cases
    test_cases = [
        {
            "message": "send email to mywork461@gmail.com",
            "description": "Email sending via MCP tools"
        },
        {
            "message": "count r letters in the word programming",
            "description": "Count R letters via MCP tools"
        },
        {
            "message": "list desktop files",
            "description": "List desktop files via MCP tools"
        },
        {
            "message": "get desktop path",
            "description": "Get desktop path via MCP tools"
        },
        {
            "message": "open gmail",
            "description": "Open Gmail via MCP tools"
        },
        {
            "message": "list available mcp tools",
            "description": "List available MCP tools"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}️⃣ Testing: {test_case['description']}")
        print(f"Message: '{test_case['message']}'")
        
        try:
            result = await smart_master_agent.process_message(
                message=test_case['message'],
                session_id="test-mcp-session",
                user_id="test_user"
            )
            
            print(f"Intent: {result['intent_analysis']['intent']} (confidence: {result['intent_analysis']['confidence']:.2f})")
            print(f"Action: {result['execution_result']['result'].get('action', 'unknown')}")
            print(f"Message: {result['execution_result']['message']}")
            
            if result['execution_result']['result'].get('error'):
                print(f"❌ Error: {result['execution_result']['result']['error']}")
            else:
                print(f"✅ Success: {result['execution_result']['result'].get('note', 'Operation completed')}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
        
        print("-" * 40)

if __name__ == "__main__":
    asyncio.run(test_smart_agent_mcp()) 