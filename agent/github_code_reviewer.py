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
import re

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
    
    def get_repository_pull_requests(self, owner: str, repo: str, state: str = "open") -> Dict[str, Any]:
        """Get all pull requests for a specific repository."""
        try:
            url = f"{self.api_base}/repos/{owner}/{repo}/pulls"
            params = {"state": state, "sort": "updated", "direction": "desc"}
            
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                prs = response.json()
                pr_list = []
                
                for pr in prs:
                    pr_info = {
                        "number": pr.get('number'),
                        "title": pr.get('title'),
                        "state": pr.get('state'),
                        "author": pr.get('user', {}).get('login'),
                        "author_avatar": pr.get('user', {}).get('avatar_url'),
                        "created_at": pr.get('created_at'),
                        "updated_at": pr.get('updated_at'),
                        "merged_at": pr.get('merged_at'),
                        "closed_at": pr.get('closed_at'),
                        "head_branch": pr.get('head', {}).get('ref'),
                        "base_branch": pr.get('base', {}).get('ref'),
                        "head_sha": pr.get('head', {}).get('sha'),
                        "base_sha": pr.get('base', {}).get('sha'),
                        "draft": pr.get('draft', False),
                        "mergeable": pr.get('mergeable'),
                        "mergeable_state": pr.get('mergeable_state'),
                        "comments": pr.get('comments', 0),
                        "review_comments": pr.get('review_comments', 0),
                        "commits": pr.get('commits', 0),
                        "additions": pr.get('additions', 0),
                        "deletions": pr.get('deletions', 0),
                        "changed_files": pr.get('changed_files', 0),
                        "labels": [label.get('name') for label in pr.get('labels', [])],
                        "assignees": [assignee.get('login') for assignee in pr.get('assignees', [])],
                        "requested_reviewers": [reviewer.get('login') for reviewer in pr.get('requested_reviewers', [])],
                        "html_url": pr.get('html_url'),
                        "diff_url": pr.get('diff_url'),
                        "patch_url": pr.get('patch_url'),
                        "body": pr.get('body', '')
                    }
                    pr_list.append(pr_info)
                
                return {
                    "success": True,
                    "pull_requests": pr_list,
                    "total_count": len(pr_list),
                    "repository": f"{owner}/{repo}"
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to fetch pull requests: {response.status_code}",
                    "pull_requests": []
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to fetch pull requests: {str(e)}",
                "pull_requests": []
            }
    
    def get_all_accessible_pull_requests(self, state: str = "open", include_private: bool = True) -> Dict[str, Any]:
        """Get all pull requests from all accessible repositories."""
        try:
            if not self.github_token:
                return {
                    "success": False,
                    "error": "GitHub token required to access pull requests",
                    "pull_requests": []
                }
            
            # Get all repositories
            repos_result = self.get_user_repositories(include_private)
            if not repos_result["success"]:
                return repos_result
            
            all_prs = []
            total_repos = len(repos_result["repositories"])
            
            for i, repo in enumerate(repos_result["repositories"], 1):
                try:
                    owner, repo_name = repo["full_name"].split("/", 1)
                    prs_result = self.get_repository_pull_requests(owner, repo_name, state)
                    
                    if prs_result["success"]:
                        for pr in prs_result["pull_requests"]:
                            pr["repository"] = repo["full_name"]
                            pr["repo_owner"] = owner
                            pr["repo_name"] = repo_name
                            pr["repo_private"] = repo["private"]
                            pr["repo_language"] = repo.get("language", "Unknown")
                        all_prs.extend(prs_result["pull_requests"])
                    
                except Exception as e:
                    logger.warning(f"Failed to fetch PRs for {repo['full_name']}: {e}")
                    continue
            
            # Sort by updated date (most recent first)
            all_prs.sort(key=lambda x: x.get('updated_at', ''), reverse=True)
            
            return {
                "success": True,
                "pull_requests": all_prs,
                "total_count": len(all_prs),
                "repositories_checked": total_repos
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to fetch all pull requests: {str(e)}",
                "pull_requests": []
            }
    
    def get_pull_request_details(self, owner: str, repo: str, pr_number: int) -> Dict[str, Any]:
        """Get detailed information about a specific pull request."""
        try:
            url = f"{self.api_base}/repos/{owner}/{repo}/pulls/{pr_number}"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                pr = response.json()
                
                # Get additional information
                reviews_url = f"{self.api_base}/repos/{owner}/{repo}/pulls/{pr_number}/reviews"
                reviews_response = requests.get(reviews_url, headers=self.headers)
                reviews = reviews_response.json() if reviews_response.status_code == 200 else []
                
                # Get comments
                comments_url = f"{self.api_base}/repos/{owner}/{repo}/issues/{pr_number}/comments"
                comments_response = requests.get(comments_url, headers=self.headers)
                comments = comments_response.json() if comments_response.status_code == 200 else []
                
                pr_details = {
                    "number": pr.get('number'),
                    "title": pr.get('title'),
                    "state": pr.get('state'),
                    "author": pr.get('user', {}).get('login'),
                    "author_avatar": pr.get('user', {}).get('avatar_url'),
                    "created_at": pr.get('created_at'),
                    "updated_at": pr.get('updated_at'),
                    "merged_at": pr.get('merged_at'),
                    "closed_at": pr.get('closed_at'),
                    "head_branch": pr.get('head', {}).get('ref'),
                    "base_branch": pr.get('base', {}).get('ref'),
                    "head_sha": pr.get('head', {}).get('sha'),
                    "base_sha": pr.get('base', {}).get('sha'),
                    "draft": pr.get('draft', False),
                    "mergeable": pr.get('mergeable'),
                    "mergeable_state": pr.get('mergeable_state'),
                    "comments": pr.get('comments', 0),
                    "review_comments": pr.get('review_comments', 0),
                    "commits": pr.get('commits', 0),
                    "additions": pr.get('additions', 0),
                    "deletions": pr.get('deletions', 0),
                    "changed_files": pr.get('changed_files', 0),
                    "labels": [label.get('name') for label in pr.get('labels', [])],
                    "assignees": [assignee.get('login') for assignee in pr.get('assignees', [])],
                    "requested_reviewers": [reviewer.get('login') for reviewer in pr.get('requested_reviewers', [])],
                    "html_url": pr.get('html_url'),
                    "diff_url": pr.get('diff_url'),
                    "patch_url": pr.get('patch_url'),
                    "body": pr.get('body', ''),
                    "reviews": reviews,
                    "comments": comments,
                    "repository": f"{owner}/{repo}"
                }
                
                return {
                    "success": True,
                    "pull_request": pr_details
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to fetch pull request: {response.status_code}",
                    "message": response.text
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to fetch pull request details: {str(e)}"
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
        """Review a specific pull request by analyzing the diff/changes."""
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
            
            # Get PR diff (the actual changes)
            diff_url = f"{pr_url}.diff"
            diff_response = requests.get(diff_url, headers=self.headers)
            
            if diff_response.status_code != 200:
                return {
                    "success": False,
                    "error": f"Failed to fetch PR diff: {diff_response.status_code}"
                }
            
            diff_content = diff_response.text
            
            # Get PR files for metadata
            files_url = f"{pr_url}/files"
            files_response = requests.get(files_url, headers=self.headers)
            
            if files_response.status_code != 200:
                return {
                    "success": False,
                    "error": f"Failed to fetch PR files: {files_response.status_code}"
                }
            
            files_data = files_response.json()
            
            # Analyze the diff and changed files
            results = []
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
    
    def _extract_file_diff(self, diff_content: str, filename: str) -> str:
        """Extract the diff for a specific file from the full diff."""
        lines = diff_content.split('\n')
        file_diff = []
        in_file = False
        
        for line in lines:
            if line.startswith(f'diff --git a/{filename} b/{filename}'):
                in_file = True
                file_diff.append(line)
            elif in_file and line.startswith('diff --git'):
                # Found next file, stop here
                break
            elif in_file:
                file_diff.append(line)
        
        return '\n'.join(file_diff) if file_diff else None
    
    def _analyze_diff_content(self, diff_content: str, filename: str) -> Dict[str, Any]:
        """Analyze the diff content for code review issues."""
        try:
            # Parse the diff to extract added/modified lines
            added_lines = []
            modified_lines = []
            removed_lines = []
            
            lines = diff_content.split('\n')
            current_line_number = 0
            
            for line in lines:
                if line.startswith('@@'):
                    # Parse the @@ line to get line numbers
                    match = re.search(r'@@ -(\d+),?(\d+)? \+(\d+),?(\d+)? @@', line)
                    if match:
                        old_start = int(match.group(1))
                        new_start = int(match.group(3))
                        current_line_number = new_start
                elif line.startswith('+') and not line.startswith('+++'):
                    # Added line
                    added_lines.append({
                        'line_number': current_line_number,
                        'content': line[1:],
                        'type': 'added'
                    })
                    current_line_number += 1
                elif line.startswith('-') and not line.startswith('---'):
                    # Removed line
                    removed_lines.append({
                        'line_number': current_line_number,
                        'content': line[1:],
                        'type': 'removed'
                    })
                elif line.startswith(' '):
                    # Context line (unchanged)
                    current_line_number += 1
            
            # Analyze the changes for issues
            issues = []
            
            # Analyze added lines for potential issues
            for line_info in added_lines:
                line_issues = self._analyze_line_for_issues(line_info['content'], line_info['line_number'], 'added')
                issues.extend(line_issues)
            
            # Analyze removed lines for potential issues
            for line_info in removed_lines:
                line_issues = self._analyze_line_for_issues(line_info['content'], line_info['line_number'], 'removed')
                issues.extend(line_issues)
            
            # Group issues by severity
            critical_issues = [i for i in issues if i.get('severity') == 'critical']
            high_issues = [i for i in issues if i.get('severity') == 'high']
            medium_issues = [i for i in issues if i.get('severity') == 'medium']
            low_issues = [i for i in issues if i.get('severity') == 'low']
            
            # Calculate score based on changes
            total_issues = len(issues)
            score = 100
            score -= len(critical_issues) * 10
            score -= len(high_issues) * 5
            score -= len(medium_issues) * 2
            score -= len(low_issues) * 1
            score = max(0, score)
            
            return {
                "filename": filename,
                "language": "python",
                "score": score,
                "grade": self._calculate_grade(score),
                "changes": {
                    "added_lines": len(added_lines),
                    "removed_lines": len(removed_lines),
                    "total_changes": len(added_lines) + len(removed_lines)
                },
                "issues": {
                    "total": total_issues,
                    "critical": len(critical_issues),
                    "high": len(high_issues),
                    "medium": len(medium_issues),
                    "low": len(low_issues),
                    "details": issues
                },
                "diff_summary": {
                    "added_lines": added_lines,
                    "removed_lines": removed_lines
                }
            }
            
        except Exception as e:
            return {
                "filename": filename,
                "language": "python",
                "score": 0,
                "grade": "F",
                "error": str(e),
                "issues": {
                    "total": 0,
                    "critical": 0,
                    "high": 0,
                    "medium": 0,
                    "low": 0,
                    "details": []
                }
            }
    
    def _analyze_line_for_issues(self, line_content: str, line_number: int, change_type: str) -> List[Dict[str, Any]]:
        """Analyze a single line for potential issues."""
        issues = []
        
        # Security issues
        if any(pattern in line_content.lower() for pattern in ['eval(', 'exec(', 'os.system(', 'subprocess.call(']):
            issues.append({
                'line': line_number,
                'severity': 'critical',
                'category': 'security',
                'message': f'Potential security vulnerability: {change_type} line contains dangerous function call',
                'suggestion': 'Use safer alternatives and validate inputs'
            })
        
        # Performance issues
        if 'for ' in line_content and ' in ' in line_content and 'range(' in line_content:
            if 'range(len(' in line_content:
                issues.append({
                    'line': line_number,
                    'severity': 'medium',
                    'category': 'performance',
                    'message': f'Performance issue: {change_type} line uses inefficient range(len()) pattern',
                    'suggestion': 'Use enumerate() instead of range(len())'
                })
        
        # Code style issues
        if len(line_content) > 120:
            issues.append({
                'line': line_number,
                'severity': 'low',
                'category': 'style',
                'message': f'Style issue: {change_type} line is too long ({len(line_content)} characters)',
                'suggestion': 'Break long lines to improve readability'
            })
        
        # Error handling issues
        if 'try:' in line_content and change_type == 'added':
            # Check if there's proper exception handling
            pass  # Could add more sophisticated checks
        
        # Documentation issues
        if line_content.strip().startswith('def ') and not any(doc in line_content for doc in ['"""', "'''"]):
            issues.append({
                'line': line_number,
                'severity': 'medium',
                'category': 'documentation',
                'message': f'Documentation issue: {change_type} function definition without docstring',
                'suggestion': 'Add a docstring to describe the function purpose and parameters'
            })
        
        return issues
    
    def _calculate_grade(self, score: int) -> str:
        """Calculate grade based on score."""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
    
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
                
                # Create line-specific comments for issues based on diff
                for result in pr_result.get("results", []):
                    if "report" in result and "issues" in result["report"]:
                        file_path = result["file"]
                        issues = result["report"]["issues"]
                        diff_summary = result["report"].get("diff_summary", {})
                        
                        # Get all issues from the details list
                        issue_details = issues.get("details", [])
                        
                        # Add comments for critical and high issues
                        for issue in issue_details:
                            severity = issue.get("severity", "medium")
                            if severity in ["critical", "high"] and "line" in issue:
                                comment_body = self._format_issue_comment(issue, severity)
                                
                                # Find the corresponding line in the diff
                                line_number = issue["line"]
                                added_lines = diff_summary.get("added_lines", [])
                                
                                # Check if this line was actually added in the diff
                                line_found = any(line["line_number"] == line_number for line in added_lines)
                                
                                if line_found:
                                    review_comments.append({
                                        "path": file_path,
                                        "line": line_number,
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
        
        # Calculate total changes across all files
        total_additions = 0
        total_deletions = 0
        total_files_changed = len(pr_result.get("results", []))
        
        for result in pr_result.get("results", []):
            if "report" in result and "changes" in result["report"]:
                changes = result["report"]["changes"]
                total_additions += changes.get("added_lines", 0)
                total_deletions += changes.get("removed_lines", 0)
        
        summary_text = f"""## 🔍 Code Review Summary

**Repository:** {pr_result.get('title', 'Unknown PR')}
**Author:** {pr_result.get('author', 'Unknown')}
**Overall Grade:** {summary.get('overall_grade', 'N/A')} ({summary.get('average_score', 0)}/100)

### 📊 Change Analysis
- **Files Changed:** {total_files_changed}
- **Lines Added:** {total_additions}
- **Lines Removed:** {total_deletions}
- **Net Changes:** {total_additions - total_deletions}

### 🎯 Issues Found
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
        
        if total_additions > 100:
            summary_text += "- 📏 **Size:** This is a large PR. Consider breaking it into smaller changes\n"
        
        summary_text += "\n---\n*This review analyzes the actual changes (diff) between branches*"
        
        return summary_text
    
    def _format_issue_comment(self, issue: Dict[str, Any], severity: str) -> str:
        """Format an issue into a comment."""
        severity_emoji = {
            "critical": "🔴",
            "high": "🟠",
            "medium": "🟡",
            "low": "🟢"
        }.get(severity, "ℹ️")
        
        category_emoji = {
            "security": "🔒",
            "performance": "⚡",
            "style": "🎨",
            "documentation": "📝",
            "error_handling": "⚠️",
            "architecture": "🏗️"
        }.get(issue.get('category', ''), "💡")
        
        comment = f"""{severity_emoji} **{severity.upper()} Priority Issue**

{category_emoji} **Category:** {issue.get('category', 'Code Quality').title()}

**Issue:** {issue.get('message', 'Unknown issue')}

**Suggestion:** {issue.get('suggestion', 'Consider reviewing this code')}

**Line Analysis:** This line was added/modified in your PR. Please review the suggested improvement.

---
*Automated code review comment*"""
        
        return comment
    
    def comment_all_pull_requests(self, state: str = "open", include_private: bool = True, auto_comment: bool = True) -> Dict[str, Any]:
        """Comment on all accessible pull requests."""
        try:
            print(f"🔍 Starting automated commenting on all {state} pull requests...")
            
            # Get all pull requests
            prs_result = self.get_all_accessible_pull_requests(state, include_private)
            if not prs_result["success"]:
                return prs_result
            
            prs = prs_result["pull_requests"]
            if not prs:
                return {
                    "success": True,
                    "message": f"No {state} pull requests found to comment on",
                    "total_prs": 0,
                    "commented_prs": 0,
                    "results": []
                }
            
            print(f"📊 Found {len(prs)} {state} pull requests to process")
            
            results = []
            commented_count = 0
            
            for i, pr in enumerate(prs, 1):
                try:
                    print(f"📝 Processing PR {i}/{len(prs)}: {pr['repository']}#{pr['number']}")
                    
                    # Comment on this PR
                    comment_result = self.review_and_comment_pr(
                        owner=pr["repo_owner"],
                        repo=pr["repo_name"],
                        pr_number=pr["number"],
                        auto_comment=auto_comment
                    )
                    
                    result = {
                        "repository": pr["repository"],
                        "pr_number": pr["number"],
                        "title": pr["title"],
                        "author": pr["author"],
                        "success": comment_result["success"],
                        "comments_added": comment_result.get("comments_added", 0),
                        "error": comment_result.get("error") if not comment_result["success"] else None
                    }
                    
                    if comment_result["success"]:
                        commented_count += 1
                        print(f"✅ Successfully commented on {pr['repository']}#{pr['number']}")
                    else:
                        print(f"❌ Failed to comment on {pr['repository']}#{pr['number']}: {comment_result.get('error', 'Unknown error')}")
                    
                    results.append(result)
                    
                except Exception as e:
                    print(f"❌ Error processing {pr['repository']}#{pr['number']}: {e}")
                    results.append({
                        "repository": pr["repository"],
                        "pr_number": pr["number"],
                        "title": pr["title"],
                        "author": pr["author"],
                        "success": False,
                        "comments_added": 0,
                        "error": str(e)
                    })
            
            return {
                "success": True,
                "message": f"Completed commenting on {len(prs)} pull requests",
                "total_prs": len(prs),
                "commented_prs": commented_count,
                "failed_prs": len(prs) - commented_count,
                "results": results
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to comment on pull requests: {str(e)}"
            }
    
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