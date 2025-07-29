#!/usr/bin/env python3
"""
Simple Interactive Test for Pull Request Agent
Quick test script for testing pull request functionality.
"""

import requests
import json

def test_pull_request_simple():
    """Simple interactive test for pull request agent."""
    
    base_url = "http://127.0.0.1:5000"  # MCP Bridge server
    
    print("🔀 Simple Pull Request Agent Test")
    print("=" * 40)
    print("Quick test of pull request functionality")
    print()
    
    # Test 1: Create a pull request
    print("1️⃣ Creating a pull request...")
    
    create_response = requests.post(
        f"{base_url}/call_tool",
        json={
            "tool_name": "create_pull_request",
            "arguments": {
                "title": "Add new feature",
                "description": "This is a test pull request",
                "source_branch": "feature/test",
                "target_branch": "main",
                "repository": "test-repo"
            }
        }
    )
    
    if create_response.status_code == 200:
        result = create_response.json()
        if result.get("success"):
            pr_id = result.get("pr_id")
            print(f"✅ Pull request created!")
            print(f"   ID: {pr_id}")
            print(f"   Title: {result.get('title')}")
            print(f"   URL: {result.get('url')}")
        else:
            print(f"❌ Failed: {result.get('error')}")
            return
    else:
        print(f"❌ HTTP error: {create_response.status_code}")
        return
    
    # Test 2: List pull requests
    print("\n2️⃣ Listing pull requests...")
    
    list_response = requests.post(
        f"{base_url}/call_tool",
        json={
            "tool_name": "list_pull_requests",
            "arguments": {
                "repository": "test-repo",
                "status": "open",
                "limit": 5
            }
        }
    )
    
    if list_response.status_code == 200:
        result = list_response.json()
        if result.get("success"):
            pull_requests = result.get("pull_requests", [])
            print(f"✅ Found {len(pull_requests)} pull requests")
            for pr in pull_requests:
                print(f"   - {pr.get('title')} (ID: {pr.get('pr_id')})")
        else:
            print(f"❌ Failed: {result.get('error')}")
    else:
        print(f"❌ HTTP error: {list_response.status_code}")
    
    # Test 3: Review the pull request
    print(f"\n3️⃣ Reviewing pull request {pr_id}...")
    
    review_response = requests.post(
        f"{base_url}/call_tool",
        json={
            "tool_name": "review_pull_request",
            "arguments": {
                "pr_id": pr_id,
                "review_type": "approve",
                "comments": ["Looks good!", "Ready to merge"],
                "reviewer": "Test Reviewer"
            }
        }
    )
    
    if review_response.status_code == 200:
        result = review_response.json()
        if result.get("success"):
            print(f"✅ Pull request reviewed!")
            print(f"   Review ID: {result.get('review_id')}")
            print(f"   Type: {result.get('review_type')}")
            print(f"   Reviewer: {result.get('reviewer')}")
        else:
            print(f"❌ Failed: {result.get('error')}")
    else:
        print(f"❌ HTTP error: {review_response.status_code}")
    
    print("\n🎉 Simple test completed!")

if __name__ == "__main__":
    test_pull_request_simple()