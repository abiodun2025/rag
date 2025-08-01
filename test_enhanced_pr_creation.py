#!/usr/bin/env python3
"""
Test script to demonstrate enhanced PR creation with intelligent validation
"""

import requests
import json
import time

def test_enhanced_pr_creation():
    """Test the enhanced PR creation functionality."""
    print("🔍 Testing Enhanced PR Creation with Intelligent Validation")
    print("=" * 60)
    
    # Test 1: Check available tools
    print("\n📋 Step 1: Checking available tools...")
    try:
        response = requests.get("http://127.0.0.1:5000/tools", timeout=5)
        if response.status_code == 200:
            tools = response.json()
            tool_names = [tool["name"] for tool in tools.get("tools", [])]
            print(f"✅ Available tools: {tool_names}")
            
            if "check_branch_commits" in tool_names:
                print("✅ Enhanced validation tools are available!")
            else:
                print("❌ Enhanced validation tools not found")
                return
        else:
            print(f"❌ Failed to get tools: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Error checking tools: {e}")
        return
    
    # Test 2: List branches
    print("\n📋 Step 2: Listing available branches...")
    try:
        response = requests.post(
            "http://127.0.0.1:5000/call",
            json={"tool": "list_branches", "arguments": {}},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                branches = result.get("branches", [])
                print(f"✅ Found {len(branches)} branches")
                
                # Find branches to test
                test_branches = []
                for branch in branches:
                    if branch["name"].startswith("feature/"):
                        test_branches.append(branch["name"])
                        if len(test_branches) >= 3:
                            break
                
                print(f"🎯 Test branches: {test_branches}")
            else:
                print(f"❌ Failed to list branches: {result.get('error')}")
                return
        else:
            print(f"❌ HTTP error: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Error listing branches: {e}")
        return
    
    # Test 3: Check branch commits for each test branch
    print("\n📋 Step 3: Checking branch commits...")
    for branch in test_branches:
        print(f"\n🔍 Checking {branch}...")
        try:
            response = requests.post(
                "http://127.0.0.1:5000/call",
                json={
                    "tool": "check_branch_commits",
                    "arguments": {"source_branch": branch, "target_branch": "main"}
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    details = result.get("details", {})
                    has_commits = details.get("has_new_commits", False)
                    message = details.get("message", "")
                    
                    if has_commits:
                        ahead_by = details.get("ahead_by", 0)
                        print(f"   ✅ {branch}: Has {ahead_by} new commits - {message}")
                    else:
                        print(f"   ⚠️  {branch}: No new commits - {message}")
                else:
                    print(f"   ❌ {branch}: Error - {result.get('error')}")
            else:
                print(f"   ❌ {branch}: HTTP error {response.status_code}")
        except Exception as e:
            print(f"   ❌ {branch}: Exception - {e}")
    
    # Test 4: Test enhanced PR creation
    print("\n📋 Step 4: Testing enhanced PR creation...")
    
    # Test with branch that has no new commits
    print(f"\n🔍 Testing PR creation with branch that has no new commits...")
    try:
        response = requests.post(
            "http://127.0.0.1:5000/call",
            json={
                "tool": "create_pull_request",
                "arguments": {
                    "title": "Test Enhanced PR - No Commits",
                    "description": "Testing enhanced PR creation with no new commits",
                    "source_branch": "feature/login",
                    "target_branch": "main"
                }
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if not result.get("success"):
                error = result.get("error", "")
                suggestion = result.get("suggestion", "")
                print(f"   ✅ Correctly rejected: {error}")
                print(f"   💡 Suggestion: {suggestion}")
            else:
                print(f"   ❌ Unexpected success: {result}")
        else:
            print(f"   ❌ HTTP error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Test with branch that has existing PR
    print(f"\n🔍 Testing PR creation with branch that has existing PR...")
    try:
        response = requests.post(
            "http://127.0.0.1:5000/call",
            json={
                "tool": "create_pull_request",
                "arguments": {
                    "title": "Test Enhanced PR - Existing PR",
                    "description": "Testing enhanced PR creation with existing PR",
                    "source_branch": "feature/agent_code_review",
                    "target_branch": "main"
                }
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if not result.get("success"):
                error = result.get("error", "")
                suggestion = result.get("suggestion", "")
                existing_pr = result.get("existing_pr", {})
                print(f"   ✅ Correctly rejected: {error}")
                if existing_pr:
                    print(f"   🔗 Existing PR: #{existing_pr.get('number')} - {existing_pr.get('url')}")
                print(f"   💡 Suggestion: {suggestion}")
            else:
                print(f"   ❌ Unexpected success: {result}")
        else:
            print(f"   ❌ HTTP error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    print("\n🎉 Enhanced PR creation testing completed!")
    print("\n📋 Summary of Enhancements:")
    print("   ✅ Automatic commit validation before PR creation")
    print("   ✅ Existing PR detection and suggestions")
    print("   ✅ Detailed error messages with helpful suggestions")
    print("   ✅ Branch comparison with commit counts")
    print("   ✅ Intelligent workflow that prevents invalid PRs")

if __name__ == "__main__":
    test_enhanced_pr_creation() 