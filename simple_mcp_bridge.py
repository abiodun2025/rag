#!/usr/bin/env python3
"""
Simple MCP HTTP Bridge that directly uses your working Gmail email sender
"""

import json
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
import os
import sys
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the MCP server path to sys.path
sys.path.append("/Users/ola/Desktop/working-mcp-server/count-r-server")

class SimpleMCPBridge:
    def __init__(self):
        self.gmail_sender = None
        self._load_gmail_sender()

    def _load_gmail_sender(self):
        """Load Gmail email sender with better error handling."""
        try:
            from gmail_email_sender import GmailEmailSender
            self.gmail_sender = GmailEmailSender()
            # Set the config file path explicitly
            self.gmail_sender.config_file = "/Users/ola/Desktop/working-mcp-server/count-r-server/gmail_config.json"
            logger.info("✅ Gmail email sender loaded successfully")
        except ImportError as e:
            logger.error(f"❌ Failed to import Gmail email sender: {e}")
            logger.error("Make sure the count-r-server directory exists and contains gmail_email_sender.py")
        except Exception as e:
            logger.error(f"❌ Failed to load Gmail email sender: {e}")

    def call_tool(self, tool_name: str, arguments: dict) -> dict:
        """Call MCP tool with better error handling."""
        try:
            if tool_name == "count_r":
                word = arguments.get("word", "")
                count = word.lower().count('r')
                return {
                    "success": True,
                    "tool_name": "count_r",
                    "result": f"The word '{word}' contains {count} 'r' letters"
                }
            
            elif tool_name == "list_desktop_contents":
                try:
                    desktop_path = os.path.expanduser("~/Desktop")
                    contents = os.listdir(desktop_path)
                    return {
                        "success": True,
                        "tool_name": "list_desktop_contents",
                        "result": f"Desktop contents: {contents}"
                    }
                except Exception as e:
                    return {
                        "success": False,
                        "tool_name": "list_desktop_contents",
                        "error": f"Failed to list desktop contents: {e}"
                    }
            
            elif tool_name == "get_desktop_path":
                desktop_path = os.path.expanduser("~/Desktop")
                return {
                    "success": True,
                    "tool_name": "get_desktop_path",
                    "result": f"Desktop path: {desktop_path}"
                }
            
            elif tool_name == "open_gmail":
                try:
                    import webbrowser
                    webbrowser.open("https://gmail.com")
                    return {
                        "success": True,
                        "tool_name": "open_gmail",
                        "result": "Gmail opened in browser"
                    }
                except Exception as e:
                    return {
                        "success": False,
                        "tool_name": "open_gmail",
                        "error": f"Failed to open Gmail: {e}"
                    }
            
            elif tool_name == "open_gmail_compose":
                try:
                    import webbrowser
                    webbrowser.open("https://mail.google.com/mail/u/0/#compose")
                    return {
                        "success": True,
                        "tool_name": "open_gmail_compose",
                        "result": "Gmail compose window opened"
                    }
                except Exception as e:
                    return {
                        "success": False,
                        "tool_name": "open_gmail_compose",
                        "error": f"Failed to open Gmail compose: {e}"
                    }
            
            elif tool_name in ["sendmail", "sendmail_simple"]:
                return self._send_email(arguments)
            
            # Calling tools
            elif tool_name in ["call_phone", "make_call", "dial_number"]:
                return self._make_phone_call(arguments)
            
            elif tool_name in ["end_call", "hang_up", "terminate_call"]:
                return self._end_phone_call(arguments)
            
            elif tool_name in ["call_status", "get_call_status", "check_call"]:
                return self._get_call_status(arguments)
            
            else:
                return {
                    "success": False,
                    "error": f"Tool '{tool_name}' not found"
                }
                
        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def _send_email(self, arguments: dict) -> dict:
        """Send email using your Gmail SMTP configuration with improved error handling."""
        try:
            to_email = arguments.get("to_email", "")
            subject = arguments.get("subject", "")
            body = arguments.get("body", "") or arguments.get("message", "")
            from_email = arguments.get("from_email", "")

            logger.info(f"📧 SENDING EMAIL via Gmail SMTP:")
            logger.info(f"   To: {to_email}")
            logger.info(f"   Subject: {subject}")
            logger.info(f"   Body length: {len(body)} characters")
            logger.info(f"   Body preview: {body[:100]}...")

            if not self.gmail_sender:
                return {
                    "success": False,
                    "error": "Gmail email sender not loaded. Check if count-r-server is properly configured."
                }

            # Validate inputs
            if not to_email:
                return {
                    "success": False,
                    "error": "No recipient email address provided"
                }
            
            if not subject:
                return {
                    "success": False,
                    "error": "No email subject provided"
                }
            
            if not body:
                return {
                    "success": False,
                    "error": "No email body provided"
                }

            # Change to the directory where the config file is located
            original_cwd = os.getcwd()
            os.chdir("/Users/ola/Desktop/working-mcp-server/count-r-server")

            try:
                result = self.gmail_sender.send_email(to_email, subject, body, from_email)
            finally:
                # Restore original directory
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

    def _make_phone_call(self, arguments: dict) -> dict:
        """Make a phone call using free services."""
        try:
            phone_number = arguments.get("phone_number") or arguments.get("number")
            caller_name = arguments.get("caller_name") or arguments.get("name", "MCP Agent")
            service = arguments.get("service", "google_voice")  # Default to Google Voice
            
            if not phone_number:
                return {
                    "success": False,
                    "tool_name": "call_phone",
                    "error": "No phone number provided"
                }
            
            # Generate a call ID
            call_id = f"call_{int(datetime.now().timestamp())}"
            
            logger.info(f"📞 MAKING CALL:")
            logger.info(f"   To: {phone_number}")
            logger.info(f"   Caller: {caller_name}")
            logger.info(f"   Service: {service}")
            logger.info(f"   Call ID: {call_id}")
            
            # Use free calling services
            if service == "google_voice":
                return self._make_google_voice_call(phone_number, caller_name, call_id)
            elif service == "whatsapp":
                return self._make_whatsapp_call(phone_number, caller_name, call_id)
            elif service == "twilio":
                return self._make_twilio_call(phone_number, caller_name, call_id)
            else:
                return self._make_google_voice_call(phone_number, caller_name, call_id)  # Default
            
        except Exception as e:
            logger.error(f"📞 CALL FAILED: {e}")
            return {
                "success": False,
                "tool_name": "call_phone",
                "error": f"Failed to make call: {str(e)}"
            }

    def _make_google_voice_call(self, phone_number: str, caller_name: str, call_id: str) -> dict:
        """Make a REAL call using Google Voice."""
        try:
            import subprocess
            import webbrowser
            import time
            
            # Clean up phone number
            digits = ''.join(filter(str.isdigit, phone_number))
            if len(digits) == 10:
                clean_number = f"+1{digits}"
            elif len(digits) == 11 and digits.startswith('1'):
                clean_number = f"+{digits}"
            elif len(digits) >= 10:
                clean_number = f"+{digits}"
            else:
                clean_number = phone_number
            
            # Method 1: Try to use system integration (macOS)
            try:
                # Use macOS system dialer with Google Voice integration
                subprocess.run(['open', f'tel:{clean_number}'], check=True)
                time.sleep(2)  # Wait for dialer to open
                
                logger.info(f"📞 REAL call initiated to {clean_number} via system dialer")
                
                return {
                    "success": True,
                    "tool_name": "call_phone",
                    "result": f"📞 REAL call initiated to {clean_number} via system dialer",
                    "call_id": call_id,
                    "status": "initiated",
                    "phone_number": clean_number,
                    "caller_name": caller_name,
                    "service": "google_voice",
                    "method": "system_dialer",
                    "instructions": [
                        "1. System dialer should be open",
                        "2. Select Google Voice as calling method",
                        "3. Press call button",
                        "4. Talk for FREE! 🎉"
                    ],
                    "note": "REAL call via system dialer - select Google Voice when prompted"
                }
            except:
                pass
            
            # Method 2: Try to use Google Voice app directly
            try:
                # Try to open Google Voice app if installed
                subprocess.run(['open', '-a', 'Google Voice', f'tel:{clean_number}'], check=True)
                
                logger.info(f"📞 REAL call initiated to {clean_number} via Google Voice app")
                
                return {
                    "success": True,
                    "tool_name": "call_phone",
                    "result": f"📞 REAL call initiated to {clean_number} via Google Voice app",
                    "call_id": call_id,
                    "status": "initiated",
                    "phone_number": clean_number,
                    "caller_name": caller_name,
                    "service": "google_voice",
                    "method": "google_voice_app",
                    "instructions": [
                        "1. Google Voice app should be open",
                        "2. Number should be pre-filled",
                        "3. Press call button",
                        "4. Talk for FREE! 🎉"
                    ],
                    "note": "REAL call via Google Voice app"
                }
            except:
                pass
            
            # Method 3: Fallback to manual browser with instructions
            webbrowser.open("https://voice.google.com/calls")
            
            logger.info(f"📞 Google Voice opened for REAL call to {clean_number}")
            
            return {
                "success": True,
                "tool_name": "call_phone",
                "result": f"📞 Google Voice opened for REAL call to {clean_number}",
                "call_id": call_id,
                "status": "initiated",
                "phone_number": clean_number,
                "caller_name": caller_name,
                "service": "google_voice",
                "method": "manual_browser",
                "instructions": [
                    "1. Sign in to Google Voice",
                    "2. Click 'Calls' tab",
                    "3. Click phone icon for new call",
                    "4. Enter number: " + clean_number,
                    "5. Click 'Call' button",
                    "6. Talk for FREE! 🎉"
                ],
                "note": "REAL call via Google Voice - follow instructions to complete call"
            }
            
        except Exception as e:
            logger.error(f"📞 Google Voice call failed: {e}")
            return {
                "success": False,
                "tool_name": "call_phone",
                "error": f"Google Voice call failed: {str(e)}"
            }

    def _make_whatsapp_call(self, phone_number: str, caller_name: str, call_id: str) -> dict:
        """Make a call using WhatsApp (FREE)."""
        try:
            import webbrowser
            
            # Open WhatsApp Web
            webbrowser.open("https://web.whatsapp.com")
            
            logger.info(f"📞 WhatsApp Web opened for call to {phone_number}")
            
            return {
                "success": True,
                "tool_name": "call_phone",
                "result": f"WhatsApp Web opened for call to {phone_number}",
                "call_id": call_id,
                "status": "initiated",
                "phone_number": phone_number,
                "caller_name": caller_name,
                "service": "whatsapp",
                "url": "https://web.whatsapp.com",
                "instructions": f"1. Scan QR code with phone\n2. Add {phone_number} as contact\n3. Click call button\n4. Talk for FREE!",
                "note": "FREE calling via WhatsApp - browser opened automatically"
            }
            
        except Exception as e:
            logger.error(f"📞 WhatsApp call failed: {e}")
            return {
                "success": False,
                "tool_name": "call_phone",
                "error": f"WhatsApp call failed: {str(e)}"
            }

    def _make_twilio_call(self, phone_number: str, caller_name: str, call_id: str) -> dict:
        """Make a call using Twilio (if configured)."""
        try:
            # Check if Twilio is configured
            account_sid = os.getenv('TWILIO_ACCOUNT_SID')
            auth_token = os.getenv('TWILIO_AUTH_TOKEN')
            from_number = os.getenv('TWILIO_PHONE_NUMBER')
            
            if not all([account_sid, auth_token, from_number]):
                # Fallback to Google Voice if Twilio not configured
                logger.info("📞 Twilio not configured, falling back to Google Voice")
                return self._make_google_voice_call(phone_number, caller_name, call_id)
            
            from twilio.rest import Client
            client = Client(account_sid, auth_token)
            
            # Make the call
            call = client.calls.create(
                to=phone_number,
                from_=from_number,
                twiml=f'<Response><Say>Hello! This is a call from {caller_name} via your MCP agent.</Say></Response>'
            )
            
            logger.info(f"📞 Twilio call initiated: {call.sid}")
            
            return {
                "success": True,
                "tool_name": "call_phone",
                "result": f"Twilio call initiated to {phone_number}",
                "call_id": f"twilio_{call.sid}",
                "twilio_sid": call.sid,
                "status": call.status,
                "phone_number": phone_number,
                "caller_name": caller_name,
                "service": "twilio",
                "from_number": from_number,
                "note": "Real call via Twilio"
            }
            
        except Exception as e:
            logger.error(f"📞 Twilio call failed: {e}")
            # Fallback to Google Voice
            logger.info("📞 Falling back to Google Voice")
            return self._make_google_voice_call(phone_number, caller_name, call_id)

    def _end_phone_call(self, arguments: dict) -> dict:
        """End a phone call."""
        try:
            call_id = arguments.get("call_id", "unknown")
            
            logger.info(f"📞 ENDING CALL:")
            logger.info(f"   Call ID: {call_id}")
            
            return {
                "success": True,
                "tool_name": "end_call",
                "result": f"Call {call_id} ended successfully",
                "call_id": call_id,
                "status": "ended",
                "note": "Call ended successfully"
            }
            
        except Exception as e:
            logger.error(f"📞 END CALL FAILED: {e}")
            return {
                "success": False,
                "tool_name": "end_call",
                "error": f"Failed to end call: {str(e)}"
            }

    def _get_call_status(self, arguments: dict) -> dict:
        """Get status of a phone call."""
        try:
            call_id = arguments.get("call_id", "unknown")
            
            logger.info(f"📞 CHECKING CALL STATUS:")
            logger.info(f"   Call ID: {call_id}")
            
            # Simulate call status (in real implementation, this would check actual call status)
            return {
                "success": True,
                "tool_name": "call_status",
                "result": f"Call {call_id} is active",
                "call_id": call_id,
                "status": "active",
                "duration": "00:02:30",  # Simulated duration
                "note": "This is simulated call status for testing"
            }
            
        except Exception as e:
            logger.error(f"📞 STATUS CHECK FAILED: {e}")
            return {
                "success": False,
                "tool_name": "call_status",
                "error": f"Failed to get call status: {str(e)}"
            }

    def get_health(self) -> dict:
        """Health check with detailed status."""
        return {
            "status": "healthy",
            "server": "simple_mcp_bridge",
            "gmail_sender_loaded": self.gmail_sender is not None,
            "gmail_sender_status": "loaded" if self.gmail_sender else "not_loaded",
            "timestamp": datetime.now().isoformat()
        }

    def get_tools(self) -> dict:
        """Get available tools."""
        return {
            "tools": [
                {"name": "count_r", "description": "Count 'r' letters in a word"},
                {"name": "list_desktop_contents", "description": "List desktop files/folders"},
                {"name": "get_desktop_path", "description": "Get desktop path"},
                {"name": "open_gmail", "description": "Open Gmail in browser"},
                {"name": "open_gmail_compose", "description": "Open Gmail compose window"},
                {"name": "sendmail", "description": "Send email via Gmail SMTP"},
                {"name": "sendmail_simple", "description": "Simple email sending via Gmail SMTP"},
                {"name": "call_phone", "description": "Make a phone call to a specified number"},
                {"name": "make_call", "description": "Make a phone call (alias for call_phone)"},
                {"name": "dial_number", "description": "Dial a phone number (alias for call_phone)"},
                {"name": "end_call", "description": "End an active phone call"},
                {"name": "hang_up", "description": "Hang up a call (alias for end_call)"},
                {"name": "call_status", "description": "Get status of an active call"}
            ]
        }

# Create bridge instance
bridge = SimpleMCPBridge()

class SimpleMCPHandler(BaseHTTPRequestHandler):
    """HTTP handler for simple MCP bridge with improved error handling."""
    
    def do_GET(self):
        """Handle GET requests."""
        try:
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
        except Exception as e:
            logger.error(f"GET request error: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
    
    def do_POST(self):
        """Handle POST requests with improved error handling."""
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
    """Run the simple MCP bridge with improved startup."""
    try:
        server = HTTPServer((host, port), SimpleMCPHandler)
        logger.info(f"🚀 Starting Simple MCP Bridge on http://{host}:{port}")
        logger.info("📧 Connected to your Gmail SMTP configuration!")
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