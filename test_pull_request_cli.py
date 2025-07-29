#!/usr/bin/env python3
"""
CLI-based Interactive Test for Pull Request Agent
Interactive command-line interface for testing pull request functionality.
"""

import requests
import json
import sys

def test_pull_request_cli():
    """Interactive CLI test for pull request agent."""
    
    base_url = "http://127.0.0.1:5000"  # MCP Bridge server
    
    print("🔀 Interactive Pull Request Agent Test")
    print("=" * 50)
    print("Interactive CLI for testing pull request functionality")
    print("Type 'help' for available commands, 'quit' to exit")
    print()
    
    # Store created PR IDs for testing
    created_prs = []
    
    while True:
        try:
            command = input("🔀 PR Agent> ").strip().lower()
            
            if command == 'quit' or command == 'exit':
                print("👋 Goodbye!")
                break
                
            elif command == 'help':
                print("\n📋 Available Commands:")
                print("  create <title> <description> - Create a pull request")
                print("  list [status] [limit] - List pull requests")
                print("  review <pr_id> <type> <comments> - Review a pull request")
                print("  merge <pr_id> - Merge a pull request")
                print("  code-review <pr_id> - Perform code review")
                print("  status - Check server status")
                print("  help - Show this help")
                print("  quit - Exit the test")
                print("\n📝 Examples:")
                print("  create 'Add auth feature' 'OAuth2 implementation'")
                print("  list open 10")
                print("  review PR_123 approve 'Great work!'")
                print("  merge PR_123")
                print()
                
            elif command == 'status':
                print("\n🔍 Checking server status...")
                try:
                    response = requests.get(f"{base_url}/health")
                    if response.status_code == 200:
                        print("✅ Server is running")
                    else:
                        print(f"❌ Server error: {response.status_code}")
                except Exception as e:
                    print(f"❌ Cannot connect to server: {e}")
                print()
                
            elif command.startswith('create '):
                parts = command.split(' ', 2)
                if len(parts) >= 3:
                    title = parts[1]
                    description = parts[2]
                    
                    print(f"\n📝 Creating pull request: {title}")
                    
                    response = requests.post(
                        f"{base_url}/call_tool",
                        json={
                            "tool_name": "create_pull_request",
                            "arguments": {
                                "title": title,
                                "description": description,
                                "source_branch": "feature/test",
                                "target_branch": "main",
                                "repository": "test-repo"
                            }
                        }
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        if result.get("success"):
                            pr_id = result.get("pr_id")
                            created_prs.append(pr_id)
                            print(f"✅ Pull request created!")
                            print(f"   ID: {pr_id}")
                            print(f"   Title: {result.get('title')}")
                            print(f"   URL: {result.get('url')}")
                        else:
                            print(f"❌ Failed: {result.get('error')}")
                    else:
                        print(f"❌ HTTP error: {response.status_code}")
                else:
                    print("❌ Usage: create <title> <description>")
                print()
                
            elif command.startswith('list'):
                parts = command.split()
                status = parts[1] if len(parts) > 1 else "all"
                limit = int(parts[2]) if len(parts) > 2 else 10
                
                print(f"\n📋 Listing pull requests (status: {status}, limit: {limit})...")
                
                response = requests.post(
                    f"{base_url}/call_tool",
                    json={
                        "tool_name": "list_pull_requests",
                        "arguments": {
                            "repository": "test-repo",
                            "status": status,
                            "limit": limit
                        }
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("success"):
                        pull_requests = result.get("pull_requests", [])
                        print(f"✅ Found {len(pull_requests)} pull requests")
                        for pr in pull_requests:
                            print(f"   - {pr.get('title')} (ID: {pr.get('pr_id')})")
                    else:
                        print(f"❌ Failed: {result.get('error')}")
                else:
                    print(f"❌ HTTP error: {response.status_code}")
                print()
                
            elif command.startswith('review '):
                parts = command.split(' ', 3)
                if len(parts) >= 4:
                    pr_id = parts[1]
                    review_type = parts[2]
                    comments = parts[3]
                    
                    print(f"\n🔍 Reviewing pull request {pr_id}...")
                    
                    response = requests.post(
                        f"{base_url}/call_tool",
                        json={
                            "tool_name": "review_pull_request",
                            "arguments": {
                                "pr_id": pr_id,
                                "review_type": review_type,
                                "comments": [comments],
                                "reviewer": "CLI Tester"
                            }
                        }
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        if result.get("success"):
                            print(f"✅ Pull request reviewed!")
                            print(f"   Review ID: {result.get('review_id')}")
                            print(f"   Type: {result.get('review_type')}")
                            print(f"   Reviewer: {result.get('reviewer')}")
                        else:
                            print(f"❌ Failed: {result.get('error')}")
                    else:
                        print(f"❌ HTTP error: {response.status_code}")
                else:
                    print("❌ Usage: review <pr_id> <type> <comments>")
                print()
                
            elif command.startswith('merge '):
                pr_id = command.split()[1]
                
                print(f"\n🔀 Merging pull request {pr_id}...")
                
                response = requests.post(
                    f"{base_url}/call_tool",
                    json={
                        "tool_name": "merge_pull_request",
                        "arguments": {
                            "pr_id": pr_id,
                            "merge_method": "squash",
                            "commit_message": f"Merged {pr_id}"
                        }
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("success"):
                        print(f"✅ Pull request merged!")
                        print(f"   Merge ID: {result.get('merge_id')}")
                        print(f"   Method: {result.get('merge_method')}")
                    else:
                        print(f"❌ Failed: {result.get('error')}")
                else:
                    print(f"❌ HTTP error: {response.status_code}")
                print()
                
            elif command.startswith('code-review '):
                pr_id = command.split()[1]
                
                print(f"\n🔍 Performing code review for {pr_id}...")
                
                response = requests.post(
                    f"{base_url}/call_tool",
                    json={
                        "tool_name": "code_review",
                        "arguments": {
                            "pr_id": pr_id,
                            "code_changes": [
                                {
                                    "file": "test.py",
                                    "changes": "Added new functionality",
                                    "lines_added": 25,
                                    "lines_removed": 5
                                }
                            ],
                            "reviewer": "CLI Code Reviewer"
                        }
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("success"):
                        print(f"✅ Code review completed!")
                        print(f"   Review ID: {result.get('review_id')}")
                        print(f"   Issues Found: {result.get('issues_found', 0)}")
                        print(f"   Suggestions: {len(result.get('suggestions', []))}")
                    else:
                        print(f"❌ Failed: {result.get('error')}")
                else:
                    print(f"❌ HTTP error: {response.status_code}")
                print()
                
            elif command == '':
                continue
                
            else:
                print(f"❌ Unknown command: {command}")
                print("Type 'help' for available commands")
                print()
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            print()

if __name__ == "__main__":
    test_pull_request_cli()