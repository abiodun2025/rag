#!/usr/bin/env python3
"""
Comprehensive email delivery testing to identify where failures occur.
Tests both MCP server and RAG agent email functionality.
"""

import asyncio
import json
import subprocess
import sys
import os
from datetime import datetime

def test_sendmail_system():
    """Test if sendmail is available and working on the system."""
    print("🔧 Testing System Sendmail...")
    print("=" * 50)
    
    try:
        # Check if sendmail exists
        result = subprocess.run(['which', 'sendmail'], capture_output=True, text=True)
        if result.returncode == 0:
            sendmail_path = result.stdout.strip()
            print(f"✅ Sendmail found at: {sendmail_path}")
        else:
            print("❌ Sendmail not found in system PATH")
            return False
        
        # Test sendmail with a simple email
        test_email = f"""From: test@localhost
To: test@example.com
Subject: System Sendmail Test

This is a test email from system sendmail.
Timestamp: {datetime.now()}
"""
        
        result = subprocess.run(
            ['sendmail', '-t'],
            input=test_email,
            text=True,
            capture_output=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print("✅ System sendmail working - email sent successfully")
            return True
        else:
            print(f"❌ System sendmail failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ System sendmail timed out")
        return False
    except Exception as e:
        print(f"❌ System sendmail error: {e}")
        return False

def test_mcp_server_email():
    """Test email sending through MCP server."""
    print("\n📧 Testing MCP Server Email...")
    print("=" * 50)
    
    try:
        import httpx
        
        # Test email via MCP server
        payload = {
            "tool": "sendmail_simple",
            "arguments": {
                "to_email": "test@example.com",
                "subject": "MCP Server Test",
                "message": f"This is a test email from MCP server. Time: {datetime.now()}"
            }
        }
        
        async def test_mcp_email():
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    "http://127.0.0.1:5000/call",
                    json=payload
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ MCP Server Response: {result}")
                    
                    if result.get("success"):
                        print("✅ MCP Server reports email sent successfully")
                        return True
                    else:
                        print(f"❌ MCP Server error: {result.get('error', 'Unknown error')}")
                        return False
                else:
                    print(f"❌ MCP Server HTTP error: {response.status_code}")
                    return False
        
        return asyncio.run(test_mcp_email())
        
    except Exception as e:
        print(f"❌ MCP Server test failed: {e}")
        return False

def test_rag_agent_email():
    """Test email sending through RAG agent."""
    print("\n🤖 Testing RAG Agent Email...")
    print("=" * 50)
    
    try:
        from agent.smart_master_agent import smart_master_agent
        
        async def test_agent_email():
            result = await smart_master_agent.process_message(
                message="send email to test@example.com with subject 'RAG Agent Test' and message 'Testing email from RAG agent'",
                session_id="email-test-session",
                user_id="test_user"
            )
            
            intent = result['intent_analysis']['intent']
            action = result['execution_result']['result'].get('action', 'unknown')
            message = result['execution_result']['message']
            
            print(f"✅ Intent: {intent}")
            print(f"✅ Action: {action}")
            print(f"✅ Response: {message}")
            
            if action == 'email_sent':
                print("✅ RAG Agent reports email sent successfully")
                return True
            elif action == 'email_error':
                error = result['execution_result']['result'].get('error', 'Unknown error')
                print(f"❌ RAG Agent email error: {error}")
                return False
            else:
                print(f"⚠️  Unexpected action: {action}")
                return False
        
        return asyncio.run(test_agent_email())
        
    except Exception as e:
        print(f"❌ RAG Agent test failed: {e}")
        return False

def main():
    """Run comprehensive email delivery tests."""
    print("🎯 Email Delivery Failure Analysis")
    print("=" * 60)
    print("This test will identify where email delivery failures occur.")
    print()
    
    # Test 1: System sendmail
    system_ok = test_sendmail_system()
    
    # Test 2: MCP Server
    mcp_ok = test_mcp_server_email()
    
    # Test 3: RAG Agent
    rag_ok = test_rag_agent_email()
    
    # Summary
    print("\n📊 Test Results Summary")
    print("=" * 50)
    print(f"System Sendmail: {'✅ Working' if system_ok else '❌ Failed'}")
    print(f"MCP Server: {'✅ Working' if mcp_ok else '❌ Failed'}")
    print(f"RAG Agent: {'✅ Working' if rag_ok else '❌ Failed'}")
    
    print("\n🔍 Failure Analysis:")
    if not system_ok:
        print("❌ SYSTEM LEVEL: Sendmail not available or not working")
        print("   Solution: Install/configure sendmail or use alternative mail service")
    
    if system_ok and not mcp_ok:
        print("❌ MCP SERVER LEVEL: Server not calling sendmail correctly")
        print("   Solution: Check MCP server implementation")
    
    if mcp_ok and not rag_ok:
        print("❌ RAG AGENT LEVEL: Agent not calling MCP server correctly")
        print("   Solution: Check agent MCP integration")
    
    if system_ok and mcp_ok and rag_ok:
        print("✅ ALL LEVELS WORKING: Email delivery should be successful")
    
    print("\n💡 Recommendations:")
    if not system_ok:
        print("1. Install sendmail: brew install sendmail (macOS)")
        print("2. Or use alternative: pip install smtplib for SMTP")
    if not mcp_ok:
        print("3. Check MCP server is running: python server.py")
        print("4. Verify MCP server has correct email implementation")
    if not rag_ok:
        print("5. Check RAG agent MCP integration")
        print("6. Verify agent is calling correct MCP server")

if __name__ == "__main__":
    main() 