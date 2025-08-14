#!/usr/bin/env python3
"""
Setup GitHub Credentials for MCP Bridge
"""

import os
import getpass
import json
from pathlib import Path

def setup_github_credentials():
    """Interactive setup for GitHub credentials."""
    
    print("🔧 GitHub Credentials Setup for MCP Bridge")
    print("=" * 50)
    print()
    
    # Check if credentials already exist
    env_file = Path(".env")
    if env_file.exists():
        print("📁 Found existing .env file")
        with open(env_file, 'r') as f:
            existing_content = f.read()
            if "GITHUB_TOKEN" in existing_content:
                print("✅ GitHub token already configured")
                response = input("Do you want to update the credentials? (y/n): ").lower()
                if response != 'y':
                    print("Keeping existing credentials.")
                    return
    
    print("📋 You need to provide the following GitHub credentials:")
    print("   1. GitHub Personal Access Token")
    print("   2. GitHub Username/Organization")
    print("   3. Repository name")
    print()
    
    # Get GitHub token
    print("🔑 GitHub Personal Access Token:")
    print("   - Go to https://github.com/settings/tokens")
    print("   - Click 'Generate new token (classic)'")
    print("   - Select scopes: repo, workflow")
    print("   - Copy the token")
    print()
    
    github_token = getpass.getpass("Enter your GitHub token: ").strip()
    if not github_token:
        print("❌ GitHub token is required!")
        return
    
    # Get GitHub owner (username or organization)
    github_owner = input("Enter GitHub username or organization: ").strip()
    if not github_owner:
        print("❌ GitHub owner is required!")
        return
    
    # Get repository name
    github_repo = input("Enter repository name: ").strip()
    if not github_repo:
        print("❌ Repository name is required!")
        return
    
    # Validate the credentials
    print("\n🔍 Validating GitHub credentials...")
    if validate_github_credentials(github_token, github_owner, github_repo):
        print("✅ GitHub credentials are valid!")
        
        # Save to .env file
        env_content = f"""# GitHub MCP Bridge Configuration
GITHUB_TOKEN={github_token}
GITHUB_OWNER={github_owner}
GITHUB_REPO={github_repo}

# Other configurations
MCP_SERVER_URL=http://127.0.0.1:5000
"""
        
        with open(env_file, 'w') as f:
            f.write(env_content)
        
        print(f"✅ Credentials saved to {env_file}")
        print()
        
        # Set environment variables for current session
        os.environ['GITHUB_TOKEN'] = github_token
        os.environ['GITHUB_OWNER'] = github_owner
        os.environ['GITHUB_REPO'] = github_repo
        
        print("🚀 Ready to use GitHub MCP Bridge!")
        print("   You can now start the bridge with: python3 github_mcp_bridge.py")
        
    else:
        print("❌ GitHub credentials validation failed!")
        print("   Please check your token, owner, and repository name.")

def validate_github_credentials(token, owner, repo):
    """Validate GitHub credentials by making a test API call."""
    try:
        import requests
        
        url = f"https://api.github.com/repos/{owner}/{repo}"
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            repo_data = response.json()
            print(f"   ✅ Repository found: {repo_data['full_name']}")
            print(f"   📝 Description: {repo_data.get('description', 'No description')}")
            return True
        elif response.status_code == 404:
            print(f"   ❌ Repository not found: {owner}/{repo}")
            return False
        elif response.status_code == 401:
            print("   ❌ Invalid GitHub token")
            return False
        else:
            print(f"   ❌ API error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Validation error: {e}")
        return False

def test_github_bridge():
    """Test the GitHub MCP bridge with configured credentials."""
    
    print("\n🧪 Testing GitHub MCP Bridge")
    print("=" * 40)
    
    # Check if credentials are set
    token = os.getenv('GITHUB_TOKEN')
    owner = os.getenv('GITHUB_OWNER')
    repo = os.getenv('GITHUB_REPO')
    
    if not all([token, owner, repo]):
        print("❌ GitHub credentials not configured!")
        print("   Run setup_github_credentials() first")
        return False
    
    print(f"✅ Using repository: {owner}/{repo}")
    
    # Test the bridge
    try:
        import requests
        
        # Test health endpoint
        response = requests.get("http://127.0.0.1:5000/health", timeout=5)
        if response.status_code != 200:
            print("❌ MCP bridge not running on port 5000")
            print("   Start it with: python3 github_mcp_bridge.py")
            return False
        
        print("✅ MCP bridge is running")
        
        # Test creating a PR
        test_data = {
            "tool": "create_pull_request",
            "arguments": {
                "title": "Test PR from MCP Bridge",
                "description": "This is a test pull request created by the MCP bridge",
                "source_branch": "test-branch",
                "target_branch": "main"
            }
        }
        
        response = requests.post(
            "http://127.0.0.1:5000/call",
            headers={"Content-Type": "application/json"},
            json=test_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ Test PR created successfully!")
                print(f"   PR Number: {result.get('pr_number')}")
                print(f"   PR URL: {result.get('pr_url')}")
                return True
            else:
                print(f"❌ PR creation failed: {result.get('error')}")
                return False
        else:
            print(f"❌ HTTP error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 GitHub MCP Bridge Setup")
    print("=" * 40)
    print()
    
    # Check if .env file exists
    if Path(".env").exists():
        print("📁 Found .env file")
        response = input("Do you want to reconfigure GitHub credentials? (y/n): ").lower()
        if response == 'y':
            setup_github_credentials()
        else:
            print("Using existing credentials.")
    else:
        setup_github_credentials()
    
    # Test the bridge
    test_github_bridge() 