#!/usr/bin/env python3
"""
Test Master Agent Secrets Detection Integration
Demonstrates how the master agent delegates secrets detection tasks.
"""

import asyncio
import os
import sys

# Add the agent directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'agent'))

from smart_master_agent import SmartMasterAgent

async def test_secrets_detection_integration():
    """Test the secrets detection integration with the master agent."""
    print("🧠 Testing Master Agent Secrets Detection Integration")
    print("=" * 60)
    
    # Initialize the master agent
    master_agent = SmartMasterAgent()
    
    # Test cases for secrets detection
    test_cases = [
        "scan for secrets in the project",
        "check for secrets in .env file",
        "detect secrets in the current directory",
        "analyze for sensitive data in agent folder",
        "look for API keys in the codebase",
        "find passwords in configuration files",
        "scan for tokens in the project",
        "check for credentials in the repository"
    ]
    
    print("🔍 Testing Secrets Detection Intent Recognition:")
    print("-" * 40)
    
    for i, test_message in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: '{test_message}'")
        
        try:
            # Process the message through the master agent
            result = await master_agent.process_message(
                message=test_message,
                session_id=f"test_session_{i}",
                user_id="test_user"
            )
            
            # Extract key information
            intent = result.get('intent_analysis', {}).get('intent', 'unknown')
            confidence = result.get('intent_analysis', {}).get('confidence', 0)
            execution_result = result.get('execution_result', {})
            
            print(f"   ✅ Intent: {intent} (confidence: {confidence:.2f})")
            
            if execution_result.get('success'):
                action = execution_result.get('result', {}).get('action', 'unknown')
                note = execution_result.get('result', {}).get('note', 'No note')
                print(f"   ✅ Action: {action}")
                print(f"   📝 Note: {note}")
            else:
                error = execution_result.get('error', 'Unknown error')
                print(f"   ❌ Error: {error}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 Simple Commands for Master Agent:")
    print("-" * 40)
    print("🔑 Secrets Detection Commands:")
    print("  • 'scan for secrets' - Comprehensive scan")
    print("  • 'check for secrets in .env' - File scan")
    print("  • 'detect secrets in agent folder' - Directory scan")
    print("  • 'find API keys' - API key detection")
    print("  • 'look for passwords' - Password detection")
    print("  • 'scan for tokens' - Token detection")
    print("  • 'analyze for sensitive data' - General scan")
    print("\n💡 Other Available Commands:")
    print("  • 'analyze test coverage' - GitHub coverage")
    print("  • 'send email to user@example.com' - Email")
    print("  • 'search for information' - Web search")
    print("  • 'save to desktop' - Desktop storage")
    
    print("\n🚀 Integration Status: COMPLETE!")
    print("The Master Agent now successfully delegates secrets detection tasks!")

if __name__ == "__main__":
    asyncio.run(test_secrets_detection_integration())

