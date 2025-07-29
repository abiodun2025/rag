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
            # Branch management tools
            elif tool_name == "create_branch":
                return self._create_branch(arguments)
            elif tool_name == "checkout_branch":
                return self._checkout_branch(arguments)
            elif tool_name == "push_branch":
                return self._push_branch(arguments)
            elif tool_name == "delete_branch":
                return self._delete_branch(arguments)
            elif tool_name == "list_branches":
                return self._list_branches(arguments)
            elif tool_name == "create_branch_from_base":
                return self._create_branch_from_base(arguments)
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

    def _create_branch(self, arguments: dict) -> dict:
        """Create a new branch from main."""
        try:
            import subprocess
            import os
            
            branch_name = arguments.get("branch_name")
            if not branch_name:
                return {
                    "success": False,
                    "tool_name": "create_branch",
                    "error": "Branch name is required"
                }
            
            # Check if we're in a git repository
            if not os.path.exists(".git"):
                return {
                    "success": False,
                    "tool_name": "create_branch",
                    "error": "Not in a git repository"
                }
            
            # Create and checkout the new branch from main
            try:
                # First, determine which base branch to use (main or master)
                check_main = subprocess.run(
                    ["git", "show-ref", "--verify", "--quiet", "refs/heads/main"],
                    capture_output=True,
                    text=True,
                    cwd=os.getcwd()
                )
                
                check_master = subprocess.run(
                    ["git", "show-ref", "--verify", "--quiet", "refs/heads/master"],
                    capture_output=True,
                    text=True,
                    cwd=os.getcwd()
                )
                
                # Determine the base branch
                if check_main.returncode == 0:
                    base_branch = "main"
                elif check_master.returncode == 0:
                    base_branch = "master"
                else:
                    return {
                        "success": False,
                        "tool_name": "create_branch",
                        "error": "Neither 'main' nor 'master' branch exists"
                    }
                
                # Checkout to the base branch
                checkout_base = subprocess.run(
                    ["git", "checkout", base_branch],
                    capture_output=True,
                    text=True,
                    cwd=os.getcwd()
                )
                
                if checkout_base.returncode != 0:
                    return {
                        "success": False,
                        "tool_name": "create_branch",
                        "error": f"Failed to checkout to {base_branch}: {checkout_base.stderr}"
                    }
                
                # Now create the new branch from main/master
                result = subprocess.run(
                    ["git", "checkout", "-b", branch_name],
                    capture_output=True,
                    text=True,
                    cwd=os.getcwd()
                )
                
                if result.returncode == 0:
                    return {
                        "success": True,
                        "tool_name": "create_branch",
                        "result": f"Successfully created and checked out branch '{branch_name}' from {base_branch}",
                        "branch_name": branch_name,
                        "current_branch": branch_name,
                        "created_from": base_branch
                    }
                else:
                    return {
                        "success": False,
                        "tool_name": "create_branch",
                        "error": f"Failed to create branch: {result.stderr}"
                    }
                    
            except Exception as e:
                return {
                    "success": False,
                    "tool_name": "create_branch",
                    "error": f"Git command failed: {str(e)}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "tool_name": "create_branch",
                "error": f"Failed to create branch: {str(e)}"
            }

    def _create_branch_from_base(self, arguments: dict) -> dict:
        """Create a new branch from a specified base branch."""
        try:
            import subprocess
            import os
            
            branch_name = arguments.get("branch_name")
            base_branch = arguments.get("base_branch", "main")
            
            if not branch_name:
                return {
                    "success": False,
                    "tool_name": "create_branch_from_base",
                    "error": "Branch name is required"
                }
            
            # Check if we're in a git repository
            if not os.path.exists(".git"):
                return {
                    "success": False,
                    "tool_name": "create_branch_from_base",
                    "error": "Not in a git repository"
                }
            
            # Create and checkout the new branch from the specified base
            try:
                # First, checkout to the base branch
                checkout_base = subprocess.run(
                    ["git", "checkout", base_branch],
                    capture_output=True,
                    text=True,
                    cwd=os.getcwd()
                )
                
                if checkout_base.returncode != 0:
                    return {
                        "success": False,
                        "tool_name": "create_branch_from_base",
                        "error": f"Failed to checkout to base branch '{base_branch}': {checkout_base.stderr}"
                    }
                
                # Now create the new branch from the base branch
                result = subprocess.run(
                    ["git", "checkout", "-b", branch_name],
                    capture_output=True,
                    text=True,
                    cwd=os.getcwd()
                )
                
                if result.returncode == 0:
                    return {
                        "success": True,
                        "tool_name": "create_branch_from_base",
                        "result": f"Successfully created and checked out branch '{branch_name}' from '{base_branch}'",
                        "branch_name": branch_name,
                        "current_branch": branch_name,
                        "created_from": base_branch
                    }
                else:
                    return {
                        "success": False,
                        "tool_name": "create_branch_from_base",
                        "error": f"Failed to create branch: {result.stderr}"
                    }
                    
            except Exception as e:
                return {
                    "success": False,
                    "tool_name": "create_branch_from_base",
                    "error": f"Git command failed: {str(e)}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "tool_name": "create_branch_from_base",
                "error": f"Failed to create branch: {str(e)}"
            }

    def _checkout_branch(self, arguments: dict) -> dict:
        """Checkout to an existing branch."""
        try:
            import subprocess
            import os
            
            branch_name = arguments.get("branch_name")
            if not branch_name:
                return {
                    "success": False,
                    "tool_name": "checkout_branch",
                    "error": "Branch name is required"
                }
            
            # Check if we're in a git repository
            if not os.path.exists(".git"):
                return {
                    "success": False,
                    "tool_name": "checkout_branch",
                    "error": "Not in a git repository"
                }
            
            try:
                # Checkout the branch
                result = subprocess.run(
                    ["git", "checkout", branch_name],
                    capture_output=True,
                    text=True,
                    cwd=os.getcwd()
                )
                
                if result.returncode == 0:
                    return {
                        "success": True,
                        "tool_name": "checkout_branch",
                        "result": f"Successfully checked out to branch '{branch_name}'",
                        "branch_name": branch_name
                    }
                else:
                    return {
                        "success": False,
                        "tool_name": "checkout_branch",
                        "error": f"Failed to checkout branch: {result.stderr}"
                    }
                    
            except Exception as e:
                return {
                    "success": False,
                    "tool_name": "checkout_branch",
                    "error": f"Git command failed: {str(e)}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "tool_name": "checkout_branch",
                "error": f"Failed to checkout branch: {str(e)}"
            }

    def _push_branch(self, arguments: dict) -> dict:
        """Push a branch to remote repository."""
        try:
            import subprocess
            import os
            
            branch_name = arguments.get("branch_name")
            if not branch_name:
                return {
                    "success": False,
                    "tool_name": "push_branch",
                    "error": "Branch name is required"
                }
            
            # Check if we're in a git repository
            if not os.path.exists(".git"):
                return {
                    "success": False,
                    "tool_name": "push_branch",
                    "error": "Not in a git repository"
                }
            
            try:
                # Push the branch
                result = subprocess.run(
                    ["git", "push", "origin", branch_name],
                    capture_output=True,
                    text=True,
                    cwd=os.getcwd()
                )
                
                if result.returncode == 0:
                    return {
                        "success": True,
                        "tool_name": "push_branch",
                        "result": f"Successfully pushed branch '{branch_name}' to remote",
                        "branch_name": branch_name
                    }
                else:
                    return {
                        "success": False,
                        "tool_name": "push_branch",
                        "error": f"Failed to push branch: {result.stderr}"
                    }
                    
            except Exception as e:
                return {
                    "success": False,
                    "tool_name": "push_branch",
                    "error": f"Git command failed: {str(e)}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "tool_name": "push_branch",
                "error": f"Failed to push branch: {str(e)}"
            }

    def _delete_branch(self, arguments: dict) -> dict:
        """Delete a branch."""
        try:
            import subprocess
            import os
            
            branch_name = arguments.get("branch_name")
            if not branch_name:
                return {
                    "success": False,
                    "tool_name": "delete_branch",
                    "error": "Branch name is required"
                }
            
            # Check if we're in a git repository
            if not os.path.exists(".git"):
                return {
                    "success": False,
                    "tool_name": "delete_branch",
                    "error": "Not in a git repository"
                }
            
            try:
                # Delete the branch locally
                result = subprocess.run(
                    ["git", "branch", "-D", branch_name],
                    capture_output=True,
                    text=True,
                    cwd=os.getcwd()
                )
                
                if result.returncode == 0:
                    # Also try to delete from remote
                    remote_result = subprocess.run(
                        ["git", "push", "origin", "--delete", branch_name],
                        capture_output=True,
                        text=True,
                        cwd=os.getcwd()
                    )
                    
                    remote_message = ""
                    if remote_result.returncode == 0:
                        remote_message = " and from remote"
                    else:
                        remote_message = " (remote deletion may have failed)"
                    
                    return {
                        "success": True,
                        "tool_name": "delete_branch",
                        "result": f"Successfully deleted branch '{branch_name}' locally{remote_message}",
                        "branch_name": branch_name
                    }
                else:
                    return {
                        "success": False,
                        "tool_name": "delete_branch",
                        "error": f"Failed to delete branch: {result.stderr}"
                    }
                    
            except Exception as e:
                return {
                    "success": False,
                    "tool_name": "delete_branch",
                    "error": f"Git command failed: {str(e)}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "tool_name": "delete_branch",
                "error": f"Failed to delete branch: {str(e)}"
            }

    def _list_branches(self, arguments: dict) -> dict:
        """List all branches."""
        try:
            import subprocess
            import os
            
            # Check if we're in a git repository
            if not os.path.exists(".git"):
                return {
                    "success": False,
                    "tool_name": "list_branches",
                    "error": "Not in a git repository"
                }
            
            try:
                # List all branches
                result = subprocess.run(
                    ["git", "branch", "-a"],
                    capture_output=True,
                    text=True,
                    cwd=os.getcwd()
                )
                
                if result.returncode == 0:
                    branches = result.stdout.strip().split('\n')
                    branch_list = []
                    
                    for branch in branches:
                        if branch.strip():
                            # Remove the * prefix for current branch
                            clean_branch = branch.strip().replace('* ', '')
                            is_current = branch.strip().startswith('* ')
                            branch_list.append({
                                "name": clean_branch,
                                "is_current": is_current
                            })
                    
                    return {
                        "success": True,
                        "tool_name": "list_branches",
                        "result": f"Found {len(branch_list)} branches",
                        "branches": branch_list
                    }
                else:
                    return {
                        "success": False,
                        "tool_name": "list_branches",
                        "error": f"Failed to list branches: {result.stderr}"
                    }
                    
            except Exception as e:
                return {
                    "success": False,
                    "tool_name": "list_branches",
                    "error": f"Git command failed: {str(e)}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "tool_name": "list_branches",
                "error": f"Failed to list branches: {str(e)}"
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
                {"name": "save_report", "description": "Save a report to local storage"},
                {"name": "create_branch", "description": "Create a new git branch from main"},
                {"name": "create_branch_from_base", "description": "Create a new git branch from a specified base branch"},
                {"name": "checkout_branch", "description": "Checkout to an existing git branch"},
                {"name": "push_branch", "description": "Push a branch to remote repository"},
                {"name": "delete_branch", "description": "Delete a git branch"},
                {"name": "list_branches", "description": "List all git branches"}
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