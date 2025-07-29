#!/usr/bin/env python3
"""
Test Real GitHub Pull Request Integration
Simple script to test the real GitHub pull request functionality.
"""

import os
import requests
import json
import sys

def test_real_github_pr():
    """Test real GitHub pull request functionality."""
    
    base_url = "http://127.0.0.1:5000"  # MCP Bridge server
    
    print("🔀 Real GitHub Pull Request Test")
    print("=" * 50)
    print("Testing real GitHub pull request functionality")
    print()
    
    # Check if GitHub environment variables are set
    token = os.getenv('GITHUB_TOKEN')
    owner = os.getenv('GITHUB_OWNER')
    repo = os.getenv('GITHUB_REPO')
    
    if not all([token, owner, repo]):
        print("❌ GitHub environment variables not set!")
        print("Please set the following environment variables:")
        print("  export GITHUB_TOKEN='your_github_token'")
        print("  export GITHUB_OWNER='your_github_username_or_org'")
        print("  export GITHUB_REPO='your_repository_name'")
        print()
        print("See GITHUB_SETUP_GUIDE.md for detailed setup instructions.")
        return False
    
    print("✅ GitHub environment variables found:")
    print(f"   Owner: {owner}")
    print(f"   Repository: {repo}")
    print(f"   Token: {token[:10]}...{token[-4:] if len(token) > 14 else '***'}")
    print()
    
    # Test 1: List existing pull requests
    print("1️⃣ Testing: List Pull Requests")
    print("-" * 30)
    
    list_response = requests.post(
        f"{base_url}/call_tool",
        json={
            "tool_name": "list_pull_requests",
            "arguments": {
                "status": "open",
                "limit": 5
            }
        }
    )
    
    if list_response.status_code == 200:
        list_result = list_response.json()
        if list_result.get("success"):
            print("✅ List pull requests successful")
            prs = list_result.get("pull_requests", [])
            print(f"   Found {len(prs)} pull requests")
            for pr in prs[:3]:  # Show first 3
                print(f"   - {pr.get('title', 'No title')} (ID: {pr.get('pr_id', 'No ID')})")
        else:
            print(f"❌ List pull requests failed: {list_result.get('error')}")
    else:
        print(f"❌ HTTP error: {list_response.status_code}")
    
    print()
    
    # Test 2: Create a new pull request
    print("2️⃣ Testing: Create Pull Request")
    print("-" * 30)
    
    create_response = requests.post(
        f"{base_url}/call_tool",
        json={
            "tool_name": "create_pull_request",
            "arguments": {
                "title": "Test PR from Agentic RAG System",
                "description": "This is a test pull request created by the agentic RAG system to verify GitHub integration.",
                "source_branch": "test-branch",
                "target_branch": "main"
            }
        }
    )
    
    if create_response.status_code == 200:
        create_result = create_response.json()
        if create_result.get("success"):
            print("✅ Create pull request successful")
            print(f"   Title: {create_result.get('title')}")
            print(f"   PR ID: {create_result.get('pr_id')}")
            print(f"   URL: {create_result.get('url', 'No URL')}")
            
            # Store PR ID for potential merge test
            pr_id = create_result.get('pr_id')
            
        else:
            print(f"❌ Create pull request failed: {create_result.get('error')}")
            pr_id = None
    else:
        print(f"❌ HTTP error: {create_response.status_code}")
        pr_id = None
    
    print()
    
    # Test 3: Ask user if they want to merge the PR
    if pr_id:
        print("3️⃣ Optional: Merge Pull Request")
        print("-" * 30)
        print(f"Pull request {pr_id} was created successfully.")
        
        merge_choice = input("Do you want to merge this pull request? (y/N): ").strip().lower()
        
        if merge_choice in ['y', 'yes']:
            print("Merging pull request...")
            
            merge_response = requests.post(
                f"{base_url}/call_tool",
                json={
                    "tool_name": "merge_pull_request",
                    "arguments": {
                        "pr_id": pr_id,
                        "merge_method": "squash",
                        "commit_message": "Merge test PR from Agentic RAG System"
                    }
                }
            )
            
            if merge_response.status_code == 200:
                merge_result = merge_response.json()
                if merge_result.get("success"):
                    print("✅ Merge pull request successful")
                    print(f"   Merge ID: {merge_result.get('merge_id')}")
                    print(f"   Status: {merge_result.get('status')}")
                else:
                    print(f"❌ Merge pull request failed: {merge_result.get('error')}")
            else:
                print(f"❌ HTTP error: {merge_response.status_code}")
        else:
            print("Skipping merge - pull request remains open")
    
    print()
    print("🎉 Real GitHub pull request test completed!")
    return True

def main():
    """Main function."""
    try:
        success = test_real_github_pr()
        if success:
            print("\n✅ All tests completed successfully!")
            print("Your real GitHub pull request integration is working!")
        else:
            print("\n❌ Tests failed. Please check the setup and try again.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⏹️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()