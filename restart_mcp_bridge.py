#!/usr/bin/env python3
"""
Script to restart the MCP bridge server with new branch listing functionality
"""

import subprocess
import time
import requests
import signal
import os
import sys

def find_mcp_bridge_process():
    """Find the MCP bridge process."""
    try:
        result = subprocess.run(['pgrep', '-f', 'github_mcp_bridge.py'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            pids = result.stdout.strip().split('\n')
            return [int(pid) for pid in pids if pid]
    except Exception:
        pass
    return []

def stop_mcp_bridge():
    """Stop the MCP bridge server."""
    pids = find_mcp_bridge_process()
    if pids:
        print(f"🛑 Stopping MCP bridge processes: {pids}")
        for pid in pids:
            try:
                os.kill(pid, signal.SIGTERM)
                print(f"   Sent SIGTERM to PID {pid}")
            except Exception as e:
                print(f"   Error stopping PID {pid}: {e}")
        
        # Wait for processes to stop
        time.sleep(2)
        
        # Force kill if still running
        remaining_pids = find_mcp_bridge_process()
        if remaining_pids:
            print(f"⚠️  Force killing remaining processes: {remaining_pids}")
            for pid in remaining_pids:
                try:
                    os.kill(pid, signal.SIGKILL)
                    print(f"   Sent SIGKILL to PID {pid}")
                except Exception as e:
                    print(f"   Error force killing PID {pid}: {e}")
    else:
        print("ℹ️  No MCP bridge processes found")

def start_mcp_bridge():
    """Start the MCP bridge server."""
    print("🚀 Starting MCP bridge server...")
    try:
        # Start in background
        process = subprocess.Popen(
            [sys.executable, 'github_mcp_bridge.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print(f"   Started with PID: {process.pid}")
        return process
    except Exception as e:
        print(f"❌ Error starting MCP bridge: {e}")
        return None

def wait_for_mcp_bridge():
    """Wait for MCP bridge to be ready."""
    print("⏳ Waiting for MCP bridge to be ready...")
    max_attempts = 30
    for attempt in range(max_attempts):
        try:
            response = requests.get("http://127.0.0.1:5000/health", timeout=2)
            if response.status_code == 200:
                health = response.json()
                print(f"✅ MCP bridge is ready: {health}")
                return True
        except Exception:
            pass
        
        time.sleep(1)
        if attempt % 5 == 0:
            print(f"   Still waiting... ({attempt + 1}/{max_attempts})")
    
    print("❌ MCP bridge failed to start within timeout")
    return False

def test_branch_listing():
    """Test the branch listing functionality."""
    print("\n🔍 Testing branch listing functionality...")
    try:
        response = requests.post(
            "http://127.0.0.1:5000/call",
            json={
                "tool": "list_branches",
                "arguments": {}
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                branches = result.get("branches", [])
                print(f"✅ Successfully listed {len(branches)} branches!")
                return True
            else:
                print(f"❌ Branch listing failed: {result.get('error')}")
                return False
        else:
            print(f"❌ HTTP error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing branch listing: {e}")
        return False

def main():
    """Main function to restart MCP bridge."""
    print("🔄 Restarting MCP Bridge with Branch Listing")
    print("=" * 50)
    
    # Stop existing MCP bridge
    stop_mcp_bridge()
    
    # Start new MCP bridge
    process = start_mcp_bridge()
    if not process:
        return
    
    # Wait for it to be ready
    if not wait_for_mcp_bridge():
        print("❌ Failed to start MCP bridge")
        return
    
    # Test branch listing
    if test_branch_listing():
        print("\n🎉 MCP bridge restarted successfully with branch listing!")
        print("   You can now use the 'branches' command in the master agent CLI")
    else:
        print("\n❌ Branch listing test failed")
    
    print(f"\n📋 MCP bridge is running on http://127.0.0.1:5000")
    print("   Press Ctrl+C to stop")

if __name__ == "__main__":
    try:
        main()
        # Keep the script running to maintain the MCP bridge process
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Stopping MCP bridge...")
        stop_mcp_bridge()
        print("✅ MCP bridge stopped") 