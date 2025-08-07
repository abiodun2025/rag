#!/usr/bin/env python3
"""
Diagnostic script to identify and fix email body issues
"""

import os
import sys
import json
import requests
import subprocess
from datetime import datetime

class EmailBodyDiagnostic:
    """Diagnose email body issues"""
    
    def __init__(self):
        self.base_url = "http://127.0.0.1:5000"
        self.issues_found = []
        
    def print_header(self, title: str):
        """Print a formatted header"""
        print(f"\n{'='*60}")
        print(f"🔍 {title}")
        print(f"{'='*60}")
    
    def print_result(self, test_name: str, success: bool, details: str = ""):
        """Print test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   └─ {details}")
        
        if not success:
            self.issues_found.append({
                "test": test_name,
                "details": details,
                "timestamp": datetime.now().isoformat()
            })
    
    def check_mcp_server(self) -> bool:
        """Check if MCP server is running"""
        self.print_header("Checking MCP Server")
        
        try:
            # Try health check
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                self.print_result("MCP Server Health", True, "Server is running")
                return True
        except:
            pass
        
        # Try tool list
        try:
            response = requests.post(
                f"{self.base_url}/call",
                json={"tool": "list_tools", "arguments": {}},
                timeout=5
            )
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    tools = result.get("tools", [])
                    sendmail_tools = [t for t in tools if "sendmail" in t.get("name", "")]
                    self.print_result("MCP Server Tools", True, f"Found {len(sendmail_tools)} sendmail tools")
                    return True
        except:
            pass
        
        self.print_result("MCP Server", False, "Server not responding")
        return False
    
    def check_email_credentials(self) -> bool:
        """Check email credentials"""
        self.print_header("Checking Email Credentials")
        
        required_vars = [
            ("GMAIL_USER", "Gmail username"),
            ("GMAIL_APP_PASSWORD", "Gmail app password"),
            ("GOOGLE_EMAIL", "Google email (alternative)"),
            ("GOOGLE_PASSWORD", "Google password (alternative)")
        ]
        
        all_present = True
        for var_name, description in required_vars:
            value = os.getenv(var_name)
            if value and value not in ["your-email@gmail.com", "your-app-password"]:
                self.print_result(f"Credential: {var_name}", True, f"{description} configured")
            else:
                self.print_result(f"Credential: {var_name}", False, f"{description} not configured")
                all_present = False
        
        return all_present
    
    def test_sendmail_tool(self) -> bool:
        """Test sendmail tool directly"""
        self.print_header("Testing Sendmail Tool")
        
        test_data = {
            "tool": "sendmail",
            "arguments": {
                "to_email": "test@example.com",
                "subject": "Email Body Test",
                "body": "This is a test email body.\n\nIt should contain multiple lines.\n\nBest regards,\nTest Script",
                "from_email": ""
            }
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/call",
                headers={"Content-Type": "application/json"},
                json=test_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    self.print_result("Sendmail Tool", True, "Tool responded successfully")
                    
                    # Check the response details
                    response_text = result.get("result", "")
                    if "body" in response_text.lower():
                        self.print_result("Body Handling", True, "Body content detected in response")
                    else:
                        self.print_result("Body Handling", False, "Body content not found in response")
                    
                    return True
                else:
                    error = result.get("error", "Unknown error")
                    self.print_result("Sendmail Tool", False, f"Tool failed: {error}")
                    return False
            else:
                self.print_result("Sendmail Tool", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.print_result("Sendmail Tool", False, f"Exception: {e}")
            return False
    
    def test_sendmail_simple_tool(self) -> bool:
        """Test sendmail_simple tool"""
        self.print_header("Testing Sendmail Simple Tool")
        
        test_data = {
            "tool": "sendmail_simple",
            "arguments": {
                "to_email": "test@example.com",
                "subject": "Simple Email Test",
                "message": "This is a simple test message.\n\nIt should work correctly."
            }
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/call",
                headers={"Content-Type": "application/json"},
                json=test_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    self.print_result("Sendmail Simple Tool", True, "Tool responded successfully")
                    return True
                else:
                    error = result.get("error", "Unknown error")
                    self.print_result("Sendmail Simple Tool", False, f"Tool failed: {error}")
                    return False
            else:
                self.print_result("Sendmail Simple Tool", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.print_result("Sendmail Simple Tool", False, f"Exception: {e}")
            return False
    
    def check_system_sendmail(self) -> bool:
        """Check if system sendmail is available"""
        self.print_header("Checking System Sendmail")
        
        try:
            result = subprocess.run(
                ["which", "sendmail"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                sendmail_path = result.stdout.strip()
                self.print_result("System Sendmail", True, f"Found at: {sendmail_path}")
                
                # Test sendmail functionality
                test_email = """From: test@localhost
To: test@example.com
Subject: System Sendmail Test

This is a test email body.
It should contain multiple lines.

Best regards,
Test Script
"""
                
                result = subprocess.run(
                    ["sendmail", "-t"],
                    input=test_email,
                    text=True,
                    capture_output=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    self.print_result("Sendmail Functionality", True, "Sendmail command works")
                    return True
                else:
                    error = result.stderr.decode() if result.stderr else "Unknown error"
                    self.print_result("Sendmail Functionality", False, f"Error: {error}")
                    return False
            else:
                self.print_result("System Sendmail", False, "Sendmail not found")
                return False
                
        except Exception as e:
            self.print_result("System Sendmail", False, f"Exception: {e}")
            return False
    
    def analyze_email_body_issue(self):
        """Analyze the specific email body issue"""
        self.print_header("Analyzing Email Body Issue")
        
        # Check the test file
        if os.path.exists("test_email_body_issue.py"):
            with open("test_email_body_issue.py", "r") as f:
                content = f.read()
            
            # Look for potential issues
            issues = []
            
            if "body" in content and "arguments" in content:
                # Check if body is properly formatted
                if "\\n" in content:
                    issues.append("Body contains escaped newlines")
                
                if "body" in content and "message" in content:
                    issues.append("Mixed body/message parameters")
            
            if issues:
                for issue in issues:
                    self.print_result("Code Analysis", False, issue)
            else:
                self.print_result("Code Analysis", True, "No obvious code issues found")
        else:
            self.print_result("Test File", False, "test_email_body_issue.py not found")
    
    def check_mcp_server_logs(self):
        """Check MCP server logs for email issues"""
        self.print_header("Checking MCP Server Logs")
        
        # Look for log files
        log_files = [
            "mcp_server.log",
            "test_results.log",
            "email_debug.log"
        ]
        
        for log_file in log_files:
            if os.path.exists(log_file):
                try:
                    with open(log_file, "r") as f:
                        content = f.read()
                    
                    # Look for email-related errors
                    email_errors = []
                    lines = content.split('\n')
                    for i, line in enumerate(lines[-50:]):  # Last 50 lines
                        if "email" in line.lower() and ("error" in line.lower() or "fail" in line.lower()):
                            email_errors.append(f"Line {len(lines)-50+i+1}: {line.strip()}")
                    
                    if email_errors:
                        self.print_result(f"Log Analysis: {log_file}", False, f"Found {len(email_errors)} email errors")
                        for error in email_errors[:3]:  # Show first 3 errors
                            print(f"   └─ {error}")
                    else:
                        self.print_result(f"Log Analysis: {log_file}", True, "No email errors found")
                        
                except Exception as e:
                    self.print_result(f"Log Analysis: {log_file}", False, f"Error reading log: {e}")
            else:
                self.print_result(f"Log File: {log_file}", False, "Log file not found")
    
    def provide_solutions(self):
        """Provide solutions for identified issues"""
        self.print_header("Recommended Solutions")
        
        if not self.issues_found:
            print("✅ No issues found! Email body should work correctly.")
            return
        
        print("🔧 Solutions for identified issues:")
        print()
        
        for issue in self.issues_found:
            test_name = issue["test"]
            details = issue["details"]
            
            if "MCP Server" in test_name:
                print(f"📧 For MCP Server issues:")
                print("   1. Start the MCP server: python simple_mcp_server.py")
                print("   2. Check if port 5000 is available")
                print("   3. Verify server is responding to health checks")
                print()
            
            elif "Credential" in test_name:
                print(f"🔑 For credential issues:")
                print("   1. Set GMAIL_USER environment variable")
                print("   2. Set GMAIL_APP_PASSWORD environment variable")
                print("   3. Use Gmail App Password (not regular password)")
                print("   4. Enable 2-factor authentication on Gmail")
                print()
            
            elif "Sendmail" in test_name:
                print(f"📧 For sendmail issues:")
                print("   1. Install sendmail: brew install sendmail (macOS)")
                print("   2. Configure sendmail for your system")
                print("   3. Use SMTP instead of sendmail")
                print("   4. Check firewall settings")
                print()
            
            elif "Body" in test_name:
                print(f"📝 For email body issues:")
                print("   1. Ensure body parameter is properly formatted")
                print("   2. Use \\n for line breaks in JSON")
                print("   3. Check MIME encoding")
                print("   4. Verify email client compatibility")
                print()
        
        print("💡 Quick Fix Commands:")
        print("   export GMAIL_USER='your-email@gmail.com'")
        print("   export GMAIL_APP_PASSWORD='your-app-password'")
        print("   python simple_mcp_server.py &")
        print("   python test_email_body_issue.py")
    
    def run_diagnosis(self):
        """Run complete diagnosis"""
        print("🔍 Starting Email Body Issue Diagnosis")
        print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Run all checks
        self.check_mcp_server()
        self.check_email_credentials()
        self.test_sendmail_tool()
        self.test_sendmail_simple_tool()
        self.check_system_sendmail()
        self.analyze_email_body_issue()
        self.check_mcp_server_logs()
        
        # Provide solutions
        self.provide_solutions()
        
        # Summary
        self.print_header("Diagnosis Summary")
        print(f"📊 Total Issues Found: {len(self.issues_found)}")
        
        if self.issues_found:
            print("❌ Issues detected. See solutions above.")
            return False
        else:
            print("✅ No issues detected. Email body should work correctly.")
            return True

def main():
    """Main function"""
    diagnostic = EmailBodyDiagnostic()
    success = diagnostic.run_diagnosis()
    
    if success:
        print("\n🎉 Email body issue diagnosis complete - no issues found!")
        sys.exit(0)
    else:
        print("\n⚠️  Issues found. Check the solutions above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 