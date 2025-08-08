#!/usr/bin/env python3
"""
Test Coverage & Suggestions Agent

Monitors test coverage of pull requests and suggests missing test cases.
Supports multiple coverage tools: JaCoCo (Java/Kotlin), Istanbul (JS), Codecov.
Uses LLM to provide intelligent suggestions for missing test cases.
"""

import os
import json
import logging
import requests
import subprocess
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import xml.etree.ElementTree as ET
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CoverageData:
    """Data structure for coverage information."""
    total_lines: int
    covered_lines: int
    coverage_percentage: float
    uncovered_lines: List[int]
    file_path: str
    language: str

@dataclass
class TestSuggestion:
    """Data structure for test suggestions."""
    file_path: str
    line_number: int
    suggestion_type: str  # 'edge_case', 'boundary', 'null_check', 'error_handling'
    description: str
    code_snippet: str
    priority: str  # 'high', 'medium', 'low'

class TestCoverageAgent:
    """Test Coverage & Suggestions Agent."""
    
    def __init__(self, llm_api_key: Optional[str] = None):
        self.llm_api_key = llm_api_key or os.getenv('LLM_API_KEY')
        self.supported_languages = {
            'java': 'jacoco',
            'kt': 'jacoco',  # Kotlin
            'js': 'istanbul',
            'ts': 'istanbul',  # TypeScript
            'py': 'coverage',  # Python coverage
            'go': 'go-test'    # Go test coverage
        }
        
    def analyze_pr_coverage(self, pr_number: int, repo_owner: str, repo_name: str) -> Dict:
        """Analyze test coverage for a specific pull request."""
        try:
            logger.info(f"🔍 Analyzing test coverage for PR #{pr_number}")
            
            # Get PR files
            pr_files = self._get_pr_files(pr_number, repo_owner, repo_name)
            if not pr_files:
                return {"error": "No files found in PR"}
            
            # Analyze coverage for each file
            coverage_results = []
            suggestions = []
            
            for file_info in pr_files:
                file_path = file_info['filename']
                language = self._detect_language(file_path)
                
                if language in self.supported_languages:
                    coverage_data = self._analyze_file_coverage(file_path, language)
                    if coverage_data:
                        coverage_results.append(coverage_data)
                        
                        # Generate suggestions for uncovered lines
                        file_suggestions = self._generate_test_suggestions(
                            coverage_data, file_path, language
                        )
                        suggestions.extend(file_suggestions)
            
            # Generate overall report
            report = self._generate_coverage_report(coverage_results, suggestions)
            
            logger.info(f"✅ Coverage analysis completed for PR #{pr_number}")
            return report
            
        except Exception as e:
            logger.error(f"❌ Error analyzing PR coverage: {e}")
            return {"error": str(e)}
    
    def _get_pr_files(self, pr_number: int, repo_owner: str, repo_name: str) -> List[Dict]:
        """Get files changed in a pull request."""
        try:
            github_token = os.getenv('GITHUB_TOKEN')
            if not github_token:
                return []
            
            url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/pulls/{pr_number}/files"
            headers = {
                "Authorization": f"token {github_token}",
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
    
    def _detect_language(self, file_path: str) -> str:
        """Detect programming language from file extension."""
        ext = Path(file_path).suffix.lower()
        language_map = {
            '.java': 'java',
            '.kt': 'kt',
            '.js': 'js',
            '.ts': 'ts',
            '.py': 'py',
            '.go': 'go'
        }
        return language_map.get(ext, 'unknown')
    
    def _analyze_file_coverage(self, file_path: str, language: str) -> Optional[CoverageData]:
        """Analyze coverage for a specific file."""
        try:
            if language == 'java' or language == 'kt':
                return self._analyze_jacoco_coverage(file_path)
            elif language in ['js', 'ts']:
                return self._analyze_istanbul_coverage(file_path)
            elif language == 'py':
                return self._analyze_python_coverage(file_path)
            elif language == 'go':
                return self._analyze_go_coverage(file_path)
            else:
                logger.warning(f"Unsupported language: {language}")
                return None
                
        except Exception as e:
            logger.error(f"Error analyzing coverage for {file_path}: {e}")
            return None
    
    def _analyze_jacoco_coverage(self, file_path: str) -> Optional[CoverageData]:
        """Analyze JaCoCo coverage for Java/Kotlin files."""
        try:
            # Look for JaCoCo XML report
            jacoco_report_path = self._find_jacoco_report(file_path)
            if not jacoco_report_path or not os.path.exists(jacoco_report_path):
                return None
            
            tree = ET.parse(jacoco_report_path)
            root = tree.getroot()
            
            # Find the specific file in the report
            for package in root.findall('.//package'):
                for sourcefile in package.findall('.//sourcefile'):
                    if sourcefile.get('name') == Path(file_path).name:
                        counter = sourcefile.find('.//counter[@type="LINE"]')
                        if counter is not None:
                            covered = int(counter.get('covered', 0))
                            missed = int(counter.get('missed', 0))
                            total = covered + missed
                            
                            # Get uncovered lines
                            uncovered_lines = []
                            for line in sourcefile.findall('.//line'):
                                if line.get('ci') == '0':  # Not covered
                                    uncovered_lines.append(int(line.get('nr')))
                            
                            return CoverageData(
                                total_lines=total,
                                covered_lines=covered,
                                coverage_percentage=(covered / total * 100) if total > 0 else 0,
                                uncovered_lines=uncovered_lines,
                                file_path=file_path,
                                language='java'
                            )
            
            return None
            
        except Exception as e:
            logger.error(f"Error analyzing JaCoCo coverage: {e}")
            return None
    
    def _analyze_istanbul_coverage(self, file_path: str) -> Optional[CoverageData]:
        """Analyze Istanbul coverage for JavaScript/TypeScript files."""
        try:
            # Look for Istanbul JSON report
            istanbul_report_path = self._find_istanbul_report(file_path)
            if not istanbul_report_path or not os.path.exists(istanbul_report_path):
                return None
            
            with open(istanbul_report_path, 'r') as f:
                coverage_data = json.load(f)
            
            # Find the specific file in the report
            file_key = os.path.abspath(file_path)
            if file_key in coverage_data:
                file_coverage = coverage_data[file_key]
                statements = file_coverage.get('s', {})
                
                total_lines = len(statements)
                covered_lines = sum(1 for count in statements.values() if count > 0)
                uncovered_lines = [line for line, count in statements.items() if count == 0]
                
                return CoverageData(
                    total_lines=total_lines,
                    covered_lines=covered_lines,
                    coverage_percentage=(covered_lines / total_lines * 100) if total_lines > 0 else 0,
                    uncovered_lines=uncovered_lines,
                    file_path=file_path,
                    language='js'
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error analyzing Istanbul coverage: {e}")
            return None
    
    def _analyze_python_coverage(self, file_path: str) -> Optional[CoverageData]:
        """Analyze Python coverage."""
        try:
            # Look for coverage report
            coverage_report_path = self._find_python_coverage_report(file_path)
            if not coverage_report_path or not os.path.exists(coverage_report_path):
                return None
            
            # Parse coverage report
            with open(coverage_report_path, 'r') as f:
                lines = f.readlines()
            
            # Extract coverage data
            total_lines = 0
            covered_lines = 0
            uncovered_lines = []
            
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
                uncovered_lines=uncovered_lines,  # Would need more parsing for specific lines
                file_path=file_path,
                language='py'
            )
            
        except Exception as e:
            logger.error(f"Error analyzing Python coverage: {e}")
            return None
    
    def _analyze_go_coverage(self, file_path: str) -> Optional[CoverageData]:
        """Analyze Go test coverage."""
        try:
            # Run go test with coverage
            result = subprocess.run(
                ['go', 'test', '-coverprofile=coverage.out', file_path],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0 and os.path.exists('coverage.out'):
                # Parse coverage.out file
                with open('coverage.out', 'r') as f:
                    lines = f.readlines()
                
                # Extract coverage data
                total_lines = 0
                covered_lines = 0
                
                for line in lines:
                    if line.startswith('mode:'):
                        continue
                    parts = line.split()
                    if len(parts) >= 3:
                        file_info = parts[0]
                        if file_path in file_info:
                            coverage_info = parts[1]
                            total, covered = map(int, coverage_info.split('/'))
                            total_lines += total
                            covered_lines += covered
                
                return CoverageData(
                    total_lines=total_lines,
                    covered_lines=covered_lines,
                    coverage_percentage=(covered_lines / total_lines * 100) if total_lines > 0 else 0,
                    uncovered_lines=[],  # Would need more parsing for specific lines
                    file_path=file_path,
                    language='go'
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error analyzing Go coverage: {e}")
            return None
    
    def _find_jacoco_report(self, file_path: str) -> Optional[str]:
        """Find JaCoCo XML report."""
        possible_paths = [
            'target/site/jacoco/jacoco.xml',
            'build/reports/jacoco/test/jacocoTestReport.xml',
            'jacoco.xml'
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        return None
    
    def _find_istanbul_report(self, file_path: str) -> Optional[str]:
        """Find Istanbul JSON report."""
        possible_paths = [
            'coverage/coverage-final.json',
            'coverage.json',
            '.nyc_output/out.json'
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        return None
    
    def _find_python_coverage_report(self, file_path: str) -> Optional[str]:
        """Find Python coverage report."""
        possible_paths = [
            '.coverage',
            'coverage.txt',
            'htmlcov/index.html'
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        return None
    
    def _generate_test_suggestions(self, coverage_data: CoverageData, file_path: str, language: str) -> List[TestSuggestion]:
        """Generate intelligent test suggestions using LLM."""
        suggestions = []
        
        if not coverage_data.uncovered_lines:
            return suggestions
        
        try:
            # Read the source file to get context
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    source_code = f.read()
                
                # Generate suggestions for each uncovered line
                for line_num in coverage_data.uncovered_lines[:10]:  # Limit to first 10 lines
                    suggestion = self._generate_line_suggestion(
                        source_code, line_num, file_path, language
                    )
                    if suggestion:
                        suggestions.append(suggestion)
            
            # Generate general suggestions based on coverage percentage
            if coverage_data.coverage_percentage < 80:
                general_suggestion = self._generate_general_suggestion(
                    coverage_data, file_path, language
                )
                if general_suggestion:
                    suggestions.append(general_suggestion)
                    
        except Exception as e:
            logger.error(f"Error generating suggestions: {e}")
        
        return suggestions
    
    def _generate_line_suggestion(self, source_code: str, line_num: int, file_path: str, language: str) -> Optional[TestSuggestion]:
        """Generate suggestion for a specific uncovered line."""
        try:
            lines = source_code.split('\n')
            if line_num <= len(lines):
                code_line = lines[line_num - 1].strip()
                
                # Simple rule-based suggestions
                suggestion_type = self._classify_line_type(code_line, language)
                description = self._generate_suggestion_description(code_line, suggestion_type, language)
                
                return TestSuggestion(
                    file_path=file_path,
                    line_number=line_num,
                    suggestion_type=suggestion_type,
                    description=description,
                    code_snippet=code_line,
                    priority='medium'
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error generating line suggestion: {e}")
            return None
    
    def _classify_line_type(self, code_line: str, language: str) -> str:
        """Classify the type of code line for better suggestions."""
        code_line_lower = code_line.lower()
        
        if any(keyword in code_line_lower for keyword in ['null', 'none', 'undefined']):
            return 'null_check'
        elif any(keyword in code_line_lower for keyword in ['if', 'else', 'switch', 'case']):
            return 'edge_case'
        elif any(keyword in code_line_lower for keyword in ['try', 'catch', 'except', 'throw']):
            return 'error_handling'
        elif any(keyword in code_line_lower for keyword in ['<', '>', '<=', '>=']):
            return 'boundary'
        elif any(keyword in code_line_lower for keyword in ['return', 'break', 'continue']):
            return 'control_flow'
        else:
            return 'general'
    
    def _generate_suggestion_description(self, code_line: str, suggestion_type: str, language: str) -> str:
        """Generate description for test suggestion."""
        suggestions = {
            'null_check': f"Add test case for null/empty input: '{code_line.strip()}'",
            'edge_case': f"Add test case for edge condition: '{code_line.strip()}'",
            'error_handling': f"Add test case for error scenario: '{code_line.strip()}'",
            'boundary': f"Add test case for boundary condition: '{code_line.strip()}'",
            'control_flow': f"Add test case for control flow: '{code_line.strip()}'",
            'general': f"Add test case for uncovered line: '{code_line.strip()}'"
        }
        
        return suggestions.get(suggestion_type, f"Add test case for: '{code_line.strip()}'")
    
    def _generate_general_suggestion(self, coverage_data: CoverageData, file_path: str, language: str) -> Optional[TestSuggestion]:
        """Generate general suggestion based on overall coverage."""
        if coverage_data.coverage_percentage < 50:
            priority = 'high'
            description = f"Critical: Coverage is only {coverage_data.coverage_percentage:.1f}%. Add comprehensive test suite."
        elif coverage_data.coverage_percentage < 80:
            priority = 'medium'
            description = f"Improvement needed: Coverage is {coverage_data.coverage_percentage:.1f}%. Add more test cases."
        else:
            return None
        
        return TestSuggestion(
            file_path=file_path,
            line_number=0,
            suggestion_type='general',
            description=description,
            code_snippet="",
            priority=priority
        )
    
    def _generate_coverage_report(self, coverage_results: List[CoverageData], suggestions: List[TestSuggestion]) -> Dict:
        """Generate comprehensive coverage report."""
        if not coverage_results:
            return {"error": "No coverage data available"}
        
        total_lines = sum(c.total_lines for c in coverage_results)
        total_covered = sum(c.covered_lines for c in coverage_results)
        overall_coverage = (total_covered / total_lines * 100) if total_lines > 0 else 0
        
        # Group suggestions by priority
        high_priority = [s for s in suggestions if s.priority == 'high']
        medium_priority = [s for s in suggestions if s.priority == 'medium']
        low_priority = [s for s in suggestions if s.priority == 'low']
        
        report = {
            "overall_coverage": {
                "percentage": round(overall_coverage, 2),
                "total_lines": total_lines,
                "covered_lines": total_covered,
                "uncovered_lines": total_lines - total_covered
            },
            "file_coverage": [
                {
                    "file_path": c.file_path,
                    "coverage_percentage": round(c.coverage_percentage, 2),
                    "total_lines": c.total_lines,
                    "covered_lines": c.covered_lines,
                    "uncovered_lines": c.uncovered_lines
                }
                for c in coverage_results
            ],
            "suggestions": {
                "high_priority": len(high_priority),
                "medium_priority": len(medium_priority),
                "low_priority": len(low_priority),
                "total": len(suggestions),
                "details": [
                    {
                        "file_path": s.file_path,
                        "line_number": s.line_number,
                        "type": s.suggestion_type,
                        "description": s.description,
                        "priority": s.priority,
                        "code_snippet": s.code_snippet
                    }
                    for s in suggestions
                ]
            },
            "recommendations": self._generate_recommendations(overall_coverage, suggestions),
            "timestamp": datetime.now().isoformat()
        }
        
        return report
    
    def _generate_recommendations(self, overall_coverage: float, suggestions: List[TestSuggestion]) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        if overall_coverage < 50:
            recommendations.append("🚨 Critical: Coverage is below 50%. Focus on high-priority test cases first.")
        elif overall_coverage < 80:
            recommendations.append("⚠️ Coverage is below 80%. Add more comprehensive test cases.")
        
        if suggestions:
            high_priority_count = len([s for s in suggestions if s.priority == 'high'])
            if high_priority_count > 0:
                recommendations.append(f"🎯 Focus on {high_priority_count} high-priority test suggestions.")
            
            null_checks = len([s for s in suggestions if s.suggestion_type == 'null_check'])
            if null_checks > 0:
                recommendations.append(f"🔍 Add {null_checks} null/empty input test cases.")
            
            edge_cases = len([s for s in suggestions if s.suggestion_type == 'edge_case'])
            if edge_cases > 0:
                recommendations.append(f"⚡ Add {edge_cases} edge case test scenarios.")
        
        if not recommendations:
            recommendations.append("✅ Good coverage! Consider adding integration tests for better confidence.")
        
        return recommendations

# Example usage and testing
if __name__ == "__main__":
    # Initialize the agent
    agent = TestCoverageAgent()
    
    # Example: Analyze PR coverage
    # report = agent.analyze_pr_coverage(123, "owner", "repo")
    # print(json.dumps(report, indent=2))
    
    print("🧪 Test Coverage & Suggestions Agent initialized!")
    print("📊 Supports: JaCoCo (Java/Kotlin), Istanbul (JS/TS), Python coverage, Go test")
    print("🤖 LLM-enhanced suggestions for missing test cases")
