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
import re  # Add re import at module level

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
            
            # Get the diff content
            diff_url = f"{url}.diff"
            diff_headers = self.headers.copy()
            diff_headers['Accept'] = 'application/vnd.github.v3.diff'
            diff_response = requests.get(diff_url, headers=diff_headers)
            
            if diff_response.status_code != 200:
                return {
                    "success": False,
                    "error": f"Failed to fetch commit diff: {diff_response.status_code}"
                }
            
            diff_content = diff_response.text
            
            return {
                "success": True,
                "commit": commit_data,
                "diff": diff_content
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error getting commit diff: {str(e)}"
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
            summary = self._generate_commit_summary(results, commit_data)
            
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
            commits_result = self.get_pull_request_commits(owner, repo, pr_number)
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
    
    def _analyze_diff_content(self, diff_content: str, filename: str) -> Dict[str, Any]:
        """Analyze diff content for code issues."""
        try:
            if not diff_content.strip():
                return {
                    "success": True,
                    "score": 100,
                    "total_issues": 0,
                    "issues": []
                }
            
            # Parse the diff content to get actual line numbers
            lines = diff_content.split('\n')
            issues = []
            total_score = 100
            current_line_number = 0
            
            for line in lines:
                # Parse diff header to get line numbers
                if line.startswith('@@'):
                    # Extract line numbers from diff header
                    # Format: @@ -old_start,old_count +new_start,new_count @@
                    import re
                    match = re.search(r'@@ -(\d+),?\d* \+(\d+),?\d* @@', line)
                    if match:
                        current_line_number = int(match.group(2)) - 1  # Start at new line number
                elif line.startswith('+') and not line.startswith('+++'):
                    current_line_number += 1
                    # Remove the + prefix and analyze the actual content
                    content = line[1:]
                    
                    # Analyze this line for issues
                    line_issues = self._analyze_line_for_issues(content, current_line_number, filename)
                    issues.extend(line_issues)
                    
                    # Calculate score deduction based on issues
                    for issue in line_issues:
                        severity = issue.get('severity', 'low')
                        if severity == 'critical':
                            total_score -= 10
                        elif severity == 'high':
                            total_score -= 5
                        elif severity == 'medium':
                            total_score -= 2
                        elif severity == 'low':
                            total_score -= 1
                elif line.startswith(' ') or line.startswith('-'):
                    # Context line or removed line, increment line number for context
                    if not line.startswith('-'):
                        current_line_number += 1
            
            # Ensure score doesn't go below 0
            total_score = max(0, total_score)
            
            return {
                "success": True,
                "score": total_score,
                "total_issues": len(issues),
                "issues": issues
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to analyze diff content: {str(e)}",
                "score": 0,
                "total_issues": 0,
                "issues": []
            }
    
    def _analyze_line_for_issues(self, line_content: str, line_num: int, filename: str) -> List[Dict]:
        """Analyze a single line of code for potential issues."""
        issues = []
        
        # Skip empty lines and comments for most checks
        if not line_content.strip() or line_content.strip().startswith('#'):
            return issues
        
        # Get file extension for language-specific checks
        file_ext = filename.split('.')[-1].lower() if '.' in filename else ''
        
        # General code quality checks (applied to all file types)
        
        # Long lines
        if len(line_content) > 100:
            issues.append({
                "line": line_num,
                "severity": "medium",
                "category": "style",
                "message": f"Line is too long ({len(line_content)} characters)",
                "suggestion": "Consider breaking the line into multiple lines for better readability"
            })
        
        # Hardcoded strings (but skip logging/debug statements)
        if len(line_content) > 30 and '"' in line_content and "'" in line_content:
            # Skip if it looks like a logging statement
            if not any(keyword in line_content.lower() for keyword in ['print(', 'logger.', 'log.', 'debug', 'info', 'warn', 'error']):
                issues.append({
                    "line": line_num,
                    "severity": "medium",
                    "category": "maintainability",
                    "message": "Hardcoded string detected",
                    "suggestion": "Consider extracting to a constant or configuration variable"
                })
        
        # Magic numbers (but exclude 0 and 1)
        import re
        magic_numbers = re.findall(r'\b[2-9]\d*\b', line_content)
        if magic_numbers:
            issues.append({
                "line": line_num,
                "severity": "medium",
                "category": "maintainability",
                "message": f"Magic numbers detected: {', '.join(magic_numbers)}",
                "suggestion": "Consider defining constants for these values"
            })
        
        # Inconsistent indentation
        if line_content.startswith(' ') and not line_content.startswith('    '):
            issues.append({
                "line": line_num,
                "severity": "high",
                "category": "style",
                "message": "Inconsistent indentation detected",
                "suggestion": "Use consistent indentation (4 spaces recommended)"
            })
        
        # Trailing whitespace
        if line_content.endswith(' '):
            issues.append({
                "line": line_num,
                "severity": "low",
                "category": "style",
                "message": "Trailing whitespace detected",
                "suggestion": "Remove trailing whitespace"
            })
        
        # Multiple spaces
        if '  ' in line_content and not line_content.startswith('  '):
            issues.append({
                "line": line_num,
                "severity": "low",
                "category": "style",
                "message": "Multiple consecutive spaces detected",
                "suggestion": "Use single spaces for indentation"
            })
        
        # Python-specific checks
        if file_ext == 'py':
            # Security patterns
            security_patterns = [
                (r'eval\s*\(', 'eval() usage detected', 'critical', 'security'),
                (r'exec\s*\(', 'exec() usage detected', 'critical', 'security'),
                (r'compile\s*\(', 'compile() usage detected', 'critical', 'security'),
                (r'__import__\s*\(', '__import__() usage detected', 'critical', 'security'),
                (r'input\s*\(', 'input() usage detected', 'high', 'security'),
                (r'pickle\.loads', 'pickle.loads() usage detected', 'high', 'security'),
                (r'os\.system\s*\(', 'os.system() usage detected', 'high', 'security'),
                (r'subprocess\.call\s*\(', 'subprocess.call() usage detected', 'high', 'security'),
            ]
            
            for pattern, message, severity, category in security_patterns:
                if re.search(pattern, line_content):
                    issues.append({
                        "line": line_num,
                        "severity": severity,
                        "category": category,
                        "message": message,
                        "suggestion": "Consider using safer alternatives"
                    })
            
            # SQL Injection patterns
            sql_patterns = [
                (r'f".*\{.*\}.*"', 'f-string with potential SQL injection', 'high', 'security'),
                (r'\+.*\+', 'String concatenation with potential SQL injection', 'high', 'security'),
            ]
            
            for pattern, message, severity, category in sql_patterns:
                if re.search(pattern, line_content):
                    issues.append({
                        "line": line_num,
                        "severity": severity,
                        "category": category,
                        "message": message,
                        "suggestion": "Use parameterized queries to prevent SQL injection"
                    })
            
            # Variable naming
            if re.search(r'\b[a-z][a-z0-9_]*\s*=', line_content) and len(re.findall(r'\b[a-z][a-z0-9_]*\s*=', line_content)[0].split('=')[0].strip()) < 3:
                issues.append({
                    "line": line_num,
                    "severity": "medium",
                    "category": "readability",
                    "message": "Variable name might be too short or generic",
                    "suggestion": "Use more descriptive variable names"
                })
            
            # Missing error handling
            error_handling_patterns = [
                (r'requests\.get\s*\(', 'requests.get() without error handling'),
                (r'requests\.post\s*\(', 'requests.post() without error handling'),
                (r'urllib\.', 'urllib usage without error handling'),
                (r'httplib\.', 'httplib usage without error handling'),
                (r'socket\.', 'socket usage without error handling'),
            ]
            
            for pattern, message in error_handling_patterns:
                if re.search(pattern, line_content):
                    issues.append({
                        "line": line_num,
                        "severity": "high",
                        "category": "error_handling",
                        "message": message,
                        "suggestion": "Wrap in try-except block for proper error handling"
                    })
            
            # Documentation
            if line_content.strip().startswith('def ') and not any(line.strip().startswith('#') for line in [line_content]):
                issues.append({
                    "line": line_num,
                    "severity": "low",
                    "category": "documentation",
                    "message": "Function definition without docstring",
                    "suggestion": "Add a docstring to document the function's purpose"
                })
            
            # Missing type hints
            if line_content.strip().startswith('def ') and '->' not in line_content:
                issues.append({
                    "line": line_num,
                    "severity": "low",
                    "category": "documentation",
                    "message": "Function definition without type hints",
                    "suggestion": "Add type hints for better code documentation"
                })
            
            # Print statements in production code
            if line_content.strip().startswith('print('):
                issues.append({
                    "line": line_num,
                    "severity": "medium",
                    "category": "style",
                    "message": "print() statement detected",
                    "suggestion": "Use proper logging instead of print statements"
                })
            
            # Bare except clauses
            if re.search(r'except\s*:', line_content):
                issues.append({
                    "line": line_num,
                    "severity": "high",
                    "category": "error_handling",
                    "message": "Bare except clause detected",
                    "suggestion": "Specify the exception type to catch"
                })
            
            # Unused imports (basic check)
            if line_content.strip().startswith('import ') or line_content.strip().startswith('from '):
                # This is a basic check - in a real implementation, you'd need more context
                pass
        
        # Markdown/README specific checks
        elif file_ext in ['md', 'markdown']:
            # Missing headers for long content
            if len(line_content) > 80 and not line_content.startswith('#'):
                issues.append({
                    "line": line_num,
                    "severity": "medium",
                    "category": "documentation",
                    "message": "Long line without header structure",
                    "suggestion": "Consider adding headers to organize content"
                })
        
        # JSON/YAML specific checks
        elif file_ext in ['json', 'yaml', 'yml']:
            # Missing comments for configuration
            if len(line_content) > 50 and not line_content.strip().startswith('#'):
                issues.append({
                    "line": line_num,
                    "severity": "medium",
                    "category": "documentation",
                    "message": "Configuration value without comment",
                    "suggestion": "Add comments to explain configuration values"
                })
        
        # If no specific issues found but line has content, suggest a generic improvement
        if not issues and line_content.strip():
            issues.append({
                "line": line_num,
                "severity": "low",
                "category": "other",
                "message": "Consider reviewing this line for potential improvements",
                "suggestion": "Review for code quality, readability, and best practices"
            })
        
        # Code duplication indicators
        if any(dup_indicator in line_content.lower() for dup_indicator in ['copy', 'duplicate', 'same as', 'identical']):
            issues.append({
                'line': line_num,
                'severity': 'low',
                'category': 'code_quality',
                'message': 'Potential code duplication indicator',
                'suggestion': 'Extract common functionality to shared functions or utility classes. Consider using inheritance, composition, or dependency injection to reduce duplication. Use design patterns like template method or strategy.'
            })
        
        # Documentation
        if line_content.strip().startswith('def ') or line_content.strip().startswith('class '):
            if '"""' not in line_content and "'''" not in line_content and '#' not in line_content:
                issues.append({
                    'line': line_num,
                    'severity': 'low',
                    'category': 'documentation',
                    'message': 'Function/class without documentation',
                    'suggestion': 'Add docstrings explaining purpose, parameters, return values, and usage examples. Consider using type hints for better code clarity and automated documentation generation.'
                })
        
        # TODO/FIXME comments
        if 'todo:' in line_content.lower() or 'fixme:' in line_content.lower():
            # Provide contextually appropriate suggestions based on the specific TODO content
            todo_content = line_content.lower()
            
            if 'error' in todo_content or 'exception' in todo_content:
                suggestion = 'Implement comprehensive error handling with proper logging, user feedback, and graceful degradation. Consider using custom exception classes for better error categorization.'
            elif 'test' in todo_content or 'unit test' in todo_content:
                suggestion = 'Write comprehensive unit tests covering edge cases, error conditions, and boundary values. Use mocking for external dependencies and aim for high test coverage.'
            elif 'log' in todo_content or 'logging' in todo_content:
                suggestion = 'Implement structured logging with appropriate log levels, contextual information, and log aggregation. Consider using correlation IDs for request tracing.'
            elif 'validate' in todo_content or 'input' in todo_content:
                suggestion = 'Add input validation with clear error messages, sanitization for security, and proper type checking. Consider using schema validation libraries for complex data structures.'
            elif 'performance' in todo_content or 'optimize' in todo_content:
                suggestion = 'Profile the code to identify bottlenecks, consider caching strategies, and optimize algorithms. Use performance monitoring tools to measure improvements.'
            elif 'refactor' in todo_content or 'clean' in todo_content:
                suggestion = 'Break down complex functions into smaller, focused methods. Extract common patterns into reusable utilities and improve naming conventions.'
            elif 'security' in todo_content or 'vulnerability' in todo_content:
                suggestion = 'Conduct security review for authentication, authorization, input validation, and data exposure. Consider using security scanning tools and following OWASP guidelines.'
            elif 'document' in todo_content or 'comment' in todo_content:
                suggestion = 'Add comprehensive documentation including API specifications, usage examples, and architectural decisions. Consider using automated documentation generation tools.'
            else:
                # Default suggestion for generic TODOs
                suggestion = 'Address this TODO with proper implementation, testing, and documentation. Consider creating a detailed issue ticket to track progress and requirements.'
            
            issues.append({
                'line': line_num,
                'severity': 'medium',
                'category': 'code_quality',
                'message': 'TODO/FIXME comment detected',
                'suggestion': suggestion
            })
        
        return issues
    
    def _group_similar_issues(self, issues: List[Dict]) -> List[Dict]:
        """Group similar issues to avoid repetition in comments."""
        if not issues:
            return []
        
        # Group issues by category and message similarity
        grouped = {}
        
        for issue in issues:
            category = issue.get('category', 'general')
            message = issue.get('message', '')
            severity = issue.get('severity', 'low')
            
            # Create a key for grouping
            group_key = f"{category}_{severity}_{self._normalize_message(message)}"
            
            if group_key not in grouped:
                grouped[group_key] = []
            grouped[group_key].append(issue)
        
        # For each group, keep only the most representative issue
        representative_issues = []
        for group_issues in grouped.values():
            if len(group_issues) == 1:
                representative_issues.append(group_issues[0])
            else:
                # If multiple similar issues, create a consolidated one
                consolidated = self._consolidate_similar_issues(group_issues)
                representative_issues.append(consolidated)
        
        return representative_issues
    
    def _normalize_message(self, message: str) -> str:
        """Normalize message text for similarity comparison."""
        # Remove common variations and normalize text
        normalized = message.lower()
        normalized = normalized.replace('detected', 'found')
        normalized = normalized.replace('without proper', 'missing')
        normalized = normalized.replace('potential ', '')
        normalized = normalized.replace(' could ', ' ')
        normalized = normalized.replace(' would ', ' ')
        
        # Extract key words for comparison
        key_words = [word for word in normalized.split() if len(word) > 3]
        return ' '.join(sorted(set(key_words)))
    
    def _consolidate_similar_issues(self, similar_issues: List[Dict]) -> Dict:
        """Consolidate multiple similar issues into one comprehensive comment."""
        if not similar_issues:
            return {}
        
        # Use the first issue as base
        base_issue = similar_issues[0]
        
        if len(similar_issues) == 1:
            return base_issue
        
        # Count occurrences and create a consolidated message
        count = len(similar_issues)
        lines = [str(issue.get('line', 0)) for issue in similar_issues]
        
        # Update the message to reflect multiple occurrences
        original_message = base_issue.get('message', '')
        if count > 1:
            if 'detected' in original_message.lower():
                new_message = f"{original_message} (found {count} similar instances on lines {', '.join(lines)})"
            else:
                new_message = f"{original_message} (found {count} similar instances on lines {', '.join(lines)})"
        else:
            new_message = original_message
        
        # Create consolidated issue
        consolidated = base_issue.copy()
        consolidated['message'] = new_message
        consolidated['line'] = int(lines[0])  # Use first line number
        consolidated['_consolidated_count'] = count
        
        return consolidated
    
    def _select_diverse_issues(self, grouped_issues: List[Dict], max_per_file: int = 3) -> List[Dict]:
        """Select diverse issues to provide varied feedback."""
        if not grouped_issues:
            return []
        
        # Sort by severity first
        severity_order = ['critical', 'high', 'medium', 'low']
        grouped_issues.sort(key=lambda x: severity_order.index(x.get('severity', 'low')))
        
        # Then sort by category diversity
        selected = []
        categories_seen = set()
        
        # First pass: get one issue from each category
        for issue in grouped_issues:
            if len(selected) >= max_per_file:
                break
            
            category = issue.get('category', 'general')
            if category not in categories_seen:
                selected.append(issue)
                categories_seen.add(category)
        
        # Second pass: fill remaining slots with highest priority issues
        for issue in grouped_issues:
            if len(selected) >= max_per_file:
                break
            
            if issue not in selected:
                selected.append(issue)
        
        return selected[:max_per_file]
    
    def _generate_pr_review_summary(self, analysis_results: List[Dict], pr_data: Dict, total_score: int, total_issues: int) -> str:
        """Generate a comprehensive PR review summary."""
        try:
            # Collect all issues for categorization
            all_issues = []
            for result in analysis_results:
                file_issues = result['analysis'].get('issues', [])
                for issue in file_issues:
                    issue['file'] = result['file']
                    all_issues.append(issue)
            
            # Group issues by category
            categories = {
                'security': [],
                'performance': [],
                'style': [],
                'documentation': [],
                'error_handling': [],
                'other': []
            }
            
            for issue in all_issues:
                category = issue.get('category', 'other')
                if category in categories:
                    categories[category].append(issue)
                else:
                    categories['other'].append(issue)
            
            # Generate summary
            summary = f"""## 🔍 Code Review Summary

**Repository:** {pr_data['repository']}
**Author:** {pr_data['user']['login']}
**PR Title:** {pr_data['title']}

### 📊 Analysis Overview
- **Files Analyzed:** {len(analysis_results)}
- **Total Suggestions:** {total_issues}
- **Critical Suggestions:** {len([i for i in all_issues if i.get('severity') == 'critical'])}
- **High Suggestions:** {len([i for i in all_issues if i.get('severity') == 'high'])}
- **Medium Suggestions:** {len([i for i in all_issues if i.get('severity') == 'medium'])}
- **Low Suggestions:** {len([i for i in all_issues if i.get('severity') == 'low'])}

### 🎯 Detailed Suggestions

"""
            
            # Add suggestions by category
            for category, issues in categories.items():
                if issues:
                    category_name = category.replace('_', ' ').title()
                    summary += f"#### {category_name}\n"
                    
                    # Show top 3 issues per category
                    top_issues = sorted(issues, key=lambda x: {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}.get(x.get('severity', 'low'), 0), reverse=True)[:3]
                    
                    for issue in top_issues:
                        severity_emoji = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'}.get(issue.get('severity', 'low'), '🟢')
                        summary += f"- {severity_emoji} **{issue['file']}:** {issue['message']}\n"
                        if issue.get('suggestion'):
                            summary += f"  💡 **Suggestion:** {issue['suggestion']}\n"
                        summary += "\n"
            
            # Add general recommendations
            if total_issues == 0:
                summary += "### ✅ **Great Work!** No specific issues detected in the changes.\n\n"
            else:
                summary += "### 💡 General Recommendations\n\n"
                
                # PR size recommendations
                changed_files = len(analysis_results)
                if changed_files > 10:
                    summary += "- 📏 **Large PR:** Consider breaking this into smaller, more focused pull requests for easier review.\n"
                elif changed_files > 5:
                    summary += "- 📏 **Medium PR:** Good size for review. Consider adding more detailed commit messages.\n"
                else:
                    summary += "- 📏 **Small PR:** Perfect size for quick review!\n"
                
                # Add specific recommendations based on issues found
                if categories['security']:
                    summary += "- 🔒 **Security:** Please review the security-related suggestions above.\n"
                if categories['performance']:
                    summary += "- ⚡ **Performance:** Consider the performance optimization suggestions.\n"
                if categories['documentation']:
                    summary += "- 📚 **Documentation:** Adding documentation would improve code maintainability.\n"
            
            summary += "\n---\n*This review was generated automatically by the GitHub Code Review Agent.*"
            
            return summary
            
        except Exception as e:
            return f"Error generating review summary: {str(e)}"
    
    def get_user_repositories(self, include_private=True):
        """Get repositories accessible to the authenticated user."""
        try:
            print(f"🔍 Fetching repositories (include_private={include_private})...")
            
            url = f"{self.api_base}/user/repos"
            params = {
                "per_page": 100,
                "sort": "updated",
                "direction": "desc"
            }
            
            if not include_private:
                params["type"] = "public"
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            repositories = response.json()
            
            return {
                "success": True,
                "repositories": repositories,
                "total_count": len(repositories)
            }
            
        except Exception as e:
            error_msg = f"Failed to get user repositories: {e}"
            print(f"❌ {error_msg}")
            return {"success": False, "error": error_msg}
    
    def _extract_file_diff_from_files(self, file_info: Dict) -> str:
        """Extract diff content from file info."""
        try:
            # The file_info should contain the patch content
            patch = file_info.get('patch', '')
            if patch:
                return patch
            
            # If no patch, try to get the diff from the API
            filename = file_info['filename']
            # This would require additional API call to get the diff
            # For now, return empty string if no patch is available
            return ""
            
        except Exception as e:
            print(f"⚠️  Warning: Failed to extract diff for {file_info.get('filename', 'unknown')}: {e}")
            return ""
    
    def review_and_comment_pr(self, owner: str, repo: str, pr_number: int, auto_comment: bool = True, output_file: str = None) -> Dict[str, Any]:
        """Review a pull request and optionally add comments like a senior developer."""
        try:
            print(f"🔍 Starting senior developer PR review for: {owner}/{repo}#{pr_number}")
            
            # Get PR details
            pr_result = self.get_pull_request_details(owner, repo, pr_number)
            if not pr_result["success"]:
                return {"success": False, "error": f"Failed to get PR details: {pr_result['error']}"}
            
            pr_data = pr_result["pull_request"]
            
            # Get PR files
            files_result = self.get_pull_request_files(owner, repo, pr_number)
            if not files_result["success"]:
                return {"success": False, "error": f"Failed to get PR files: {files_result['error']}"}
            
            files = files_result["files"]
            
            print(f"📁 Found {len(files)} changed files")
            
            # Analyze each changed file (all file types, not just Python)
            analysis_results = []
            total_issues = 0
            total_score = 100
            
            for file_info in files:
                filename = file_info['filename']
                print(f"🔍 Analyzing {filename}...")
                
                # Get the diff for this file
                file_diff = self._extract_file_diff_from_files(file_info)
                
                if file_diff:
                    # Analyze the diff content for any file type
                    analysis = self._analyze_diff_content_senior(file_diff, filename)
                    analysis_results.append({
                        'file': filename,
                        'analysis': analysis,
                        'status': file_info['status'],
                        'additions': file_info['additions'],
                        'deletions': file_info['deletions']
                    })
                    
                    # Update totals
                    total_issues += analysis.get('total_issues', 0)
                    total_score = min(total_score, analysis.get('score', 100))
            
            # Generate review summary
            review_summary = self._generate_pr_review_summary(analysis_results, pr_data, total_score, total_issues)
            
            # Create file-specific comments if auto_comment is enabled
            comments_added = 0
            review_url = None
            
            if auto_comment:
                # Get the latest commit SHA for the review
                commits_result = self.get_pull_request_commits(owner, repo, pr_number)
                if not commits_result["success"]:
                    print(f"⚠️  Failed to get PR commits: {commits_result['error']}")
                    return {"success": False, "error": f"Failed to get PR commits: {commits_result['error']}"}
                
                latest_commit_sha = commits_result["commits"][-1]["sha"] if commits_result["commits"] else None
                
                # Collect all comments for the review
                all_comments = []
                review_created = False  # Track if a review has been created
                
                # Create thoughtful senior developer comments
                for analysis_result in analysis_results:
                    file_analysis = analysis_result['analysis']
                    filename = analysis_result['file']
                    
                    print(f"\n🔍 Processing file: {filename}")
                    
                    if file_analysis.get('issues'):
                        print(f"   📋 Found {len(file_analysis['issues'])} raw issues")
                        
                        # Sort issues by importance (critical, high, medium, low)
                        issues = file_analysis['issues']
                        severity_order = ['critical', 'high', 'medium', 'low']
                        issues.sort(key=lambda x: severity_order.index(x.get('severity', 'low')))
                        
                        # Show raw issues for debugging
                        for i, issue in enumerate(issues):
                            print(f"      {i+1}. Line {issue['line']}: {issue['severity']} {issue['category']} - {issue['message']}")
                        
                        # Group similar issues to avoid repetition
                        print(f"   🔍 Grouping similar issues...")
                        grouped_issues = self._group_similar_issues(issues)
                        print(f"   📊 After grouping: {len(grouped_issues)} issues")
                        
                        # Show grouped issues for debugging
                        for i, issue in enumerate(grouped_issues):
                            count = issue.get('_consolidated_count', 1)
                            print(f"      {i+1}. Line {issue['line']}: {issue['severity']} {issue['category']} - {issue['message']} (consolidated: {count})")
                        
                        # Take only the most important and diverse issues (max 3 per file for thoughtful review)
                        print(f"   🎯 Selecting diverse issues...")
                        important_issues = self._select_diverse_issues(grouped_issues, max_per_file=3)
                        print(f"   ✅ Selected {len(important_issues)} diverse issues")
                        
                        for issue in important_issues:
                            line_num = issue.get('line', 0)
                            if line_num <= 0:
                                continue
                            
                            message = issue.get('message', '')
                            suggestion = issue.get('suggestion', '')
                            severity = issue.get('severity', 'low')
                            category = issue.get('category', 'general')
                            
                            print(f"      💬 Creating comment: {severity} {category} - {message}")
                            
                            # Create senior developer-style comment with better context
                            severity_emoji = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'}
                            emoji = severity_emoji.get(severity, '🟢')
                            
                            # Enhanced comment format with better context and guidance
                            if severity == 'critical':
                                comment_body = f"{emoji} **{severity.title()} {category.title()} Issue**\n\n{message}\n\n💡 **Why this matters**: This could create a security vulnerability or cause system failures.\n\n🔧 **Suggestion**: {suggestion}\n\n⚠️ **Priority**: Address this before merging to production."
                            elif severity == 'high':
                                comment_body = f"{emoji} **{severity.title()} {category.title()} Issue**\n\n{message}\n\n💡 **Why this matters**: This could cause runtime errors or performance issues in production.\n\n🔧 **Suggestion**: {suggestion}\n\n📋 **Next steps**: Consider adding this to your technical debt backlog if not critical for this release."
                            elif severity == 'medium':
                                comment_body = f"{emoji} **{severity.title()} {category.title()} Issue**\n\n{message}\n\n💡 **Why this matters**: This affects code maintainability and could lead to technical debt.\n\n🔧 **Suggestion**: {suggestion}\n\n💭 **Consideration**: This is a good improvement for code quality but not blocking for merge."
                            else:
                                comment_body = f"{emoji} **{severity.title()} {category.title()} Issue**\n\n{message}\n\n💡 **Why this matters**: This improves code quality and developer experience.\n\n🔧 **Suggestion**: {suggestion}\n\n✨ **Bonus**: This is a nice-to-have improvement that shows attention to detail."
                            
                            # Add to comments list for the review
                            # GitHub API requires position to be a positive integer
                            if line_num > 0:
                                # For review comments, we need to use 'position' field
                                # Position refers to the line number in the diff, not the file
                                all_comments.append({
                                    "path": filename,
                                    "position": line_num,  # Use position for review comments (Files changed tab)
                                    "body": comment_body
                                })
                                print(f"      ✅ Added comment for {filename} at position {line_num}")
                            else:
                                print(f"      ⚠️  Skipping comment for {filename} - invalid position: {line_num}")
                    else:
                        print(f"   ✅ No issues found in {filename}")
            
                # Create a review with all comments
                if all_comments:
                    print(f"🔍 Creating review with {len(all_comments)} comments...")
                    print(f"📝 Sample comment data: {all_comments[0] if all_comments else 'None'}")
                    
                    review_result = self.create_pull_request_review(
                        owner, repo, pr_number, "COMMENT", review_summary, all_comments, latest_commit_sha
                    )
                    
                    if review_result["success"]:
                        comments_added = len(all_comments)
                        review_url = review_result["review"]["html_url"]
                        print(f"✅ Senior developer review with {comments_added} thoughtful comments added successfully!")
                        print(f"🔗 Review URL: {review_url}")
                        # Primary method succeeded, no need for fallback
                        fallback_needed = False
                        review_created = True
                    else:
                        print(f"⚠️  Failed to add review with comments: {review_result['error']}")
                        print("🔄 Primary method failed, attempting fallback with individual comments...")
                        fallback_needed = True
                        
                        # Fallback: create individual comments using review API
                        # Only run this if the primary method failed
                        comments_added = 0
                        for comment_data in all_comments:
                            # Create a review with just this one comment
                            single_comment_review = self.create_pull_request_review(
                                owner, repo, pr_number, 
                                "COMMENT", 
                                f"Comment on {comment_data['path']}", 
                                [comment_data], 
                                latest_commit_sha
                            )
                            
                            if single_comment_review["success"]:
                                comments_added += 1
                                print(f"✅ Created review comment on {comment_data['path']} at position {comment_data['position']}")
                            else:
                                print(f"❌ Failed to create review comment on {comment_data['path']}: {single_comment_review['error']}")
                        
                        if comments_added > 0:
                            print(f"✅ Created {comments_added} review comments as fallback")
                            review_created = True
                        else:
                            print("❌ Failed to create review comments as fallback")
                else:
                    # If no issues found, just add the summary
                    review_result = self.create_pull_request_review(
                        owner, repo, pr_number, "COMMENT", review_summary, None, latest_commit_sha
                    )
                    
                    if review_result["success"]:
                        review_url = review_result["review"]["html_url"]
                        print(f"✅ Review summary added successfully!")
                        print(f"🔗 Review URL: {review_url}")
                        review_created = True
                    else:
                        print(f"⚠️  Failed to add review summary: {review_result['error']}")
                
                # Only mark files as viewed if we haven't already created a review with comments
                # This prevents duplicate reviews
                if not review_created:
                    print("👁️  No review created yet, marking files as viewed with separate review...")
                    self._mark_files_as_viewed(owner, repo, pr_number, files, latest_commit_sha)
                else:
                    print("👁️  Review already created, skipping separate 'mark as viewed' review to prevent duplicates...")
            
            # Save report if output file is specified
            if output_file:
                report_data = {
                    "pr_number": pr_number,
                    "repository": f"{owner}/{repo}",
                    "title": pr_data["title"],
                    "author": pr_data["user"]["login"],
                    "created_at": pr_data["created_at"],
                    "updated_at": pr_data["updated_at"],
                    "analysis_results": analysis_results,
                    "review_summary": review_summary,
                    "total_issues": total_issues,
                    "total_score": total_score,
                    "comments_added": comments_added,
                    "review_url": review_url
                }
                
                # Save to Downloads folder
                downloads_path = os.path.expanduser("~/Downloads")
                output_path = os.path.join(downloads_path, output_file)
                
                with open(output_path, 'w') as f:
                    json.dump(report_data, f, indent=2)
                
                print(f"📄 Report saved to: {output_path}")
            
            return {
                "success": True,
                "pr_number": pr_number,
                "repository": f"{owner}/{repo}",
                "analysis_results": analysis_results,
                "review_summary": review_summary,
                "total_issues": total_issues,
                "total_score": total_score,
                "comments_added": comments_added,
                "review_url": review_url,
                "output_file": output_file
            }
            
        except Exception as e:
            error_msg = f"PR review and comment failed: {str(e)}"
            print(f"❌ {error_msg}")
            return {"success": False, "error": error_msg}
    
    def _mark_files_as_viewed(self, owner: str, repo: str, pr_number: int, files: List[Dict], commit_sha: str):
        """Mark files as viewed by creating a review without comments."""
        try:
            print("👁️  Marking files as viewed...")
            
            # Create a review with no comments to mark files as viewed
            # Use a different event type to avoid confusion with comment reviews
            review_result = self.create_pull_request_review(
                owner, repo, pr_number, "COMMENT", "Files reviewed (no issues found)", [], commit_sha
            )
            
            if review_result["success"]:
                print("✅ Files marked as viewed")
            else:
                print(f"⚠️  Failed to mark files as viewed: {review_result['error']}")
                
        except Exception as e:
            print(f"⚠️  Failed to mark files as viewed: {e}")
    
    def _analyze_diff_content_senior(self, diff_content: str, filename: str) -> Dict[str, Any]:
        """Analyze diff content like a senior developer would."""
        
        try:
            if not diff_content.strip():
                return {
                    "success": True,
                    "score": 100,
                    "total_issues": 0,
                    "issues": []
                }
            
            # Parse the diff content to get actual line numbers
            lines = diff_content.split('\n')
            issues = []
            total_score = 100
            current_line_number = 0
            
            print(f"🔍 Analyzing diff for {filename} with {len(lines)} lines")
            
            for line in lines:
                # Parse diff header to get line numbers
                if line.startswith('@@'):
                    # Extract line numbers from diff header
                    # Format: @@ -old_start,old_count +new_start,new_count @@
                    match = re.search(r'@@ -(\d+),?\d* \+(\d+),?\d* @@', line)
                    if match:
                        current_line_number = int(match.group(2)) - 1  # Start at new line number
                        print(f"📍 Diff header: new lines start at {current_line_number + 1}")
                elif line.startswith('+') and not line.startswith('+++'):
                    current_line_number += 1
                    # Remove the + prefix and analyze the actual content
                    content = line[1:]
                    
                    print(f"📝 Line {current_line_number}: {content[:50]}...")
                    
                    # Analyze this line for issues like a senior developer would
                    line_issues = self._analyze_line_for_issues_senior(content, current_line_number, filename)
                    if line_issues:
                        print(f"⚠️  Found {len(line_issues)} issues on line {current_line_number}")
                        issues.extend(line_issues)
                    
                    # Calculate score deduction based on issues
                    for issue in line_issues:
                        severity = issue.get('severity', 'low')
                        if severity == 'critical':
                            total_score -= 10
                        elif severity == 'high':
                            total_score -= 5
                        elif severity == 'medium':
                            total_score -= 2
                        elif severity == 'low':
                            total_score -= 1
                elif line.startswith(' ') or line.startswith('-'):
                    # Context line or removed line, increment line number for context
                    if not line.startswith('-'):
                        current_line_number += 1
            
            print(f"📊 Analysis complete: {len(issues)} issues found, score: {total_score}")
            
            # Ensure score doesn't go below 0
            total_score = max(0, total_score)
            
            return {
                "success": True,
                "score": total_score,
                "total_issues": len(issues),
                "issues": issues
            }
            
        except Exception as e:
            print(f"❌ Error analyzing diff: {e}")
            return {
                "success": False,
                "error": f"Failed to analyze diff content: {str(e)}",
                "score": 0,
                "total_issues": 0,
                "issues": []
            }
    
    def _analyze_line_for_issues_senior(self, line_content: str, line_num: int, filename: str) -> List[Dict]:
        """Analyze a single line for senior developer-level issues with varied, useful suggestions."""
        issues = []
        
        # Security issues
        if any(secret in line_content.lower() for secret in ['password', 'secret', 'key', 'token', 'credential']):
            if 'private_key' in line_content.lower() or '-----begin' in line_content.lower():
                # Vary the suggestion based on context
                if 'rsa' in line_content.lower() or 'ecdsa' in line_content.lower():
                    issues.append({
                        'line': line_num,
                        'severity': 'critical',
                        'category': 'security',
                        'message': 'Cryptographic private key material exposed in code',
                        'suggestion': 'Store cryptographic keys in hardware security modules (HSMs) or cloud KMS services. Implement proper key lifecycle management including rotation, backup, and secure disposal procedures.'
                    })
                else:
                    issues.append({
                        'line': line_num,
                        'severity': 'critical',
                        'category': 'security',
                        'message': 'Private key material exposed in code',
                        'suggestion': 'Store private keys in environment variables, AWS Secrets Manager, or HashiCorp Vault. Never commit cryptographic material to version control. Consider using key rotation policies.'
                    })
            elif any(env_var in line_content.lower() for env_var in ['process.env', 'dotenv', 'config']):
                issues.append({
                    'line': line_num,
                    'severity': 'critical',
                    'category': 'security',
                    'message': 'Sensitive configuration exposed in code',
                    'suggestion': 'Use environment variables with proper validation and encryption. Consider using a secrets management service like AWS Parameter Store or Azure Key Vault for production deployments.'
                })
            elif 'api_key' in line_content.lower() or 'sk-' in line_content.lower():
                if 'openai' in line_content.lower() or 'anthropic' in line_content.lower():
                    issues.append({
                        'line': line_num,
                        'severity': 'critical',
                        'category': 'security',
                        'message': 'AI service API key exposed in code',
                        'suggestion': 'Store AI service keys in environment variables with proper rate limiting. Consider using API key rotation and monitoring for unusual usage patterns. Implement proper access controls for AI service consumption.'
                    })
                else:
                    issues.append({
                        'line': line_num,
                        'severity': 'critical',
                        'category': 'security',
                        'message': 'API keys or secrets exposed in code',
                        'suggestion': 'Store API keys in secure environment variables or use OAuth2 flows. Implement proper key rotation and monitor for unauthorized usage. Consider using service accounts with minimal permissions.'
                    })
            elif 'token' in line_content.lower() or 'ghp_' in line_content.lower():
                if 'github' in line_content.lower() or 'ghp_' in line_content.lower():
                    issues.append({
                        'line': line_num,
                        'severity': 'critical',
                        'category': 'security',
                        'message': 'GitHub personal access token hardcoded in source',
                        'suggestion': 'Use GitHub Actions secrets, environment variables, or OAuth apps instead of PATs. Implement proper token scoping with minimal required permissions and enable token expiration.'
                    })
                else:
                    issues.append({
                        'line': line_num,
                        'severity': 'critical',
                        'category': 'security',
                        'message': 'Authentication tokens hardcoded in source',
                        'suggestion': 'Use environment variables for tokens and implement proper token lifecycle management. Consider using short-lived tokens with automatic renewal and proper scoping.'
                    })
            elif 'password' in line_content.lower():
                if 'admin' in line_content.lower() or 'root' in line_content.lower():
                    issues.append({
                        'line': line_num,
                        'severity': 'critical',
                        'category': 'security',
                        'message': 'Admin/root password hardcoded in source',
                        'suggestion': 'Use secure password hashing (bcrypt, Argon2) and implement multi-factor authentication. Consider using certificate-based authentication or OAuth2 for administrative access.'
                    })
                else:
                    issues.append({
                        'line': line_num,
                        'severity': 'critical',
                        'category': 'security',
                        'message': 'Hardcoded password detected',
                        'suggestion': 'Use secure password hashing (bcrypt, Argon2) and store hashes in secure databases. Implement password policies, complexity requirements, and secure reset mechanisms.'
                    })
            elif 'secret' in line_content.lower():
                issues.append({
                    'line': line_num,
                    'severity': 'critical',
                    'category': 'security',
                    'message': 'Hardcoded secret detected',
                    'suggestion': 'Use environment variables or secrets management services. Implement proper access controls, audit logging, and consider using hardware security modules (HSMs) for critical secrets.'
                })
            else:
                issues.append({
                    'line': line_num,
                    'severity': 'critical',
                    'category': 'security',
                    'message': 'Hardcoded sensitive information detected',
                    'suggestion': 'Extract to environment variables or secure configuration files. Use tools like python-dotenv for local development and encrypted configs for production. Implement proper access controls.'
                })
        
        # Additional security checks
        if 'sql' in line_content.lower() and any(sql_keyword in line_content.lower() for sql_keyword in ['select', 'insert', 'update', 'delete']):
            if not any(safe_pattern in line_content.lower() for safe_pattern in ['prepared', 'stmt', 'parameter', '?', '%s', 'execute']):
                issues.append({
                    'line': line_num,
                    'severity': 'critical',
                    'category': 'security',
                    'message': 'Potential SQL injection vulnerability',
                    'suggestion': 'Use parameterized queries or ORM methods. Never concatenate user input directly into SQL strings. Consider using SQLAlchemy, Prisma, or similar ORMs with built-in protection.'
                })
        
        if any(xss_pattern in line_content.lower() for xss_pattern in ['innerhtml', 'document.write', 'eval(', 'settimeout(0']):
            issues.append({
                'line': line_num,
                'severity': 'critical',
                'category': 'security',
                'message': 'XSS vulnerability risk detected',
                'suggestion': 'Use textContent for plain text or createElement/appendChild for safe DOM manipulation. Implement proper input sanitization and consider using Content Security Policy (CSP) headers.'
            })
        
        if 'http://' in line_content.lower() and not any(safe_context in line_content.lower() for safe_context in ['localhost', '127.0.0.1', 'example.com', 'test']):
            issues.append({
                'line': line_num,
                'severity': 'high',
                'category': 'security',
                'message': 'Insecure HTTP protocol detected',
                'suggestion': 'Use HTTPS for all external communications. Implement proper SSL/TLS configuration, certificate validation, and consider using HTTP Strict Transport Security (HSTS) headers.'
            })
        
        # Advanced security patterns
        if any(crypto_pattern in line_content.lower() for crypto_pattern in ['md5(', 'sha1(', 'crc32(']):
            if 'md5(' in line_content.lower():
                issues.append({
                    'line': line_num,
                    'severity': 'high',
                    'category': 'security',
                    'message': 'MD5 hash function usage detected',
                    'suggestion': 'MD5 is cryptographically broken. Use SHA-256, SHA-3, or Argon2 for hashing. For password hashing, use bcrypt, Argon2, or PBKDF2 with appropriate salt rounds.'
                })
            elif 'sha1(' in line_content.lower():
                issues.append({
                    'line': line_num,
                    'severity': 'high',
                    'category': 'security',
                    'message': 'SHA-1 hash function usage detected',
                    'suggestion': 'SHA-1 is cryptographically weak. Use SHA-256, SHA-3, or Blake2 for hashing. For password hashing, use bcrypt, Argon2, or PBKDF2 with appropriate salt rounds.'
                })
            else:
                issues.append({
                    'line': line_num,
                    'severity': 'medium',
                    'category': 'security',
                    'message': 'Weak cryptographic hash function detected',
                    'suggestion': 'Use modern cryptographic hash functions like SHA-256, SHA-3, or Blake2. For password hashing, use bcrypt, Argon2, or PBKDF2 with appropriate salt rounds.'
                })
        
        # Authentication bypass patterns
        if any(auth_bypass in line_content.lower() for auth_bypass in ['admin = true', 'role = "admin"', 'is_admin = 1', 'bypass_auth', 'skip_auth', 'auth = false']):
            if 'admin' in line_content.lower() or 'role' in line_content.lower():
                issues.append({
                    'line': line_num,
                    'severity': 'critical',
                    'category': 'security',
                    'message': 'Hardcoded admin access detected',
                    'suggestion': 'Implement proper role-based access control (RBAC). Use JWT tokens, OAuth, or session-based authentication with proper authorization checks. Consider using policy-based authorization.'
                })
            elif 'bypass' in line_content.lower() or 'skip' in line_content.lower():
                issues.append({
                    'line': line_num,
                    'severity': 'critical',
                    'category': 'security',
                    'message': 'Authentication bypass mechanism detected',
                    'suggestion': 'Remove all authentication bypass mechanisms. Implement proper authentication flows with secure session management. Use multi-factor authentication for sensitive operations.'
                })
            else:
                issues.append({
                    'line': line_num,
                    'severity': 'critical',
                    'category': 'security',
                    'message': 'Hardcoded authentication override detected',
                    'suggestion': 'Implement proper authentication and authorization systems. Use secure token-based authentication with proper expiration and refresh mechanisms.'
                })
        
        # Session management issues
        if any(session_pattern in line_content.lower() for session_pattern in ['session_timeout = 0', 'session_lifetime = -1', 'remember_me = true']):
            if 'timeout' in line_content.lower() or 'lifetime' in line_content.lower():
                issues.append({
                    'line': line_num,
                    'severity': 'high',
                    'category': 'security',
                    'message': 'Infinite or excessive session lifetime detected',
                    'suggestion': 'Set reasonable session timeouts (15-30 minutes for web apps, 8 hours max for mobile). Implement session refresh mechanisms and automatic logout for inactive sessions.'
                })
            elif 'remember_me' in line_content.lower():
                issues.append({
                    'line': line_num,
                    'severity': 'medium',
                    'category': 'security',
                    'message': 'Remember me functionality without proper security',
                    'suggestion': 'Implement secure remember me tokens with limited scope and expiration. Use secure, random tokens and consider implementing device fingerprinting.'
                })
        
        # File upload security
        if any(upload_pattern in line_content.lower() for upload_pattern in ['file.upload', 'multipart/form-data', 'enctype="multipart"']):
            if 'validation' not in line_content.lower() and 'type' not in line_content.lower():
                issues.append({
                    'line': line_num,
                    'severity': 'high',
                    'category': 'security',
                    'message': 'File upload without proper validation',
                    'suggestion': 'Implement file type validation, size limits, and content scanning. Use allowlists for file extensions and consider implementing virus scanning for uploaded files.'
                })
        
        # Command injection patterns
        if any(cmd_pattern in line_content.lower() for cmd_pattern in ['os.system', 'subprocess.call', 'subprocess.run', 'subprocess.popen']):
            if any(user_input in line_content.lower() for user_input in ['input(', 'request.', 'argv', 'args']):
                issues.append({
                    'line': line_num,
                    'severity': 'critical',
                    'category': 'security',
                    'message': 'Command injection vulnerability detected',
                    'suggestion': 'Avoid shell commands when possible. Use subprocess.run with shell=False and validate all inputs. Consider using higher-level APIs or libraries instead of shell commands.'
                })
            else:
                issues.append({
                    'line': line_num,
                    'severity': 'medium',
                    'category': 'security',
                    'message': 'Shell command execution detected',
                    'suggestion': 'Use subprocess.run with shell=False for better security. Validate all command arguments and consider using higher-level APIs when possible.'
                })
        
        # Deserialization security
        if any(deserial_pattern in line_content.lower() for deserial_pattern in ['pickle.loads', 'yaml.load(', 'marshal.loads']):
            if 'pickle.loads' in line_content.lower():
                issues.append({
                    'line': line_num,
                    'severity': 'critical',
                    'category': 'security',
                    'message': 'Unsafe pickle deserialization detected',
                    'suggestion': 'Pickle is inherently unsafe. Use JSON, MessagePack, or Protocol Buffers for data serialization. If pickle is required, implement strict allowlists for allowed classes.'
                })
            elif 'yaml.load(' in line_content.lower():
                issues.append({
                    'line': line_num,
                    'severity': 'high',
                    'category': 'security',
                    'message': 'Unsafe YAML deserialization detected',
                    'suggestion': 'Use yaml.safe_load() instead of yaml.load(). Implement proper input validation and consider using schema validation for YAML documents.'
                })
            else:
                issues.append({
                    'line': line_num,
                    'severity': 'high',
                    'category': 'security',
                    'message': 'Unsafe deserialization detected',
                    'suggestion': 'Use safe deserialization methods with proper input validation. Implement allowlists for allowed types and consider using schema validation.'
                })
        
        # SQL injection prevention
        if any(sql_pattern in line_content.lower() for sql_pattern in ['execute(', 'executescript(', 'executemany(']):
            if any(safe_pattern in line_content.lower() for safe_pattern in ['prepared', 'stmt', 'parameter', '?', '%s']):
                pass  # Safe parameterized query
            else:
                issues.append({
                    'line': line_num,
                    'severity': 'critical',
                    'category': 'security',
                    'message': 'Potential SQL injection vulnerability',
                    'suggestion': 'Use parameterized queries or ORM methods. Never concatenate user input directly into SQL strings. Consider using SQLAlchemy or similar ORMs.'
                })
        
        # Authentication bypass
        if any(auth_bypass in line_content.lower() for auth_bypass in ['admin = true', 'role = "admin"', 'is_admin = 1', 'bypass_auth']):
            issues.append({
                'line': line_num,
                'severity': 'critical',
                'category': 'security',
                'message': 'Hardcoded admin access detected',
                'suggestion': 'Implement proper role-based access control (RBAC). Use JWT tokens, OAuth, or session-based authentication with proper authorization checks.'
            })
        
        # Error handling
        if 'open(' in line_content and ')' in line_content:
            if 'with open(' in line_content:
                pass  # Context manager handles cleanup
            else:
                # Vary suggestions based on file operation type
                if 'w' in line_content.lower() and '+' in line_content.lower():
                    issues.append({
                        'line': line_num,
                        'severity': 'high',
                        'category': 'error_handling',
                        'message': 'File read-write operation without proper error handling',
                        'suggestion': 'Use context managers (with open()) and implement proper file locking for concurrent access. Handle potential corruption scenarios and implement atomic write operations with backup strategies.'
                    })
                elif 'a' in line_content.lower():
                    issues.append({
                        'line': line_num,
                        'severity': 'high',
                        'category': 'error_handling',
                        'message': 'File append operation without proper error handling',
                        'suggestion': 'Use context managers (with open()) and implement proper error handling for append operations. Consider using file rotation and backup strategies for log files.'
                    })
                else:
                    issues.append({
                        'line': line_num,
                        'severity': 'high',
                        'category': 'error_handling',
                        'message': 'File operation without proper error handling',
                        'suggestion': 'Use context managers (with open()) or try-finally blocks. Handle FileNotFoundError, PermissionError, and other I/O exceptions appropriately. Consider using pathlib for modern path operations.'
                    })
        
        if any(read_op in line_content.lower() for read_op in ['.read()', '.readline()', '.readlines()']):
            if 'try:' in line_content or 'with ' in line_content:
                pass  # Has error handling
            else:
                # Vary suggestions based on read operation
                if '.readlines()' in line_content.lower():
                    issues.append({
                        'line': line_num,
                        'severity': 'high',
                        'category': 'error_handling',
                        'message': 'File readlines operation missing error handling',
                        'suggestion': 'Wrap readlines operations in try-catch blocks. Handle memory issues for large files, encoding errors, and consider using generators for memory-efficient line processing.'
                    })
                elif '.readline()' in line_content.lower():
                    issues.append({
                        'line': line_num,
                        'severity': 'high',
                        'category': 'error_handling',
                        'message': 'File readline operation missing error handling',
                        'suggestion': 'Implement proper error handling for readline operations. Handle end-of-file conditions, encoding issues, and consider using iterators for more robust line processing.'
                    })
                else:
                    issues.append({
                        'line': line_num,
                        'severity': 'high',
                        'category': 'error_handling',
                        'message': 'File read operation missing error handling',
                        'suggestion': 'Wrap file operations in try-catch blocks. Handle potential encoding issues, file corruption, and I/O errors gracefully. Consider using pathlib.read_text() with encoding specification.'
                    })
        
        if any(write_op in line_content.lower() for write_op in ['.write(', '.writelines(', '.flush(']):
            if 'try:' in line_content or 'with ' in line_content:
                pass  # Has error handling
            else:
                # Vary suggestions based on write operation
                if '.writelines(' in line_content.lower():
                    issues.append({
                        'line': line_num,
                        'severity': 'high',
                        'category': 'error_handling',
                        'message': 'File writelines operation without error handling',
                        'suggestion': 'Handle potential encoding issues and implement proper error handling for batch write operations. Consider using atomic writes and implementing rollback mechanisms for failed batch operations.'
                    })
                elif '.flush(' in line_content.lower():
                    issues.append({
                        'line': line_num,
                        'severity': 'high',
                        'category': 'error_handling',
                        'message': 'File flush operation without error handling',
                        'suggestion': 'Handle flush failures and implement proper error handling for buffer operations. Consider the impact of flush failures on data integrity and implement appropriate recovery mechanisms.'
                    })
                else:
                    issues.append({
                        'line': line_num,
                        'severity': 'high',
                        'category': 'error_handling',
                        'message': 'File write operation without error handling',
                        'suggestion': 'Handle disk space issues, permission errors, and write failures. Use atomic write operations when possible to prevent data corruption. Consider using tempfile for safe temporary file creation.'
                    })
        
        # Network operations
        if any(net_op in line_content.lower() for net_op in ['requests.get(', 'requests.post(', 'urllib.request', 'http.client']):
            if 'try:' in line_content or 'timeout=' in line_content:
                pass  # Has error handling or timeout
            else:
                if 'get(' in line_content.lower():
                    if 'json' in line_content.lower():
                        issues.append({
                            'line': line_num,
                            'severity': 'high',
                            'category': 'error_handling',
                            'message': 'JSON API GET request missing error handling',
                            'suggestion': 'Add timeout parameters, handle JSON parsing errors, HTTP status codes, and network timeouts. Implement proper error handling for malformed JSON responses and consider using retry mechanisms with exponential backoff.'
                        })
                    else:
                        issues.append({
                            'line': line_num,
                            'severity': 'high',
                            'category': 'error_handling',
                            'message': 'HTTP GET request missing error handling',
                            'suggestion': 'Add timeout parameters, handle connection errors, HTTP status codes, and network timeouts. Consider using retry mechanisms with exponential backoff and circuit breaker patterns.'
                        })
                elif 'post(' in line_content.lower():
                    if 'json' in line_content.lower():
                        issues.append({
                            'line': line_num,
                            'severity': 'high',
                            'category': 'error_handling',
                            'message': 'JSON API POST request missing error handling',
                            'suggestion': 'Implement proper error handling for JSON serialization failures, network errors, and server responses. Add request/response logging and consider implementing idempotency for critical operations.'
                        })
                    else:
                        issues.append({
                            'line': line_num,
                            'severity': 'high',
                            'category': 'error_handling',
                            'message': 'HTTP POST request missing error handling',
                            'suggestion': 'Implement proper error handling for network failures, validation errors, and server responses. Add request/response logging and consider implementing idempotency for critical operations.'
                        })
                elif 'put(' in line_content.lower() or 'patch(' in line_content.lower():
                    issues.append({
                        'line': line_num,
                        'severity': 'high',
                        'category': 'error_handling',
                        'message': 'HTTP PUT/PATCH request missing error handling',
                        'suggestion': 'Handle optimistic locking conflicts, validation errors, and partial update failures. Implement proper error responses and consider using ETags for concurrency control.'
                    })
                elif 'delete(' in line_content.lower():
                    issues.append({
                        'line': line_num,
                        'severity': 'high',
                        'category': 'error_handling',
                        'message': 'HTTP DELETE request missing error handling',
                        'suggestion': 'Handle cascading delete failures, permission errors, and resource not found scenarios. Implement soft delete patterns and proper cleanup procedures.'
                    })
                else:
                    issues.append({
                        'line': line_num,
                        'severity': 'high',
                        'category': 'error_handling',
                        'message': 'HTTP request missing error handling',
                        'suggestion': 'Add comprehensive error handling including timeouts, retries, and proper HTTP status code checking. Consider using HTTP client libraries with built-in error handling and connection pooling.'
                    })
        
        # Database operations
        if any(db_op in line_content.lower() for db_op in ['execute(', 'query(', 'cursor.execute', 'db.execute']):
            if 'try:' in line_content or 'except' in line_content:
                pass  # Has error handling
            else:
                # Vary suggestions based on database operation type
                if 'select' in line_content.lower():
                    issues.append({
                        'line': line_num,
                        'severity': 'high',
                        'category': 'error_handling',
                        'message': 'Database SELECT operation missing error handling',
                        'suggestion': 'Handle database connection errors, query syntax errors, and result set processing failures. Implement proper connection pooling and consider using query timeouts for long-running operations.'
                    })
                elif 'insert' in line_content.lower() or 'update' in line_content.lower():
                    issues.append({
                        'line': line_num,
                        'severity': 'high',
                        'category': 'error_handling',
                        'message': 'Database INSERT/UPDATE operation missing error handling',
                        'suggestion': 'Handle constraint violations, duplicate key errors, and transaction failures. Implement proper rollback mechanisms and consider using database connection pooling with retry logic.'
                    })
                elif 'delete' in line_content.lower():
                    issues.append({
                        'line': line_num,
                        'severity': 'high',
                        'category': 'error_handling',
                        'message': 'Database DELETE operation missing error handling',
                        'suggestion': 'Handle foreign key constraint violations, permission errors, and cascade delete failures. Implement proper rollback mechanisms and consider using soft delete patterns.'
                    })
                else:
                    issues.append({
                        'line': line_num,
                        'severity': 'high',
                        'category': 'error_handling',
                        'message': 'Database operation missing error handling',
                        'suggestion': 'Handle database connection errors, constraint violations, and transaction failures. Implement proper rollback mechanisms and consider using database connection pooling.'
                    })
        
        # JSON parsing
        if 'json.loads(' in line_content.lower() or 'json.load(' in line_content.lower():
            if 'try:' in line_content or 'except' in line_content:
                pass  # Has error handling
            else:
                # Vary suggestions based on JSON operation
                if 'json.loads(' in line_content.lower():
                    issues.append({
                        'line': line_num,
                        'severity': 'medium',
                        'category': 'error_handling',
                        'message': 'JSON string parsing without error handling',
                        'suggestion': 'Handle malformed JSON strings, encoding issues, and parsing errors. Validate JSON structure before processing and provide meaningful error messages for debugging. Consider using JSON schema validation.'
                    })
                else:
                    issues.append({
                        'line': line_num,
                        'severity': 'medium',
                        'category': 'error_handling',
                        'message': 'JSON file parsing without error handling',
                        'suggestion': 'Handle file I/O errors, malformed JSON content, and encoding issues. Validate JSON structure before processing and provide meaningful error messages for debugging.'
                    })
        
        # Advanced error handling patterns
        if any(parse_pattern in line_content.lower() for parse_pattern in ['xml.parse', 'yaml.load', 'toml.load', 'ini.read']):
            if 'try:' in line_content or 'except' in line_content:
                pass  # Has error handling
            else:
                if 'xml.parse' in line_content.lower():
                    issues.append({
                        'line': line_num,
                        'severity': 'medium',
                        'category': 'error_handling',
                        'message': 'XML parsing without error handling',
                        'suggestion': 'Handle malformed XML, DTD validation errors, and entity expansion attacks. Use defusedxml for safe XML parsing and implement proper error handling for parsing failures.'
                    })
                elif 'yaml.load' in line_content.lower():
                    issues.append({
                        'line': line_num,
                        'severity': 'medium',
                        'category': 'error_handling',
                        'message': 'YAML parsing without error handling',
                        'suggestion': 'Handle malformed YAML, anchor/alias issues, and parsing errors. Use yaml.safe_load() and implement proper error handling for parsing failures with user-friendly error messages.'
                    })
                elif 'toml.load' in line_content.lower():
                    issues.append({
                        'line': line_num,
                        'severity': 'medium',
                        'category': 'error_handling',
                        'message': 'TOML parsing without error handling',
                        'suggestion': 'Handle malformed TOML, parsing errors, and validation failures. Implement proper error handling for configuration parsing with fallback to default values.'
                    })
                else:
                    issues.append({
                        'line': line_num,
                        'severity': 'medium',
                        'category': 'error_handling',
                        'message': 'Configuration parsing without error handling',
                        'suggestion': 'Handle parsing errors, validation failures, and malformed configuration. Implement proper error handling with fallback to default values and user-friendly error messages.'
                    })
        
        # Network timeout and retry patterns
        if any(timeout_pattern in line_content.lower() for timeout_pattern in ['timeout=', 'retry=', 'max_retries']):
            if 'timeout=' in line_content.lower():
                if 'timeout=0' in line_content.lower() or 'timeout=None' in line_content.lower():
                    issues.append({
                        'line': line_num,
                        'severity': 'high',
                        'category': 'error_handling',
                        'message': 'Infinite timeout detected in network operation',
                        'suggestion': 'Set reasonable timeouts (30s for web requests, 60s for file uploads). Implement exponential backoff retry strategies and circuit breaker patterns for network resilience.'
                    })
                else:
                    issues.append({
                        'line': line_num,
                        'severity': 'medium',
                        'category': 'error_handling',
                        'message': 'Network timeout configuration detected',
                        'suggestion': 'Ensure timeouts are appropriate for the operation. Consider implementing retry mechanisms with exponential backoff and circuit breaker patterns for network resilience.'
                    })
            elif 'retry=' in line_content.lower():
                if 'retry=0' in line_content.lower() or 'retry=False' in line_content.lower():
                    issues.append({
                        'line': line_num,
                        'severity': 'medium',
                        'category': 'error_handling',
                        'message': 'Retry mechanism disabled for network operation',
                        'suggestion': 'Enable retry mechanisms with exponential backoff for transient failures. Implement circuit breaker patterns and consider using libraries like tenacity for robust retry logic.'
                    })
        
        # Exception handling patterns
        if 'except Exception:' in line_content or 'except:' in line_content:
            if 'except Exception:' in line_content:
                issues.append({
                    'line': line_num,
                    'severity': 'medium',
                    'category': 'error_handling',
                    'message': 'Generic exception handling detected',
                    'suggestion': 'Catch specific exception types instead of generic Exception. Implement proper error logging, user-friendly error messages, and consider using custom exception hierarchies.'
                })
            else:
                issues.append({
                    'line': line_num,
                    'severity': 'high',
                    'category': 'error_handling',
                    'message': 'Bare except clause detected',
                    'suggestion': 'Specify the exception type to catch. Implement proper error logging, user-friendly error messages, and consider using custom exception hierarchies for better error handling.'
                })
        
        # Logging and monitoring patterns
        if any(log_pattern in line_content.lower() for log_pattern in ['print(', 'console.log', 'echo', 'printf']):
            if 'print(' in line_content.lower():
                issues.append({
                    'line': line_num,
                    'severity': 'medium',
                    'category': 'style',
                    'message': 'print() statement detected in production code',
                    'suggestion': 'Replace with proper logging (logging module in Python, winston in Node.js). Implement structured logging with appropriate log levels and consider using correlation IDs for request tracing.'
                })
            elif 'console.log' in line_content.lower():
                issues.append({
                    'line': line_num,
                    'severity': 'medium',
                    'category': 'style',
                    'message': 'console.log detected in production code',
                    'suggestion': 'Replace with proper logging library (winston, pino). Implement structured logging with appropriate log levels and consider using correlation IDs for request tracing.'
                })
            else:
                issues.append({
                    'line': line_num,
                    'severity': 'medium',
                    'category': 'style',
                    'message': 'Debug output statement detected',
                    'suggestion': 'Replace with proper logging mechanisms. Implement structured logging with appropriate log levels and consider using correlation IDs for request tracing.'
                })
        
        # Performance issues
        if 'setinterval(' in line_content.lower() or 'settimeout(' in line_content.lower():
            if 'clearinterval(' in line_content or 'cleartimeout(' in line_content:
                pass  # Properly managed
            else:
                # Vary suggestions based on timer type
                if 'setinterval(' in line_content.lower():
                    issues.append({
                        'line': line_num,
                        'severity': 'medium',
                        'category': 'performance',
                        'message': 'setInterval without cleanup mechanism detected',
                        'suggestion': 'Store interval references and clear them in cleanup functions or component unmount. Consider using requestAnimationFrame for UI updates or implementing proper lifecycle management for background tasks.'
                    })
                else:
                    issues.append({
                        'line': line_num,
                        'severity': 'medium',
                        'category': 'performance',
                        'message': 'setTimeout without cleanup mechanism detected',
                        'suggestion': 'Store timeout references and clear them in cleanup functions or component unmount. Consider using AbortController for modern JavaScript applications or implementing proper cleanup strategies.'
                    })
        
        if 'innerhtml' in line_content.lower():
            issues.append({
                'line': line_num,
                'severity': 'medium',
                'category': 'security',
                'message': 'innerHTML usage can lead to XSS attacks',
                'suggestion': 'Use textContent for plain text or createElement/appendChild for safe DOM manipulation. Consider using a templating library with built-in XSS protection.'
            })
        
        if 'eval(' in line_content.lower():
            issues.append({
                'line': line_num,
                'severity': 'critical',
                'category': 'security',
                'message': 'eval() usage creates security vulnerabilities',
                'suggestion': 'Use JSON.parse() for data, Function constructor for limited code execution, or refactor to avoid dynamic code execution entirely.'
            })
        
        # Memory management
        if any(memory_pattern in line_content.lower() for memory_pattern in ['addlistener', 'onevent', 'addEventListener']):
            if any(cleanup_pattern in line_content.lower() for cleanup_pattern in ['removelistener', 'removeevent', 'removeEventListener']):
                pass  # Properly managed
            else:
                # Vary suggestions based on event type
                if 'click' in line_content.lower() or 'submit' in line_content.lower():
                    issues.append({
                        'line': line_num,
                        'severity': 'medium',
                        'category': 'performance',
                        'message': 'UI event listener without cleanup mechanism',
                        'suggestion': 'Store event listener references and remove them in cleanup functions. Consider using event delegation for dynamic content or implementing proper lifecycle management for UI components.'
                    })
                elif 'scroll' in line_content.lower() or 'resize' in line_content.lower():
                    issues.append({
                        'line': line_num,
                        'severity': 'medium',
                        'category': 'performance',
                        'message': 'High-frequency event listener without cleanup mechanism',
                        'suggestion': 'Store event listener references and remove them in cleanup functions. Consider using throttling/debouncing for high-frequency events and implement proper cleanup for performance-critical operations.'
                    })
                else:
                    issues.append({
                        'line': line_num,
                        'severity': 'medium',
                        'category': 'performance',
                        'message': 'Event listener without cleanup mechanism',
                        'suggestion': 'Store event listener references and remove them in cleanup functions. Consider using AbortController or implementing proper lifecycle management for event handlers.'
                    })
        
        # Resource management
        if any(resource_pattern in line_content.lower() for resource_pattern in ['new file', 'new socket', 'new connection']):
            if 'using' in line_content.lower() or 'with ' in line_content.lower() or 'try:' in line_content.lower():
                pass  # Properly managed
            else:
                # Vary suggestions based on resource type
                if 'socket' in line_content.lower() or 'connection' in line_content.lower():
                    issues.append({
                        'line': line_num,
                        'severity': 'medium',
                        'category': 'resource_management',
                        'message': 'Network resource creation without proper disposal',
                        'suggestion': 'Use context managers, try-finally blocks, or implement IDisposable pattern. Ensure network connections are properly closed, disposed, or returned to connection pools with proper timeout handling.'
                    })
                elif 'file' in line_content.lower():
                    issues.append({
                        'line': line_num,
                        'severity': 'medium',
                        'category': 'resource_management',
                        'message': 'File resource creation without proper disposal',
                        'suggestion': 'Use context managers, try-finally blocks, or implement IDisposable pattern. Ensure file handles are properly closed, disposed, and consider using file locking for concurrent access scenarios.'
                    })
                else:
                    issues.append({
                        'line': line_num,
                        'severity': 'medium',
                        'category': 'resource_management',
                        'message': 'Resource creation without proper disposal',
                        'suggestion': 'Use context managers, try-finally blocks, or implement IDisposable pattern. Ensure resources are properly closed, disposed, or returned to pools.'
                    })
        
        # Concurrency issues
        if any(concurrency_pattern in line_content.lower() for concurrency_pattern in ['thread', 'async', 'promise', 'future']):
            if any(safe_pattern in line_content.lower() for safe_pattern in ['await', 'async', 'lock', 'mutex', 'semaphore']):
                pass  # Properly handled
            else:
                # Vary suggestions based on concurrency type
                if 'thread' in line_content.lower():
                    issues.append({
                        'line': line_num,
                        'severity': 'high',
                        'category': 'concurrency',
                        'message': 'Thread creation without proper synchronization',
                        'suggestion': 'Use proper synchronization primitives like locks, mutexes, or semaphores. Consider using thread pools, async/await patterns, or thread-safe data structures. Implement proper error handling for concurrent operations.'
                    })
                elif 'promise' in line_content.lower() or 'future' in line_content.lower():
                    issues.append({
                        'line': line_num,
                        'severity': 'high',
                        'category': 'concurrency',
                        'message': 'Promise/Future without proper error handling',
                        'suggestion': 'Use proper async/await patterns with try-catch blocks. Handle promise rejections, implement proper error propagation, and consider using Promise.allSettled for multiple concurrent operations.'
                    })
                else:
                    issues.append({
                        'line': line_num,
                        'severity': 'high',
                        'category': 'concurrency',
                        'message': 'Potential concurrency issue detected',
                        'suggestion': 'Use proper synchronization primitives, async/await patterns, or consider using thread-safe data structures. Implement proper error handling for concurrent operations.'
                    })
        
        # Advanced concurrency patterns
        if any(race_pattern in line_content.lower() for race_pattern in ['global ', 'static ', 'shared_', 'common_']):
            if any(safe_pattern in line_content.lower() for safe_pattern in ['lock', 'mutex', 'atomic', 'volatile']):
                pass  # Properly protected
            else:
                if 'global ' in line_content.lower():
                    issues.append({
                        'line': line_num,
                        'severity': 'high',
                        'category': 'concurrency',
                        'message': 'Global variable access without synchronization',
                        'suggestion': 'Use thread-local storage, dependency injection, or pass variables as parameters. Consider using immutable data structures or proper synchronization primitives for shared state.'
                    })
                elif 'static ' in line_content.lower():
                    issues.append({
                        'line': line_num,
                        'severity': 'medium',
                        'category': 'concurrency',
                        'message': 'Static variable access without synchronization',
                        'suggestion': 'Use thread-local storage, dependency injection, or pass variables as parameters. Consider using immutable data structures or proper synchronization primitives for shared state.'
                    })
                else:
                    issues.append({
                        'line': line_num,
                        'severity': 'medium',
                        'category': 'concurrency',
                        'message': 'Shared variable access without synchronization',
                        'suggestion': 'Use proper synchronization primitives, immutable data structures, or consider using thread-local storage. Implement proper error handling for concurrent access.'
                    })
        
        # Memory management patterns
        if any(memory_pattern in line_content.lower() for memory_pattern in ['new ', 'malloc', 'alloc', 'create']):
            if any(cleanup_pattern in line_content.lower() for cleanup_pattern in ['delete', 'free', 'dispose', 'close']):
                pass  # Properly managed
            else:
                if 'new ' in line_content.lower():
                    issues.append({
                        'line': line_num,
                        'severity': 'medium',
                        'category': 'memory_management',
                        'message': 'Object creation without cleanup mechanism',
                        'suggestion': 'Use smart pointers, RAII patterns, or ensure proper cleanup in destructors. Consider using factory patterns or dependency injection for object lifecycle management.'
                    })
                elif 'malloc' in line_content.lower():
                    issues.append({
                        'line': line_num,
                        'severity': 'high',
                        'category': 'memory_management',
                        'message': 'Manual memory allocation without cleanup',
                        'suggestion': 'Use smart pointers, RAII patterns, or ensure proper cleanup with free(). Consider using standard containers or smart pointers for automatic memory management.'
                    })
                else:
                    issues.append({
                        'line': line_num,
                        'severity': 'medium',
                        'category': 'memory_management',
                        'message': 'Resource creation without cleanup mechanism',
                        'suggestion': 'Use smart pointers, RAII patterns, or ensure proper cleanup. Consider using factory patterns or dependency injection for resource lifecycle management.'
                    })
        
        # Modern development practices
        if any(modern_pattern in line_content.lower() for modern_pattern in ['var ', 'let ', 'const ', 'function ', 'def ']):
            if 'var ' in line_content.lower():
                issues.append({
                    'line': line_num,
                    'severity': 'low',
                    'category': 'modern_practices',
                    'message': 'var keyword usage detected',
                    'suggestion': 'Use let or const instead of var. Prefer const for values that won\'t be reassigned, and let for variables that will change. This provides better block scoping and prevents hoisting issues.'
                })
            elif 'function ' in line_content.lower() and '=>' not in line_content:
                issues.append({
                    'line': line_num,
                    'severity': 'low',
                    'category': 'modern_practices',
                    'message': 'Function declaration syntax detected',
                    'suggestion': 'Consider using arrow functions for callbacks and short functions. Use function declarations for named functions that need hoisting. Consider using async/await for asynchronous operations.'
                })
            elif 'def ' in line_content.lower() and '->' not in line_content:
                issues.append({
                    'line': line_num,
                    'severity': 'low',
                    'category': 'modern_practices',
                    'message': 'Function definition without type hints',
                    'suggestion': 'Add type hints for better code documentation and IDE support. Use mypy for static type checking and consider using dataclasses for simple data structures.'
                })
        
        # Testing and quality patterns
        if any(test_pattern in line_content.lower() for test_pattern in ['test_', 'spec_', 'describe(', 'it(']):
            if 'assert' in line_content.lower() or 'expect' in line_content.lower():
                pass  # Has assertions
            else:
                if 'test_' in line_content.lower():
                    issues.append({
                        'line': line_num,
                        'severity': 'low',
                        'category': 'testing',
                        'message': 'Test function without assertions',
                        'suggestion': 'Add proper assertions to verify expected behavior. Use descriptive test names and consider using test data builders or factories for complex test setup.'
                    })
                elif 'describe(' in line_content.lower() or 'it(' in line_content.lower():
                    issues.append({
                        'line': line_num,
                        'severity': 'low',
                        'category': 'testing',
                        'message': 'Test description without assertions',
                        'suggestion': 'Add proper assertions to verify expected behavior. Use descriptive test names and consider using test data builders or factories for complex test setup.'
                    })
        
        # Documentation patterns
        if line_content.strip().startswith(('def ', 'class ', 'function ')):
            if '"""' in line_content or "'''" in line_content or '///' in line_content:
                pass  # Has documentation
            else:
                if 'def ' in line_content.lower():
                    issues.append({
                        'line': line_num,
                        'severity': 'low',
                        'category': 'documentation',
                        'message': 'Function definition without docstring',
                        'suggestion': 'Add comprehensive docstrings following PEP 257. Include parameter descriptions, return values, exceptions, and usage examples. Consider using type hints for better documentation.'
                    })
                elif 'class ' in line_content.lower():
                    issues.append({
                        'line': line_num,
                        'severity': 'low',
                        'category': 'documentation',
                        'message': 'Class definition without docstring',
                        'suggestion': 'Add comprehensive class docstrings explaining purpose, responsibilities, and usage. Document public methods and consider using dataclasses for simple data structures.'
                    })
                else:
                    issues.append({
                        'line': line_num,
                        'severity': 'low',
                        'category': 'documentation',
                        'message': 'Function/class definition without documentation',
                        'suggestion': 'Add comprehensive documentation explaining purpose, parameters, return values, and usage examples. Consider using type hints and following language-specific documentation standards.'
                    })
        
        # Input validation
        if any(input_pattern in line_content.lower() for input_pattern in ['input(', 'readline(', 'gets(', 'scanf(']):
            if any(validation_pattern in line_content.lower() for validation_pattern in ['validate', 'check', 'verify', 'sanitize']):
                pass  # Has validation
            else:
                # Vary suggestions based on input type
                if 'input(' in line_content.lower():
                    issues.append({
                        'line': line_num,
                        'severity': 'medium',
                        'category': 'input_validation',
                        'message': 'User input without validation',
                        'suggestion': 'Implement input validation, sanitization, and type checking. Consider using schema validation libraries and implement proper error handling for invalid input with user-friendly error messages.'
                    })
                elif 'readline(' in line_content.lower():
                    issues.append({
                        'line': line_num,
                        'severity': 'medium',
                        'category': 'input_validation',
                        'message': 'Command line input without validation',
                        'suggestion': 'Implement proper command line argument validation, sanitization, and help text. Consider using argument parsing libraries and implement proper error handling for invalid command line inputs.'
                    })
                else:
                    issues.append({
                        'line': line_num,
                        'severity': 'medium',
                        'category': 'input_validation',
                        'message': 'User input without validation',
                        'suggestion': 'Implement input validation, sanitization, and type checking. Consider using schema validation libraries and implement proper error handling for invalid input.'
                    })
        
        # Advanced input validation patterns
        if any(web_input in line_content.lower() for web_input in ['request.', 'req.', 'params.', 'query.', 'body.']):
            if any(validation_pattern in line_content.lower() for validation_pattern in ['validate', 'check', 'verify', 'sanitize', 'escape']):
                pass  # Has validation
            else:
                if 'request.' in line_content.lower():
                    if 'json' in line_content.lower():
                        issues.append({
                            'line': line_num,
                            'severity': 'high',
                            'category': 'input_validation',
                            'message': 'JSON request body without validation',
                            'suggestion': 'Implement JSON schema validation, type checking, and sanitization. Use libraries like Pydantic, Marshmallow, or Joi for robust validation. Consider implementing input sanitization for XSS prevention.'
                        })
                    elif 'form' in line_content.lower() or 'multipart' in line_content.lower():
                        issues.append({
                            'line': line_num,
                            'severity': 'high',
                            'category': 'input_validation',
                            'message': 'Form data without validation',
                            'suggestion': 'Implement form validation, file type checking, and size limits. Use validation libraries and implement proper error handling for invalid form submissions. Consider CSRF protection.'
                        })
                    else:
                        issues.append({
                            'line': line_num,
                            'severity': 'medium',
                            'category': 'input_validation',
                            'message': 'Web request data without validation',
                            'suggestion': 'Implement proper input validation, sanitization, and type checking. Use validation libraries and implement proper error handling for invalid requests. Consider implementing rate limiting.'
                        })
        
        # Framework-specific patterns
        if any(framework_pattern in line_content.lower() for framework_pattern in ['django', 'flask', 'fastapi', 'express', 'react', 'vue', 'angular']):
            if 'django' in line_content.lower():
                if 'models.CharField' in line_content and 'max_length' not in line_content:
                    issues.append({
                        'line': line_num,
                        'severity': 'medium',
                        'category': 'framework_best_practices',
                        'message': 'Django CharField without max_length',
                        'suggestion': 'Always specify max_length for CharField to prevent database issues and improve performance. Consider using TextField for longer content and implement proper validation.'
                    })
                elif 'models.DateTimeField' in line_content and 'auto_now' not in line_content and 'auto_now_add' not in line_content:
                    issues.append({
                        'line': line_num,
                        'severity': 'low',
                        'category': 'framework_best_practices',
                        'message': 'DateTimeField without auto timestamps',
                        'suggestion': 'Consider using auto_now_add for creation timestamps and auto_now for modification timestamps. This provides automatic audit trail functionality.'
                    })
            elif 'flask' in line_content.lower():
                if 'app.run(' in line_content and 'debug=True' in line_content:
                    issues.append({
                        'line': line_num,
                        'severity': 'high',
                        'category': 'framework_best_practices',
                        'message': 'Flask debug mode enabled in production code',
                        'suggestion': 'Remove debug=True from production code. Use environment variables to control debug mode and implement proper logging and error handling for production environments.'
                    })
            elif 'react' in line_content.lower():
                if 'useState(' in line_content and 'useEffect(' not in line_content:
                    issues.append({
                        'line': line_num,
                        'severity': 'low',
                        'category': 'framework_best_practices',
                        'message': 'useState without useEffect for side effects',
                        'suggestion': 'Use useEffect for side effects when state changes. Consider using useCallback and useMemo for performance optimization. Implement proper cleanup in useEffect.'
                    })
        
        # Database and ORM patterns
        if any(db_pattern in line_content.lower() for db_pattern in ['select *', 'select count(*)', 'n+1', 'lazy loading']):
            if 'select *' in line_content.lower():
                issues.append({
                    'line': line_num,
                    'severity': 'medium',
                    'category': 'database',
                    'message': 'SELECT * query detected',
                    'suggestion': 'Specify only required columns to improve performance and reduce network transfer. Use column aliases for clarity and consider implementing pagination for large result sets.'
                })
            elif 'select count(*)' in line_content.lower():
                issues.append({
                    'line': line_num,
                    'severity': 'low',
                    'category': 'database',
                    'message': 'COUNT(*) query for large tables',
                    'suggestion': 'Consider using approximate counts, cached counts, or pagination for large tables. Use database-specific optimizations like COUNT(1) or indexed columns for better performance.'
                })
            elif 'n+1' in line_content.lower():
                issues.append({
                    'line': line_num,
                    'severity': 'high',
                    'category': 'database',
                    'message': 'N+1 query problem detected',
                    'suggestion': 'Use eager loading, JOIN queries, or batch loading to avoid N+1 queries. Consider using ORM features like select_related, prefetch_related, or implementing data access patterns.'
                })
        
        # API design patterns
        if any(api_pattern in line_content.lower() for api_pattern in ['api/v1', 'version', 'endpoint', 'route']):
            if 'api/v1' in line_content.lower() or 'v1/' in line_content.lower():
                issues.append({
                    'line': line_num,
                    'severity': 'low',
                    'category': 'api_design',
                    'message': 'API versioning in URL path',
                    'suggestion': 'Consider using header-based versioning (Accept header) or content negotiation for better API versioning. Implement proper version deprecation strategies and backward compatibility.'
                })
            elif 'endpoint' in line_content.lower() and 'auth' not in line_content.lower():
                issues.append({
                    'line': line_num,
                    'severity': 'medium',
                    'category': 'api_design',
                    'message': 'API endpoint without authentication',
                    'suggestion': 'Implement proper authentication and authorization for API endpoints. Use JWT tokens, OAuth2, or API keys with proper scoping and rate limiting.'
                })
        
        # Configuration and environment patterns
        if any(config_pattern in line_content.lower() for config_pattern in ['config.', 'settings.', 'env.', 'process.env']):
            if 'hardcoded' in line_content.lower() or 'localhost' in line_content.lower():
                issues.append({
                    'line': line_num,
                    'severity': 'medium',
                    'category': 'configuration',
                    'message': 'Hardcoded configuration values',
                    'suggestion': 'Use environment variables, configuration files, or configuration management systems. Implement configuration validation and consider using configuration management tools for different environments.'
                })
            elif 'dev' in line_content.lower() and 'prod' not in line_content.lower():
                issues.append({
                    'line': line_num,
                    'severity': 'low',
                    'category': 'configuration',
                    'message': 'Development-only configuration',
                    'suggestion': 'Ensure configuration works across all environments. Use environment-specific configuration files and implement proper configuration validation for production deployments.'
                })
        
        # Code quality
        if re.search(r'\b\d{4,}\b', line_content):  # Magic numbers 1000+
            # Provide different suggestions based on the context
            if any(time_indicator in line_content.lower() for time_indicator in ['timeout', 'delay', 'interval', 'sleep']):
                issues.append({
                    'line': line_num,
                    'severity': 'medium',
                    'category': 'code_quality',
                    'message': 'Magic number detected in timing configuration',
                    'suggestion': 'Extract timeout values to named constants with descriptive names. Consider using configuration files or environment variables for different environments (dev/staging/prod).'
                })
            elif any(size_indicator in line_content.lower() for size_indicator in ['size', 'buffer', 'limit', 'capacity']):
                issues.append({
                    'line': line_num,
                    'severity': 'medium',
                    'category': 'code_quality',
                    'message': 'Magic number detected in size configuration',
                    'suggestion': 'Define size constants with clear naming conventions. Consider using enums or configuration objects for related constants and document the reasoning behind specific values.'
                })
            elif any(port_indicator in line_content.lower() for port_indicator in ['port', 'socket', 'bind']):
                issues.append({
                    'line': line_num,
                    'severity': 'medium',
                    'category': 'code_quality',
                    'message': 'Hardcoded port number detected',
                    'suggestion': 'Use configuration files or environment variables for port numbers. Consider implementing port scanning to find available ports or using well-known port ranges.'
                })
            elif any(version_indicator in line_content.lower() for version_indicator in ['version', 'build', 'release']):
                issues.append({
                    'line': line_num,
                    'severity': 'medium',
                    'category': 'code_quality',
                    'message': 'Hardcoded version number detected',
                    'suggestion': 'Extract version information to a dedicated version file or use semantic versioning. Consider automating version bumping through CI/CD pipelines.'
                })
            else:
                issues.append({
                    'line': line_num,
                    'severity': 'medium',
                    'category': 'code_quality',
                    'message': 'Magic number detected',
                    'suggestion': 'Extract to named constants with descriptive names. Consider using enums or configuration objects for related constants. Document the business logic behind these values.'
                })
        
        # Advanced code quality patterns
        if re.search(r'\b\d{2,3}\b', line_content):  # Magic numbers 10-999
            if any(rate_indicator in line_content.lower() for rate_indicator in ['rate', 'frequency', 'interval', 'period']):
                issues.append({
                    'line': line_num,
                    'severity': 'low',
                    'category': 'code_quality',
                    'message': 'Magic number detected in rate configuration',
                    'suggestion': 'Extract rate values to named constants. Consider using configuration files for different environments and document the business reasoning behind specific rates.'
                })
            elif any(threshold_indicator in line_content.lower() for threshold_indicator in ['threshold', 'limit', 'max', 'min']):
                issues.append({
                    'line': line_num,
                    'severity': 'low',
                    'category': 'code_quality',
                    'message': 'Magic number detected in threshold configuration',
                    'suggestion': 'Extract threshold values to named constants. Consider using configuration files and document the business logic behind specific threshold values.'
                })
        
        # String concatenation patterns
        if line_content.count('+') > 2 and any(string_indicator in line_content for string_indicator in ['"', "'"]):
            if 'sql' in line_content.lower() or 'query' in line_content.lower():
                issues.append({
                    'line': line_num,
                    'severity': 'high',
                    'category': 'security',
                    'message': 'SQL query construction with string concatenation',
                    'suggestion': 'Use parameterized queries or query builders. Never concatenate user input into SQL strings. Consider using ORMs or query builders with built-in SQL injection protection.'
                })
            elif 'url' in line_content.lower() or 'http' in line_content.lower():
                issues.append({
                    'line': line_num,
                    'severity': 'medium',
                    'category': 'code_quality',
                    'message': 'URL construction with string concatenation',
                    'suggestion': 'Use URL builders or urllib.parse.urljoin() for safe URL construction. Validate and sanitize URL components before concatenation.'
                })
            else:
                issues.append({
                    'line': line_num,
                    'severity': 'low',
                    'category': 'code_quality',
                    'message': 'Multiple string concatenations detected',
                    'suggestion': 'Use f-strings, .format(), or join() for better performance and readability. Consider using string builders for complex string construction.'
                })
        
        # Variable naming patterns
        if re.search(r'\b[a-z][a-z0-9_]*\s*=', line_content):
            var_name = re.search(r'\b([a-z][a-z0-9_]*)\s*=', line_content).group(1)
            if len(var_name) < 3:
                issues.append({
                    'line': line_num,
                    'severity': 'low',
                    'category': 'readability',
                    'message': 'Variable name too short',
                    'suggestion': 'Use descriptive variable names that clearly indicate purpose. Avoid single letters except for loop counters or mathematical formulas.'
                })
            elif var_name in ['data', 'info', 'stuff', 'temp', 'tmp']:
                issues.append({
                    'line': line_num,
                    'severity': 'medium',
                    'category': 'readability',
                    'message': 'Generic variable name detected',
                    'suggestion': 'Use specific, descriptive variable names that indicate the data type and purpose. Consider using domain-specific terminology.'
                })
        
        # Function complexity patterns
        if line_content.count('(') > 3 and line_content.count(')') > 3:
            if 'if' in line_content and 'and' in line_content:
                issues.append({
                    'line': line_num,
                    'severity': 'medium',
                    'category': 'code_quality',
                    'message': 'Complex function call with multiple conditions',
                    'suggestion': 'Extract complex conditions to well-named boolean methods. Consider using early returns or guard clauses to reduce nesting and improve readability.'
                })
            else:
                issues.append({
                    'line': line_num,
                    'severity': 'low',
                    'category': 'code_quality',
                    'message': 'Function call with many parameters',
                    'suggestion': 'Consider using parameter objects, builder pattern, or default parameters. Group related parameters into configuration objects for better maintainability.'
                })
        
        # Loop and iteration patterns
        if any(loop_pattern in line_content.lower() for loop_pattern in ['for ', 'while ', 'foreach', 'map(', 'filter(']):
            if 'range(' in line_content.lower() and 'len(' in line_content.lower():
                issues.append({
                    'line': line_num,
                    'severity': 'low',
                    'category': 'code_quality',
                    'message': 'Index-based loop with len()',
                    'suggestion': 'Use enumerate() for index-based loops or direct iteration for value-based loops. Consider using list comprehensions or generator expressions for simple transformations.'
                })
            elif 'enumerate(' in line_content.lower():
                pass  # Good practice
            elif 'in ' in line_content.lower():
                pass  # Good practice
            else:
                issues.append({
                    'line': line_num,
                    'severity': 'low',
                    'category': 'code_quality',
                    'message': 'Loop pattern detected',
                    'suggestion': 'Consider using list comprehensions, generator expressions, or functional programming patterns when appropriate. Ensure loops have clear termination conditions.'
                })
        
        # Nested conditionals
        if line_content.count('if ') > 2 or (line_content.count('if ') > 1 and line_content.count('and ') > 0):
            if 'admin' in line_content.lower() or 'permission' in line_content.lower():
                issues.append({
                    'line': line_num,
                    'severity': 'medium',
                    'category': 'code_quality',
                    'message': 'Complex authorization logic detected',
                    'suggestion': 'Extract authorization logic to dedicated service classes. Consider using decorators, middleware, or policy-based authorization patterns for cleaner, more maintainable code.'
                })
            elif 'validation' in line_content.lower() or 'check' in line_content.lower():
                issues.append({
                    'line': line_num,
                    'severity': 'medium',
                    'category': 'code_quality',
                    'message': 'Complex validation logic detected',
                    'suggestion': 'Use validation libraries or create dedicated validator classes. Consider implementing the chain of responsibility pattern for complex validation workflows.'
                })
            elif 'status' in line_content.lower() or 'state' in line_content.lower():
                issues.append({
                    'line': line_num,
                    'severity': 'medium',
                    'category': 'code_quality',
                    'message': 'Complex state checking logic detected',
                    'suggestion': 'Consider using state machines, enums, or the command pattern for complex state transitions. Extract state logic to dedicated state management classes.'
                })
            elif 'error' in line_content.lower() or 'exception' in line_content.lower():
                issues.append({
                    'line': line_num,
                    'severity': 'medium',
                    'category': 'code_quality',
                    'message': 'Complex error handling logic detected',
                    'suggestion': 'Use custom exception hierarchies and error codes. Consider implementing the strategy pattern for different error handling approaches based on context.'
                })
            else:
                issues.append({
                    'line': line_num,
                    'severity': 'medium',
                    'category': 'code_quality',
                    'message': 'Complex conditional logic detected',
                    'suggestion': 'Extract complex conditions to well-named boolean methods. Consider using early returns, guard clauses, or strategy pattern for complex branching. Use truth tables to verify logic.'
                })
        
        # Long method chains
        if line_content.count('.') > 3:
            if 'api' in line_content.lower() or 'client' in line_content.lower():
                issues.append({
                    'line': line_num,
                    'severity': 'medium',
                    'category': 'code_quality',
                    'message': 'Long API method chain detected',
                    'suggestion': 'Break into intermediate variables for readability. Consider using builder pattern or fluent interfaces with proper error handling at each step. Add logging for debugging.'
                })
            elif 'query' in line_content.lower() or 'filter' in line_content.lower():
                issues.append({
                    'line': line_num,
                    'severity': 'medium',
                    'category': 'code_quality',
                    'message': 'Long query method chain detected',
                    'suggestion': 'Extract query building logic to dedicated query builder classes. Consider using the repository pattern or query objects for complex data access operations.'
                })
            elif 'transform' in line_content.lower() or 'map' in line_content.lower():
                issues.append({
                    'line': line_num,
                    'severity': 'medium',
                    'category': 'code_quality',
                    'message': 'Long data transformation chain detected',
                    'suggestion': 'Break transformations into separate functions or use the pipeline pattern. Consider implementing the builder pattern for complex object construction.'
                })
            elif 'config' in line_content.lower() or 'setting' in line_content.lower():
                issues.append({
                    'line': line_num,
                    'severity': 'medium',
                    'category': 'code_quality',
                    'message': 'Long configuration method chain detected',
                    'suggestion': 'Use configuration builder pattern or fluent configuration APIs. Consider using configuration objects with validation and default values.'
                })
            else:
                issues.append({
                    'line': line_num,
                    'severity': 'medium',
                    'category': 'code_quality',
                    'message': 'Long method chain detected',
                    'suggestion': 'Break into intermediate variables for readability. Consider using builder pattern or method chaining with proper error handling at each step. Add validation between steps.'
                })
        
        # Hardcoded paths
        if any(path_indicator in line_content for path_indicator in ['/usr/local/', 'c:\\', '/home/', 'c:/', '/tmp/']):
            if 'tmp' in line_content.lower() or 'temp' in line_content.lower():
                issues.append({
                    'line': line_num,
                    'severity': 'medium',
                    'category': 'code_quality',
                    'message': 'Hardcoded temporary directory path detected',
                    'suggestion': 'Use tempfile.gettempdir() or os.path.join(tempfile.gettempdir(), filename) for cross-platform compatibility. Consider using context managers for temporary file cleanup.'
                })
            elif 'home' in line_content.lower() or 'user' in line_content.lower():
                issues.append({
                    'line': line_num,
                    'severity': 'medium',
                    'category': 'code_quality',
                    'message': 'Hardcoded user directory path detected',
                    'suggestion': 'Use os.path.expanduser("~") or pathlib.Path.home() for user directories. Consider using XDG base directories or platform-specific user data locations.'
                })
            elif 'log' in line_content.lower() or 'output' in line_content.lower():
                issues.append({
                    'line': line_num,
                    'severity': 'medium',
                    'category': 'code_quality',
                    'message': 'Hardcoded log/output directory path detected',
                    'suggestion': 'Use environment variables or configuration for log directories. Consider implementing log rotation and centralized logging with proper permissions.'
                })
            elif 'data' in line_content.lower() or 'storage' in line_content.lower():
                issues.append({
                    'line': line_num,
                    'severity': 'medium',
                    'category': 'code_quality',
                    'message': 'Hardcoded data storage path detected',
                    'suggestion': 'Use configuration files or environment variables for data paths. Consider implementing data migration strategies and backup/restore procedures.'
                })
                            else:
                    issues.append({
                        'line': line_num,
                        'severity': 'medium',
                        'category': 'code_quality',
                        'message': 'Hardcoded file path detected',
                        'suggestion': 'Use path.join() for cross-platform compatibility, environment variables for configurable paths, or relative paths when appropriate. Consider using pathlib for modern path operations.'
                    })
        
        # Final specialized patterns for 100+ unique comment types
        
        # TODO/FIXME comment analysis with context-aware suggestions
        if any(todo_pattern in line_content.lower() for todo_pattern in ['todo:', 'fixme:', 'hack:', 'note:', 'xxx:', 'bug:']):
            todo_content = line_content.lower()
            if 'error' in todo_content or 'exception' in todo_content:
                issues.append({
                    'line': line_num,
                    'severity': 'medium',
                    'category': 'code_quality',
                    'message': 'TODO comment for error handling',
                    'suggestion': 'Implement comprehensive error handling with proper logging, user-friendly error messages, and graceful degradation. Consider using custom exception hierarchies and error codes.'
                })
            elif 'test' in todo_content:
                issues.append({
                    'line': line_num,
                    'severity': 'medium',
                    'category': 'testing',
                    'message': 'TODO comment for testing',
                    'suggestion': 'Write comprehensive unit tests covering edge cases, error conditions, and integration scenarios. Use mocking for external dependencies and aim for high test coverage.'
                })
            elif 'log' in todo_content:
                issues.append({
                    'line': line_num,
                    'severity': 'low',
                    'category': 'monitoring',
                    'message': 'TODO comment for logging',
                    'suggestion': 'Implement structured logging with appropriate log levels, correlation IDs, and context information. Consider using centralized logging and log aggregation for production environments.'
                })
            elif 'validate' in todo_content:
                issues.append({
                    'line': line_num,
                    'severity': 'medium',
                    'category': 'input_validation',
                    'message': 'TODO comment for validation',
                    'suggestion': 'Implement comprehensive input validation, sanitization, and schema validation. Use validation libraries and provide user-friendly error messages for invalid input.'
                })
            elif 'performance' in todo_content or 'optimize' in todo_content:
                issues.append({
                    'line': line_num,
                    'severity': 'medium',
                    'category': 'performance',
                    'message': 'TODO comment for performance optimization',
                    'suggestion': 'Profile the code to identify bottlenecks, implement caching strategies, and optimize algorithms. Consider using performance monitoring tools and implementing metrics collection.'
                })
            elif 'refactor' in todo_content:
                issues.append({
                    'line': line_num,
                    'severity': 'low',
                    'category': 'code_quality',
                    'message': 'TODO comment for refactoring',
                    'suggestion': 'Break down complex functions, extract common patterns, and improve naming conventions. Consider using design patterns and implementing code review guidelines.'
                })
            elif 'security' in todo_content:
                issues.append({
                    'line': line_num,
                    'severity': 'high',
                    'category': 'security',
                    'message': 'TODO comment for security improvements',
                    'suggestion': 'Conduct security review following OWASP guidelines, implement proper authentication and authorization, and consider using security scanning tools.'
                })
            elif 'document' in todo_content:
                issues.append({
                    'line': line_num,
                    'severity': 'low',
                    'category': 'documentation',
                    'message': 'TODO comment for documentation',
                    'suggestion': 'Write comprehensive API documentation, code comments, and user guides. Consider using automated documentation generation tools and maintaining up-to-date examples.'
                })
            else:
                issues.append({
                    'line': line_num,
                    'severity': 'low',
                    'category': 'code_quality',
                    'message': 'Generic TODO comment detected',
                    'suggestion': 'Provide specific details about what needs to be implemented. Include acceptance criteria, implementation notes, and consider creating proper issue tickets for tracking.'
                })
        
        # Language-specific best practices
        if any(lang_pattern in line_content.lower() for lang_pattern in ['python', 'javascript', 'java', 'c++', 'go', 'rust']):
            if 'python' in line_content.lower():
                if 'import *' in line_content:
                    issues.append({
                        'line': line_num,
                        'severity': 'medium',
                        'category': 'python_best_practices',
                        'message': 'Wildcard import detected',
                        'suggestion': 'Import only specific modules to avoid namespace pollution and improve code clarity. Use absolute imports and consider using __all__ to control public API.'
                    })
                elif 'lambda' in line_content and len(line_content) > 80:
                    issues.append({
                        'line': line_num,
                        'severity': 'low',
                        'category': 'python_best_practices',
                        'message': 'Complex lambda expression detected',
                        'suggestion': 'Extract complex lambda expressions to named functions for better readability and testability. Use list comprehensions or generator expressions when appropriate.'
                    })
            elif 'javascript' in line_content.lower():
                if 'var ' in line_content:
                    issues.append({
                        'line': line_num,
                        'severity': 'low',
                        'category': 'javascript_best_practices',
                        'message': 'var keyword usage in modern JavaScript',
                        'suggestion': 'Use const for values that won\'t be reassigned, let for variables that will change. This provides better block scoping and prevents hoisting issues.'
                    })
                elif '===' not in line_content and '==' in line_content:
                    issues.append({
                        'line': line_num,
                        'severity': 'medium',
                        'category': 'javascript_best_practices',
                        'message': 'Loose equality comparison detected',
                        'suggestion': 'Use strict equality (===) and strict inequality (!==) to avoid type coercion issues. Consider using explicit type conversion when needed.'
                    })
            elif 'java' in line_content.lower():
                if 'public static void main' in line_content and 'args' in line_content:
                    issues.append({
                        'line': line_num,
                        'severity': 'low',
                        'category': 'java_best_practices',
                        'message': 'Main method without proper argument handling',
                        'suggestion': 'Implement proper command line argument parsing and validation. Use argument parsing libraries and provide help text for command line usage.'
                    })
        
        # Cloud and deployment patterns
        if any(cloud_pattern in line_content.lower() for cloud_pattern in ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform']):
            if 'aws' in line_content.lower():
                if 'access_key' in line_content or 'secret_key' in line_content:
                    issues.append({
                        'line': line_num,
                        'severity': 'critical',
                        'category': 'cloud_security',
                        'message': 'AWS credentials hardcoded in source',
                        'suggestion': 'Use IAM roles, environment variables, or AWS Secrets Manager. Implement proper credential rotation and use least privilege access policies.'
                    })
                elif 'region' in line_content and 'us-east-1' in line_content:
                    issues.append({
                        'line': line_num,
                        'severity': 'low',
                        'category': 'cloud_configuration',
                        'message': 'Hardcoded AWS region detected',
                        'suggestion': 'Use environment variables or configuration files for region selection. Consider implementing multi-region deployment strategies for high availability.'
                    })
            elif 'docker' in line_content.lower():
                if 'FROM ubuntu:latest' in line_content or 'FROM debian:latest' in line_content:
                    issues.append({
                        'line': line_num,
                        'severity': 'medium',
                        'category': 'container_security',
                        'message': 'Latest tag in Docker base image',
                        'suggestion': 'Use specific version tags for reproducible builds and security. Implement image scanning and consider using minimal base images like Alpine Linux.'
                    })
                elif 'RUN apt-get update' in line_content and 'apt-get clean' not in line_content:
                    issues.append({
                        'line': line_num,
                        'severity': 'medium',
                        'category': 'container_optimization',
                        'message': 'Docker layer optimization opportunity',
                        'suggestion': 'Combine RUN commands, clean package caches, and remove unnecessary files in the same layer. Use multi-stage builds to reduce final image size.'
                    })
        
        # Monitoring and observability patterns
        if any(monitor_pattern in line_content.lower() for monitor_pattern in ['metrics', 'logging', 'tracing', 'monitoring', 'alerting']):
            if 'metrics' in line_content.lower() and 'counter' not in line_content.lower() and 'gauge' not in line_content.lower():
                issues.append({
                    'line': line_num,
                    'severity': 'low',
                    'category': 'monitoring',
                    'message': 'Generic metrics collection detected',
                    'suggestion': 'Use specific metric types (counters, gauges, histograms) with proper labels and documentation. Implement metric aggregation and consider using Prometheus or similar monitoring systems.'
                })
            elif 'logging' in line_content.lower() and 'level' not in line_content.lower():
                issues.append({
                    'line': line_num,
                    'severity': 'low',
                    'category': 'monitoring',
                    'message': 'Logging without level specification',
                    'suggestion': 'Use appropriate log levels (DEBUG, INFO, WARN, ERROR) and implement structured logging with correlation IDs. Consider log aggregation and retention policies.'
                })
        
        # Accessibility and internationalization patterns
        if any(accessibility_pattern in line_content.lower() for accessibility_pattern in ['alt=', 'aria-', 'lang=', 'translate', 'i18n']):
            if 'alt=' in line_content.lower() and 'alt=""' in line_content:
                issues.append({
                    'line': line_num,
                    'severity': 'medium',
                    'category': 'accessibility',
                    'message': 'Empty alt attribute for image',
                    'suggestion': 'Provide descriptive alt text for images or use alt="" for decorative images. Consider using aria-label for complex images and implementing proper accessibility testing.'
                })
            elif 'lang=' in line_content.lower() and 'en' in line_content.lower():
                issues.append({
                    'line': line_num,
                    'severity': 'low',
                    'category': 'internationalization',
                    'message': 'Hardcoded language attribute',
                    'suggestion': 'Use dynamic language detection or configuration-based language selection. Implement proper internationalization (i18n) and localization (l10n) support.'
                })
        
        return issues
    
    def _generate_pr_review_summary(self, analysis_results: List[Dict], pr_data: Dict, total_score: int, total_issues: int) -> str:
        """Generate a comprehensive PR review summary."""
        try:
            # Collect all issues for categorization
            all_issues = []
            for result in analysis_results:
                file_issues = result['analysis'].get('issues', [])
                for issue in file_issues:
                    issue['file'] = result['file']
                    all_issues.append(issue)
            
            # Group issues by category
            categories = {
                'security': [],
                'performance': [],
                'style': [],
                'documentation': [],
                'error_handling': [],
                'other': []
            }
            
            for issue in all_issues:
                category = issue.get('category', 'other')
                if category in categories:
                    categories[category].append(issue)
                else:
                    categories['other'].append(issue)
            
            # Generate summary
            summary = f"""## 🔍 Code Review Summary

**Repository:** {pr_data['repository']}
**Author:** {pr_data['user']['login']}
**PR Title:** {pr_data['title']}

### 📊 Analysis Overview
- **Files Analyzed:** {len(analysis_results)}
- **Total Suggestions:** {total_issues}
- **Critical Suggestions:** {len([i for i in all_issues if i.get('severity') == 'critical'])}
- **High Suggestions:** {len([i for i in all_issues if i.get('severity') == 'high'])}
- **Medium Suggestions:** {len([i for i in all_issues if i.get('severity') == 'medium'])}
- **Low Suggestions:** {len([i for i in all_issues if i.get('severity') == 'low'])}

### 🎯 Detailed Suggestions

"""
            
            # Add suggestions by category
            for category, issues in categories.items():
                if issues:
                    category_name = category.replace('_', ' ').title()
                    summary += f"#### {category_name}\n"
                    
                    # Show top 3 issues per category
                    top_issues = sorted(issues, key=lambda x: {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}.get(x.get('severity', 'low'), 0), reverse=True)[:3]
                    
                    for issue in top_issues:
                        severity_emoji = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'}.get(issue.get('severity', 'low'), '🟢')
                        summary += f"- {severity_emoji} **{issue['file']}:** {issue['message']}\n"
                        if issue.get('suggestion'):
                            summary += f"  💡 **Suggestion:** {issue['suggestion']}\n"
                        summary += "\n"
            
            # Add general recommendations
            if total_issues == 0:
                summary += "### ✅ **Great Work!** No specific issues detected in the changes.\n\n"
            else:
                summary += "### 💡 General Recommendations\n\n"
                
                # PR size recommendations
                changed_files = len(analysis_results)
                if changed_files > 10:
                    summary += "- 📏 **Large PR:** Consider breaking this into smaller, more focused pull requests for easier review.\n"
                elif changed_files > 5:
                    summary += "- 📏 **Medium PR:** Good size for review. Consider adding more detailed commit messages.\n"
                else:
                    summary += "- 📏 **Small PR:** Perfect size for quick review!\n"
                
                # Add specific recommendations based on issues found
                if categories['security']:
                    summary += "- 🔒 **Security:** Please review the security-related suggestions above.\n"
                if categories['performance']:
                    summary += "- ⚡ **Performance:** Consider the performance optimization suggestions.\n"
                if categories['documentation']:
                    summary += "- 📚 **Documentation:** Adding documentation would improve code maintainability.\n"
            
            summary += "\n---\n*This review was generated automatically by the GitHub Code Review Agent.*"
            
            return summary
            
        except Exception as e:
            return f"Error generating review summary: {str(e)}"
    
    def get_all_accessible_pull_requests(self, state="open", include_private=True):
        """Get all pull requests from repositories accessible to the user."""
        try:
            print(f"🔍 Fetching {state} pull requests from accessible repositories...")
            
            # First get all repositories
            repos_result = self.get_user_repositories(include_private=include_private)
            if not repos_result["success"]:
                return {"success": False, "error": f"Failed to get repositories: {repos_result['error']}"}
            
            all_prs = []
            repos = repos_result["repositories"]
            
            for repo in repos:
                owner = repo["owner"]["login"]
                repo_name = repo["name"]
                
                # Get PRs for this repository
                prs_result = self.get_repository_pull_requests(owner, repo_name, state)
                if prs_result["success"]:
                    prs = prs_result["pull_requests"]
                    for pr in prs:
                        pr["repository"] = f"{owner}/{repo_name}"
                    all_prs.extend(prs)
                else:
                    print(f"⚠️  Warning: Failed to get PRs for {owner}/{repo_name}: {prs_result['error']}")
            
            return {
                "success": True,
                "pull_requests": all_prs,
                "total_count": len(all_prs)
            }
            
        except Exception as e:
            error_msg = f"Failed to get all accessible pull requests: {e}"
            print(f"❌ {error_msg}")
            return {"success": False, "error": error_msg}
    
    def get_repository_pull_requests(self, owner, repo, state="open"):
        """Get pull requests for a specific repository."""
        try:
            url = f"{self.api_base}/repos/{owner}/{repo}/pulls"
            params = {"state": state, "per_page": 100}
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            pull_requests = response.json()
            
            # Add repository info to each PR
            for pr in pull_requests:
                pr["repository"] = f"{owner}/{repo}"
                pr["head_branch"] = pr["head"]["ref"]
                pr["base_branch"] = pr["base"]["ref"]
            
            return {
                "success": True,
                "pull_requests": pull_requests,
                "total_count": len(pull_requests)
            }
            
        except Exception as e:
            error_msg = f"Failed to get pull requests for {owner}/{repo}: {e}"
            print(f"❌ {error_msg}")
            return {"success": False, "error": error_msg}
    
    def get_pull_request_details(self, owner, repo, pr_number):
        """Get detailed information about a specific pull request."""
        try:
            url = f"{self.api_base}/repos/{owner}/{repo}/pulls/{pr_number}"
            
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            pr_data = response.json()
            
            # Add repository info
            pr_data["repository"] = f"{owner}/{repo}"
            pr_data["head_branch"] = pr_data["head"]["ref"]
            pr_data["base_branch"] = pr_data["base"]["ref"]
            
            return {
                "success": True,
                "pull_request": pr_data
            }
            
        except Exception as e:
            error_msg = f"Failed to get pull request details: {e}"
            print(f"❌ {error_msg}")
            return {"success": False, "error": error_msg}
    
    def get_pull_request_files(self, owner, repo, pr_number):
        """Get files changed in a pull request."""
        try:
            url = f"{self.api_base}/repos/{owner}/{repo}/pulls/{pr_number}/files"
            
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            files = response.json()
            
            return {
                "success": True,
                "files": files,
                "total_count": len(files)
            }
            
        except Exception as e:
            error_msg = f"Failed to get pull request files: {e}"
            print(f"❌ {error_msg}")
            return {"success": False, "error": error_msg}
    
    def get_pull_request_commits(self, owner, repo, pr_number):
        """Get commits in a pull request."""
        try:
            url = f"{self.api_base}/repos/{owner}/{repo}/pulls/{pr_number}/commits"
            
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            commits = response.json()
            
            return {
                "success": True,
                "commits": commits,
                "total_count": len(commits)
            }
            
        except Exception as e:
            error_msg = f"Failed to get pull request commits: {e}"
            print(f"❌ {error_msg}")
            return {"success": False, "error": error_msg}
    
    def create_pull_request_comment(self, owner, repo, pr_number, comment, line=None, file=None):
        """Create a comment on a pull request."""
        try:
            url = f"{self.api_base}/repos/{owner}/{repo}/pulls/{pr_number}/comments"
            
            data = {
                "body": comment
            }
            
            if line and file:
                data["line"] = line
                data["path"] = file
            
            response = requests.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            
            comment_data = response.json()
            
            return {
                "success": True,
                "comment": comment_data
            }
            
        except Exception as e:
            error_msg = f"Failed to create pull request comment: {e}"
            print(f"❌ {error_msg}")
            return {"success": False, "error": error_msg}
    
    def create_pull_request_review(self, owner, repo, pr_number, event, body, comments=None, commit_sha=None):
        """Create a review on a pull request."""
        try:
            url = f"{self.api_base}/repos/{owner}/{repo}/pulls/{pr_number}/reviews"
            
            data = {
                "event": event,
                "body": body
            }
            
            if comments:
                data["comments"] = comments
            
            if commit_sha:
                data["commit_id"] = commit_sha
            
            response = requests.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            
            review_data = response.json()
            
            return {
                "success": True,
                "review": review_data
            }
            
        except Exception as e:
            error_msg = f"Failed to create pull request review: {e}"
            print(f"❌ {error_msg}")
            return {"success": False, "error": error_msg}

# Global instance
github_reviewer = GitHubCodeReviewer() 