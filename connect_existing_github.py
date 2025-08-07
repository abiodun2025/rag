#!/usr/bin/env python3
"""
Connect Existing GitHub Configuration to MCP Server
"""

import os
import json
import subprocess
from pathlib import Path

def connect_existing_github():
    """Connect existing GitHub configuration to MCP server."""
    
    print("🔗 Connecting Existing GitHub Configuration")
    print("=" * 60)
    print()
    
    # Check existing GitHub config
    github_config_path = "/Users/ola/Desktop/working-mcp-server/github_config.json"
    if Path(github_config_path).exists():
        with open(github_config_path, 'r') as f:
            github_config = json.load(f)
        
        print("📋 Found existing GitHub configuration:")
        print(f"   Username: {github_config.get('username', 'Not set')}")
        print(f"   Token: {'***' if github_config.get('token') != 'YOUR_GITHUB_TOKEN_HERE' else 'Not set'}")
        print()
    
    # Check current .env
    env_file = Path(".env")
    if env_file.exists():
        print("📋 Current .env file:")
        with open(env_file, 'r') as f:
            content = f.read()
            print(content)
        print()
    
    print("🔧 To connect your existing GitHub setup:")
    print("1. Get your GitHub Personal Access Token")
    print("2. Update the .env file with your real token")
    print("3. Restart the MCP bridge")
    print()
    
    print("💡 Quick setup:")
    print("   # Edit .env file")
    print("   nano .env")
    print()
    print("   # Replace with your actual values:")
    print("   GITHUB_TOKEN=ghp_your_actual_token_here")
    print("   GITHUB_OWNER=abiodun2025")
    print("   GITHUB_REPO=your_repository_name")
    print()
    
    print("✅ After updating, restart the MCP bridge:")
    print("   python3 switch_bridge.py github")
    print()
    
    print("🎯 This will connect your existing GitHub tools to real GitHub operations!")

if __name__ == "__main__":
    connect_existing_github() 