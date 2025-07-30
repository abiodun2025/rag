#!/usr/bin/env python3
"""
GitHub Code Reviewer
===================

Integration with GitHub to perform code reviews on real repositories.
Enhanced with full repository and branch access, plus PR commenting capabilities.
"""

import os
import requests
import base64
import tempfile
import json
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime
import subprocess
import shutil

from .code_reviewer import code_reviewer

logger = logging.getLogger(__name__)

class GitHubCodeReviewer:
    """GitHub integration for code review with full repository access and PR commenting."""
    
    def __init__(self, github_token: str = None):
        self.github_token = github_token or os.getenv('GITHUB_TOKEN')
        self.api_base = "https://api.github.com"
        self.headers = {}
        
        if self.github_token:
            self.headers = {
                'Authorization': f'token {self.github_token}',
                'Accept': 'application/vnd.github.v3+json'
            }
        else:
            logger.warning("No GitHub token provided. Limited to public repositories only.")
    
    def test_connection(self) -> Dict[str, Any]:
        """Test GitHub API connection and get user info."""
        try:
            response = requests.get(f"{self.api_base}/user", headers=self.headers)
            if response.status_code == 200:
                user_data = response.json()
                return {
                    "success": True,
                    "user": user_data.get('login'),
                    "name": user_data.get('name'),
                    "email": user_data.get('email'),
                    "public_repos": user_data.get('public_repos', 0),
                    "private_repos": user_data.get('total_private_repos', 0),
                    "avatar_url": user_data.get('avatar_url'),
                    "authenticated": True
                }
            else:
                return {
                    "success": False,
                    "error": f"GitHub API error: {response.status_code}",
                    "message": response.text,
                    "authenticated": False
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Connection failed: {str(e)}",
                "authenticated": False
            }
    
    def get_user_repositories(self, include_private: bool = True) -> Dict[str, Any]:
        """Get all repositories for the authenticated user."""
        try:
            if not self.github_token:
                return {
                    "success": False,
                    "error": "GitHub token required to access user repositories",
                    "repositories": []
                }
            
            repos = []
            page = 1
            per_page = 100
            
            while True:
                url = f"{self.api_base}/user/repos?page={page}&per_page={per_page}&sort=updated"
                if not include_private:
                    url += "&type=public"
                
                response = requests.get(url, headers=self.headers)
                
                if response.status_code != 200:
                    return {
                        "success": False,
                        "error": f"Failed to fetch repositories: {response.status_code}",
                        "repositories": repos
                    }
                
                page_repos = response.json()
                if not page_repos:
                    break
                
                for repo in page_repos:
                    repo_info = {
                        "name": repo.get('name'),
                        "full_name": repo.get('full_name'),
                        "description": repo.get('description'),
                        "private": repo.get('private', False),
                        "fork": repo.get('fork', False),
                        "language": repo.get('language'),
                        "stars": repo.get('stargazers_count', 0),
                        "forks": repo.get('forks_count', 0),
                        "updated_at": repo.get('updated_at'),
                        "clone_url": repo.get('clone_url'),
                        "ssh_url": repo.get('ssh_url'),
                        "default_branch": repo.get('default_branch', 'main'),
                        "size": repo.get('size', 0),
                        "topics": repo.get('topics', [])
                    }
                    repos.append(repo_info)
                
                page += 1
                if len(page_repos) < per_page:
                    break
            
            return {
                "success": True,
                "repositories": repos,
                "total_count": len(repos)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to fetch repositories: {str(e)}",
                "repositories": []
            }
    
    def get_repository_branches(self, owner: str, repo: str) -> Dict[str, Any]:
        """Get all branches for a specific repository."""
        try:
            url = f"{self.api_base}/repos/{owner}/{repo}/branches"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                branches = response.json()
                branch_list = []
                
                for branch in branches:
                    branch_info = {
                        "name": branch.get('name'),
                        "commit": {
                            "sha": branch.get('commit', {}).get('sha'),
                            "message": branch.get('commit', {}).get('commit', {}).get('message'),
                            "date": branch.get('commit', {}).get('commit', {}).get('author', {}).get('date')
                        },
                        "protected": branch.get('protected', False)
                    }
                    branch_list.append(branch_info)
                
                return {
                    "success": True,
                    "branches": branch_list,
                    "total_count": len(branch_list)
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to fetch branches: {response.status_code}",
                    "branches": []
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to fetch branches: {str(e)}",
                "branches": []
            }
    
    def get_repository_content(self, owner: str, repo: str, path: str = "", branch: str = None) -> Dict[str, Any]:
        """Get repository content at a specific path and branch."""
        try:
            url = f"{self.api_base}/repos/{owner}/{repo}/contents/{path}"
            params = {}
            if branch:
                params['ref'] = branch
            
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                content = response.json()
                
                if isinstance(content, list):
                    # Directory listing
                    return {
                        "success": True,
                        "type": "directory",
                        "path": path,
                        "items": [
                            {
                                "name": item.get('name'),
                                "path": item.get('path'),
                                "type": item.get('type'),
                                "size": item.get('size'),
                                "sha": item.get('sha')
                            }
                            for item in content
                        ]
                    }
                else:
                    # Single file
                    return {
                        "success": True,
                        "type": "file",
                        "name": content.get('name'),
                        "path": content.get('path'),
                        "size": content.get('size'),
                        "sha": content.get('sha'),
                        "content": base64.b64decode(content.get('content', '')).decode('utf-8'),
                        "encoding": content.get('encoding')
                    }
            else:
                return {
                    "success": False,
                    "error": f"Failed to fetch content: {response.status_code}",
                    "message": response.text
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to fetch content: {str(e)}"
            }
    
    def get_file_content(self, owner: str, repo: str, file_path: str, branch: str = None) -> Dict[str, Any]:
        """Get content of a specific file."""
        return self.get_repository_content(owner, repo, file_path, branch)
    
    def clone_repository(self, owner: str, repo: str, branch: str = None) -> Dict[str, Any]:
        """Clone a repository locally for analysis."""
        try:
            # Create temporary directory
            local_path = tempfile.mkdtemp(prefix="github_review_")
            
            # Determine clone URL
            if self.github_token:
                # Use authenticated URL for private repos
                clone_url = f"https://{self.github_token}@github.com/{owner}/{repo}.git"
            else:
                # Use public URL
                clone_url = f"https://github.com/{owner}/{repo}.git"
            
            # Clone command
            clone_cmd = ["git", "clone", clone_url, local_path]
            if branch and branch != "main" and branch != "master":
                clone_cmd.extend(["-b", branch])
            
            # Execute clone
            result = subprocess.run(clone_cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "local_path": local_path,
                    "repository": f"{owner}/{repo}",
                    "branch": branch or "default"
                }
            else:
                # Clean up on failure
                shutil.rmtree(local_path, ignore_errors=True)
                return {
                    "success": False,
                    "error": f"Clone failed: {result.stderr}",
                    "local_path": None
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Clone failed: {str(e)}",
                "local_path": None
            }
    
    def analyze_repository(self, owner: str, repo: str, clone_locally: bool = True, branch: str = None) -> Dict[str, Any]:
        """Analyze a repository using the code reviewer."""
        try:
            if clone_locally:
                # Clone repository locally
                clone_result = self.clone_repository(owner, repo, branch)
                if not clone_result["success"]:
                    return clone_result
                
                local_path = clone_result["local_path"]
                
                # Analyze the local repository
                analysis_result = self._analyze_local_repository(local_path)
                analysis_result["local_path"] = local_path
                
                return analysis_result
            else:
                # Analyze using GitHub API only
                return self._analyze_remote_repository(owner, repo, branch)
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Analysis failed: {str(e)}"
            }
    
    def _analyze_local_repository(self, local_path: str) -> Dict[str, Any]:
        """Analyze a locally cloned repository."""
        try:
            # Get all Python files in the repository
            python_files = []
            for root, dirs, files in os.walk(local_path):
                # Skip common directories that shouldn't be analyzed
                dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv', 'venv']]
                
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        relative_path = os.path.relpath(file_path, local_path)
                        python_files.append({
                            'file': relative_path,
                            'full_path': file_path
                        })
            
            # Analyze each file
            results = []
            for file_info in python_files:
                try:
                    with open(file_info['full_path'], 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Analyze the file
                    report = code_reviewer.analyze_code(content, file_info['file'])
                    results.append({
                        'file': file_info['file'],
                        'report': report
                    })
                except Exception as e:
                    logger.warning(f"Failed to analyze {file_info['file']}: {e}")
                    results.append({
                        'file': file_info['file'],
                        'error': str(e)
                    })
            
            # Generate summary
            summary = self._generate_summary(results)
            
            return {
                "success": True,
                "results": results,
                "summary": summary,
                "total_files": len(python_files)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Local analysis failed: {str(e)}"
            }
    
    def _analyze_remote_repository(self, owner: str, repo: str, branch: str = None) -> Dict[str, Any]:
        """Analyze a repository using GitHub API only."""
        try:
            # Get repository content
            content_result = self.get_repository_content(owner, repo, "", branch)
            
            if not content_result["success"]:
                return content_result
            
            if content_result["type"] != "directory":
                return {
                    "success": False,
                    "error": "Repository root is not a directory"
                }
            
            # Find Python files
            python_files = []
            self._find_python_files_recursive(owner, repo, "", python_files, branch)
            
            # Analyze each file
            results = []
            for file_info in python_files:
                try:
                    file_content = self.get_file_content(owner, repo, file_info['path'], branch)
                    if file_content["success"] and file_content["type"] == "file":
                        content = file_content["content"]
                        report = code_reviewer.analyze_code(content, file_info['path'])
                        results.append({
                            'file': file_info['path'],
                            'report': report
                        })
                except Exception as e:
                    logger.warning(f"Failed to analyze {file_info['path']}: {e}")
                    results.append({
                        'file': file_info['path'],
                        'error': str(e)
                    })
            
            # Generate summary
            summary = self._generate_summary(results)
            
            return {
                "success": True,
                "results": results,
                "summary": summary,
                "total_files": len(python_files)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Remote analysis failed: {str(e)}"
            }
    
    def _find_python_files_recursive(self, owner: str, repo: str, path: str, python_files: List[Dict], branch: str = None):
        """Recursively find Python files in repository."""
        try:
            content_result = self.get_repository_content(owner, repo, path, branch)
            
            if not content_result["success"] or content_result["type"] != "directory":
                return
            
            for item in content_result["items"]:
                if item["type"] == "file" and item["name"].endswith('.py'):
                    python_files.append({
                        'path': item['path'],
                        'name': item['name']
                    })
                elif item["type"] == "directory":
                    # Skip common directories
                    if item["name"] not in ['.git', '__pycache__', 'node_modules', '.venv', 'venv']:
                        self._find_python_files_recursive(owner, repo, item["path"], python_files, branch)
                        
        except Exception as e:
            logger.warning(f"Failed to explore directory {path}: {e}")
    
    def _generate_summary(self, results: List[Dict]) -> Dict[str, Any]:
        """Generate summary statistics from analysis results."""
        total_files = len(results)
        successful_reviews = len([r for r in results if 'report' in r])
        
        if successful_reviews == 0:
            return {
                "total_files": total_files,
                "successful_reviews": 0,
                "average_score": 0,
                "overall_grade": "F",
                "total_issues": 0,
                "critical_issues": 0,
                "high_issues": 0,
                "medium_issues": 0,
                "low_issues": 0
            }
        
        # Calculate scores and issues
        scores = []
        total_issues = 0
        critical_issues = 0
        high_issues = 0
        medium_issues = 0
        low_issues = 0
        
        for result in results:
            if 'report' in result:
                report = result['report']
                scores.append(report.get('score', 0))
                
                issues = report.get('issues', {})
                total_issues += issues.get('total', 0)
                critical_issues += issues.get('critical', 0)
                high_issues += issues.get('high', 0)
                medium_issues += issues.get('medium', 0)
                low_issues += issues.get('low', 0)
        
        average_score = sum(scores) / len(scores) if scores else 0
        
        # Determine overall grade
        if average_score >= 90:
            overall_grade = "A"
        elif average_score >= 80:
            overall_grade = "B"
        elif average_score >= 70:
            overall_grade = "C"
        elif average_score >= 60:
            overall_grade = "D"
        else:
            overall_grade = "F"
        
        return {
            "total_files": total_files,
            "successful_reviews": successful_reviews,
            "average_score": round(average_score, 2),
            "overall_grade": overall_grade,
            "total_issues": total_issues,
            "critical_issues": critical_issues,
            "high_issues": high_issues,
            "medium_issues": medium_issues,
            "low_issues": low_issues
        }
    
    def review_pull_request(self, owner: str, repo: str, pr_number: int) -> Dict[str, Any]:
        """Review a specific pull request."""
        try:
            # Get PR details
            pr_url = f"{self.api_base}/repos/{owner}/{repo}/pulls/{pr_number}"
            response = requests.get(pr_url, headers=self.headers)
            
            if response.status_code != 200:
                return {
                    "success": False,
                    "error": f"Failed to fetch PR: {response.status_code}"
                }
            
            pr_data = response.json()
            
            # Get PR files
            files_url = f"{pr_url}/files"
            files_response = requests.get(files_url, headers=self.headers)
            
            if files_response.status_code != 200:
                return {
                    "success": False,
                    "error": f"Failed to fetch PR files: {files_response.status_code}"
                }
            
            files_data = files_response.json()
            
            # Analyze changed files
            results = []
            for file_info in files_data:
                if file_info['filename'].endswith('.py'):
                    # Get file content
                    content_url = f"{self.api_base}/repos/{owner}/{repo}/contents/{file_info['filename']}?ref={pr_data['head']['ref']}"
                    content_response = requests.get(content_url, headers=self.headers)
                    
                    if content_response.status_code == 200:
                        content_data = content_response.json()
                        content = base64.b64decode(content_data.get('content', '')).decode('utf-8')
                        
                        # Analyze the file
                        report = code_reviewer.analyze_code(content, file_info['filename'])
                        results.append({
                            'file': file_info['filename'],
                            'report': report,
                            'status': file_info['status'],
                            'additions': file_info['additions'],
                            'deletions': file_info['deletions']
                        })
            
            # Generate summary
            summary = self._generate_summary(results)
            
            return {
                "success": True,
                "pr_number": pr_number,
                "title": pr_data.get('title'),
                "author": pr_data.get('user', {}).get('login'),
                "state": pr_data.get('state'),
                "results": results,
                "summary": summary
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"PR review failed: {str(e)}"
            }
    
    def create_pr_comment(self, owner: str, repo: str, pr_number: int, comment: str, commit_id: str = None, path: str = None, line: int = None) -> Dict[str, Any]:
        """Create a comment on a pull request."""
        try:
            if not self.github_token:
                return {
                    "success": False,
                    "error": "GitHub token required to create comments"
                }
            
            url = f"{self.api_base}/repos/{owner}/{repo}/pulls/{pr_number}/comments"
            
            comment_data = {
                "body": comment
            }
            
            # If line-specific comment
            if commit_id and path and line:
                comment_data.update({
                    "commit_id": commit_id,
                    "path": path,
                    "line": line
                })
            
            response = requests.post(url, headers=self.headers, json=comment_data)
            
            if response.status_code in [200, 201]:
                return {
                    "success": True,
                    "comment_id": response.json().get('id'),
                    "url": response.json().get('html_url'),
                    "message": "Comment created successfully"
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to create comment: {response.status_code}",
                    "message": response.text
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create comment: {str(e)}"
            }
    
    def create_pr_review(self, owner: str, repo: str, pr_number: int, review_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a review on a pull request with comments."""
        try:
            if not self.github_token:
                return {
                    "success": False,
                    "error": "GitHub token required to create reviews"
                }
            
            url = f"{self.api_base}/repos/{owner}/{repo}/pulls/{pr_number}/reviews"
            
            response = requests.post(url, headers=self.headers, json=review_data)
            
            if response.status_code in [200, 201]:
                return {
                    "success": True,
                    "review_id": response.json().get('id'),
                    "url": response.json().get('html_url'),
                    "message": "Review created successfully"
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to create review: {response.status_code}",
                    "message": response.text
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create review: {str(e)}"
            }
    
    def get_pr_commits(self, owner: str, repo: str, pr_number: int) -> Dict[str, Any]:
        """Get commits for a pull request."""
        try:
            url = f"{self.api_base}/repos/{owner}/{repo}/pulls/{pr_number}/commits"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                commits = response.json()
                return {
                    "success": True,
                    "commits": commits,
                    "total_count": len(commits)
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to fetch commits: {response.status_code}",
                    "commits": []
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to fetch commits: {str(e)}",
                "commits": []
            }
    
    def get_pr_files(self, owner: str, repo: str, pr_number: int) -> Dict[str, Any]:
        """Get files changed in a pull request."""
        try:
            url = f"{self.api_base}/repos/{owner}/{repo}/pulls/{pr_number}/files"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                files = response.json()
                return {
                    "success": True,
                    "files": files,
                    "total_count": len(files)
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to fetch files: {response.status_code}",
                    "files": []
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to fetch files: {str(e)}",
                "files": []
            }
    
    def review_and_comment_pr(self, owner: str, repo: str, pr_number: int, auto_comment: bool = True) -> Dict[str, Any]:
        """Review a pull request and optionally add comments."""
        try:
            print(f"🔍 Reviewing PR #{pr_number} in {owner}/{repo}...")
            
            # Get PR details
            pr_result = self.review_pull_request(owner, repo, pr_number)
            if not pr_result["success"]:
                return pr_result
            
            # Get PR files for commenting
            files_result = self.get_pr_files(owner, repo, pr_number)
            if not files_result["success"]:
                return files_result
            
            # Get PR commits
            commits_result = self.get_pr_commits(owner, repo, pr_number)
            if not commits_result["success"]:
                return commits_result
            
            # Prepare review data
            review_comments = []
            review_summary = self._generate_pr_review_summary(pr_result)
            
            if auto_comment and commits_result["commits"]:
                latest_commit = commits_result["commits"][-1]["sha"]
                
                # Create line-specific comments for issues
                for result in pr_result.get("results", []):
                    if "report" in result and "issues" in result["report"]:
                        file_path = result["file"]
                        issues = result["report"]["issues"]
                        
                        # Add comments for critical and high issues
                        for severity in ["critical", "high"]:
                            for issue in issues.get(severity, []):
                                if isinstance(issue, dict) and "line" in issue:
                                    comment_body = self._format_issue_comment(issue, severity)
                                    review_comments.append({
                                        "path": file_path,
                                        "line": issue["line"],
                                        "body": comment_body
                                    })
            
            # Create the review
            review_data = {
                "body": review_summary,
                "event": "COMMENT"  # Can be COMMENT, APPROVE, REQUEST_CHANGES
            }
            
            if review_comments:
                review_data["comments"] = review_comments
            
            review_result = self.create_pr_review(owner, repo, pr_number, review_data)
            
            return {
                "success": True,
                "pr_review": pr_result,
                "review_created": review_result,
                "comments_added": len(review_comments),
                "summary": review_summary
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"PR review and comment failed: {str(e)}"
            }
    
    def _generate_pr_review_summary(self, pr_result: Dict[str, Any]) -> str:
        """Generate a summary for PR review."""
        summary = pr_result.get("summary", {})
        
        summary_text = f"""## 🔍 Code Review Summary

**Repository:** {pr_result.get('title', 'Unknown PR')}
**Author:** {pr_result.get('author', 'Unknown')}
**Overall Grade:** {summary.get('overall_grade', 'N/A')} ({summary.get('average_score', 0)}/100)

### 📊 Statistics
- **Files Analyzed:** {summary.get('total_files', 0)}
- **Total Issues:** {summary.get('total_issues', 0)}
- **Critical Issues:** {summary.get('critical_issues', 0)}
- **High Priority Issues:** {summary.get('high_issues', 0)}
- **Medium Issues:** {summary.get('medium_issues', 0)}
- **Low Issues:** {summary.get('low_issues', 0)}

### 🎯 Recommendations
"""
        
        # Add recommendations based on issues
        if summary.get('critical_issues', 0) > 0:
            summary_text += f"- 🔴 **Critical:** Address {summary['critical_issues']} critical issues immediately\n"
        
        if summary.get('high_issues', 0) > 0:
            summary_text += f"- 🟠 **High:** Fix {summary['high_issues']} high priority issues\n"
        
        if summary.get('average_score', 0) < 70:
            summary_text += "- 🟡 **Quality:** Consider improving overall code quality\n"
        
        summary_text += "\n---\n*This review was generated automatically by the Code Review Agent*"
        
        return summary_text
    
    def _format_issue_comment(self, issue: Dict[str, Any], severity: str) -> str:
        """Format an issue into a comment."""
        severity_emoji = {
            "critical": "🔴",
            "high": "🟠",
            "medium": "🟡",
            "low": "🟢"
        }.get(severity, "ℹ️")
        
        comment = f"""{severity_emoji} **{severity.upper()} Priority Issue**

**Issue:** {issue.get('message', 'Unknown issue')}

**Category:** {issue.get('category', 'Unknown')}

**Suggestion:** {issue.get('suggestion', 'Consider reviewing this code')}

---
*Automated review comment*"""
        
        return comment
    
    def cleanup_local_repository(self, local_path: str):
        """Clean up locally cloned repository."""
        if local_path and os.path.exists(local_path):
            try:
                shutil.rmtree(local_path)
                logger.info(f"Cleaned up: {local_path}")
            except Exception as e:
                logger.error(f"Failed to clean up {local_path}: {e}")

# Global instance
github_reviewer = GitHubCodeReviewer() 