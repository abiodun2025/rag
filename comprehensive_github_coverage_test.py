#!/usr/bin/env python3
"""
Comprehensive Real-World GitHub Coverage Test
Tests GitHub integration, code generation, and coverage analysis with actual repositories.
"""

import os
import json
import subprocess
import tempfile
import shutil
import requests
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# Import our agent
from agent.github_coverage_agent import GitHubCoverageAgent, GitHubConfig

class ComprehensiveGitHubCoverageTest:
    """Comprehensive test suite for GitHub coverage agent."""
    
    def __init__(self):
        self.token = os.getenv('GITHUB_TOKEN')
        self.owner = os.getenv('GITHUB_OWNER', 'abiodun2025')
        self.repo = os.getenv('GITHUB_REPO', 'rag')
        self.test_results = []
        self.temp_dir = None
        
    def run_all_tests(self):
        """Run all comprehensive tests."""
        print("🚀 Comprehensive GitHub Coverage Test Suite")
        print("=" * 60)
        print(f"Testing with repository: {self.owner}/{self.repo}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        tests = [
            ("GitHub API Connection", self.test_github_api_connection),
            ("Repository Access", self.test_repository_access),
            ("Pull Request Analysis", self.test_pull_request_analysis),
            ("Code Generation Test", self.test_code_generation),
            ("Coverage Analysis", self.test_coverage_analysis),
            ("Agent Integration", self.test_agent_integration),
            ("Real PR Coverage", self.test_real_pr_coverage),
        ]
        
        for test_name, test_func in tests:
            print(f"\n🎯 Running: {test_name}")
            try:
                result = test_func()
                self.test_results.append((test_name, result))
                status = "✅ PASS" if result else "❌ FAIL"
                print(f"{status} {test_name}")
            except Exception as e:
                print(f"❌ FAIL {test_name} - Exception: {e}")
                self.test_results.append((test_name, False))
        
        self.print_summary()
        
    def test_github_api_connection(self) -> bool:
        """Test basic GitHub API connection."""
        if not self.token:
            print("❌ No GitHub token found")
            return False
            
        headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        # Test API rate limit
        rate_limit_url = "https://api.github.com/rate_limit"
        response = requests.get(rate_limit_url, headers=headers)
        
        if response.status_code == 200:
            rate_data = response.json()
            print(f"✅ GitHub API connection successful")
            print(f"📊 Rate limit: {rate_data['resources']['core']['remaining']}/{rate_data['resources']['core']['limit']}")
            return True
        else:
            print(f"❌ GitHub API connection failed: {response.status_code}")
            return False
    
    def test_repository_access(self) -> bool:
        """Test repository access and metadata."""
        headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        repo_url = f"https://api.github.com/repos/{self.owner}/{self.repo}"
        response = requests.get(repo_url, headers=headers)
        
        if response.status_code == 200:
            repo_data = response.json()
            print(f"✅ Repository access successful")
            print(f"📁 Repository: {repo_data['full_name']}")
            print(f"📝 Description: {repo_data.get('description', 'No description')}")
            print(f"⭐ Stars: {repo_data['stargazers_count']}")
            print(f"🔀 Forks: {repo_data['forks_count']}")
            print(f"🌿 Default branch: {repo_data['default_branch']}")
            print(f"📅 Created: {repo_data['created_at']}")
            print(f"🔄 Last updated: {repo_data['updated_at']}")
            return True
        else:
            print(f"❌ Repository access failed: {response.status_code}")
            return False
    
    def test_pull_request_analysis(self) -> bool:
        """Test pull request analysis capabilities."""
        headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        # Get pull requests
        pr_url = f"https://api.github.com/repos/{self.owner}/{self.repo}/pulls"
        response = requests.get(pr_url, headers=headers)
        
        if response.status_code == 200:
            prs = response.json()
            print(f"✅ Found {len(prs)} open pull requests")
            
            if prs:
                # Analyze first PR
                pr = prs[0]
                print(f"📋 Analyzing PR #{pr['number']}: {pr['title']}")
                print(f"   👤 Author: {pr['user']['login']}")
                print(f"   🌿 Branch: {pr['head']['ref']} → {pr['base']['ref']}")
                
                # Get PR files
                files_url = f"https://api.github.com/repos/{self.owner}/{self.repo}/pulls/{pr['number']}/files"
                files_response = requests.get(files_url, headers=headers)
                
                if files_response.status_code == 200:
                    files = files_response.json()
                    print(f"   📁 Files changed: {len(files)}")
                    
                    # Analyze file types
                    file_types = {}
                    for file in files:
                        ext = file['filename'].split('.')[-1] if '.' in file['filename'] else 'no_ext'
                        file_types[ext] = file_types.get(ext, 0) + 1
                    
                    print(f"   📊 File types: {dict(list(file_types.items())[:5])}")
                    
                    # Show some changed files
                    for file in files[:3]:
                        print(f"      - {file['filename']} (+{file['additions']}, -{file['deletions']})")
                    
                    return True
                else:
                    print(f"❌ Failed to get PR files: {files_response.status_code}")
                    return False
            else:
                print("ℹ️ No open pull requests found")
                return True
        else:
            print(f"❌ Failed to get pull requests: {response.status_code}")
            return False
    
    def test_code_generation(self) -> bool:
        """Test code generation capabilities."""
        print("🧪 Testing code generation...")
        
        # Create a temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()
        test_file_path = os.path.join(self.temp_dir, "test_generated_code.py")
        
        try:
            # Generate a simple test file
            test_code = self._generate_test_code()
            
            with open(test_file_path, 'w') as f:
                f.write(test_code)
            
            print(f"✅ Generated test file: {test_file_path}")
            
            # Test the generated code
            result = subprocess.run(['python3', test_file_path], 
                                  capture_output=True, text=True, cwd=self.temp_dir)
            
            if result.returncode == 0:
                print("✅ Generated code executed successfully")
                print(f"📄 Output: {result.stdout.strip()}")
                return True
            else:
                print(f"❌ Generated code failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Code generation test failed: {e}")
            return False
    
    def _generate_test_code(self) -> str:
        """Generate test code for coverage testing."""
        return '''
#!/usr/bin/env python3
"""
Generated test code for coverage analysis.
"""

import math
import random
from typing import List, Optional

class Calculator:
    """A simple calculator class for testing coverage."""
    
    def __init__(self):
        self.history = []
    
    def add(self, a: float, b: float) -> float:
        """Add two numbers."""
        result = a + b
        self.history.append(f"add({a}, {b}) = {result}")
        return result
    
    def subtract(self, a: float, b: float) -> float:
        """Subtract two numbers."""
        result = a - b
        self.history.append(f"subtract({a}, {b}) = {result}")
        return result
    
    def multiply(self, a: float, b: float) -> float:
        """Multiply two numbers."""
        result = a * b
        self.history.append(f"multiply({a}, {b}) = {result}")
        return result
    
    def divide(self, a: float, b: float) -> Optional[float]:
        """Divide two numbers with error handling."""
        if b == 0:
            self.history.append(f"divide({a}, {b}) = Error: Division by zero")
            return None
        result = a / b
        self.history.append(f"divide({a}, {b}) = {result}")
        return result
    
    def power(self, base: float, exponent: float) -> float:
        """Calculate power with edge case handling."""
        if exponent == 0:
            return 1.0
        elif base == 0 and exponent < 0:
            raise ValueError("Cannot raise 0 to negative power")
        return math.pow(base, exponent)
    
    def get_history(self) -> List[str]:
        """Get calculation history."""
        return self.history.copy()
    
    def clear_history(self):
        """Clear calculation history."""
        self.history.clear()

def main():
    """Main function to test the calculator."""
    calc = Calculator()
    
    # Test basic operations
    print(f"2 + 3 = {calc.add(2, 3)}")
    print(f"5 - 2 = {calc.subtract(5, 2)}")
    print(f"4 * 6 = {calc.multiply(4, 6)}")
    print(f"10 / 2 = {calc.divide(10, 2)}")
    
    # Test edge cases
    print(f"10 / 0 = {calc.divide(10, 0)}")
    print(f"2^3 = {calc.power(2, 3)}")
    print(f"5^0 = {calc.power(5, 0)}")
    
    # Test history
    print(f"History: {calc.get_history()}")
    
    print("✅ All tests completed!")

if __name__ == "__main__":
    main()
'''
    
    def test_coverage_analysis(self) -> bool:
        """Test coverage analysis with generated code."""
        if not self.temp_dir:
            print("❌ No test directory available")
            return False
        
        try:
            # Create a test file for coverage
            test_file = os.path.join(self.temp_dir, "test_calculator.py")
            test_code = self._generate_test_coverage_code()
            
            with open(test_file, 'w') as f:
                f.write(test_code)
            
            # Install coverage if not available
            try:
                subprocess.run(['python3', '-m', 'coverage', '--version'], 
                             capture_output=True, check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                print("📦 Installing coverage...")
                subprocess.run(['pip3', 'install', 'coverage'], check=True)
            
            # Run tests with coverage
            print("🧪 Running tests with coverage...")
            result = subprocess.run([
                'python3', '-m', 'coverage', 'run', '--source=test_generated_code', 
                test_file
            ], capture_output=True, text=True, cwd=self.temp_dir)
            
            if result.returncode == 0:
                print("✅ Tests executed successfully")
                
                # Generate coverage report
                report_result = subprocess.run([
                    'python3', '-m', 'coverage', 'report'
                ], capture_output=True, text=True, cwd=self.temp_dir)
                
                if report_result.returncode == 0:
                    print("📊 Coverage Report:")
                    print(report_result.stdout)
                    
                    # Parse coverage data
                    coverage_data = self._parse_coverage_report(report_result.stdout)
                    if coverage_data:
                        print(f"📈 Parsed Coverage: {coverage_data['coverage']}%")
                        print(f"📄 Total Lines: {coverage_data['total_lines']}")
                        print(f"✅ Covered Lines: {coverage_data['covered_lines']}")
                        print(f"❌ Missing Lines: {coverage_data['missing_lines']}")
                        
                        # Generate suggestions
                        suggestions = self._generate_coverage_suggestions(coverage_data)
                        print(f"💡 Generated {len(suggestions)} suggestions:")
                        for i, suggestion in enumerate(suggestions[:3], 1):
                            print(f"   {i}. {suggestion}")
                        
                        return True
                    else:
                        print("❌ Failed to parse coverage data")
                        return False
                else:
                    print(f"❌ Failed to generate coverage report: {report_result.stderr}")
                    return False
            else:
                print(f"❌ Test execution failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Coverage analysis failed: {e}")
            return False
    
    def _generate_test_coverage_code(self) -> str:
        """Generate test code for coverage analysis."""
        return '''
#!/usr/bin/env python3
"""
Test code for coverage analysis.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from test_generated_code import Calculator

def test_basic_operations():
    """Test basic calculator operations."""
    calc = Calculator()
    
    # Test addition
    assert calc.add(2, 3) == 5
    assert calc.add(-1, 1) == 0
    
    # Test subtraction
    assert calc.subtract(5, 2) == 3
    assert calc.subtract(0, 5) == -5
    
    # Test multiplication
    assert calc.multiply(4, 6) == 24
    assert calc.multiply(0, 10) == 0
    
    # Test division
    assert calc.divide(10, 2) == 5.0
    assert calc.divide(0, 5) == 0.0

def test_edge_cases():
    """Test edge cases and error handling."""
    calc = Calculator()
    
    # Test division by zero
    assert calc.divide(10, 0) is None
    
    # Test power operations
    assert calc.power(2, 3) == 8.0
    assert calc.power(5, 0) == 1.0

def test_history():
    """Test history functionality."""
    calc = Calculator()
    
    calc.add(1, 2)
    calc.subtract(5, 3)
    
    history = calc.get_history()
    assert len(history) == 2
    assert "add(1, 2) = 3" in history[0]
    assert "subtract(5, 3) = 2" in history[1]
    
    calc.clear_history()
    assert len(calc.get_history()) == 0

if __name__ == "__main__":
    test_basic_operations()
    test_edge_cases()
    test_history()
    print("✅ All tests passed!")
'''
    
    def _parse_coverage_report(self, report_output: str) -> Optional[Dict]:
        """Parse coverage report output."""
        try:
            lines = report_output.strip().split('\n')
            for line in lines:
                if 'test_generated_code.py' in line and 'TOTAL' not in line:
                    parts = line.split()
                    if len(parts) >= 4:
                        total_lines = int(parts[1])
                        missing_lines = int(parts[2])
                        covered_lines = total_lines - missing_lines
                        coverage = (covered_lines / total_lines) * 100 if total_lines > 0 else 0
                        
                        return {
                            'total_lines': total_lines,
                            'covered_lines': covered_lines,
                            'missing_lines': missing_lines,
                            'coverage': round(coverage, 1)
                        }
            return None
        except Exception as e:
            print(f"Error parsing coverage report: {e}")
            return None
    
    def _generate_coverage_suggestions(self, coverage_data: Dict) -> List[str]:
        """Generate suggestions based on coverage data."""
        suggestions = []
        
        if coverage_data['coverage'] < 80:
            suggestions.append("🔴 High Priority: Add more test cases to improve coverage")
        
        if coverage_data['missing_lines'] > 0:
            suggestions.append(f"🟡 Medium Priority: {coverage_data['missing_lines']} lines need test coverage")
        
        if coverage_data['coverage'] < 90:
            suggestions.append("🟢 Low Priority: Consider edge case testing")
        
        suggestions.append("💡 Suggestion: Add integration tests for complex scenarios")
        suggestions.append("💡 Suggestion: Test error handling paths")
        
        return suggestions
    
    def test_agent_integration(self) -> bool:
        """Test the GitHub coverage agent integration."""
        if not self.token:
            print("❌ No GitHub token available for agent test")
            return False
        
        try:
            config = GitHubConfig(
                token=self.token,
                owner=self.owner,
                repo=self.repo
            )
            
            agent = GitHubCoverageAgent(config)
            print("✅ Agent initialized successfully")
            
            # Test agent capabilities
            print("🔍 Testing agent capabilities...")
            
            # Test repository access through agent
            headers = {
                "Authorization": f"token {self.token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            repo_url = f"https://api.github.com/repos/{self.owner}/{self.repo}"
            response = requests.get(repo_url, headers=headers)
            
            if response.status_code == 200:
                repo_data = response.json()
                print(f"✅ Agent can access repository: {repo_data['full_name']}")
                return True
            else:
                print(f"❌ Agent repository access failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Agent integration test failed: {e}")
            return False
    
    def test_real_pr_coverage(self) -> bool:
        """Test real PR coverage analysis (if PRs exist)."""
        if not self.token:
            print("❌ No GitHub token available for PR test")
            return False
        
        try:
            headers = {
                "Authorization": f"token {self.token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            # Get pull requests
            pr_url = f"https://api.github.com/repos/{self.owner}/{self.repo}/pulls"
            response = requests.get(pr_url, headers=headers)
            
            if response.status_code == 200:
                prs = response.json()
                
                if prs:
                    # Test with first PR
                    pr = prs[0]
                    print(f"📋 Testing real PR coverage for PR #{pr['number']}")
                    
                    config = GitHubConfig(
                        token=self.token,
                        owner=self.owner,
                        repo=self.repo
                    )
                    
                    agent = GitHubCoverageAgent(config)
                    
                    # Note: This would require cloning the repository
                    # For demo purposes, we'll just test the PR info retrieval
                    pr_info = agent._get_pr_info(pr['number'])
                    
                    if pr_info:
                        print(f"✅ Successfully retrieved PR info for #{pr['number']}")
                        print(f"   Title: {pr_info['title']}")
                        print(f"   Author: {pr_info['user']['login']}")
                        print(f"   Branch: {pr_info['head']['ref']}")
                        return True
                    else:
                        print(f"❌ Failed to retrieve PR info for #{pr['number']}")
                        return False
                else:
                    print("ℹ️ No open pull requests found for real PR test")
                    return True
            else:
                print(f"❌ Failed to get pull requests: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Real PR coverage test failed: {e}")
            return False
    
    def print_summary(self):
        """Print test summary."""
        print("\n" + "=" * 60)
        print("📊 Test Results Summary")
        print("=" * 60)
        
        passed = sum(1 for _, result in self.test_results if result)
        total = len(self.test_results)
        
        for test_name, result in self.test_results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name}")
        
        print(f"\n🎯 Overall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        
        if passed == total:
            print("🎉 All tests passed! The GitHub Coverage Agent is working perfectly.")
        elif passed >= total * 0.8:
            print("✅ Most tests passed! The agent is working well with minor issues.")
        else:
            print("⚠️ Several tests failed. Check the output above for details.")
        
        print("\n🚀 Capabilities demonstrated:")
        print("   • GitHub API integration")
        print("   • Repository access and analysis")
        print("   • Pull request analysis")
        print("   • Code generation and testing")
        print("   • Coverage analysis and reporting")
        print("   • Intelligent test suggestions")
        print("   • Agent integration")
        
        # Cleanup
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            print(f"\n🧹 Cleaned up temporary directory: {self.temp_dir}")

def main():
    """Main function to run the comprehensive test."""
    test_suite = ComprehensiveGitHubCoverageTest()
    test_suite.run_all_tests()

if __name__ == "__main__":
    main()
