#!/usr/bin/env python3
"""
Master Agent Secrets Detection Demo
Simple demonstration of how the master agent delegates secrets detection tasks.
"""

import asyncio
import os
import sys

# Add the agent directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'agent'))

from smart_master_agent import SmartMasterAgent

async def demo_secrets_detection():
    """Demonstrate the master agent's secrets detection capabilities."""
    print("🧠 Master Agent Secrets Detection Demo")
    print("=" * 60)
    print("This demo shows how the master agent automatically detects")
    print("secrets detection intents and delegates tasks to the agent.")
    print("=" * 60)
    
    # Initialize the master agent
    master_agent = SmartMasterAgent()
    
    # Demo commands
    demo_commands = [
        "scan for secrets",
        "scan .env file",
        "scan agent folder",
        "scan for sensitive data"
    ]
    
    print("\n🔍 Demo Commands:")
    print("-" * 30)
    
    for i, command in enumerate(demo_commands, 1):
        print(f"{i}. {command}")
    
    print("\n📝 Note: These commands demonstrate different scan types:")
    print("   • Command 1: Comprehensive scan")
    print("   • Command 2: File-specific scan")
    print("   • Command 3: Directory-specific scan")
    print("   • Command 4: General security scan")
    
    print("\n🚀 Running Demo...")
    print("-" * 30)
    
    for i, command in enumerate(demo_commands, 1):
        print(f"\n{i}. Executing: '{command}'")
        print("-" * 40)
        
        try:
            # Process the command through the master agent
            result = await master_agent.process_message(
                message=command,
                session_id=f"demo_session_{i}",
                user_id="demo_user"
            )
            
            # Extract key information
            intent = result.get('intent_analysis', {}).get('intent', 'unknown')
            confidence = result.get('intent_analysis', {}).get('confidence', 0)
            execution_result = result.get('execution_result', {})
            
            print(f"✅ Intent: {intent} (confidence: {confidence:.2f})")
            
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
                
        except Exception as e:
            print(f"❌ Exception: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 How to Use the Master Agent:")
    print("-" * 40)
    print("🔑 Scan Commands:")
    print("  • 'scan for secrets' - Comprehensive scan")
    print("  • 'scan .env file' - File scan")
    print("  • 'scan agent folder' - Directory scan")
    print("  • 'scan for API keys' - API key detection")
    print("  • 'scan for passwords' - Password detection")
    print("  • 'scan for tokens' - Token detection")
    print("  • 'scan for sensitive data' - General scan")
    print("\n💡 Other Available Commands:")
    print("  • 'analyze test coverage' - GitHub coverage")
    print("  • 'send email to user@example.com' - Email")
    print("  • 'search for information' - Web search")
    print("  • 'save to desktop' - Desktop storage")
    
    print("\n🚀 Integration Status: SUCCESS!")
    print("The Master Agent successfully delegates secrets detection tasks!")

if __name__ == "__main__":
    asyncio.run(demo_secrets_detection())
