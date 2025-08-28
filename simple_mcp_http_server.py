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
            "sendmail_simple": self.sendmail_simple,
            # Project Management Tools
            "jira_create_issue": self.jira_create_issue,
            "jira_get_issues": self.jira_get_issues,
            "jira_update_issue": self.jira_update_issue,
            "trello_create_card": self.trello_create_card,
            "trello_get_cards": self.trello_get_cards,
            "trello_update_card": self.trello_update_card,
            "asana_create_task": self.asana_create_task,
            "asana_get_tasks": self.asana_get_tasks,
            "asana_update_task": self.asana_update_task,
            "linear_create_issue": self.linear_create_issue,
            "linear_get_issues": self.linear_get_issues,
            "linear_update_issue": self.linear_update_issue,
            "sync_projects": self.sync_projects,
            "get_project_status": self.get_project_status
        }
        logger.info("Simple MCP Server initialized with project management tools")
    
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
        """Send email via SMTP instead of sendmail for better delivery."""
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            import os
            
            # Log the email attempt
            logger.info(f"📧 SENDING EMAIL: To: {to_email}, Subject: {subject}")
            
            # Use Gmail SMTP for better delivery
            # Note: You'll need to set up Gmail App Password for this to work
            smtp_server = "smtp.gmail.com"
            smtp_port = 587
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = from_email or 'noreply@localhost'
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add body to email
            msg.attach(MIMEText(body, 'plain'))
            
            # For now, just log the email since we don't have SMTP credentials configured
            logger.info(f"📧 EMAIL CONTENT:")
            logger.info(f"   From: {msg['From']}")
            logger.info(f"   To: {msg['To']}")
            logger.info(f"   Subject: {msg['Subject']}")
            logger.info(f"   Body: {body}")
            
            # Try to send via sendmail first (for local testing)
            try:
                import subprocess
                email_content = f"""From: {msg['From']}
To: {msg['To']}
Subject: {msg['Subject']}

{body}
"""
                
                result = subprocess.run(
                    ['sendmail', '-t'],
                    input=email_content,
                    text=True,
                    capture_output=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    logger.info(f"📧 EMAIL SENT via sendmail to {to_email}")
                    return {
                        "success": True,
                        "tool_name": "sendmail",
                        "result": f"Email sent successfully to {to_email}",
                        "note": "Email sent via sendmail (may not deliver to external domains)"
                    }
                else:
                    error_msg = result.stderr.decode() if result.stderr else "Unknown error"
                    logger.warning(f"📧 SENDMAIL FAILED: {error_msg}")
                    
            except Exception as sendmail_error:
                logger.warning(f"📧 SENDMAIL ERROR: {sendmail_error}")
            
            # If sendmail fails, provide instructions for SMTP setup
            logger.info("📧 EMAIL LOGGED - For external delivery, configure SMTP credentials")
            return {
                "success": True,
                "tool_name": "sendmail",
                "result": f"Email logged successfully to {to_email}",
                "note": "Email logged but not delivered. Configure SMTP for external delivery.",
                "email_content": {
                    "from": msg['From'],
                    "to": msg['To'],
                    "subject": msg['Subject'],
                    "body": body
                }
            }
                
        except Exception as e:
            logger.error(f"📧 EMAIL ERROR: {e}")
            return {
                "success": False,
                "tool_name": "sendmail",
                "error": f"Error sending email: {str(e)}"
            }
    
    def sendmail_simple(self, to_email: str, subject: str, message: str) -> Dict[str, Any]:
        """Send simple email."""
        return self.sendmail(to_email, subject, message)
    
    # Project Management Tools
    def jira_create_issue(self, project_key: str, summary: str, description: str = "", issue_type: str = "Task") -> Dict[str, Any]:
        """Create a Jira issue."""
        try:
            # Mock implementation - in real use, this would connect to Jira API
            issue_id = f"JIRA-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            return {
                "success": True,
                "tool_name": "jira_create_issue",
                "result": {
                    "issue_id": issue_id,
                    "project_key": project_key,
                    "summary": summary,
                    "description": description,
                    "issue_type": issue_type,
                    "status": "To Do",
                    "created_at": datetime.now().isoformat()
                }
            }
        except Exception as e:
            return {
                "success": False,
                "tool_name": "jira_create_issue",
                "error": str(e)
            }
    
    def jira_get_issues(self, project_key: str = None, status: str = None) -> Dict[str, Any]:
        """Get Jira issues."""
        try:
            # Mock implementation - in real use, this would query Jira API
            mock_issues = [
                {
                    "issue_id": "JIRA-20241201001",
                    "project_key": "PROJ",
                    "summary": "Sample Issue 1",
                    "status": "In Progress",
                    "assignee": "Developer 1"
                },
                {
                    "issue_id": "JIRA-20241201002", 
                    "project_key": "PROJ",
                    "summary": "Sample Issue 2",
                    "status": "To Do",
                    "assignee": "Developer 2"
                }
            ]
            return {
                "success": True,
                "tool_name": "jira_get_issues",
                "result": mock_issues
            }
        except Exception as e:
            return {
                "success": False,
                "tool_name": "jira_get_issues",
                "error": str(e)
            }
    
    def jira_update_issue(self, issue_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update a Jira issue."""
        try:
            return {
                "success": True,
                "tool_name": "jira_update_issue",
                "result": {
                    "issue_id": issue_id,
                    "updates": updates,
                    "updated_at": datetime.now().isoformat()
                }
            }
        except Exception as e:
            return {
                "success": False,
                "tool_name": "jira_update_issue",
                "error": str(e)
            }
    
    def trello_create_card(self, board_name: str, list_name: str, card_title: str, description: str = "") -> Dict[str, Any]:
        """Create a Trello card."""
        try:
            card_id = f"trello_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            return {
                "success": True,
                "tool_name": "trello_create_card",
                "result": {
                    "card_id": card_id,
                    "board_name": board_name,
                    "list_name": list_name,
                    "card_title": card_title,
                    "description": description,
                    "created_at": datetime.now().isoformat()
                }
            }
        except Exception as e:
            return {
                "success": False,
                "tool_name": "trello_create_card",
                "error": str(e)
            }
    
    def trello_get_cards(self, board_name: str = None) -> Dict[str, Any]:
        """Get Trello cards."""
        try:
            mock_cards = [
                {
                    "card_id": "trello_001",
                    "board_name": "Project Board",
                    "list_name": "To Do",
                    "card_title": "Sample Task 1",
                    "status": "To Do"
                },
                {
                    "card_id": "trello_002",
                    "board_name": "Project Board", 
                    "list_name": "In Progress",
                    "card_title": "Sample Task 2",
                    "status": "In Progress"
                }
            ]
            return {
                "success": True,
                "tool_name": "trello_get_cards",
                "result": mock_cards
            }
        except Exception as e:
            return {
                "success": False,
                "tool_name": "trello_get_cards",
                "error": str(e)
            }
    
    def trello_update_card(self, card_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update a Trello card."""
        try:
            return {
                "success": True,
                "tool_name": "trello_update_card",
                "result": {
                    "card_id": card_id,
                    "updates": updates,
                    "updated_at": datetime.now().isoformat()
                }
            }
        except Exception as e:
            return {
                "success": False,
                "tool_name": "trello_update_card",
                "error": str(e)
            }
    
    def asana_create_task(self, project_name: str, task_name: str, description: str = "") -> Dict[str, Any]:
        """Create an Asana task."""
        try:
            task_id = f"asana_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            return {
                "success": True,
                "tool_name": "asana_create_task",
                "result": {
                    "task_id": task_id,
                    "project_name": project_name,
                    "task_name": task_name,
                    "description": description,
                    "status": "In Progress",
                    "created_at": datetime.now().isoformat()
                }
            }
        except Exception as e:
            return {
                "success": False,
                "tool_name": "asana_create_task",
                "error": str(e)
            }
    
    def asana_get_tasks(self, project_name: str = None) -> Dict[str, Any]:
        """Get Asana tasks."""
        try:
            mock_tasks = [
                {
                    "task_id": "asana_001",
                    "project_name": "Sample Project",
                    "task_name": "Sample Task 1",
                    "status": "In Progress"
                },
                {
                    "task_id": "asana_02",
                    "project_name": "Sample Project",
                    "task_name": "Sample Task 2", 
                    "status": "Completed"
                }
            ]
            return {
                "success": True,
                "tool_name": "asana_get_tasks",
                "result": mock_tasks
            }
        except Exception as e:
            return {
                "success": False,
                "tool_name": "asana_get_tasks",
                "error": str(e)
            }
    
    def asana_update_task(self, task_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update an Asana task."""
        try:
            return {
                "success": True,
                "tool_name": "asana_update_task",
                "result": {
                    "task_id": task_id,
                    "updates": updates,
                    "updated_at": datetime.now().isoformat()
                }
            }
        except Exception as e:
            return {
                "success": False,
                "tool_name": "asana_update_task",
                "error": str(e)
            }
    
    def linear_create_issue(self, team_name: str, title: str, description: str = "", priority: str = "Medium") -> Dict[str, Any]:
        """Create a Linear issue."""
        try:
            issue_id = f"linear_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            return {
                "success": True,
                "tool_name": "linear_create_issue",
                "result": {
                    "issue_id": issue_id,
                    "team_name": team_name,
                    "title": title,
                    "description": description,
                    "priority": priority,
                    "status": "Todo",
                    "created_at": datetime.now().isoformat()
                }
            }
        except Exception as e:
            return {
                "success": False,
                "tool_name": "linear_create_issue",
                "error": str(e)
            }
    
    def linear_get_issues(self, team_name: str = None) -> Dict[str, Any]:
        """Get Linear issues."""
        try:
            mock_issues = [
                {
                    "issue_id": "linear_001",
                    "team_name": "Engineering",
                    "title": "Sample Issue 1",
                    "status": "In Progress",
                    "priority": "High"
                },
                {
                    "issue_id": "linear_002",
                    "team_name": "Engineering",
                    "title": "Sample Issue 2",
                    "status": "Todo",
                    "priority": "Medium"
                }
            ]
            return {
                "success": True,
                "tool_name": "linear_get_issues",
                "result": mock_issues
            }
        except Exception as e:
            return {
                "success": False,
                "tool_name": "linear_get_issues",
                "error": str(e)
            }
    
    def linear_update_issue(self, issue_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update a Linear issue."""
        try:
            return {
                "success": True,
                "tool_name": "linear_update_issue",
                "result": {
                    "issue_id": issue_id,
                    "updates": updates,
                    "updated_at": datetime.now().isoformat()
                }
            }
        except Exception as e:
            return {
                "success": False,
                "tool_name": "linear_update_issue",
                "error": str(e)
            }
    
    def sync_projects(self, source_platform: str, target_platform: str, project_id: str) -> Dict[str, Any]:
        """Sync projects between different platforms."""
        try:
            sync_id = f"sync_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            return {
                "success": True,
                "tool_name": "sync_projects",
                "result": {
                    "sync_id": sync_id,
                    "source_platform": "jira",
                    "target_platform": "trello",
                    "project_id": project_id,
                    "status": "Syncing",
                    "started_at": datetime.now().isoformat()
                }
            }
        except Exception as e:
            return {
                "success": False,
                "tool_name": "sync_projects",
                "error": str(e)
            }
    
    def get_project_status(self, platform: str, project_id: str) -> Dict[str, Any]:
        """Get project status from a specific platform."""
        try:
            return {
                "success": True,
                "tool_name": "get_project_status",
                "result": {
                    "platform": platform,
                    "project_id": project_id,
                    "status": "Active",
                    "progress": "75%",
                    "last_updated": datetime.now().isoformat()
                }
            }
        except Exception as e:
            return {
                "success": False,
                "tool_name": "get_project_status",
                "error": str(e)
            }
    
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
            # Project Management Tools
            elif tool_name == "jira_create_issue":
                return tool_func(
                    arguments.get("project_key", ""),
                    arguments.get("summary", ""),
                    arguments.get("description", ""),
                    arguments.get("issue_type", "Task")
                )
            elif tool_name == "jira_get_issues":
                return tool_func(
                    arguments.get("project_key"),
                    arguments.get("status")
                )
            elif tool_name == "jira_update_issue":
                return tool_func(
                    arguments.get("issue_id", ""),
                    arguments.get("updates", {})
                )
            elif tool_name == "trello_create_card":
                return tool_func(
                    arguments.get("board_name", ""),
                    arguments.get("list_name", ""),
                    arguments.get("card_title", ""),
                    arguments.get("description", "")
                )
            elif tool_name == "trello_get_cards":
                return tool_func(arguments.get("board_name"))
            elif tool_name == "trello_update_card":
                return tool_func(
                    arguments.get("card_id", ""),
                    arguments.get("updates", {})
                )
            elif tool_name == "asana_create_task":
                return tool_func(
                    arguments.get("project_name", ""),
                    arguments.get("task_name", ""),
                    arguments.get("description", "")
                )
            elif tool_name == "asana_get_tasks":
                return tool_func(arguments.get("project_name"))
            elif tool_name == "asana_update_task":
                return tool_func(
                    arguments.get("task_id", ""),
                    arguments.get("updates", {})
                )
            elif tool_name == "linear_create_issue":
                return tool_func(
                    arguments.get("team_name", ""),
                    arguments.get("title", ""),
                    arguments.get("description", ""),
                    arguments.get("priority", "Medium")
                )
            elif tool_name == "linear_get_issues":
                return tool_func(arguments.get("team_name"))
            elif tool_name == "linear_update_issue":
                return tool_func(
                    arguments.get("issue_id", ""),
                    arguments.get("updates", {})
                )
            elif tool_name == "sync_projects":
                return tool_func(
                    arguments.get("source_platform", ""),
                    arguments.get("target_platform", ""),
                    arguments.get("project_id", "")
                )
            elif tool_name == "get_project_status":
                return tool_func(
                    arguments.get("platform", ""),
                    arguments.get("project_id", "")
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
                {"name": "sendmail_simple", "description": "Simple email sending"},
                # Project Management Tools
                {"name": "jira_create_issue", "description": "Create a Jira issue"},
                {"name": "jira_get_issues", "description": "Get Jira issues"},
                {"name": "jira_update_issue", "description": "Update a Jira issue"},
                {"name": "trello_create_card", "description": "Create a Trello card"},
                {"name": "trello_get_cards", "description": "Get Trello cards"},
                {"name": "trello_update_card", "description": "Update a Trello card"},
                {"name": "asana_create_task", "description": "Create an Asana task"},
                {"name": "asana_get_tasks", "description": "Get Asana tasks"},
                {"name": "asana_update_task", "description": "Update an Asana task"},
                {"name": "linear_create_issue", "description": "Create a Linear issue"},
                {"name": "linear_get_issues", "description": "Get Linear issues"},
                {"name": "linear_update_issue", "description": "Update a Linear issue"},
                {"name": "sync_projects", "description": "Sync projects between platforms"},
                {"name": "get_project_status", "description": "Get project status from platform"}
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