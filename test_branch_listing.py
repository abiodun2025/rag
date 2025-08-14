#!/usr/bin/env python3
"""
Test script for branch listing functionality
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_branch_listing():
    """Test the branch listing functionality."""
    print("🔍 Testing Branch Listing Functionality")
    print("=" * 50)
    
    # Check if MCP bridge is running
    try:
        response = requests.get("http://127.0.0.1:5000/health", timeout=5)
        if response.status_code == 200:
            health = response.json()
            print(f"✅ MCP Bridge is running: {health}")
        else:
            print(f"❌ MCP Bridge health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ MCP Bridge not accessible: {e}")
        print("   Please start the MCP bridge server first:")
        print("   python3 github_mcp_bridge.py")
        return
    
    # Test branch listing
    print("\n📋 Testing branch listing...")
    try:
        response = requests.post(
            "http://127.0.0.1:5000/call",
            json={
                "tool": "list_branches",
                "arguments": {}
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Branch listing response: {json.dumps(result, indent=2)}")
            
            if result.get("success"):
                branches = result.get("branches", [])
                print(f"\n🎉 Successfully listed {len(branches)} branches!")
                
                for i, branch in enumerate(branches, 1):
                    protection = "🔒" if branch.get("protected") else "🔓"
                    print(f"   {i:2d}. {protection} {branch['name']}")
                    if branch.get("commit_message"):
                        msg = branch["commit_message"][:60] + "..." if len(branch["commit_message"]) > 60 else branch["commit_message"]
                        print(f"       📝 {msg}")
            else:
                print(f"❌ Branch listing failed: {result.get('error')}")
        else:
            print(f"❌ HTTP error: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing branch listing: {e}")
    
    # Test tools endpoint
    print("\n📋 Testing tools endpoint...")
    try:
        response = requests.get("http://127.0.0.1:5000/tools", timeout=5)
        if response.status_code == 200:
            tools = response.json()
            print(f"✅ Available tools: {json.dumps(tools, indent=2)}")
            
            tool_names = [tool["name"] for tool in tools.get("tools", [])]
            if "list_branches" in tool_names:
                print("✅ list_branches tool is available!")
            else:
                print("❌ list_branches tool is NOT available")
                print("   The MCP bridge server needs to be restarted to pick up the new tool")
        else:
            print(f"❌ Tools endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing tools endpoint: {e}")

if __name__ == "__main__":
    test_branch_listing() 