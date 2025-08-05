#!/usr/bin/env python3
"""
Test script to demonstrate the GitHub PR issue
"""

import requests
import json

def test_mcp_bridge():
    """Test what tools are available on the MCP bridge."""
    print("🔍 Testing MCP Bridge...")
    
    try:
        # Test health endpoint
        response = requests.get("http://localhost:5000/health")
        print(f"Health check: {response.status_code}")
        if response.status_code == 200:
            print(f"Health response: {response.json()}")
        
        # Test tools endpoint
        response = requests.get("http://localhost:5000/tools")
        print(f"Tools check: {response.status_code}")
        if response.status_code == 200:
            tools = response.json()
            print("Available tools:")
            for tool in tools.get("tools", []):
                print(f"  - {tool['name']}: {tool['description']}")
        
        # Test create_pull_request (this will fail)
        print("\n🔍 Testing create_pull_request...")
        response = requests.post("http://localhost:5000/call", json={
            "tool": "create_pull_request",
            "arguments": {
                "title": "Test PR",
                "description": "Test description",
                "source_branch": "test-branch",
                "target_branch": "main"
            }
        })
        print(f"Create PR response: {response.status_code}")
        print(f"Response: {response.json()}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_mcp_bridge()