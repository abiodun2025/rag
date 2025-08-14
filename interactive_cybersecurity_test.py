#!/usr/bin/env python3
"""
Interactive Cybersecurity Testing Script
Test the smart master agent's cybersecurity features in real-time.
"""

import asyncio
import logging
from agent.smart_master_agent import smart_master_agent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def interactive_test():
    """Interactive testing of cybersecurity features."""
    
    print("🔒 Interactive Cybersecurity Testing")
    print("=" * 50)
    print("Type your cybersecurity requests and see how the system responds!")
    print("Type 'quit' to exit, 'help' for examples, 'status' for agent stats")
    print()
    
    session_id = "interactive_test_session"
    user_id = "interactive_user"
    
    while True:
        try:
            # Get user input
            user_input = input("🔒 Enter cybersecurity request: ").strip()
            
            if user_input.lower() == 'quit':
                print("👋 Goodbye!")
                break
            elif user_input.lower() == 'help':
                print("\n📚 Example Cybersecurity Requests:")
                print("• 'scan dependencies for vulnerabilities in my project'")
                print("• 'perform SAST security analysis on my code'")
                print("• 'check license compliance in my repository'")
                print("• 'run comprehensive cybersecurity scan'")
                print("• 'scan for secrets in my files'")
                print("• 'analyze PR coverage for security'")
                print("• 'check security best practices'")
                print("• 'verify pre-merge security gates'")
                print("• 'track security metrics over time'")
                print()
                continue
            elif user_input.lower() == 'status':
                print(f"\n📊 Agent Statistics:")
                for intent, stats in smart_master_agent.agent_stats.items():
                    print(f"  {intent}: {stats['calls']} calls, {stats['success']} success, {stats['errors']} errors")
                print()
                continue
            elif not user_input:
                continue
            
            print(f"\n🔄 Processing: {user_input}")
            print("-" * 40)
            
            # Process the message through the smart master agent
            result = await smart_master_agent.process_message(user_input, session_id, user_id)
            
            # Display results
            intent = result["intent_analysis"]["intent"]
            confidence = result["intent_analysis"]["confidence"]
            extracted_data = result["intent_analysis"]["extracted_data"]
            execution_result = result["execution_result"]
            
            print(f"🎯 Intent: {intent}")
            print(f"📊 Confidence: {confidence:.2f}")
            print(f"🔍 Extracted Data: {extracted_data}")
            print(f"✅ Execution Result: {execution_result.get('action', 'Unknown')}")
            print(f"📝 Note: {execution_result.get('note', 'No note')}")
            
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
            
            print()
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            print()

if __name__ == "__main__":
    asyncio.run(interactive_test())
