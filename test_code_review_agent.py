#!/usr/bin/env python3
"""
Test Automated Code Review Agent
Demonstrates the automated code review agent functionality.
"""

import requests
import json
import sys

def test_code_review_agent():
    """Test the automated code review agent."""
    
    base_url = "http://127.0.0.1:5000"  # MCP Bridge server
    
    print("🔍 Automated Code Review Agent Test")
    print("=" * 60)
    print("Testing automated code review functionality")
    print()
    
    # Test 1: List code reviews
    print("1️⃣ Testing List Code Reviews")
    print("-" * 40)
    
    response = requests.post(
        f"{base_url}/call",
        json={
            "tool": "list_code_reviews",
            "arguments": {}
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            reviews = result.get("reviews", [])
            print(f"✅ Found {len(reviews)} code reviews")
            for review in reviews:
                print(f"   PR #{review['pr_number']} - Score: {review['overall_score']}/100 - {review['status']}")
                print(f"     Report: {review['report_url']}")
        else:
            print(f"❌ Failed: {result.get('error')}")
    else:
        print(f"❌ HTTP Error: {response.status_code}")
    
    print()
    
    # Test 2: Automated code review (simulated)
    print("2️⃣ Testing Automated Code Review")
    print("-" * 40)
    
    response = requests.post(
        f"{base_url}/call",
        json={
            "tool": "automated_code_review",
            "arguments": {
                "pr_number": 1
            }
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            print(f"✅ Code review completed!")
            print(f"   Review ID: {result.get('review_id')}")
            print(f"   PR Number: {result.get('pr_number')}")
            print(f"   Overall Score: {result.get('overall_score')}/100")
            print(f"   Status: {result.get('status')}")
            print(f"   Findings Count: {result.get('findings_count')}")
            print(f"   Report URL: {result.get('report_url')}")
            print(f"   Summary: {result.get('summary')}")
            print(f"   Recommendations: {', '.join(result.get('recommendations', []))}")
            
            # Test 3: Get specific review report
            print()
            print("3️⃣ Testing Get Review Report")
            print("-" * 40)
            
            review_id = result.get('review_id')
            if review_id:
                response2 = requests.post(
                    f"{base_url}/call",
                    json={
                        "tool": "get_code_review_report",
                        "arguments": {
                            "review_id": review_id
                        }
                    }
                )
                
                if response2.status_code == 200:
                    result2 = response2.json()
                    if result2.get("success"):
                        print(f"✅ Review report retrieved!")
                        print(f"   Report URL: {result2.get('report_url')}")
                    else:
                        print(f"❌ Failed to get report: {result2.get('error')}")
                else:
                    print(f"❌ HTTP Error: {response2.status_code}")
            
            # Test 4: Open review report
            print()
            print("4️⃣ Testing Open Review Report")
            print("-" * 40)
            
            if review_id:
                response3 = requests.post(
                    f"{base_url}/call",
                    json={
                        "tool": "open_review_report",
                        "arguments": {
                            "review_id": review_id
                        }
                    }
                )
                
                if response3.status_code == 200:
                    result3 = response3.json()
                    if result3.get("success"):
                        print(f"✅ Review report opened in browser!")
                    else:
                        print(f"❌ Failed to open report: {result3.get('error')}")
                else:
                    print(f"❌ HTTP Error: {response3.status_code}")
        else:
            print(f"❌ Failed: {result.get('error')}")
    else:
        print(f"❌ HTTP Error: {response.status_code}")
    
    print()
    print("🎉 Code Review Agent Test Complete!")
    print()
    print("📋 Available Commands:")
    print("   automated_code_review - Review a pull request")
    print("   list_code_reviews - List all review reports")
    print("   get_code_review_report - Get specific report")
    print("   open_review_report - Open report in browser")

def test_real_code_review():
    """Test with the actual code review agent."""
    
    print("🔍 Testing Real Code Review Agent")
    print("=" * 50)
    
    try:
        from code_review_agent import CodeReviewAgent
        
        agent = CodeReviewAgent()
        
        # Test with a PR number
        pr_number = input("Enter PR number to review (or press Enter to skip): ").strip()
        
        if pr_number:
            try:
                pr_number = int(pr_number)
                result = agent.review_pull_request(pr_number)
                
                if result["success"]:
                    print(f"✅ Real code review completed!")
                    print(f"   Review ID: {result['review_id']}")
                    print(f"   Score: {result['overall_score']}/100")
                    print(f"   Status: {result['status']}")
                    print(f"   Findings: {result['findings_count']}")
                    print(f"   Report URL: {result['report_url']}")
                    
                    # Open report in browser
                    open_report = input("Open report in browser? (y/N): ").strip().lower()
                    if open_report in ['y', 'yes']:
                        agent.open_review_report(result['review_id'])
                else:
                    print(f"❌ Review failed: {result['error']}")
            except ValueError:
                print("❌ Invalid PR number")
        else:
            # Show review history
            history = agent.get_review_history()
            if history:
                print("📋 Review History:")
                for review in history[:5]:  # Show last 5
                    print(f"   PR #{review['pr_number']} - Score: {review['overall_score']}/100 - {review['status']}")
                    print(f"     Report: {review['report_url']}")
                    print()
            else:
                print("No review history found")
                
    except ImportError:
        print("❌ Code review agent not available")
        print("Make sure code_review_agent.py is in the same directory")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "real":
        test_real_code_review()
    else:
        test_code_review_agent()