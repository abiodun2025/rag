#!/usr/bin/env python3
"""
Test script for Agent Monitoring Integration.
Demonstrates how monitoring works with existing agents.
"""

import asyncio
import logging
from datetime import datetime

from agent_monitoring_integration import (
    get_agent_monitor, 
    integrate_monitoring_with_agents,
    monitor_agent,
    monitor_tool
)
from alert_system import AlertSeverity

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_agent_monitoring():
    """Test the agent monitoring integration."""
    
    print("🎯 Testing Agent Monitoring Integration")
    print("=" * 50)
    
    # Initialize monitoring
    print("1. Initializing monitoring system...")
    integrate_monitoring_with_agents()
    
    # Get monitor instance
    monitor = get_agent_monitor()
    
    print("2. Testing decorator-based monitoring...")
    
    # Test agent monitoring decorator
    @monitor_agent("test_agent", AlertSeverity.HIGH)
    async def test_agent_function():
        """Test function that simulates agent behavior."""
        await asyncio.sleep(1)  # Simulate work
        return {"status": "success", "data": "test result"}
    
    # Test tool monitoring decorator
    @monitor_tool("test_tool", AlertSeverity.MEDIUM)
    async def test_tool_function():
        """Test function that simulates tool behavior."""
        await asyncio.sleep(0.5)  # Simulate work
        return {"status": "success", "data": "tool result"}
    
    # Test error monitoring
    @monitor_agent("error_test_agent", AlertSeverity.CRITICAL)
    async def test_error_function():
        """Test function that raises an error."""
        await asyncio.sleep(0.1)
        raise Exception("Test error for monitoring")
    
    # Test performance monitoring
    @monitor_agent("slow_agent", AlertSeverity.MEDIUM)
    async def test_slow_function():
        """Test function that takes a long time."""
        await asyncio.sleep(35)  # Over 30 second threshold
        return {"status": "success", "data": "slow result"}
    
    print("3. Running test functions...")
    
    # Test successful execution
    try:
        result = await test_agent_function()
        print(f"✅ Agent function result: {result}")
    except Exception as e:
        print(f"❌ Agent function failed: {e}")
    
    # Test tool execution
    try:
        result = await test_tool_function()
        print(f"✅ Tool function result: {result}")
    except Exception as e:
        print(f"❌ Tool function failed: {e}")
    
    # Test error handling
    try:
        result = await test_error_function()
        print(f"✅ Error function result: {result}")
    except Exception as e:
        print(f"❌ Error function failed (expected): {e}")
    
    # Test performance monitoring (this will trigger an alert)
    print("4. Testing performance monitoring (this will take 35 seconds)...")
    try:
        result = await test_slow_function()
        print(f"✅ Slow function result: {result}")
    except Exception as e:
        print(f"❌ Slow function failed: {e}")
    
    print("5. Getting monitoring statistics...")
    stats = monitor.get_agent_stats()
    
    print("\n📊 Monitoring Statistics:")
    print(f"Total executions: {stats['summary']['total_executions']}")
    print(f"Successful executions: {stats['summary']['successful_executions']}")
    print(f"Failed executions: {stats['summary']['failed_executions']}")
    print(f"Success rate: {stats['summary']['success_rate']:.2f}%")
    print(f"Average execution time: {stats['summary']['average_execution_time']:.2f}s")
    
    print("\n🔍 Agent Status:")
    for agent_key, agent_data in stats['agent_stats'].items():
        status = agent_data.get('status', 'unknown')
        start_time = agent_data.get('start_time', 'N/A')
        end_time = agent_data.get('end_time', 'N/A')
        error = agent_data.get('error', 'None')
        
        print(f"  {agent_key}: {status}")
        if error != 'None':
            print(f"    Error: {error}")
        if start_time != 'N/A':
            print(f"    Start: {start_time}")
        if end_time != 'N/A':
            print(f"    End: {end_time}")
    
    print("\n⏱️ Execution Times:")
    for key, times in stats['execution_times'].items():
        if times:
            avg_time = sum(t['execution_time'] for t in times) / len(times)
            success_count = sum(1 for t in times if t['success'])
            total_count = len(times)
            print(f"  {key}: {avg_time:.2f}s avg ({success_count}/{total_count} successful)")
    
    print("\n🎉 Agent monitoring test completed!")
    print("📧 Check your email for any alerts that were triggered")

async def test_existing_agent_integration():
    """Test integration with existing agents."""
    
    print("\n🔗 Testing Existing Agent Integration")
    print("=" * 50)
    
    try:
        # Import existing agents
        from agent.smart_master_agent import SmartMasterAgent
        from agent.master_agent import MasterAgent
        
        print("1. Creating agent instances...")
        
        # Create agent instances
        smart_agent = SmartMasterAgent()
        master_agent = MasterAgent()
        
        print("2. Testing SmartMasterAgent with monitoring...")
        
        # Test intent analysis
        try:
            intent_result = smart_agent.analyze_intent("save this to my desktop")
            print(f"✅ Intent analysis result: {intent_result.intent}")
        except Exception as e:
            print(f"❌ Intent analysis failed: {e}")
        
        print("3. Testing MasterAgent with monitoring...")
        
        # Test request analysis
        try:
            tasks = await master_agent.analyze_request("save this message")
            print(f"✅ Request analysis result: {len(tasks)} tasks")
        except Exception as e:
            print(f"❌ Request analysis failed: {e}")
        
        print("4. Getting final statistics...")
        monitor = get_agent_monitor()
        stats = monitor.get_agent_stats()
        
        print(f"Total agent executions: {stats['summary']['total_executions']}")
        print(f"Success rate: {stats['summary']['success_rate']:.2f}%")
        
        print("\n✅ Existing agent integration test completed!")
        
    except Exception as e:
        print(f"❌ Existing agent integration failed: {e}")

async def main():
    """Main test function."""
    print("🚀 Starting Agent Monitoring Integration Tests")
    print("=" * 60)
    
    # Test basic monitoring
    await test_agent_monitoring()
    
    # Test existing agent integration
    await test_existing_agent_integration()
    
    print("\n🎯 All tests completed!")
    print("📧 Check your email for monitoring alerts")
    print("📊 Monitor your agents in real-time with the alert system")

if __name__ == "__main__":
    asyncio.run(main()) 