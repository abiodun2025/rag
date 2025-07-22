"""
MCP (Model Context Protocol) tools integration for the agentic RAG system.
Connects to the count-r MCP server running on localhost:5000.
"""

import os
import asyncio
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import httpx
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# MCP Server Configuration
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://127.0.0.1:5000")
MCP_SERVER_NAME = os.getenv("MCP_SERVER_NAME", "count-r-server")

class MCPClient:
    """Client for connecting to the count-r MCP server."""
    
    def __init__(self, base_url: str = MCP_SERVER_URL):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
        self.connected = False
        self.available_tools = []
    
    async def connect(self) -> bool:
        """Connect to the MCP server and discover available tools."""
        try:
            # Test connection
            response = await self.client.get(f"{self.base_url}/health")
            if response.status_code == 200:
                self.connected = True
                logger.info(f"Connected to MCP server: {self.base_url}")
                
                # Discover available tools
                await self.discover_tools()
                return True
            else:
                logger.error(f"MCP server health check failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to connect to MCP server: {e}")
            return False
    
    async def discover_tools(self) -> List[Dict[str, Any]]:
        """Discover available tools from the MCP server."""
        try:
            # Try to get tools list from the server
            response = await self.client.get(f"{self.base_url}/tools")
            if response.status_code == 200:
                self.available_tools = response.json()
                logger.info(f"Discovered {len(self.available_tools)} tools from MCP server")
            else:
                # Fallback: define known tools based on server documentation
                self.available_tools = [
                    {
                        "name": "count_r",
                        "description": "Count 'r' letters in a word",
                        "parameters": {"word": {"type": "string", "description": "Word to count 'r' letters in"}}
                    },
                    {
                        "name": "list_desktop_contents",
                        "description": "List desktop files/folders",
                        "parameters": {"random_string": {"type": "string", "description": "Dummy parameter for no-parameter tools"}}
                    },
                    {
                        "name": "get_desktop_path",
                        "description": "Get desktop path",
                        "parameters": {"random_string": {"type": "string", "description": "Dummy parameter for no-parameter tools"}}
                    },
                    {
                        "name": "open_gmail",
                        "description": "Open Gmail in browser",
                        "parameters": {"random_string": {"type": "string", "description": "Dummy parameter for no-parameter tools"}}
                    },
                    {
                        "name": "open_gmail_compose",
                        "description": "Open Gmail compose window",
                        "parameters": {"random_string": {"type": "string", "description": "Dummy parameter for no-parameter tools"}}
                    },
                    {
                        "name": "sendmail",
                        "description": "Send email via sendmail",
                        "parameters": {
                            "to_email": {"type": "string", "description": "Recipient email address"},
                            "subject": {"type": "string", "description": "Email subject"},
                            "body": {"type": "string", "description": "Email body content"},
                            "from_email": {"type": "string", "description": "Sender email address (optional)"}
                        }
                    },
                    {
                        "name": "sendmail_simple",
                        "description": "Simple email sending",
                        "parameters": {
                            "to_email": {"type": "string", "description": "Recipient email address"},
                            "subject": {"type": "string", "description": "Email subject"},
                            "message": {"type": "string", "description": "Email message"}
                        }
                    }
                ]
                logger.info(f"Using fallback tool definitions: {len(self.available_tools)} tools")
            
            return self.available_tools
            
        except Exception as e:
            logger.error(f"Failed to discover tools: {e}")
            return []
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a specific tool on the MCP server."""
        if not self.connected:
            await self.connect()
        
        try:
            # Prepare the request payload
            payload = {
                "tool": tool_name,
                "arguments": arguments
            }
            
            # Make the request to the MCP server
            response = await self.client.post(
                f"{self.base_url}/call",
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.debug(f"MCP tool '{tool_name}' called successfully")
                return {
                    "success": True,
                    "tool_name": tool_name,
                    "result": result
                }
            else:
                logger.error(f"MCP tool '{tool_name}' failed: {response.status_code}")
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "tool_name": tool_name
                }
                
        except Exception as e:
            logger.error(f"MCP tool '{tool_name}' call failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool_name": tool_name
            }
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

# Initialize MCP client
mcp_client = MCPClient()

# Tool Input Models
class CountRInput(BaseModel):
    """Input for count_r tool."""
    word: str = Field(..., description="Word to count 'r' letters in")

class DesktopContentsInput(BaseModel):
    """Input for list_desktop_contents tool."""
    random_string: str = Field(default="dummy", description="Dummy parameter for no-parameter tools")

class DesktopPathInput(BaseModel):
    """Input for get_desktop_path tool."""
    random_string: str = Field(default="dummy", description="Dummy parameter for no-parameter tools")

class OpenGmailInput(BaseModel):
    """Input for open_gmail tool."""
    random_string: str = Field(default="dummy", description="Dummy parameter for no-parameter tools")

class OpenGmailComposeInput(BaseModel):
    """Input for open_gmail_compose tool."""
    random_string: str = Field(default="dummy", description="Dummy parameter for no-parameter tools")

class SendmailInput(BaseModel):
    """Input for sendmail tool."""
    to_email: str = Field(..., description="Recipient email address")
    subject: str = Field(..., description="Email subject")
    body: str = Field(..., description="Email body content")
    from_email: str = Field("", description="Sender email address (optional, leave empty for default)")

class SendmailSimpleInput(BaseModel):
    """Input for sendmail_simple tool."""
    to_email: str = Field(..., description="Recipient email address")
    subject: str = Field(..., description="Email subject")
    message: str = Field(..., description="Email message")

class MCPToolInput(BaseModel):
    """Generic input for any MCP tool."""
    tool_name: str = Field(..., description="Name of the MCP tool to call")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Tool parameters")

# Tool Functions
async def count_r_tool(input_data: CountRInput) -> Dict[str, Any]:
    """Count 'r' letters in a word using MCP server."""
    return await mcp_client.call_tool("count_r", {"word": input_data.word})

async def list_desktop_contents_tool(input_data: DesktopContentsInput) -> Dict[str, Any]:
    """List desktop files/folders using MCP server."""
    return await mcp_client.call_tool("list_desktop_contents", {"random_string": input_data.random_string})

async def get_desktop_path_tool(input_data: DesktopPathInput) -> Dict[str, Any]:
    """Get desktop path using MCP server."""
    return await mcp_client.call_tool("get_desktop_path", {"random_string": input_data.random_string})

async def open_gmail_tool(input_data: OpenGmailInput) -> Dict[str, Any]:
    """Open Gmail in browser using MCP server."""
    return await mcp_client.call_tool("open_gmail", {"random_string": input_data.random_string})

async def open_gmail_compose_tool(input_data: OpenGmailComposeInput) -> Dict[str, Any]:
    """Open Gmail compose window using MCP server."""
    return await mcp_client.call_tool("open_gmail_compose", {"random_string": input_data.random_string})

async def sendmail_tool(input_data: SendmailInput) -> Dict[str, Any]:
    """Send email via sendmail using MCP server."""
    params = {
        "to_email": input_data.to_email,
        "subject": input_data.subject,
        "body": input_data.body
    }
    if input_data.from_email:
        params["from_email"] = input_data.from_email
    return await mcp_client.call_tool("sendmail", params)

async def sendmail_simple_tool(input_data: SendmailSimpleInput) -> Dict[str, Any]:
    """Simple email sending using MCP server."""
    return await mcp_client.call_tool("sendmail_simple", {
        "to_email": input_data.to_email,
        "subject": input_data.subject,
        "message": input_data.message
    })

async def generic_mcp_tool(input_data: MCPToolInput) -> Dict[str, Any]:
    """Generic MCP tool wrapper for any tool."""
    return await mcp_client.call_tool(input_data.tool_name, input_data.parameters)

async def list_mcp_tools() -> Dict[str, Any]:
    """List all available MCP tools."""
    try:
        tools = await mcp_client.discover_tools()
        return {
            "success": True,
            "server_url": MCP_SERVER_URL,
            "server_name": MCP_SERVER_NAME,
            "tools_count": len(tools),
            "tools": tools
        }
    except Exception as e:
        logger.error(f"Failed to list MCP tools: {e}")
        return {
            "success": False,
            "error": str(e)
        } 