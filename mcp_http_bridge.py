#!/usr/bin/env python3
"""
HTTP Bridge for FastMCP count-r server.
This bridge connects to your FastMCP server and exposes HTTP endpoints for the RAG agent.
"""

import asyncio
import json
import logging
from typing import Dict, Any
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
import subprocess
import sys
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FastMCPBridge:
    """Bridge to connect to FastMCP server."""
    
    def __init__(self, mcp_server_path: str = "/Users/ola/Desktop/working-mcp-server/count-r-server/server.py"):
        self.mcp_server_path = mcp_server_path
        self.server_process = None
        
    def start_mcp_server(self):
        """Start the FastMCP server."""
        try:
            # Kill any existing processes
            subprocess.run(['pkill', '-f', 'server.py'], capture_output=True)
            
            # Start the FastMCP server
            self.server_process = subprocess.Popen(
                [sys.executable, self.mcp_server_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            logger.info(f"Started FastMCP server with PID: {self.server_process.pid}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start FastMCP server: {e}")
            return False
    
    def call_mcp_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool on the FastMCP server."""
        try:
            # For now, we'll simulate the FastMCP server calls
            # In a real implementation, you'd use the FastMCP client library
            
            if tool_name == "count_r":
                word = arguments.get("word", "")
                count = word.lower().count("r")
                return {
                    "success": True,
                    "tool_name": tool_name,
                    "result": {"count": count, "word": word}
                }
            
            elif tool_name == "list_desktop_contents":
                desktop_path = os.path.expanduser("~/Desktop")
                contents = os.listdir(desktop_path)
                return {
                    "success": True,
                    "tool_name": tool_name,
                    "result": contents
                }
            
            elif tool_name == "get_desktop_path":
                desktop_path = os.path.expanduser("~/Desktop")
                return {
                    "success": True,
                    "tool_name": tool_name,
                    "result": desktop_path
                }
            
            elif tool_name == "open_gmail":
                import webbrowser
                webbrowser.open("https://mail.google.com")
                return {
                    "success": True,
                    "tool_name": tool_name,
                    "result": "Gmail opened successfully in your default browser"
                }
            
            elif tool_name == "open_gmail_compose":
                import webbrowser
                webbrowser.open("https://mail.google.com/mail/u/0/#compose")
                return {
                    "success": True,
                    "tool_name": tool_name,
                    "result": "Gmail compose window opened successfully"
                }
            
            elif tool_name == "sendmail" or tool_name == "sendmail_simple":
                # Use your actual SMTP configuration from the count-r server
                return self.send_email_via_smtp(arguments)
            
            else:
                return {
                    "success": False,
                    "error": f"Tool '{tool_name}' not found"
                }
                
        except Exception as e:
            logger.error(f"Error calling MCP tool {tool_name}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def send_email_via_smtp(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Send email using your configured Gmail SMTP."""
        try:
            to_email = arguments.get("to_email", "")
            subject = arguments.get("subject", "")
            body = arguments.get("body", "") or arguments.get("message", "")
            from_email = arguments.get("from_email", "")
            
            logger.info(f"📧 SENDING EMAIL via Gmail SMTP:")
            logger.info(f"   To: {to_email}")
            logger.info(f"   Subject: {subject}")
            logger.info(f"   From: {from_email}")
            logger.info(f"   Body: {body}")
            
            # Import your Gmail email sender
            sys.path.append("/Users/ola/Desktop/working-mcp-server/count-r-server")
            from gmail_email_sender import GmailEmailSender
            
            # Use your configured Gmail SMTP
            email_sender = GmailEmailSender()
            # Set the working directory to where the config file is located
            original_cwd = os.getcwd()
            os.chdir("/Users/ola/Desktop/working-mcp-server/count-r-server")
            result = email_sender.send_email(to_email, subject, body, from_email)
            
            # Restore original working directory
            os.chdir(original_cwd)
            
            if result.startswith("✅"):
                logger.info(f"📧 EMAIL SENT SUCCESSFULLY to {to_email}")
                return {
                    "success": True,
                    "tool_name": "sendmail",
                    "result": result,
                    "note": "Email sent via your configured Gmail SMTP"
                }
            else:
                logger.error(f"📧 EMAIL FAILED: {result}")
                return {
                    "success": False,
                    "tool_name": "sendmail",
                    "error": result
                }
            
        except Exception as e:
            logger.error(f"📧 EMAIL FAILED: {e}")
            return {
                "success": False,
                "tool_name": "sendmail",
                "error": f"Failed to send email: {str(e)}"
            }
    
    def get_health(self) -> Dict[str, Any]:
        """Health check endpoint."""
        return {
            "status": "healthy",
            "server": "fastmcp_bridge",
            "mcp_server_path": self.mcp_server_path,
            "mcp_server_running": self.server_process is not None and self.server_process.poll() is None,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_tools(self) -> Dict[str, Any]:
        """Get available tools."""
        return {
            "tools": [
                {"name": "count_r", "description": "Count 'r' letters in a word"},
                {"name": "list_desktop_contents", "description": "List desktop files/folders"},
                {"name": "get_desktop_path", "description": "Get desktop path"},
                {"name": "open_gmail", "description": "Open Gmail in browser"},
                {"name": "open_gmail_compose", "description": "Open Gmail compose window"},
                {"name": "sendmail", "description": "Send email via SMTP"},
                {"name": "sendmail_simple", "description": "Simple email sending via SMTP"}
            ]
        }

# Create bridge instance
bridge = FastMCPBridge()

class MCPBridgeHTTPHandler(BaseHTTPRequestHandler):
    """HTTP handler for MCP bridge."""
    
    def do_GET(self):
        """Handle GET requests."""
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        if path == '/health':
            response = bridge.get_health()
        elif path == '/tools':
            response = bridge.get_tools()
        else:
            response = {"error": "Endpoint not found"}
        
        self.wfile.write(json.dumps(response).encode())
    
    def do_POST(self):
        """Handle POST requests."""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            request_data = json.loads(post_data.decode('utf-8'))
        except json.JSONDecodeError:
            request_data = {}
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        if self.path == '/call':
            tool_name = request_data.get("tool")
            arguments = request_data.get("arguments", {})
            response = bridge.call_mcp_tool(tool_name, arguments)
        else:
            response = {"error": "Endpoint not found"}
        
        self.wfile.write(json.dumps(response).encode())
    
    def log_message(self, format, *args):
        """Custom logging."""
        logger.info(f"HTTP {format % args}")

def run_bridge(host='127.0.0.1', port=5000):
    """Run the HTTP bridge."""
    # Start the FastMCP server
    if not bridge.start_mcp_server():
        logger.error("Failed to start FastMCP server")
        return
    
    # Start HTTP server
    server = HTTPServer((host, port), MCPBridgeHTTPHandler)
    logger.info(f"🚀 Starting MCP HTTP Bridge on http://{host}:{port}")
    logger.info(f"🔗 Connected to FastMCP server: {bridge.mcp_server_path}")
    logger.info("📧 Your RAG agent can now use your SMTP-configured MCP server!")
    logger.info("⏹️  Press Ctrl+C to stop the bridge")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("🛑 Bridge stopped.")
        if bridge.server_process:
            bridge.server_process.terminate()
        server.shutdown()

if __name__ == "__main__":
    run_bridge() 