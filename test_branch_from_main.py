#!/usr/bin/env python3
"""
Test that branches are created from main correctly
"""

import requests
import json
import time
import subprocess
import os

def test_branch_from_main():
    """Test that branches are created from main."""
    print("🧪 Testing Branch Creation from Main")
    print("=" * 50)
    
    # Test 1: Check current branch
    print("\n📋 Test 1: Checking Current Branch")
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        current_branch = result.stdout.strip()
        print(f"✅ Current branch: {current_branch}")
    except Exception as e:
        print(f"❌ Error getting current branch: {e}")
        return False
    
    # Test 2: Check if GitHub MCP Bridge is running
    print("\n📋 Test 2: Checking GitHub MCP Bridge Health")
    try:
        response = requests.get("http://localhost:5000/health")
        if response.status_code == 200:
            print("✅ GitHub MCP Bridge is running")
        else:
            print("❌ GitHub MCP Bridge is not responding properly")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ GitHub MCP Bridge is not running on port 5000")
        print("   Start it with: python3 github_mcp_bridge.py")
        return False
    
    # Test 3: Create a test branch from main
    print("\n📋 Test 3: Creating Test Branch from Main")
    test_branch_name = f"test-from-main-{int(time.time())}"
    try:
        response = requests.post("http://localhost:5000/call", json={
            "tool": "create_branch",
            "arguments": {
                "branch_name": test_branch_name
            }
        })
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print(f"✅ Successfully created branch: {test_branch_name}")
                print(f"   Result: {result.get('result')}")
                print(f"   Created from: {result.get('created_from', 'unknown')}")
                
                # Verify the branch was created from main
                if "from main" in result.get('result', ''):
                    print("✅ Confirmed: Branch was created from main")
                else:
                    print("⚠️  Warning: Branch creation message doesn't mention 'from main'")
            else:
                print(f"❌ Failed to create branch: {result.get('error')}")
        else:
            print("❌ Failed to call create_branch")
    except Exception as e:
        print(f"❌ Error creating branch: {e}")
    
    # Test 4: Check the branch history to verify it's from main
    print("\n📋 Test 4: Verifying Branch History")
    try:
        # Get the commit hash of the new branch
        result = subprocess.run(
            ["git", "rev-parse", test_branch_name],
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        if result.returncode == 0:
            branch_commit = result.stdout.strip()
            print(f"✅ Branch commit: {branch_commit[:8]}...")
            
            # Get the commit hash of main
            result = subprocess.run(
                ["git", "rev-parse", "main"],
                capture_output=True,
                text=True,
                cwd=os.getcwd()
            )
            if result.returncode == 0:
                main_commit = result.stdout.strip()
                print(f"✅ Main commit: {main_commit[:8]}...")
                
                # Check if they're the same (branch created from main)
                if branch_commit == main_commit:
                    print("✅ SUCCESS: Branch was created from main (same commit hash)")
                else:
                    print("❌ FAILED: Branch was not created from main (different commit hash)")
                    
                    # Show the difference
                    result = subprocess.run(
                        ["git", "log", "--oneline", f"{main_commit}..{branch_commit}"],
                        capture_output=True,
                        text=True,
                        cwd=os.getcwd()
                    )
                    if result.stdout.strip():
                        print(f"   Commits ahead of main: {result.stdout.strip()}")
                    else:
                        print("   No commits ahead of main")
            else:
                print("❌ Failed to get main commit hash")
        else:
            print("❌ Failed to get branch commit hash")
    except Exception as e:
        print(f"❌ Error verifying branch history: {e}")
    
    # Test 5: Clean up - delete the test branch
    print("\n📋 Test 5: Cleaning Up Test Branch")
    try:
        # First checkout back to main
        subprocess.run(
            ["git", "checkout", "main"],
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        
        # Delete the test branch
        result = subprocess.run(
            ["git", "branch", "-D", test_branch_name],
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        if result.returncode == 0:
            print(f"✅ Successfully deleted test branch: {test_branch_name}")
        else:
            print(f"⚠️  Warning: Failed to delete test branch: {result.stderr}")
    except Exception as e:
        print(f"❌ Error cleaning up: {e}")
    
    print("\n🎉 Branch from Main Testing Complete!")
    return True

if __name__ == "__main__":
    test_branch_from_main() 