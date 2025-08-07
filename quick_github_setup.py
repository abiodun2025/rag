#!/usr/bin/env python3
"""
Quick GitHub Token Setup
"""

import os
import subprocess
import getpass

def setup_github_token():
    print("🔧 Quick GitHub Token Setup")
    print("=" * 30)
    print("Please enter your new GitHub Personal Access Token:")
    print("(Create at: https://github.com/settings/tokens)")
    print("Required scopes: repo, workflow")
    print()
    
    token = getpass.getpass("GitHub Token: ")
    
    if not token:
        print("❌ No token provided")
        return
    
    # Test token
    print("\n🔍 Testing token...")
    import requests
    headers = {"Authorization": f"token {token}"}
    response = requests.get("https://api.github.com/user", headers=headers)
    
    if response.status_code == 200:
        user_data = response.json()
        print(f"✅ Token valid! Authenticated as: {user_data.get('login')}")
    else:
        print(f"❌ Token invalid: {response.status_code}")
        return
    
    # Update Git remote
    print("\n📝 Updating Git remote...")
    new_url = f"https://abiodun2025:{token}@github.com/abiodun2025/rag.git"
    subprocess.run(["git", "remote", "set-url", "origin", new_url], check=True)
    print("✅ Git remote updated")
    
    # Set environment variable
    os.environ['GITHUB_TOKEN'] = token
    print("✅ Environment variable set")
    
    # Add to shell profile
    import re
    shell_profile = os.path.expanduser("~/.zshrc")
    if os.path.exists(shell_profile):
        with open(shell_profile, 'r') as f:
            content = f.read()
        
        if "GITHUB_TOKEN" in content:
            new_content = re.sub(r'export GITHUB_TOKEN="[^"]*"', f'export GITHUB_TOKEN="{token}"', content)
        else:
            new_content = content + f'\nexport GITHUB_TOKEN="{token}"\n'
        
        with open(shell_profile, 'w') as f:
            f.write(new_content)
        print("✅ Added to shell profile")
    
    # Test push
    print("\n🚀 Testing Git push...")
    try:
        result = subprocess.run(["git", "push", "-u", "origin", "feature/alert_monitoring"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Successfully pushed to GitHub!")
            print("   Branch: feature/alert_monitoring")
            print("   URL: https://github.com/abiodun2025/rag/tree/feature/alert_monitoring")
        else:
            print(f"❌ Push failed: {result.stderr}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n🎉 Setup complete!")

if __name__ == "__main__":
    setup_github_token() 