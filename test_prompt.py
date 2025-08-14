#!/usr/bin/env python3
"""
Simple Prompt Test for Master Agent
Test the master agent with a single cybersecurity prompt.
"""

import asyncio
import sys
from agent.smart_master_agent import smart_master_agent

async def test_prompt(prompt: str):
    """Test the master agent with a single prompt."""
    
    print(f"🤖 Testing Master Agent with: '{prompt}'")
    print("=" * 60)
    
    session_id = "single_test_session"
    user_id = "single_test_user"
    
    try:
        # Process the prompt through the master agent
        result = await smart_master_agent.process_message(prompt, session_id, user_id)
        
        # Display results
        intent = result["intent_analysis"]["intent"]
        confidence = result["intent_analysis"]["confidence"]
        extracted_data = result["intent_analysis"]["extracted_data"]
        execution_result = result["execution_result"]
        
        print(f"🎯 Intent: {intent}")
        print(f"📊 Confidence: {confidence:.2f}")
        print(f"🔍 Extracted Data: {extracted_data}")
        # Get the actual result from the handler
        actual_result = execution_result.get('result', {})
        print(f"✅ Execution Result: {actual_result.get('action', 'Unknown')}")
        print(f"📝 Note: {actual_result.get('note', 'No note')}")
        print(f"📝 Message: {execution_result.get('message', 'No message')}")
        
        # Show specific cybersecurity features if applicable
        if intent == "cybersecurity_scan":
            scan_type = extracted_data.get("scan_type", "comprehensive")
            print(f"🔒 Scan Type: {scan_type}")
            
            if "dependency" in scan_type:
                print("   📦 Will scan dependencies for vulnerabilities")
            if "sast" in scan_type:
                print("   🔍 Will perform SAST static analysis")
            if "license" in scan_type:
                print("   📜 Will check license compliance")
            if "best_practices" in scan_type:
                print("   ✅ Will check security best practices")
            if "pre_merge" in scan_type:
                print("   🚦 Will check pre-merge security gates")
            if "metrics" in scan_type:
                print("   📊 Will track security metrics")
                
        elif intent == "secrets_detection":
            scan_type = extracted_data.get("scan_type", "comprehensive")
            target = extracted_data.get("target", ".")
            print(f"🔐 Scan Type: {scan_type}")
            print(f"🎯 Target: {target}")
            
        elif intent == "github_coverage":
            analysis_type = extracted_data.get("analysis_type", "repository")
            pr_number = extracted_data.get("pr_number")
            branch = extracted_data.get("branch", "main")
            print(f"🔍 Analysis Type: {analysis_type}")
            if pr_number:
                print(f"📝 PR Number: {pr_number}")
            print(f"🌿 Branch: {branch}")
        
        print("\n✅ Test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("🤖 Simple Master Agent Test")
        print("Usage: python test_prompt.py 'your cybersecurity prompt'")
        print("\nExamples:")
        print("  python test_prompt.py 'scan dependencies for vulnerabilities'")
        print("  python test_prompt.py 'perform SAST security analysis'")
        print("  python test_prompt.py 'check license compliance'")
        print("  python test_prompt.py 'run comprehensive cybersecurity scan'")
        print("  python test_prompt.py 'scan for secrets in my files'")
        return
    
    prompt = " ".join(sys.argv[1:])
    asyncio.run(test_prompt(prompt))

if __name__ == "__main__":
    main()
