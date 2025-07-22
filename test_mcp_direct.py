#!/usr/bin/env python3
"""
Direct test of MCP server tools without going through the agent.
"""

import asyncio
import httpx
import json

async def test_mcp_server_direct():
    """Test MCP server directly."""
    
    print("🧪 Testing MCP Server Directly")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:5000"
    
    # Test 1: Health check
    print("\n1️⃣ Testing health endpoint:")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/health", timeout=5.0)
            print(f"Health check: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Health check failed: {e}")
    
    # Test 2: Tools endpoint
    print("\n2️⃣ Testing tools endpoint:")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/tools", timeout=5.0)
            print(f"Tools endpoint: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Tools endpoint failed: {e}")
    
    # Test 3: Count R tool
    print("\n3️⃣ Testing count_r tool:")
    try:
        async with httpx.AsyncClient() as client:
            payload = {"tool": "count_r", "arguments": {"word": "programming"}}
            response = await client.post(f"{base_url}/call", json=payload, timeout=5.0)
            print(f"Count R tool: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Count R tool failed: {e}")
    
    # Test 4: List desktop contents
    print("\n4️⃣ Testing list_desktop_contents tool:")
    try:
        async with httpx.AsyncClient() as client:
            payload = {"tool": "list_desktop_contents", "arguments": {}}
            response = await client.post(f"{base_url}/call", json=payload, timeout=5.0)
            print(f"List desktop: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"List desktop failed: {e}")
    
    # Test 5: Get desktop path
    print("\n5️⃣ Testing get_desktop_path tool:")
    try:
        async with httpx.AsyncClient() as client:
            payload = {"tool": "get_desktop_path", "arguments": {}}
            response = await client.post(f"{base_url}/call", json=payload, timeout=5.0)
            print(f"Get desktop path: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Get desktop path failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_mcp_server_direct()) 