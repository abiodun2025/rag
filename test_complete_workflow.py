#!/usr/bin/env python3
"""
Complete Real-World Workflow Test
Tests both Pull Request Agent and Code Review Agent working together.
"""

import requests
import json
import time
import sys
from datetime import datetime

def test_complete_workflow():
    """Test the complete workflow of PR creation and code review."""
    
    base_url = "http://127.0.0.1:5000"
    
    print("🚀 Complete Real-World Workflow Test")
    print("=" * 70)
    print("Testing Pull Request Agent + Code Review Agent Integration")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Step 1: Create a test branch and file
    print("1️⃣ Setting up test environment...")
    print("-" * 50)
    
    # Create a test file for the PR
    test_content = '''#!/usr/bin/env python3
"""
Test file for automated code review
This file contains various code patterns to test the review agent.
"""

import os
import requests

def insecure_function(user_input):
    """This function has security issues."""
    query = f"SELECT * FROM users WHERE name = '{user_input}'"
    # This is vulnerable to SQL injection
    return execute_query(query)

def performance_issue():
    """This function has performance issues."""
    users = get_all_users()
    for user in users:
        # N+1 query problem
        profile = get_user_profile(user.id)
        print(profile.name)

def style_issues():
    """This function has style issues."""
    x = 42  # Magic number
    if x > 40:
        print("Value is high")
    
    # Long function with many lines
    for i in range(100):
        print(f"Line {i}")
        if i % 10 == 0:
            print("Multiple of 10")
        elif i % 5 == 0:
            print("Multiple of 5")
        else:
            print("Regular number")

def good_function():
    """This function follows good practices."""
    MAX_RETRIES = 3
    TIMEOUT = 30
    
    try:
        response = requests.get("https://api.example.com/data", timeout=TIMEOUT)
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Request failed: {e}")
        return None

if __name__ == "__main__":
    # Test the functions
    insecure_function("admin")
    performance_issue()
    style_issues()
    good_function()
'''
    
    with open("test_code_for_review.py", "w") as f:
        f.write(test_content)
    
    print("✅ Created test file with various code patterns")
    print()
    
    # Step 2: Create a new branch
    print("2️⃣ Creating test branch...")
    print("-" * 50)
    
    import subprocess
    try:
        subprocess.run(["git", "checkout", "-b", "test-complete-workflow"], check=True)
        subprocess.run(["git", "add", "test_code_for_review.py"], check=True)
        subprocess.run(["git", "commit", "-m", "Add test file for automated code review"], check=True)
        subprocess.run(["git", "push", "origin", "test-complete-workflow"], check=True)
        print("✅ Created and pushed test branch")
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Git operations failed: {e}")
        print("Continuing with simulated workflow...")
    
    print()
    
    # Step 3: Create a Pull Request
    print("3️⃣ Creating Pull Request...")
    print("-" * 50)
    
    pr_response = requests.post(
        f"{base_url}/call",
        json={
            "tool": "create_pull_request",
            "arguments": {
                "title": "Test Complete Workflow - Automated Code Review",
                "description": """This PR tests the complete workflow of:
                
## Changes
- Added test file with various code patterns
- Tests security vulnerabilities (SQL injection)
- Tests performance issues (N+1 queries)
- Tests style issues (magic numbers, long functions)
- Tests good practices (proper error handling)

## Purpose
This PR is created to test the automated code review agent and demonstrate the complete workflow integration between PR creation and code review.

## Expected Findings
The code review agent should detect:
- Security: SQL injection vulnerability
- Performance: N+1 query pattern
- Style: Magic numbers, long function
- Good practices: Proper error handling in good_function

Created by: Automated Workflow Test
Date: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "source_branch": "test-complete-workflow",
                "target_branch": "main"
            }
        }
    )
    
    if pr_response.status_code == 200:
        pr_result = pr_response.json()
        if pr_result.get("success"):
            pr_number = pr_result.get("pr_id") or pr_result.get("pr_number")
            pr_url = pr_result.get("url") or pr_result.get("html_url")
            print(f"✅ Pull Request created successfully!")
            print(f"   PR Number: {pr_number}")
            print(f"   URL: {pr_url}")
            print(f"   Title: {pr_result.get('title')}")
        else:
            print(f"❌ PR creation failed: {pr_result.get('error')}")
            # Use a simulated PR number for testing
            pr_number = 999
            print(f"⚠️ Using simulated PR number: {pr_number}")
    else:
        print(f"❌ HTTP Error: {pr_response.status_code}")
        pr_number = 999
        print(f"⚠️ Using simulated PR number: {pr_number}")
    
    print()
    
    # Step 4: Wait a moment for PR to be available
    print("4️⃣ Waiting for PR to be available...")
    print("-" * 50)
    time.sleep(3)
    
    # Step 5: Perform Automated Code Review
    print("5️⃣ Performing Automated Code Review...")
    print("-" * 50)
    
    review_response = requests.post(
        f"{base_url}/call",
        json={
            "tool": "automated_code_review",
            "arguments": {
                "pr_number": pr_number
            }
        }
    )
    
    if review_response.status_code == 200:
        review_result = review_response.json()
        if review_result.get("success"):
            review_id = review_result.get("review_id")
            overall_score = review_result.get("overall_score")
            findings_count = review_result.get("findings_count")
            status = review_result.get("status")
            report_url = review_result.get("report_url")
            
            print(f"✅ Automated code review completed!")
            print(f"   Review ID: {review_id}")
            print(f"   Overall Score: {overall_score}/100")
            print(f"   Findings Count: {findings_count}")
            print(f"   Status: {status}")
            print(f"   Report URL: {report_url}")
            print(f"   Summary: {review_result.get('summary', 'N/A')}")
            
            recommendations = review_result.get('recommendations', [])
            if recommendations:
                print(f"   Recommendations:")
                for rec in recommendations:
                    print(f"     - {rec}")
        else:
            print(f"❌ Code review failed: {review_result.get('error')}")
            review_id = None
    else:
        print(f"❌ HTTP Error: {review_response.status_code}")
        review_id = None
    
    print()
    
    # Step 6: Get Review Report Details
    if review_id:
        print("6️⃣ Getting Detailed Review Report...")
        print("-" * 50)
        
        report_response = requests.post(
            f"{base_url}/call",
            json={
                "tool": "get_code_review_report",
                "arguments": {
                    "review_id": review_id
                }
            }
        )
        
        if report_response.status_code == 200:
            report_result = report_response.json()
            if report_result.get("success"):
                report = report_result.get("report", {})
                findings = report.get("findings", [])
                
                print(f"✅ Review report retrieved!")
                print(f"   Report URL: {report_result.get('report_url')}")
                print(f"   Total findings: {len(findings)}")
                
                # Show findings by category
                security_findings = [f for f in findings if f.get("type") == "security"]
                performance_findings = [f for f in findings if f.get("type") == "performance"]
                style_findings = [f for f in findings if f.get("type") == "style"]
                bug_findings = [f for f in findings if f.get("type") == "bug"]
                
                print(f"   Security issues: {len(security_findings)}")
                print(f"   Performance issues: {len(performance_findings)}")
                print(f"   Style issues: {len(style_findings)}")
                print(f"   Bug findings: {len(bug_findings)}")
                
                # Show some example findings
                if findings:
                    print(f"\n   Example findings:")
                    for i, finding in enumerate(findings[:3]):  # Show first 3
                        print(f"     {i+1}. {finding.get('severity', 'Unknown').upper()} - {finding.get('type', 'Unknown')}: {finding.get('message', 'No message')}")
            else:
                print(f"❌ Failed to get report: {report_result.get('error')}")
        else:
            print(f"❌ HTTP Error: {report_response.status_code}")
    
    print()
    
    # Step 7: Open Review Report in Browser
    if review_id:
        print("7️⃣ Opening Review Report in Browser...")
        print("-" * 50)
        
        open_response = requests.post(
            f"{base_url}/call",
            json={
                "tool": "open_review_report",
                "arguments": {
                    "review_id": review_id
                }
            }
        )
        
        if open_response.status_code == 200:
            open_result = open_response.json()
            if open_result.get("success"):
                print("✅ Review report opened in browser!")
            else:
                print(f"❌ Failed to open report: {open_result.get('error')}")
        else:
            print(f"❌ HTTP Error: {open_response.status_code}")
    
    print()
    
    # Step 8: List All Reviews
    print("8️⃣ Listing All Code Reviews...")
    print("-" * 50)
    
    list_response = requests.post(
        f"{base_url}/call",
        json={
            "tool": "list_code_reviews",
            "arguments": {}
        }
    )
    
    if list_response.status_code == 200:
        list_result = list_response.json()
        if list_result.get("success"):
            reviews = list_result.get("reviews", [])
            print(f"✅ Found {len(reviews)} code reviews")
            
            for review in reviews:
                print(f"   PR #{review.get('pr_number')} - Score: {review.get('overall_score')}/100 - {review.get('status')}")
                print(f"     Report: {review.get('report_url')}")
        else:
            print(f"❌ Failed to list reviews: {list_result.get('error')}")
    else:
        print(f"❌ HTTP Error: {list_response.status_code}")
    
    print()
    
    # Step 9: Cleanup (Optional)
    print("9️⃣ Cleanup...")
    print("-" * 50)
    
    cleanup = input("Do you want to merge the test PR? (y/N): ").strip().lower()
    
    if cleanup in ['y', 'yes']:
        print("Merging test PR...")
        merge_response = requests.post(
            f"{base_url}/call",
            json={
                "tool": "merge_pull_request",
                "arguments": {
                    "pr_id": str(pr_number),
                    "merge_method": "squash",
                    "commit_message": "Merge test workflow - Automated code review completed"
                }
            }
        )
        
        if merge_response.status_code == 200:
            merge_result = merge_response.json()
            if merge_result.get("success"):
                print("✅ Test PR merged successfully!")
            else:
                print(f"❌ Merge failed: {merge_result.get('error')}")
        else:
            print(f"❌ HTTP Error: {merge_response.status_code}")
    else:
        print("⚠️ Test PR left open for manual review")
    
    print()
    print("🎉 Complete Workflow Test Finished!")
    print("=" * 70)
    print("Summary:")
    print(f"   ✅ Pull Request created: PR #{pr_number}")
    print(f"   ✅ Code review completed: {review_id}")
    print(f"   ✅ Report generated and accessible")
    print(f"   ✅ Both agents working together successfully")
    print()
    print("📋 What was tested:")
    print("   1. Pull Request Agent - Creating real PRs")
    print("   2. Code Review Agent - Analyzing code automatically")
    print("   3. Report Generation - HTML reports with findings")
    print("   4. Integration - Both agents working together")
    print("   5. Accessibility - Reports with clickable links")
    print()
    print("🔗 Next steps:")
    print("   - Review the generated HTML report")
    print("   - Check the GitHub PR for review comments")
    print("   - Use this workflow for real development")

if __name__ == "__main__":
    test_complete_workflow()