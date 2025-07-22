#!/usr/bin/env python3
"""
Test script to demonstrate MCP integration with the agentic RAG system.
This script shows how the MCP tools are integrated and can be called.
"""

import asyncio
import json
import httpx
from datetime import datetime
import uuid # Import uuid for generating valid UUIDs

# Test the MCP integration
async def test_mcp_integration():
    """Test the MCP integration with the agent."""
    
    print("🧪 Testing MCP Integration with Agentic RAG System")
    print("=" * 60)
    
    # Test 1: Count R letters
    print("\n1️⃣ Testing count_r_letters tool:")
    response = await call_agent("count r letters in the word programming")
    print(f"Response: {response}")
    
    # Test 2: List desktop files
    print("\n2️⃣ Testing list_desktop_files tool:")
    response = await call_agent("list desktop files")
    print(f"Response: {response}")
    
    # Test 3: Get desktop path
    print("\n3️⃣ Testing get_desktop_directory tool:")
    response = await call_agent("get desktop directory path")
    print(f"Response: {response}")
    
    # Test 4: List available MCP tools
    print("\n4️⃣ Testing list_available_mcp_tools:")
    response = await call_agent("list available MCP tools")
    print(f"Response: {response}")
    
    # Test 5: Generic MCP tool call
    print("\n5️⃣ Testing generic MCP tool call:")
    response = await call_agent("call MCP tool count_r with word 'hello'")
    print(f"Response: {response}")

async def call_agent(message: str) -> dict:
    """Call the agent with a message."""
    url = "http://localhost:8058/chat"
    payload = {
        "message": message,
        "session_id": str(uuid.uuid4()), # Generate a valid UUID
        "user_id": "test_user"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=30.0)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"HTTP {response.status_code}", "details": response.text}
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}

def print_integration_summary():
    """Print a summary of the MCP integration."""
    print("\n" + "=" * 60)
    print("📋 MCP Integration Summary")
    print("=" * 60)
    print("✅ MCP Tools Successfully Integrated:")
    print("   • count_r_letters - Count 'r' letters in words")
    print("   • list_desktop_files - List desktop contents")
    print("   • get_desktop_directory - Get desktop path")
    print("   • open_gmail_browser - Open Gmail in browser")
    print("   • open_gmail_compose_window - Open Gmail compose")
    print("   • call_mcp_tool - Generic MCP tool caller")
    print("   • list_available_mcp_tools - List all MCP tools")
    print("\n🔧 Configuration:")
    print("   • MCP Server URL: http://127.0.0.1:5000")
    print("   • Server Name: count-r-server")
    print("   • Protocol: FastMCP (HTTP-based)")
    print("\n📝 Usage:")
    print("   • Agent automatically detects when to use MCP tools")
    print("   • Tools are called via HTTP requests to your MCP server")
    print("   • Results are integrated into agent responses")
    print("\n⚠️  Note: MCP server must be running for tools to work")
    print("   Start your count-r server with: python server.py")

if __name__ == "__main__":
    print_integration_summary()
    
    # Run the tests
    asyncio.run(test_mcp_integration())
    
    print("\n🎉 MCP Integration Test Complete!")
    print("\nTo use the MCP tools:")
    print("1. Start your count-r MCP server: python server.py")
    print("2. Start the agentic RAG system: python -m agent.api")
    print("3. Use the CLI: python cli.py")
    print("4. Ask questions like:")
    print("   - 'count r letters in the word programming'")
    print("   - 'list desktop files'")
    print("   - 'get desktop path'")
    print("   - 'open Gmail'") 