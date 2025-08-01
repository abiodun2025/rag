#!/usr/bin/env python3
"""
Test script to verify create PR workflow functionality
"""

import requests
import json
import time
from master_agent import MasterAgent

def test_create_pr_workflow():
    """Test the create PR workflow functionality."""
    print("🔍 Testing Create PR Workflow")
    print("=" * 50)
    
    # Initialize master agent
    try:
        master = MasterAgent()
        print("✅ Master Agent initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize Master Agent: {e}")
        return
    
    # Test 1: List branches first
    print("\n📋 Step 1: Listing available branches...")
    try:
        response = master._execute_branch_listing()
        if response and response.get("success"):
            branches = response.get("branches", [])
            print(f"✅ Found {len(branches)} branches")
            
            # Find a branch that might work for PR creation
            available_branches = []
            for branch in branches:
                if branch["name"] not in ["main", "master"]:
                    available_branches.append(branch["name"])
            
            print(f"📋 Available branches for PR creation: {available_branches[:5]}...")
            
            if available_branches:
                test_branch = available_branches[0]
                print(f"🎯 Using branch: {test_branch}")
            else:
                print("❌ No suitable branches found")
                return
        else:
            print(f"❌ Failed to list branches: {response.get('error')}")
            return
    except Exception as e:
        print(f"❌ Error listing branches: {e}")
        return
    
    # Test 2: Create a workflow
    print(f"\n📋 Step 2: Creating PR workflow...")
    try:
        workflow_id = master.create_workflow(
            "create_pr",
            {
                "title": f"Test PR from Workflow - {int(time.time())}",
                "description": "Testing PR creation from master agent workflow",
                "source_branch": test_branch,
                "target_branch": "main"
            }
        )
        print(f"✅ Created workflow: {workflow_id}")
        
        # Wait for execution
        print("⏳ Waiting for workflow execution...")
        time.sleep(3)
        
        # Check status
        status = master.get_workflow_status(workflow_id)
        print(f"📊 Workflow status: {json.dumps(status, indent=2)}")
        
    except Exception as e:
        print(f"❌ Error creating workflow: {e}")
        return
    
    # Test 3: List existing PRs
    print(f"\n📋 Step 3: Listing existing PRs...")
    try:
        response = requests.post(
            "http://127.0.0.1:5000/call",
            json={
                "tool": "list_pull_requests",
                "arguments": {}
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                prs = result.get("pull_requests", [])
                print(f"✅ Found {len(prs)} existing pull requests:")
                for pr in prs[:3]:  # Show first 3
                    print(f"   PR #{pr['number']}: {pr['title']} ({pr['head_branch']} → {pr['base_branch']})")
            else:
                print(f"❌ Failed to list PRs: {result.get('error')}")
        else:
            print(f"❌ HTTP error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error listing PRs: {e}")

if __name__ == "__main__":
    test_create_pr_workflow() 