#!/usr/bin/env python3
"""
Test MCP Server
Check if the MCP server is working properly
"""

import asyncio
import sys
from agent.mcp_tools import sendmail_simple_tool, SendmailSimpleInput

async def test_mcp_connection():
    """Test MCP server connection."""
    print("🔗 Testing MCP Server Connection")
    print("=" * 40)
    
    try:
        # Create a test input
        test_input = SendmailSimpleInput(
            to_email="test@example.com",
            subject="MCP Server Test",
            message="This is a test email to check if the MCP server is working."
        )
        
        print("📧 Sending test email via MCP server...")
        result = await sendmail_simple_tool(test_input)
        
        if result.get("success"):
            print("✅ MCP server is working!")
            print(f"📊 Result: {result}")
            return True
        else:
            print(f"❌ MCP server error: {result}")
            return False
            
    except Exception as e:
        print(f"❌ MCP server connection failed: {e}")
        return False

async def test_mcp_tools_import():
    """Test if MCP tools can be imported."""
    print("📦 Testing MCP Tools Import")
    print("=" * 40)
    
    try:
        from agent.mcp_tools import sendmail_simple_tool, SendmailSimpleInput
        print("✅ MCP tools imported successfully")
        return True
    except Exception as e:
        print(f"❌ MCP tools import failed: {e}")
        return False

async def test_simple_email():
    """Test a simple email composition."""
    print("📧 Testing Simple Email")
    print("=" * 40)
    
    try:
        # Test with a simple email request
        from agent.dynamic_email_composer import analyze_and_compose_email
        
        test_command = "send email to test@example.com about MCP server test"
        print(f"💡 Testing: '{test_command}'")
        
        result = await analyze_and_compose_email(test_command)
        
        if result.get("status") == "success":
            print("✅ Email composition successful!")
            print(f"📧 To: {result.get('to_email')}")
            print(f"📝 Subject: {result.get('subject')}")
            return True
        else:
            print(f"❌ Email composition failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Email composition error: {e}")
        return False

async def run_mcp_tests():
    """Run all MCP-related tests."""
    print("🧪 MCP Server Tests")
    print("=" * 50)
    
    tests = [
        ("MCP Tools Import", test_mcp_tools_import),
        ("MCP Server Connection", test_mcp_connection),
        ("Simple Email", test_simple_email),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running: {test_name}")
        print("-" * 30)
        
        try:
            result = await test_func()
            results[test_name] = result
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status}: {test_name}")
        except Exception as e:
            results[test_name] = False
            print(f"❌ ERROR: {test_name} - {e}")
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! MCP server is working perfectly.")
    elif passed >= 2:
        print("⚠️  Some tests passed. MCP server has partial functionality.")
    else:
        print("⚠️  Most tests failed. MCP server may not be running.")
        print("💡 Make sure your MCP server is started and accessible.")
    
    return passed >= 2

async def main():
    """Main test function."""
    try:
        success = await run_mcp_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n👋 Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 