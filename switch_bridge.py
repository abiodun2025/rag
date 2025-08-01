#!/usr/bin/env python3
"""
MCP Bridge Switcher - Switch between different MCP bridges based on operation type
"""

import subprocess
import time
import requests
import os
import signal
import sys

def check_bridge_health():
    """Check if any bridge is running on port 5000."""
    try:
        response = requests.get("http://localhost:5000/health", timeout=2)
        if response.status_code == 200:
            data = response.json()
            return data.get("server", "unknown")
        return None
    except:
        return None

def stop_current_bridge():
    """Stop any running bridge on port 5000."""
    try:
        # Kill any process using port 5000
        subprocess.run(['pkill', '-f', 'mcp.*bridge'], capture_output=True)
        subprocess.run(['pkill', '-f', 'server.py'], capture_output=True)
        time.sleep(2)
        print("✅ Stopped current bridge")
    except Exception as e:
        print(f"⚠️  Could not stop bridge: {e}")

def start_email_bridge():
    """Start the email-focused MCP bridge."""
    print("📧 Starting Email MCP Bridge...")
    stop_current_bridge()
    
    try:
        # Start the MCP HTTP bridge (email-focused)
        process = subprocess.Popen(
            [sys.executable, "mcp_http_bridge.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for it to start
        time.sleep(3)
        
        # Check if it started successfully
        if check_bridge_health() == "fastmcp_bridge":
            print("✅ Email MCP Bridge started successfully")
            print("📧 Available tools: email, desktop, count_r")
            return True
        else:
            print("❌ Failed to start Email MCP Bridge")
            return False
            
    except Exception as e:
        print(f"❌ Error starting Email MCP Bridge: {e}")
        return False

def start_github_bridge():
    """Start the GitHub-focused MCP bridge."""
    print("🔗 Starting GitHub MCP Bridge...")
    stop_current_bridge()
    
    try:
        # Start the GitHub MCP bridge
        process = subprocess.Popen(
            [sys.executable, "github_mcp_bridge.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for it to start
        time.sleep(3)
        
        # Check if it started successfully
        if check_bridge_health() == "github_mcp_bridge":
            print("✅ GitHub MCP Bridge started successfully")
            print("🔗 Available tools: GitHub operations, PRs, branches, reports")
            return True
        else:
            print("❌ Failed to start GitHub MCP Bridge")
            return False
            
    except Exception as e:
        print(f"❌ Error starting GitHub MCP Bridge: {e}")
        return False

def show_current_status():
    """Show current bridge status."""
    print("🔍 Current MCP Bridge Status")
    print("=" * 40)
    
    bridge_type = check_bridge_health()
    if bridge_type:
        print(f"✅ Bridge running: {bridge_type}")
        
        # Show available tools
        try:
            response = requests.get("http://localhost:5000/tools")
            if response.status_code == 200:
                tools = response.json().get("tools", [])
                print(f"📋 Available tools: {len(tools)}")
                for tool in tools:
                    print(f"   - {tool['name']}: {tool['description']}")
        except:
            print("❌ Could not fetch tools list")
    else:
        print("❌ No bridge running on port 5000")

def main():
    """Main function."""
    print("🔄 MCP Bridge Switcher")
    print("=" * 30)
    print()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 switch_bridge.py status    - Show current bridge status")
        print("  python3 switch_bridge.py email     - Start email-focused bridge")
        print("  python3 switch_bridge.py github    - Start GitHub-focused bridge")
        print("  python3 switch_bridge.py stop      - Stop current bridge")
        print()
        show_current_status()
        return
    
    command = sys.argv[1].lower()
    
    if command == "status":
        show_current_status()
        
    elif command == "email":
        if start_email_bridge():
            print("\n🎯 Email bridge ready for email operations!")
        else:
            print("\n❌ Failed to start email bridge")
            
    elif command == "github":
        # Check if GitHub credentials are configured
        if not all([os.getenv('GITHUB_TOKEN'), os.getenv('GITHUB_OWNER'), os.getenv('GITHUB_REPO')]):
            print("⚠️  GitHub credentials not configured!")
            print("   Please update your .env file with:")
            print("   GITHUB_TOKEN=your_github_token")
            print("   GITHUB_OWNER=your_github_username")
            print("   GITHUB_REPO=your_repository_name")
            print()
            print("   Or run: python3 setup_github.py")
            return
            
        if start_github_bridge():
            print("\n🎯 GitHub bridge ready for full branch workflow!")
        else:
            print("\n❌ Failed to start GitHub bridge")
            
    elif command == "stop":
        stop_current_bridge()
        print("✅ Bridge stopped")
        
    else:
        print(f"❌ Unknown command: {command}")
        print("Use: status, email, github, or stop")

if __name__ == "__main__":
    main() 