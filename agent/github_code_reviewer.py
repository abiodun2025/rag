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

# Create a global instance
github_reviewer = GitHubCodeReviewer() 