#!/usr/bin/env python3
"""
Example: GitHub Repository Code Review
=====================================

Simple example showing how to use the GitHub review agent.
"""

from github_review_agent import GitHubReviewAgent

def main():
    """Example usage of the GitHub review agent."""
    
    # Initialize the agent
    # You can pass a GitHub token here or set GITHUB_TOKEN environment variable
    agent = GitHubReviewAgent()
    
    # Example repositories to review
    repositories = [
        "https://github.com/olaoluwagureje1/my-mcp-server",
        "facebook/react",
        "microsoft/vscode",
        "tensorflow/tensorflow"
    ]
    
    print("🔍 GitHub Repository Code Review Examples")
    print("=" * 50)
    
    for repo_url in repositories:
        print(f"\n📦 Reviewing: {repo_url}")
        print("-" * 40)
        
        try:
            # Review the repository
            report = agent.review_repository(
                repo_url=repo_url,
                output_file=f"review_{repo_url.replace('/', '_').replace('https://github.com/', '')}.json",
                clone_locally=True
            )
            
            # Print summary
            agent.print_report_summary(report)
            
            # Clean up local repository
            if report.get('local_path'):
                agent.cleanup_local_repository(report['local_path'])
            
        except Exception as e:
            print(f"❌ Error reviewing {repo_url}: {e}")
        
        print("\n" + "="*50)

if __name__ == "__main__":
    main() 