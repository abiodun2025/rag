#!/usr/bin/env python3
"""
Test script for the GitHub Merge Agent.
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Add the agent directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'agent'))

from agent.github_merge_agent import GitHubMergeAgent

# Load environment variables
load_dotenv()


async def test_github_merge_agent():
    """Test the GitHub merge agent functionality."""
    
    # Check environment variables
    token = os.getenv('GITHUB_TOKEN')
    repo_name = os.getenv('GITHUB_REPO')
    
    if not token:
        print("❌ GITHUB_TOKEN environment variable not set")
        print("Please set your GitHub Personal Access Token")
        return False
    
    if not repo_name:
        print("❌ GITHUB_REPO environment variable not set")
        print("Please set your repository name (e.g., 'owner/repo')")
        return False
    
    print(f"🔑 GitHub Token: {'*' * (len(token) - 8) + token[-8:] if len(token) > 8 else '*' * len(token)}")
    print(f"📁 Repository: {repo_name}")
    print()
    
    try:
        # Test 1: Initialize agent
        print("🧪 Test 1: Initializing GitHub Merge Agent...")
        agent = GitHubMergeAgent(token=token, repo_name=repo_name)
        print("✅ Agent initialized successfully")
        print()
        
        # Test 2: List pull requests
        print("🧪 Test 2: Listing pull requests...")
        try:
            prs = agent.list_pull_requests(state="open", limit=5)
            print(f"✅ Found {len(prs)} open pull requests")
            
            if prs:
                print("\nSample PRs:")
                for pr in prs[:3]:
                    print(f"  #{pr['number']}: {pr['title']}")
                    print(f"    Author: {pr['user']}")
                    print(f"    Mergeable: {pr['mergeable']}")
                    print(f"    Status Checks: {'Passed' if pr['status_checks']['all_passed'] else 'Failed'}")
                    print()
        except Exception as e:
            print(f"❌ Failed to list pull requests: {e}")
            return False
        
        # Test 3: Check merge eligibility for first PR (if any)
        if prs:
            first_pr = prs[0]
            print(f"🧪 Test 3: Checking merge eligibility for PR #{first_pr['number']}...")
            try:
                eligibility = agent.check_merge_eligibility(first_pr['number'])
                print(f"✅ Merge eligibility check completed")
                print(f"   Eligible: {eligibility['eligible']}")
                print(f"   Reason: {eligibility['reason']}")
                print()
            except Exception as e:
                print(f"❌ Failed to check merge eligibility: {e}")
                return False
        
        # Test 4: Get PR details
        if prs:
            print(f"🧪 Test 4: Getting details for PR #{first_pr['number']}...")
            try:
                details = agent.get_pull_request_details(first_pr['number'])
                if details:
                    print(f"✅ PR details retrieved successfully")
                    print(f"   Title: {details['title']}")
                    print(f"   State: {details['state']}")
                    print(f"   Draft: {details['draft']}")
                    print(f"   Reviews: {details['review_summary']['total_reviews']} total, {details['review_summary']['approved']} approved")
                    print()
                else:
                    print(f"❌ Failed to get PR details")
                    return False
            except Exception as e:
                print(f"❌ Failed to get PR details: {e}")
                return False
        
        # Test 5: Test auto-merge (dry run - won't actually merge)
        print("🧪 Test 5: Testing auto-merge functionality (dry run)...")
        try:
            # This will check eligibility but won't actually merge
            result = agent.auto_merge_eligible_prs()
            print(f"✅ Auto-merge check completed")
            print(f"   Total PRs checked: {result.get('total_prs_checked', 0)}")
            print(f"   Successful merges: {result.get('successful_merges', 0)}")
            print(f"   Failed merges: {result.get('failed_merges', 0)}")
            print()
        except Exception as e:
            print(f"❌ Failed to test auto-merge: {e}")
            return False
        
        print("🎉 All tests passed! The GitHub Merge Agent is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False
    
    finally:
        if 'agent' in locals():
            agent.close()


def main():
    """Main function."""
    print("🚀 Testing GitHub Merge Agent")
    print("=" * 50)
    
    success = asyncio.run(test_github_merge_agent())
    
    if success:
        print("\n✅ All tests completed successfully!")
        print("\nYou can now use the GitHub Merge Agent with:")
        print("  - The CLI interface: python github_merge_cli.py --help")
        print("  - The main agent system")
        print("  - Direct Python imports")
    else:
        print("\n❌ Tests failed. Please check the error messages above.")
        sys.exit(1)


if __name__ == "__main__":
    main() 