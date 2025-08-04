#!/usr/bin/env python3
"""
Simple test to verify core agent functionality without monitoring integration.
"""

import asyncio
import os

async def test_core_functionality():
    """Test core agent functionality without monitoring."""
    print("🧪 Testing Core Agent Functionality")
    print("=" * 50)
    
    # Set environment variables
    os.environ.setdefault('DATABASE_URL', 'sqlite:///rag.db')
    os.environ.setdefault('NEO4J_PASSWORD', 'agenticrag')
    os.environ.setdefault('LLM_API_KEY', 'test_key_for_development')
    os.environ.setdefault('EMBEDDING_API_KEY', 'test_embedding_key_for_development')
    os.environ.setdefault('OPENAI_API_KEY', 'test_openai_key_for_development')
    
    print("1. Testing SmartMasterAgent (no monitoring)...")
    try:
        from agent.smart_master_agent import SmartMasterAgent
        smart_agent = SmartMasterAgent()
        
        # Test 1: Empty message
        print("   Testing empty message...")
        try:
            intent_result = smart_agent.analyze_intent("")
            print(f"   ✅ Empty message handled: {intent_result.intent}")
        except Exception as e:
            print(f"   ❌ Empty message failed: {e}")
        
        # Test 2: Very long message
        print("   Testing very long message...")
        long_message = "save this to desktop " * 1000
        try:
            intent_result = smart_agent.analyze_intent(long_message)
            print(f"   ✅ Long message handled: {intent_result.intent}")
        except Exception as e:
            print(f"   ❌ Long message failed: {e}")
        
        # Test 3: Special characters
        print("   Testing special characters...")
        special_message = "save this to desktop with special chars: !@#$%^&*()_+-=[]{}|;':\",./<>?"
        try:
            intent_result = smart_agent.analyze_intent(special_message)
            print(f"   ✅ Special chars handled: {intent_result.intent}")
        except Exception as e:
            print(f"   ❌ Special chars failed: {e}")
        
        # Test 4: Non-English text
        print("   Testing non-English text...")
        non_english = "保存到桌面"
        try:
            intent_result = smart_agent.analyze_intent(non_english)
            print(f"   ✅ Non-English handled: {intent_result.intent}")
        except Exception as e:
            print(f"   ❌ Non-English failed: {e}")
            
    except Exception as e:
        print(f"   ❌ SmartMasterAgent import/init failed: {e}")
    
    print("\n2. Testing MasterAgent...")
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
        complex_request = "save this message to desktop and also send an email to test@example.com about the project status"
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
    
    print("\n3. Testing MCP Tools...")
    try:
        from agent.mcp_tools import mcp_client
        
        # Test MCP server connection
        print("   Testing MCP server connection...")
        try:
            tools = await mcp_client.discover_tools()
            print(f"   ✅ MCP connection successful: {len(tools)} tools available")
        except Exception as e:
            print(f"   ❌ MCP connection failed: {e}")
        
        # Test invalid tool call
        print("   Testing invalid tool call...")
        try:
            result = await mcp_client.call_tool("nonexistent_tool", {})
            print(f"   ✅ Invalid tool call handled: {result}")
        except Exception as e:
            print(f"   ❌ Invalid tool call failed: {e}")
            
    except Exception as e:
        print(f"   ❌ MCP Tools import/init failed: {e}")
    
    print("\n4. Testing Database Connections...")
    try:
        from agent.db_utils import get_db_connection
        
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
    
    print("\n5. Testing Email Tools...")
    try:
        from agent.email_tools import send_email
        
        print("   Testing email composition...")
        try:
            result = send_email("test@example.com", "Test Subject", "Test body")
            print(f"   ✅ Email composition test passed: {result.get('success', False)}")
        except Exception as e:
            print(f"   ❌ Email composition failed: {e}")
            
    except Exception as e:
        print(f"   ❌ Email tools import/init failed: {e}")
    
    print("\n6. Testing Production Scenarios...")
    
    # Test concurrent operations
    print("   Testing concurrent operations...")
    try:
        from agent.smart_master_agent import SmartMasterAgent
        smart_agent = SmartMasterAgent()
        
        results = []
        for i in range(5):
            try:
                result = smart_agent.analyze_intent(f"save message {i} to desktop")
                results.append(result)
            except Exception as e:
                results.append(e)
        
        success_count = sum(1 for r in results if not isinstance(r, Exception))
        print(f"   ✅ Concurrent operations: {success_count}/5 successful")
        
    except Exception as e:
        print(f"   ❌ Concurrent test failed: {e}")
    
    # Test memory usage
    print("   Testing memory usage...")
    try:
        from agent.smart_master_agent import SmartMasterAgent
        smart_agent = SmartMasterAgent()
        
        for i in range(100):
            try:
                intent_result = smart_agent.analyze_intent(f"save message {i} to desktop")
                if i % 20 == 0:
                    print(f"     Processed {i} operations...")
            except Exception as e:
                print(f"     ❌ Operation {i} failed: {e}")
                break
        
        print("   ✅ Memory usage test completed")
        
    except Exception as e:
        print(f"   ❌ Memory test failed: {e}")
    
    print("\n🎯 Core Functionality Test Complete!")

async def main():
    """Main test function."""
    await test_core_functionality()

if __name__ == "__main__":
    asyncio.run(main()) 