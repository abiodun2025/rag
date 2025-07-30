#!/usr/bin/env python3
"""
GitHub Repository Code Review Agent
==================================

A simple agent that reviews any GitHub repository and returns a comprehensive report.
Enhanced with full repository and branch access.
Version: 1.1.0
"""

import sys
import os
import json
import argparse
from datetime import datetime
from typing import Dict, Any, List

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.github_code_reviewer import GitHubCodeReviewer
from agent.code_reviewer import code_reviewer

class GitHubReviewAgent:
    """Agent for reviewing GitHub repositories with full access."""
    
    def __init__(self, github_token: str = None):
        self.github_token = github_token or os.getenv('GITHUB_TOKEN')
        self.reviewer = GitHubCodeReviewer(self.github_token)
        self.version = "1.1.0"
    
    def test_github_connection(self) -> Dict[str, Any]:
        """Test GitHub connection and get user information."""
        return self.reviewer.test_connection()
    
    def list_user_repositories(self, include_private: bool = True) -> Dict[str, Any]:
        """List all repositories for the authenticated user."""
        return self.reviewer.get_user_repositories(include_private)
    
    def list_repository_branches(self, owner: str, repo: str) -> Dict[str, Any]:
        """List all branches for a specific repository."""
        return self.reviewer.get_repository_branches(owner, repo)
    
    def extract_repo_info(self, repo_url: str) -> Dict[str, str]:
        """Extract owner and repo name from various URL formats."""
        # Clean the URL
        repo_url = repo_url.strip()
        
        # Handle different URL formats
        if repo_url.startswith('https://github.com/'):
            repo_url = repo_url.replace('https://github.com/', '')
        elif repo_url.startswith('http://github.com/'):
            repo_url = repo_url.replace('http://github.com/', '')
        elif repo_url.startswith('github.com/'):
            repo_url = repo_url.replace('github.com/', '')
        
        # Remove trailing slash and .git
        repo_url = repo_url.rstrip('/').replace('.git', '')
        
        # Split into owner and repo
        if '/' in repo_url:
            parts = repo_url.split('/')
            if len(parts) >= 2:
                owner = parts[0]
                repo = parts[1]
                return {"owner": owner, "repo": repo}
        
        raise ValueError(f"Invalid GitHub repository URL: {repo_url}")
    
    def review_repository(self, repo_url: str, output_file: str = None, clone_locally: bool = True, branch: str = None) -> Dict[str, Any]:
        """Review a GitHub repository and generate a comprehensive report."""
        try:
            # Extract repository information
            repo_info = self.extract_repo_info(repo_url)
            owner = repo_info["owner"]
            repo = repo_info["repo"]
            
            print(f"🔍 Starting code review for: {repo_url}")
            print(f"📦 Repository: {owner}/{repo}")
            if branch:
                print(f"🌿 Branch: {branch}")
            print("📊 Analyzing repository...")
            
            # Analyze the repository
            analysis_result = self.reviewer.analyze_repository(owner, repo, clone_locally, branch)
            
            if not analysis_result["success"]:
                return {
                    "success": False,
                    "error": analysis_result["error"],
                    "repository": f"{owner}/{repo}",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Generate comprehensive report
            report = self._generate_comprehensive_report(analysis_result, repo_url, branch)
            
            # Save report if output file specified
            if output_file:
                self._save_report(report, output_file)
            
            return report
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Review failed: {str(e)}",
                "repository": repo_url,
                "timestamp": datetime.now().isoformat()
            }
    
    def review_pull_request(self, owner: str, repo: str, pr_number: int, output_file: str = None) -> Dict[str, Any]:
        """Review a specific pull request."""
        try:
            print(f"🔍 Starting pull request review for: {owner}/{repo}#{pr_number}")
            print("📊 Analyzing pull request changes...")
            
            # Review the pull request
            pr_result = self.reviewer.review_pull_request(owner, repo, pr_number)
            
            if not pr_result["success"]:
                return {
                    "success": False,
                    "error": pr_result["error"],
                    "repository": f"{owner}/{repo}",
                    "pr_number": pr_number,
                    "timestamp": datetime.now().isoformat()
                }
            
            # Generate comprehensive report
            report = self._generate_pr_report(pr_result, owner, repo, pr_number)
            
            # Save report if output file specified
            if output_file:
                self._save_report(report, output_file)
            
            return report
            
        except Exception as e:
            return {
                "success": False,
                "error": f"PR review failed: {str(e)}",
                "repository": f"{owner}/{repo}",
                "pr_number": pr_number,
                "timestamp": datetime.now().isoformat()
            }
    
    def review_user_repositories(self, review_type: str = "full", include_private: bool = True, output_file: str = None) -> Dict[str, Any]:
        """Review all repositories for the authenticated user."""
        try:
            print("🔍 Starting review of all user repositories...")
            
            # Get user repositories
            repos_result = self.list_user_repositories(include_private)
            
            if not repos_result["success"]:
                return {
                    "success": False,
                    "error": repos_result["error"],
                    "timestamp": datetime.now().isoformat()
                }
            
            repositories = repos_result["repositories"]
            print(f"📦 Found {len(repositories)} repositories to review")
            
            # Review each repository
            results = []
            for i, repo_info in enumerate(repositories, 1):
                repo_name = repo_info["full_name"]
                print(f"📊 Reviewing {i}/{len(repositories)}: {repo_name}")
                
                try:
                    # Review the repository
                    repo_result = self.review_repository(
                        repo_name, 
                        output_file=None, 
                        clone_locally=False,  # Use API for faster bulk review
                        branch=repo_info.get("default_branch", "main")
                    )
                    
                    if repo_result["success"]:
                        results.append({
                            "repository": repo_name,
                            "info": repo_info,
                            "review": repo_result
                        })
                    else:
                        results.append({
                            "repository": repo_name,
                            "info": repo_info,
                            "error": repo_result.get("error", "Unknown error")
                        })
                        
                except Exception as e:
                    results.append({
                        "repository": repo_name,
                        "info": repo_info,
                        "error": str(e)
                    })
            
            # Generate comprehensive report
            report = self._generate_user_repos_report(results, review_type)
            
            # Save report if output file specified
            if output_file:
                self._save_report(report, output_file)
            
            return report
            
        except Exception as e:
            return {
                "success": False,
                "error": f"User repositories review failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    def _generate_comprehensive_report(self, analysis_result: Dict[str, Any], repo_url: str, branch: str = None) -> Dict[str, Any]:
        """Generate a comprehensive report from analysis results."""
        summary = analysis_result.get("summary", {})
        
        # Find critical and high priority issues
        critical_issues = []
        high_priority_issues = []
        recommendations = []
        
        for result in analysis_result.get("results", []):
            if "report" in result:
                report = result["report"]
                file_path = result["file"]
                
                # Collect critical issues
                for issue in report.get("issues", {}).get("critical", []):
                    critical_issues.append({
                        "file": file_path,
                        "issue": issue
                    })
                
                # Collect high priority issues
                for issue in report.get("issues", {}).get("high", []):
                    high_priority_issues.append({
                        "file": file_path,
                        "issue": issue
                    })
        
        # Generate recommendations
        if summary.get("critical_issues", 0) > 0:
            recommendations.append(f"🔴 CRITICAL: Address {summary['critical_issues']} critical issues immediately")
        
        if summary.get("high_issues", 0) > 0:
            recommendations.append(f"🟠 HIGH: Address {summary['high_issues']} high priority issues")
        
        if summary.get("average_score", 0) < 70:
            recommendations.append("🟡 QUALITY: Consider improving overall code quality")
        
        if summary.get("total_files", 0) > 0 and summary.get("successful_reviews", 0) < summary.get("total_files", 0):
            recommendations.append("🟡 COVERAGE: Some files could not be analyzed")
        
        return {
            "success": True,
            "repository": analysis_result.get("repository", repo_url),
            "repository_url": repo_url,
            "branch": branch or "default",
            "timestamp": datetime.now().isoformat(),
            "summary": summary,
            "critical_issues": critical_issues[:10],  # Top 10 critical issues
            "high_priority_issues": high_priority_issues[:10],  # Top 10 high priority issues
            "recommendations": recommendations,
            "total_files_analyzed": len(analysis_result.get("results", [])),
            "local_path": analysis_result.get("local_path")
        }
    
    def _generate_pr_report(self, pr_result: Dict[str, Any], owner: str, repo: str, pr_number: int) -> Dict[str, Any]:
        """Generate a report for pull request review."""
        summary = pr_result.get("summary", {})
        
        return {
            "success": True,
            "repository": f"{owner}/{repo}",
            "pr_number": pr_number,
            "pr_title": pr_result.get("title"),
            "pr_author": pr_result.get("author"),
            "pr_state": pr_result.get("state"),
            "timestamp": datetime.now().isoformat(),
            "summary": summary,
            "changed_files": len(pr_result.get("results", [])),
            "results": pr_result.get("results", [])
        }
    
    def _generate_user_repos_report(self, results: List[Dict[str, Any]], review_type: str) -> Dict[str, Any]:
        """Generate a report for user repositories review."""
        successful_reviews = [r for r in results if "review" in r]
        failed_reviews = [r for r in results if "error" in r]
        
        # Calculate overall statistics
        total_repos = len(results)
        successful_count = len(successful_reviews)
        failed_count = len(failed_reviews)
        
        # Calculate average scores
        scores = []
        total_issues = 0
        critical_issues = 0
        high_issues = 0
        
        for result in successful_reviews:
            if "review" in result and "summary" in result["review"]:
                summary = result["review"]["summary"]
                scores.append(summary.get("average_score", 0))
                total_issues += summary.get("total_issues", 0)
                critical_issues += summary.get("critical_issues", 0)
                high_issues += summary.get("high_issues", 0)
        
        avg_score = sum(scores) / len(scores) if scores else 0
        
        # Determine overall grade
        if avg_score >= 90:
            overall_grade = "A"
        elif avg_score >= 80:
            overall_grade = "B"
        elif avg_score >= 70:
            overall_grade = "C"
        elif avg_score >= 60:
            overall_grade = "D"
        else:
            overall_grade = "F"
        
        return {
            "success": True,
            "review_type": review_type,
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_repositories": total_repos,
                "successful_reviews": successful_count,
                "failed_reviews": failed_count,
                "average_score": round(avg_score, 2),
                "overall_grade": overall_grade,
                "total_issues": total_issues,
                "critical_issues": critical_issues,
                "high_issues": high_issues
            },
            "repositories": results,
            "top_repositories": sorted(
                successful_reviews, 
                key=lambda x: x.get("review", {}).get("summary", {}).get("average_score", 0),
                reverse=True
            )[:5]
        }
    
    def _save_report(self, report: Dict[str, Any], output_file: str):
        """Save report to file."""
        try:
            # If output_file doesn't have a path, save to Downloads folder
            if not os.path.dirname(output_file):
                # Get Downloads folder path
                downloads_path = os.path.expanduser("~/Downloads")
                output_file = os.path.join(downloads_path, output_file)
            
            # Ensure the directory exists
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, default=str)
            print(f"📄 Report saved to: {output_file}")
        except Exception as e:
            print(f"⚠️  Failed to save report: {e}")
    
    def cleanup_local_repository(self, local_path: str):
        """Clean up locally cloned repository."""
        if local_path:
            self.reviewer.cleanup_local_repository(local_path)

# Example usage
if __name__ == "__main__":
    # Initialize the agent
    agent = GitHubReviewAgent()
    
    # Test GitHub connection
    connection = agent.test_github_connection()
    if connection["success"]:
        print(f"✅ Connected to GitHub as: {connection['user']}")
        print(f"📊 Public repos: {connection['public_repos']}")
        print(f"🔒 Private repos: {connection['private_repos']}")
    else:
        print(f"❌ GitHub connection failed: {connection['error']}")
    
    # Example: Review a repository
    # result = agent.review_repository("https://github.com/owner/repo")
    # print(json.dumps(result, indent=2)) 