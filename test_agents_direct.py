#!/usr/bin/env python3
"""
Direct Agent Testing - Tests agents without full API server
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class DirectAgentTester:
    """Test agents directly without API server"""
    
    def __init__(self):
        self.test_results = {}
        self.issues_found = []
        self.start_time = datetime.now()
        
    def print_header(self, title: str):
        """Print formatted header"""
        print(f"\n{'='*60}")
        print(f"🧪 {title}")
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
        
        self.test_results[test_name] = success
    
    def test_agent_imports(self):
        """Test if agent modules can be imported"""
        self.print_header("Testing Agent Imports")
        
        try:
            # Test core agent imports
            from agent.agent import rag_agent, AgentDependencies
            self.print_result("Agent Core", True, "rag_agent and AgentDependencies imported successfully")
        except Exception as e:
            self.print_result("Agent Core", False, f"Import failed: {e}")
        
        try:
            # Test MCP tools
            from agent.mcp_tools import sendmail_tool, sendmail_simple_tool
            self.print_result("MCP Tools", True, "Email tools imported successfully")
        except Exception as e:
            self.print_result("MCP Tools", False, f"Import failed: {e}")
        
        try:
            # Test models
            from agent.models import ChatRequest, SearchRequest
            self.print_result("Agent Models", True, "Request models imported successfully")
        except Exception as e:
            self.print_result("Agent Models", False, f"Import failed: {e}")
        
        try:
            # Test database utilities
            from agent.db_utils import DatabasePool
            self.print_result("Database Utils", True, "Database utilities imported successfully")
        except Exception as e:
            self.print_result("Database Utils", False, f"Import failed: {e}")
    
    def test_master_agent_imports(self):
        """Test master agent imports"""
        self.print_header("Testing Master Agent Imports")
        
        try:
            from agent.master_agent import MasterAgent
            self.print_result("Master Agent", True, "MasterAgent imported successfully")
        except Exception as e:
            self.print_result("Master Agent", False, f"Import failed: {e}")
        
        try:
            from agent.smart_master_agent import SmartMasterAgent
            self.print_result("Smart Master Agent", True, "SmartMasterAgent imported successfully")
        except Exception as e:
            self.print_result("Smart Master Agent", False, f"Import failed: {e}")
        
        try:
            from agent.unified_master_agent import UnifiedMasterAgent
            self.print_result("Unified Master Agent", True, "UnifiedMasterAgent imported successfully")
        except Exception as e:
            self.print_result("Unified Master Agent", False, f"Import failed: {e}")
    
    def test_agent_initialization(self):
        """Test agent initialization"""
        self.print_header("Testing Agent Initialization")
        
        try:
            # Test basic agent initialization
            from agent.agent import AgentDependencies
            
            # Create minimal dependencies for testing
            deps = AgentDependencies(
                vector_search_enabled=True,
                graph_search_enabled=True,
                hybrid_search_enabled=True
            )
            self.print_result("Agent Dependencies", True, "AgentDependencies created successfully")
        except Exception as e:
            self.print_result("Agent Dependencies", False, f"Initialization failed: {e}")
        
        try:
            # Test master agent initialization
            from agent.master_agent import MasterAgent
            
            # This might fail due to missing dependencies, but we can test the import
            self.print_result("Master Agent Class", True, "MasterAgent class accessible")
        except Exception as e:
            self.print_result("Master Agent Class", False, f"Access failed: {e}")
    
    def test_mcp_tools_functionality(self):
        """Test MCP tools functionality"""
        self.print_header("Testing MCP Tools Functionality")
        
        try:
            import requests
            
            # Test MCP server connection
            response = requests.get("http://127.0.0.1:5000/health", timeout=5)
            if response.status_code == 200:
                self.print_result("MCP Server Connection", True, "Server responding on port 5000")
            else:
                self.print_result("MCP Server Connection", False, f"Server returned {response.status_code}")
        except Exception as e:
            self.print_result("MCP Server Connection", False, f"Connection failed: {e}")
        
        try:
            # Test MCP tools list
            response = requests.post(
                "http://127.0.0.1:5000/call",
                json={"tool": "list_tools", "arguments": {}},
                timeout=5
            )
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    tools = result.get("tools", [])
                    email_tools = [t for t in tools if "mail" in t.get("name", "").lower()]
                    self.print_result("MCP Tools List", True, f"Found {len(email_tools)} email tools")
                else:
                    self.print_result("MCP Tools List", False, f"Failed to get tools: {result.get('error')}")
            else:
                self.print_result("MCP Tools List", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.print_result("MCP Tools List", False, f"Request failed: {e}")
    
    def test_email_functionality(self):
        """Test email functionality"""
        self.print_header("Testing Email Functionality")
        
        try:
            import requests
            
            # Test sendmail tool
            test_data = {
                "tool": "sendmail",
                "arguments": {
                    "to_email": "test@example.com",
                    "subject": "Agent Test",
                    "body": "This is a test email from agent testing.",
                    "from_email": ""
                }
            }
            
            response = requests.post(
                "http://127.0.0.1:5000/call",
                json=test_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    self.print_result("Email Sendmail Tool", True, "Email tool working correctly")
                else:
                    self.print_result("Email Sendmail Tool", False, f"Tool failed: {result.get('error')}")
            else:
                self.print_result("Email Sendmail Tool", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.print_result("Email Sendmail Tool", False, f"Request failed: {e}")
        
        try:
            # Test sendmail_simple tool
            test_data = {
                "tool": "sendmail_simple",
                "arguments": {
                    "to_email": "test@example.com",
                    "subject": "Simple Agent Test",
                    "message": "This is a simple test email from agent testing."
                }
            }
            
            response = requests.post(
                "http://127.0.0.1:5000/call",
                json=test_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    self.print_result("Email Simple Tool", True, "Simple email tool working correctly")
                else:
                    self.print_result("Email Simple Tool", False, f"Tool failed: {result.get('error')}")
            else:
                self.print_result("Email Simple Tool", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.print_result("Email Simple Tool", False, f"Request failed: {e}")
    
    def test_agent_configuration(self):
        """Test agent configuration"""
        self.print_header("Testing Agent Configuration")
        
        try:
            # Test configuration files
            config_files = [
                "agent/prompts.py",
                "agent/schemas.py",
                "agent/providers.py"
            ]
            
            for config_file in config_files:
                if os.path.exists(config_file):
                    self.print_result(f"Config: {config_file}", True, "Configuration file exists")
                else:
                    self.print_result(f"Config: {config_file}", False, "Configuration file missing")
        except Exception as e:
            self.print_result("Configuration Files", False, f"Check failed: {e}")
        
        try:
            # Test environment variables
            required_vars = ["GITHUB_TOKEN"]
            missing_vars = []
            
            for var in required_vars:
                if not os.getenv(var):
                    missing_vars.append(var)
            
            if not missing_vars:
                self.print_result("Environment Variables", True, "Required variables set")
            else:
                self.print_result("Environment Variables", False, f"Missing: {missing_vars}")
        except Exception as e:
            self.print_result("Environment Variables", False, f"Check failed: {e}")
    
    def print_summary(self):
        """Print test summary"""
        self.print_header("Direct Agent Test Summary")
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result)
        failed_tests = total_tests - passed_tests
        
        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"📈 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print(f"⏱️  Test Duration: {(datetime.now() - self.start_time).total_seconds():.1f} seconds")
        
        if self.issues_found:
            print(f"\n🔧 Issues Found:")
            for issue in self.issues_found:
                print(f"   • {issue['test']}: {issue['details']}")
        
        print(f"\n🎯 Overall Status: {'✅ AGENTS WORKING' if failed_tests == 0 else '❌ ISSUES FOUND'}")
    
    def run_all_tests(self):
        """Run all direct agent tests"""
        print("🚀 Starting Direct Agent Testing")
        print(f"⏰ Started at: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Run all test categories
        self.test_agent_imports()
        self.test_master_agent_imports()
        self.test_agent_initialization()
        self.test_mcp_tools_functionality()
        self.test_email_functionality()
        self.test_agent_configuration()
        
        # Print summary
        self.print_summary()
        
        return len(self.issues_found) == 0

def main():
    """Main function"""
    tester = DirectAgentTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All agents are working correctly!")
        sys.exit(0)
    else:
        print("\n⚠️  Some agent issues found. Check the details above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 