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
            elif tool_name == "list_branches":
                return self._list_branches(arguments)
            elif tool_name == "check_branch_commits":
                return self._check_branch_commits_tool(arguments)
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
        """Create a pull request on GitHub with intelligent validation."""
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
            
            # Step 1: Check if branch has new commits
            logger.info(f"🔍 Checking if {source_branch} has new commits compared to {target_branch}")
            commit_check = self._check_branch_has_new_commits(source_branch, target_branch)
            
            if not commit_check.get("success"):
                return {
                    "success": False,
                    "tool_name": "create_pull_request",
                    "error": f"Branch validation failed: {commit_check.get('error')}",
                    "validation_details": commit_check
                }
            
            if not commit_check.get("has_new_commits"):
                return {
                    "success": False,
                    "tool_name": "create_pull_request",
                    "error": f"No new commits found in {source_branch} compared to {target_branch}. Cannot create pull request.",
                    "validation_details": commit_check,
                    "suggestion": f"Make commits to {source_branch} before creating a pull request"
                }
            
            # Step 2: Check if PR already exists
            logger.info(f"🔍 Checking if PR already exists for {source_branch} → {target_branch}")
            existing_pr_check = self._check_existing_pull_request(source_branch, target_branch)
            
            if existing_pr_check.get("exists"):
                existing_pr = existing_pr_check.get("pr")
                return {
                    "success": False,
                    "tool_name": "create_pull_request",
                    "error": f"A pull request already exists for {source_branch} → {target_branch}",
                    "existing_pr": existing_pr,
                    "suggestion": f"Use existing PR #{existing_pr['number']}: {existing_pr['url']}"
                }
            
            # Step 3: Create the pull request
            logger.info(f"🚀 Creating pull request: {source_branch} → {target_branch}")
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
                logger.info(f"✅ Pull request created successfully: #{pr_data['number']}")
                return {
                    "success": True,
                    "tool_name": "create_pull_request",
                    "result": f"Pull request created successfully",
                    "pr_id": pr_data["id"],
                    "pr_number": pr_data["number"],
                    "pr_url": pr_data["html_url"],
                    "pr_title": pr_data["title"],
                    "validation_details": commit_check
                }
            else:
                error_msg = f"Failed to create pull request: {response.status_code} - {response.text}"
                logger.error(f"❌ {error_msg}")
                return {
                    "success": False,
                    "tool_name": "create_pull_request",
                    "error": error_msg,
                    "status_code": response.status_code
                }
                
        except Exception as e:
            error_msg = f"Failed to create pull request: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return {
                "success": False,
                "tool_name": "create_pull_request",
                "error": error_msg
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

    def _list_branches(self, arguments: dict) -> dict:
        """List all branches in the GitHub repository."""
        try:
            if not all([self.github_token, self.github_owner, self.github_repo]):
                return {
                    "success": False,
                    "tool_name": "list_branches",
                    "error": "GitHub configuration missing. Set GITHUB_TOKEN, GITHUB_OWNER, and GITHUB_REPO environment variables."
                }
            
            url = f"https://api.github.com/repos/{self.github_owner}/{self.github_repo}/branches"
            headers = {
                "Authorization": f"token {self.github_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                branches = response.json()
                branch_list = []
                
                for branch in branches:
                    try:
                        # Safely extract branch information
                        branch_info = {
                            "name": branch.get("name", "unknown"),
                            "commit_sha": branch.get("commit", {}).get("sha", ""),
                            "commit_message": "",
                            "protected": branch.get("protection", {}).get("enabled", False)
                        }
                        
                        # Safely extract commit message
                        commit_data = branch.get("commit", {})
                        if isinstance(commit_data, dict):
                            commit_details = commit_data.get("commit", {})
                            if isinstance(commit_details, dict):
                                branch_info["commit_message"] = commit_details.get("message", "")
                        
                        branch_list.append(branch_info)
                    except Exception as e:
                        logger.warning(f"Error processing branch {branch.get('name', 'unknown')}: {e}")
                        # Add basic branch info even if commit details fail
                        branch_info = {
                            "name": branch.get("name", "unknown"),
                            "commit_sha": "",
                            "commit_message": "",
                            "protected": False
                        }
                        branch_list.append(branch_info)
                
                # Sort branches: main/master first, then feature branches, then others
                def sort_key(branch):
                    name = branch["name"].lower()
                    if name in ["main", "master"]:
                        return (0, name)
                    elif name.startswith("feature/"):
                        return (1, name)
                    elif name.startswith("hotfix/"):
                        return (2, name)
                    elif name.startswith("release/"):
                        return (3, name)
                    else:
                        return (4, name)
                
                branch_list.sort(key=sort_key)
                
                return {
                    "success": True,
                    "tool_name": "list_branches",
                    "result": f"Found {len(branch_list)} branches",
                    "branches": branch_list,
                    "total_count": len(branch_list)
                }
            else:
                return {
                    "success": False,
                    "tool_name": "list_branches",
                    "error": f"Failed to list branches: {response.status_code} - {response.text}",
                    "status_code": response.status_code
                }
                
        except Exception as e:
            return {
                "success": False,
                "tool_name": "list_branches",
                "error": f"Failed to list branches: {str(e)}"
            }

    def _check_branch_has_new_commits(self, source_branch: str, target_branch: str) -> dict:
        """Check if source branch has new commits compared to target branch."""
        try:
            # Get the latest commit SHA for both branches
            source_url = f"https://api.github.com/repos/{self.github_owner}/{self.github_repo}/branches/{source_branch}"
            target_url = f"https://api.github.com/repos/{self.github_owner}/{self.github_repo}/branches/{target_branch}"
            
            headers = {
                "Authorization": f"token {self.github_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            # Get source branch info
            source_response = requests.get(source_url, headers=headers)
            if source_response.status_code != 200:
                return {
                    "success": False,
                    "error": f"Source branch '{source_branch}' not found: {source_response.status_code}"
                }
            
            source_data = source_response.json()
            source_sha = source_data["commit"]["sha"]
            
            # Get target branch info
            target_response = requests.get(target_url, headers=headers)
            if target_response.status_code != 200:
                return {
                    "success": False,
                    "error": f"Target branch '{target_branch}' not found: {target_response.status_code}"
                }
            
            target_data = target_response.json()
            target_sha = target_data["commit"]["sha"]
            
            # Check if branches are identical
            if source_sha == target_sha:
                return {
                    "success": True,
                    "has_new_commits": False,
                    "source_sha": source_sha,
                    "target_sha": target_sha,
                    "message": f"Branches {source_branch} and {target_branch} are identical"
                }
            
            # Check if source branch is ahead of target branch
            compare_url = f"https://api.github.com/repos/{self.github_owner}/{self.github_repo}/compare/{target_branch}...{source_branch}"
            compare_response = requests.get(compare_url, headers=headers)
            
            if compare_response.status_code == 200:
                compare_data = compare_response.json()
                ahead_by = compare_data.get("ahead_by", 0)
                behind_by = compare_data.get("behind_by", 0)
                
                has_new_commits = ahead_by > 0
                
                return {
                    "success": True,
                    "has_new_commits": has_new_commits,
                    "source_sha": source_sha,
                    "target_sha": target_sha,
                    "ahead_by": ahead_by,
                    "behind_by": behind_by,
                    "total_commits": compare_data.get("total_commits", 0),
                    "message": f"Source branch is {ahead_by} commits ahead, {behind_by} commits behind"
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to compare branches: {compare_response.status_code}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Error checking branch commits: {str(e)}"
            }

    def _check_existing_pull_request(self, source_branch: str, target_branch: str) -> dict:
        """Check if a pull request already exists for the given branch combination."""
        try:
            url = f"https://api.github.com/repos/{self.github_owner}/{self.github_repo}/pulls?state=open&head={self.github_owner}:{source_branch}&base={target_branch}"
            headers = {
                "Authorization": f"token {self.github_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                prs = response.json()
                
                if prs:
                    # Return the first (and should be only) PR
                    pr = prs[0]
                    return {
                        "exists": True,
                        "pr": {
                            "number": pr["number"],
                            "title": pr["title"],
                            "url": pr["html_url"],
                            "state": pr["state"],
                            "head_branch": pr["head"]["ref"],
                            "base_branch": pr["base"]["ref"]
                        }
                    }
                else:
                    return {
                        "exists": False,
                        "pr": None
                    }
            else:
                return {
                    "exists": False,
                    "error": f"Failed to check existing PRs: {response.status_code}"
                }
                
        except Exception as e:
            return {
                "exists": False,
                "error": f"Error checking existing PRs: {str(e)}"
            }

    def _check_branch_commits_tool(self, arguments: dict) -> dict:
        """Tool to check if a branch has new commits compared to another branch."""
        try:
            source_branch = arguments.get("source_branch")
            target_branch = arguments.get("target_branch", "main")
            
            if not source_branch:
                return {
                    "success": False,
                    "tool_name": "check_branch_commits",
                    "error": "source_branch parameter is required"
                }
            
            result = self._check_branch_has_new_commits(source_branch, target_branch)
            
            if result.get("success"):
                return {
                    "success": True,
                    "tool_name": "check_branch_commits",
                    "result": f"Branch {source_branch} has new commits: {result.get('has_new_commits')}",
                    "details": result
                }
            else:
                return {
                    "success": False,
                    "tool_name": "check_branch_commits",
                    "error": result.get("error"),
                    "details": result
                }
                
        except Exception as e:
            return {
                "success": False,
                "tool_name": "check_branch_commits",
                "error": f"Failed to check branch commits: {str(e)}"
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
                {"name": "list_branches", "description": "List all branches in the GitHub repository"},
                {"name": "check_branch_commits", "description": "Check if a branch has new commits compared to another branch"},
                {"name": "create_pull_request", "description": "Create a pull request on GitHub with intelligent validation"},
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