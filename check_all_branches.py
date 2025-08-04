#!/usr/bin/env python3
"""
Script to check which branches have new commits
"""

import requests
import json

def check_all_branches():
    """Check all branches for new commits."""
    print("🔍 Checking which branches have new commits...")
    print("=" * 60)
    
    # First, get all branches
    try:
        response = requests.post(
            "http://127.0.0.1:5000/call",
            json={"tool": "list_branches", "arguments": {}},
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to get branches: {response.status_code}")
            return
        
        result = response.json()
        if not result.get("success"):
            print(f"❌ Error: {result.get('error')}")
            return
        
        branches = result.get("branches", [])
        print(f"📋 Found {len(branches)} branches to check")
        print()
        
        # Check each branch for new commits
        branches_with_commits = []
        branches_without_commits = []
        
        for branch in branches:
            branch_name = branch["name"]
            
            # Skip main branch
            if branch_name == "main":
                continue
                
            print(f"🔍 Checking {branch_name}...", end=" ")
            
            try:
                response = requests.post(
                    "http://127.0.0.1:5000/call",
                    json={
                        "tool": "check_branch_commits",
                        "arguments": {"source_branch": branch_name, "target_branch": "main"}
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("success"):
                        details = result.get("details", {})
                        has_commits = details.get("has_new_commits", False)
                        
                        if has_commits:
                            ahead_by = details.get("ahead_by", 0)
                            print(f"✅ Has {ahead_by} new commits")
                            branches_with_commits.append({
                                "name": branch_name,
                                "ahead_by": ahead_by,
                                "message": details.get("message", "")
                            })
                        else:
                            print("⚠️  No new commits")
                            branches_without_commits.append(branch_name)
                    else:
                        print(f"❌ Error: {result.get('error')}")
                else:
                    print(f"❌ HTTP error: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Exception: {e}")
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 SUMMARY")
        print("=" * 60)
        
        if branches_with_commits:
            print(f"\n✅ Branches with new commits ({len(branches_with_commits)}):")
            for branch in branches_with_commits:
                print(f"   • {branch['name']}: {branch['ahead_by']} commits ahead")
                print(f"     📝 {branch['message']}")
        else:
            print("\n❌ No branches with new commits found")
        
        if branches_without_commits:
            print(f"\n⚠️  Branches without new commits ({len(branches_without_commits)}):")
            for branch in branches_without_commits:
                print(f"   • {branch}")
        
        print(f"\n💡 Ready for PR creation: {len(branches_with_commits)} branches")
        print(f"💡 Need commits first: {len(branches_without_commits)} branches")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_all_branches() 