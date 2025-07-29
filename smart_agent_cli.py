#!/usr/bin/env python3
"""
Interactive CLI for Smart Agent
Allows real-time interaction with the smart agent and MCP tools.
"""

import asyncio
import json
import sys
from datetime import datetime
from agent.smart_master_agent import SmartMasterAgent

class SmartAgentCLI:
    def __init__(self):
        self.agent = SmartMasterAgent()
        self.session_id = f"cli_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.running = True
        
    async def start(self):
        """Start the interactive CLI."""
        print("🤖 Smart Agent CLI Started!")
        print("=" * 50)
        print("Available commands:")
        print("- Type any message to interact with the smart agent")
        print("- Type 'tools' to see available MCP tools")
        print("- Type 'status' to check system status")
        print("- Type 'quit' or 'exit' to stop")
        print("=" * 50)
        
        while self.running:
            try:
                # Get user input
                user_input = input("\n💬 You: ").strip()
                
                if not user_input:
                    continue
                    
                # Handle special commands
                if user_input.lower() in ['quit', 'exit', 'q']:
                    await self.quit()
                    break
                elif user_input.lower() == 'tools':
                    await self.show_tools()
                    continue
                elif user_input.lower() == 'status':
                    await self.show_status()
                    continue
                elif user_input.lower() == 'help':
                    await self.show_help()
                    continue
                
                # Process with smart agent
                await self.process_message(user_input)
                
            except KeyboardInterrupt:
                print("\n\n⚠️  Interrupted by user")
                await self.quit()
                break
            except Exception as e:
                print(f"❌ Error: {str(e)}")
    
    async def process_message(self, message: str):
        """Process a message with the smart agent."""
        try:
            print(f"🤖 Processing: {message}")
            
            # Process with smart agent
            response = await self.agent.process_message(message, self.session_id)
            
            # Display response
            print(f"🧠 Intent: {response.get('intent', 'unknown')}")
            print(f"⚡ Action: {response.get('action', 'unknown')}")
            print(f"💭 Message: {response.get('message', 'No message')}")
            
            # Show additional details if available
            if 'details' in response:
                print(f"📋 Details: {response['details']}")
                
        except Exception as e:
            print(f"❌ Error processing message: {str(e)}")
    
    async def show_tools(self):
        """Show available MCP tools."""
        try:
            import requests
            response = requests.get("http://127.0.0.1:5000/tools")
            if response.status_code == 200:
                tools = response.json()
                print(f"\n🔧 Available MCP Tools ({len(tools)} total):")
                print("-" * 40)
                
                # Group tools by category
                categories = {
                    "📧 Email": [],
                    "🖥️ Desktop": [],
                    "📞 Phone": [],
                    "💻 Code": [],
                    "🔧 Utility": []
                }
                
                for tool in tools:
                    name = tool.get('name', 'unknown')
                    if 'email' in name or 'gmail' in name or 'sendmail' in name:
                        categories["📧 Email"].append(name)
                    elif 'desktop' in name or 'path' in name:
                        categories["🖥️ Desktop"].append(name)
                    elif 'phone' in name or 'call' in name:
                        categories["📞 Phone"].append(name)
                    elif 'code' in name or 'generate' in name or 'read' in name:
                        categories["💻 Code"].append(name)
                    else:
                        categories["🔧 Utility"].append(name)
                
                for category, tool_list in categories.items():
                    if tool_list:
                        print(f"\n{category}:")
                        for tool in tool_list:
                            print(f"  • {tool}")
            else:
                print("❌ Could not fetch tools from MCP server")
                
        except Exception as e:
            print(f"❌ Error fetching tools: {str(e)}")
    
    async def show_status(self):
        """Show system status."""
        try:
            import requests
            
            # Check MCP server health
            health_response = requests.get("http://127.0.0.1:5000/health")
            mcp_status = "✅ Online" if health_response.status_code == 200 else "❌ Offline"
            
            print(f"\n📊 System Status:")
            print(f"🤖 Smart Agent: ✅ Running")
            print(f"🔧 MCP Server: {mcp_status}")
            print(f"🆔 Session ID: {self.session_id}")
            print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
        except Exception as e:
            print(f"❌ Error checking status: {str(e)}")
    
    async def show_help(self):
        """Show help information."""
        print(f"\n📖 Smart Agent CLI Help:")
        print("=" * 40)
        print("💬 Interactive Mode:")
        print("  - Type any message to interact with the smart agent")
        print("  - The agent will detect your intent and take appropriate action")
        print("  - Supports email, file operations, phone calls, code generation, etc.")
        print()
        print("🔧 Special Commands:")
        print("  - 'tools' - Show available MCP tools")
        print("  - 'status' - Check system status")
        print("  - 'help' - Show this help message")
        print("  - 'quit' or 'exit' - Stop the CLI")
        print()
        print("🎯 Example Messages:")
        print("  - 'send email to test@example.com'")
        print("  - 'list desktop files'")
        print("  - 'generate a python calculator'")
        print("  - 'count r letters in programming'")
        print("  - 'get desktop path'")
    
    async def quit(self):
        """Quit the CLI."""
        print("\n👋 Goodbye! Smart Agent CLI stopped.")
        self.running = False

async def main():
    """Main entry point."""
    cli = SmartAgentCLI()
    await cli.start()

if __name__ == "__main__":
    asyncio.run(main()) 