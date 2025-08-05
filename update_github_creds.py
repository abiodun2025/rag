#!/usr/bin/env python3
"""
Update GitHub Credentials Script
"""

import os
from pathlib import Path

def update_github_credentials():
    """Update GitHub credentials with real values."""
    
    print("🔧 GitHub Credentials Update")
    print("=" * 50)
    print()
    
    # Check current .env
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found!")
        return
    
    print("📋 Current .env contents:")
    with open(env_file, 'r') as f:
        content = f.read()
        print(content)
    
    print("\n🔧 To fix GitHub integration, update these values:")
    print("1. GITHUB_TOKEN=ghp_your_actual_token_here")
    print("2. GITHUB_OWNER=your_actual_github_username")
    print("3. GITHUB_REPO=your_actual_repository_name")
    print()
    print("💡 Example:")
    print("   GITHUB_TOKEN=ghp_1234567890abcdef1234567890abcdef12345678")
    print("   GITHUB_OWNER=johndoe")
    print("   GITHUB_REPO=my-awesome-project")
    print()
    print("📝 Edit the .env file with your real GitHub credentials")
    print("   nano .env  # or use your preferred editor")
    print()
    print("✅ After updating, restart the MCP bridge:")
    print("   python3 switch_bridge.py github")

if __name__ == "__main__":
    update_github_credentials() 