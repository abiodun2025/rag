#!/usr/bin/env python3
"""
Create Real Pull Request Script
Simple script to create actual pull requests on your GitHub repository.
"""

import os
import sys
from real_github_pull_request import RealGitHubPullRequest, GitHubConfig, create_github_config_interactive

def create_real_pull_request():
    """Create a real pull request on your repository."""
    
    print("🔀 Create Real Pull Request")
    print("=" * 50)
    print("This script will create an actual pull request on your GitHub repository.")
    print()
    
    # Get GitHub configuration
    print("🔧 Step 1: GitHub Configuration")
    print("-" * 30)
    
    # Check if environment variables are set
    token = os.getenv('GITHUB_TOKEN')
    owner = os.getenv('GITHUB_OWNER')
    repo = os.getenv('GITHUB_REPO')
    
    if token and owner and repo:
        print("✅ Using environment variables:")
        print(f"   Token: {token[:8]}...")
        print(f"   Owner: {owner}")
        print(f"   Repo: {repo}")
        config = GitHubConfig(token=token, owner=owner, repo=repo)
    else:
        print("📝 Please provide your GitHub credentials:")
        config = create_github_config_interactive()
        if not config:
            print("❌ Failed to create configuration")
            return
    
    # Create the GitHub PR client
    github_pr = RealGitHubPullRequest(config)
    
    # Test connection by listing pull requests
    print("\n🔍 Step 2: Testing Connection")
    print("-" * 30)
    
    result = github_pr.list_pull_requests(state="open", limit=3)
    if not result.get("success"):
        print(f"❌ Connection failed: {result.get('error')}")
        print("Please check your GitHub token and repository access.")
        return
    
    print(f"✅ Connection successful! Found {result['total_count']} open pull requests")
    for pr in result['pull_requests']:
        print(f"   - #{pr['pr_number']}: {pr['title']}")
    
    # Get pull request details
    print("\n📝 Step 3: Pull Request Details")
    print("-" * 30)
    
    title = input("Enter pull request title: ").strip()
    if not title:
        print("❌ Title is required")
        return
    
    description = input("Enter pull request description (optional): ").strip()
    if not description:
        description = "Pull request created via automated script"
    
    source_branch = input("Enter source branch name: ").strip()
    if not source_branch:
        print("❌ Source branch is required")
        return
    
    target_branch = input("Enter target branch name (default: main): ").strip()
    if not target_branch:
        target_branch = "main"
    
    # Confirm before creating
    print("\n📋 Step 4: Confirmation")
    print("-" * 30)
    print(f"Repository: {config.owner}/{config.repo}")
    print(f"Title: {title}")
    print(f"Description: {description}")
    print(f"Source Branch: {source_branch}")
    print(f"Target Branch: {target_branch}")
    print()
    
    confirm = input("Create this pull request? (y/N): ").strip().lower()
    if confirm not in ['y', 'yes']:
        print("❌ Pull request creation cancelled")
        return
    
    # Create the pull request
    print("\n🔀 Step 5: Creating Pull Request")
    print("-" * 30)
    
    result = github_pr.create_pull_request(
        title=title,
        description=description,
        source_branch=source_branch,
        target_branch=target_branch
    )
    
    if result.get("success"):
        print("✅ Pull request created successfully!")
        print(f"   PR Number: #{result['pr_number']}")
        print(f"   Title: {result['title']}")
        print(f"   URL: {result['url']}")
        print(f"   Status: {result['status']}")
        print()
        print("🎉 Your pull request is now live on GitHub!")
        print(f"   View it at: {result['url']}")
    else:
        print(f"❌ Failed to create pull request: {result.get('error')}")
        
        # Provide helpful error messages
        error = result.get('error', '').lower()
        if 'not found' in error:
            print("\n💡 Troubleshooting:")
            print("   - Check that the repository exists and you have access")
            print("   - Verify the owner and repository name are correct")
        elif 'bad credentials' in error:
            print("\n💡 Troubleshooting:")
            print("   - Check that your GitHub token is valid")
            print("   - Ensure the token has 'repo' permissions")
        elif 'branch' in error:
            print("\n💡 Troubleshooting:")
            print("   - Check that the source branch exists")
            print("   - Verify the branch names are correct")

def main():
    """Main function."""
    try:
        create_real_pull_request()
    except KeyboardInterrupt:
        print("\n\n❌ Operation cancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("Please check your configuration and try again.")

if __name__ == "__main__":
    main()