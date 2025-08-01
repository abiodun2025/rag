#!/usr/bin/env python3
"""
GitHub Setup Script for MCP Bridge
"""

import os
import json
from pathlib import Path

def setup_github_credentials():
    """Setup GitHub credentials for the MCP bridge."""
    
    print("🔧 GitHub Setup for MCP Bridge")
    print("=" * 50)
    print()
    print("To use GitHub features (PR creation, branch management), you need to:")
    print("1. Create a GitHub Personal Access Token")
    print("2. Set your GitHub username and repository")
    print()
    
    # Check if .env file exists
    env_file = Path(".env")
    if env_file.exists():
        print("✅ Found existing .env file")
        with open(env_file, 'r') as f:
            content = f.read()
            if 'GITHUB_TOKEN' in content:
                print("✅ GitHub token already configured")
            else:
                print("❌ GitHub token not found in .env")
    else:
        print("❌ No .env file found")
    
    print()
    print("📋 Required Environment Variables:")
    print("   GITHUB_TOKEN=your_github_personal_access_token")
    print("   GITHUB_OWNER=your_github_username")
    print("   GITHUB_REPO=your_repository_name")
    print()
    
    print("🔗 How to get a GitHub Personal Access Token:")
    print("1. Go to GitHub.com → Settings → Developer settings → Personal access tokens")
    print("2. Click 'Generate new token (classic)'")
    print("3. Select scopes: 'repo' (full control of private repositories)")
    print("4. Copy the generated token")
    print()
    
    print("📝 Create or update your .env file with:")
    print("   GITHUB_TOKEN=ghp_your_token_here")
    print("   GITHUB_OWNER=your_username")
    print("   GITHUB_REPO=your_repo_name")
    print()
    
    # Ask user if they want to create .env file
    create_env = input("Would you like to create/update .env file now? (y/n): ").lower().strip()
    
    if create_env == 'y':
        token = input("Enter your GitHub Personal Access Token: ").strip()
        owner = input("Enter your GitHub username: ").strip()
        repo = input("Enter your repository name: ").strip()
        
        if token and owner and repo:
            # Create or update .env file
            env_content = f"""# GitHub Configuration
GITHUB_TOKEN={token}
GITHUB_OWNER={owner}
GITHUB_REPO={repo}

# Other configurations
MCP_SERVER_URL=http://127.0.0.1:5000
"""
            
            with open(env_file, 'w') as f:
                f.write(env_content)
            
            print(f"✅ Created .env file with GitHub configuration")
            print(f"   Owner: {owner}")
            print(f"   Repo: {repo}")
            print(f"   Token: {'*' * 10}{token[-4:] if len(token) > 4 else '***'}")
            print()
            print("🔄 Please restart your MCP bridge to load the new configuration")
        else:
            print("❌ Missing required information. Please try again.")
    else:
        print("📝 Please manually create/update your .env file with the required variables")

def test_github_connection():
    """Test GitHub connection with current credentials."""
    print("\n🧪 Testing GitHub Connection")
    print("=" * 30)
    
    token = os.getenv('GITHUB_TOKEN')
    owner = os.getenv('GITHUB_OWNER')
    repo = os.getenv('GITHUB_REPO')
    
    if not all([token, owner, repo]):
        print("❌ GitHub credentials not configured")
        print("   Please set GITHUB_TOKEN, GITHUB_OWNER, and GITHUB_REPO environment variables")
        return False
    
    try:
        import requests
        
        # Test GitHub API connection
        url = f"https://api.github.com/repos/{owner}/{repo}"
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            repo_data = response.json()
            print("✅ GitHub connection successful!")
            print(f"   Repository: {repo_data['full_name']}")
            print(f"   Description: {repo_data.get('description', 'No description')}")
            print(f"   Default branch: {repo_data['default_branch']}")
            return True
        else:
            print(f"❌ GitHub connection failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ GitHub connection error: {e}")
        return False

if __name__ == "__main__":
    setup_github_credentials()
    test_github_connection() 