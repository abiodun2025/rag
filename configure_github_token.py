#!/usr/bin/env python3
"""
Configure GitHub Token for Git Operations and Alert System
"""

import os
import subprocess
import getpass
from pathlib import Path

def configure_github_token():
    """Configure GitHub token for both Git and alert system."""
    
    print("🔧 GitHub Token Configuration")
    print("=" * 40)
    
    # Get the token
    print("Please enter your GitHub Personal Access Token:")
    print("(Create one at: https://github.com/settings/tokens)")
    print("Required scopes: repo, workflow")
    print()
    
    token = getpass.getpass("GitHub Token: ")
    
    if not token or token.strip() == "":
        print("❌ No token provided.")
        return False
    
    # Test the token
    print("\n🔍 Testing GitHub token...")
    try:
        import requests
        
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        response = requests.get("https://api.github.com/user", headers=headers)
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ Token is valid! Authenticated as: {user_data.get('login', 'Unknown')}")
        else:
            print(f"❌ Token validation failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing token: {e}")
        return False
    
    # Configure Git remote
    print("\n📝 Configuring Git remote...")
    try:
        # Update remote URL with new token
        new_url = f"https://abiodun2025:{token}@github.com/abiodun2025/rag.git"
        
        subprocess.run([
            "git", "remote", "set-url", "origin", new_url
        ], check=True)
        
        print("✅ Updated Git remote URL with new token")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error updating Git remote: {e}")
        return False
    
    # Set environment variable
    print("\n🔧 Setting environment variables...")
    
    # Update shell profile
    shell_profile = Path.home() / ".zshrc"
    if not shell_profile.exists():
        shell_profile = Path.home() / ".bash_profile"
    
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
    
    # Test Git push
    print("\n🧪 Testing Git push...")
    try:
        # Try to push the branch
        result = subprocess.run([
            "git", "push", "-u", "origin", "feature/alert_monitoring"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Successfully pushed to GitHub!")
            print("   Branch: feature/alert_monitoring")
            print("   URL: https://github.com/abiodun2025/rag/tree/feature/alert_monitoring")
        else:
            print(f"⚠️  Git push output: {result.stdout}")
            print(f"⚠️  Git push errors: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Error testing Git push: {e}")
    
    print("\n🎉 GitHub token configuration completed!")
    print("\nNext steps:")
    print("1. Restart your terminal or run: source ~/.zshrc")
    print("2. Test the alert system: python3 test_real_github_alerts.py")
    print("3. Create a pull request: python3 real_github_cli.py test-full")
    
    return True

if __name__ == "__main__":
    configure_github_token() 