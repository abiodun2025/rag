#!/usr/bin/env python3
"""
Test MCP Bridge for Pull Request Operations (No GitHub credentials required)
"""

import json
import logging
import os
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestMCPBridge:
    def __init__(self):
        self.pr_counter = 1
        logger.info("Test MCP Bridge initialized - no GitHub credentials required")

    def call_tool(self, tool_name: str, arguments: dict) -> dict:
        """Call test tool."""
        try:
            if tool_name == "create_pull_request":
                return self._create_pull_request(arguments)
            elif tool_name == "list_pull_requests":
                return self._list_pull_requests(arguments)
            elif tool_name == "merge_pull_request":
                return self._merge_pull_request(arguments)
            elif tool_name == "generate_report":
                return self._generate_report(arguments)
            elif tool_name == "create_local_url":
                return self._create_local_url(arguments)
            elif tool_name == "save_report":
                return self._save_report(arguments)
            else:
                return {
                    "success": False,
                    "tool_name": tool_name,
                    "error": f"Tool '{tool_name}' not found"
                }
        except Exception as e:
            return {
                "success": False,
                "tool_name": tool_name,
                "error": f"Failed to execute {tool_name}: {str(e)}"
            }

    def _create_pull_request(self, arguments: dict) -> dict:
        """Simulate creating a pull request."""
        try:
            title = arguments.get("title", "Test Pull Request")
            description = arguments.get("description", "Test PR created via MCP Bridge")
            source_branch = arguments.get("source_branch", "feature/test")
            target_branch = arguments.get("target_branch", "main")
            
            # Simulate API delay
            time.sleep(1)
            
            pr_number = self.pr_counter
            self.pr_counter += 1
            
            return {
                "success": True,
                "tool_name": "create_pull_request",
                "result": f"Pull request created successfully",
                "pr_id": pr_number,
                "pr_number": pr_number,
                "pr_url": f"https://github.com/test/test-repo/pull/{pr_number}",
                "pr_title": title,
                "source_branch": source_branch,
                "target_branch": target_branch,
                "description": description
            }
                
        except Exception as e:
            return {
                "success": False,
                "tool_name": "create_pull_request",
                "error": f"Failed to create pull request: {str(e)}"
            }

    def _list_pull_requests(self, arguments: dict) -> dict:
        """Simulate listing pull requests."""
        try:
            # Simulate API delay
            time.sleep(0.5)
            
            # Return mock PRs
            mock_prs = [
                {
                    "number": 1,
                    "title": "Test PR 1",
                    "state": "open",
                    "html_url": "https://github.com/test/test-repo/pull/1"
                },
                {
                    "number": 2,
                    "title": "Test PR 2", 
                    "state": "closed",
                    "html_url": "https://github.com/test/test-repo/pull/2"
                }
            ]
            
            return {
                "success": True,
                "tool_name": "list_pull_requests",
                "result": f"Found {len(mock_prs)} pull requests",
                "pull_requests": mock_prs
            }
                
        except Exception as e:
            return {
                "success": False,
                "tool_name": "list_pull_requests",
                "error": f"Failed to list pull requests: {str(e)}"
            }

    def _merge_pull_request(self, arguments: dict) -> dict:
        """Simulate merging a pull request."""
        try:
            pr_number = arguments.get("pr_number")
            if not pr_number:
                return {
                    "success": False,
                    "tool_name": "merge_pull_request",
                    "error": "PR number is required"
                }
            
            # Simulate API delay
            time.sleep(1)
            
            return {
                "success": True,
                "tool_name": "merge_pull_request",
                "result": f"Pull request #{pr_number} merged successfully",
                "pr_number": pr_number,
                "merged_at": datetime.now().isoformat()
            }
                
        except Exception as e:
            return {
                "success": False,
                "tool_name": "merge_pull_request",
                "error": f"Failed to merge pull request: {str(e)}"
            }

    def _generate_report(self, arguments: dict) -> dict:
        """Simulate generating a report."""
        try:
            report_type = arguments.get("type", "general")
            content = arguments.get("content", "Test report content")
            
            # Simulate processing delay
            time.sleep(0.5)
            
            return {
                "success": True,
                "tool_name": "generate_report",
                "result": f"Report generated successfully",
                "report_type": report_type,
                "content": content,
                "generated_at": datetime.now().isoformat()
            }
                
        except Exception as e:
            return {
                "success": False,
                "tool_name": "generate_report",
                "error": f"Failed to generate report: {str(e)}"
            }

    def _create_local_url(self, arguments: dict) -> dict:
        """Simulate creating a local URL."""
        try:
            content = arguments.get("content", "Test content")
            filename = f"report_{int(time.time())}.html"
            
            return {
                "success": True,
                "tool_name": "create_local_url",
                "result": f"Local URL created successfully",
                "url": f"file:///tmp/{filename}",
                "filename": filename
            }
                
        except Exception as e:
            return {
                "success": False,
                "tool_name": "create_local_url",
                "error": f"Failed to create local URL: {str(e)}"
            }

    def _save_report(self, arguments: dict) -> dict:
        """Simulate saving a report."""
        try:
            content = arguments.get("content", "Test report")
            filename = arguments.get("filename", f"report_{int(time.time())}.txt")
            
            return {
                "success": True,
                "tool_name": "save_report",
                "result": f"Report saved successfully",
                "filename": filename,
                "saved_at": datetime.now().isoformat()
            }
                
        except Exception as e:
            return {
                "success": False,
                "tool_name": "save_report",
                "error": f"Failed to save report: {str(e)}"
            }

    def get_health(self) -> dict:
        """Get health status."""
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "service": "test_mcp_bridge",
            "version": "1.0.0"
        }

    def get_tools(self) -> dict:
        """Get available tools."""
        return {
            "tools": [
                {"name": "create_pull_request", "description": "Create a pull request (test mode)"},
                {"name": "list_pull_requests", "description": "List pull requests (test mode)"},
                {"name": "merge_pull_request", "description": "Merge a pull request (test mode)"},
                {"name": "generate_report", "description": "Generate a report (test mode)"},
                {"name": "create_local_url", "description": "Create a local URL for a report (test mode)"},
                {"name": "save_report", "description": "Save a report to local storage (test mode)"}
            ]
        }

# Create bridge instance
bridge = TestMCPBridge()

class TestMCPHandler(BaseHTTPRequestHandler):
    """HTTP handler for Test MCP bridge."""
    
    def do_GET(self):
        """Handle GET requests."""
        try:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            if self.path == '/health':
                response = bridge.get_health()
            elif self.path == '/tools':
                response = bridge.get_tools()
            else:
                response = {"error": "Endpoint not found"}
            
            self.wfile.write(json.dumps(response).encode())
        except Exception as e:
            logger.error(f"GET request error: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
    
    def do_POST(self):
        """Handle POST requests."""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            try:
                request_data = json.loads(post_data.decode('utf-8'))
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")
                request_data = {}
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            if self.path == '/call':
                tool_name = request_data.get("tool")
                arguments = request_data.get("arguments", {})
                
                if not tool_name:
                    response = {"error": "No tool name provided"}
                else:
                    response = bridge.call_tool(tool_name, arguments)
            else:
                response = {"error": "Endpoint not found"}
            
            self.wfile.write(json.dumps(response).encode())
        except Exception as e:
            logger.error(f"POST request error: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
    
    def log_message(self, format, *args):
        """Custom logging."""
        logger.info(f"HTTP {format % args}")

def run_bridge(host='127.0.0.1', port=5000):
    """Run the Test MCP bridge."""
    try:
        server = HTTPServer((host, port), TestMCPHandler)
        logger.info(f"🚀 Starting Test MCP Bridge on http://{host}:{port}")
        logger.info("🧪 Running in TEST MODE - no GitHub credentials required")
        logger.info("⏹️  Press Ctrl+C to stop the bridge")
        
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("🛑 Bridge stopped by user.")
        server.shutdown()
    except Exception as e:
        logger.error(f"🛑 Bridge failed to start: {e}")
        raise

if __name__ == "__main__":
    run_bridge() 