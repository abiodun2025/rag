#!/usr/bin/env python3
"""
GitHub Token Setup Script
Helps you set up your GitHub token for the alert system.
"""

import os
import json
import getpass
from pathlib import Path

def setup_github_token():
    """Set up GitHub token for the alert system."""
    
    print("🔧 GitHub Token Setup for Real-Time Alert System")
    print("=" * 50)
    
    # Check current configuration
    print("Current GitHub Configuration:")
    print(f"  GITHUB_TOKEN: {'***' if os.getenv('GITHUB_TOKEN') else 'Not set'}")
    print(f"  GITHUB_OWNER: {os.getenv('GITHUB_OWNER', 'abiodun2025')}")
    print(f"  GITHUB_REPO: {os.getenv('GITHUB_REPO', 'rag')}")
    print()
    
    # Get GitHub token securely
    print("Please enter your GitHub Personal Access Token:")
    print("(You can create one at: https://github.com/settings/tokens)")
    print("Required permissions: repo, workflow")
    print()
    
    token = getpass.getpass("GitHub Token: ")
    
    if not token or token.strip() == "":
        print("❌ No token provided. Setup cancelled.")
        return False
    
    if token == "YOUR_GITHUB_TOKEN_HERE" or "your_github_token" in token.lower():
        print("❌ Please provide your actual GitHub token, not the placeholder.")
        return False
    
    # Test the token
    print("\n🔍 Testing GitHub token...")
    try:
        import requests
        
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        # Test API access
        response = requests.get("https://api.github.com/user", headers=headers)
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ Token is valid! Authenticated as: {user_data.get('login', 'Unknown')}")
            print(f"   Name: {user_data.get('name', 'Not set')}")
            print(f"   Email: {user_data.get('email', 'Not set')}")
        else:
            print(f"❌ Token validation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing token: {e}")
        return False
    
    # Set environment variable
    print("\n📝 Setting up GitHub token...")
    
    # Update shell profile
    shell_profile = Path.home() / ".zshrc"
    if not shell_profile.exists():
        shell_profile = Path.home() / ".bash_profile"
    
    # Check if GITHUB_TOKEN is already in profile
    if shell_profile.exists():
        with open(shell_profile, 'r') as f:
            content = f.read()
        
        if "GITHUB_TOKEN" in content:
            # Update existing line
            import re
            new_content = re.sub(
                r'export GITHUB_TOKEN="[^"]*"',
                f'export GITHUB_TOKEN="{token}"',
                content
            )
            with open(shell_profile, 'w') as f:
                f.write(new_content)
            print(f"✅ Updated GITHUB_TOKEN in {shell_profile}")
        else:
            # Add new line
            with open(shell_profile, 'a') as f:
                f.write(f'\nexport GITHUB_TOKEN="{token}"\n')
            print(f"✅ Added GITHUB_TOKEN to {shell_profile}")
    
    # Set for current session
    os.environ['GITHUB_TOKEN'] = token
    print("✅ Set GITHUB_TOKEN for current session")
    
    # Update github_config.json in working-mcp-server
    github_config_path = Path.home() / "Desktop" / "working-mcp-server" / "github_config.json"
    if github_config_path.exists():
        try:
            with open(github_config_path, 'r') as f:
                config = json.load(f)
            
            config['token'] = token
            
            with open(github_config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            print(f"✅ Updated {github_config_path}")
        except Exception as e:
            print(f"⚠️  Could not update {github_config_path}: {e}")
    
    # Create local github_config.json
    local_config_path = Path("github_config.json")
    try:
        config = {
            "username": "abiodun2025",
            "token": token
        }
        
        with open(local_config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Created {local_config_path}")
    except Exception as e:
        print(f"⚠️  Could not create local config: {e}")
    
    print("\n🎉 GitHub token setup completed!")
    print("\nNext steps:")
    print("1. Restart your terminal or run: source ~/.zshrc")
    print("2. Test the real GitHub integration:")
    print("   python3 real_github_cli.py test-full")
    print("3. Check your email for real GitHub workflow alerts!")
    
    return True

def test_github_integration():
    """Test GitHub integration with the token."""
    
    print("\n🧪 Testing GitHub Integration")
    print("=" * 30)
    
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        print("❌ GITHUB_TOKEN not set")
        return False
    
    try:
        import requests
        
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        # Test repository access
        owner = os.getenv('GITHUB_OWNER', 'abiodun2025')
        repo = os.getenv('GITHUB_REPO', 'rag')
        
        response = requests.get(f"https://api.github.com/repos/{owner}/{repo}", headers=headers)
        
        if response.status_code == 200:
            repo_data = response.json()
            print(f"✅ Repository access confirmed: {repo_data['full_name']}")
            print(f"   Description: {repo_data.get('description', 'No description')}")
            print(f"   Private: {repo_data['private']}")
            print(f"   Default branch: {repo_data['default_branch']}")
            
            # Test branches
            branches_response = requests.get(f"https://api.github.com/repos/{owner}/{repo}/branches", headers=headers)
            if branches_response.status_code == 200:
                branches = branches_response.json()
                print(f"   Available branches: {', '.join([b['name'] for b in branches[:5]])}")
            
            return True
        else:
            print(f"❌ Repository access failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing GitHub integration: {e}")
        return False

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_github_integration()
    else:
        setup_github_token() 