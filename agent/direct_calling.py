"""
Direct Calling Integration for Smart Agent
Uses MCP server for actual phone calls
"""

import httpx
import asyncio
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class DirectCaller:
    """Direct calling service using MCP server."""
    
    def __init__(self, mcp_server_url: str = "http://127.0.0.1:5000"):
        self.mcp_server_url = mcp_server_url
        self.client = httpx.AsyncClient(timeout=30.0)
        
    async def make_call(self, phone_number: str, caller_name: str = "Smart Agent", service: str = "google_voice") -> Dict[str, Any]:
        """
        Make a direct call using MCP server.
        
        Args:
            phone_number: Phone number to call
            caller_name: Name of the caller
            service: Calling service (google_voice, whatsapp, twilio)
            
        Returns:
            Dictionary with call result
        """
        try:
            # Check if MCP server is running
            health_check = await self._check_health()
            if not health_check["success"]:
                return {
                    "success": False,
                    "error": "MCP server not available",
                    "note": "Please start the MCP server first: python simple_mcp_bridge.py"
                }
            
            # Make the call via MCP server
            call_data = {
                "tool": "call_phone",
                "arguments": {
                    "phone_number": phone_number,
                    "caller_name": caller_name,
                    "service": service
                }
            }
            
            response = await self.client.post(
                f"{self.mcp_server_url}/call",
                json=call_data
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "phone_number": phone_number,
                    "method": service,
                    "call_id": result.get("call_id"),
                    "status": result.get("status"),
                    "message": result.get("result", "Call initiated"),
                    "instructions": result.get("instructions", []),
                    "note": result.get("note", "Call processed via MCP server")
                }
            else:
                return {
                    "success": False,
                    "error": f"MCP server error: {response.status_code}",
                    "note": "Failed to make call via MCP server"
                }
                
        except Exception as e:
            logger.error(f"Direct calling failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "note": "Failed to connect to MCP server"
            }
    
    async def check_call_status(self, call_id: str) -> Dict[str, Any]:
        """Check the status of a call."""
        try:
            response = await self.client.post(
                f"{self.mcp_server_url}/call",
                json={"action": "status", "call_id": call_id}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "success": False,
                    "error": f"Status check failed: {response.status_code}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def end_call(self, call_id: str) -> Dict[str, Any]:
        """End a call."""
        try:
            response = await self.client.post(
                f"{self.mcp_server_url}/call",
                json={"action": "end", "call_id": call_id}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "success": False,
                    "error": f"End call failed: {response.status_code}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _check_health(self) -> Dict[str, Any]:
        """Check if MCP server is healthy."""
        try:
            response = await self.client.get(f"{self.mcp_server_url}/health")
            if response.status_code == 200:
                return {"success": True, "status": "healthy"}
            else:
                return {"success": False, "status": "unhealthy"}
        except:
            return {"success": False, "status": "unreachable"}
    
    async def get_available_services(self) -> Dict[str, Any]:
        """Get available calling services."""
        try:
            response = await self.client.get(f"{self.mcp_server_url}/tools")
            if response.status_code == 200:
                return response.json()
            else:
                return {"success": False, "error": "Failed to get tools"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

# Global instance
direct_caller = DirectCaller() 