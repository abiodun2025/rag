#!/usr/bin/env python3
"""
GitHub Code Review CLI
=====================

A command-line interface for reviewing GitHub repositories and pull requests.
"""

import sys
import os
import json
from datetime import datetime
from typing import Dict, Any

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.github_code_reviewer import github_reviewer

class GitHubReviewCLI:
    """Command-line interface for GitHub code review."""
    
    def __init__(self):
        self.reviewer = github_reviewer
    
    def print_banner(self):
        """Print the application banner."""
        print("=" * 70)
        print("🔍 GitHub Code Review CLI")
        print("=" * 70)
        print("Review GitHub repositories and pull requests with AI-powered analysis")
        print("Type 'help' for commands or 'exit' to quit")
        print("=" * 70)
    
    def print_help(self):
        """Print help information."""
        print("\n🔍 GitHub Code Review Commands:")
        print("-" * 40)
        print("connect [token]                      - Connect to GitHub with token")
        print("test                                 - Test GitHub connection")
        print("repos [username]                     - List repositories")
        print("analyze [owner/repo]                 - Analyze entire repository")
        print("analyze [owner] [repo]               - Analyze repository (separate)")
        print("file [owner/repo] [path]             - Review specific file")
        print("pr [owner/repo] [number]             - Review pull request")
        print("clone [owner/repo]                   - Clone and analyze locally")
        print("cleanup [path]                       - Clean up cloned repository")
        print("\n🔧 Setup:")
        print("1. Get GitHub token from: https://github.com/settings/tokens")
        print("2. Set environment variable: export GITHUB_TOKEN=your_token")
        print("3. Or use: connect your_token")
        print("\n💡 Examples:")
        print("connect ghp_1234567890abcdef")
        print("test")
        print("repos octocat")
        print("analyze facebook/react")
        print("analyze https://github.com/facebook/react")
        print("analyze microsoft vscode")
        print("file facebook/react src/index.js")
        print("pr facebook/react 12345")
        print("clone tensorflow/tensorflow")
        print("\n📊 Analysis Features:")
        print("- Security vulnerabilities")
        print("- Performance optimizations")
        print("- Code style and formatting")
        print("- Architecture patterns")
        print("- Best practices")
        print("- Pull request review")
        print("- Repository-wide analysis")
    
    def setup_github_token(self, token: str = None):
        """Setup GitHub token."""
        if token:
            os.environ['GITHUB_TOKEN'] = token
            # Reinitialize the reviewer with new token
            from agent.github_code_reviewer import GitHubCodeReviewer
            self.reviewer = GitHubCodeReviewer(token)
            return True
        else:
            token = os.getenv('GITHUB_TOKEN')
            if token:
                return True
            else:
                print("❌ No GitHub token found.")
                print("💡 Set GITHUB_TOKEN environment variable or use 'connect [token]'")
                return False
    
    def test_connection(self) -> Dict[str, Any]:
        """Test GitHub connection."""
        if not self.setup_github_token():
            return {"success": False, "error": "No GitHub token"}
        
        try:
            print("🔍 Testing GitHub connection...")
            result = self.reviewer.test_connection()
            return result
        except Exception as e:
            return {
                "success": False,
                "error": f"Connection test failed: {str(e)}"
            }
    
    def list_repositories(self, username: str = None) -> Dict[str, Any]:
        """List repositories for a user."""
        if not self.setup_github_token():
            return {"success": False, "error": "No GitHub token"}
        
        try:
            print(f"🔍 Fetching repositories{' for ' + username if username else ''}...")
            result = self.reviewer.get_repositories(username)
            return result
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to fetch repositories: {str(e)}"
            }
    
    def analyze_repository(self, owner: str, repo: str, clone_locally: bool = True) -> Dict[str, Any]:
        """Analyze a repository."""
        if not self.setup_github_token():
            return {"success": False, "error": "No GitHub token"}
        
        try:
            print(f"🔍 Analyzing repository: {owner}/{repo}")
            print(f"📥 Clone locally: {clone_locally}")
            
            result = self.reviewer.analyze_repository(owner, repo, clone_locally)
            return result
        except Exception as e:
            return {
                "success": False,
                "error": f"Repository analysis failed: {str(e)}"
            }
    
    def review_file(self, owner: str, repo: str, path: str) -> Dict[str, Any]:
        """Review a specific file."""
        if not self.setup_github_token():
            return {"success": False, "error": "No GitHub token"}
        
        try:
            print(f"🔍 Reviewing file: {owner}/{repo}/{path}")
            
            result = self.reviewer.get_file_content(owner, repo, path)
            if result["success"]:
                from agent.code_reviewer import code_reviewer
                report = code_reviewer.generate_report(result["content"], result["filename"])
                return {
                    "success": True,
                    "file_info": result,
                    "report": report
                }
            else:
                return result
        except Exception as e:
            return {
                "success": False,
                "error": f"File review failed: {str(e)}"
            }
    
    def review_pull_request(self, owner: str, repo: str, pr_number: int) -> Dict[str, Any]:
        """Review a pull request."""
        if not self.setup_github_token():
            return {"success": False, "error": "No GitHub token"}
        
        try:
            print(f"🔍 Reviewing pull request: {owner}/{repo}#{pr_number}")
            
            result = self.reviewer.review_pull_request(owner, repo, pr_number)
            return result
        except Exception as e:
            return {
                "success": False,
                "error": f"Pull request review failed: {str(e)}"
            }
    
    def display_connection_test(self, result: Dict[str, Any]):
        """Display connection test results."""
        if result["success"]:
            print(f"✅ GitHub connection successful!")
            print(f"👤 User: {result.get('user', 'Unknown')}")
            print(f"📝 Name: {result.get('name', 'Unknown')}")
            print(f"📧 Email: {result.get('email', 'Unknown')}")
        else:
            print(f"❌ Connection failed: {result.get('error', 'Unknown error')}")
    
    def display_repositories(self, result: Dict[str, Any]):
        """Display repository list."""
        if result["success"]:
            repos = result["repositories"]
            print(f"📚 Found {len(repos)} repositories:")
            print("-" * 50)
            
            for repo in repos[:10]:  # Show first 10
                print(f"📦 {repo['full_name']}")
                print(f"   Description: {repo.get('description', 'No description')}")
                print(f"   Language: {repo.get('language', 'Unknown')}")
                print(f"   Private: {repo.get('private', False)}")
                print(f"   URL: {repo.get('url', 'N/A')}")
                print()
            
            if len(repos) > 10:
                print(f"... and {len(repos) - 10} more repositories")
        else:
            print(f"❌ Failed to fetch repositories: {result.get('error', 'Unknown error')}")
    
    def display_repository_analysis(self, result: Dict[str, Any]):
        """Display repository analysis results."""
        if result["success"]:
            summary = result["summary"]
            print(f"✅ Repository analysis completed!")
            print("=" * 60)
            print(f"📦 Repository: {result['repository']}")
            print(f"📁 Total files: {summary.get('total_files', 0)}")
            print(f"✅ Successful reviews: {summary.get('successful_reviews', 0)}")
            print(f"🚨 Total issues: {summary.get('total_issues', 0)}")
            print(f"📈 Average score: {summary.get('average_score', 0)}/100")
            
            if 'local_path' in result:
                print(f"📂 Local path: {result['local_path']}")
                print("💡 Use 'cleanup [path]' to remove cloned repository")
            
            # Show top issues
            results = result.get("results", [])
            if results:
                print(f"\n🚨 Top Issues Found:")
                all_issues = []
                for file_result in results:
                    if 'report' in file_result:
                        report = file_result['report']
                        issues = report.get('issues', {}).get('details', [])
                        for issue in issues:
                            all_issues.append({
                                'file': file_result['file'],
                                'line': issue.get('line', 'N/A'),
                                'severity': issue.get('severity', 'unknown'),
                                'message': issue.get('message', ''),
                                'category': issue.get('category', 'unknown')
                            })
                
                # Sort by severity
                severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3, 'info': 4}
                all_issues.sort(key=lambda x: severity_order.get(x['severity'], 5))
                
                for issue in all_issues[:10]:  # Show top 10
                    severity_emoji = {
                        'critical': '🔴',
                        'high': '🟠',
                        'medium': '🟡',
                        'low': '🟢',
                        'info': 'ℹ️'
                    }.get(issue['severity'], 'ℹ️')
                    
                    print(f"   {severity_emoji} {issue['file']}:{issue['line']} - {issue['message']}")
        else:
            print(f"❌ Analysis failed: {result.get('error', 'Unknown error')}")
    
    def display_file_review(self, result: Dict[str, Any]):
        """Display file review results."""
        if result["success"]:
            file_info = result["file_info"]
            report = result["report"]
            
            print(f"✅ File review completed!")
            print("=" * 50)
            print(f"📄 File: {file_info['filename']}")
            print(f"📁 Path: {file_info['path']}")
            print(f"📏 Size: {file_info['size']} bytes")
            print(f"📈 Score: {report['score']}/100 ({report['grade']})")
            
            issues = report.get('issues', {})
            print(f"🚨 Issues: {issues.get('total', 0)} total")
            print(f"   🔴 Critical: {issues.get('critical', 0)}")
            print(f"   🟠 High: {issues.get('high', 0)}")
            print(f"   🟡 Medium: {issues.get('medium', 0)}")
            print(f"   🟢 Low: {issues.get('low', 0)}")
            
            # Show critical and high issues
            issue_details = issues.get('details', [])
            critical_high = [i for i in issue_details if i.get('severity') in ['critical', 'high']]
            
            if critical_high:
                print(f"\n🚨 Critical & High Issues:")
                for issue in critical_high:
                    severity_emoji = "🔴" if issue.get('severity') == 'critical' else "🟠"
                    print(f"   {severity_emoji} Line {issue.get('line', 'N/A')}: {issue.get('message', '')}")
        else:
            print(f"❌ File review failed: {result.get('error', 'Unknown error')}")
    
    def display_pull_request_review(self, result: Dict[str, Any]):
        """Display pull request review results."""
        if result["success"]:
            pr_info = result["pull_request"]
            print(f"✅ Pull request review completed!")
            print("=" * 60)
            print(f"🔀 PR #{pr_info['number']}: {pr_info['title']}")
            print(f"👤 Author: {pr_info['author']}")
            print(f"📊 State: {pr_info['state']}")
            print(f"📁 Changed files: {pr_info['changed_files']}")
            
            results = result.get("results", [])
            if results:
                print(f"\n📊 Review Results:")
                total_issues = 0
                for file_result in results:
                    report = file_result.get('report', {})
                    issues = report.get('issues', {}).get('total', 0)
                    total_issues += issues
                    
                    print(f"   📄 {file_result['file']}")
                    print(f"      Status: {file_result.get('status', 'N/A')}")
                    print(f"      Additions: +{file_result.get('additions', 0)}")
                    print(f"      Deletions: -{file_result.get('deletions', 0)}")
                    print(f"      Issues: {issues}")
                    print(f"      Score: {report.get('score', 0)}/100")
                    print()
                
                print(f"📈 Total issues across all files: {total_issues}")
        else:
            print(f"❌ Pull request review failed: {result.get('error', 'Unknown error')}")
    
    def run(self):
        """Run the CLI."""
        
        self.print_banner()
        
        while True:
            try:
                print(f"\n🔍 GitHub Reviewer > ", end="")
                command = input().strip()
                
                if not command:
                    continue
                
                if command.lower() in ['exit', 'quit', 'q']:
                    print("👋 Thank you for using GitHub Code Reviewer!")
                    break
                
                if command.lower() in ['help', 'h', '?']:
                    self.print_help()
                    continue
                
                if command.lower() in ['clear', 'cls']:
                    os.system('clear' if os.name == 'posix' else 'cls')
                    self.print_banner()
                    continue
                
                # Parse command
                parts = command.split()
                if not parts:
                    continue
                
                action = parts[0].lower()
                
                if action == 'connect':
                    if len(parts) < 2:
                        print("❌ Please provide a GitHub token.")
                        print("💡 Example: connect ghp_1234567890abcdef")
                        continue
                    
                    token = parts[1]
                    if self.setup_github_token(token):
                        print("✅ GitHub token set successfully!")
                    else:
                        print("❌ Failed to set GitHub token.")
                
                elif action == 'test':
                    result = self.test_connection()
                    self.display_connection_test(result)
                
                elif action == 'repos':
                    username = parts[1] if len(parts) > 1 else None
                    result = self.list_repositories(username)
                    self.display_repositories(result)
                
                elif action == 'analyze':
                    if len(parts) < 2:
                        print("❌ Please specify a repository to analyze.")
                        print("💡 Example: analyze facebook/react")
                        continue
                    
                    repo_arg = parts[1]
                    
                    # Handle full GitHub URLs
                    if repo_arg.startswith('https://github.com/'):
                        repo_arg = repo_arg.replace('https://github.com/', '').split('/')[0] + '/' + repo_arg.replace('https://github.com/', '').split('/')[1]
                    elif repo_arg.startswith('http://github.com/'):
                        repo_arg = repo_arg.replace('http://github.com/', '').split('/')[0] + '/' + repo_arg.replace('http://github.com/', '').split('/')[1]
                    
                    if '/' in repo_arg:
                        owner, repo = repo_arg.split('/', 1)
                    elif len(parts) > 2:
                        owner = repo_arg
                        repo = parts[2]
                    else:
                        print("❌ Please specify repository as 'owner/repo' or 'owner repo'")
                        continue
                    
                    clone_locally = True
                    if len(parts) > 3 and parts[3] == '--api':
                        clone_locally = False
                    
                    result = self.analyze_repository(owner, repo, clone_locally)
                    self.display_repository_analysis(result)
                
                elif action == 'file':
                    if len(parts) < 3:
                        print("❌ Please specify repository and file path.")
                        print("💡 Example: file facebook/react src/index.js")
                        continue
                    
                    repo_arg = parts[1]
                    
                    # Handle full GitHub URLs
                    if repo_arg.startswith('https://github.com/'):
                        repo_arg = repo_arg.replace('https://github.com/', '').split('/')[0] + '/' + repo_arg.replace('https://github.com/', '').split('/')[1]
                    elif repo_arg.startswith('http://github.com/'):
                        repo_arg = repo_arg.replace('http://github.com/', '').split('/')[0] + '/' + repo_arg.replace('http://github.com/', '').split('/')[1]
                    
                    if '/' in repo_arg:
                        owner, repo = repo_arg.split('/', 1)
                    else:
                        print("❌ Please specify repository as 'owner/repo'")
                        continue
                    
                    path = parts[2]
                    result = self.review_file(owner, repo, path)
                    self.display_file_review(result)
                
                elif action == 'pr':
                    if len(parts) < 3:
                        print("❌ Please specify repository and PR number.")
                        print("💡 Example: pr facebook/react 12345")
                        continue
                    
                    repo_arg = parts[1]
                    
                    # Handle full GitHub URLs
                    if repo_arg.startswith('https://github.com/'):
                        repo_arg = repo_arg.replace('https://github.com/', '').split('/')[0] + '/' + repo_arg.replace('https://github.com/', '').split('/')[1]
                    elif repo_arg.startswith('http://github.com/'):
                        repo_arg = repo_arg.replace('http://github.com/', '').split('/')[0] + '/' + repo_arg.replace('http://github.com/', '').split('/')[1]
                    
                    if '/' in repo_arg:
                        owner, repo = repo_arg.split('/', 1)
                    else:
                        print("❌ Please specify repository as 'owner/repo'")
                        continue
                    
                    try:
                        pr_number = int(parts[2])
                    except ValueError:
                        print("❌ PR number must be an integer.")
                        continue
                    
                    result = self.review_pull_request(owner, repo, pr_number)
                    self.display_pull_request_review(result)
                
                elif action == 'clone':
                    if len(parts) < 2:
                        print("❌ Please specify a repository to clone.")
                        print("💡 Example: clone facebook/react")
                        continue
                    
                    repo_arg = parts[1]
                    
                    # Handle full GitHub URLs
                    if repo_arg.startswith('https://github.com/'):
                        repo_arg = repo_arg.replace('https://github.com/', '').split('/')[0] + '/' + repo_arg.replace('https://github.com/', '').split('/')[1]
                    elif repo_arg.startswith('http://github.com/'):
                        repo_arg = repo_arg.replace('http://github.com/', '').split('/')[0] + '/' + repo_arg.replace('http://github.com/', '').split('/')[1]
                    
                    if '/' in repo_arg:
                        owner, repo = repo_arg.split('/', 1)
                    else:
                        print("❌ Please specify repository as 'owner/repo'")
                        continue
                    
                    result = self.analyze_repository(owner, repo, clone_locally=True)
                    self.display_repository_analysis(result)
                
                elif action == 'cleanup':
                    if len(parts) < 2:
                        print("❌ Please specify a path to clean up.")
                        continue
                    
                    path = parts[1]
                    if self.reviewer.cleanup_local_repository(path):
                        print(f"✅ Cleaned up: {path}")
                    else:
                        print(f"❌ Failed to clean up: {path}")
                
                else:
                    print(f"❌ Unknown command: {action}")
                    print("💡 Type 'help' for available commands")
                
            except KeyboardInterrupt:
                print("\n\n👋 Thank you for using GitHub Code Reviewer!")
                break
            except Exception as e:
                print(f"\n❌ Unexpected error: {e}")
                print("💡 Type 'help' for available commands")

def main():
    """Main function."""
    
    cli = GitHubReviewCLI()
    cli.run()

if __name__ == "__main__":
    main() 