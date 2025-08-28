#!/usr/bin/env python3
"""
CLI interface for the GitHub Merge Agent.
"""

import os
import sys
import asyncio
import argparse
from typing import Optional
from dotenv import load_dotenv

# Add the agent directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'agent'))

from agent.github_merge_agent import GitHubMergeAgent

# Load environment variables
load_dotenv()


async def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(description="GitHub Merge Agent CLI")
    parser.add_argument("--token", help="GitHub Personal Access Token")
    parser.add_argument("--repo", help="Repository name (owner/repo)")
    parser.add_argument("--action", required=True, choices=[
        "list", "details", "check", "merge", "auto-merge"
    ], help="Action to perform")
    parser.add_argument("--pr-number", type=int, help="Pull request number")
    parser.add_argument("--state", default="open", choices=["open", "closed", "all"], 
                       help="PR state filter for listing")
    parser.add_argument("--limit", type=int, default=10, help="Maximum number of PRs to list")
    parser.add_argument("--merge-method", default="merge", choices=["merge", "squash", "rebase"],
                       help="Merge method")
    parser.add_argument("--commit-title", help="Custom commit title")
    parser.add_argument("--commit-message", help="Custom commit message")
    parser.add_argument("--auto-merge-label", help="Label for auto-merge filtering")
    
    args = parser.parse_args()
    
    # Get token and repo from args or environment
    token = args.token or os.getenv('GITHUB_TOKEN')
    repo_name = args.repo or os.getenv('GITHUB_REPO')
    
    if not token:
        print("Error: GitHub token is required. Set GITHUB_TOKEN environment variable or use --token")
        sys.exit(1)
    
    if not repo_name:
        print("Error: Repository name is required. Set GITHUB_REPO environment variable or use --repo")
        sys.exit(1)
    
    try:
        # Initialize the agent
        agent = GitHubMergeAgent(token=token, repo_name=repo_name)
        print(f"Connected to repository: {repo_name}")
        
        if args.action == "list":
            await list_pull_requests(agent, args)
        elif args.action == "details":
            await get_pr_details(agent, args)
        elif args.action == "check":
            await check_merge_eligibility(agent, args)
        elif args.action == "merge":
            await merge_pr(agent, args)
        elif args.action == "auto-merge":
            await auto_merge_prs(agent, args)
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        if 'agent' in locals():
            agent.close()


async def list_pull_requests(agent: GitHubMergeAgent, args):
    """List pull requests."""
    print(f"\nListing {args.state} pull requests (limit: {args.limit})...")
    
    prs = agent.list_pull_requests(state=args.state, limit=args.limit)
    
    if not prs:
        print("No pull requests found.")
        return
    
    print(f"\nFound {len(prs)} pull requests:")
    print("-" * 80)
    
    for pr in prs:
        status_icon = "✅" if pr['status_checks']['all_passed'] else "❌"
        merge_icon = "🟢" if pr['mergeable'] else "🔴"
        
        print(f"#{pr['number']} {status_icon}{merge_icon} {pr['title']}")
        print(f"  Author: {pr['user']} | Reviews: {pr['branch']} → {pr['base_branch']}")
        print(f"  Status: {pr['mergeable_state']} | Checks: {'Passed' if pr['status_checks']['all_passed'] else 'Failed'}")
        print()


async def get_pr_details(agent: GitHubMergeAgent, args):
    """Get PR details."""
    if not args.pr_number:
        print("Error: --pr-number is required for details action")
        return
    
    print(f"\nGetting details for PR #{args.pr_number}...")
    
    details = agent.get_pull_request_details(args.pr_number)
    if not details:
        print(f"PR #{args.pr_number} not found.")
        return
    
    print(f"\nPR #{details['number']}: {details['title']}")
    print("-" * 80)
    print(f"Author: {details['user']}")
    print(f"State: {details['state']}")
    print(f"Branch: {details['branch']} → {details['base_branch']}")
    print(f"Draft: {'Yes' if details['draft'] else 'No'}")
    print(f"Mergeable: {'Yes' if details['mergeable'] else 'No'}")
    print(f"Mergeable State: {details['mergeable_state']}")
    
    # Review summary
    reviews = details['review_summary']
    print(f"\nReviews:")
    print(f"  Total: {reviews['total_reviews']}")
    print(f"  Approved: {reviews['approved']}")
    print(f"  Changes Requested: {reviews['changes_requested']}")
    print(f"  Commented: {reviews['commented']}")
    print(f"  Pending: {reviews['pending']}")
    
    # Status checks
    checks = details['status_checks']
    print(f"\nStatus Checks:")
    print(f"  All Passed: {'Yes' if checks['all_passed'] else 'No'}")
    for check in checks['checks']:
        status_icon = "✅" if check['state'] == 'success' else "❌"
        print(f"  {status_icon} {check['name']}: {check['state']}")
    
    # Labels
    if details['labels']:
        print(f"\nLabels: {', '.join(details['labels'])}")


async def check_merge_eligibility(agent: GitHubMergeAgent, args):
    """Check merge eligibility."""
    if not args.pr_number:
        print("Error: --pr-number is required for check action")
        return
    
    print(f"\nChecking merge eligibility for PR #{args.pr_number}...")
    
    eligibility = agent.check_merge_eligibility(args.pr_number)
    
    print(f"\nMerge Eligibility: {'✅ ELIGIBLE' if eligibility['eligible'] else '❌ NOT ELIGIBLE'}")
    print("-" * 80)
    print(f"Reason: {eligibility['reason']}")
    print(f"Mergeable: {'Yes' if eligibility['mergeable'] else 'No'}")
    
    if 'review_summary' in eligibility:
        reviews = eligibility['review_summary']
        print(f"\nReview Status:")
        print(f"  Approved: {reviews['approved']}")
        print(f"  Changes Requested: {reviews['changes_requested']}")
        print(f"  Total Reviews: {reviews['total_reviews']}")
    
    if 'status_checks' in eligibility:
        checks = eligibility['status_checks']
        print(f"\nStatus Checks:")
        print(f"  All Passed: {'Yes' if checks['all_passed'] else 'No'}")
        for check in checks['checks']:
            status_icon = "✅" if check['state'] == 'success' else "❌"
            print(f"  {status_icon} {check['name']}: {check['state']}")


async def merge_pr(agent: GitHubMergeAgent, args):
    """Merge a PR."""
    if not args.pr_number:
        print("Error: --pr-number is required for merge action")
        return
    
    print(f"\nAttempting to merge PR #{args.pr_number}...")
    
    # Check eligibility first
    eligibility = agent.check_merge_eligibility(args.pr_number)
    if not eligibility['eligible']:
        print(f"Cannot merge PR #{args.pr_number}: {eligibility['reason']}")
        return
    
    print("PR is eligible for merging. Proceeding...")
    
    result = agent.merge_pull_request(
        pr_number=args.pr_number,
        merge_method=args.merge_method,
        commit_title=args.commit_title,
        commit_message=args.commit_message
    )
    
    if result['success']:
        print(f"✅ Successfully merged PR #{args.pr_number}")
        print(f"Merge SHA: {result['merge_sha']}")
        if result['message']:
            print(f"Message: {result['message']}")
    else:
        print(f"❌ Failed to merge PR #{args.pr_number}")
        print(f"Reason: {result['reason']}")


async def auto_merge_prs(agent: GitHubMergeAgent, args):
    """Auto-merge eligible PRs."""
    print(f"\nAuto-merging eligible pull requests...")
    if args.auto_merge_label:
        print(f"Filtering by label: {args.auto_merge_label}")
    
    result = agent.auto_merge_eligible_prs(auto_merge_label=args.auto_merge_label)
    
    if 'error' in result:
        print(f"❌ Auto-merge failed: {result['error']}")
        return
    
    print(f"\nAuto-merge completed:")
    print(f"  Total PRs checked: {result['total_prs_checked']}")
    print(f"  Successful merges: {result['successful_merges']}")
    print(f"  Failed merges: {result['failed_merges']}")
    
    if result['merge_results']:
        print(f"\nDetailed results:")
        for pr_result in result['merge_results']:
            status_icon = "✅" if pr_result['merge_result']['success'] else "❌"
            print(f"  {status_icon} PR #{pr_result['pr_number']}: {pr_result['title']}")
            if not pr_result['merge_result']['success']:
                print(f"    Reason: {pr_result['merge_result']['reason']}")


if __name__ == "__main__":
    asyncio.run(main()) 