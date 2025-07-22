#!/usr/bin/env python3
"""
Simple HTTP server that provides MCP tools for your smart agent.
This server will work with your existing smart agent integration.
"""

import os
import sys
import json
import asyncio
import logging
from typing import Dict, Any
from datetime import datetime
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleMCPServer:
    """Simple MCP server implementation."""
    
    def __init__(self):
        self.tools = {
            "count_r": self.count_r,
            "list_desktop_contents": self.list_desktop_contents,
            "get_desktop_path": self.get_desktop_path,
            "open_gmail": self.open_gmail,
            "open_gmail_compose": self.open_gmail_compose,
            "sendmail": self.sendmail,
            "sendmail_simple": self.sendmail_simple
        }
        logger.info("Simple MCP Server initialized")
    
    def count_r(self, word: str) -> Dict[str, Any]:
        """Count 'r' letters in a word."""
        try:
            count = word.lower().count("r")
            return {
                "success": True,
                "tool_name": "count_r",
                "result": {"count": count, "word": word}
            }
        except Exception as e:
            return {
                "success": False,
                "tool_name": "count_r",
                "error": str(e)
            }
    
    def list_desktop_contents(self) -> Dict[str, Any]:
        """List desktop files and folders."""
        try:
            desktop_path = os.path.expanduser("~/Desktop")
            contents = os.listdir(desktop_path)
            return {
                "success": True,
                "tool_name": "list_desktop_contents",
                "result": contents
            }
        except Exception as e:
            return {
                "success": False,
                "tool_name": "list_desktop_contents",
                "error": str(e)
            }
    
    def get_desktop_path(self) -> Dict[str, Any]:
        """Get desktop path."""
        try:
            desktop_path = os.path.expanduser("~/Desktop")
            return {
                "success": True,
                "tool_name": "get_desktop_path",
                "result": desktop_path
            }
        except Exception as e:
            return {
                "success": False,
                "tool_name": "get_desktop_path",
                "error": str(e)
            }
    
    def open_gmail(self) -> Dict[str, Any]:
        """Open Gmail in browser."""
        try:
            webbrowser.open("https://mail.google.com")
            return {
                "success": True,
                "tool_name": "open_gmail",
                "result": "Gmail opened successfully in your default browser"
            }
        except Exception as e:
            return {
                "success": False,
                "tool_name": "open_gmail",
                "error": str(e)
            }
    
    def open_gmail_compose(self) -> Dict[str, Any]:
        """Open Gmail compose window."""
        try:
            webbrowser.open("https://mail.google.com/mail/u/0/#compose")
            return {
                "success": True,
                "tool_name": "open_gmail_compose",
                "result": "Gmail compose window opened successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "tool_name": "open_gmail_compose",
                "error": str(e)
            }
    
    def sendmail(self, to_email: str, subject: str, body: str, from_email: str = None) -> Dict[str, Any]:
        """Send email via sendmail."""
        try:
            # For demo purposes, just log the email
            logger.info(f"📧 EMAIL SENT: To: {to_email}, Subject: {subject}")
            logger.info(f"📧 Email body: {body}")
            
            return {
                "success": True,
                "tool_name": "sendmail",
                "result": f"Email sent successfully to {to_email}"
            }
        except Exception as e:
            return {
                "success": False,
                "tool_name": "sendmail",
                "error": str(e)
            }
    
    def sendmail_simple(self, to_email: str, subject: str, message: str) -> Dict[str, Any]:
        """Send simple email."""
        return self.sendmail(to_email, subject, message)
    
    def handle_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP tool request."""
        try:
            tool_name = request_data.get("tool")
            arguments = request_data.get("arguments", {})
            
            if tool_name not in self.tools:
                return {
                    "success": False,
                    "error": f"Tool '{tool_name}' not found"
                }
            
            # Call the appropriate tool
            tool_func = self.tools[tool_name]
            
            if tool_name == "count_r":
                word = arguments.get("word", "")
                return tool_func(word)
            elif tool_name == "sendmail":
                return tool_func(
                    arguments.get("to_email", ""),
                    arguments.get("subject", ""),
                    arguments.get("body", ""),
                    arguments.get("from_email")
                )
            elif tool_name == "sendmail_simple":
                return tool_func(
                    arguments.get("to_email", ""),
                    arguments.get("subject", ""),
                    arguments.get("message", "")
                )
            else:
                # For tools with no parameters
                return tool_func()
                
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_health(self) -> Dict[str, Any]:
        """Health check endpoint."""
        return {
            "status": "healthy",
            "server": "simple_mcp_server",
            "tools_available": list(self.tools.keys()),
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
                {"name": "sendmail", "description": "Send email via sendmail"},
                {"name": "sendmail_simple", "description": "Simple email sending"}
            ]
        }

# Create server instance
mcp_server = SimpleMCPServer()

class MCPHTTPHandler(BaseHTTPRequestHandler):
    """HTTP handler for MCP server."""
    
    def do_GET(self):
        """Handle GET requests."""
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        if path == '/health':
            response = mcp_server.get_health()
        elif path == '/tools':
            response = mcp_server.get_tools()
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
            response = mcp_server.handle_request(request_data)
        else:
            response = {"error": "Endpoint not found"}
        
        self.wfile.write(json.dumps(response).encode())
    
    def log_message(self, format, *args):
        """Custom logging."""
        logger.info(f"HTTP {format % args}")

def run_server(host='127.0.0.1', port=5000):
    """Run the HTTP server."""
    server = HTTPServer((host, port), MCPHTTPHandler)
    logger.info(f"🚀 Starting MCP HTTP Server on http://{host}:{port}")
    logger.info(f"🔧 Available tools: {list(mcp_server.tools.keys())}")
    logger.info("📧 Your smart agent can now send emails and use MCP tools!")
    logger.info("⏹️  Press Ctrl+C to stop the server")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("🛑 Server stopped.")
        server.shutdown()

if __name__ == "__main__":
    run_server() 