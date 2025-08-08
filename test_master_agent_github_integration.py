#!/usr/bin/env python3
"""
Test SmartMasterAgent GitHub Coverage Integration
"""

import asyncio
import os
from agent.smart_master_agent import SmartMasterAgent

async def test_github_coverage_integration():
    """Test GitHub coverage integration with SmartMasterAgent."""
    print("🧪 Testing SmartMasterAgent GitHub Coverage Integration")
    print("=" * 60)
    
    # Set up environment variables
    os.environ['GITHUB_TOKEN'] = 'YOUR_GITHUB_TOKEN_HERE'
    os.environ['GITHUB_OWNER'] = 'abiodun2025'
    os.environ['GITHUB_REPO'] = 'rag'
    
    # Initialize SmartMasterAgent
    agent = SmartMasterAgent()
    
    # Test cases
    test_cases = [
        "analyze coverage for PR #11",
        "test coverage analysis",
        "run coverage test",
        "check coverage for main branch",
        "analyze test coverage",
        "coverage analysis for repository"
    ]
    
    for i, test_message in enumerate(test_cases, 1):
        print(f"\n🎯 Test {i}: '{test_message}'")
        print("-" * 40)
        
        try:
            # Analyze intent
            intent_result = agent.analyze_intent(test_message)
            print(f"📊 Intent: {intent_result.intent.value}")
            print(f"📈 Confidence: {intent_result.confidence:.2f}")
            print(f"📋 Extracted Data: {intent_result.extracted_data}")
            
            # Execute intent
            result = await agent.execute_intent(intent_result, "test_session", "test_user")
            print(f"✅ Result Action: {result.get('action', 'unknown')}")
            print(f"📝 Note: {result.get('note', 'No note')}")
            
            # Get user-friendly message
            friendly_message = agent._get_user_friendly_message(intent_result.intent, result)
            print(f"💬 User Message: {friendly_message}")
            
            if result.get('action') == 'github_coverage_error':
                print(f"❌ Error: {result.get('error', 'Unknown error')}")
            else:
                print("✅ Success!")
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 GitHub Coverage Integration Test Complete!")

if __name__ == "__main__":
    asyncio.run(test_github_coverage_integration())
