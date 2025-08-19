#!/usr/bin/env python3
"""
Debug script to test PR analysis
"""

import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.github_code_reviewer import GitHubCodeReviewer

def test_pr_analysis():
    """Test PR analysis with a real PR."""
    
    # Initialize the reviewer
    reviewer = GitHubCodeReviewer()
    
    print("🔍 Testing PR analysis...")
    print("=" * 50)
    
    # Test with PR #6
    owner = "abiodun2025"
    repo = "rag"
    pr_number = 6
    
    print(f"📊 Analyzing PR #{pr_number} in {owner}/{repo}...")
    
    # Get PR details
    pr_result = reviewer.review_pull_request(owner, repo, pr_number)
    
    if not pr_result["success"]:
        print(f"❌ Failed to get PR: {pr_result.get('error', 'Unknown error')}")
        return
    
    print(f"✅ PR fetched successfully")
    print(f"   Title: {pr_result.get('title', 'N/A')}")
    print(f"   Author: {pr_result.get('author', 'N/A')}")
    print(f"   Results: {len(pr_result.get('results', []))}")
    
    # Analyze each result
    for i, result in enumerate(pr_result.get("results", []), 1):
        print(f"\n📁 File {i}: {result.get('file', 'N/A')}")
        print(f"   Status: {result.get('status', 'N/A')}")
        print(f"   Additions: {result.get('additions', 0)}")
        print(f"   Deletions: {result.get('deletions', 0)}")
        
        if "report" in result:
            report = result["report"]
            print(f"   Score: {report.get('score', 'N/A')}")
            print(f"   Grade: {report.get('grade', 'N/A')}")
            
            issues = report.get("issues", {})
            print(f"   Total Issues: {issues.get('total', 0)}")
            print(f"   Critical: {issues.get('critical', 0)}")
            print(f"   High: {issues.get('high', 0)}")
            print(f"   Medium: {issues.get('medium', 0)}")
            print(f"   Low: {issues.get('low', 0)}")
            
            # Check if there are any issues
            issue_details = issues.get("details", [])
            if issue_details:
                print(f"   📝 Issues found:")
                for j, issue in enumerate(issue_details, 1):
                    print(f"      {j}. Line {issue.get('line')}: {issue.get('severity')} - {issue.get('message')}")
            else:
                print(f"   ❌ No issues found!")
                
                # Let's check the diff content
                diff_summary = report.get("diff_summary", {})
                added_lines = diff_summary.get("added_lines", [])
                removed_lines = diff_summary.get("removed_lines", [])
                
                print(f"   🔍 Diff Analysis:")
                print(f"      Added lines: {len(added_lines)}")
                print(f"      Removed lines: {len(removed_lines)}")
                
                if added_lines:
                    print(f"   📝 Sample added lines:")
                    for k, line_info in enumerate(added_lines[:3], 1):
                        print(f"      {k}. Line {line_info.get('line_number')}: {line_info.get('content', '')[:50]}...")
                else:
                    print(f"   ❌ No added lines found in diff!")
        else:
            print(f"   ❌ No report generated!")
    
    # Check the summary
    summary = pr_result.get("summary", {})
    print(f"\n📊 Overall Summary:")
    print(f"   Average Score: {summary.get('average_score', 'N/A')}")
    print(f"   Overall Grade: {summary.get('overall_grade', 'N/A')}")
    print(f"   Total Issues: {summary.get('total_issues', 'N/A')}")

def test_diff_parsing():
    """Test diff parsing specifically."""
    
    reviewer = GitHubCodeReviewer()
    
    print("\n🔍 Testing diff parsing...")
    print("=" * 50)
    
    # Get the raw diff for PR #6
    owner = "abiodun2025"
    repo = "rag"
    pr_number = 6
    
    # Get PR diff
    pr_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
    diff_url = f"{pr_url}.diff"
    
    import requests
    headers = {"Authorization": f"token {os.getenv('GITHUB_TOKEN')}"}
    
    response = requests.get(diff_url, headers=headers)
    if response.status_code == 200:
        diff_content = response.text
        print(f"✅ Diff fetched successfully ({len(diff_content)} characters)")
        
        # Test diff extraction for a specific file
        files_response = requests.get(f"{pr_url}/files", headers=headers)
        if files_response.status_code == 200:
            files_data = files_response.json()
            
            for file_info in files_data:
                if file_info['filename'].endswith('.py'):
                    filename = file_info['filename']
                    print(f"\n📁 Testing diff extraction for: {filename}")
                    
                    file_diff = reviewer._extract_file_diff(diff_content, filename)
                    if file_diff:
                        print(f"   ✅ File diff extracted ({len(file_diff)} characters)")
                        
                        # Test diff analysis
                        report = reviewer._analyze_diff_content(file_diff, filename)
                        print(f"   📊 Analysis result:")
                        print(f"      Score: {report.get('score', 'N/A')}")
                        print(f"      Grade: {report.get('grade', 'N/A')}")
                        print(f"      Issues: {report.get('issues', {}).get('total', 0)}")
                        
                        # Check added lines
                        added_lines = report.get("diff_summary", {}).get("added_lines", [])
                        print(f"      Added lines: {len(added_lines)}")
                        
                        if added_lines:
                            print(f"      📝 Sample added lines:")
                            for i, line_info in enumerate(added_lines[:3], 1):
                                content = line_info.get('content', '')[:50]
                                print(f"         {i}. Line {line_info.get('line_number')}: {content}...")
                    else:
                        print(f"   ❌ No diff extracted for {filename}")
    else:
        print(f"❌ Failed to fetch diff: {response.status_code}")

if __name__ == "__main__":
    test_pr_analysis()
    test_diff_parsing() 