#!/usr/bin/env python3
"""
Fix GitHub Credentials with Real Values
"""

import subprocess
import re
import os

def extract_github_info():
    """Extract GitHub info from git remote."""
    try:
        result = subprocess.run(['git', 'remote', '-v'], capture_output=True, text=True)
        if result.returncode == 0:
            # Parse the git remote output
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if 'origin' in line and 'github.com' in line:
                    # Extract username and repo from URL
                    match = re.search(r'github\.com/([^/]+)/([^/]+)\.git', line)
                    if match:
                        username = match.group(1)
                        repo = match.group(2)
                        return username, repo
        return None, None
    except Exception as e:
        print(f"Error extracting git info: {e}")
        return None, None

def extract_github_token():
    """Extract GitHub token from git remote URL."""
    try:
        result = subprocess.run(['git', 'remote', '-v'], capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if 'origin' in line and 'github.com' in line:
                    # Extract token from URL
                    match = re.search(r'ghp_[a-zA-Z0-9]+', line)
                    if match:
                        return match.group(0)
        return None
    except Exception as e:
        print(f"Error extracting token: {e}")
        return None

def update_env_file():
    """Update .env file with real GitHub credentials."""
    
    print("🔧 Fixing GitHub Credentials")
    print("=" * 50)
    
    # Extract info from git
    username, repo = extract_github_info()
    token = extract_github_token()
    
    if not username or not repo or not token:
        print("❌ Could not extract GitHub info from git remote")
        print("Please make sure you have a git remote configured with GitHub")
        return
    
    print(f"📋 Found GitHub configuration:")
    print(f"   Username: {username}")
    print(f"   Repository: {repo}")
    print(f"   Token: ***{token[-4:]}")
    print()
    
    # Read current .env
    env_content = ""
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            env_content = f.read()
    
    # Update GitHub credentials
    new_content = ""
    lines = env_content.split('\n')
    updated = False
    
    for line in lines:
        if line.startswith('GITHUB_TOKEN='):
            new_content += f"GITHUB_TOKEN={token}\n"
            updated = True
        elif line.startswith('GITHUB_OWNER='):
            new_content += f"GITHUB_OWNER={username}\n"
            updated = True
        elif line.startswith('GITHUB_REPO='):
            new_content += f"GITHUB_REPO={repo}\n"
            updated = True
        else:
            new_content += line + '\n'
    
    # Write updated .env
    with open('.env', 'w') as f:
        f.write(new_content)
    
    print("✅ Updated .env file with real GitHub credentials!")
    print()
    print("📋 New .env contents:")
    print(f"   GITHUB_TOKEN={token}")
    print(f"   GITHUB_OWNER={username}")
    print(f"   GITHUB_REPO={repo}")
    print()
    print("🔄 Now restart the MCP bridge to use GitHub tools:")
    print("   python3 switch_bridge.py github")
    print()
    print("🎯 After restarting, your workflows will create real GitHub branches and PRs!")

if __name__ == "__main__":
    update_env_file() 