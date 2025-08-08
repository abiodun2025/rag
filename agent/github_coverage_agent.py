#!/usr/bin/env python3
"""
GitHub-Integrated Test Coverage & Suggestions Agent

Connects to GitHub repositories, clones code, runs tests with coverage,
and provides intelligent suggestions for missing test cases.
"""

import os
import json
import logging
import requests
import subprocess
import tempfile
import shutil
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import xml.etree.ElementTree as ET

from .test_coverage_agent import TestCoverageAgent, CoverageData, TestSuggestion

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class GitHubConfig:
    """GitHub configuration."""
    token: str
    owner: str
    repo: str
    branch: str = "main"

@dataclass
class TestResult:
    """Test execution result."""
    success: bool
    output: str
    error: Optional[str] = None
    coverage_data: Optional[CoverageData] = None

class GitHubCoverageAgent(TestCoverageAgent):
    """GitHub-integrated Test Coverage Agent."""
    
    def __init__(self, github_config: GitHubConfig, llm_api_key: Optional[str] = None):
        super().__init__(llm_api_key)
        self.github_config = github_config
        self.temp_dir = None
        self.repo_path = None
        
    def analyze_pr_coverage(self, pr_number: int) -> Dict:
        """Analyze test coverage for a GitHub pull request."""
        try:
            logger.info(f"🔍 Analyzing PR #{pr_number} in {self.github_config.owner}/{self.github_config.repo}")
            
            # Get PR information
            pr_info = self._get_pr_info(pr_number)
            if not pr_info:
                return {"error": "Failed to get PR information"}
            
            # Clone the repository
            if not self._clone_repository(pr_info['head']['ref']):
                return {"error": "Failed to clone repository"}
            
            # Get changed files
            changed_files = self._get_pr_files(pr_number)
            if not changed_files:
                return {"error": "No files found in PR"}
            
            # Run tests and collect coverage
            coverage_results = []
            suggestions = []
            
            for file_info in changed_files:
                file_path = file_info['filename']
                language = self._detect_language(file_path)
                
                if language in self.supported_languages:
                    # Run tests for this file type
                    test_result = self._run_tests_with_coverage(language)
                    if test_result.success and test_result.coverage_data:
                        coverage_results.append(test_result.coverage_data)
                        
                        # Generate suggestions for uncovered lines
                        file_suggestions = self._generate_test_suggestions(
                            test_result.coverage_data, file_path, language
                        )
                        suggestions.extend(file_suggestions)
            
            # Generate overall report
            report = self._generate_coverage_report(coverage_results, suggestions)
            report['pr_info'] = pr_info
            
            logger.info(f"✅ Coverage analysis completed for PR #{pr_number}")
            return report
            
        except Exception as e:
            logger.error(f"❌ Error analyzing PR coverage: {e}")
            return {"error": str(e)}
        finally:
            self._cleanup()
    
    def analyze_repository_coverage(self, branch: str = "main") -> Dict:
        """Analyze test coverage for an entire repository."""
        try:
            logger.info(f"🔍 Analyzing repository coverage for {self.github_config.owner}/{self.github_config.repo}")
            
            # Clone the repository
            if not self._clone_repository(branch):
                return {"error": "Failed to clone repository"}
            
            # Detect project type and run tests
            project_type = self._detect_project_type()
            test_result = self._run_tests_with_coverage(project_type)
            
            if not test_result.success:
                return {"error": f"Test execution failed: {test_result.error}"}
            
            # Analyze coverage for all source files
            source_files = self._find_source_files(project_type)
            coverage_results = []
            suggestions = []
            
            for file_path in source_files:
                language = self._detect_language(file_path)
                if language in self.supported_languages:
                    coverage_data = self._analyze_file_coverage(file_path, language)
                    if coverage_data:
                        coverage_results.append(coverage_data)
                        
                        # Generate suggestions
                        file_suggestions = self._generate_test_suggestions(
                            coverage_data, file_path, language
                        )
                        suggestions.extend(file_suggestions)
            
            # Generate report
            report = self._generate_coverage_report(coverage_results, suggestions)
            report['repository'] = f"{self.github_config.owner}/{self.github_config.repo}"
            report['branch'] = branch
            
            logger.info(f"✅ Repository coverage analysis completed")
            return report
            
        except Exception as e:
            logger.error(f"❌ Error analyzing repository coverage: {e}")
            return {"error": str(e)}
        finally:
            self._cleanup()
    
    def _get_pr_info(self, pr_number: int) -> Optional[Dict]:
        """Get pull request information from GitHub."""
        try:
            url = f"https://api.github.com/repos/{self.github_config.owner}/{self.github_config.repo}/pulls/{pr_number}"
            headers = {
                "Authorization": f"token {self.github_config.token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get PR info: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting PR info: {e}")
            return None
    
    def _get_pr_files(self, pr_number: int) -> List[Dict]:
        """Get files changed in a pull request."""
        try:
            url = f"https://api.github.com/repos/{self.github_config.owner}/{self.github_config.repo}/pulls/{pr_number}/files"
            headers = {
                "Authorization": f"token {self.github_config.token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get PR files: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting PR files: {e}")
            return []
    
    def _clone_repository(self, branch: str) -> bool:
        """Clone the GitHub repository."""
        try:
            # Create temporary directory
            self.temp_dir = tempfile.mkdtemp()
            self.repo_path = os.path.join(self.temp_dir, self.github_config.repo)
            
            # Clone repository
            clone_url = f"https://{self.github_config.token}@github.com/{self.github_config.owner}/{self.github_config.repo}.git"
            
            result = subprocess.run([
                'git', 'clone', '--depth', '1', '--branch', branch, clone_url, self.repo_path
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"✅ Repository cloned to {self.repo_path}")
                return True
            else:
                logger.error(f"❌ Failed to clone repository: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error cloning repository: {e}")
            return False
    
    def _detect_project_type(self) -> str:
        """Detect the type of project (language/framework)."""
        if not self.repo_path:
            return "unknown"
        
        # Check for common project files
        if os.path.exists(os.path.join(self.repo_path, "pom.xml")):
            return "java"
        elif os.path.exists(os.path.join(self.repo_path, "build.gradle")):
            return "java"
        elif os.path.exists(os.path.join(self.repo_path, "package.json")):
            return "js"
        elif os.path.exists(os.path.join(self.repo_path, "requirements.txt")):
            return "py"
        elif os.path.exists(os.path.join(self.repo_path, "go.mod")):
            return "go"
        else:
            # Try to detect from file extensions
            for root, dirs, files in os.walk(self.repo_path):
                for file in files:
                    if file.endswith('.java'):
                        return "java"
                    elif file.endswith('.py'):
                        return "py"
                    elif file.endswith('.js') or file.endswith('.ts'):
                        return "js"
                    elif file.endswith('.go'):
                        return "go"
        
        return "unknown"
    
    def _run_tests_with_coverage(self, project_type: str) -> TestResult:
        """Run tests with coverage for the detected project type."""
        if not self.repo_path:
            return TestResult(False, "", "Repository not cloned")
        
        try:
            os.chdir(self.repo_path)
            
            if project_type == "java":
                return self._run_java_tests()
            elif project_type == "js":
                return self._run_js_tests()
            elif project_type == "py":
                return self._run_python_tests()
            elif project_type == "go":
                return self._run_go_tests()
            else:
                return TestResult(False, "", f"Unsupported project type: {project_type}")
                
        except Exception as e:
            return TestResult(False, "", str(e))
    
    def _run_java_tests(self) -> TestResult:
        """Run Java tests with JaCoCo coverage."""
        try:
            # Check if Maven is available
            maven_result = subprocess.run(['mvn', '--version'], capture_output=True, text=True)
            if maven_result.returncode != 0:
                return TestResult(False, "", "Maven not found")
            
            # Run tests with JaCoCo
            test_result = subprocess.run([
                'mvn', 'clean', 'test', 'jacoco:report'
            ], capture_output=True, text=True)
            
            if test_result.returncode == 0:
                # Look for JaCoCo report
                jacoco_report = os.path.join(self.repo_path, "target", "site", "jacoco", "jacoco.xml")
                if os.path.exists(jacoco_report):
                    # Parse coverage data
                    coverage_data = self._parse_jacoco_report(jacoco_report)
                    return TestResult(True, test_result.stdout, coverage_data=coverage_data)
                else:
                    return TestResult(True, test_result.stdout, "No JaCoCo report found")
            else:
                return TestResult(False, test_result.stdout, test_result.stderr)
                
        except Exception as e:
            return TestResult(False, "", str(e))
    
    def _run_js_tests(self) -> TestResult:
        """Run JavaScript tests with Istanbul coverage."""
        try:
            # Check if npm is available
            npm_result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
            if npm_result.returncode != 0:
                return TestResult(False, "", "npm not found")
            
            # Install dependencies
            install_result = subprocess.run(['npm', 'install'], capture_output=True, text=True)
            if install_result.returncode != 0:
                return TestResult(False, "", f"Failed to install dependencies: {install_result.stderr}")
            
            # Run tests with coverage
            test_result = subprocess.run([
                'npm', 'run', 'test:coverage'
            ], capture_output=True, text=True)
            
            if test_result.returncode == 0:
                # Look for coverage report
                coverage_report = os.path.join(self.repo_path, "coverage", "coverage-final.json")
                if os.path.exists(coverage_report):
                    # Parse coverage data
                    coverage_data = self._parse_istanbul_report(coverage_report)
                    return TestResult(True, test_result.stdout, coverage_data=coverage_data)
                else:
                    return TestResult(True, test_result.stdout, "No coverage report found")
            else:
                return TestResult(False, test_result.stdout, test_result.stderr)
                
        except Exception as e:
            return TestResult(False, "", str(e))
    
    def _run_python_tests(self) -> TestResult:
        """Run Python tests with coverage."""
        try:
            # Check if pip3 is available
            pip_result = subprocess.run(['pip3', '--version'], capture_output=True, text=True)
            if pip_result.returncode != 0:
                # Try python3 -m pip as fallback
                pip_result = subprocess.run(['python3', '-m', 'pip', '--version'], capture_output=True, text=True)
                if pip_result.returncode != 0:
                    return TestResult(False, "", "pip not found")
                pip_cmd = ['python3', '-m', 'pip']
            else:
                pip_cmd = ['pip3']
            
            # Install dependencies
            if os.path.exists("requirements.txt"):
                # Try to install with flexible version requirements
                install_result = subprocess.run(pip_cmd + ['install', '--upgrade', 'pip'], capture_output=True, text=True)
                
                # Try installing core dependencies first
                core_deps = ['pytest', 'coverage', 'requests']
                for dep in core_deps:
                    subprocess.run(pip_cmd + ['install', dep], capture_output=True, text=True)
                
                # Try to install requirements with more flexible version handling
                install_result = subprocess.run(pip_cmd + ['install', '-r', 'requirements.txt', '--no-deps'], capture_output=True, text=True)
                if install_result.returncode != 0:
                    # If that fails, try without version constraints
                    logger.warning(f"Failed to install exact versions: {install_result.stderr}")
                    logger.info("Trying to install core dependencies only...")
            
            # Install coverage if not available
            subprocess.run(pip_cmd + ['install', 'coverage'], capture_output=True)
            
            # Run tests with coverage
            logger.info("Running Python tests with coverage...")
            test_result = subprocess.run([
                'python3', '-m', 'coverage', 'run', '-m', 'pytest'
            ], capture_output=True, text=True)
            
            logger.info(f"Test result return code: {test_result.returncode}")
            logger.info(f"Test stdout: {test_result.stdout[:200]}...")
            logger.info(f"Test stderr: {test_result.stderr[:200]}...")
            
            if test_result.returncode == 0:
                # Generate coverage report
                logger.info("Generating coverage report...")
                report_result = subprocess.run(['python3', '-m', 'coverage', 'report'], capture_output=True, text=True)
                logger.info(f"Report result return code: {report_result.returncode}")
                logger.info(f"Report stdout: {report_result.stdout[:200]}...")
                
                if report_result.returncode == 0:
                    # Parse coverage data
                    coverage_data = self._parse_python_coverage(report_result.stdout)
                    return TestResult(True, test_result.stdout, coverage_data=coverage_data)
                else:
                    return TestResult(True, test_result.stdout, f"Failed to generate coverage report: {report_result.stderr}")
            else:
                return TestResult(False, test_result.stdout, test_result.stderr)
                
        except Exception as e:
            return TestResult(False, "", str(e))
    
    def _run_go_tests(self) -> TestResult:
        """Run Go tests with coverage."""
        try:
            # Check if go is available
            go_result = subprocess.run(['go', 'version'], capture_output=True, text=True)
            if go_result.returncode != 0:
                return TestResult(False, "", "Go not found")
            
            # Run tests with coverage
            test_result = subprocess.run([
                'go', 'test', '-coverprofile=coverage.out', './...'
            ], capture_output=True, text=True)
            
            if test_result.returncode == 0:
                # Parse coverage data
                coverage_data = self._parse_go_coverage("coverage.out")
                return TestResult(True, test_result.stdout, coverage_data=coverage_data)
            else:
                return TestResult(False, test_result.stdout, test_result.stderr)
                
        except Exception as e:
            return TestResult(False, "", str(e))
    
    def _parse_jacoco_report(self, report_path: str) -> Optional[CoverageData]:
        """Parse JaCoCo XML report."""
        try:
            tree = ET.parse(report_path)
            root = tree.getroot()
            
            total_lines = 0
            covered_lines = 0
            uncovered_lines = []
            
            for counter in root.findall('.//counter[@type="LINE"]'):
                covered = int(counter.get('covered', 0))
                missed = int(counter.get('missed', 0))
                total_lines += covered + missed
                covered_lines += covered
            
            return CoverageData(
                total_lines=total_lines,
                covered_lines=covered_lines,
                coverage_percentage=(covered_lines / total_lines * 100) if total_lines > 0 else 0,
                uncovered_lines=uncovered_lines,
                file_path="repository",
                language="java"
            )
            
        except Exception as e:
            logger.error(f"Error parsing JaCoCo report: {e}")
            return None
    
    def _parse_istanbul_report(self, report_path: str) -> Optional[CoverageData]:
        """Parse Istanbul JSON report."""
        try:
            with open(report_path, 'r') as f:
                coverage_data = json.load(f)
            
            total_lines = 0
            covered_lines = 0
            
            for file_data in coverage_data.values():
                statements = file_data.get('s', {})
                total_lines += len(statements)
                covered_lines += sum(1 for count in statements.values() if count > 0)
            
            return CoverageData(
                total_lines=total_lines,
                covered_lines=covered_lines,
                coverage_percentage=(covered_lines / total_lines * 100) if total_lines > 0 else 0,
                uncovered_lines=[],
                file_path="repository",
                language="js"
            )
            
        except Exception as e:
            logger.error(f"Error parsing Istanbul report: {e}")
            return None
    
    def _parse_python_coverage(self, report_output: str) -> Optional[CoverageData]:
        """Parse Python coverage report output."""
        try:
            lines = report_output.split('\n')
            total_lines = 0
            covered_lines = 0
            
            for line in lines:
                if line.startswith('TOTAL'):
                    parts = line.split()
                    if len(parts) >= 4:
                        total_lines = int(parts[1])
                        covered_lines = int(parts[2])
                        break
            
            return CoverageData(
                total_lines=total_lines,
                covered_lines=covered_lines,
                coverage_percentage=(covered_lines / total_lines * 100) if total_lines > 0 else 0,
                uncovered_lines=[],
                file_path="repository",
                language="py"
            )
            
        except Exception as e:
            logger.error(f"Error parsing Python coverage: {e}")
            return None
    
    def _parse_go_coverage(self, report_path: str) -> Optional[CoverageData]:
        """Parse Go coverage report."""
        try:
            if not os.path.exists(report_path):
                return None
            
            with open(report_path, 'r') as f:
                lines = f.readlines()
            
            total_lines = 0
            covered_lines = 0
            
            for line in lines:
                if line.startswith('mode:'):
                    continue
                parts = line.split()
                if len(parts) >= 3:
                    coverage_info = parts[1]
                    total, covered = map(int, coverage_info.split('/'))
                    total_lines += total
                    covered_lines += covered
            
            return CoverageData(
                total_lines=total_lines,
                covered_lines=covered_lines,
                coverage_percentage=(covered_lines / total_lines * 100) if total_lines > 0 else 0,
                uncovered_lines=[],
                file_path="repository",
                language="go"
            )
            
        except Exception as e:
            logger.error(f"Error parsing Go coverage: {e}")
            return None
    
    def _find_source_files(self, project_type: str) -> List[str]:
        """Find source files in the repository."""
        source_files = []
        
        if not self.repo_path:
            return source_files
        
        extensions = {
            "java": [".java", ".kt"],
            "js": [".js", ".ts", ".jsx", ".tsx"],
            "py": [".py"],
            "go": [".go"]
        }
        
        file_extensions = extensions.get(project_type, [])
        
        for root, dirs, files in os.walk(self.repo_path):
            # Skip common directories to ignore
            dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', 'target', 'build', '__pycache__']]
            
            for file in files:
                if any(file.endswith(ext) for ext in file_extensions):
                    file_path = os.path.join(root, file)
                    source_files.append(file_path)
        
        return source_files
    
    def _cleanup(self):
        """Clean up temporary files."""
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
                logger.info("🧹 Cleaned up temporary files")
            except Exception as e:
                logger.error(f"Error cleaning up: {e}")

# Example usage
if __name__ == "__main__":
    # Example configuration
    config = GitHubConfig(
        token="your_github_token",
        owner="owner",
        repo="repo"
    )
    
    agent = GitHubCoverageAgent(config)
    
    # Analyze PR coverage
    # report = agent.analyze_pr_coverage(123)
    # print(json.dumps(report, indent=2))
    
    # Analyze repository coverage
    # report = agent.analyze_repository_coverage("main")
    # print(json.dumps(report, indent=2))
    
    print("🔗 GitHub-Integrated Test Coverage Agent initialized!")
    print("📊 Can clone repositories, run tests, and analyze coverage")
    print("🤖 Provides intelligent suggestions for missing test cases")
