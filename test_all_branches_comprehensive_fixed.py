#!/usr/bin/env python3
"""
Fixed Comprehensive testing script for all branches
Tests all code on all branches and identifies issues that need fixing
"""

import json
import logging
import os
import subprocess
import sys
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import requests
import sqlite3

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_results.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ComprehensiveBranchTester:
    """Comprehensive testing framework for all branches"""
    
    def __init__(self):
        self.base_url = "http://127.0.0.1:5000"
        self.test_results = {}
        self.branch_results = {}
        self.issues_found = []
        self.start_time = datetime.now()
        
    def print_header(self, title: str):
        """Print a formatted header"""
        print(f"\n{'='*80}")
        print(f"🧪 {title}")
        print(f"{'='*80}")
    
    def print_result(self, test_name: str, success: bool, details: str = "", branch: str = "main"):
        """Print test result with branch context"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} [{branch}] {test_name}")
        if details:
            print(f"   └─ {details}")
        
        if not success:
            self.issues_found.append({
                "branch": branch,
                "test": test_name,
                "details": details,
                "timestamp": datetime.now().isoformat()
            })
        
        # Store results
        if branch not in self.test_results:
            self.test_results[branch] = {}
        self.test_results[branch][test_name] = success
    
    def check_prerequisites(self) -> bool:
        """Check if all prerequisites are met"""
        self.print_header("Checking Prerequisites")
        
        checks = [
            ("Python Version", self.check_python_version),
            ("Dependencies", self.check_dependencies),
            ("Environment Variables", self.check_environment),
            ("MCP Server", self.check_mcp_server),
            ("Database", self.check_database),
            ("Git Setup", self.check_git_setup),
        ]
        
        all_passed = True
        for check_name, check_func in checks:
            try:
                result = check_func()
                self.print_result(check_name, result)
                if not result:
                    all_passed = False
            except Exception as e:
                self.print_result(check_name, False, f"Exception: {e}")
                all_passed = False
        
        return all_passed
    
    def check_python_version(self) -> bool:
        """Check Python version"""
        version = sys.version_info
        if version.major >= 3 and version.minor >= 8:
            return True
        return False
    
    def check_dependencies(self) -> bool:
        """Check if required packages are installed"""
        required_packages = [
            "pytest", "requests", "aiohttp", "sqlite3", 
            "anthropic", "openai", "neo4j", "fastapi"
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            logger.error(f"Missing packages: {missing_packages}")
            return False
        return True
    
    def check_environment(self) -> bool:
        """Check environment variables"""
        required_vars = [
            "GITHUB_TOKEN",
            "GMAIL_USER", 
            "GMAIL_APP_PASSWORD"
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            logger.warning(f"Missing environment variables: {missing_vars}")
            return False
        return True
    
    def check_mcp_server(self) -> bool:
        """Check if MCP server is running"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                return True
        except:
            pass
        
        # Try alternative health check
        try:
            response = requests.post(
                f"{self.base_url}/call",
                json={"tool": "list_tools", "arguments": {}},
                timeout=5
            )
            if response.status_code == 200:
                return True
        except:
            pass
        
        return False
    
    def check_database(self) -> bool:
        """Check database connectivity"""
        try:
            # Check if database files exist
            db_files = ["alerts.db", "messages.db"]
            for db_file in db_files:
                if os.path.exists(db_file):
                    # Try to connect
                    conn = sqlite3.connect(db_file)
                    conn.close()
            return True
        except Exception as e:
            logger.error(f"Database check failed: {e}")
            return False
    
    def check_git_setup(self) -> bool:
        """Check git configuration"""
        try:
            result = subprocess.run(
                ["git", "status"], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Git check failed: {e}")
            return False
    
    def get_all_branches(self) -> List[Dict[str, Any]]:
        """Get all branches from the repository"""
        self.print_header("Getting All Branches")
        
        try:
            # Use git command to get branches
            result = subprocess.run(
                ["git", "branch", "-r"], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            
            if result.returncode != 0:
                logger.error(f"Failed to get branches: {result.stderr}")
                return []
            
            branches = []
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    branch_name = line.strip().replace('origin/', '')
                    branches.append({
                        "name": branch_name,
                        "has_commits": True  # We'll check this later
                    })
            
            # Also get local branches
            result = subprocess.run(
                ["git", "branch"], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line.strip() and not line.startswith('*'):
                        branch_name = line.strip()
                        if not any(b["name"] == branch_name for b in branches):
                            branches.append({
                                "name": branch_name,
                                "has_commits": True
                            })
            
            print(f"📋 Found {len(branches)} branches")
            return branches
            
        except Exception as e:
            logger.error(f"Error getting branches: {e}")
            return []
    
    def check_branch_commits(self, branch_name: str) -> bool:
        """Check if branch has new commits compared to main"""
        try:
            result = subprocess.run(
                ["git", "rev-list", "--count", f"main..{branch_name}"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                commit_count = int(result.stdout.strip())
                return commit_count > 0
            return False
        except Exception as e:
            logger.error(f"Error checking commits for {branch_name}: {e}")
            return False
    
    def checkout_branch(self, branch_name: str) -> bool:
        """Checkout a specific branch"""
        try:
            result = subprocess.run(
                ["git", "checkout", branch_name],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                print(f"✅ Checked out branch: {branch_name}")
                return True
            else:
                logger.error(f"Failed to checkout {branch_name}: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Error checking out {branch_name}: {e}")
            return False
    
    def run_pytest_tests(self, branch_name: str) -> bool:
        """Run pytest tests for the current branch"""
        self.print_header(f"Running Pytest Tests - Branch: {branch_name}")
        
        try:
            # Run pytest with coverage
            result = subprocess.run([
                "python3", "-m", "pytest",
                "--cov=agent",
                "--cov=ingestion", 
                "--cov-report=term-missing",
                "--cov-report=html:htmlcov",
                "-v"
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                self.print_result("Pytest Tests", True, "All tests passed", branch_name)
                
                # Extract coverage information
                coverage_lines = [line for line in result.stdout.split('\n') if 'TOTAL' in line]
                if coverage_lines:
                    self.print_result("Coverage Report", True, coverage_lines[-1], branch_name)
                
                return True
            else:
                self.print_result("Pytest Tests", False, f"Tests failed: {result.stderr}", branch_name)
                return False
                
        except subprocess.TimeoutExpired:
            self.print_result("Pytest Tests", False, "Tests timed out", branch_name)
            return False
        except Exception as e:
            self.print_result("Pytest Tests", False, f"Exception: {e}", branch_name)
            return False
    
    def run_integration_tests(self, branch_name: str) -> bool:
        """Run integration tests"""
        self.print_header(f"Running Integration Tests - Branch: {branch_name}")
        
        integration_tests = [
            "test_all_agents.py",
            "test_alert_system.py",
            "test_mcp_integration.py",
            "test_email_body_fixed.py"
        ]
        
        all_passed = True
        
        for test_file in integration_tests:
            if os.path.exists(test_file):
                try:
                    result = subprocess.run(
                        ["python3", test_file],
                        capture_output=True,
                        text=True,
                        timeout=60
                    )
                    
                    if result.returncode == 0:
                        self.print_result(f"Integration: {test_file}", True, "", branch_name)
                    else:
                        self.print_result(f"Integration: {test_file}", False, result.stderr, branch_name)
                        all_passed = False
                        
                except subprocess.TimeoutExpired:
                    self.print_result(f"Integration: {test_file}", False, "Timeout", branch_name)
                    all_passed = False
                except Exception as e:
                    self.print_result(f"Integration: {test_file}", False, f"Exception: {e}", branch_name)
                    all_passed = False
            else:
                self.print_result(f"Integration: {test_file}", False, "File not found", branch_name)
                all_passed = False
        
        return all_passed
    
    def run_branch_specific_tests(self, branch_name: str) -> bool:
        """Run branch-specific tests"""
        self.print_header(f"Running Branch-Specific Tests - Branch: {branch_name}")
        
        branch_tests = [
            "test_branch_agent.py",
            "test_branch_agent_real.py", 
            "test_full_branch_workflow.py",
            "test_enhanced_pr_creation.py"
        ]
        
        all_passed = True
        
        for test_file in branch_tests:
            if os.path.exists(test_file):
                try:
                    result = subprocess.run(
                        ["python3", test_file],
                        capture_output=True,
                        text=True,
                        timeout=120
                    )
                    
                    if result.returncode == 0:
                        self.print_result(f"Branch Test: {test_file}", True, "", branch_name)
                    else:
                        self.print_result(f"Branch Test: {test_file}", False, result.stderr, branch_name)
                        all_passed = False
                        
                except subprocess.TimeoutExpired:
                    self.print_result(f"Branch Test: {test_file}", False, "Timeout", branch_name)
                    all_passed = False
                except Exception as e:
                    self.print_result(f"Branch Test: {test_file}", False, f"Exception: {e}", branch_name)
                    all_passed = False
            else:
                self.print_result(f"Branch Test: {test_file}", False, "File not found", branch_name)
                all_passed = False
        
        return all_passed
    
    def test_email_body_issue(self, branch_name: str) -> bool:
        """Specifically test the email body issue"""
        self.print_header(f"Testing Email Body Issue - Branch: {branch_name}")
        
        try:
            # Check if the test file exists
            if not os.path.exists("test_email_body_fixed.py"):
                self.print_result("Email Body Test", False, "Test file not found", branch_name)
                return False
            
            # Run the specific test
            result = subprocess.run(
                ["python3", "test_email_body_fixed.py"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                self.print_result("Email Body Test", True, "Email body issue resolved", branch_name)
                return True
            else:
                self.print_result("Email Body Test", False, f"Email body issue persists: {result.stderr}", branch_name)
                return False
                
        except Exception as e:
            self.print_result("Email Body Test", False, f"Exception: {e}", branch_name)
            return False
    
    def test_mcp_tools(self, branch_name: str) -> bool:
        """Test MCP tools functionality"""
        self.print_header(f"Testing MCP Tools - Branch: {branch_name}")
        
        try:
            response = requests.post(
                f"{self.base_url}/call",
                json={"tool": "list_tools", "arguments": {}},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    tools = result.get("tools", [])
                    self.print_result("MCP Tools", True, f"Found {len(tools)} tools", branch_name)
                    return True
                else:
                    self.print_result("MCP Tools", False, f"Failed to get tools: {result.get('error')}", branch_name)
                    return False
            else:
                self.print_result("MCP Tools", False, f"HTTP {response.status_code}", branch_name)
                return False
                
        except Exception as e:
            self.print_result("MCP Tools", False, f"Exception: {e}", branch_name)
            return False
    
    def save_test_results(self):
        """Save test results to file"""
        results = {
            "timestamp": self.start_time.isoformat(),
            "duration": (datetime.now() - self.start_time).total_seconds(),
            "test_results": self.test_results,
            "issues_found": self.issues_found,
            "summary": {
                "total_branches": len(self.test_results),
                "branches_with_issues": len([b for b in self.test_results.values() if not all(b.values())]),
                "total_issues": len(self.issues_found)
            }
        }
        
        with open("comprehensive_test_results.json", "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"\n📊 Test results saved to: comprehensive_test_results.json")
    
    def print_summary(self):
        """Print comprehensive test summary"""
        self.print_header("Comprehensive Test Summary")
        
        total_branches = len(self.test_results)
        branches_with_issues = len([b for b in self.test_results.values() if not all(b.values())])
        total_issues = len(self.issues_found)
        
        print(f"📊 Total Branches Tested: {total_branches}")
        print(f"✅ Branches Without Issues: {total_branches - branches_with_issues}")
        print(f"❌ Branches With Issues: {branches_with_issues}")
        print(f"🔧 Total Issues Found: {total_issues}")
        print(f"⏱️  Total Test Duration: {(datetime.now() - self.start_time).total_seconds():.1f} seconds")
        
        if self.issues_found:
            print(f"\n🔧 Issues Found:")
            for issue in self.issues_found:
                print(f"   • [{issue['branch']}] {issue['test']}: {issue['details']}")
        
        print(f"\n🎯 Overall Status: {'✅ ALL BRANCHES PASSED' if branches_with_issues == 0 else '❌ ISSUES FOUND'}")
    
    def run_comprehensive_testing(self):
        """Run comprehensive testing on all branches"""
        print("🚀 Starting Comprehensive Branch Testing")
        print(f"⏰ Started at: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Check prerequisites
        if not self.check_prerequisites():
            print("\n❌ Prerequisites not met. Please fix the issues above and try again.")
            return False
        
        # Get all branches
        branches = self.get_all_branches()
        if not branches:
            print("\n❌ No branches found or error getting branches.")
            return False
        
        # Test each branch
        for branch in branches:
            branch_name = branch["name"]
            
            # Skip main branch for now (test it last)
            if branch_name == "main":
                continue
            
            print(f"\n🌿 Testing Branch: {branch_name}")
            
            # Check if branch has commits
            has_commits = self.check_branch_commits(branch_name)
            if not has_commits:
                self.print_result("Branch Commits", False, "No new commits", branch_name)
                continue
            
            # Checkout branch
            if not self.checkout_branch(branch_name):
                continue
            
            # Run tests
            self.run_pytest_tests(branch_name)
            self.run_integration_tests(branch_name)
            self.run_branch_specific_tests(branch_name)
            self.test_email_body_issue(branch_name)
            self.test_mcp_tools(branch_name)
        
        # Test main branch last
        print(f"\n🌿 Testing Main Branch")
        self.checkout_branch("main")
        self.run_pytest_tests("main")
        self.run_integration_tests("main")
        self.run_branch_specific_tests("main")
        self.test_email_body_issue("main")
        self.test_mcp_tools("main")
        
        # Save results and print summary
        self.save_test_results()
        self.print_summary()
        
        return len(self.issues_found) == 0

def main():
    """Main function"""
    tester = ComprehensiveBranchTester()
    success = tester.run_comprehensive_testing()
    
    if success:
        print("\n🎉 All branches passed comprehensive testing!")
        sys.exit(0)
    else:
        print("\n⚠️  Issues found. Check the detailed report above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 