#!/usr/bin/env python3
"""
Review Any GitHub Repository
===========================

Simple script to review any GitHub repository with one command.
Usage: python review_any_repo.py <repository_url>
"""

import sys
import os
from github_review_agent import GitHubReviewAgent

def main():
    """Review any GitHub repository."""
    
    if len(sys.argv) < 2:
        print("🔍 GitHub Repository Code Review")
        print("=" * 40)
        print("Usage: python review_any_repo.py <repository_url>")
        print()
        print("Examples:")
        print("  python review_any_repo.py https://github.com/facebook/react")
        print("  python review_any_repo.py facebook/react")
        print("  python review_any_repo.py microsoft/vscode")
        print()
        print("The script will:")
        print("  ✅ Clone the repository locally")
        print("  🔍 Analyze all code files")
        print("  📊 Generate a comprehensive report")
        print("  📄 Save detailed report to JSON file")
        print("  🧹 Clean up cloned repository")
        print("  📋 Display summary in terminal")
        return
    
    repo_url = sys.argv[1]
    
    print(f"🔍 Starting code review for: {repo_url}")
    print("=" * 60)
    
    # Initialize agent
    agent = GitHubReviewAgent()
    
    try:
        # Generate output filename
        repo_name = repo_url.replace('https://github.com/', '').replace('/', '_')
        output_file = f"code_review_{repo_name}_{os.getpid()}.json"
        
        # Review repository
        report = agent.review_repository(
            repo_url=repo_url,
            output_file=output_file,
            clone_locally=True
        )
        
        # Print summary
        agent.print_report_summary(report)
        
        # Clean up
        if report.get('local_path'):
            agent.cleanup_local_repository(report['local_path'])
        
        print(f"\n✅ Review completed! Detailed report saved to: {output_file}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure the repository URL is correct and accessible")

if __name__ == "__main__":
    main() 