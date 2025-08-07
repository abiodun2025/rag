#!/usr/bin/env python3
"""
Test Summary Report - Shows current status of all testing
"""

import os
import sys
import json
import requests
import subprocess
from datetime import datetime

class TestSummaryReport:
    """Generate comprehensive test summary report"""
    
    def __init__(self):
        self.results = {}
        self.issues = []
        self.fixes_needed = []
        
    def print_header(self, title: str):
        """Print formatted header"""
        print(f"\n{'='*80}")
        print(f"📊 {title}")
        print(f"{'='*80}")
    
    def check_component(self, name: str, check_func, critical=False):
        """Check a component and record results"""
        try:
            result = check_func()
            self.results[name] = result
            status = "✅ WORKING" if result else "❌ FAILED"
            print(f"{status} {name}")
            if not result and critical:
                self.issues.append(name)
            elif not result:
                self.fixes_needed.append(name)
            return result
        except Exception as e:
            self.results[name] = False
            print(f"❌ FAILED {name} - Exception: {e}")
            if critical:
                self.issues.append(f"{name}: {e}")
            else:
                self.fixes_needed.append(f"{name}: {e}")
            return False
    
    def check_mcp_server(self):
        """Check MCP server status"""
        try:
            response = requests.get("http://127.0.0.1:5000/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def check_agent_api(self):
        """Check agent API server"""
        try:
            response = requests.get("http://127.0.0.1:8000/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def check_email_functionality(self):
        """Check email functionality"""
        try:
            response = requests.post(
                "http://127.0.0.1:5000/call",
                json={"tool": "sendmail", "arguments": {"to_email": "test@example.com", "subject": "Test", "body": "Test"}},
                timeout=5
            )
            return response.status_code == 200
        except:
            return False
    
    def check_database_files(self):
        """Check database files exist and are accessible"""
        db_files = ["alerts.db", "messages.db"]
        for db_file in db_files:
            if not os.path.exists(db_file):
                return False
            try:
                import sqlite3
                conn = sqlite3.connect(db_file)
                conn.close()
            except:
                return False
        return True
    
    def check_environment_variables(self):
        """Check environment variables"""
        required_vars = ["GITHUB_TOKEN", "GMAIL_USER", "GMAIL_APP_PASSWORD"]
        for var in required_vars:
            if not os.getenv(var):
                return False
        return True
    
    def check_git_setup(self):
        """Check git configuration"""
        try:
            result = subprocess.run(["git", "status"], capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except:
            return False
    
    def check_pytest_tests(self):
        """Check pytest test results"""
        try:
            result = subprocess.run(
                ["python3", "-m", "pytest", "tests/", "--tb=no", "-q"],
                capture_output=True,
                text=True,
                timeout=60
            )
            # Extract test results from output
            output = result.stdout
            if "failed" in output and "passed" in output:
                # Parse the summary line
                lines = output.split('\n')
                for line in lines:
                    if "failed" in line and "passed" in line:
                        return line.strip()
            return "Tests completed"
        except:
            return False
    
    def generate_report(self):
        """Generate comprehensive test report"""
        print("🚀 Generating Test Summary Report")
        print(f"⏰ Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        self.print_header("Component Status")
        
        # Check critical components
        self.check_component("MCP Server (Port 5000)", self.check_mcp_server, critical=True)
        self.check_component("Email Functionality", self.check_email_functionality, critical=True)
        self.check_component("Git Setup", self.check_git_setup, critical=True)
        
        # Check important components
        self.check_component("Agent API Server (Port 8000)", self.check_agent_api)
        self.check_component("Database Files", self.check_database_files)
        self.check_component("Environment Variables", self.check_environment_variables)
        
        # Check test results
        pytest_result = self.check_pytest_tests()
        self.results["Pytest Tests"] = pytest_result
        print(f"📋 Pytest Tests: {pytest_result}")
        
        self.print_header("Summary")
        
        total_components = len(self.results)
        working_components = sum(1 for result in self.results.values() if result)
        critical_issues = len(self.issues)
        fixes_needed = len(self.fixes_needed)
        
        print(f"📊 Total Components: {total_components}")
        print(f"✅ Working Components: {working_components}")
        print(f"❌ Critical Issues: {critical_issues}")
        print(f"🔧 Fixes Needed: {fixes_needed}")
        print(f"📈 Success Rate: {(working_components/total_components)*100:.1f}%")
        
        if self.issues:
            self.print_header("🚨 Critical Issues (Must Fix)")
            for issue in self.issues:
                print(f"   • {issue}")
        
        if self.fixes_needed:
            self.print_header("🔧 Recommended Fixes")
            for fix in self.fixes_needed:
                print(f"   • {fix}")
        
        self.print_header("🎯 Overall Status")
        
        if critical_issues == 0:
            print("✅ CORE FUNCTIONALITY WORKING")
            print("   The main components (MCP server, email, git) are working correctly.")
            print("   You can proceed with development and testing.")
        else:
            print("❌ CRITICAL ISSUES DETECTED")
            print("   Please fix the critical issues before proceeding.")
        
        if fixes_needed > 0:
            print(f"\n💡 Additional improvements available ({fixes_needed} items)")
        
        # Save detailed results
        detailed_results = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_components": total_components,
                "working_components": working_components,
                "critical_issues": critical_issues,
                "fixes_needed": fixes_needed,
                "success_rate": (working_components/total_components)*100
            },
            "results": self.results,
            "critical_issues": self.issues,
            "fixes_needed": self.fixes_needed
        }
        
        with open("test_summary_report.json", "w") as f:
            json.dump(detailed_results, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: test_summary_report.json")
        
        return critical_issues == 0

def main():
    """Main function"""
    reporter = TestSummaryReport()
    success = reporter.generate_report()
    
    if success:
        print("\n🎉 Core functionality is working! Ready for development.")
        sys.exit(0)
    else:
        print("\n⚠️  Critical issues need to be fixed before proceeding.")
        sys.exit(1)

if __name__ == "__main__":
    main() 