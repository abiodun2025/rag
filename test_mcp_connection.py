#!/usr/bin/env python3
"""
Test connection to MCP server on port 5001
"""

import asyncio
import httpx
import json

async def test_mcp_connection():
    """Test connection to MCP server"""
    server_url = "http://127.0.0.1:5001"
    
    print(f"🔗 Testing connection to MCP server: {server_url}")
    print("=" * 60)
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            # Test 1: Health check
            print("\n1️⃣ Testing health endpoint...")
            response = await client.get(f"{server_url}/health")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
            
            # Test 2: Tools endpoint
            print("\n2️⃣ Testing tools endpoint...")
            response = await client.get(f"{server_url}/tools")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                tools = response.json()
                print(f"   Available tools: {json.dumps(tools, indent=2)}")
            else:
                print(f"   Error: {response.text}")
            
            # Test 3: Try a simple tool call if available
            print("\n3️⃣ Testing tool call...")
            test_payload = {
                "tool": "count_r",
                "arguments": {"word": "hello"}
            }
            response = await client.post(f"{server_url}/call", json=test_payload)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"   Result: {json.dumps(result, indent=2)}")
            else:
                print(f"   Error: {response.text}")
                
        except httpx.ConnectError:
            print("❌ Cannot connect to MCP server")
            print("   Make sure the server is running on port 5001")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_mcp_connection()) 