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
            # New Slack tools - safely added without breaking existing functionality
            "slack_post_alert": self.slack_post_alert,
            "slack_post_message": self.slack_post_message,
            "slack_post_rich_message": self.slack_post_rich_message
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
            
            # Try to send via Gmail SMTP first (using your credentials)
            gmail_user = os.getenv('GOOGLE_EMAIL')
            gmail_password = os.getenv('GOOGLE_PASSWORD')
            
            if gmail_user and gmail_password and gmail_user != 'your-email@gmail.com' and gmail_password != 'your-app-password':
                try:
                    # Use Gmail SMTP for reliable delivery
                    server = smtplib.SMTP(smtp_server, smtp_port)
                    server.starttls()
                    
                    # Login with your credentials
                    server.login(gmail_user, gmail_password)
                    
                    # Send email
                    text = msg.as_string()
                    server.sendmail(gmail_user, to_email, text)
                    server.quit()
                    
                    logger.info(f"📧 EMAIL SENT via Gmail SMTP to {to_email}")
                    return {
                        "success": True,
                        "tool_name": "sendmail",
                        "result": f"Email sent successfully to {to_email} via Gmail SMTP",
                        "note": "Email delivered via Gmail SMTP"
                    }
                    
                except Exception as smtp_error:
                    logger.warning(f"📧 GMAIL SMTP FAILED: {smtp_error}")
            else:
                logger.info("📧 Gmail credentials not configured, trying sendmail...")
            
            # Log the email content for debugging
            logger.info(f"📧 EMAIL CONTENT:")
            logger.info(f"   From: {msg['From']}")
            logger.info(f"   To: {msg['To']}")
            logger.info(f"   Subject: {msg['Subject']}")
            logger.info(f"   Body: {body}")
            
            # Try to send via sendmail as fallback
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
    
    # New Slack tools - safely implemented without breaking existing functionality
    def slack_post_alert(self, channel: str, title: str, message: str, severity: str = "info") -> Dict[str, Any]:
        """Post alert to Slack channel."""
        try:
            # Get Slack webhook URL from environment variable
            slack_webhook_url = os.getenv('SLACK_WEBHOOK_URL')
            
            if not slack_webhook_url:
                logger.warning("📢 SLACK: No webhook URL configured, logging alert instead")
                return {
                    "success": False,
                    "tool_name": "slack_post_alert",
                    "error": "SLACK_WEBHOOK_URL environment variable not set",
                    "note": "Set SLACK_WEBHOOK_URL to enable Slack integration",
                    "alert_data": {
                        "channel": channel,
                        "title": title,
                        "message": message,
                        "severity": severity
                    }
                }
            
            # Try to import requests for HTTP calls
            try:
                import requests
            except ImportError:
                logger.warning("📢 SLACK: requests library not available, logging alert instead")
                return {
                    "success": False,
                    "tool_name": "slack_post_alert",
                    "error": "requests library not installed",
                    "note": "Install requests: pip install requests",
                    "alert_data": {
                        "channel": channel,
                        "title": title,
                        "message": message,
                        "severity": severity
                    }
                }
            
            # Format Slack message
            severity_colors = {
                "error": "#FF0000",      # Red for critical/error
                "warning": "#FFA500",    # Orange for warning
                "info": "#0000FF",       # Blue for info
                "success": "#00FF00"     # Green for success
            }
            
            slack_data = {
                "channel": channel,
                "attachments": [{
                    "color": severity_colors.get(severity, "#0000FF"),
                    "title": title,
                    "text": message,
                    "footer": "Agentic RAG Alert System",
                    "ts": int(datetime.now().timestamp())
                }]
            }
            
            # Send to Slack
            response = requests.post(slack_webhook_url, json=slack_data, timeout=10)
            
            if response.status_code == 200:
                logger.info(f"📢 SLACK: Alert sent to {channel}: {title}")
                return {
                    "success": True,
                    "tool_name": "slack_post_alert",
                    "result": f"Alert sent to Slack channel {channel}",
                    "slack_response": "ok"
                }
            else:
                logger.warning(f"📢 SLACK: Failed to send alert, status {response.status_code}")
                return {
                    "success": False,
                    "tool_name": "slack_post_alert",
                    "error": f"Slack API returned status {response.status_code}",
                    "slack_response": response.text
                }
                
        except Exception as e:
            logger.error(f"📢 SLACK ERROR: {e}")
            return {
                "success": False,
                "tool_name": "slack_post_alert",
                "error": f"Error sending Slack alert: {str(e)}",
                "note": "Check Slack webhook configuration and network connectivity"
            }
    
    def slack_post_message(self, channel: str, message: str) -> Dict[str, Any]:
        """Post simple message to Slack channel."""
        try:
            # Get Slack webhook URL from environment variable
            slack_webhook_url = os.getenv('SLACK_WEBHOOK_URL')
            
            if not slack_webhook_url:
                logger.warning("📢 SLACK: No webhook URL configured, logging message instead")
                return {
                    "success": False,
                    "tool_name": "slack_post_message",
                    "error": "SLACK_WEBHOOK_URL environment variable not set",
                    "note": "Set SLACK_WEBHOOK_URL to enable Slack integration",
                    "message_data": {
                        "channel": channel,
                        "message": message
                    }
                }
            
            # Try to import requests for HTTP calls
            try:
                import requests
            except ImportError:
                logger.warning("📢 SLACK: requests library not available, logging message instead")
                return {
                    "success": False,
                    "tool_name": "slack_post_message",
                    "error": "requests library not installed",
                    "note": "Install requests: pip install requests",
                    "message_data": {
                        "channel": channel,
                        "message": message
                    }
                }
            
            # Format Slack message
            slack_data = {
                "channel": channel,
                "text": message
            }
            
            # Send to Slack
            response = requests.post(slack_webhook_url, json=slack_data, timeout=10)
            
            if response.status_code == 200:
                logger.info(f"📢 SLACK: Message sent to {channel}")
                return {
                    "success": True,
                    "tool_name": "slack_post_message",
                    "result": f"Message sent to Slack channel {channel}",
                    "slack_response": "ok"
                }
            else:
                logger.warning(f"📢 SLACK: Failed to send message, status {response.status_code}")
                return {
                    "success": False,
                    "tool_name": "slack_post_message",
                    "error": f"Slack API returned status {response.status_code}",
                    "slack_response": response.text
                }
                
        except Exception as e:
            logger.error(f"📢 SLACK ERROR: {e}")
            return {
                "success": False,
                "tool_name": "slack_post_message",
                "error": f"Error sending Slack message: {str(e)}",
                "note": "Check Slack webhook configuration and network connectivity"
            }
    
    def slack_post_rich_message(self, channel: str, blocks: list) -> Dict[str, Any]:
        """Post rich formatted message with Slack blocks to channel."""
        try:
            # Get Slack webhook URL from environment variable
            slack_webhook_url = os.getenv('SLACK_WEBHOOK_URL')
            
            if not slack_webhook_url:
                logger.warning("📢 SLACK: No webhook URL configured, logging rich message instead")
                return {
                    "success": False,
                    "tool_name": "slack_post_rich_message",
                    "error": "SLACK_WEBHOOK_URL environment variable not set",
                    "note": "Set SLACK_WEBHOOK_URL to enable Slack integration",
                    "message_data": {
                        "channel": channel,
                        "blocks": blocks
                    }
                }
            
            # Try to import requests for HTTP calls
            try:
                import requests
            except ImportError:
                logger.warning("📢 SLACK: requests library not available, logging rich message instead")
                return {
                    "success": False,
                    "tool_name": "slack_post_rich_message",
                    "error": "requests library not installed",
                    "note": "Install requests: pip install requests",
                    "message_data": {
                        "channel": channel,
                        "blocks": blocks
                    }
                }
            
            # Format Slack message with blocks
            slack_data = {
                "channel": channel,
                "blocks": blocks
            }
            
            # Send to Slack
            response = requests.post(slack_webhook_url, json=slack_data, timeout=10)
            
            if response.status_code == 200:
                logger.info(f"📢 SLACK: Rich message sent to {channel}")
                return {
                    "success": True,
                    "tool_name": "slack_post_rich_message",
                    "result": f"Rich message sent to Slack channel {channel}",
                    "slack_response": "ok"
                }
            else:
                logger.warning(f"📢 SLACK: Failed to send rich message, status {response.status_code}")
                return {
                    "success": False,
                    "tool_name": "slack_post_rich_message",
                    "error": f"Slack API returned status {response.status_code}",
                    "slack_response": response.text
                }
                
        except Exception as e:
            logger.error(f"📢 SLACK ERROR: {e}")
            return {
                "success": False,
                "tool_name": "slack_post_rich_message",
                "error": f"Error sending Slack rich message: {str(e)}",
                "note": "Check Slack webhook configuration and network connectivity"
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
            # New Slack tool handlers - safely added without breaking existing functionality
            elif tool_name == "slack_post_alert":
                return tool_func(
                    arguments.get("channel", "#general"),
                    arguments.get("title", "Alert"),
                    arguments.get("message", ""),
                    arguments.get("severity", "info")
                )
            elif tool_name == "slack_post_message":
                return tool_func(
                    arguments.get("channel", "#general"),
                    arguments.get("message", "")
                )
            elif tool_name == "slack_post_rich_message":
                return tool_func(
                    arguments.get("channel", "#general"),
                    arguments.get("blocks", [])
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
                {"name": "slack_post_alert", "description": "Post alert to Slack channel"},
                {"name": "slack_post_message", "description": "Post simple message to Slack channel"},
                {"name": "slack_post_rich_message", "description": "Post rich formatted message with Slack blocks"}
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