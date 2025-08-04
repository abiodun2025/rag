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
        
        return issues
    
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
    
    def review_and_comment_pr(self, owner: str, repo: str, pr_number: int, auto_comment: bool = True, output_file: str = None) -> Dict[str, Any]:
        """Review a pull request and optionally add comments."""
        try:
            print(f"🔍 Starting PR review with comments for: {owner}/{repo}#{pr_number}")
            
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
            
            # Analyze each changed file
            analysis_results = []
            total_issues = 0
            total_score = 100
            
            for file_info in files:
                if file_info['filename'].endswith('.py'):
                    # Get the diff for this file
                    file_diff = self._extract_file_diff_from_files(file_info)
                    
                    if file_diff:
                        # Analyze the diff content
                        analysis = self._analyze_diff_content(file_diff, file_info['filename'])
                        analysis_results.append({
                            'file': file_info['filename'],
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
            
            # Create line-specific comments if auto_comment is enabled
            comments_added = 0
            review_url = None
            
            if auto_comment:
                # Add line-specific comments for each issue found
                for analysis_result in analysis_results:
                    file_analysis = analysis_result['analysis']
                    filename = analysis_result['file']
                    
                    if file_analysis.get('issues'):
                        for issue in file_analysis['issues']:
                            line_number = issue.get('line')
                            if line_number:
                                # Create line-specific comment
                                comment_body = f"**{issue.get('category', 'Issue').title()}**: {issue.get('message', '')}\n\n**Suggestion**: {issue.get('suggestion', '')}"
                                
                                comment_result = self.create_pull_request_comment(
                                    owner, repo, pr_number, comment_body, line_number, filename
                                )
                                
                                if comment_result["success"]:
                                    comments_added += 1
                                    print(f"✅ Line {line_number} comment added for {filename}")
                                else:
                                    print(f"⚠️  Failed to add line {line_number} comment: {comment_result['error']}")
                
                # Also create a general review summary
                review_result = self.create_pull_request_review(
                    owner, repo, pr_number, "COMMENT", review_summary
                )
                
                if review_result["success"]:
                    review_url = review_result["review"]["html_url"]
                    print(f"✅ Review summary added successfully!")
                    print(f"🔗 Review URL: {review_url}")
                else:
                    print(f"⚠️  Failed to add review summary: {review_result['error']}")
            
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
    
    def create_pull_request_review(self, owner, repo, pr_number, event, body, comments=None):
        """Create a review on a pull request."""
        try:
            url = f"{self.api_base}/repos/{owner}/{repo}/pulls/{pr_number}/reviews"
            
            data = {
                "event": event,
                "body": body
            }
            
            if comments:
                data["comments"] = comments
            
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