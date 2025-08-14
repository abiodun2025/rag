#!/usr/bin/env python3
"""
Quick script to check PR status on GitHub
"""

import requests
import json
import os
from datetime import datetime

def check_prs():
    """Check existing PRs on GitHub."""
    try:
        print("🔍 Checking existing pull requests on GitHub...")
        
        response = requests.post(
            "http://127.0.0.1:5000/call",
            json={
                "tool": "list_pull_requests",
                "arguments": {"state": "open"}
            },
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                prs = result.get("pull_requests", [])
                
                if not prs:
                    print("✅ No open pull requests found on GitHub")
                    return
                
                print(f"\n✅ Found {len(prs)} open pull request(s) on GitHub:")
                print("=" * 80)
                
                for i, pr in enumerate(prs, 1):
                    title = pr.get("title", "No title")
                    number = pr.get("number", "N/A")
                    state = pr.get("state", "unknown")
                    source_branch = pr.get("head", {}).get("ref", "unknown")
                    target_branch = pr.get("base", {}).get("ref", "unknown")
                    created_at = pr.get("created_at", "")
                    html_url = pr.get("html_url", "")
                    
                    # Format date
                    if created_at:
                        created_date = created_at.split('T')[0] if 'T' in created_at else created_at
                    else:
                        created_date = "Unknown"
                    
                    print(f"   {i:2d}. #{number} {title}")
                    print(f"       🔄 {source_branch} → {target_branch}")
                    print(f"       📅 Created: {created_date}")
                    print(f"       📊 State: {state.upper()}")
                    print(f"       🔗 URL: {html_url}")
                    
                    # Show labels if any
                    labels = pr.get("labels", [])
                    if labels:
                        label_names = [label.get("name", "") for label in labels]
                        print(f"       🏷️  Labels: {', '.join(label_names)}")
                    
                    print()  # Empty line for readability
                
                print("=" * 80)
                print("💡 You can click the URLs above to view PRs directly on GitHub")
                
            else:
                print(f"❌ Error: {result.get('error')}")
        else:
            print(f"❌ HTTP error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error checking pull requests: {e}")

def check_branch_status():
    """Check branch status to see which have open PRs."""
    try:
        print("\n🔍 Checking branch status...")
        
        response = requests.post(
            "http://127.0.0.1:5000/call",
            json={
                "tool": "list_branches",
                "arguments": {}
            },
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                branches = result.get("branches", [])
                
                print(f"\n✅ Found {len(branches)} branches:")
                print("=" * 60)
                
                for branch in branches:
                    branch_name = branch["name"]
                    if branch_name == "main":
                        continue
                    
                    # Check if this branch has an open PR
                    pr_response = requests.post(
                        "http://127.0.0.1:5000/call",
                        json={
                            "tool": "list_pull_requests",
                            "arguments": {"state": "open"}
                        },
                        timeout=10
                    )
                    
                    has_open_pr = False
                    if pr_response.status_code == 200:
                        pr_result = pr_response.json()
                        if pr_result.get("success"):
                            prs = pr_result.get("pull_requests", [])
                            for pr in prs:
                                if pr.get("head", {}).get("ref") == branch_name:
                                    has_open_pr = True
                                    pr_number = pr.get("number", "N/A")
                                    print(f"   🔄 {branch_name} → PR #{pr_number} OPEN")
                                    break
                    
                    if not has_open_pr:
                        print(f"   ✅ {branch_name} → Ready for PR")
                
                print("=" * 60)
                
            else:
                print(f"❌ Error: {result.get('error')}")
        else:
            print(f"❌ HTTP error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error checking branch status: {e}")

if __name__ == "__main__":
    print("🚀 GitHub PR Status Checker")
    print("=" * 40)
    print(f"⏰ Checked at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    check_prs()
    check_branch_status()
    
    print("\n✅ Status check complete!") 