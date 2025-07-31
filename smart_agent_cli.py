#!/usr/bin/env python3
"""
Direct Smart Agent CLI - Works without API server
"""

import asyncio
import sys
from agent.smart_master_agent import smart_master_agent

class SmartAgentCLI:
    """Direct Smart Agent CLI"""
    
    def __init__(self):
        self.session_id = f"cli_session_{int(asyncio.get_event_loop().time())}"
        self.user_id = "cli_user"
    
    def print_banner(self):
        """Print welcome banner."""
        print("\n" + "=" * 60)
        print("🧠 Smart Master Agent CLI (Direct Mode)")
        print("=" * 60)
        print("Just type naturally - I'll automatically understand what you want to do!")
        print("Type 'help' for commands or 'exit' to quit")
        print("=" * 60 + "\n")
    
    def print_help(self):
        """Print help information."""
        help_text = """
Smart Master Agent - Just Type Naturally!

Examples:
  Hello world                    - Saves to Desktop
  Remember this meeting note     - Saves to Desktop
  Email john@example.com about project - Email composition
  What's the latest AI news?     - Web search
  Search for OpenAI funding      - Internal search
  Relationship between X and Y   - Knowledge graph
  Count r letters in programming - MCP tools
  List desktop files             - MCP tools
  Open gmail                     - MCP tools

Commands:
  help           - Show this help message
  clear          - Clear the session
  exit/quit      - Exit the CLI

How it works:
  The Smart Master Agent automatically identifies what you want to do:
  • Save messages → Desktop (default)
  • Search queries → Web search
  • Email mentions → Email composition
  • Relationship questions → Knowledge graph
  • MCP tool requests → MCP server tools
  • Everything else → General conversation
"""
        print(help_text)
    
    async def run(self):
        """Run the CLI main loop."""
        self.print_banner()
        print("✅ Smart Agent ready! Just type naturally and I'll understand what you want to do.\n")
        
        try:
            while True:
                try:
                    # Get user input
                    user_input = input("🎯 Smart Agent > ").strip()
                    
                    if not user_input:
                        continue
                    
                    # Handle commands
                    if user_input.lower() in ['exit', 'quit']:
                        print("👋 Goodbye!")
                        break
                    elif user_input.lower() == 'help':
                        self.print_help()
                        continue
                    elif user_input.lower() == 'clear':
                        self.session_id = f"cli_session_{int(asyncio.get_event_loop().time())}"
                        print("✓ Session cleared")
                        continue
                    
                    # Process with Smart Master Agent
                    print(f"\n🤖 Processing: {user_input}")
                    print("-" * 50)
                    
                    result = await smart_master_agent.process_message(
                        message=user_input,
                        session_id=self.session_id,
                        user_id=self.user_id
                    )
                    
                    # Display results
                    intent_analysis = result['intent_analysis']
                    execution_result = result['execution_result']
                    
                    print(f"🎯 Intent: {intent_analysis['intent']} (confidence: {intent_analysis['confidence']:.2f})")
                    
                    if execution_result['success']:
                        print(f"✅ Success: {execution_result['message']}")
                        
                        # Show detailed result if available
                        if 'result' in execution_result and execution_result['result']:
                            result_data = execution_result['result']
                            if isinstance(result_data, dict):
                                if 'file_path' in result_data:
                                    print(f"📁 File: {result_data['file_path']}")
                                if 'email_to' in result_data:
                                    print(f"📧 Email: {result_data['email_to']}")
                                if 'search_results' in result_data:
                                    print(f"🔍 Found {len(result_data['search_results'])} results")
                                if 'action' in result_data:
                                    print(f"📋 Action: {result_data['action']}")
                    else:
                        print(f"❌ Error: {execution_result.get('error', 'Unknown error')}")
                    
                    print("-" * 50 + "\n")
                    
                except KeyboardInterrupt:
                    print("\n👋 Goodbye!")
                    break
                except EOFError:
                    print("\n👋 Goodbye!")
                    break
                except Exception as e:
                    print(f"❌ Error: {e}")
                    print("Please try again.\n")
        
        except Exception as e:
            print(f"❌ CLI error: {e}")

async def main():
    """Main entry point."""
    cli = SmartAgentCLI()
    await cli.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Startup error: {e}")
        sys.exit(1) 