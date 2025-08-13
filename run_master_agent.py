#!/usr/bin/env python3
"""
Interactive Master Agent Runner
Run the master agent directly without needing the API server
"""

import asyncio
from agent.smart_master_agent import SmartMasterAgent

async def run_master_agent():
    """Run the master agent interactively."""
    print("🧠 Smart Master Agent - Interactive Mode")
    print("=" * 60)
    print("🔑 Available Scan Commands:")
    print("  • 'scan for secrets' - Comprehensive security scan")
    print("  • 'scan .env file' - File-specific scan")
    print("  • 'scan agent folder' - Directory-specific scan")
    print("  • 'scan for API keys' - API key detection")
    print("  • 'scan for passwords' - Password detection")
    print("  • 'scan for tokens' - Token detection")
    print("  • 'scan for sensitive data' - General security scan")
    print("\n💡 Other Commands:")
    print("  • 'analyze test coverage' - GitHub coverage analysis")
    print("  • 'send email to user@example.com' - Email composition")
    print("  • 'search for information' - Web search")
    print("  • 'save to desktop' - Desktop storage")
    print("\nType 'exit' to quit")
    print("=" * 60)
    
    # Initialize the master agent
    agent = SmartMasterAgent()
    
    while True:
        try:
            # Get user input
            user_input = input("\n🤖 Master Agent> ").strip()
            
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not user_input:
                continue
            
            print(f"🔍 Processing: {user_input}")
            
            # Process the message through the master agent
            result = await agent.process_message(
                message=user_input,
                session_id="interactive-session",
                user_id="interactive-user"
            )
            
            # Extract key information
            intent_analysis = result.get('intent_analysis', {})
            execution_result = result.get('execution_result', {})
            
            # Display the result
            print(f"📊 Intent: {intent_analysis.get('intent', 'unknown')}")
            print(f"📈 Confidence: {intent_analysis.get('confidence', 0):.2f}")
            
            if execution_result.get('success'):
                action = execution_result.get('result', {}).get('action', 'unknown')
                note = execution_result.get('result', {}).get('note', 'No note')
                print(f"✅ Action: {action}")
                print(f"📝 Note: {note}")
                
                # Show secrets detection results if available
                if action == 'secrets_detection_success':
                    result_data = execution_result.get('result', {}).get('result', {})
                    secrets_count = result_data.get('total_secrets', 0)
                    files_scanned = result_data.get('files_scanned', 0)
                    print(f"🔍 Secrets Found: {secrets_count}")
                    print(f"📁 Files Scanned: {files_scanned}")
            else:
                error = execution_result.get('error', 'Unknown error')
                print(f"❌ Error: {error}")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(run_master_agent())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
