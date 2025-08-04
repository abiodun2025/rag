#!/usr/bin/env python3
"""
GitHub Code Review Agent CLI
============================

A dedicated command-line interface for reviewing GitHub repositories.
Enhanced with full GitHub access, repository management, and PR commenting.
Version: 1.4.0
"""

import sys
import os
import asyncio
import argparse
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from github_review_agent import GitHubReviewAgent

class CodeReviewCLI:
    """Command-line interface for GitHub code review."""
    
    def __init__(self):
        self.agent = GitHubReviewAgent()
        self.version = "1.4.0"
    
    def print_banner(self):
        """Print the CLI banner."""
        print("=" * 60)
        print("🔍 GitHub Code Review Agent CLI")
        print("=" * 60)
        print("Review any GitHub repository with comprehensive analysis!")
        print("Type 'help' for commands or 'exit' to quit")
        print("=" * 60)
    
    def print_help(self):
        """Print help information."""
        print("\n📋 Available Commands:")
        print("  review <repo_url> [options]           - Review a GitHub repository")
        print("  list-repos [--public-only]            - List all your repositories")
        print("  list-branches <repo>                  - List branches for a repository")
        print("  review-all [options]                  - Review all your repositories")
        print("  review-pr <owner/repo> <pr#>          - Review a specific pull request")
        print("  review-commits <owner/repo> <pr#>     - Review each commit in a PR individually")
        print("  review-commit <owner/repo> <sha>      - Review a specific commit")
        print("  comment-pr <owner/repo> <pr#> [options] - Review and comment on PR")
        print("  add-comment <owner/repo> <pr#> <comment> - Add a single comment to PR")
        print("  list-prs [options]                    - List all accessible pull requests")
        print("  select-pr                             - Interactive PR selection and commenting")
        print("  comment-all-prs [options]             - Comment on all accessible pull requests")
        print("  test-connection                       - Test GitHub connection")
        print("  help                                  - Show this help")
        print("  version                               - Show version information")
        print("  exit                                  - Exit the CLI")
        print("\n📝 Examples:")
        print("  review https://github.com/owner/repo")
        print("  review https://github.com/owner/repo --type security")
        print("  review https://github.com/owner/repo --format detailed")
        print("  review https://github.com/owner/repo --no-clone")
        print("  list-repos")
        print("  list-repos --public-only")
        print("  list-branches owner/repo")
        print("  review-all --type security")
        print("  review-pr owner/repo 123")
        print("  review-commits owner/repo 123")
        print("  review-commit owner/repo abc123def")
        print("  comment-pr owner/repo 123 --auto-comment")
        print("  comment-pr owner/repo 123 --no-auto-comment")
        print("  add-comment owner/repo 123 \"Great work on this feature!\"")
        print("  list-prs --state open")
        print("  list-prs --state closed")
        print("  select-pr")
        print("  comment-all-prs")
        print("  comment-all-prs --state open")
        print("  comment-all-prs --public-only")
        print("\n🔧 Review Options:")
        print("  --type <type>               - Review type: full, security, performance, style")
        print("  --format <format>           - Output format: summary, detailed, json")
        print("  --no-clone                  - Don't clone locally (faster but less thorough)")
        print("  --output <filename>         - Custom output filename (saves to Downloads folder)")
        print("  --branch <branch>           - Review specific branch")
        print("\n🔧 PR Commenting Options:")
        print("  --auto-comment              - Automatically add line-specific comments (default)")
        print("  --no-auto-comment           - Don't add automatic comments")
        print("  --line <line_number>        - Specify line for single comment")
        print("  --file <file_path>          - Specify file for single comment")
        print("\n💡 Tips:")
        print("  • Reports are automatically saved to your Downloads folder")
        print("  • Use '--no-clone' for faster analysis of public repositories")
        print("  • Security reviews focus on vulnerabilities and best practices")
        print("  • Performance reviews analyze code efficiency and optimization")
        print("  • Set GITHUB_TOKEN environment variable for private repository access")
        print("  • PR comments are automatically formatted with severity levels")
        print("  • Line-specific comments appear directly on the code in GitHub")
        print("  • Commit-by-commit review analyzes each commit's changes individually")
        print("  • Use review-commits for detailed analysis of PR history")
    
    def parse_command(self, command: str):
        """Parse user command."""
        parts = command.strip().split()
        if not parts:
            return None, {}
        
        cmd = parts[0].lower()
        args = parts[1:]
        
        if cmd == "review":
            return self.parse_review_command(args)
        elif cmd == "list-repos":
            return self.parse_list_repos_command(args)
        elif cmd == "list-branches":
            return self.parse_list_branches_command(args)
        elif cmd == "review-all":
            return self.parse_review_all_command(args)
        elif cmd == "review-pr":
            return self.parse_review_pr_command(args)
        elif cmd == "review-commits":
            return self.parse_review_commits_command(args)
        elif cmd == "review-commit":
            return self.parse_review_commit_command(args)
        elif cmd == "comment-pr":
            return self.parse_comment_pr_command(args)
        elif cmd == "add-comment":
            return self.parse_add_comment_command(args)
        elif cmd == "list-prs":
            return self.parse_list_prs_command(args)
        elif cmd == "select-pr":
            return "select_pr", {}
        elif cmd == "comment-all-prs":
            return self.parse_comment_all_prs_command(args)
        elif cmd == "test-connection":
            return "test_connection", {}
        elif cmd == "help":
            return "help", {}
        elif cmd == "exit":
            return "exit", {}
        else:
            return "unknown", {"command": cmd}
    
    def parse_review_command(self, args):
        """Parse review command arguments."""
        if not args:
            return "error", {"message": "Please provide a repository URL"}
        
        repo_url = args[0]
        options = {}
        
        # Parse additional options
        i = 1
        while i < len(args):
            if args[i] == "--type" and i + 1 < len(args):
                options["review_type"] = args[i + 1]
                i += 2
            elif args[i] == "--format" and i + 1 < len(args):
                options["output_format"] = args[i + 1]
                i += 2
            elif args[i] == "--output" and i + 1 < len(args):
                options["output_file"] = args[i + 1]
                i += 2
            elif args[i] == "--no-clone":
                options["clone_locally"] = False
                i += 1
            else:
                i += 1
        
        return "review", {"repo_url": repo_url, **options}
    
    def parse_list_repos_command(self, args):
        """Parse list-repos command arguments."""
        options = {"include_private": True}
        
        i = 0
        while i < len(args):
            if args[i] == "--public-only":
                options["include_private"] = False
                i += 1
            else:
                return "error", {"message": f"Unknown option: {args[i]}"}
        
        return "list_repos", options
    
    def parse_list_branches_command(self, args):
        """Parse list-branches command arguments."""
        if not args:
            return "error", {"message": "Repository name required (format: owner/repo)"}
        
        repo_name = args[0]
        if "/" not in repo_name:
            return "error", {"message": "Repository must be in format: owner/repo"}
        
        owner, repo = repo_name.split("/", 1)
        return "list_branches", {"owner": owner, "repo": repo}
    
    def parse_review_all_command(self, args):
        """Parse review-all command arguments."""
        options = {
            "review_type": "full",
            "output_format": "summary",
            "clone_locally": True,
            "include_private": True
        }
        
        i = 0
        while i < len(args):
            if args[i] == "--type" and i + 1 < len(args):
                options["review_type"] = args[i + 1]
                i += 2
            elif args[i] == "--format" and i + 1 < len(args):
                options["output_format"] = args[i + 1]
                i += 2
            elif args[i] == "--no-clone":
                options["clone_locally"] = False
                i += 1
            elif args[i] == "--public-only":
                options["include_private"] = False
                i += 1
            else:
                return "error", {"message": f"Unknown option: {args[i]}"}
        
        return "review_all", options
    
    def parse_review_pr_command(self, args):
        """Parse review-pr command arguments."""
        if len(args) < 2:
            return "error", {"message": "Repository and PR number required (format: owner/repo pr_number)"}
        
        repo_name = args[0]
        if "/" not in repo_name:
            return "error", {"message": "Repository must be in format: owner/repo"}
        
        try:
            pr_number = int(args[1])
        except ValueError:
            return "error", {"message": "PR number must be a valid integer"}
        
        owner, repo = repo_name.split("/", 1)
        options = {
            "owner": owner,
            "repo": repo,
            "pr_number": pr_number,
            "output_file": None
        }
        
        # Check for output file option
        if len(args) > 2 and args[2] == "--output" and len(args) > 3:
            options["output_file"] = args[3]
        
        return "review_pr", options
    
    def parse_review_commits_command(self, args):
        """Parse review-commits command arguments."""
        if len(args) < 2:
            return "error", {"message": "Repository and PR number required (format: owner/repo pr_number)"}
        
        repo_name = args[0]
        if "/" not in repo_name:
            return "error", {"message": "Repository must be in format: owner/repo"}
        
        try:
            pr_number = int(args[1])
        except ValueError:
            return "error", {"message": "PR number must be a valid integer"}
        
        owner, repo = repo_name.split("/", 1)
        return "review_commits", {"owner": owner, "repo": repo, "pr_number": pr_number}
    
    def parse_review_commit_command(self, args):
        """Parse review-commit command arguments."""
        if len(args) < 2:
            return "error", {"message": "Repository and commit SHA required (format: owner/repo sha)"}
        
        repo_name = args[0]
        if "/" not in repo_name:
            return "error", {"message": "Repository must be in format: owner/repo"}
        
        sha = args[1]
        owner, repo = repo_name.split("/", 1)
        return "review_commit", {"owner": owner, "repo": repo, "sha": sha}
    
    def parse_comment_pr_command(self, args):
        """Parse comment-pr command arguments."""
        if len(args) < 2:
            return "error", {"message": "Repository and PR number required (format: owner/repo pr_number)"}
        
        repo_name = args[0]
        if "/" not in repo_name:
            return "error", {"message": "Repository must be in format: owner/repo"}
        
        try:
            pr_number = int(args[1])
        except ValueError:
            return "error", {"message": "PR number must be a valid integer"}
        
        owner, repo = repo_name.split("/", 1)
        options = {
            "owner": owner,
            "repo": repo,
            "pr_number": pr_number,
            "auto_comment": True,
            "output_file": None
        }
        
        # Parse additional options
        i = 2
        while i < len(args):
            if args[i] == "--auto-comment":
                options["auto_comment"] = True
                i += 1
            elif args[i] == "--no-auto-comment":
                options["auto_comment"] = False
                i += 1
            elif args[i] == "--output" and i + 1 < len(args):
                options["output_file"] = args[i + 1]
                i += 2
            else:
                return "error", {"message": f"Unknown option: {args[i]}"}
        
        return "comment_pr", options
    
    def parse_add_comment_command(self, args):
        """Parse add-comment command arguments."""
        if len(args) < 3:
            return "error", {"message": "Repository, PR number, and comment required (format: owner/repo pr_number \"comment\")"}
        
        repo_name = args[0]
        if "/" not in repo_name:
            return "error", {"message": "Repository must be in format: owner/repo"}
        
        try:
            pr_number = int(args[1])
        except ValueError:
            return "error", {"message": "PR number must be a valid integer"}
        
        # Extract comment (everything after the first two arguments)
        comment = " ".join(args[2:])
        if not comment:
            return "error", {"message": "Comment text is required"}
        
        owner, repo = repo_name.split("/", 1)
        options = {
            "owner": owner,
            "repo": repo,
            "pr_number": pr_number,
            "comment": comment,
            "line": None,
            "file": None
        }
        
        return "add_comment", options
    
    def parse_list_prs_command(self, args):
        """Parse list-prs command arguments."""
        options = {
            "state": "open",
            "include_private": True
        }
        
        i = 0
        while i < len(args):
            if args[i] == "--state" and i + 1 < len(args):
                state = args[i + 1].lower()
                if state in ["open", "closed", "all"]:
                    options["state"] = state
                else:
                    return "error", {"message": "State must be 'open', 'closed', or 'all'"}
                i += 2
            elif args[i] == "--public-only":
                options["include_private"] = False
                i += 1
            else:
                return "error", {"message": f"Unknown option: {args[i]}"}
        
        return "list_prs", options
    
    def parse_comment_all_prs_command(self, args):
        """Parse comment-all-prs command arguments."""
        options = {
            "state": "open",
            "include_private": True,
            "auto_comment": True
        }
        
        i = 0
        while i < len(args):
            if args[i] == "--state" and i + 1 < len(args):
                state = args[i + 1].lower()
                if state in ["open", "closed", "all"]:
                    options["state"] = state
                else:
                    return "error", {"message": "State must be 'open', 'closed', or 'all'"}
                i += 2
            elif args[i] == "--public-only":
                options["include_private"] = False
                i += 1
            elif args[i] == "--no-auto-comment":
                options["auto_comment"] = False
                i += 1
            else:
                return "error", {"message": f"Unknown option: {args[i]}"}
        
        return "comment_all_prs", options
    
    async def execute_review(self, repo_url: str, options: dict) -> bool:
        """Execute the review command."""
        print(f"\n🔍 Starting code review for: {repo_url}")
        print("⏳ This may take a few minutes...")
        
        try:
            # Set default options
            review_type = options.get("review_type", "full")
            output_format = options.get("output_format", "summary")
            clone_locally = options.get("clone_locally", True)
            output_file = options.get("output_file")
            
            # Generate default output filename if not provided
            if not output_file:
                repo_name = repo_url.replace('https://github.com/', '').replace('/', '_')
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = f"code_review_{repo_name}_{timestamp}.json"
                # This will be automatically saved to Downloads folder by the agent
            
            print(f"📊 Review type: {review_type}")
            print(f"📄 Output format: {output_format}")
            print(f"💾 Output file: {output_file}")
            print(f"📁 Clone locally: {clone_locally}")
            
            # Execute the review
            report = self.agent.review_repository(
                repo_url=repo_url,
                output_file=output_file,
                clone_locally=clone_locally
            )
            
            if report["success"]:
                print("\n✅ Code review completed successfully!")
                self.agent.print_report_summary(report)
                
                # Clean up local repository if it was cloned
                if report.get("local_path"):
                    self.agent.cleanup_local_repository(report["local_path"])
                    print("🧹 Local repository cleaned up")
                
                return True
            else:
                print(f"\n❌ Code review failed: {report.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"\n❌ Error during code review: {str(e)}")
            return False
    
    async def execute_list_repos(self, args):
        """Execute list repositories command."""
        try:
            print("🔍 Fetching repositories...")
            
            include_private = True
            if len(args) > 0 and args[0] == "--public-only":
                include_private = False
            
            result = self.agent.list_user_repositories(include_private=include_private)
            
            if result["success"]:
                repos = result.get("repositories", [])
                if repos is None:
                    repos = []
                
                print(f"\n📊 Found {len(repos)} repositories:")
                print("-" * 60)
                
                if repos:
                    for i, repo in enumerate(repos, 1):
                        print(f"{i:2d}. {repo.get('name', 'Unknown')}")
                        print(f"     📁 {repo.get('private', 'Public')}")
                        print(f"     🔗 {repo.get('html_url', 'N/A')}")
                        print()
                else:
                    print("📭 No repositories found.")
                
                return True
            else:
                print(f"❌ Failed to list repositories: {result.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"❌ Failed to list repositories: {e}")
            return False
    
    async def execute_list_branches(self, owner: str, repo: str) -> bool:
        """Execute list branches command."""
        try:
            print(f"🌿 Fetching branches for {owner}/{repo}...")
            
            result = self.agent.list_repository_branches(owner, repo)
            
            # Debug: Print the raw result
            print(f"🔍 Debug: Result type: {type(result)}")
            print(f"🔍 Debug: Result keys: {result.keys() if result else 'None'}")
            print(f"🔍 Debug: Success: {result.get('success') if result else 'None'}")
            print(f"🔍 Debug: Branches type: {type(result.get('branches')) if result else 'None'}")
            print(f"🔍 Debug: Branches length: {len(result.get('branches', [])) if result and result.get('branches') else 'None'}")
            
            if result and result.get("success"):
                branches = result.get("branches", [])
                if branches is None:
                    branches = []
                
                print(f"\n📊 Found {len(branches)} branches:")
                print("-" * 60)
                
                if branches:
                    for i, branch in enumerate(branches, 1):
                        print(f"🔍 Debug: Branch {i}: {branch}")
                        protected = "🔒" if branch.get("protected", False) else "🔓"
                        commit_info = branch.get("commit", {})
                        commit_msg = commit_info.get("message", "No message")
                        
                        # Handle None commit message
                        if commit_msg is None:
                            commit_msg = "No commit message"
                        else:
                            commit_msg = commit_msg[:50] + "..." if len(commit_msg) > 50 else commit_msg
                        
                        print(f"{i:2d}. {protected} {branch.get('name', 'Unknown')}")
                        print(f"     📝 {commit_msg}")
                        print(f"     📅 {commit_info.get('date', 'Unknown date')}")
                        print()
                else:
                    print("📭 No branches found.")
                
                return True
            else:
                error_msg = result.get('error', 'Unknown error') if result else 'No response from API'
                print(f"❌ Failed to fetch branches: {error_msg}")
                return False
                
        except Exception as e:
            print(f"❌ Failed to list branches: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def execute_review_all(self, options: dict) -> bool:
        """Execute review all repositories command."""
        try:
            print("🔍 Starting review of all your repositories...")
            print("⚠️  This may take a while depending on the number of repositories.")
            
            # Generate output filename if not provided
            if not options.get("output_file"):
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                options["output_file"] = f"all_repos_review_{timestamp}.json"
            
            result = self.agent.review_user_repositories(
                review_type=options["review_type"],
                include_private=options["include_private"],
                output_file=options["output_file"]
            )
            
            if result["success"]:
                self.print_review_all_summary(result)
                return True
            else:
                print(f"❌ Review failed: {result.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"❌ Review failed: {e}")
            return False
    
    async def execute_review_pr(self, owner: str, repo: str, pr_number: int, output_file: str = None) -> bool:
        """Execute PR review."""
        try:
            print(f"🔍 Reviewing PR #{pr_number} in {owner}/{repo}...")
            
            result = self.agent.review_pull_request(owner, repo, pr_number, output_file)
            
            if result["success"]:
                self.print_pr_summary(result)
                return True
            else:
                print(f"❌ PR review failed: {result.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"❌ Error during PR review: {e}")
            return False
    
    async def execute_review_commits(self, owner: str, repo: str, pr_number: int, output_file: str = None) -> bool:
        """Execute commit-by-commit PR review."""
        try:
            print(f"🔍 Starting commit-by-commit review for PR #{pr_number} in {owner}/{repo}...")
            
            result = self.agent.review_pull_request_commits(owner, repo, pr_number, output_file)
            
            if result["success"]:
                self.print_commit_reviews_summary(result)
                return True
            else:
                print(f"❌ PR commits review failed: {result.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"❌ Error during PR commits review: {e}")
            return False
    
    async def execute_review_commit(self, owner: str, repo: str, sha: str, output_file: str = None) -> bool:
        """Execute single commit review."""
        try:
            print(f"🔍 Reviewing commit {sha[:8]} in {owner}/{repo}...")
            
            result = self.agent.review_commit(owner, repo, sha, output_file)
            
            if result["success"]:
                self.print_commit_summary(result)
                return True
            else:
                print(f"❌ Commit review failed: {result.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"❌ Error during commit review: {e}")
            return False
    
    async def execute_comment_pr(self, owner: str, repo: str, pr_number: int, auto_comment: bool = True, output_file: str = None) -> bool:
        """Execute pull request review with comments."""
        try:
            print(f"🔍 Starting PR review with comments for #{pr_number} in {owner}/{repo}...")
            
            # Generate output filename if not provided
            if not output_file:
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = f"pr_comment_review_{owner}_{repo}_{pr_number}_{timestamp}.json"
            
            result = self.agent.review_and_comment_pr(
                owner=owner,
                repo=repo,
                pr_number=pr_number,
                auto_comment=auto_comment,
                output_file=output_file
            )
            
            if result["success"]:
                self.print_pr_comment_summary(result)
                return True
            else:
                print(f"❌ PR review and comment failed: {result.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"❌ PR review and comment failed: {e}")
            return False
    
    async def execute_add_comment(self, owner: str, repo: str, pr_number: int, comment: str, line: int = None, file: str = None) -> bool:
        """Execute add single comment command."""
        try:
            print(f"💬 Adding comment to PR #{pr_number} in {owner}/{repo}...")
            
            result = self.agent.create_pr_comment(
                owner=owner,
                repo=repo,
                pr_number=pr_number,
                comment=comment,
                line=line,
                path=file
            )
            
            if result["success"]:
                print(f"✅ Comment added successfully!")
                print(f"🔗 View comment: {result.get('url', 'N/A')}")
                return True
            else:
                print(f"❌ Failed to add comment: {result.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"❌ Failed to add comment: {e}")
            return False
    
    async def execute_list_prs(self, args):
        """Execute list pull requests command."""
        try:
            print(f"📋 Fetching {args['state']} pull requests...")
            
            result = self.agent.list_all_pull_requests(
                state=args["state"],
                include_private=args["include_private"]
            )
            
            if result["success"]:
                prs = result["pull_requests"]
                print(f"\n📋 Found {len(prs)} {args['state']} pull requests:")
                print("-" * 100)
                
                for i, pr in enumerate(prs, 1):
                    state_emoji = "🟢" if pr["state"] == "open" else "🔴"
                    draft_emoji = "📝" if pr.get("draft", False) else ""
                    repo_visibility = "🔒" if pr.get("repo_private", False) else "🌐"
                    
                    # Handle author field safely
                    author = pr.get('user', {}).get('login', 'Unknown') if pr.get('user') else 'Unknown'
                    
                    print(f"{i:3d}. {state_emoji} {draft_emoji} {repo_visibility} {pr['repository']}#{pr['number']}")
                    print(f"     📝 {pr['title']}")
                    print(f"     👤 {author} | 🌿 {pr['head_branch']} → {pr['base_branch']}")
                    print(f"     📅 Updated: {pr['updated_at']}")
                    print(f"     📁 Files: {pr.get('changed_files', 'N/A')} | 💬 Comments: {pr.get('comments', 'N/A')}")
                    print()
                
                return True
            else:
                print(f"❌ Failed to fetch pull requests: {result.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"❌ Failed to list pull requests: {e}")
            return False
    
    async def execute_select_pr(self) -> bool:
        """Execute interactive PR selection and commenting."""
        try:
            print("🔍 Interactive PR Selection Mode")
            print("=" * 50)
            
            # First, get all open PRs
            print("📋 Fetching open pull requests...")
            result = self.agent.list_all_pull_requests(state="open", include_private=True)
            
            if not result["success"]:
                print(f"❌ Failed to fetch pull requests: {result.get('error', 'Unknown error')}")
                return False
            
            prs = result["pull_requests"]
            if not prs:
                print("📭 No open pull requests found.")
                return True
            
            print(f"\n📊 Found {len(prs)} open pull requests:")
            print("-" * 80)
            
            # Display PRs with selection numbers
            for i, pr in enumerate(prs, 1):
                draft_emoji = "📝" if pr.get("draft", False) else ""
                repo_visibility = "🔒" if pr.get("repo_private", False) else "🌐"
                
                # Handle author field safely
                author = pr.get('user', {}).get('login', 'Unknown') if pr.get('user') else 'Unknown'
                
                print(f"{i:2d}. {draft_emoji} {repo_visibility} {pr['repository']}#{pr['number']}")
                print(f"     📝 {pr['title']}")
                print(f"     👤 {author} | 🌿 {pr['head_branch']} → {pr['base_branch']}")
                print(f"     📅 Updated: {pr['updated_at']}")
                print(f"     📁 Files: {pr.get('changed_files', 'N/A')} | 💬 Comments: {pr.get('comments', 'N/A')}")
                print()
            
            # Get user selection
            while True:
                try:
                    selection = input("🔢 Select a PR number (or 'q' to quit): ").strip()
                    
                    if selection.lower() == 'q':
                        print("👋 Exiting PR selection mode.")
                        return True
                    
                    pr_index = int(selection) - 1
                    if 0 <= pr_index < len(prs):
                        selected_pr = prs[pr_index]
                        break
                    else:
                        print(f"❌ Invalid selection. Please choose a number between 1 and {len(prs)}")
                        
                except ValueError:
                    print("❌ Please enter a valid number or 'q' to quit")
            
            # Show PR details
            print(f"\n📋 Selected: {selected_pr['repository']}#{selected_pr['number']}")
            print(f"📝 Title: {selected_pr['title']}")
            # Handle author field safely
            author = selected_pr.get('user', {}).get('login', 'Unknown') if selected_pr.get('user') else 'Unknown'
            print(f"👤 Author: {author}")
            print(f"🌿 Branch: {selected_pr['head_branch']} → {selected_pr['base_branch']}")
            print(f"📅 Created: {selected_pr['created_at']}")
            print(f"📅 Updated: {selected_pr['updated_at']}")
            print(f"📁 Changed Files: {selected_pr['changed_files']}")
            print(f"💬 Comments: {selected_pr['comments']}")
            print(f"🔗 URL: {selected_pr['html_url']}")
            
            # Ask what action to take
            print("\n🎯 What would you like to do?")
            print("1. Review and comment on this PR")
            print("2. Add a single comment")
            print("3. Just review (no comments)")
            print("4. View PR details")
            print("5. Cancel")
            
            while True:
                action = input("\n🔢 Choose action (1-5): ").strip()
                
                if action == "1":
                    # Review and comment
                    return await self.execute_comment_pr({
                        "owner": selected_pr["repo_owner"],
                        "repo": selected_pr["repo_name"],
                        "pr_number": selected_pr["number"],
                        "auto_comment": True
                    })
                    
                elif action == "2":
                    # Add single comment
                    comment = input("💬 Enter your comment: ").strip()
                    if comment:
                        return await self.execute_add_comment(
                            selected_pr["repo_owner"],
                            selected_pr["repo_name"],
                            selected_pr["number"],
                            comment
                        )
                    else:
                        print("❌ Comment cannot be empty")
                        
                elif action == "3":
                    # Just review
                    return await self.execute_review_pr(
                        selected_pr["repo_owner"],
                        selected_pr["repo_name"],
                        selected_pr["number"]
                    )
                    
                elif action == "4":
                    # View PR details
                    details_result = self.agent.get_pull_request_details(
                        selected_pr["repo_owner"],
                        selected_pr["repo_name"],
                        selected_pr["number"]
                    )
                    
                    if details_result["success"]:
                        pr_details = details_result["pull_request"]
                        print(f"\n📋 PR Details:")
                        print(f"   📝 Body: {pr_details.get('body', 'No description')[:200]}...")
                        print(f"   🏷️  Labels: {', '.join(pr_details.get('labels', []))}")
                        print(f"   👥 Assignees: {', '.join(pr_details.get('assignees', []))}")
                        print(f"   👀 Requested Reviewers: {', '.join(pr_details.get('requested_reviewers', []))}")
                        print(f"   📊 Reviews: {len(pr_details.get('reviews', []))}")
                        print(f"   💬 Comments: {len(pr_details.get('comments', []))}")
                    else:
                        print(f"❌ Failed to get PR details: {details_result.get('error', 'Unknown error')}")
                    
                    # Ask again what to do
                    print("\n🎯 What would you like to do?")
                    print("1. Review and comment on this PR")
                    print("2. Add a single comment")
                    print("3. Just review (no comments)")
                    print("4. View PR details")
                    print("5. Cancel")
                    
                elif action == "5":
                    print("👋 Cancelled.")
                    return True
                    
                else:
                    print("❌ Please choose a number between 1 and 5")
            
        except Exception as e:
            print(f"❌ PR selection failed: {e}")
            return False
    
    async def execute_test_connection(self) -> bool:
        """Execute GitHub connection test."""
        try:
            print("🔐 Testing GitHub connection...")
            
            result = self.agent.test_github_connection()
            
            if result["success"]:
                print(f"✅ Connected successfully!")
                print(f"👤 User: {result['user']}")
                print(f"📛 Name: {result.get('name', 'Not set')}")
                print(f"📧 Email: {result.get('email', 'Not set')}")
                print(f"📊 Public repos: {result.get('public_repos', 0)}")
                print(f"🔒 Private repos: {result.get('private_repos', 0)}")
                return True
            else:
                print(f"❌ Connection failed: {result.get('error', 'Unknown error')}")
                print("💡 Make sure you have set the GITHUB_TOKEN environment variable")
                return False
                
        except Exception as e:
            print(f"❌ Connection test failed: {e}")
            return False
    
    def print_review_summary(self, result: dict):
        """Print a summary of the review results."""
        summary = result.get("summary", {})
        
        print("\n" + "="*80)
        print("🔍 GITHUB REPOSITORY CODE REVIEW REPORT")
        print("="*80)
        print(f"📦 Repository: {result.get('repository', 'Unknown')}")
        print(f"🔗 URL: {result.get('repository_url', 'Unknown')}")
        print(f"🌿 Branch: {result.get('branch', 'default')}")
        print(f"📅 Timestamp: {result.get('timestamp', 'Unknown')}")
        print(f"📊 Overall Grade: {summary.get('overall_grade', 'N/A')} ({summary.get('average_score', 0)}/100)")
        print()
        
        print("📈 SUMMARY STATISTICS:")
        print(f"   📁 Total Files: {summary.get('total_files', 0)}")
        print(f"   ✅ Successful Reviews: {summary.get('successful_reviews', 0)}")
        print(f"   🚨 Total Issues: {summary.get('total_issues', 0)}")
        print(f"   🔴 Critical: {summary.get('critical_issues', 0)}")
        print(f"   🟠 High: {summary.get('high_issues', 0)}")
        print(f"   🟡 Medium: {summary.get('medium_issues', 0)}")
        print(f"   🟢 Low: {summary.get('low_issues', 0)}")
        print()
        
        # Show recommendations
        recommendations = result.get("recommendations", [])
        if recommendations:
            print("🎯 KEY RECOMMENDATIONS:")
            for rec in recommendations:
                print(f"   • {rec}")
            print()
        
        print("="*80)
    
    def print_review_all_summary(self, result: dict):
        """Print a summary of the review all results."""
        summary = result.get("summary", {})
        
        print("\n" + "="*80)
        print("🔍 ALL REPOSITORIES REVIEW REPORT")
        print("="*80)
        print(f"📅 Timestamp: {result.get('timestamp', 'Unknown')}")
        print(f"📊 Overall Grade: {summary.get('overall_grade', 'N/A')} ({summary.get('average_score', 0)}/100)")
        print()
        
        print("📈 SUMMARY STATISTICS:")
        print(f"   📦 Total Repositories: {summary.get('total_repositories', 0)}")
        print(f"   ✅ Successful Reviews: {summary.get('successful_reviews', 0)}")
        print(f"   ❌ Failed Reviews: {summary.get('failed_reviews', 0)}")
        print(f"   🚨 Total Issues: {summary.get('total_issues', 0)}")
        print(f"   🔴 Critical: {summary.get('critical_issues', 0)}")
        print(f"   �� High: {summary.get('high_issues', 0)}")
        print()
        
        # Show top repositories
        top_repos = result.get("top_repositories", [])
        if top_repos:
            print("🏆 TOP REPOSITORIES:")
            for i, repo in enumerate(top_repos[:5], 1):
                repo_name = repo.get("repository", "Unknown")
                score = repo.get("review", {}).get("summary", {}).get("average_score", 0)
                grade = repo.get("review", {}).get("summary", {}).get("overall_grade", "N/A")
                print(f"   {i}. {repo_name} - Grade: {grade} ({score}/100)")
            print()
        
        print("="*80)
    
    def print_pr_summary(self, result: dict):
        """Print a summary of the PR review results."""
        summary = result.get("summary", {})
        
        print("\n" + "="*80)
        print("🔍 PULL REQUEST REVIEW REPORT")
        print("="*80)
        print(f"📦 Repository: {result.get('repository', 'Unknown')}")
        print(f"🔢 PR Number: #{result.get('pr_number', 'Unknown')}")
        print(f"📝 Title: {result.get('pr_title', 'Unknown')}")
        print(f"👤 Author: {result.get('pr_author', 'Unknown')}")
        print(f"📊 State: {result.get('pr_state', 'Unknown')}")
        print(f"📅 Timestamp: {result.get('timestamp', 'Unknown')}")
        print(f"📊 Overall Grade: {summary.get('overall_grade', 'N/A')} ({summary.get('average_score', 0)}/100)")
        print()
        
        print("📈 SUMMARY STATISTICS:")
        print(f"   📁 Changed Files: {result.get('changed_files', 0)}")
        print(f"   🚨 Total Issues: {summary.get('total_issues', 0)}")
        print(f"   🔴 Critical: {summary.get('critical_issues', 0)}")
        print(f"   🟠 High: {summary.get('high_issues', 0)}")
        print(f"   🟡 Medium: {summary.get('medium_issues', 0)}")
        print(f"   🟢 Low: {summary.get('low_issues', 0)}")
        print()
        
        print("="*80)
    
    def print_pr_comment_summary(self, result: dict):
        """Print PR comment summary."""
        if not result.get("success"):
            print(f"❌ Failed: {result.get('error', 'Unknown error')}")
            return
        
        summary = result.get("summary", {})
        print(f"\n📊 PR Comment Summary:")
        print(f"   Repository: {result.get('repository', 'N/A')}")
        print(f"   PR Number: {result.get('pr_number', 'N/A')}")
        print(f"   Comments Added: {result.get('comments_added', 0)}")
        review_created = result.get('review_created', {})
        if isinstance(review_created, dict):
            review_success = review_created.get('success', False)
        else:
            review_success = bool(review_created)
        print(f"   Review Created: {'✅' if review_success else '❌'}")
        
        if result.get("summary"):
            print(f"\n📝 Review Summary:")
            print(result["summary"])
    
    def print_commit_summary(self, result: dict):
        """Print single commit review summary."""
        if not result.get("success"):
            print(f"❌ Failed: {result.get('error', 'Unknown error')}")
            return
        
        commit_info = result.get("commit_info", {})
        print(f"\n📊 Commit Review Summary:")
        print(f"   Repository: {result.get('repository', 'N/A')}")
        print(f"   Commit SHA: {result.get('commit_sha', 'N/A')}")
        print(f"   Author: {commit_info.get('author', 'N/A')}")
        print(f"   Date: {commit_info.get('date', 'N/A')}")
        print(f"   Files Changed: {commit_info.get('files_changed', 0)}")
        
        if result.get("summary"):
            print(f"\n📝 Review Summary:")
            print(result["summary"])
    
    def print_commit_reviews_summary(self, result: dict):
        """Print commit-by-commit PR review summary."""
        if not result.get("success"):
            print(f"❌ Failed: {result.get('error', 'Unknown error')}")
            return
        
        summary = result.get("summary", {})
        print(f"\n📊 Commit-by-Commit Review Summary:")
        print(f"   Repository: {result.get('repository', 'N/A')}")
        print(f"   PR Number: {result.get('pr_number', 'N/A')}")
        print(f"   Total Commits: {summary.get('total_commits', 0)}")
        print(f"   Reviewed Commits: {summary.get('reviewed_commits', 0)}")
        print(f"   Total Score: {summary.get('total_score', 0)}")
        print(f"   Total Issues: {summary.get('total_issues', 0)}")
        print(f"   Average Score: {summary.get('average_score', 0):.1f}/100")
        
        if result.get("overall_summary"):
            print(f"\n📝 Overall Summary:")
            print(result["overall_summary"])
    
    async def execute_comment_all_prs(self, args):
        """Execute comment on all accessible pull requests."""
        try:
            print("🔍 Starting comment on all accessible pull requests...")
            
            # Get all open PRs
            result = self.agent.list_all_pull_requests(state="open", include_private=True)
            
            if not result["success"]:
                print(f"❌ Failed to fetch pull requests: {result.get('error', 'Unknown error')}")
                return False
            
            prs = result["pull_requests"]
            if not prs:
                print("📭 No open pull requests found to comment on.")
                return True
            
            print(f"\n📊 Found {len(prs)} open pull requests to comment on:")
            print("-" * 80)
            
            for i, pr in enumerate(prs, 1):
                draft_emoji = "📝" if pr.get("draft", False) else ""
                repo_visibility = "🔒" if pr.get("repo_private", False) else "🌐"
                
                print(f"{i:2d}. {draft_emoji} {repo_visibility} {pr['repository']}#{pr['number']}")
                print(f"     📝 {pr['title']}")
                print(f"     👤 {pr['author']} | 🌿 {pr['head_branch']} → {pr['base_branch']}")
                print(f"     📅 Updated: {pr['updated_at']}")
                print(f"     📁 Files: {pr['changed_files']} | 💬 Comments: {pr['comments']}")
                print()
            
            # Get user confirmation
            while True:
                confirm = input("🔄 Are you sure you want to comment on ALL these PRs? (y/N): ").strip().lower()
                if confirm in ["y", "yes"]:
                    break
                elif confirm in ["n", "no"]:
                    print("👋 Cancelled comment on all PRs.")
                    return True
                else:
                    print("❌ Please enter 'y' or 'n'.")
            
            # Execute comment on each PR
            for i, pr in enumerate(prs, 1):
                print(f"💬 Commenting on PR #{pr['number']} in {pr['repository']}...")
                comment_result = self.agent.review_and_comment_pr(
                    owner=pr["repo_owner"],
                    repo=pr["repo_name"],
                    pr_number=pr["number"],
                    auto_comment=True, # Always auto-comment for this command
                    output_file=None # No specific output file for this command
                )
                
                if comment_result["success"]:
                    print(f"✅ PR #{pr['number']} commented successfully!")
                    print(f"🔗 Review URL: {comment_result.get('review_url', 'N/A')}")
                    print(f"💬 Comments Added: {comment_result.get('comments_added', 0)}")
                else:
                    print(f"❌ Failed to comment on PR #{pr['number']}: {comment_result.get('error', 'Unknown error')}")
                print() # Add a newline for better readability
            
            print("\n🎉 All accessible pull requests commented!")
            return True
            
        except Exception as e:
            print(f"❌ Failed to comment on all PRs: {e}")
            return False
    
    async def run(self):
        """Run the CLI."""
        self.print_banner()
        
        while True:
            try:
                command = input("\n🔍 Code Review > ").strip()
                
                if not command:
                    continue
                
                cmd, args = self.parse_command(command)
                
                if cmd == "help":
                    self.print_help()
                elif cmd == "exit":
                    print("👋 Goodbye!")
                    break
                elif cmd == "review":
                    success = await self.execute_review(args["repo_url"], args)
                    if success:
                        print("\n🎉 Review completed! Check the Downloads folder for the detailed report.")
                elif cmd == "list_repos":
                    await self.execute_list_repos(args)
                elif cmd == "list_branches":
                    await self.execute_list_branches(args["owner"], args["repo"])
                elif cmd == "review_all":
                    success = await self.execute_review_all(args)
                    if success:
                        print("\n🎉 All repositories review completed! Check the Downloads folder for the detailed report.")
                elif cmd == "review_pr":
                    success = await self.execute_review_pr(args["owner"], args["repo"], args["pr_number"], args.get("output_file"))
                    if success:
                        print("\n🎉 PR review completed! Check the Downloads folder for the detailed report.")
                elif cmd == "review_commits":
                    success = await self.execute_review_commits(args["owner"], args["repo"], args["pr_number"], args.get("output_file"))
                    if success:
                        print("\n🎉 PR commits review completed! Check the Downloads folder for the detailed report.")
                elif cmd == "review_commit":
                    success = await self.execute_review_commit(args["owner"], args["repo"], args["sha"], args.get("output_file"))
                    if success:
                        print("\n🎉 Commit review completed! Check the Downloads folder for the detailed report.")
                elif cmd == "comment_pr":
                    success = await self.execute_comment_pr(args["owner"], args["repo"], args["pr_number"], args["auto_comment"], args.get("output_file"))
                    if success:
                        print("\n🎉 PR review with comments completed! Check the Downloads folder for the detailed report.")
                elif cmd == "add_comment":
                    success = await self.execute_add_comment(args["owner"], args["repo"], args["pr_number"], args["comment"], args.get("line"), args.get("file"))
                    if success:
                        print("\n🎉 Comment added successfully!")
                elif cmd == "list_prs":
                    await self.execute_list_prs(args)
                elif cmd == "select_pr":
                    await self.execute_select_pr()
                elif cmd == "comment_all_prs":
                    await self.execute_comment_all_prs(args)
                elif cmd == "test_connection":
                    await self.execute_test_connection()
                elif cmd == "error":
                    print(f"❌ {args['message']}")
                elif cmd == "unknown":
                    print(f"❌ Unknown command: {args['command']}")
                    print("Type 'help' for available commands")
                else:
                    print("❌ Unexpected error")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {str(e)}")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="GitHub Code Review Agent CLI")
    parser.add_argument("--repo", help="Repository URL to review")
    parser.add_argument("--type", default="full", choices=["full", "security", "performance", "style"], 
                       help="Review type")
    parser.add_argument("--format", default="summary", choices=["summary", "detailed", "json"], 
                       help="Output format")
    parser.add_argument("--output", help="Output filename")
    parser.add_argument("--no-clone", action="store_true", help="Don't clone locally")
    
    args = parser.parse_args()
    
    if args.repo:
        # Single command mode
        agent = GitHubReviewAgent()
        options = {
            "review_type": args.type,
            "output_format": args.format,
            "clone_locally": not args.no_clone
        }
        if args.output:
            options["output_file"] = args.output
        
        async def run_single():
            cli = CodeReviewCLI()
            await cli.execute_review(args.repo, options)
        
        asyncio.run(run_single())
    else:
        # Interactive mode
        cli = CodeReviewCLI()
        asyncio.run(cli.run())

if __name__ == "__main__":
    main() 