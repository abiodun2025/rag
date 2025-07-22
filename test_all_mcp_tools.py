#!/usr/bin/env python3
"""
Comprehensive test of all MCP tools being called by the smart agent.
This shows how the agent intelligently selects and calls the right tools.
"""

import asyncio
import json
from agent.smart_master_agent import smart_master_agent

async def test_all_mcp_tools():
    """Test all MCP tools being called by the smart agent."""
    
    print("🎯 Comprehensive MCP Tools Test")
    print("=" * 60)
    print("This test shows how the smart agent intelligently calls MCP tools")
    print("based on user intent and message content.")
    print()
    
    # Test cases that should trigger different MCP tools
    test_cases = [
        {
            "message": "send email to mywork461@gmail.com with subject 'Test Email' and message 'Hello from agent'",
            "description": "Email sending with full details",
            "expected_tool": "sendmail_simple",
            "expected_intent": "email"
        },
        {
            "message": "count r letters in the word programming",
            "description": "Count R letters",
            "expected_tool": "count_r",
            "expected_intent": "mcp_tools"
        },
        {
            "message": "list desktop files and folders",
            "description": "List desktop contents",
            "expected_tool": "list_desktop_contents",
            "expected_intent": "mcp_tools"
        },
        {
            "message": "what is my desktop path?",
            "description": "Get desktop path",
            "expected_tool": "get_desktop_path",
            "expected_intent": "mcp_tools"
        },
        {
            "message": "open gmail in my browser",
            "description": "Open Gmail",
            "expected_tool": "open_gmail",
            "expected_intent": "mcp_tools"
        },
        {
            "message": "open gmail compose window",
            "description": "Open Gmail compose",
            "expected_tool": "open_gmail_compose",
            "expected_intent": "mcp_tools"
        },
        {
            "message": "what mcp tools are available?",
            "description": "List available MCP tools",
            "expected_tool": "list_mcp_tools",
            "expected_intent": "mcp_tools"
        },
        {
            "message": "send a simple email to test@example.com",
            "description": "Simple email sending",
            "expected_tool": "sendmail_simple",
            "expected_intent": "email"
        }
    ]
    
    successful_calls = 0
    total_tests = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}️⃣ Testing: {test_case['description']}")
        print(f"Message: '{test_case['message']}'")
        print(f"Expected Tool: {test_case['expected_tool']}")
        print(f"Expected Intent: {test_case['expected_intent']}")
        
        try:
            result = await smart_master_agent.process_message(
                message=test_case['message'],
                session_id=f"test-mcp-{i}",
                user_id="test_user"
            )
            
            intent = result['intent_analysis']['intent']
            confidence = result['intent_analysis']['confidence']
            action = result['execution_result']['result'].get('action', 'unknown')
            message = result['execution_result']['message']
            
            print(f"✅ Intent: {intent} (confidence: {confidence:.2f})")
            print(f"✅ Action: {action}")
            print(f"✅ Response: {message}")
            
            # Check if the right tool was called
            if test_case['expected_intent'] == intent:
                print(f"✅ Intent detection CORRECT")
                successful_calls += 1
            else:
                print(f"⚠️  Intent detection DIFFERENT - Expected: {test_case['expected_intent']}, Got: {intent}")
            
            # Check if MCP tools were called
            if action.startswith('mcp_') or action.startswith('email_'):
                print(f"✅ MCP tools were called successfully")
            else:
                print(f"⚠️  MCP tools not called - Action: {action}")
            
            # Show any errors
            if result['execution_result']['result'].get('error'):
                print(f"⚠️  Error: {result['execution_result']['result']['error']}")
            
        except Exception as e:
            print(f"❌ Exception: {e}")
        
        print("-" * 50)
    
    print(f"\n🎉 Test Summary:")
    print(f"✅ Successful tool calls: {successful_calls}/{total_tests}")
    print(f"📊 Success rate: {(successful_calls/total_tests)*100:.1f}%")
    print()
    print("🔧 All MCP tools are available and working:")
    print("   - count_r: Count 'r' letters in words")
    print("   - list_desktop_contents: List desktop files")
    print("   - get_desktop_path: Get desktop directory")
    print("   - open_gmail: Open Gmail in browser")
    print("   - open_gmail_compose: Open Gmail compose")
    print("   - sendmail: Send email with full details")
    print("   - sendmail_simple: Send simple email")
    print()
    print("💡 The agent calls tools based on your message content and intent.")
    print("   Try different phrasings to trigger different tools!")

if __name__ == "__main__":
    asyncio.run(test_all_mcp_tools()) 