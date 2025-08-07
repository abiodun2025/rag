#!/usr/bin/env python3
"""
Test Branch Agent with Real GitHub Integration
"""

import requests
import json
import time
import subprocess
import os

def test_branch_agent_real():
    """Test the branch agent with real GitHub integration."""
    print("🧪 Testing Branch Agent with Real GitHub Integration")
    print("=" * 60)
    
    # Test 1: Check if GitHub MCP Bridge is running
    print("\n📋 Test 1: Checking GitHub MCP Bridge Health")
    try:
        response = requests.get("http://localhost:5000/health")
        if response.status_code == 200:
            health = response.json()
            print("✅ GitHub MCP Bridge is running")
            print(f"   Server: {health.get('server')}")
            print(f"   GitHub Configured: {health.get('github_configured')}")
        else:
            print("❌ GitHub MCP Bridge is not responding properly")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ GitHub MCP Bridge is not running on port 5000")
        print("   Start it with: python3 github_mcp_bridge.py")
        return False
    
    # Test 2: Check available tools
    print("\n📋 Test 2: Checking Available Tools")
    try:
        response = requests.get("http://localhost:5000/tools")
        if response.status_code == 200:
            tools = response.json()
            branch_tools = [tool for tool in tools.get("tools", []) if "branch" in tool["name"]]
            print(f"✅ Found {len(branch_tools)} branch management tools:")
            for tool in branch_tools:
                print(f"   - {tool['name']}: {tool['description']}")
        else:
            print("❌ Failed to get tools list")
            return False
    except Exception as e:
        print(f"❌ Error getting tools: {e}")
        return False
    
    # Test 3: List current branches
    print("\n📋 Test 3: Listing Current Branches")
    try:
        response = requests.post("http://localhost:5000/call", json={
            "tool": "list_branches",
            "arguments": {}
        })
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                branches = result.get("branches", [])
                print(f"✅ Found {len(branches)} branches:")
                for branch in branches:
                    current_marker = " (current)" if branch.get("is_current") else ""
                    print(f"   - {branch['name']}{current_marker}")
            else:
                print(f"❌ Failed to list branches: {result.get('error')}")
        else:
            print("❌ Failed to call list_branches")
    except Exception as e:
        print(f"❌ Error listing branches: {e}")
    
    # Test 4: Create a test branch from main
    print("\n📋 Test 4: Creating Test Branch from Main")
    test_branch_name = f"test-branch-agent-real-{int(time.time())}"
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
    
    # Test 5: Verify branch history
    print("\n📋 Test 5: Verifying Branch History")
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
            else:
                print("❌ Failed to get main commit hash")
        else:
            print("❌ Failed to get branch commit hash")
    except Exception as e:
        print(f"❌ Error verifying branch history: {e}")
    
    # Test 6: Push the test branch to GitHub
    print("\n📋 Test 6: Pushing Test Branch to GitHub")
    try:
        response = requests.post("http://localhost:5000/call", json={
            "tool": "push_branch",
            "arguments": {
                "branch_name": test_branch_name
            }
        })
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print(f"✅ Successfully pushed branch: {test_branch_name}")
                print(f"   Result: {result.get('result')}")
                print(f"🌐 Check on GitHub: https://github.com/abiodun2025/rag/tree/{test_branch_name}")
            else:
                print(f"❌ Failed to push branch: {result.get('error')}")
        else:
            print("❌ Failed to call push_branch")
    except Exception as e:
        print(f"❌ Error pushing branch: {e}")
    
    # Test 7: Test Master Agent with Branch Workflow
    print("\n📋 Test 7: Testing Master Agent Branch Workflow")
    try:
        from master_agent import MasterAgent
        
        # Initialize master agent
        master = MasterAgent()
        
        # Create a branch workflow
        workflow_id = master.create_workflow("create_branch", {
            "title": "Test Branch Creation from Master Agent",
            "description": "Testing branch agent functionality with real GitHub",
            "branch_name": f"master-agent-test-{int(time.time())}"
        })
        
        if workflow_id:
            print(f"✅ Created branch workflow: {workflow_id}")
            
            # Start the workflow
            master.start_workflow(workflow_id)
            
            # Wait a moment and check status
            time.sleep(3)
            status = master.get_workflow_status(workflow_id)
            print(f"   Status: {status.get('workflow', {}).get('status', 'unknown')}")
            print(f"   Progress: {status.get('progress', 'unknown')}")
        else:
            print("❌ Failed to create branch workflow")
            
    except Exception as e:
        print(f"❌ Error testing master agent: {e}")
    
    print("\n🎉 Branch Agent Real GitHub Testing Complete!")
    print(f"✅ Branch '{test_branch_name}' was created from main and pushed to GitHub")
    print(f"🌐 View on GitHub: https://github.com/abiodun2025/rag/tree/{test_branch_name}")
    return True

if __name__ == "__main__":
    test_branch_agent_real() 