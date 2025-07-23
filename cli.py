#!/usr/bin/env python3
"""
Command Line Interface for Agentic RAG with Knowledge Graph.

This CLI connects to the API and demonstrates the agent's tool usage capabilities.
"""

import json
import asyncio
import aiohttp
import argparse
import os
from typing import Dict, Any, List
from datetime import datetime
import sys

# ANSI color codes for better formatting
class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


class AgenticRAGCLI:
    """CLI for interacting with the Agentic RAG API."""
    
    def __init__(self, base_url: str = "http://localhost:8058"):
        """Initialize CLI with base URL."""
        self.base_url = base_url.rstrip('/')
        self.session_id = None
        self.user_id = "cli_user"
        
    def print_banner(self):
        """Print welcome banner."""
        print(f"\n{Colors.CYAN}{Colors.BOLD}=" * 60)
        print("🧠 Smart Master Agent CLI")
        print("=" * 60)
        print(f"{Colors.WHITE}Connected to: {self.base_url}")
        print(f"Just type naturally - I'll automatically understand what you want to do!")
        print(f"Type 'help' for commands or 'exit' to quit")
        print("=" * 60 + f"{Colors.END}\n")
    
    def print_help(self):
        """Print help information."""
        help_text = f"""
{Colors.BOLD}Smart Master Agent - Just Type Naturally!{Colors.END}

{Colors.BOLD}Examples:{Colors.END}
  {Colors.GREEN}Hello world{Colors.END}                    - Saves to Desktop
  {Colors.GREEN}Remember this meeting note{Colors.END}      - Saves to Desktop
  {Colors.GREEN}Email john@example.com about project{Colors.END} - Email composition
  {Colors.GREEN}What's the latest AI news?{Colors.END}     - Web search
  {Colors.GREEN}Search for OpenAI funding{Colors.END}       - Internal search
  {Colors.GREEN}Relationship between X and Y{Colors.END}    - Knowledge graph

{Colors.BOLD}Commands:{Colors.END}
  {Colors.GREEN}help{Colors.END}           - Show this help message
  {Colors.GREEN}health{Colors.END}         - Check API health status
  {Colors.GREEN}clear{Colors.END}          - Clear the session
  {Colors.GREEN}chat{Colors.END}           - Traditional chat mode
  {Colors.GREEN}exit/quit{Colors.END}      - Exit the CLI

{Colors.BOLD}How it works:{Colors.END}
  The Smart Master Agent automatically identifies what you want to do:
  • Save messages → Desktop (default)
  • Search queries → Web search
  • Email mentions → Email composition
  • Relationship questions → Knowledge graph
  • Everything else → General conversation
"""
        print(help_text)
    
    async def check_health(self) -> bool:
        """Check API health."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/health") as response:
                    if response.status == 200:
                        data = await response.json()
                        status = data.get('status', 'unknown')
                        if status in ['healthy', 'degraded']:
                            if status == 'healthy':
                                print(f"{Colors.GREEN}✓ API is healthy{Colors.END}")
                            else:
                                print(f"{Colors.YELLOW}⚠ API status: {status} (some features may be limited){Colors.END}")
                            return True
                        else:
                            print(f"{Colors.RED}✗ API status: {status}{Colors.END}")
                            return False
                    else:
                        print(f"{Colors.RED}✗ API health check failed (HTTP {response.status}){Colors.END}")
                        return False
        except Exception as e:
            print(f"{Colors.RED}✗ Failed to connect to API: {e}{Colors.END}")
            return False
    
    def format_tools_used(self, tools: List[Dict[str, Any]]) -> str:
        """Format tools used for display."""
        if not tools:
            return f"{Colors.YELLOW}No tools used{Colors.END}"
        
        formatted = f"{Colors.MAGENTA}{Colors.BOLD}🛠 Tools Used:{Colors.END}\n"
        for i, tool in enumerate(tools, 1):
            tool_name = tool.get('tool_name', 'unknown')
            args = tool.get('args', {})
            
            formatted += f"  {Colors.CYAN}{i}. {tool_name}{Colors.END}"
            
            # Show key arguments for context
            if args:
                key_args = []
                if 'query' in args:
                    key_args.append(f"query='{args['query'][:50]}{'...' if len(args['query']) > 50 else ''}'")
                if 'limit' in args:
                    key_args.append(f"limit={args['limit']}")
                if 'entity_name' in args:
                    key_args.append(f"entity='{args['entity_name']}'")
                
                if key_args:
                    formatted += f" ({', '.join(key_args)})"
            
            formatted += "\n"
        
        return formatted
    
    async def stream_chat(self, message: str) -> None:
        """Send message to streaming chat endpoint and display response."""
        print(f"{Colors.CYAN}DEBUG: Sending message to {self.base_url}/chat/stream{Colors.END}")
        print(f"{Colors.CYAN}DEBUG: Message: '{message}'{Colors.END}")
        print(f"{Colors.CYAN}DEBUG: Session ID: {self.session_id}{Colors.END}")
        
        request_data = {
            "message": message,
            "session_id": self.session_id,
            "user_id": self.user_id,
            "search_type": "hybrid"
        }
        
        print(f"{Colors.CYAN}DEBUG: Request data: {request_data}{Colors.END}")
        
        try:
            async with aiohttp.ClientSession() as session:
                print(f"{Colors.CYAN}DEBUG: Making POST request{Colors.END}")
                async with session.post(
                    f"{self.base_url}/chat/stream",
                    json=request_data,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    
                    print(f"{Colors.CYAN}DEBUG: Response status: {response.status}{Colors.END}")
                    
                    if response.status != 200:
                        error_text = await response.text()
                        print(f"{Colors.RED}✗ API Error ({response.status}): {error_text}{Colors.END}")
                        return
                    
                    print(f"\n{Colors.BOLD}🤖 Assistant:{Colors.END}")
                    
                    tools_used = []
                    full_response = ""
                    line_count = 0
                    
                    print(f"{Colors.CYAN}DEBUG: Starting to read response stream{Colors.END}")
                    async for line in response.content:
                        line = line.decode('utf-8').strip()
                        line_count += 1
                        
                        if line.startswith('data: '):
                            try:
                                data = json.loads(line[6:])  # Remove 'data: ' prefix
                                print(f"{Colors.CYAN}DEBUG: Received data type: {data.get('type')}{Colors.END}")
                                
                                if data.get('type') == 'session':
                                    # Store session ID for future requests
                                    self.session_id = data.get('session_id')
                                    print(f"{Colors.CYAN}DEBUG: Session ID set to: {self.session_id}{Colors.END}")
                                
                                elif data.get('type') == 'text':
                                    # Stream text content
                                    content = data.get('content', '')
                                    print(content, end='', flush=True)
                                    full_response += content
                                
                                elif data.get('type') == 'tools':
                                    # Store tools used information
                                    tools_used = data.get('tools', [])
                                    print(f"{Colors.CYAN}DEBUG: Tools used: {len(tools_used)} tools{Colors.END}")
                                
                                elif data.get('type') == 'end':
                                    # End of stream
                                    print(f"{Colors.CYAN}DEBUG: Stream ended{Colors.END}")
                                    break
                                
                                elif data.get('type') == 'error':
                                    # Handle errors
                                    error_content = data.get('content', 'Unknown error')
                                    print(f"\n{Colors.RED}Error: {error_content}{Colors.END}")
                                    return
                            
                            except json.JSONDecodeError as e:
                                # Skip malformed JSON
                                print(f"{Colors.YELLOW}DEBUG: JSON decode error on line {line_count}: {e}{Colors.END}")
                                continue
                    
                    print(f"{Colors.CYAN}DEBUG: Stream processing completed, {line_count} lines processed{Colors.END}")
                    print(f"{Colors.CYAN}DEBUG: Full response length: {len(full_response)} characters{Colors.END}")
                    
                    # Print newline after response
                    print()
                    
                    # Display tools used
                    if tools_used:
                        print(f"\n{self.format_tools_used(tools_used)}")
                    
                    # Print separator
                    print(f"{Colors.BLUE}{'─' * 60}{Colors.END}")
        
        except aiohttp.ClientError as e:
            print(f"{Colors.RED}✗ Connection error: {e}{Colors.END}")
            print(f"{Colors.CYAN}DEBUG: Client error details: {type(e).__name__}{Colors.END}")
        except Exception as e:
            print(f"{Colors.RED}✗ Unexpected error: {e}{Colors.END}")
            print(f"{Colors.CYAN}DEBUG: Exception type: {type(e).__name__}{Colors.END}")
            import traceback
            print(f"{Colors.CYAN}DEBUG: Traceback: {traceback.format_exc()}{Colors.END}")
    
    async def run(self):
        """Run the CLI main loop."""
        self.print_banner()
        
        # Check API health
        if not await self.check_health():
            print(f"{Colors.RED}Cannot connect to API. Please ensure the server is running.{Colors.END}")
            return
        
        print(f"{Colors.GREEN}Ready! Just type naturally and I'll automatically understand what you want to do.{Colors.END}\n")
        
        try:
            while True:
                try:
                    # Get user input
                    user_input = input(f"{Colors.BOLD}🎯 Smart Agent > {Colors.END}").strip()
                    
                    if not user_input:
                        continue
                    
                    # Handle commands
                    if user_input.lower() in ['exit', 'quit']:
                        print(f"{Colors.CYAN}👋 Goodbye!{Colors.END}")
                        break
                    elif user_input.lower() == 'help':
                        self.print_help()
                        continue
                    elif user_input.lower() == 'health':
                        await self.check_health()
                        continue
                    elif user_input.lower() == 'clear':
                        self.session_id = None
                        print(f"{Colors.GREEN}✓ Session cleared{Colors.END}")
                        continue
                    elif user_input.lower() == 'chat':
                        print("🤖 Traditional Chat Mode")
                        print("Type 'exit' to return to Smart Agent mode")
                        
                        chat_mode = True
                        while chat_mode:
                            try:
                                chat_input = input("\n🤖 Chat > ").strip()
                                if not chat_input:
                                    continue
                                    
                                if chat_input.lower() in ['exit', 'quit', 'q']:
                                    chat_mode = False
                                    break
                                
                                # Send to traditional chat endpoint
                                await self.stream_chat(chat_input)
                                        
                            except KeyboardInterrupt:
                                chat_mode = False
                                break
                            except EOFError:
                                chat_mode = False
                                break
                            except Exception as e:
                                print(f"❌ Error: {e}")
                        
                        print("Returning to Smart Agent mode...")
                        continue
                    
                    # Process with Smart Master Agent by default
                    try:
                        async with aiohttp.ClientSession() as session:
                            response = await session.post(
                                f"{self.base_url}/smart-agent/process",
                                json={
                                    "message": user_input,
                                    "user_id": self.user_id,
                                    "session_id": self.session_id,
                                    "search_type": "hybrid"
                                },
                                headers={"Content-Type": "application/json"}
                            )
                            
                            if response.status == 200:
                                result = await response.json()
                                smart_result = result['smart_agent_result']
                                intent_analysis = smart_result['intent_analysis']
                                execution_result = smart_result['execution_result']
                                
                                print(f"\n🤖 Smart Agent Response:")
                                print(f"Session: {result['session_id']}")
                                print(f"Processing Time: {result['processing_time_ms']:.2f}ms")
                                print(f"Intent: {intent_analysis['intent']} (confidence: {intent_analysis['confidence']:.2f})")
                                
                                if execution_result['success']:
                                    print(f"{Colors.GREEN}✅ {execution_result['message']}{Colors.END}")
                                    
                                    # Show results if available
                                    result_data = execution_result['result']
                                    if isinstance(result_data, dict):
                                        # Handle web search results (direct web search)
                                        if result_data.get('action') == 'web_search' and result_data.get('results'):
                                            print(f"\n{Colors.CYAN}🌐 Web Search Results:{Colors.END}")
                                            for i, item in enumerate(result_data['results'][:3], 1):
                                                title = item.get('title', 'No title')
                                                content = item.get('content', item.get('snippet', 'No content'))
                                                
                                                # Clean up the content for better readability
                                                if content:
                                                    # Remove URLs from content
                                                    import re
                                                    content = re.sub(r'https?://\S+', '', content)
                                                    content = re.sub(r'www\.\S+', '', content)
                                                    content = content.strip()
                                                
                                                print(f"\n{Colors.BOLD}{i}. {title}{Colors.END}")
                                                if content:
                                                    # Truncate content to 200 characters for readability
                                                    display_content = content[:200] + "..." if len(content) > 200 else content
                                                    print(f"   {display_content}")
                                                
                                        # Handle web search fallback results
                                        elif result_data.get('action') == 'internal_search_with_web_fallback' and result_data.get('web_results'):
                                            print(f"\n{Colors.CYAN}🌐 Web Search Fallback Results:{Colors.END}")
                                            for i, item in enumerate(result_data['web_results'][:3], 1):
                                                title = item.get('title', 'No title')
                                                content = item.get('content', item.get('snippet', 'No content'))
                                                
                                                # Clean up the content for better readability
                                                if content:
                                                    # Remove URLs from content
                                                    import re
                                                    content = re.sub(r'https?://\S+', '', content)
                                                    content = re.sub(r'www\.\S+', '', content)
                                                    content = content.strip()
                                                
                                                print(f"\n{Colors.BOLD}{i}. {title}{Colors.END}")
                                                if content:
                                                    # Truncate content to 200 characters for readability
                                                    display_content = content[:200] + "..." if len(content) > 200 else content
                                                    print(f"   {display_content}")
                                        
                                        # Handle knowledge graph web search fallback
                                        elif result_data.get('action') == 'knowledge_graph_search_with_web_fallback' and result_data.get('web_results'):
                                            print(f"\n{Colors.MAGENTA}🧠 Knowledge Graph Web Search Fallback:{Colors.END}")
                                            for i, item in enumerate(result_data['web_results'][:3], 1):
                                                title = item.get('title', 'No title')
                                                content = item.get('content', item.get('snippet', 'No content'))
                                                
                                                # Clean up the content for better readability
                                                if content:
                                                    # Remove URLs from content
                                                    import re
                                                    content = re.sub(r'https?://\S+', '', content)
                                                    content = re.sub(r'www\.\S+', '', content)
                                                    content = content.strip()
                                                
                                                print(f"\n{Colors.BOLD}{i}. {title}{Colors.END}")
                                                if content:
                                                    # Truncate content to 200 characters for readability
                                                    display_content = content[:200] + "..." if len(content) > 200 else content
                                                    print(f"   {display_content}")
                                        
                                        # Handle internal search results
                                        elif result_data.get('action') == 'internal_search' and result_data.get('results'):
                                            print(f"\n{Colors.GREEN}🔍 Internal Search Results:{Colors.END}")
                                            for i, item in enumerate(result_data['results'][:3], 1):
                                                content = item.get('content', 'No content')
                                                source = item.get('document_title', 'Unknown source')
                                                
                                                print(f"\n{Colors.BOLD}{i}. {source}{Colors.END}")
                                                if content and content != 'No content':
                                                    formatted_content = content[:150] + "..." if len(content) > 150 else content
                                                    print(f"   {formatted_content}")
                                        
                                        # Handle knowledge graph results
                                        elif result_data.get('action') == 'knowledge_graph_search' and result_data.get('graph_results'):
                                            print(f"\n{Colors.MAGENTA}🧠 Knowledge Graph Results:{Colors.END}")
                                            for i, item in enumerate(result_data['graph_results'][:3], 1):
                                                fact = item.get('fact', 'No fact')
                                                
                                                print(f"\n{Colors.BOLD}{i}. Knowledge Fact{Colors.END}")
                                                if fact and fact != 'No fact':
                                                    formatted_fact = fact[:150] + "..." if len(fact) > 150 else fact
                                                    print(f"   {formatted_fact}")
                                        
                                        # Handle other actions
                                        elif result_data.get('action'):
                                            print(f"  📋 Action: {result_data['action']}")
                                            if result_data.get('fallback_message'):
                                                print(f"       Note: {result_data['fallback_message']}")
                                else:
                                    print(f"❌ Error: {execution_result.get('error', 'Unknown error')}")
                                
                            else:
                                error_text = await response.text()
                                print(f"❌ Error: {response.status}")
                                print(f"Response: {error_text}")
                                
                    except Exception as e:
                        print(f"❌ Smart Agent Error: {e}")
                        # Fallback to traditional chat
                        print("Falling back to traditional chat...")
                        await self.stream_chat(user_input)
                
                except KeyboardInterrupt:
                    print(f"\n{Colors.CYAN}👋 Goodbye!{Colors.END}")
                    break
                except EOFError:
                    print(f"\n{Colors.CYAN}👋 Goodbye!{Colors.END}")
                    break
        
        except Exception as e:
            print(f"{Colors.RED}✗ CLI error: {e}{Colors.END}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="CLI for Agentic RAG with Knowledge Graph",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--url',
        default='http://localhost:8058',
        help='Base URL for the API (default: http://localhost:8058)'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        help='Port number (overrides URL port)'
    )
    
    args = parser.parse_args()
    
    # Build base URL
    base_url = args.url
    if args.port:
        # Extract host from URL and use provided port
        if '://' in base_url:
            protocol, rest = base_url.split('://', 1)
            host = rest.split(':')[0].split('/')[0]
            base_url = f"{protocol}://{host}:{args.port}"
        else:
            base_url = f"http://localhost:{args.port}"
    
    # Create and run CLI
    cli = AgenticRAGCLI(base_url)
    
    try:
        asyncio.run(cli.run())
    except KeyboardInterrupt:
        print(f"\n{Colors.CYAN}👋 Goodbye!{Colors.END}")
    except Exception as e:
        print(f"{Colors.RED}✗ CLI startup error: {e}{Colors.END}")
        sys.exit(1)


if __name__ == "__main__":
    main()