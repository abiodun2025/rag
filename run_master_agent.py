#!/usr/bin/env python3
"""
Simple Interactive Master Agent Runner
Run the master agent directly without needing the API server
"""

import asyncio
from agent.smart_master_agent import SmartMasterAgent

async def run_master_agent():
    """Run the master agent interactively."""
    print("🧠 Smart Master Agent - Interactive Mode")
    print("=" * 50)
    print("Available intents: email, mcp_tools, github_coverage, knowledge_graph, web_search, desktop_save")
    print("Type 'exit' to quit")
    print("=" * 50)
    
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
            
            # Display the result
            print(f"📊 Intent: {result.get('intent', 'unknown')}")
            print(f"📈 Confidence: {result.get('confidence', 0):.2f}")
            print(f"✅ Action: {result.get('action', 'unknown')}")
            print(f"📝 Note: {result.get('note', 'No note')}")
            print(f"💬 Response: {result.get('user_message', 'No response')}")
            
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
