#!/usr/bin/env python3
"""
MCP Calling Agent
Connects to standalone MCP server and provides calling capabilities
"""

import asyncio
import json
import httpx
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import time
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class CallResult:
    """Result of a calling operation"""
    success: bool
    call_id: Optional[str] = None
    duration: Optional[float] = None
    status: Optional[str] = None
    error_message: Optional[str] = None
    timestamp: str = None

class MCPCallingAgent:
    """Agent for making calls using MCP server tools"""
    
    def __init__(self, mcp_server_url: str = "http://127.0.0.1:5000"):
        self.mcp_server_url = mcp_server_url
        self.client = httpx.AsyncClient(timeout=60.0)  # Longer timeout for calls
        self.available_tools = []
        self.calling_tools = []
        self.session_id = f"calling_session_{int(time.time())}"
        
    async def connect_to_server(self) -> bool:
        """Connect to MCP server and discover calling tools"""
        try:
            # Check server health
            response = await self.client.get(f"{self.mcp_server_url}/health")
            if response.status_code != 200:
                logger.error(f"❌ MCP server health check failed: {response.status_code}")
                return False
            
            # Get available tools
            response = await self.client.get(f"{self.mcp_server_url}/tools")
            if response.status_code == 200:
                data = response.json()
                tools = data.get("tools", []) if isinstance(data, dict) else data
                self.available_tools = tools
                
                # Find calling-related tools
                self.calling_tools = [
                    tool for tool in tools 
                    if any(keyword in tool.get("name", "").lower() 
                          for keyword in ["call", "phone", "dial", "voice"])
                ]
                
                logger.info(f"✅ Connected to MCP server: {self.mcp_server_url}")
                logger.info(f"📋 Found {len(tools)} total tools")
                logger.info(f"📞 Found {len(self.calling_tools)} calling tools")
                
                for tool in self.calling_tools:
                    logger.info(f"   - {tool.get('name')}: {tool.get('description')}")
                
                return True
            else:
                logger.error(f"❌ Failed to get tools: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to connect to MCP server: {e}")
            return False
    
    async def call_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Call a specific tool on the MCP server"""
        try:
            payload = {
                "tool": tool_name,
                "arguments": params
            }
            
            logger.info(f"📞 Calling MCP tool: {tool_name}")
            logger.debug(f"   Parameters: {params}")
            
            response = await self.client.post(
                f"{self.mcp_server_url}/call",
                json=payload,
                timeout=60.0
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ {tool_name} call successful")
                return result
            else:
                logger.error(f"❌ {tool_name} call failed: HTTP {response.status_code}")
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            logger.error(f"❌ Error calling {tool_name}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def make_call(self, phone_number: str, caller_name: str = None) -> CallResult:
        """Make a phone call using available calling tools"""
        timestamp = datetime.now().isoformat()
        
        try:
            # Try different calling tool names
            calling_tool_names = ["call_phone", "make_call", "dial_number", "phone_call"]
            
            for tool_name in calling_tool_names:
                # Check if this tool exists
                tool_exists = any(tool.get("name") == tool_name for tool in self.available_tools)
                
                if tool_exists:
                    logger.info(f"📞 Attempting to make call using {tool_name}")
                    
                    # Prepare parameters based on tool name
                    if tool_name == "call_phone":
                        params = {
                            "phone_number": phone_number,
                            "caller_name": caller_name or "MCP Agent"
                        }
                    elif tool_name == "make_call":
                        params = {
                            "number": phone_number,
                            "name": caller_name or "MCP Agent"
                        }
                    elif tool_name == "dial_number":
                        params = {
                            "phone_number": phone_number
                        }
                    else:
                        params = {
                            "phone_number": phone_number,
                            "caller": caller_name or "MCP Agent"
                        }
                    
                    result = await self.call_tool(tool_name, params)
                    
                    if result.get("success"):
                        return CallResult(
                            success=True,
                            call_id=result.get("call_id"),
                            status=result.get("status", "initiated"),
                            timestamp=timestamp
                        )
                    else:
                        logger.warning(f"⚠️ {tool_name} failed: {result.get('error')}")
                        continue
            
            # If no calling tools worked
            return CallResult(
                success=False,
                error_message="No working calling tools found",
                timestamp=timestamp
            )
            
        except Exception as e:
            logger.error(f"❌ Make call failed: {e}")
            return CallResult(
                success=False,
                error_message=str(e),
                timestamp=timestamp
            )
    
    async def end_call(self, call_id: str = None) -> CallResult:
        """End an active call"""
        timestamp = datetime.now().isoformat()
        
        try:
            # Try different end call tool names
            end_call_tool_names = ["end_call", "hang_up", "terminate_call", "stop_call"]
            
            for tool_name in end_call_tool_names:
                tool_exists = any(tool.get("name") == tool_name for tool in self.available_tools)
                
                if tool_exists:
                    logger.info(f"📞 Attempting to end call using {tool_name}")
                    
                    params = {"call_id": call_id} if call_id else {}
                    result = await self.call_tool(tool_name, params)
                    
                    if result.get("success"):
                        return CallResult(
                            success=True,
                            call_id=call_id,
                            status="ended",
                            timestamp=timestamp
                        )
                    else:
                        logger.warning(f"⚠️ {tool_name} failed: {result.get('error')}")
                        continue
            
            return CallResult(
                success=False,
                error_message="No working end call tools found",
                timestamp=timestamp
            )
            
        except Exception as e:
            logger.error(f"❌ End call failed: {e}")
            return CallResult(
                success=False,
                error_message=str(e),
                timestamp=timestamp
            )
    
    async def get_call_status(self, call_id: str) -> CallResult:
        """Get status of an active call"""
        timestamp = datetime.now().isoformat()
        
        try:
            # Try different status tool names
            status_tool_names = ["call_status", "get_call_status", "check_call"]
            
            for tool_name in status_tool_names:
                tool_exists = any(tool.get("name") == tool_name for tool in self.available_tools)
                
                if tool_exists:
                    logger.info(f"📞 Checking call status using {tool_name}")
                    
                    params = {"call_id": call_id}
                    result = await self.call_tool(tool_name, params)
                    
                    if result.get("success"):
                        return CallResult(
                            success=True,
                            call_id=call_id,
                            status=result.get("status"),
                            duration=result.get("duration"),
                            timestamp=timestamp
                        )
                    else:
                        logger.warning(f"⚠️ {tool_name} failed: {result.get('error')}")
                        continue
            
            return CallResult(
                success=False,
                error_message="No working call status tools found",
                timestamp=timestamp
            )
            
        except Exception as e:
            logger.error(f"❌ Get call status failed: {e}")
            return CallResult(
                success=False,
                error_message=str(e),
                timestamp=timestamp
            )
    
    async def list_calling_tools(self) -> Dict[str, Any]:
        """List all available calling tools"""
        return {
            "success": True,
            "server_url": self.mcp_server_url,
            "total_tools": len(self.available_tools),
            "calling_tools": self.calling_tools,
            "calling_tool_names": [tool.get("name") for tool in self.calling_tools]
        }
    
    async def test_calling_capabilities(self) -> Dict[str, Any]:
        """Test calling capabilities without making actual calls"""
        logger.info("🧪 Testing calling capabilities...")
        
        test_results = {
            "server_connected": False,
            "calling_tools_found": False,
            "available_calling_tools": [],
            "test_calls": []
        }
        
        # Test connection
        if await self.connect_to_server():
            test_results["server_connected"] = True
            test_results["calling_tools_found"] = len(self.calling_tools) > 0
            test_results["available_calling_tools"] = [
                tool.get("name") for tool in self.calling_tools
            ]
            
            # Test tool discovery for each calling tool
            for tool in self.calling_tools:
                tool_name = tool.get("name")
                test_results["test_calls"].append({
                    "tool_name": tool_name,
                    "description": tool.get("description"),
                    "available": True
                })
        
        return test_results
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

class CallingAgentCLI:
    """Interactive CLI for the calling agent"""
    
    def __init__(self, mcp_server_url: str = "http://127.0.0.1:5000"):
        self.agent = MCPCallingAgent(mcp_server_url)
    
    async def run_interactive(self):
        """Run interactive CLI"""
        print("📞 MCP Calling Agent")
        print("=" * 50)
        
        # Connect to server
        print(f"🔗 Connecting to MCP server: {self.agent.mcp_server_url}")
        if not await self.agent.connect_to_server():
            print("❌ Failed to connect to MCP server")
            return
        
        print("✅ Connected successfully!")
        
        # Show available calling tools
        calling_info = await self.agent.list_calling_tools()
        if calling_info["calling_tools_found"]:
            print(f"\n📞 Available calling tools ({len(calling_info['calling_tools'])}):")
            for tool in calling_info["calling_tools"]:
                print(f"   - {tool['name']}: {tool['description']}")
        else:
            print("\n⚠️ No calling tools found on this MCP server")
            print("   Available tools:")
            for tool in self.agent.available_tools:
                print(f"   - {tool['name']}: {tool['description']}")
        
        # Interactive menu
        while True:
            print("\n" + "=" * 50)
            print("📋 Available Commands:")
            print("1. Make a call")
            print("2. End a call")
            print("3. Check call status")
            print("4. List calling tools")
            print("5. Test calling capabilities")
            print("6. Exit")
            print("=" * 50)
            
            choice = input("\nEnter your choice (1-6): ").strip()
            
            if choice == "1":
                await self.make_call_interactive()
            elif choice == "2":
                await self.end_call_interactive()
            elif choice == "3":
                await self.check_status_interactive()
            elif choice == "4":
                await self.list_tools_interactive()
            elif choice == "5":
                await self.test_capabilities_interactive()
            elif choice == "6":
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please enter 1-6.")
    
    async def make_call_interactive(self):
        """Interactive call making"""
        print("\n📞 Make a Call")
        print("-" * 30)
        
        phone_number = input("Enter phone number: ").strip()
        if not phone_number:
            print("❌ Phone number is required")
            return
        
        caller_name = input("Enter caller name (optional): ").strip()
        if not caller_name:
            caller_name = "MCP Agent"
        
        print(f"\n📞 Making call to {phone_number} as {caller_name}...")
        result = await self.agent.make_call(phone_number, caller_name)
        
        if result.success:
            print(f"✅ Call initiated successfully!")
            print(f"   Call ID: {result.call_id}")
            print(f"   Status: {result.status}")
        else:
            print(f"❌ Call failed: {result.error_message}")
    
    async def end_call_interactive(self):
        """Interactive call ending"""
        print("\n📞 End a Call")
        print("-" * 30)
        
        call_id = input("Enter call ID (optional): ").strip()
        if not call_id:
            call_id = None
        
        print("📞 Ending call...")
        result = await self.agent.end_call(call_id)
        
        if result.success:
            print(f"✅ Call ended successfully!")
            print(f"   Call ID: {result.call_id}")
            print(f"   Status: {result.status}")
        else:
            print(f"❌ End call failed: {result.error_message}")
    
    async def check_status_interactive(self):
        """Interactive status checking"""
        print("\n📞 Check Call Status")
        print("-" * 30)
        
        call_id = input("Enter call ID: ").strip()
        if not call_id:
            print("❌ Call ID is required")
            return
        
        print(f"📞 Checking status for call {call_id}...")
        result = await self.agent.get_call_status(call_id)
        
        if result.success:
            print(f"✅ Call status retrieved!")
            print(f"   Call ID: {result.call_id}")
            print(f"   Status: {result.status}")
            print(f"   Duration: {result.duration}")
        else:
            print(f"❌ Status check failed: {result.error_message}")
    
    async def list_tools_interactive(self):
        """Interactive tool listing"""
        print("\n📞 Calling Tools")
        print("-" * 30)
        
        calling_info = await self.agent.list_calling_tools()
        
        if calling_info["calling_tools_found"]:
            print(f"Found {len(calling_info['calling_tools'])} calling tools:")
            for tool in calling_info["calling_tools"]:
                print(f"   - {tool['name']}: {tool['description']}")
        else:
            print("No calling tools found")
            print("Available tools:")
            for tool in self.agent.available_tools:
                print(f"   - {tool['name']}: {tool['description']}")
    
    async def test_capabilities_interactive(self):
        """Interactive capability testing"""
        print("\n🧪 Testing Calling Capabilities")
        print("-" * 40)
        
        test_results = await self.agent.test_calling_capabilities()
        
        print(f"Server Connected: {'✅' if test_results['server_connected'] else '❌'}")
        print(f"Calling Tools Found: {'✅' if test_results['calling_tools_found'] else '❌'}")
        
        if test_results['calling_tools_found']:
            print(f"Available calling tools: {', '.join(test_results['available_calling_tools'])}")
        else:
            print("No calling tools available on this server")

async def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="MCP Calling Agent")
    parser.add_argument("--url", default="http://127.0.0.1:5000", 
                       help="MCP server URL (default: http://127.0.0.1:5000)")
    parser.add_argument("--test", action="store_true", 
                       help="Test calling capabilities and exit")
    parser.add_argument("--call", type=str, 
                       help="Make a call to the specified phone number")
    parser.add_argument("--list", action="store_true", 
                       help="List available calling tools and exit")
    
    args = parser.parse_args()
    
    agent = MCPCallingAgent(args.url)
    
    try:
        if args.test:
            # Test capabilities
            results = await agent.test_calling_capabilities()
            print(json.dumps(results, indent=2))
            
        elif args.call:
            # Make a call
            if await agent.connect_to_server():
                result = await agent.make_call(args.call)
                print(json.dumps({
                    "success": result.success,
                    "call_id": result.call_id,
                    "status": result.status,
                    "error": result.error_message
                }, indent=2))
            else:
                print("❌ Failed to connect to MCP server")
                
        elif args.list:
            # List tools
            if await agent.connect_to_server():
                tools_info = await agent.list_calling_tools()
                print(json.dumps(tools_info, indent=2))
            else:
                print("❌ Failed to connect to MCP server")
                
        else:
            # Interactive mode
            cli = CallingAgentCLI(args.url)
            await cli.run_interactive()
            
    except Exception as e:
        logger.error(f"❌ Calling agent failed: {e}")
    finally:
        await agent.close()

if __name__ == "__main__":
    asyncio.run(main()) 