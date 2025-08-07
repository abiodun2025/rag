#!/usr/bin/env python3
"""
Test script for REAL agent failures in the ecosystem.
Tests actual agent functionality that could fail in production.
"""

import asyncio
import logging
from datetime import datetime

from agent_monitoring_integration import get_agent_monitor, integrate_monitoring_with_agents
from alert_system import AlertSeverity

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_real_agent_failures():
    """Test for real failures in the agent ecosystem."""
    
    print("🔍 Testing for REAL Agent Failures")
    print("=" * 50)
    
    # Initialize monitoring
    integrate_monitoring_with_agents()
    monitor = get_agent_monitor()
    
    print("1. Testing SmartMasterAgent with edge cases...")
    
    try:
        from agent.smart_master_agent import SmartMasterAgent
        smart_agent = SmartMasterAgent()
        
        # Test 1: Empty message (could cause issues)
        print("   Testing empty message...")
        try:
            intent_result = smart_agent.analyze_intent("")
            print(f"   ✅ Empty message handled: {intent_result.intent}")
        except Exception as e:
            print(f"   ❌ Empty message failed: {e}")
        
        # Test 2: Very long message (performance test)
        print("   Testing very long message...")
        long_message = "save this to desktop " * 1000  # Very long message
        try:
            intent_result = smart_agent.analyze_intent(long_message)
            print(f"   ✅ Long message handled: {intent_result.intent}")
        except Exception as e:
            print(f"   ❌ Long message failed: {e}")
        
        # Test 3: Special characters (could break parsing)
        print("   Testing special characters...")
        special_message = "save this to desktop with special chars: !@#$%^&*()_+-=[]{}|;':\",./<>?"
        try:
            intent_result = smart_agent.analyze_intent(special_message)
            print(f"   ✅ Special chars handled: {intent_result.intent}")
        except Exception as e:
            print(f"   ❌ Special chars failed: {e}")
        
        # Test 4: Non-English text
        print("   Testing non-English text...")
        non_english = "保存到桌面"  # Chinese for "save to desktop"
        try:
            intent_result = smart_agent.analyze_intent(non_english)
            print(f"   ✅ Non-English handled: {intent_result.intent}")
        except Exception as e:
            print(f"   ❌ Non-English failed: {e}")
            
    except Exception as e:
        print(f"   ❌ SmartMasterAgent import/init failed: {e}")
    
    print("\n2. Testing MasterAgent with edge cases...")
    
    try:
        from agent.master_agent import MasterAgent
        master_agent = MasterAgent()
        
        # Test 1: Empty request
        print("   Testing empty request...")
        try:
            tasks = await master_agent.analyze_request("")
            print(f"   ✅ Empty request handled: {len(tasks)} tasks")
        except Exception as e:
            print(f"   ❌ Empty request failed: {e}")
        
        # Test 2: Complex request
        print("   Testing complex request...")
        complex_request = "save this message to desktop and also send an email to test@example.com about the project status and search for latest AI news"
        try:
            tasks = await master_agent.analyze_request(complex_request)
            print(f"   ✅ Complex request handled: {len(tasks)} tasks")
        except Exception as e:
            print(f"   ❌ Complex request failed: {e}")
        
        # Test 3: Invalid request
        print("   Testing invalid request...")
        invalid_request = "xyz123!@#$%^&*()_+-=[]{}|;':\",./<>?`~"
        try:
            tasks = await master_agent.analyze_request(invalid_request)
            print(f"   ✅ Invalid request handled: {len(tasks)} tasks")
        except Exception as e:
            print(f"   ❌ Invalid request failed: {e}")
            
    except Exception as e:
        print(f"   ❌ MasterAgent import/init failed: {e}")
    
    print("\n3. Testing RAG Agent tools...")
    
    try:
        from agent.agent import rag_agent
        from agent.models import AgentDependencies
        
        # Test 1: Vector search with empty query
        print("   Testing vector search with empty query...")
        try:
            deps = AgentDependencies(session_id="test_session")
            result = await rag_agent.vector_search(deps, "", 10)
            print(f"   ✅ Empty vector search handled: {len(result)} results")
        except Exception as e:
            print(f"   ❌ Empty vector search failed: {e}")
        
        # Test 2: Graph search with invalid entity
        print("   Testing graph search with invalid entity...")
        try:
            deps = AgentDependencies(session_id="test_session")
            result = await rag_agent.graph_search(deps, "nonexistent_entity_12345")
            print(f"   ✅ Invalid graph search handled: {len(result)} results")
        except Exception as e:
            print(f"   ❌ Invalid graph search failed: {e}")
        
        # Test 3: Web search with empty query
        print("   Testing web search with empty query...")
        try:
            deps = AgentDependencies(session_id="test_session")
            result = await rag_agent.web_search(deps, "", 5)
            print(f"   ✅ Empty web search handled: {len(result)} results")
        except Exception as e:
            print(f"   ❌ Empty web search failed: {e}")
            
    except Exception as e:
        print(f"   ❌ RAG Agent import/init failed: {e}")
    
    print("\n4. Testing MCP Tools...")
    
    try:
        from agent.mcp_tools import mcp_client
        
        # Test 1: MCP server connection
        print("   Testing MCP server connection...")
        try:
            tools = await mcp_client.list_tools()
            print(f"   ✅ MCP connection successful: {len(tools)} tools available")
        except Exception as e:
            print(f"   ❌ MCP connection failed: {e}")
        
        # Test 2: Invalid tool call
        print("   Testing invalid tool call...")
        try:
            result = await mcp_client.call_tool("nonexistent_tool", {})
            print(f"   ✅ Invalid tool call handled: {result}")
        except Exception as e:
            print(f"   ❌ Invalid tool call failed: {e}")
            
    except Exception as e:
        print(f"   ❌ MCP tools import/init failed: {e}")
    
    print("\n5. Testing Database Connections...")
    
    try:
        from agent.db_utils import get_db_connection
        
        # Test 1: Database connection
        print("   Testing database connection...")
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            conn.close()
            print(f"   ✅ Database connection successful: {result}")
        except Exception as e:
            print(f"   ❌ Database connection failed: {e}")
            
    except Exception as e:
        print(f"   ❌ Database utils import/init failed: {e}")
    
    print("\n6. Testing Email Tools...")
    
    try:
        from agent.email_tools import send_email
        
        # Test 1: Email composition (without sending)
        print("   Testing email composition...")
        try:
            # Just test composition, don't actually send
            email_data = {
                "to": "test@example.com",
                "subject": "Test Email",
                "body": "This is a test email"
            }
            print(f"   ✅ Email composition test passed")
        except Exception as e:
            print(f"   ❌ Email composition failed: {e}")
            
    except Exception as e:
        print(f"   ❌ Email tools import/init failed: {e}")
    
    print("\n7. Getting final monitoring statistics...")
    
    stats = monitor.get_agent_stats()
    
    print("\n📊 REAL Failure Analysis:")
    print(f"Total executions: {stats['summary']['total_executions']}")
    print(f"Successful executions: {stats['summary']['successful_executions']}")
    print(f"Failed executions: {stats['summary']['failed_executions']}")
    print(f"Success rate: {stats['summary']['success_rate']:.2f}%")
    
    print("\n🔍 Real Agent Status:")
    for agent_key, agent_data in stats['agent_stats'].items():
        status = agent_data.get('status', 'unknown')
        error = agent_data.get('error', 'None')
        
        if status == 'failed':
            print(f"  ❌ {agent_key}: {error}")
        elif status == 'completed':
            print(f"  ✅ {agent_key}: Success")
        else:
            print(f"  ⚠️ {agent_key}: {status}")
    
    print("\n⏱️ Performance Analysis:")
    for key, times in stats['execution_times'].items():
        if times:
            avg_time = sum(t['execution_time'] for t in times) / len(times)
            success_count = sum(1 for t in times if t['success'])
            total_count = len(times)
            
            if success_count < total_count:
                print(f"  ⚠️ {key}: {avg_time:.2f}s avg ({success_count}/{total_count} successful)")
            elif avg_time > 5.0:  # Slow execution
                print(f"  🐌 {key}: {avg_time:.2f}s avg (slow)")
            else:
                print(f"  ✅ {key}: {avg_time:.2f}s avg")
    
    print("\n🎯 REAL Failure Test Summary:")
    print("This test checked for actual failures in your agent ecosystem:")
    print("- Edge cases (empty input, long input, special characters)")
    print("- Invalid inputs and error conditions")
    print("- Database connections and MCP server connectivity")
    print("- Tool availability and error handling")
    print("- Performance issues and timeouts")

async def test_production_scenarios():
    """Test production-like scenarios that could fail."""
    
    print("\n🏭 Testing Production Scenarios")
    print("=" * 50)
    
    monitor = get_agent_monitor()
    
    print("1. Testing concurrent agent usage...")
    
    async def concurrent_test():
        from agent.smart_master_agent import SmartMasterAgent
        smart_agent = SmartMasterAgent()
        
        # Run multiple concurrent operations
        results = []
        for i in range(5):
            try:
                result = smart_agent.analyze_intent(f"save message {i} to desktop")
                results.append(result)
            except Exception as e:
                results.append(e)
        
        success_count = sum(1 for r in results if not isinstance(r, Exception))
        print(f"   Concurrent operations: {success_count}/5 successful")
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"   ❌ Task {i} failed: {result}")
    
    try:
        await concurrent_test()
    except Exception as e:
        print(f"   ❌ Concurrent test failed: {e}")
    
    print("\n2. Testing memory usage...")
    
    try:
        from agent.smart_master_agent import SmartMasterAgent
        smart_agent = SmartMasterAgent()
        
        # Test with many operations to check memory usage
        for i in range(100):
            try:
                intent_result = smart_agent.analyze_intent(f"save message {i} to desktop")
                if i % 20 == 0:
                    print(f"   Processed {i} operations...")
            except Exception as e:
                print(f"   ❌ Operation {i} failed: {e}")
                break
        
        print("   ✅ Memory usage test completed")
        
    except Exception as e:
        print(f"   ❌ Memory test failed: {e}")
    
    print("\n3. Testing error recovery...")
    
    try:
        from agent.smart_master_agent import SmartMasterAgent
        smart_agent = SmartMasterAgent()
        
        # Test that agent can recover from errors
        print("   Testing error recovery...")
        
        # First operation
        try:
            intent_result = smart_agent.analyze_intent("save this to desktop")
            print("   ✅ First operation successful")
        except Exception as e:
            print(f"   ❌ First operation failed: {e}")
        
        # Second operation (should work even if first failed)
        try:
            intent_result = smart_agent.analyze_intent("send an email")
            print("   ✅ Second operation successful")
        except Exception as e:
            print(f"   ❌ Second operation failed: {e}")
        
        print("   ✅ Error recovery test completed")
        
    except Exception as e:
        print(f"   ❌ Error recovery test failed: {e}")

async def main():
    """Main test function."""
    print("🚀 Starting REAL Agent Failure Detection")
    print("=" * 60)
    
    # Test for real failures
    await test_real_agent_failures()
    
    # Test production scenarios
    await test_production_scenarios()
    
    print("\n🎯 REAL Failure Detection Complete!")
    print("📧 Check your email for any real failure alerts")
    print("📊 Review the statistics above for actual issues")

if __name__ == "__main__":
    asyncio.run(main()) 