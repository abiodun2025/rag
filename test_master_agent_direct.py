#!/usr/bin/env python3
"""
Direct Test of SmartMasterAgent GitHub Coverage Integration
"""

import asyncio
import os
from agent.smart_master_agent import SmartMasterAgent

async def test_direct_integration():
    """Test SmartMasterAgent directly with GitHub coverage requests."""
    print("🧪 Direct Test of SmartMasterAgent GitHub Coverage Integration")
    print("=" * 70)
    
    # Set up environment variables
    os.environ['GITHUB_TOKEN'] = 'YOUR_GITHUB_TOKEN_HERE'
    os.environ['GITHUB_OWNER'] = 'abiodun2025'
    os.environ['GITHUB_REPO'] = 'rag'
    
    # Initialize SmartMasterAgent
    agent = SmartMasterAgent()
    
    # Test a simple coverage request
    test_message = "analyze coverage for PR #11"
    
    print(f"🎯 Testing: '{test_message}'")
    print("-" * 50)
    
    try:
        # Process the message directly
        result = await agent.process_message(test_message, "test_session", "test_user")
        
        # Extract key information
        intent = result['intent_analysis']['intent']
        confidence = result['intent_analysis']['confidence']
        execution_result = result['execution_result']
        
        print(f"📊 Intent Detected: {intent}")
        print(f"📈 Confidence: {confidence:.2f}")
        print(f"✅ Execution Action: {execution_result.get('action', 'unknown')}")
        print(f"📝 Result Note: {execution_result.get('note', 'No note')}")
        
        # Get user-friendly message
        friendly_message = agent._get_user_friendly_message(
            result['intent_analysis']['intent'], 
            execution_result
        )
        print(f"💬 User Message: {friendly_message}")
        
        if execution_result.get('action') == 'github_coverage_error':
            print(f"❌ Error: {execution_result.get('error', 'Unknown error')}")
        else:
            print("✅ Success! GitHub Coverage Agent integration working!")
            
            # Show some details if available
            if 'result' in execution_result:
                coverage_result = execution_result['result']
                if 'overall_coverage' in coverage_result:
                    overall = coverage_result['overall_coverage']
                    print(f"📊 Coverage: {overall.get('percentage', 0):.1f}%")
                    print(f"📈 Total Lines: {overall.get('total_lines', 0)}")
                    print(f"✅ Covered Lines: {overall.get('covered_lines', 0)}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("🎉 Direct Integration Test Complete!")
    print("\n💡 Now you can use simple commands like:")
    print("   • 'analyze coverage for PR #11'")
    print("   • 'test coverage analysis'")
    print("   • 'run coverage test'")
    print("   • 'check coverage for main branch'")
    print("   • 'analyze test coverage'")
    print("\n🚀 The Master Agent will automatically delegate to the GitHub Coverage Agent!")

if __name__ == "__main__":
    asyncio.run(test_direct_integration())
