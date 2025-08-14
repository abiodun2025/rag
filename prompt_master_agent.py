#!/usr/bin/env python3
"""
Prompt Master Agent Interface
Direct prompt-based testing of the Smart Master Agent's cybersecurity capabilities.
"""

import asyncio
import logging
from agent.smart_master_agent import smart_master_agent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def prompt_master_agent():
    """Prompt the master agent with cybersecurity requests."""
    
    print("🤖 Smart Master Agent - Cybersecurity Testing Interface")
    print("=" * 60)
    print("This interface directly prompts the master agent with cybersecurity requests.")
    print("Type 'quit' to exit, 'help' for examples, 'demo' for automatic demo")
    print()
    
    session_id = "prompt_test_session"
    user_id = "prompt_user"
    
    while True:
        try:
            # Get user input
            user_input = input("🤖 Enter cybersecurity prompt: ").strip()
            
            if user_input.lower() == 'quit':
                print("👋 Goodbye!")
                break
            elif user_input.lower() == 'help':
                print("\n📚 Cybersecurity Prompt Examples:")
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
            elif user_input.lower() == 'demo':
                await run_automated_demo(session_id, user_id)
                continue
            elif not user_input:
                continue
            
            print(f"\n🔄 Processing prompt: {user_input}")
            print("-" * 50)
            
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
            
            print()
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            print()

async def run_automated_demo(session_id: str, user_id: str):
    """Run an automated demo of cybersecurity features."""
    
    print("\n🎬 Running Automated Cybersecurity Demo")
    print("=" * 50)
    
    demo_prompts = [
        "scan dependencies for vulnerabilities in my project",
        "perform SAST security analysis on my code",
        "check license compliance in my repository",
        "run comprehensive cybersecurity scan",
        "scan for secrets in my files",
        "analyze PR coverage for security",
        "check security best practices",
        "verify pre-merge security gates",
        "track security metrics over time"
    ]
    
    for i, prompt in enumerate(demo_prompts, 1):
        print(f"\n🧪 Demo {i}: {prompt}")
        print("-" * 40)
        
        try:
            # Process the prompt through the master agent
            result = await smart_master_agent.process_message(prompt, session_id, user_id)
            
            # Display results
            intent = result["intent_analysis"]["intent"]
            confidence = result["intent_analysis"]["confidence"]
            execution_result = result["execution_result"]
            
            print(f"🎯 Intent: {intent}")
            print(f"📊 Confidence: {confidence:.2f}")
            # Get the actual result from the handler
            actual_result = execution_result.get('result', {})
            print(f"✅ Action: {actual_result.get('action', 'Unknown')}")
            print(f"📝 Note: {actual_result.get('note', 'No note')}")
            print(f"📝 Message: {execution_result.get('message', 'No message')}")
            
            # Brief pause between demos
            await asyncio.sleep(1)
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n🎉 Automated Demo Completed!")
    print("Now try your own cybersecurity prompts!")

def main():
    """Main function."""
    print("🚀 Starting Smart Master Agent Cybersecurity Interface...")
    asyncio.run(prompt_master_agent())

if __name__ == "__main__":
    main()
