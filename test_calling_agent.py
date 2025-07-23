#!/usr/bin/env python3
"""
Test script for MCP Calling Agent
Tests the calling agent with your standalone MCP server
"""

import asyncio
import json
from mcp_calling_agent import MCPCallingAgent

async def test_calling_agent():
    """Test the calling agent with your standalone MCP server"""
    print("🧪 Testing MCP Calling Agent")
    print("=" * 60)
    
    # You can change this URL to point to your standalone MCP server
    # that has the call_phone tools
    standalone_server_url = "http://127.0.0.1:5000"  # Change this to your server URL
    
    print(f"🔗 Testing with MCP server: {standalone_server_url}")
    
    # Create calling agent
    agent = MCPCallingAgent(standalone_server_url)
    
    try:
        # Test 1: Connect to server
        print("\n1️⃣ Testing server connection...")
        if await agent.connect_to_server():
            print("✅ Successfully connected to MCP server")
        else:
            print("❌ Failed to connect to MCP server")
            return
        
        # Test 2: List calling tools
        print("\n2️⃣ Testing calling tools discovery...")
        calling_info = await agent.list_calling_tools()
        print(f"Total tools found: {calling_info['total_tools']}")
        print(f"Calling tools found: {len(calling_info['calling_tools'])}")
        
        if calling_info['calling_tools']:
            print("📞 Available calling tools:")
            for tool in calling_info['calling_tools']:
                print(f"   - {tool['name']}: {tool['description']}")
        else:
            print("⚠️ No calling tools found on this server")
            print("Available tools:")
            for tool in agent.available_tools:
                print(f"   - {tool['name']}: {tool['description']}")
        
        # Test 3: Test calling capabilities
        print("\n3️⃣ Testing calling capabilities...")
        test_results = await agent.test_calling_capabilities()
        print(f"Server Connected: {'✅' if test_results['server_connected'] else '❌'}")
        print(f"Calling Tools Found: {'✅' if test_results['calling_tools_found'] else '❌'}")
        
        if test_results['calling_tools_found']:
            print(f"Available calling tools: {', '.join(test_results['available_calling_tools'])}")
            
            # Test 4: Test making a call (without actually calling)
            print("\n4️⃣ Testing call initiation (dry run)...")
            print("This will test the calling interface without making actual calls")
            
            # Test with a dummy number
            test_number = "+1234567890"
            print(f"Testing call to: {test_number}")
            
            result = await agent.make_call(test_number, "Test Caller")
            
            if result.success:
                print(f"✅ Call test successful!")
                print(f"   Call ID: {result.call_id}")
                print(f"   Status: {result.status}")
            else:
                print(f"❌ Call test failed: {result.error_message}")
                print("   This is expected if the MCP server doesn't have calling tools yet")
        else:
            print("⚠️ No calling tools available - this is expected if your standalone server")
            print("   doesn't have call_phone tools implemented yet")
        
        # Test 5: Test tool calling interface
        print("\n5️⃣ Testing generic tool calling...")
        if agent.available_tools:
            # Test with the first available tool
            first_tool = agent.available_tools[0]
            tool_name = first_tool['name']
            print(f"Testing generic call to: {tool_name}")
            
            # Prepare test parameters based on tool name
            if tool_name == "count_r":
                params = {"word": "test"}
            elif tool_name == "get_desktop_path":
                params = {"random_string": "test"}
            elif tool_name == "list_desktop_contents":
                params = {"random_string": "test"}
            else:
                params = {}
            
            result = await agent.call_tool(tool_name, params)
            
            if result.get("success"):
                print(f"✅ Generic tool call successful!")
                print(f"   Result: {result.get('result', 'No result')}")
            else:
                print(f"❌ Generic tool call failed: {result.get('error')}")
        
        print("\n🎉 Calling agent test completed!")
        
        # Summary
        print("\n📊 SUMMARY:")
        print(f"   Server URL: {standalone_server_url}")
        print(f"   Server Connected: {'✅' if test_results['server_connected'] else '❌'}")
        print(f"   Total Tools: {calling_info['total_tools']}")
        print(f"   Calling Tools: {len(calling_info['calling_tools'])}")
        
        if calling_info['calling_tools']:
            print("   📞 Ready for calling operations!")
        else:
            print("   ⚠️ No calling tools found - need to implement call_phone in MCP server")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
    finally:
        await agent.close()

async def test_with_custom_server():
    """Test with a custom server URL"""
    print("\n🔧 Custom Server Test")
    print("=" * 40)
    
    # You can specify your standalone MCP server URL here
    custom_url = input("Enter your standalone MCP server URL (or press Enter to skip): ").strip()
    
    if not custom_url:
        print("Skipping custom server test")
        return
    
    print(f"Testing with custom server: {custom_url}")
    
    agent = MCPCallingAgent(custom_url)
    
    try:
        if await agent.connect_to_server():
            print("✅ Connected to custom server!")
            
            calling_info = await agent.list_calling_tools()
            print(f"Found {len(calling_info['calling_tools'])} calling tools")
            
            for tool in calling_info['calling_tools']:
                print(f"   - {tool['name']}: {tool['description']}")
        else:
            print("❌ Failed to connect to custom server")
            
    except Exception as e:
        print(f"❌ Custom server test failed: {e}")
    finally:
        await agent.close()

if __name__ == "__main__":
    asyncio.run(test_calling_agent())
    
    # Uncomment the line below to test with a custom server URL
    # asyncio.run(test_with_custom_server()) 