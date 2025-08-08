#!/usr/bin/env python3
"""
CLI for GitHub PR Commenter
Demonstrates how the agent can analyze PRs and add intelligent comments.
"""

import os
import json
import argparse
from agent.github_pr_commenter import GitHubPRCommenter
from agent.github_coverage_agent import GitHubConfig

def print_banner():
    """Print the CLI banner."""
    print("🔗 GitHub PR Commenter CLI")
    print("=" * 50)
    print("📊 Analyzes PRs and adds intelligent comments")
    print("🤖 Provides test coverage analysis and suggestions")
    print("💬 Automatically comments on GitHub pull requests")
    print("=" * 50)

def load_github_config() -> GitHubConfig:
    """Load GitHub configuration from environment variables."""
    token = os.getenv('GITHUB_TOKEN')
    owner = os.getenv('GITHUB_OWNER')
    repo = os.getenv('GITHUB_REPO')
    
    if not all([token, owner, repo]):
        print("❌ Missing GitHub configuration!")
        print("Please set the following environment variables:")
        print("  GITHUB_TOKEN - Your GitHub personal access token")
        print("  GITHUB_OWNER - Repository owner (username or organization)")
        print("  GITHUB_REPO - Repository name")
        return None
    
    return GitHubConfig(token=token, owner=owner, repo=repo)

def list_prs():
    """List all open pull requests."""
    print("📋 Listing open pull requests...")
    
    config = load_github_config()
    if not config:
        return
    
    commenter = GitHubPRCommenter(config)
    prs = commenter.list_prs()
    
    if prs:
        print(f"✅ Found {len(prs)} open pull requests:")
        print()
        
        for pr in prs:
            print(f"📋 PR #{pr['number']}: {pr['title']}")
            print(f"   👤 Author: {pr['user']['login']}")
            print(f"   🌿 Branch: {pr['head']['ref']} → {pr['base']['ref']}")
            print(f"   📅 Created: {pr['created_at']}")
            print(f"   🔗 URL: {pr['html_url']}")
            print()
    else:
        print("❌ No open pull requests found")

def analyze_and_comment_pr(pr_number: int, dry_run: bool = False):
    """Analyze a PR and add a comment."""
    print(f"🔍 Analyzing PR #{pr_number}...")
    
    config = load_github_config()
    if not config:
        return
    
    commenter = GitHubPRCommenter(config)
    
    if dry_run:
        print("🧪 DRY RUN MODE - No comment will be posted")
        print("=" * 50)
        
        # Get PR info to show what would be analyzed
        pr_info = commenter.coverage_agent._get_pr_info(pr_number)
        if pr_info:
            print(f"📋 PR #{pr_info['number']}: {pr_info['title']}")
            print(f"👤 Author: {pr_info['user']['login']}")
            print(f"🌿 Branch: {pr_info['head']['ref']} → {pr_info['base']['ref']}")
            
            # Get PR files
            files = commenter.coverage_agent._get_pr_files(pr_number)
            if files:
                print(f"📁 Files changed: {len(files)}")
                for file in files[:5]:
                    print(f"   - {file['filename']} (+{file['additions']}, -{file['deletions']})")
                if len(files) > 5:
                    print(f"   ... and {len(files) - 5} more files")
                
                # Show what the comment would look like
                print("\n📝 Generated comment preview:")
                print("-" * 30)
                
                # Generate mock coverage results for preview
                coverage_results = []
                for file in files[:3]:  # Show first 3 files
                    if file['filename'].endswith('.py'):
                        coverage_results.append({
                            "file_path": file['filename'],
                            "language": "py",
                            "total_lines": 50,
                            "covered_lines": 35,
                            "coverage_percentage": 70.0
                        })
                
                comment_content = commenter._generate_pr_comment(pr_info, files, coverage_results, [])
                print(comment_content)
                print("-" * 30)
            else:
                print("❌ No files found in PR")
        else:
            print(f"❌ Failed to get PR #{pr_number} information")
    else:
        # Actually analyze and comment
        result = commenter.analyze_and_comment_on_pr(pr_number)
        
        if result.get("success"):
            print("✅ Successfully analyzed PR and added comment!")
            print(f"📋 PR #{result['pr_number']}")
            print(f"💬 Comment ID: {result['comment_id']}")
            
            if result.get('coverage_results'):
                print(f"📊 Coverage results: {len(result['coverage_results'])} files analyzed")
            
            if result.get('suggestions'):
                print(f"💡 Generated {len(result['suggestions'])} test suggestions")
        else:
            print(f"❌ Error: {result.get('error')}")

def demo_comment_generation():
    """Demonstrate comment generation without posting."""
    print("🎬 Demo: Comment Generation")
    print("=" * 50)
    
    config = load_github_config()
    if not config:
        return
    
    commenter = GitHubPRCommenter(config)
    
    # Create mock data for demonstration
    mock_pr_info = {
        "number": 11,
        "title": "Testing all agents",
        "user": {"login": "abiodun2025"},
        "head": {"ref": "testing-all-agents"},
        "base": {"ref": "main"},
        "created_at": "2025-08-07T15:58:54Z"
    }
    
    mock_files = [
        {"filename": "agent/test_coverage_agent.py", "additions": 150, "deletions": 0},
        {"filename": "test_coverage_cli.py", "additions": 80, "deletions": 0},
        {"filename": "README.md", "additions": 50, "deletions": 0}
    ]
    
    mock_coverage_results = [
        {
            "file_path": "agent/test_coverage_agent.py",
            "language": "py",
            "total_lines": 200,
            "covered_lines": 160,
            "coverage_percentage": 80.0
        },
        {
            "file_path": "test_coverage_cli.py",
            "language": "py",
            "total_lines": 100,
            "covered_lines": 70,
            "coverage_percentage": 70.0
        }
    ]
    
    # Generate sample suggestions
    from dataclasses import dataclass
    
    @dataclass
    class MockTestSuggestion:
        description: str
        type: str
        priority: str
        line_number: int
        file_path: str
        code_snippet: str
    
    mock_suggestions = [
        MockTestSuggestion(
            description="Add test case for null input validation",
            type="null_check",
            priority="high",
            line_number=25,
            file_path="agent/test_coverage_agent.py",
            code_snippet="if user_data is None:"
        ),
        MockTestSuggestion(
            description="Add test case for edge condition",
            type="edge_case",
            priority="medium",
            line_number=35,
            file_path="agent/test_coverage_agent.py",
            code_snippet="if age >= 18:"
        )
    ]
    
    # Generate comment
    comment_content = commenter._generate_pr_comment(
        mock_pr_info, mock_files, mock_coverage_results, mock_suggestions
    )
    
    print("📝 Generated comment:")
    print("=" * 50)
    print(comment_content)
    print("=" * 50)
    
    print("\n💡 This is what would be posted to GitHub!")
    print("🔗 The comment includes:")
    print("   • Coverage analysis for changed files")
    print("   • Test suggestions with priorities")
    print("   • Actionable recommendations")
    print("   • Professional formatting with emojis")

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="GitHub PR Commenter CLI - Analyze PRs and add intelligent comments",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 github_pr_commenter_cli.py list
  python3 github_pr_commenter_cli.py analyze 11
  python3 github_pr_commenter_cli.py analyze 11 --dry-run
  python3 github_pr_commenter_cli.py demo

Environment Variables:
  GITHUB_TOKEN - Your GitHub personal access token
  GITHUB_OWNER - Repository owner (username or organization)
  GITHUB_REPO - Repository name
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # List PRs command
    subparsers.add_parser('list', help='List all open pull requests')
    
    # Analyze PR command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze PR and add comment')
    analyze_parser.add_argument('pr_number', type=int, help='Pull request number')
    analyze_parser.add_argument('--dry-run', action='store_true', help='Show what would be posted without actually posting')
    
    # Demo command
    subparsers.add_parser('demo', help='Demonstrate comment generation')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    print_banner()
    
    if args.command == 'list':
        list_prs()
    elif args.command == 'analyze':
        analyze_and_comment_pr(args.pr_number, args.dry_run)
    elif args.command == 'demo':
        demo_comment_generation()

if __name__ == "__main__":
    main()
