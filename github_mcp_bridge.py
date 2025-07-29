#!/usr/bin/env python3
"""
Simple GitHub MCP Bridge for Pull Request Operations
"""

import json
import logging
import os
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GitHubMCPBridge:
    def __init__(self):
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.github_owner = os.getenv('GITHUB_OWNER')
        self.github_repo = os.getenv('GITHUB_REPO')
        logger.info(f"GitHub config: owner={self.github_owner}, repo={self.github_repo}, token={'***' if self.github_token else 'None'}")

    def call_tool(self, tool_name: str, arguments: dict) -> dict:
        """Call GitHub tool."""
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
        """Create a pull request on GitHub."""
        try:
            if not all([self.github_token, self.github_owner, self.github_repo]):
                return {
                    "success": False,
                    "tool_name": "create_pull_request",
                    "error": "GitHub configuration missing. Set GITHUB_TOKEN, GITHUB_OWNER, and GITHUB_REPO environment variables."
                }
            
            title = arguments.get("title", "New Pull Request")
            description = arguments.get("description", "Pull request created via MCP Bridge")
            source_branch = arguments.get("source_branch", "main")
            target_branch = arguments.get("target_branch", "main")
            
            url = f"https://api.github.com/repos/{self.github_owner}/{self.github_repo}/pulls"
            headers = {
                "Authorization": f"token {self.github_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            data = {
                "title": title,
                "body": description,
                "head": source_branch,
                "base": target_branch
            }
            
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 201:
                pr_data = response.json()
                return {
                    "success": True,
                    "tool_name": "create_pull_request",
                    "result": f"Pull request created successfully",
                    "pr_id": pr_data["id"],
                    "pr_number": pr_data["number"],
                    "pr_url": pr_data["html_url"],
                    "pr_title": pr_data["title"]
                }
            else:
                return {
                    "success": False,
                    "tool_name": "create_pull_request",
                    "error": f"Failed to create pull request: {response.status_code} - {response.text}",
                    "status_code": response.status_code
                }
                
        except Exception as e:
            return {
                "success": False,
                "tool_name": "create_pull_request",
                "error": f"Failed to create pull request: {str(e)}"
            }

    def _list_pull_requests(self, arguments: dict) -> dict:
        """List pull requests on GitHub."""
        try:
            if not all([self.github_token, self.github_owner, self.github_repo]):
                return {
                    "success": False,
                    "tool_name": "list_pull_requests",
                    "error": "GitHub configuration missing"
                }
            
            state = arguments.get("state", "open")
            url = f"https://api.github.com/repos/{self.github_owner}/{self.github_repo}/pulls?state={state}"
            headers = {
                "Authorization": f"token {self.github_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                prs = response.json()
                return {
                    "success": True,
                    "tool_name": "list_pull_requests",
                    "result": f"Found {len(prs)} pull requests",
                    "pull_requests": [
                        {
                            "number": pr["number"],
                            "title": pr["title"],
                            "state": pr["state"],
                            "url": pr["html_url"],
                            "head_branch": pr["head"]["ref"],
                            "base_branch": pr["base"]["ref"]
                        }
                        for pr in prs
                    ]
                }
            else:
                return {
                    "success": False,
                    "tool_name": "list_pull_requests",
                    "error": f"Failed to list pull requests: {response.status_code}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "tool_name": "list_pull_requests",
                "error": f"Failed to list pull requests: {str(e)}"
            }

    def _merge_pull_request(self, arguments: dict) -> dict:
        """Merge a pull request on GitHub."""
        try:
            if not all([self.github_token, self.github_owner, self.github_repo]):
                return {
                    "success": False,
                    "tool_name": "merge_pull_request",
                    "error": "GitHub configuration missing"
                }
            
            pr_number = arguments.get("pr_number")
            if not pr_number:
                return {
                    "success": False,
                    "tool_name": "merge_pull_request",
                    "error": "PR number is required"
                }
            
            url = f"https://api.github.com/repos/{self.github_owner}/{self.github_repo}/pulls/{pr_number}/merge"
            headers = {
                "Authorization": f"token {self.github_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            data = {
                "merge_method": arguments.get("merge_method", "merge")
            }
            
            response = requests.put(url, headers=headers, json=data)
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "tool_name": "merge_pull_request",
                    "result": f"Pull request #{pr_number} merged successfully"
                }
            else:
                return {
                    "success": False,
                    "tool_name": "merge_pull_request",
                    "error": f"Failed to merge pull request: {response.status_code} - {response.text}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "tool_name": "merge_pull_request",
                "error": f"Failed to merge pull request: {str(e)}"
            }

    def _generate_report(self, arguments: dict) -> dict:
        """Generate a report."""
        try:
            report_type = arguments.get("type", "general")
            pr_number = arguments.get("pr_number")
            
            report = {
                "id": f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "type": report_type,
                "pr_number": pr_number,
                "generated_at": datetime.now().isoformat(),
                "summary": f"Report generated for {report_type}",
                "details": "This is a sample report generated by the GitHub MCP Bridge"
            }
            
            return {
                "success": True,
                "tool_name": "generate_report",
                "result": f"Generated {report_type} report",
                "report": report
            }
            
        except Exception as e:
            return {
                "success": False,
                "tool_name": "generate_report",
                "error": f"Failed to generate report: {str(e)}"
            }

    def _create_local_url(self, arguments: dict) -> dict:
        """Create a local URL for a report."""
        try:
            report_id = arguments.get("report_id")
            if not report_id:
                return {
                    "success": False,
                    "tool_name": "create_local_url",
                    "error": "Report ID is required"
                }
            
            url = f"http://localhost:8000/reports/{report_id}.html"
            
            return {
                "success": True,
                "tool_name": "create_local_url",
                "result": f"Created local URL for report {report_id}",
                "url": url
            }
            
        except Exception as e:
            return {
                "success": False,
                "tool_name": "create_local_url",
                "error": f"Failed to create local URL: {str(e)}"
            }

    def _save_report(self, arguments: dict) -> dict:
        """Save a report to local storage."""
        try:
            report = arguments.get("report")
            if not report:
                return {
                    "success": False,
                    "tool_name": "save_report",
                    "error": "Report data is required"
                }
            
            # Create reports directory if it doesn't exist
            os.makedirs("reports", exist_ok=True)
            
            report_id = report.get("id", f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            filename = f"reports/{report_id}.json"
            
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2)
            
            return {
                "success": True,
                "tool_name": "save_report",
                "result": f"Saved report to {filename}",
                "filename": filename
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
            "server": "github_mcp_bridge",
            "github_configured": bool(all([self.github_token, self.github_owner, self.github_repo])),
            "timestamp": datetime.now().isoformat()
        }

    def get_tools(self) -> dict:
        """Get available tools."""
        return {
            "tools": [
                {"name": "create_pull_request", "description": "Create a pull request on GitHub"},
                {"name": "list_pull_requests", "description": "List pull requests on GitHub"},
                {"name": "merge_pull_request", "description": "Merge a pull request on GitHub"},
                {"name": "generate_report", "description": "Generate a report"},
                {"name": "create_local_url", "description": "Create a local URL for a report"},
                {"name": "save_report", "description": "Save a report to local storage"}
            ]
        }

# Create bridge instance
bridge = GitHubMCPBridge()

class GitHubMCPHandler(BaseHTTPRequestHandler):
    """HTTP handler for GitHub MCP bridge."""
    
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
    """Run the GitHub MCP bridge."""
    try:
        server = HTTPServer((host, port), GitHubMCPHandler)
        logger.info(f"🚀 Starting GitHub MCP Bridge on http://{host}:{port}")
        logger.info("🔗 Connected to GitHub API!")
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