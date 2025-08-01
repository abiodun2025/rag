#!/usr/bin/env python3
"""
GitHub Code Reviewer
===================

Integration with GitHub to perform code reviews on real repositories.
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
    """GitHub integration for code review."""
    
    def __init__(self, github_token: str = None):
        self.github_token = github_token or os.getenv('GITHUB_TOKEN')
        self.api_base = "https://api.github.com"
        self.headers = {}
        
        if self.github_token:
            self.headers = {
                'Authorization': f'token {self.github_token}',
                'Accept': 'application/vnd.github.v3+json'
            }
    
    def test_connection(self) -> Dict[str, Any]:
        """Test GitHub API connection."""
        try:
            response = requests.get(f"{self.api_base}/user", headers=self.headers)
            if response.status_code == 200:
                user_data = response.json()
                return {
                    "success": True,
                    "user": user_data.get('login'),
                    "name": user_data.get('name'),
                    "email": user_data.get('email')
                }
            else:
                return {
                    "success": False,
                    "error": f"GitHub API error: {response.status_code}",
                    "message": response.text
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Connection failed: {str(e)}"
            }
    
    def get_repositories(self, username: str = None) -> Dict[str, Any]:
        """Get list of repositories for a user."""
        try:
            if username:
                url = f"{self.api_base}/users/{username}/repos"
            else:
                url = f"{self.api_base}/user/repos"
            
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                repos = response.json()
                return {
                    "success": True,
                    "repositories": [
                        {
                            "name": repo.get('name'),
                            "full_name": repo.get('full_name'),
                            "description": repo.get('description'),
                            "language": repo.get('language'),
                            "private": repo.get('private'),
                            "url": repo.get('html_url'),
                            "clone_url": repo.get('clone_url')
                        }
                        for repo in repos
                    ]
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to fetch repositories: {response.status_code}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error fetching repositories: {str(e)}"
            }
    
    def get_repository_content(self, owner: str, repo: str, path: str = "") -> Dict[str, Any]:
        """Get content of a repository or specific path."""
        try:
            url = f"{self.api_base}/repos/{owner}/{repo}/contents/{path}"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                content = response.json()
                return {
                    "success": True,
                    "content": content
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to fetch content: {response.status_code}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error fetching content: {str(e)}"
            }
    
    def get_file_content(self, owner: str, repo: str, path: str) -> Dict[str, Any]:
        """Get content of a specific file."""
        try:
            url = f"{self.api_base}/repos/{owner}/{repo}/contents/{path}"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                file_data = response.json()
                if file_data.get('type') == 'file':
                    # Decode content
                    content = base64.b64decode(file_data.get('content', '')).decode('utf-8')
                    return {
                        "success": True,
                        "content": content,
                        "filename": file_data.get('name'),
                        "path": file_data.get('path'),
                        "size": file_data.get('size'),
                        "sha": file_data.get('sha')
                    }
                else:
                    return {
                        "success": False,
                        "error": "Path is not a file"
                    }
            else:
                return {
                    "success": False,
                    "error": f"Failed to fetch file: {response.status_code}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error fetching file: {str(e)}"
            }
    
    def clone_repository(self, repo_url: str, local_path: str = None) -> Dict[str, Any]:
        """Clone a repository locally for analysis."""
        try:
            if not local_path:
                local_path = tempfile.mkdtemp(prefix="github_review_")
            
            # Clone the repository
            result = subprocess.run(
                ['git', 'clone', repo_url, local_path],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "local_path": local_path,
                    "message": "Repository cloned successfully"
                }
            else:
                return {
                    "success": False,
                    "error": f"Git clone failed: {result.stderr}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error cloning repository: {str(e)}"
            }
    
    def analyze_repository(self, owner: str, repo: str, clone_locally: bool = True) -> Dict[str, Any]:
        """Analyze an entire repository."""
        try:
            repo_url = f"https://github.com/{owner}/{repo}.git"
            
            if clone_locally:
                # Clone repository locally
                clone_result = self.clone_repository(repo_url)
                if not clone_result["success"]:
                    return clone_result
                
                local_path = clone_result["local_path"]
                
                # Analyze all files in the repository
                return self._analyze_local_repository(local_path, f"{owner}/{repo}")
            else:
                # Analyze repository via GitHub API
                return self._analyze_remote_repository(owner, repo)
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Error analyzing repository: {str(e)}"
            }
    
    def _analyze_local_repository(self, local_path: str, repo_name: str) -> Dict[str, Any]:
        """Analyze a locally cloned repository."""
        try:
            results = []
            supported_extensions = ['.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.cpp', '.cc', '.cxx', '.h', '.hpp', '.cs']
            
            # Walk through all files
            for root, dirs, files in os.walk(local_path):
                # Skip .git directory
                if '.git' in dirs:
                    dirs.remove('.git')
                
                for file in files:
                    if any(file.endswith(ext) for ext in supported_extensions):
                        filepath = os.path.join(root, file)
                        relative_path = os.path.relpath(filepath, local_path)
                        
                        try:
                            with open(filepath, 'r', encoding='utf-8') as f:
                                code = f.read()
                            
                            # Analyze the file
                            report = code_reviewer.generate_report(code, relative_path)
                            results.append({
                                "file": relative_path,
                                "report": report
                            })
                            
                        except Exception as e:
                            results.append({
                                "file": relative_path,
                                "error": str(e)
                            })
            
            # Calculate overall statistics
            total_files = len(results)
            successful_reviews = len([r for r in results if 'report' in r])
            total_issues = sum([r['report']['issues']['total'] for r in results if 'report' in r])
            avg_score = sum([r['report']['score'] for r in results if 'report' in r]) / successful_reviews if successful_reviews > 0 else 0
            
            return {
                "success": True,
                "repository": repo_name,
                "local_path": local_path,
                "summary": {
                    "total_files": total_files,
                    "successful_reviews": successful_reviews,
                    "total_issues": total_issues,
                    "average_score": round(avg_score, 2)
                },
                "results": results
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error analyzing local repository: {str(e)}"
            }
    
    def _analyze_remote_repository(self, owner: str, repo: str) -> Dict[str, Any]:
        """Analyze repository via GitHub API (limited to smaller files)."""
        try:
            # Get repository content
            content_result = self.get_repository_content(owner, repo)
            if not content_result["success"]:
                return content_result
            
            results = []
            supported_extensions = ['.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.cpp', '.cc', '.cxx', '.h', '.hpp', '.cs']
            
            # Analyze files (this is a simplified version - for full analysis, clone locally)
            for item in content_result["content"]:
                if item.get('type') == 'file':
                    filename = item.get('name', '')
                    if any(filename.endswith(ext) for ext in supported_extensions):
                        # Only analyze smaller files via API
                        if item.get('size', 0) < 1000000:  # 1MB limit
                            file_result = self.get_file_content(owner, repo, item.get('path', ''))
                            if file_result["success"]:
                                report = code_reviewer.generate_report(
                                    file_result["content"], 
                                    file_result["filename"]
                                )
                                results.append({
                                    "file": item.get('path', ''),
                                    "report": report
                                })
            
            return {
                "success": True,
                "repository": f"{owner}/{repo}",
                "summary": {
                    "total_files": len(results),
                    "note": "Limited analysis via API. Use clone_locally=True for full analysis."
                },
                "results": results
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error analyzing remote repository: {str(e)}"
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
            
<<<<<<< Updated upstream
            # Get PR files
=======
            # Get PR diff (the actual changes)
            diff_url = f"{pr_url}.diff"
            # Use Accept header to get diff format instead of JSON
            diff_headers = self.headers.copy()
            diff_headers['Accept'] = 'application/vnd.github.v3.diff'
            diff_response = requests.get(diff_url, headers=diff_headers)
            
            if diff_response.status_code != 200:
                return {
                    "success": False,
                    "error": f"Failed to fetch PR diff: {diff_response.status_code}"
                }
            
            diff_content = diff_response.text
            
            # Get PR files for metadata
>>>>>>> Stashed changes
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
            supported_extensions = ['.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.cpp', '.cc', '.cxx', '.h', '.hpp', '.cs']
            
            for file_info in files_data:
                filename = file_info.get('filename', '')
                if any(filename.endswith(ext) for ext in supported_extensions):
                    # Get file content
                    file_result = self.get_file_content(owner, repo, filename)
                    if file_result["success"]:
                        report = code_reviewer.generate_report(
                            file_result["content"], 
                            filename
                        )
                        results.append({
                            "file": filename,
                            "status": file_info.get('status'),
                            "additions": file_info.get('additions'),
                            "deletions": file_info.get('deletions'),
                            "report": report
                        })
            
            return {
                "success": True,
                "pull_request": {
                    "number": pr_number,
                    "title": pr_data.get('title'),
                    "author": pr_data.get('user', {}).get('login'),
                    "state": pr_data.get('state'),
                    "changed_files": len(files_data)
                },
                "results": results
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error reviewing pull request: {str(e)}"
            }
    
    def cleanup_local_repository(self, local_path: str):
        """Clean up locally cloned repository."""
        try:
            if os.path.exists(local_path):
                shutil.rmtree(local_path)
                return True
        except Exception as e:
            logger.error(f"Error cleaning up {local_path}: {e}")
            return False

<<<<<<< Updated upstream
# Create a global instance
=======
    def get_commit_diff(self, owner: str, repo: str, commit_sha: str) -> Dict[str, Any]:
        """Get the diff for a specific commit."""
        try:
            url = f"{self.api_base}/repos/{owner}/{repo}/commits/{commit_sha}"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code != 200:
                return {
                    "success": False,
                    "error": f"Failed to fetch commit: {response.status_code}"
                }
            
            commit_data = response.json()
            
            # Get the diff for this commit
            diff_url = f"{self.api_base}/repos/{owner}/{repo}/commits/{commit_sha}.diff"
            # Use Accept header to get diff format instead of JSON
            diff_headers = self.headers.copy()
            diff_headers['Accept'] = 'application/vnd.github.v3.diff'
            diff_response = requests.get(diff_url, headers=diff_headers)
            
            if diff_response.status_code != 200:
                return {
                    "success": False,
                    "error": f"Failed to fetch commit diff: {diff_response.status_code}"
                }
            
            return {
                "success": True,
                "commit": commit_data,
                "diff": diff_response.text,
                "message": commit_data.get('commit', {}).get('message', ''),
                "author": commit_data.get('commit', {}).get('author', {}).get('name', ''),
                "date": commit_data.get('commit', {}).get('author', {}).get('date', ''),
                "files_changed": len(commit_data.get('files', []))
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to fetch commit diff: {str(e)}"
            }
    
    def review_commit(self, owner: str, repo: str, commit_sha: str) -> Dict[str, Any]:
        """Review a specific commit by analyzing its diff."""
        try:
            # Get commit diff
            commit_result = self.get_commit_diff(owner, repo, commit_sha)
            if not commit_result["success"]:
                return commit_result
            
            diff_content = commit_result["diff"]
            commit_data = commit_result["commit"]
            
            # Analyze the diff for each file
            results = []
            files_data = commit_data.get('files', [])
            
            for file_info in files_data:
                if file_info['filename'].endswith('.py'):
                    # Extract the diff for this specific file
                    file_diff = self._extract_file_diff(diff_content, file_info['filename'])
                    
                    if file_diff:
                        # Analyze the diff content
                        report = self._analyze_diff_content(file_diff, file_info['filename'])
                        results.append({
                            'file': file_info['filename'],
                            'report': report,
                            'status': file_info['status'],
                            'additions': file_info['additions'],
                            'deletions': file_info['deletions'],
                            'diff': file_diff
                        })
            
            # Generate summary for this commit
            summary = self._generate_commit_summary(results, commit_result)
            
            return {
                "success": True,
                "commit_sha": commit_sha,
                "message": commit_result["message"],
                "author": commit_result["author"],
                "date": commit_result["date"],
                "results": results,
                "summary": summary
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Commit review failed: {str(e)}"
            }
    
    def review_pull_request_commits(self, owner: str, repo: str, pr_number: int) -> Dict[str, Any]:
        """Review each commit in a pull request individually."""
        try:
            print(f"🔍 Reviewing commits in PR #{pr_number} in {owner}/{repo}...")
            
            # Get PR commits
            commits_result = self.get_pr_commits(owner, repo, pr_number)
            if not commits_result["success"]:
                return commits_result
            
            commits = commits_result["commits"]
            print(f"📝 Found {len(commits)} commits to review")
            
            # Review each commit
            commit_reviews = []
            total_issues = 0
            total_score = 0
            
            for i, commit in enumerate(commits, 1):
                commit_sha = commit["sha"]
                commit_message = commit["commit"]["message"]
                
                print(f"🔍 Reviewing commit {i}/{len(commits)}: {commit_sha[:8]} - {commit_message[:50]}...")
                
                # Review this commit
                commit_review = self.review_commit(owner, repo, commit_sha)
                
                if commit_review["success"]:
                    commit_reviews.append(commit_review)
                    
                    # Aggregate issues and scores
                    commit_score = 0
                    commit_issues = 0
                    
                    for result in commit_review.get("results", []):
                        if "report" in result:
                            report = result["report"]
                            commit_score += report.get("score", 0)
                            commit_issues += report.get("issues", {}).get("total", 0)
                    
                    total_score += commit_score
                    total_issues += commit_issues
                    
                    print(f"   📊 Score: {commit_score}, Issues: {commit_issues}")
                else:
                    print(f"   ❌ Failed to review commit: {commit_review.get('error', 'Unknown error')}")
            
            # Generate overall summary
            overall_summary = self._generate_commit_reviews_summary(commit_reviews, total_score, total_issues)
            
            return {
                "success": True,
                "pr_number": pr_number,
                "total_commits": len(commits),
                "reviewed_commits": len(commit_reviews),
                "commit_reviews": commit_reviews,
                "total_score": total_score,
                "total_issues": total_issues,
                "average_score": total_score / len(commit_reviews) if commit_reviews else 0,
                "summary": overall_summary
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"PR commits review failed: {str(e)}"
            }
    
    def _generate_commit_summary(self, results: List[Dict], commit_data: Dict) -> str:
        """Generate a summary for a single commit."""
        if not results:
            return "No Python files changed in this commit."
        
        total_files = len(results)
        total_issues = 0
        critical_issues = 0
        high_issues = 0
        medium_issues = 0
        low_issues = 0
        total_score = 0
        
        for result in results:
            if "report" in result:
                report = result["report"]
                issues = report.get("issues", {})
                total_issues += issues.get("total", 0)
                critical_issues += issues.get("critical", 0)
                high_issues += issues.get("high", 0)
                medium_issues += issues.get("medium", 0)
                low_issues += issues.get("low", 0)
                total_score += report.get("score", 0)
        
        average_score = total_score / total_files if total_files > 0 else 0
        grade = self._calculate_grade(average_score)
        
        summary = f"""## Commit Review: {commit_data['message'][:50]}...

**📊 Summary:**
- **Files Changed:** {total_files} Python files
- **Average Score:** {average_score:.1f}/100 ({grade})
- **Total Issues:** {total_issues}
  - 🔴 Critical: {critical_issues}
  - 🟠 High: {high_issues}
  - 🟡 Medium: {medium_issues}
  - 🟢 Low: {low_issues}

**📝 Changes:**
"""
        
        for result in results:
            file_name = result["file"]
            additions = result.get("additions", 0)
            deletions = result.get("deletions", 0)
            score = result["report"].get("score", 0)
            grade = result["report"].get("grade", "F")
            
            summary += f"- **{file_name}:** +{additions} -{deletions} lines (Score: {score}/100, Grade: {grade})\n"
        
        return summary
    
    def _generate_commit_reviews_summary(self, commit_reviews: List[Dict], total_score: int, total_issues: int) -> str:
        """Generate an overall summary for all commit reviews."""
        if not commit_reviews:
            return "No commits were successfully reviewed."
        
        average_score = total_score / len(commit_reviews)
        overall_grade = self._calculate_grade(average_score)
        
        summary = f"""## Commit-by-Commit Review Summary

**📊 Overall Statistics:**
- **Commits Reviewed:** {len(commit_reviews)}
- **Average Score:** {average_score:.1f}/100 ({overall_grade})
- **Total Issues Found:** {total_issues}

**📝 Commit Breakdown:**
"""
        
        for i, commit_review in enumerate(commit_reviews, 1):
            commit_sha = commit_review["commit_sha"][:8]
            message = commit_review["message"][:50]
            author = commit_review["author"]
            
            # Calculate commit score
            commit_score = 0
            commit_issues = 0
            for result in commit_review.get("results", []):
                if "report" in result:
                    report = result["report"]
                    commit_score += report.get("score", 0)
                    commit_issues += report.get("issues", {}).get("total", 0)
            
            avg_commit_score = commit_score / len(commit_review.get("results", [])) if commit_review.get("results") else 0
            grade = self._calculate_grade(avg_commit_score)
            
            summary += f"{i}. **{commit_sha}** by {author} - {message}...\n"
            summary += f"   Score: {avg_commit_score:.1f}/100 ({grade}), Issues: {commit_issues}\n\n"
        
        return summary

# Global instance
>>>>>>> Stashed changes
github_reviewer = GitHubCodeReviewer() 