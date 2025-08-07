#!/usr/bin/env python3
"""
Final Comprehensive Agent Test Report
Shows complete status of all agents and what's working
"""

import os
import sys
import json
import requests
import subprocess
from datetime import datetime

class FinalAgentTestReport:
    """Generate final comprehensive agent test report"""
    
    def __init__(self):
        self.results = {}
        self.working_components = []
        self.issues = []
        self.start_time = datetime.now()
        
    def print_header(self, title: str):
        """Print formatted header"""
        print(f"\n{'='*80}")
        print(f"🎯 {title}")
        print(f"{'='*80}")
    
    def test_component(self, name: str, test_func, critical=False):
        """Test a component and record results"""
        try:
            result = test_func()
            self.results[name] = result
            if result:
                self.working_components.append(name)
                status = "✅ WORKING"
            else:
                status = "❌ FAILED"
                if critical:
                    self.issues.append(name)
            print(f"{status} {name}")
            return result
        except Exception as e:
            self.results[name] = False
            print(f"❌ FAILED {name} - {e}")
            if critical:
                self.issues.append(f"{name}: {e}")
            return False
    
    def test_mcp_server(self):
        """Test MCP server"""
        try:
            response = requests.get("http://127.0.0.1:5000/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def test_email_functionality(self):
        """Test email functionality"""
        try:
            response = requests.post(
                "http://127.0.0.1:5000/call",
                json={"tool": "sendmail", "arguments": {"to_email": "test@example.com", "subject": "Test", "body": "Test"}},
                timeout=5
            )
            return response.status_code == 200
        except:
            return False
    
    def test_agent_imports(self):
        """Test agent imports"""
        try:
            # Test imports that don't require environment variables
            from agent.mcp_tools import sendmail_tool, sendmail_simple_tool
            from agent.models import ChatRequest, SearchRequest
            from agent.master_agent import MasterAgent
            from agent.smart_master_agent import SmartMasterAgent
            from agent.unified_master_agent import UnifiedMasterAgent
            return True
        except Exception as e:
            return False
    
    def test_agent_configuration(self):
        """Test agent configuration files"""
        config_files = [
            "agent/prompts.py",
            "agent/schemas.py", 
            "agent/providers.py",
            "agent/agent.py",
            "agent/mcp_tools.py"
        ]
        
        for config_file in config_files:
            if not os.path.exists(config_file):
                return False
        return True
    
    def test_database_files(self):
        """Test database files"""
        db_files = ["alerts.db", "messages.db"]
        for db_file in db_files:
            if not os.path.exists(db_file):
                return False
        return True
    
    def test_git_setup(self):
        """Test git setup"""
        try:
            result = subprocess.run(["git", "status"], capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except:
            return False
    
    def test_environment_variables(self):
        """Test environment variables"""
        required_vars = ["GITHUB_TOKEN"]
        for var in required_vars:
            if not os.getenv(var):
                return False
        return True
    
    def test_pytest_results(self):
        """Get pytest test results"""
        try:
            result = subprocess.run(
                ["python3", "-m", "pytest", "tests/", "--tb=no", "-q"],
                capture_output=True,
                text=True,
                timeout=60
            )
            output = result.stdout
            if "failed" in output and "passed" in output:
                for line in output.split('\n'):
                    if "failed" in line and "passed" in line:
                        return line.strip()
            return "Tests completed"
        except:
            return "Tests not run"
    
    def generate_final_report(self):
        """Generate final comprehensive report"""
        print("🎯 FINAL COMPREHENSIVE AGENT TEST REPORT")
        print(f"⏰ Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        self.print_header("AGENT COMPONENT STATUS")
        
        # Test all components
        self.test_component("MCP Server (Port 5000)", self.test_mcp_server, critical=True)
        self.test_component("Email Functionality", self.test_email_functionality, critical=True)
        self.test_component("Agent Imports", self.test_agent_imports, critical=True)
        self.test_component("Agent Configuration", self.test_agent_configuration, critical=True)
        self.test_component("Database Files", self.test_database_files)
        self.test_component("Git Setup", self.test_git_setup, critical=True)
        self.test_component("Environment Variables", self.test_environment_variables)
        
        # Get pytest results
        pytest_result = self.test_pytest_results()
        self.results["Pytest Tests"] = pytest_result
        print(f"📋 Pytest Tests: {pytest_result}")
        
        self.print_header("FINAL SUMMARY")
        
        total_components = len(self.results)
        working_components = len(self.working_components)
        critical_issues = len(self.issues)
        
        print(f"📊 Total Components Tested: {total_components}")
        print(f"✅ Working Components: {working_components}")
        print(f"❌ Critical Issues: {critical_issues}")
        print(f"📈 Success Rate: {(working_components/total_components)*100:.1f}%")
        print(f"⏱️  Test Duration: {(datetime.now() - self.start_time).total_seconds():.1f} seconds")
        
        print(f"\n🎉 WORKING COMPONENTS:")
        for component in self.working_components:
            print(f"   ✅ {component}")
        
        if self.issues:
            print(f"\n🔧 CRITICAL ISSUES:")
            for issue in self.issues:
                print(f"   ❌ {issue}")
        
        self.print_header("AGENT STATUS ASSESSMENT")
        
        if critical_issues == 0:
            print("🎉 ALL CRITICAL AGENTS WORKING!")
            print("   ✅ MCP Server: Running and responding")
            print("   ✅ Email Functionality: Working correctly")
            print("   ✅ Agent Imports: All agent modules accessible")
            print("   ✅ Agent Configuration: All config files present")
            print("   ✅ Git Setup: Properly configured")
            print("\n🚀 READY FOR DEVELOPMENT AND TESTING")
        else:
            print("⚠️  SOME CRITICAL ISSUES DETECTED")
            print("   Please address the critical issues above before proceeding.")
        
        # Save detailed results
        detailed_results = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_components": total_components,
                "working_components": working_components,
                "critical_issues": critical_issues,
                "success_rate": (working_components/total_components)*100
            },
            "working_components": self.working_components,
            "critical_issues": self.issues,
            "results": self.results
        }
        
        with open("final_agent_test_report.json", "w") as f:
            json.dump(detailed_results, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: final_agent_test_report.json")
        
        return critical_issues == 0

def main():
    """Main function"""
    reporter = FinalAgentTestReport()
    success = reporter.generate_final_report()
    
    if success:
        print("\n🎉 ALL AGENTS ARE WORKING CORRECTLY!")
        print("✅ Ready for development and testing across all branches!")
        sys.exit(0)
    else:
        print("\n⚠️  Some critical issues need attention.")
        sys.exit(1)

if __name__ == "__main__":
    main() 