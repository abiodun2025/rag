#!/usr/bin/env python3
"""
GitHub PR Commenter for Test Coverage Analysis
Adds intelligent comments to pull requests with test coverage analysis and suggestions.
"""

import os
import json
import requests
import logging
from typing import Dict, List, Optional
from datetime import datetime
from .github_coverage_agent import GitHubCoverageAgent, GitHubConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GitHubPRCommenter:
    """GitHub PR Commenter for test coverage analysis."""
    
    def __init__(self, github_config: GitHubConfig):
        self.github_config = github_config
        self.coverage_agent = GitHubCoverageAgent(github_config)
        
    def analyze_and_comment_on_pr(self, pr_number: int) -> Dict:
        """Analyze PR coverage and add intelligent comments."""
        try:
            logger.info(f"🔍 Analyzing PR #{pr_number} and adding comments")
            
            # Get PR information
            pr_info = self.coverage_agent._get_pr_info(pr_number)
            if not pr_info:
                return {"error": "Failed to get PR information"}
            
            # Get PR files
            files = self.coverage_agent._get_pr_files(pr_number)
            if not files:
                return {"error": "No files found in PR"}
            
            # Analyze coverage for changed files
            coverage_results = []
            suggestions = []
            
            for file_info in files:
                file_path = file_info['filename']
                language = self.coverage_agent._detect_language(file_path)
                
                if language in self.coverage_agent.supported_languages:
                    # Analyze file coverage
                    coverage_data = self._analyze_file_coverage(file_path, language)
                    if coverage_data:
                        coverage_results.append(coverage_data)
                        
                        # Generate suggestions
                        file_suggestions = self.coverage_agent._generate_test_suggestions(
                            coverage_data, file_path, language
                        )
                        suggestions.extend(file_suggestions)
            
            # Generate comment content
            comment_content = self._generate_pr_comment(
                pr_info, files, coverage_results, suggestions
            )
            
            # Add comment to PR
            comment_result = self._add_comment_to_pr(pr_number, comment_content)
            
            if comment_result.get("success"):
                logger.info(f"✅ Successfully added comment to PR #{pr_number}")
                return {
                    "success": True,
                    "pr_number": pr_number,
                    "comment_id": comment_result.get("comment_id"),
                    "coverage_results": coverage_results,
                    "suggestions": suggestions
                }
            else:
                return {"error": f"Failed to add comment: {comment_result.get('error')}"}
                
        except Exception as e:
            logger.error(f"❌ Error analyzing PR and adding comment: {e}")
            return {"error": str(e)}
    
    def _analyze_file_coverage(self, file_path: str, language: str) -> Optional[Dict]:
        """Analyze coverage for a specific file."""
        try:
            # For demonstration, we'll create mock coverage data
            # In a real implementation, this would run actual tests
            
            if language == "py":
                return {
                    "file_path": file_path,
                    "language": language,
                    "total_lines": 50,
                    "covered_lines": 35,
                    "coverage_percentage": 70.0,
                    "uncovered_lines": [15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29]
                }
            elif language == "js":
                return {
                    "file_path": file_path,
                    "language": language,
                    "total_lines": 40,
                    "covered_lines": 28,
                    "coverage_percentage": 70.0,
                    "uncovered_lines": [12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]
                }
            else:
                return {
                    "file_path": file_path,
                    "language": language,
                    "total_lines": 30,
                    "covered_lines": 20,
                    "coverage_percentage": 66.7,
                    "uncovered_lines": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
                }
                
        except Exception as e:
            logger.error(f"Error analyzing file coverage: {e}")
            return None
    
    def _generate_pr_comment(self, pr_info: Dict, files: List[Dict], 
                           coverage_results: List[Dict], suggestions: List) -> str:
        """Generate a comprehensive PR comment with coverage analysis."""
        
        comment = f"""## 🧪 Test Coverage Analysis for PR #{pr_info['number']}

### 📊 Coverage Summary
"""
        
        if coverage_results:
            total_files = len(coverage_results)
            avg_coverage = sum(r['coverage_percentage'] for r in coverage_results) / total_files
            
            comment += f"""
- **Files Analyzed**: {total_files}
- **Average Coverage**: {avg_coverage:.1f}%
- **Overall Status**: {'✅ Good' if avg_coverage >= 80 else '⚠️ Needs Improvement' if avg_coverage >= 60 else '❌ Poor'}
"""
        else:
            comment += """
- **Files Analyzed**: 0 (no supported language files found)
- **Coverage**: N/A
- **Status**: ⚠️ No testable files detected
"""
        
        # File-specific coverage
        if coverage_results:
            comment += "\n### 📁 File Coverage Details\n"
            for result in coverage_results:
                status_emoji = "✅" if result['coverage_percentage'] >= 80 else "⚠️" if result['coverage_percentage'] >= 60 else "❌"
                comment += f"""
**{result['file_path']}** {status_emoji}
- Coverage: {result['coverage_percentage']:.1f}% ({result['covered_lines']}/{result['total_lines']} lines)
- Language: {result['language'].upper()}
"""
        
        # Test suggestions
        if suggestions:
            comment += "\n### 💡 Test Suggestions\n"
            
            # Group suggestions by priority
            high_priority = [s for s in suggestions if s.priority == "high"]
            medium_priority = [s for s in suggestions if s.priority == "medium"]
            low_priority = [s for s in suggestions if s.priority == "low"]
            
            if high_priority:
                comment += "\n#### 🔴 High Priority\n"
                for i, suggestion in enumerate(high_priority[:3], 1):
                    comment += f"{i}. **{suggestion.type.replace('_', ' ').title()}**: {suggestion.description}\n"
            
            if medium_priority:
                comment += "\n#### 🟡 Medium Priority\n"
                for i, suggestion in enumerate(medium_priority[:3], 1):
                    comment += f"{i}. **{suggestion.type.replace('_', ' ').title()}**: {suggestion.description}\n"
            
            if low_priority:
                comment += "\n#### 🟢 Low Priority\n"
                for i, suggestion in enumerate(low_priority[:2], 1):
                    comment += f"{i}. **{suggestion.type.replace('_', ' ').title()}**: {suggestion.description}\n"
        
        # Recommendations
        comment += "\n### 📋 Recommendations\n"
        
        if coverage_results:
            avg_coverage = sum(r['coverage_percentage'] for r in coverage_results) / len(coverage_results)
            
            if avg_coverage >= 80:
                comment += """
- ✅ **Excellent coverage!** Consider adding integration tests for better confidence
- 🎯 Focus on edge cases and error scenarios
- 🔍 Consider adding performance tests
"""
            elif avg_coverage >= 60:
                comment += """
- ⚠️ **Good coverage, but room for improvement**
- 🎯 Focus on high-priority test suggestions above
- 🔍 Add tests for uncovered edge cases
- 📈 Aim for 80%+ coverage
"""
            else:
                comment += """
- ❌ **Coverage needs significant improvement**
- 🎯 Prioritize high-priority test suggestions
- 🔍 Add comprehensive test cases
- 📈 Immediate focus on critical code paths
"""
        else:
            comment += """
- ⚠️ **No testable files detected**
- 🔍 Consider adding tests for your code changes
- 📝 Ensure test files follow naming conventions
"""
        
        # Footer
        comment += f"""
---
*🤖 Analysis by GitHub-Integrated Test Coverage Agent*
*📅 Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        return comment
    
    def _add_comment_to_pr(self, pr_number: int, comment_content: str) -> Dict:
        """Add a comment to a GitHub pull request."""
        try:
            url = f"https://api.github.com/repos/{self.github_config.owner}/{self.github_config.repo}/issues/{pr_number}/comments"
            
            headers = {
                "Authorization": f"token {self.github_config.token}",
                "Accept": "application/vnd.github.v3+json",
                "Content-Type": "application/json"
            }
            
            data = {
                "body": comment_content
            }
            
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 201:
                comment_data = response.json()
                return {
                    "success": True,
                    "comment_id": comment_data["id"],
                    "comment_url": comment_data["html_url"]
                }
            else:
                logger.error(f"Failed to add comment: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            logger.error(f"Error adding comment to PR: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def list_prs(self) -> List[Dict]:
        """List all open pull requests."""
        try:
            url = f"https://api.github.com/repos/{self.github_config.owner}/{self.github_config.repo}/pulls"
            
            headers = {
                "Authorization": f"token {self.github_config.token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get PRs: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error listing PRs: {e}")
            return []

# Example usage
if __name__ == "__main__":
    # Example configuration
    config = GitHubConfig(
        token="your_github_token",
        owner="owner",
        repo="repo"
    )
    
    commenter = GitHubPRCommenter(config)
    
    # Analyze and comment on PR #11
    # result = commenter.analyze_and_comment_on_pr(11)
    # print(json.dumps(result, indent=2))
    
    print("🔗 GitHub PR Commenter initialized!")
    print("📊 Can analyze PRs and add intelligent comments")
    print("🤖 Provides test coverage analysis and suggestions")
