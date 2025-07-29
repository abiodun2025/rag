#!/usr/bin/env python3
"""
Test script for Real-Time Pull Request Agent
Tests all pull request and code review functionality through the MCP bridge.
"""

import asyncio
import json
import requests
import time
from datetime import datetime

def test_pull_request_agent():
    """Test the pull request agent with comprehensive scenarios."""
    
    base_url = "http://127.0.0.1:5000"  # MCP Bridge server
    
    print("🔀 Real-Time Pull Request Agent Test")
    print("=" * 60)
    print("Testing pull request creation, review, and management functionality")
    print()
    
    # Test 1: Direct MCP Bridge Testing
    print("1️⃣ Testing Direct MCP Bridge Pull Request Tools")
    print("-" * 50)
    
    # Test create_pull_request
    print("\n📝 Test 1.1: Create Pull Request")
    create_pr_response = requests.post(
        f"{base_url}/call_tool",
        json={
            "tool_name": "create_pull_request",
            "arguments": {
                "title": "Add new authentication feature",
                "description": "This PR adds OAuth2 authentication to the application",
                "source_branch": "feature/auth",
                "target_branch": "main",
                "repository": "my-app"
            }
        }
    )
    
    if create_pr_response.status_code == 200:
        result = create_pr_response.json()
        if result.get("success"):
            pr_id = result.get("pr_id")
            print(f"✅ Pull request created successfully!")
            print(f"   PR ID: {pr_id}")
            print(f"   Title: {result.get('title')}")
            print(f"   URL: {result.get('url')}")
            print(f"   Status: {result.get('status')}")
        else:
            print(f"❌ Failed to create pull request: {result.get('error')}")
            return
    else:
        print(f"❌ HTTP error: {create_pr_response.status_code}")
        return
    
    # Test list_pull_requests
    print("\n📋 Test 1.2: List Pull Requests")
    list_pr_response = requests.post(
        f"{base_url}/call_tool",
        json={
            "tool_name": "list_pull_requests",
            "arguments": {
                "repository": "my-app",
                "status": "open",
                "limit": 10
            }
        }
    )
    
    if list_pr_response.status_code == 200:
        result = list_pr_response.json()
        if result.get("success"):
            pull_requests = result.get("pull_requests", [])
            print(f"✅ Found {len(pull_requests)} pull requests")
            for pr in pull_requests:
                print(f"   - {pr.get('title')} (ID: {pr.get('pr_id')})")
        else:
            print(f"❌ Failed to list pull requests: {result.get('error')}")
    else:
        print(f"❌ HTTP error: {list_pr_response.status_code}")
    
    # Test review_pull_request
    print("\n🔍 Test 1.3: Review Pull Request")
    review_pr_response = requests.post(
        f"{base_url}/call_tool",
        json={
            "tool_name": "review_pull_request",
            "arguments": {
                "pr_id": pr_id,
                "review_type": "approve",
                "comments": [
                    "Great implementation!",
                    "Please add unit tests for the new authentication methods"
                ],
                "reviewer": "Code Reviewer"
            }
        }
    )
    
    if review_pr_response.status_code == 200:
        result = review_pr_response.json()
        if result.get("success"):
            print(f"✅ Pull request reviewed successfully!")
            print(f"   Review ID: {result.get('review_id')}")
            print(f"   Review Type: {result.get('review_type')}")
            print(f"   Reviewer: {result.get('reviewer')}")
            print(f"   Comments: {len(result.get('comments', []))}")
        else:
            print(f"❌ Failed to review pull request: {result.get('error')}")
    else:
        print(f"❌ HTTP error: {review_pr_response.status_code}")
    
    # Test code_review
    print("\n🔍 Test 1.4: Code Review Analysis")
    code_review_response = requests.post(
        f"{base_url}/call_tool",
        json={
            "tool_name": "code_review",
            "arguments": {
                "pr_id": pr_id,
                "code_changes": [
                    {
                        "file": "auth.py",
                        "changes": "Added OAuth2 authentication methods",
                        "lines_added": 50,
                        "lines_removed": 5
                    }
                ],
                "reviewer": "Senior Developer"
            }
        }
    )
    
    if code_review_response.status_code == 200:
        result = code_review_response.json()
        if result.get("success"):
            print(f"✅ Code review completed!")
            print(f"   Review ID: {result.get('review_id')}")
            print(f"   Issues Found: {result.get('issues_found', 0)}")
            print(f"   Suggestions: {len(result.get('suggestions', []))}")
        else:
            print(f"❌ Failed to perform code review: {result.get('error')}")
    else:
        print(f"❌ HTTP error: {code_review_response.status_code}")
    
    # Test 2: Smart Agent Integration Testing
    print("\n\n2️⃣ Testing Smart Agent Pull Request Integration")
    print("-" * 50)
    
    smart_agent_url = "http://localhost:8058"
    
    # Test smart agent with pull request requests
    smart_agent_tests = [
        {
            "message": "create a pull request for the authentication feature",
            "description": "Smart agent pull request creation"
        },
        {
            "message": "review the latest pull request in my-app repository",
            "description": "Smart agent pull request review"
        },
        {
            "message": "list all open pull requests",
            "description": "Smart agent list pull requests"
        }
    ]
    
    for i, test_case in enumerate(smart_agent_tests, 1):
        print(f"\n🧠 Test 2.{i}: {test_case['description']}")
        print(f"Message: {test_case['message']}")
        
        try:
            response = requests.post(
                f"{smart_agent_url}/smart-agent/process",
                json={
                    "message": test_case['message'],
                    "user_id": "test_user",
                    "session_id": None,
                    "search_type": "hybrid"
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                smart_result = result.get('smart_agent_result', {})
                intent_analysis = smart_result.get('intent_analysis', {})
                execution_result = smart_result.get('execution_result', {})
                
                print(f"✅ Success!")
                print(f"   Intent: {intent_analysis.get('intent')}")
                print(f"   Confidence: {intent_analysis.get('confidence', 0):.2f}")
                print(f"   Success: {execution_result.get('success')}")
                print(f"   Message: {execution_result.get('message', 'No message')}")
                
            else:
                print(f"❌ HTTP error: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
    
    # Test 3: Real-time Workflow Testing
    print("\n\n3️⃣ Testing Real-time Pull Request Workflow")
    print("-" * 50)
    
    workflow_steps = [
        {
            "step": "Create PR",
            "tool": "create_pull_request",
            "arguments": {
                "title": "Fix critical security vulnerability",
                "description": "Addresses CVE-2024-1234 in authentication module",
                "source_branch": "hotfix/security",
                "target_branch": "main"
            }
        },
        {
            "step": "List PRs",
            "tool": "list_pull_requests",
            "arguments": {
                "status": "open",
                "limit": 5
            }
        },
        {
            "step": "Review PR",
            "tool": "review_pull_request",
            "arguments": {
                "pr_id": "PR_workflow_test",
                "review_type": "request_changes",
                "comments": ["Security review required", "Add more test coverage"]
            }
        },
        {
            "step": "Code Review",
            "tool": "code_review",
            "arguments": {
                "pr_id": "PR_workflow_test",
                "code_changes": [
                    {
                        "file": "security.py",
                        "changes": "Fixed authentication bypass vulnerability",
                        "lines_added": 15,
                        "lines_removed": 8
                    }
                ]
            }
        }
    ]
    
    workflow_results = []
    
    for i, step in enumerate(workflow_steps, 1):
        print(f"\n🔄 Step {i}: {step['step']}")
        
        response = requests.post(
            f"{base_url}/call_tool",
            json={
                "tool_name": step['tool'],
                "arguments": step['arguments']
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            workflow_results.append({
                "step": step['step'],
                "success": result.get("success", False),
                "result": result.get("result", "No result")
            })
            
            if result.get("success"):
                print(f"✅ {step['step']} completed successfully")
                print(f"   Result: {result.get('result', 'No result')}")
            else:
                print(f"❌ {step['step']} failed: {result.get('error')}")
        else:
            print(f"❌ HTTP error in {step['step']}: {response.status_code}")
            workflow_results.append({
                "step": step['step'],
                "success": False,
                "result": f"HTTP {response.status_code}"
            })
    
    # Test 4: Performance Testing
    print("\n\n4️⃣ Performance Testing")
    print("-" * 50)
    
    performance_tests = []
    
    for i in range(5):
        start_time = time.time()
        
        response = requests.post(
            f"{base_url}/call_tool",
            json={
                "tool_name": "list_pull_requests",
                "arguments": {
                    "repository": "test-repo",
                    "status": "all",
                    "limit": 10
                }
            }
        )
        
        end_time = time.time()
        response_time = (end_time - start_time) * 1000  # Convert to milliseconds
        
        performance_tests.append({
            "test": f"List PRs #{i+1}",
            "response_time_ms": response_time,
            "success": response.status_code == 200
        })
        
        print(f"   Test {i+1}: {response_time:.2f}ms")
    
    # Calculate performance metrics
    successful_tests = [t for t in performance_tests if t['success']]
    if successful_tests:
        avg_response_time = sum(t['response_time_ms'] for t in successful_tests) / len(successful_tests)
        min_response_time = min(t['response_time_ms'] for t in successful_tests)
        max_response_time = max(t['response_time_ms'] for t in successful_tests)
        
        print(f"\n📊 Performance Summary:")
        print(f"   Average Response Time: {avg_response_time:.2f}ms")
        print(f"   Min Response Time: {min_response_time:.2f}ms")
        print(f"   Max Response Time: {max_response_time:.2f}ms")
        print(f"   Success Rate: {len(successful_tests)}/{len(performance_tests)} ({len(successful_tests)/len(performance_tests)*100:.1f}%)")
    
    # Test 5: Error Handling Testing
    print("\n\n5️⃣ Error Handling Testing")
    print("-" * 50)
    
    error_test_cases = [
        {
            "description": "Missing PR title",
            "tool": "create_pull_request",
            "arguments": {
                "description": "Test PR without title"
            }
        },
        {
            "description": "Invalid PR ID",
            "tool": "review_pull_request",
            "arguments": {
                "pr_id": "",
                "review_type": "approve"
            }
        },
        {
            "description": "Invalid review type",
            "tool": "review_pull_request",
            "arguments": {
                "pr_id": "test_pr",
                "review_type": "invalid_type"
            }
        }
    ]
    
    for test_case in error_test_cases:
        print(f"\n❌ Testing: {test_case['description']}")
        
        response = requests.post(
            f"{base_url}/call_tool",
            json={
                "tool_name": test_case['tool'],
                "arguments": test_case['arguments']
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            if not result.get("success"):
                print(f"✅ Error handled correctly: {result.get('error')}")
            else:
                print(f"⚠️ Expected error but got success")
        else:
            print(f"❌ HTTP error: {response.status_code}")
    
    # Summary
    print("\n\n📋 Test Summary")
    print("=" * 60)
    
    total_workflow_steps = len(workflow_results)
    successful_workflow_steps = len([r for r in workflow_results if r['success']])
    
    print(f"✅ Direct MCP Bridge Tests: Completed")
    print(f"✅ Smart Agent Integration Tests: Completed")
    print(f"✅ Workflow Tests: {successful_workflow_steps}/{total_workflow_steps} successful")
    print(f"✅ Performance Tests: {len(successful_tests)}/{len(performance_tests)} successful")
    print(f"✅ Error Handling Tests: Completed")
    
    print(f"\n🎉 Pull Request Agent testing completed!")
    print(f"📊 Overall Success Rate: {(successful_workflow_steps/total_workflow_steps)*100:.1f}%")

if __name__ == "__main__":
    test_pull_request_agent()