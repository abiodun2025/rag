#!/usr/bin/env python3
"""
GitHub Repository Code Review Agent
==================================

A simple agent that reviews any GitHub repository and returns a comprehensive report.
<<<<<<< Updated upstream
=======
Enhanced with full repository and branch access, plus PR commenting capabilities.
Version: 1.4.0
>>>>>>> Stashed changes
"""

import sys
import os
import json
import argparse
from datetime import datetime
from typing import Dict, Any

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.github_code_reviewer import GitHubCodeReviewer
from agent.code_reviewer import code_reviewer

class GitHubReviewAgent:
    """Agent for reviewing GitHub repositories."""
    
    def __init__(self, github_token: str = None):
        self.github_token = github_token or os.getenv('GITHUB_TOKEN')
        self.reviewer = GitHubCodeReviewer(self.github_token)
<<<<<<< Updated upstream
=======
        self.version = "1.4.0"
    
    def test_github_connection(self) -> Dict[str, Any]:
        """Test GitHub connection and get user information."""
        return self.reviewer.test_connection()
    
    def list_user_repositories(self, include_private: bool = True) -> Dict[str, Any]:
        """List all repositories for the authenticated user."""
        return self.reviewer.get_user_repositories(include_private)
    
    def list_repository_branches(self, owner: str, repo: str) -> Dict[str, Any]:
        """List all branches for a specific repository."""
        return self.reviewer.get_repository_branches(owner, repo)
    
    def list_repository_pull_requests(self, owner: str, repo: str, state: str = "open") -> Dict[str, Any]:
        """List all pull requests for a specific repository."""
        return self.reviewer.get_repository_pull_requests(owner, repo, state)
    
    def list_all_pull_requests(self, state: str = "open", include_private: bool = True) -> Dict[str, Any]:
        """List all pull requests from all accessible repositories."""
        return self.reviewer.get_all_accessible_pull_requests(state, include_private)
    
    def get_pull_request_details(self, owner: str, repo: str, pr_number: int) -> Dict[str, Any]:
        """Get detailed information about a specific pull request."""
        return self.reviewer.get_pull_request_details(owner, repo, pr_number)
>>>>>>> Stashed changes
    
    def extract_repo_info(self, repo_url: str) -> Dict[str, str]:
        """Extract owner and repo name from various URL formats."""
        
        # Remove trailing slashes and common paths
        repo_url = repo_url.rstrip('/')
        repo_url = repo_url.replace('/settings/access', '')
        repo_url = repo_url.replace('/settings', '')
        repo_url = repo_url.replace('/issues', '')
        repo_url = repo_url.replace('/pulls', '')
        repo_url = repo_url.replace('/blob/main', '')
        repo_url = repo_url.replace('/blob/master', '')
        
        # Handle different URL formats
        if repo_url.startswith('https://github.com/'):
            parts = repo_url.replace('https://github.com/', '').split('/')
            if len(parts) >= 2:
                return {"owner": parts[0], "repo": parts[1]}
        elif repo_url.startswith('http://github.com/'):
            parts = repo_url.replace('http://github.com/', '').split('/')
            if len(parts) >= 2:
                return {"owner": parts[0], "repo": parts[1]}
        elif '/' in repo_url and not repo_url.startswith('http'):
            # Assume it's already in owner/repo format
            parts = repo_url.split('/')
            if len(parts) >= 2:
                return {"owner": parts[0], "repo": parts[1]}
        
        raise ValueError(f"Invalid repository URL format: {repo_url}")
    
    def review_repository(self, repo_url: str, output_file: str = None, clone_locally: bool = True) -> Dict[str, Any]:
        """Review a GitHub repository and generate a comprehensive report."""
        
        try:
            print(f"🔍 Starting code review for: {repo_url}")
            
            # Extract repository information
            repo_info = self.extract_repo_info(repo_url)
            owner = repo_info["owner"]
            repo = repo_info["repo"]
            
            print(f"📦 Repository: {owner}/{repo}")
            
            # Test GitHub connection
            if self.github_token:
                print("🔐 Testing GitHub connection...")
                connection_test = self.reviewer.test_connection()
                if not connection_test["success"]:
                    print(f"⚠️  GitHub connection failed: {connection_test.get('error', 'Unknown error')}")
                    print("💡 Continuing with public repository access...")
            
            # Analyze the repository
            print("📊 Analyzing repository...")
            analysis_result = self.reviewer.analyze_repository(owner, repo, clone_locally)
            
            if not analysis_result["success"]:
                return {
                    "success": False,
                    "error": analysis_result["error"],
                    "repository": f"{owner}/{repo}",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Generate comprehensive report
            report = self._generate_comprehensive_report(analysis_result, repo_url)
            
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
    
<<<<<<< Updated upstream
    def _generate_comprehensive_report(self, analysis_result: Dict[str, Any], repo_url: str) -> Dict[str, Any]:
=======
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
    
    def review_and_comment_pr(self, owner: str, repo: str, pr_number: int, auto_comment: bool = True, output_file: str = None) -> Dict[str, Any]:
        """Review a pull request and add comments directly to the PR."""
        try:
            print(f"🔍 Starting PR review with comments for: {owner}/{repo}#{pr_number}")
            print("📊 Analyzing and commenting on pull request...")
            
            # Review and comment on the pull request
            result = self.reviewer.review_and_comment_pr(owner, repo, pr_number, auto_comment)
            
            if not result["success"]:
                return {
                    "success": False,
                    "error": result["error"],
                    "repository": f"{owner}/{repo}",
                    "pr_number": pr_number,
                    "timestamp": datetime.now().isoformat()
                }
            
            # Generate comprehensive report
            report = self._generate_pr_comment_report(result, owner, repo, pr_number)
            
            # Save report if output file specified
            if output_file:
                self._save_report(report, output_file)
            
            return report
            
        except Exception as e:
            return {
                "success": False,
                "error": f"PR review and comment failed: {str(e)}",
                "repository": f"{owner}/{repo}",
                "pr_number": pr_number,
                "timestamp": datetime.now().isoformat()
            }
    
    def create_pr_comment(self, owner: str, repo: str, pr_number: int, comment: str, commit_id: str = None, path: str = None, line: int = None) -> Dict[str, Any]:
        """Create a single comment on a pull request."""
        try:
            print(f"💬 Creating comment on PR #{pr_number} in {owner}/{repo}...")
            
            result = self.reviewer.create_pr_comment(owner, repo, pr_number, comment, commit_id, path, line)
            
            if result["success"]:
                print(f"✅ Comment created successfully: {result.get('url', 'N/A')}")
            else:
                print(f"❌ Failed to create comment: {result.get('error', 'Unknown error')}")
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create comment: {str(e)}"
            }
    
    def create_pr_review(self, owner: str, repo: str, pr_number: int, review_body: str, comments: List[Dict] = None, event: str = "COMMENT") -> Dict[str, Any]:
        """Create a review on a pull request with optional comments."""
        try:
            print(f"📝 Creating review on PR #{pr_number} in {owner}/{repo}...")
            
            review_data = {
                "body": review_body,
                "event": event  # COMMENT, APPROVE, REQUEST_CHANGES
            }
            
            if comments:
                review_data["comments"] = comments
            
            result = self.reviewer.create_pr_review(owner, repo, pr_number, review_data)
            
            if result["success"]:
                print(f"✅ Review created successfully: {result.get('url', 'N/A')}")
            else:
                print(f"❌ Failed to create review: {result.get('error', 'Unknown error')}")
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create review: {str(e)}"
            }
    
    def get_pr_commits(self, owner: str, repo: str, pr_number: int) -> Dict[str, Any]:
        """Get commits for a pull request."""
        return self.reviewer.get_pr_commits(owner, repo, pr_number)
    
    def get_pr_files(self, owner: str, repo: str, pr_number: int) -> Dict[str, Any]:
        """Get files changed in a pull request."""
        return self.reviewer.get_pr_files(owner, repo, pr_number)
    
    def review_commit(self, owner: str, repo: str, commit_sha: str, output_file: str = None) -> Dict[str, Any]:
        """Review a specific commit by analyzing its diff."""
        try:
            print(f"🔍 Reviewing commit: {commit_sha[:8]} in {owner}/{repo}...")
            
            # Review the commit
            result = self.reviewer.review_commit(owner, repo, commit_sha)
            
            if result["success"]:
                # Generate report
                report = self._generate_commit_report(result, owner, repo, commit_sha)
                
                # Save report if output file specified
                if output_file:
                    self._save_report(report, output_file)
                    print(f"📄 Report saved to: {output_file}")
                
                return report
            else:
                return result
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Commit review failed: {str(e)}"
            }
    
    def review_pull_request_commits(self, owner: str, repo: str, pr_number: int, output_file: str = None) -> Dict[str, Any]:
        """Review each commit in a pull request individually."""
        try:
            print(f"🔍 Starting commit-by-commit review for PR #{pr_number} in {owner}/{repo}...")
            
            # Review all commits in the PR
            result = self.reviewer.review_pull_request_commits(owner, repo, pr_number)
            
            if result["success"]:
                # Generate report
                report = self._generate_commit_reviews_report(result, owner, repo, pr_number)
                
                # Save report if output file specified
                if output_file:
                    self._save_report(report, output_file)
                    print(f"📄 Report saved to: {output_file}")
                
                return report
            else:
                return result
                
        except Exception as e:
            return {
                "success": False,
                "error": f"PR commits review failed: {str(e)}"
            }
    
    def get_commit_diff(self, owner: str, repo: str, commit_sha: str) -> Dict[str, Any]:
        """Get the diff for a specific commit."""
        return self.reviewer.get_commit_diff(owner, repo, commit_sha)
    
    def comment_all_pull_requests(self, state: str = "open", include_private: bool = True, auto_comment: bool = True, output_file: str = None) -> Dict[str, Any]:
        """Comment on all accessible pull requests."""
        try:
            print(f"🔍 Starting automated commenting on all {state} pull requests...")
            
            # Comment on all pull requests
            result = self.reviewer.comment_all_pull_requests(state, include_private, auto_comment)
            
            if not result["success"]:
                return {
                    "success": False,
                    "error": result["error"],
                    "timestamp": datetime.now().isoformat()
                }
            
            # Generate comprehensive report
            report = self._generate_all_prs_comment_report(result, state)
            
            # Save report if output file specified
            if output_file:
                self._save_report(report, output_file)
            
            return report
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to comment on all pull requests: {str(e)}",
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
>>>>>>> Stashed changes
        """Generate a comprehensive report from analysis results."""
        
        summary = analysis_result["summary"]
        results = analysis_result["results"]
        
        # Collect all issues and categorize them
        all_issues = []
        critical_issues = []
        high_issues = []
        medium_issues = []
        low_issues = []
        
        file_reports = []
        
        for file_result in results:
            if 'report' in file_result:
                report = file_result['report']
                file_info = {
                    "file": file_result['file'],
                    "score": report['score'],
                    "grade": report['grade'],
                    "language": report['language'],
                    "issues_count": report['issues']['total'],
                    "critical_issues": report['issues']['critical'],
                    "high_issues": report['issues']['high'],
                    "medium_issues": report['issues']['medium'],
                    "low_issues": report['issues']['low']
                }
                file_reports.append(file_info)
                
                # Collect all issues
                for issue in report['issues']['details']:
                    issue_info = {
                        'file': file_result['file'],
                        'line': issue.get('line', 'N/A'),
                        'severity': issue.get('severity', 'unknown'),
                        'category': issue.get('category', 'unknown'),
                        'message': issue.get('message', ''),
                        'suggestion': issue.get('suggestion', '')
                    }
                    all_issues.append(issue_info)
                    
                    # Categorize by severity
                    if issue.get('severity') == 'critical':
                        critical_issues.append(issue_info)
                    elif issue.get('severity') == 'high':
                        high_issues.append(issue_info)
                    elif issue.get('severity') == 'medium':
                        medium_issues.append(issue_info)
                    elif issue.get('severity') == 'low':
                        low_issues.append(issue_info)
        
<<<<<<< Updated upstream
        # Calculate overall metrics
        total_files = len(file_reports)
        successful_reviews = len([f for f in file_reports if f['score'] > 0])
        avg_score = sum([f['score'] for f in file_reports]) / total_files if total_files > 0 else 0
=======
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
    
    def _generate_pr_comment_report(self, result: Dict[str, Any], owner: str, repo: str, pr_number: int) -> Dict[str, Any]:
        """Generate a report for PR review with comments."""
        pr_review = result.get("pr_review", {})
        review_created = result.get("review_created", {})
        
        return {
            "success": True,
            "repository": f"{owner}/{repo}",
            "pr_number": pr_number,
            "pr_title": pr_review.get("title"),
            "pr_author": pr_review.get("author"),
            "pr_state": pr_review.get("state"),
            "timestamp": datetime.now().isoformat(),
            "review_created": review_created.get("success", False) if isinstance(review_created, dict) else bool(review_created),
            "review_url": review_created.get("url") if isinstance(review_created, dict) else None,
            "comments_added": result.get("comments_added", 0),
            "summary": result.get("summary", ""),
            "pr_review": pr_review
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
>>>>>>> Stashed changes
        
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
        
        # Generate recommendations
        recommendations = self._generate_recommendations(critical_issues, high_issues, medium_issues, file_reports)
        
        # Create comprehensive report
        report = {
            "success": True,
            "repository": analysis_result["repository"],
            "repository_url": repo_url,
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_files": total_files,
                "successful_reviews": successful_reviews,
                "average_score": round(avg_score, 2),
                "overall_grade": overall_grade,
                "total_issues": len(all_issues),
                "critical_issues": len(critical_issues),
                "high_issues": len(high_issues),
                "medium_issues": len(medium_issues),
                "low_issues": len(low_issues)
            },
            "file_analysis": file_reports,
            "critical_issues": critical_issues[:20],  # Top 20 critical issues
            "high_priority_issues": high_issues[:30],  # Top 30 high priority issues
            "recommendations": recommendations,
            "local_path": analysis_result.get("local_path"),
            "note": "Use cleanup_local_repository() to remove cloned repository"
        }
        
        return report
    
    def _generate_recommendations(self, critical_issues: list, high_issues: list, medium_issues: list, file_reports: list) -> list:
        """Generate actionable recommendations based on analysis."""
        
        recommendations = []
        
        # Critical issues
        if critical_issues:
            recommendations.append({
                "priority": "critical",
                "message": f"🔴 CRITICAL: Address {len(critical_issues)} critical issues immediately",
                "details": "These issues pose serious security or safety risks and must be fixed before deployment."
            })
        
        # High priority issues
        if high_issues:
            recommendations.append({
                "priority": "high",
                "message": f"🟠 HIGH: Fix {len(high_issues)} high-priority issues",
                "details": "These issues should be addressed before the next release."
            })
        
        # Performance recommendations
        low_score_files = [f for f in file_reports if f['score'] < 70]
        if low_score_files:
            recommendations.append({
                "priority": "medium",
                "message": f"🟡 MEDIUM: Improve {len(low_score_files)} files with low scores",
                "details": "Focus on files with scores below 70 for significant improvements."
            })
        
        # Security recommendations
        security_issues = [i for i in critical_issues + high_issues if i['category'] == 'security']
        if security_issues:
            recommendations.append({
                "priority": "high",
                "message": f"🔒 SECURITY: Address {len(security_issues)} security vulnerabilities",
                "details": "Security issues should be prioritized for immediate attention."
            })
        
        # Code quality recommendations
        if len(file_reports) > 10:
            recommendations.append({
                "priority": "medium",
                "message": "📚 DOCUMENTATION: Consider improving code documentation",
                "details": "Large codebases benefit from comprehensive documentation."
            })
        
        # Testing recommendations
        if len(critical_issues) + len(high_issues) > 20:
            recommendations.append({
                "priority": "medium",
                "message": "🧪 TESTING: Consider adding more comprehensive tests",
                "details": "High issue count suggests need for better testing coverage."
            })
        
        return recommendations
    
    def _generate_commit_report(self, result: Dict[str, Any], owner: str, repo: str, commit_sha: str) -> Dict[str, Any]:
        """Generate a report for a single commit review."""
        return {
            "success": True,
            "operation": "review_commit",
            "repository": f"{owner}/{repo}",
            "commit_sha": commit_sha,
            "timestamp": datetime.now().isoformat(),
            "commit_info": {
                "message": result.get("message", ""),
                "author": result.get("author", ""),
                "date": result.get("date", ""),
                "files_changed": len(result.get("results", []))
            },
            "review_results": result.get("results", []),
            "summary": result.get("summary", ""),
            "raw_result": result
        }
    
    def _generate_commit_reviews_report(self, result: Dict[str, Any], owner: str, repo: str, pr_number: int) -> Dict[str, Any]:
        """Generate a report for commit-by-commit PR review."""
        return {
            "success": True,
            "operation": "review_pull_request_commits",
            "repository": f"{owner}/{repo}",
            "pr_number": pr_number,
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_commits": result.get("total_commits", 0),
                "reviewed_commits": result.get("reviewed_commits", 0),
                "total_score": result.get("total_score", 0),
                "total_issues": result.get("total_issues", 0),
                "average_score": result.get("average_score", 0)
            },
            "commit_reviews": result.get("commit_reviews", []),
            "overall_summary": result.get("summary", ""),
            "raw_result": result
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
        if local_path and os.path.exists(local_path):
            try:
                self.reviewer.cleanup_local_repository(local_path)
                print(f"🧹 Cleaned up: {local_path}")
                return True
            except Exception as e:
                print(f"⚠️  Failed to clean up {local_path}: {e}")
                return False
        return False
    
    def print_report_summary(self, report: Dict[str, Any]):
        """Print a summary of the report."""
        if not report["success"]:
            print(f"❌ Review failed: {report.get('error', 'Unknown error')}")
            return
        
        summary = report["summary"]
        
        print("\n" + "="*80)
        print("🔍 GITHUB REPOSITORY CODE REVIEW REPORT")
        print("="*80)
        print(f"📦 Repository: {report['repository']}")
        print(f"🔗 URL: {report['repository_url']}")
        print(f"📅 Timestamp: {report['timestamp']}")
        print(f"📊 Overall Grade: {summary['overall_grade']} ({summary['average_score']}/100)")
        print()
        
        print("📈 SUMMARY STATISTICS:")
        print(f"   📁 Total Files: {summary['total_files']}")
        print(f"   ✅ Successful Reviews: {summary['successful_reviews']}")
        print(f"   🚨 Total Issues: {summary['total_issues']}")
        print(f"   🔴 Critical: {summary['critical_issues']}")
        print(f"   🟠 High: {summary['high_issues']}")
        print(f"   🟡 Medium: {summary['medium_issues']}")
        print(f"   🟢 Low: {summary['low_issues']}")
        print()
        
        # Show top critical and high issues
        if report.get('critical_issues'):
            print("🔴 CRITICAL ISSUES (Top 5):")
            for i, issue in enumerate(report['critical_issues'][:5], 1):
                print(f"   {i}. {issue['file']}:{issue['line']} - {issue['message']}")
            print()
        
        if report.get('high_priority_issues'):
            print("🟠 HIGH PRIORITY ISSUES (Top 5):")
            for i, issue in enumerate(report['high_priority_issues'][:5], 1):
                print(f"   {i}. {issue['file']}:{issue['line']} - {issue['message']}")
            print()
        
        # Show recommendations
        if report.get('recommendations'):
            print("🎯 KEY RECOMMENDATIONS:")
            for rec in report['recommendations']:
                priority_emoji = {
                    'critical': '🔴',
                    'high': '🟠',
                    'medium': '🟡',
                    'low': '🟢'
                }.get(rec['priority'], 'ℹ️')
                print(f"   {priority_emoji} {rec['message']}")
            print()
        
        if report.get('local_path'):
            print(f"📂 Local repository: {report['local_path']}")
            print("💡 Use cleanup_local_repository() to remove cloned repository")
        
        print("="*80)

def main():
    """Main function for command-line usage."""
    
    parser = argparse.ArgumentParser(description='Review GitHub repositories with AI-powered analysis')
    parser.add_argument('repository', help='GitHub repository URL or owner/repo format')
    parser.add_argument('--token', '-t', help='GitHub token (or set GITHUB_TOKEN env var)')
    parser.add_argument('--output', '-o', help='Output file for detailed report (JSON)')
    parser.add_argument('--api-only', action='store_true', help='Use GitHub API only (no local cloning)')
    parser.add_argument('--cleanup', action='store_true', help='Clean up local repository after analysis')
    
    args = parser.parse_args()
    
    # Initialize agent
    agent = GitHubReviewAgent(args.token)
    
    # Review repository
    report = agent.review_repository(
        args.repository, 
        args.output, 
        clone_locally=not args.api_only
    )
    
    # Print summary
    agent.print_report_summary(report)
    
    # Cleanup if requested
    if args.cleanup and report.get('local_path'):
        agent.cleanup_local_repository(report['local_path'])

if __name__ == "__main__":
    main() 