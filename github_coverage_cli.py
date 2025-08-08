#!/usr/bin/env python3
"""
CLI for GitHub-Integrated Test Coverage & Suggestions Agent

Connects to GitHub repositories, clones code, runs tests with coverage,
and provides intelligent suggestions for missing test cases.
"""

import sys
import json
import argparse
import os
import subprocess
from pathlib import Path
from agent.github_coverage_agent import GitHubCoverageAgent, GitHubConfig

def print_banner():
    """Print the CLI banner."""
    print("🔗 GitHub-Integrated Test Coverage & Suggestions Agent CLI")
    print("=" * 60)
    print("📊 Connects to GitHub, clones repos, runs tests, analyzes coverage")
    print("🔧 Supports: Java (Maven), JS/TS (npm), Python (pip), Go")
    print("🤖 LLM-enhanced intelligent suggestions")
    print("=" * 60)

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
        print("\nExample:")
        print("  export GITHUB_TOKEN='ghp_your_token_here'")
        print("  export GITHUB_OWNER='your_username'")
        print("  export GITHUB_REPO='your_repo'")
        return None
    
    return GitHubConfig(token=token, owner=owner, repo=repo)

def analyze_pr_coverage(pr_number: int):
    """Analyze test coverage for a GitHub pull request."""
    print(f"🔍 Analyzing PR #{pr_number}")
    
    config = load_github_config()
    if not config:
        return
    
    agent = GitHubCoverageAgent(config)
    report = agent.analyze_pr_coverage(pr_number)
    
    if "error" in report:
        print(f"❌ Error: {report['error']}")
        return
    
    print_coverage_report(report)

def analyze_repository_coverage(branch: str = "main"):
    """Analyze test coverage for an entire repository."""
    print(f"🔍 Analyzing repository coverage for branch: {branch}")
    
    config = load_github_config()
    if not config:
        return
    
    agent = GitHubCoverageAgent(config)
    report = agent.analyze_repository_coverage(branch)
    
    if "error" in report:
        print(f"❌ Error: {report['error']}")
        return
    
    print_coverage_report(report)

def test_github_connection():
    """Test GitHub connection and repository access."""
    print("🔗 Testing GitHub connection...")
    
    config = load_github_config()
    if not config:
        return
    
    try:
        import requests
        
        # Test API access
        url = f"https://api.github.com/repos/{config.owner}/{config.repo}"
        headers = {
            "Authorization": f"token {config.token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            repo_info = response.json()
            print("✅ GitHub connection successful!")
            print(f"📁 Repository: {repo_info['full_name']}")
            print(f"📝 Description: {repo_info.get('description', 'No description')}")
            print(f"⭐ Stars: {repo_info['stargazers_count']}")
            print(f"🔀 Forks: {repo_info['forks_count']}")
            print(f"🌿 Default branch: {repo_info['default_branch']}")
            
            # Test if we can access PRs
            pr_url = f"https://api.github.com/repos/{config.owner}/{config.repo}/pulls"
            pr_response = requests.get(pr_url, headers=headers)
            
            if pr_response.status_code == 200:
                prs = pr_response.json()
                print(f"📋 Open PRs: {len(prs)}")
                if prs:
                    print("   Recent PRs:")
                    for pr in prs[:3]:
                        print(f"   - #{pr['number']}: {pr['title']}")
            else:
                print("⚠️ Could not access pull requests")
                
        else:
            print(f"❌ GitHub API error: {response.status_code}")
            print(f"   {response.text}")
            
    except Exception as e:
        print(f"❌ Connection error: {e}")

def check_prerequisites():
    """Check if required tools are available."""
    print("🔧 Checking prerequisites...")
    
    tools = {
        'git': 'Git (for cloning repositories)',
        'mvn': 'Maven (for Java projects)',
        'npm': 'npm (for JavaScript/TypeScript projects)',
        'pip3': 'pip3 (for Python projects)',
        'go': 'Go (for Go projects)'
    }
    
    missing_tools = []
    
    for tool, description in tools.items():
        try:
            result = subprocess.run([tool, '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                version = result.stdout.split('\n')[0]
                print(f"✅ {description}: {version}")
            else:
                missing_tools.append(description)
                print(f"❌ {description}: Not found")
        except FileNotFoundError:
            missing_tools.append(description)
            print(f"❌ {description}: Not found")
    
    if missing_tools:
        print(f"\n⚠️ Missing tools: {', '.join(missing_tools)}")
        print("   Some project types may not work without these tools.")
    else:
        print("\n✅ All tools available!")

def interactive_mode():
    """Interactive mode for the CLI."""
    print_banner()
    print("\n🎯 Interactive Mode")
    print("Type 'help' for commands or 'exit' to quit")
    print("-" * 40)
    
    config = load_github_config()
    if not config:
        print("❌ Cannot start interactive mode without GitHub configuration")
        return
    
    agent = GitHubCoverageAgent(config)
    
    while True:
        try:
            command = input(f"\n🤖 GitHub Coverage Agent ({config.owner}/{config.repo})> ").strip()
            
            if command.lower() in ['exit', 'quit', 'q']:
                print("👋 Goodbye!")
                break
            elif command.lower() == 'help':
                print_help()
            elif command.lower() == 'test':
                test_github_connection()
            elif command.lower() == 'check':
                check_prerequisites()
            elif command.startswith('pr '):
                try:
                    pr_number = int(command.split()[1])
                    analyze_pr_coverage(pr_number)
                except (ValueError, IndexError):
                    print("❌ Usage: pr <pr_number>")
            elif command.startswith('repo '):
                parts = command.split()
                branch = parts[1] if len(parts) > 1 else "main"
                analyze_repository_coverage(branch)
            elif command == 'repo':
                analyze_repository_coverage("main")
            elif command == 'demo':
                run_demo(agent)
            else:
                print("❌ Unknown command. Type 'help' for available commands.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def run_demo(agent):
    """Run a demonstration of the GitHub coverage agent."""
    print("\n🎬 Running GitHub Demo...")
    
    # Test with a public repository
    demo_config = GitHubConfig(
        token=os.getenv('GITHUB_TOKEN'),
        owner="octocat",
        repo="Hello-World"
    )
    
    demo_agent = GitHubCoverageAgent(demo_config)
    
    print("📁 Cloning demo repository...")
    print("🔍 This will demonstrate the GitHub integration capabilities")
    print("💡 Note: This is a demo repository, actual test coverage may vary")
    
    # Try to analyze the demo repository
    try:
        report = demo_agent.analyze_repository_coverage("main")
        if "error" not in report:
            print_coverage_report(report)
        else:
            print(f"⚠️ Demo completed with note: {report['error']}")
    except Exception as e:
        print(f"⚠️ Demo completed with note: {e}")

def print_coverage_report(report):
    """Print a formatted coverage report."""
    print("\n📊 Coverage Report")
    print("=" * 60)
    
    # Repository info
    if 'repository' in report:
        print(f"📁 Repository: {report['repository']}")
    if 'branch' in report:
        print(f"🌿 Branch: {report['branch']}")
    if 'pr_info' in report:
        pr_info = report['pr_info']
        print(f"📋 PR #{pr_info['number']}: {pr_info['title']}")
        print(f"👤 Author: {pr_info['user']['login']}")
    
    overall = report.get('overall_coverage', {})
    print(f"\n🎯 Overall Coverage: {overall.get('percentage', 0):.1f}%")
    print(f"📈 Total Lines: {overall.get('total_lines', 0)}")
    print(f"✅ Covered Lines: {overall.get('covered_lines', 0)}")
    print(f"❌ Uncovered Lines: {overall.get('uncovered_lines', 0)}")
    
    # File coverage
    file_coverage = report.get('file_coverage', [])
    if file_coverage:
        print(f"\n📁 File Coverage:")
        for file_data in file_coverage:
            print(f"   {file_data['file_path']}: {file_data['coverage_percentage']:.1f}%")
    
    # Suggestions
    suggestions = report.get('suggestions', {})
    if suggestions['total'] > 0:
        print(f"\n💡 Test Suggestions:")
        print(f"   🔴 High Priority: {suggestions['high_priority']}")
        print(f"   🟡 Medium Priority: {suggestions['medium_priority']}")
        print(f"   🟢 Low Priority: {suggestions['low_priority']}")
        
        # Show top suggestions
        details = suggestions.get('details', [])
        if details:
            print(f"\n🎯 Top Suggestions:")
            for i, suggestion in enumerate(details[:5], 1):
                print(f"   {i}. {suggestion['description']}")
                if suggestion['file_path'] != "repository":
                    print(f"      File: {suggestion['file_path']}:{suggestion['line_number']}")
                print(f"      Type: {suggestion['type']} | Priority: {suggestion['priority']}")
                if suggestion['code_snippet']:
                    print(f"      Code: {suggestion['code_snippet']}")
                print()
    
    # Recommendations
    recommendations = report.get('recommendations', [])
    if recommendations:
        print(f"📋 Recommendations:")
        for rec in recommendations:
            print(f"   • {rec}")
    
    print("=" * 60)

def print_help():
    """Print help information."""
    print("\n📖 Available Commands:")
    print("   pr <number>                    - Analyze PR coverage")
    print("   repo [branch]                  - Analyze repository coverage")
    print("   test                           - Test GitHub connection")
    print("   check                          - Check prerequisites")
    print("   demo                           - Run demo")
    print("   help                           - Show this help")
    print("   exit                           - Exit the CLI")
    print("\n💡 Examples:")
    print("   pr 123                         - Analyze PR #123")
    print("   repo main                      - Analyze main branch")
    print("   repo feature/new-feature       - Analyze specific branch")

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="GitHub-Integrated Test Coverage & Suggestions Agent CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 github_coverage_cli.py pr 123
  python3 github_coverage_cli.py repo main
  python3 github_coverage_cli.py test
  python3 github_coverage_cli.py interactive

Environment Variables:
  GITHUB_TOKEN - Your GitHub personal access token
  GITHUB_OWNER - Repository owner (username or organization)
  GITHUB_REPO - Repository name
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Analyze PR command
    pr_parser = subparsers.add_parser('pr', help='Analyze PR coverage')
    pr_parser.add_argument('pr_number', type=int, help='Pull request number')
    
    # Analyze repository command
    repo_parser = subparsers.add_parser('repo', help='Analyze repository coverage')
    repo_parser.add_argument('branch', nargs='?', default='main', help='Branch name (default: main)')
    
    # Test connection command
    subparsers.add_parser('test', help='Test GitHub connection')
    
    # Check prerequisites command
    subparsers.add_parser('check', help='Check prerequisites')
    
    # Interactive command
    subparsers.add_parser('interactive', help='Start interactive mode')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    print_banner()
    
    if args.command == 'pr':
        analyze_pr_coverage(args.pr_number)
    elif args.command == 'repo':
        analyze_repository_coverage(args.branch)
    elif args.command == 'test':
        test_github_connection()
    elif args.command == 'check':
        check_prerequisites()
    elif args.command == 'interactive':
        interactive_mode()

if __name__ == "__main__":
    main()
