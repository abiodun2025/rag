#!/usr/bin/env python3
"""
Test script for MCP Performance Agent
"""

import asyncio
import sys
from mcp_performance_agent import MCPPerformanceAgent

async def test_performance_agent():
    """Test the performance agent"""
    print("🧪 Testing MCP Performance Agent")
    print("=" * 50)
    
    # Create agent
    agent = MCPPerformanceAgent()
    
    try:
        # Test server health
        print("1. Testing server health...")
        health_ok = await agent.check_server_health()
        if health_ok:
            print("✅ Server health check passed")
        else:
            print("❌ Server health check failed")
            return
        
        # Test getting tools
        print("\n2. Testing tool discovery...")
        tools = await agent.get_available_tools()
        if tools:
            print(f"✅ Found {len(tools)} tools")
            for tool in tools:
                print(f"   - {tool.get('name', 'unknown')}")
        else:
            print("❌ No tools found")
            return
        
        # Test single tool call
        print("\n3. Testing single tool call...")
        result = await agent.call_tool("count_r", {"word": "test"})
        if result.success:
            print(f"✅ Tool call successful: {result.response_time_ms:.2f}ms")
            print(f"   Response: {result.response_data}")
        else:
            print(f"❌ Tool call failed: {result.error_message}")
        
        # Test quick workflow
        print("\n4. Testing count_r workflow (3 iterations)...")
        results = await agent.test_count_r_workflow(3)
        successful = len([r for r in results if r.success])
        print(f"✅ Workflow test: {successful}/{len(results)} successful")
        
        # Test report generation
        print("\n5. Testing report generation...")
        report = agent.generate_performance_report(results, tools)
        if report:
            print("✅ Report generated successfully")
            print(f"   Total tests: {report['overall_stats']['total_tests']}")
            print(f"   Success rate: {report['overall_stats']['overall_success_rate']:.1f}%")
        else:
            print("❌ Report generation failed")
        
        print("\n🎉 All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
    finally:
        await agent.close()

if __name__ == "__main__":
    asyncio.run(test_performance_agent()) 