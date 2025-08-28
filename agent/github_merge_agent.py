"""
GitHub Merge Agent for automatically merging reviewed pull requests.
"""

import os
import logging
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import asyncio
from dataclasses import dataclass

from pydantic import BaseModel, Field
from dotenv import load_dotenv
from github import Github, GithubException
from github.PullRequest import PullRequest
from github.Repository import Repository

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


@dataclass
class PRStatus:
    """Status information for a pull request."""
    number: int
    title: str
    state: str
    review_status: str
    mergeable: bool
    mergeable_state: str
    required_status_checks: List[str]
    branch_protection_rules: Dict[str, Any]
    last_updated: datetime


class GitHubMergeAgent:
    """Agent for managing GitHub pull request merges."""
    
    def __init__(self, token: Optional[str] = None, repo_name: Optional[str] = None):
        """
        Initialize the GitHub merge agent.
        
        Args:
            token: GitHub Personal Access Token
            repo_name: Repository name in format 'owner/repo'
        """
        self.token = token or os.getenv('GITHUB_TOKEN')
        if not self.token:
            raise ValueError("GitHub token is required. Set GITHUB_TOKEN environment variable or pass token parameter.")
        
        self.github = Github(self.token)
        self.repo_name = repo_name or os.getenv('GITHUB_REPO')
        self.repo: Optional[Repository] = None
        
        if self.repo_name:
            self.set_repository(self.repo_name)
    
    def set_repository(self, repo_name: str) -> None:
        """Set the repository to work with."""
        try:
            self.repo = self.github.get_repo(repo_name)
            logger.info(f"Connected to repository: {repo_name}")
        except GithubException as e:
            logger.error(f"Failed to connect to repository {repo_name}: {e}")
            raise
    
    def list_pull_requests(self, state: str = "open", limit: int = 50) -> List[Dict[str, Any]]:
        """
        List pull requests in the repository.
        
        Args:
            state: PR state ('open', 'closed', 'all')
            limit: Maximum number of PRs to return
            
        Returns:
            List of PR information dictionaries
        """
        if not self.repo:
            raise ValueError("Repository not set. Call set_repository() first.")
        
        try:
            prs = self.repo.get_pulls(state=state)
            pr_list = []
            
            for pr in prs[:limit]:
                pr_info = {
                    'number': pr.number,
                    'title': pr.title,
                    'state': pr.state,
                    'user': pr.user.login,
                    'created_at': pr.created_at.isoformat(),
                    'updated_at': pr.updated_at.isoformat(),
                    'mergeable': pr.mergeable,
                    'mergeable_state': pr.mergeable_state,
                    'review_count': pr.get_reviews().totalCount,
                    'status_checks': self._get_status_checks(pr),
                    'branch': pr.head.ref,
                    'base_branch': pr.base.ref
                }
                pr_list.append(pr_info)
            
            return pr_list
            
        except GithubException as e:
            logger.error(f"Failed to list pull requests: {e}")
            raise
    
    def get_pull_request_details(self, pr_number: int) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific pull request.
        
        Args:
            pr_number: Pull request number
            
        Returns:
            Detailed PR information or None if not found
        """
        if not self.repo:
            raise ValueError("Repository not set. Call set_repository() first.")
        
        try:
            pr = self.repo.get_pull(pr_number)
            
            # Get reviews
            reviews = pr.get_reviews()
            review_summary = self._analyze_reviews(reviews)
            
            # Get status checks
            status_checks = self._get_status_checks(pr)
            
            # Get branch protection rules
            branch_protection = self._get_branch_protection(pr.base.ref)
            
            pr_details = {
                'number': pr.number,
                'title': pr.title,
                'state': pr.state,
                'user': pr.user.login,
                'created_at': pr.created_at.isoformat(),
                'updated_at': pr.updated_at.isoformat(),
                'mergeable': pr.mergeable,
                'mergeable_state': pr.mergeable_state,
                'review_summary': review_summary,
                'status_checks': status_checks,
                'branch_protection': branch_protection,
                'branch': pr.head.ref,
                'base_branch': pr.base.ref,
                'labels': [label.name for label in pr.get_labels()],
                'assignees': [assignee.login for assignee in pr.get_assignees()],
                'requested_reviewers': [reviewer.login for reviewer in pr.get_requested_reviewers()],
                'body': pr.body,
                'draft': pr.draft
            }
            
            return pr_details
            
        except GithubException as e:
            logger.error(f"Failed to get PR {pr_number} details: {e}")
            return None
    
    def check_merge_eligibility(self, pr_number: int) -> Dict[str, Any]:
        """
        Check if a pull request is eligible for merging.
        
        Args:
            pr_number: Pull request number
            
        Returns:
            Dictionary with merge eligibility status and details
        """
        if not self.repo:
            raise ValueError("Repository not set. Call set_repository() first.")
        
        try:
            pr = self.repo.get_pull(pr_number)
            
            # Check basic mergeability
            if pr.state != 'open':
                return {
                    'eligible': False,
                    'reason': f"PR is not open (state: {pr.state})",
                    'mergeable': False
                }
            
            if pr.draft:
                return {
                    'eligible': False,
                    'reason': "PR is in draft state",
                    'mergeable': False
                }
            
            # Check mergeable state
            if pr.mergeable_state == 'blocked':
                return {
                    'eligible': False,
                    'reason': "PR is blocked from merging",
                    'mergeable': False
                }
            
            # Check reviews
            reviews = pr.get_reviews()
            review_status = self._analyze_reviews(reviews)
            
            if not review_status['approved']:
                return {
                    'eligible': False,
                    'reason': "PR does not have required approvals",
                    'review_summary': review_status,
                    'mergeable': pr.mergeable
                }
            
            # Check status checks
            status_checks = self._get_status_checks(pr)
            if not status_checks['all_passed']:
                return {
                    'eligible': False,
                    'reason': "Not all status checks have passed",
                    'status_checks': status_checks,
                    'mergeable': pr.mergeable
                }
            
            # Check branch protection
            branch_protection = self._get_branch_protection(pr.base.ref)
            if branch_protection['protected'] and not branch_protection['all_requirements_met']:
                return {
                    'eligible': False,
                    'reason': "Branch protection requirements not met",
                    'branch_protection': branch_protection,
                    'mergeable': pr.mergeable
                }
            
            return {
                'eligible': True,
                'reason': "All requirements met",
                'mergeable': pr.mergeable,
                'review_summary': review_status,
                'status_checks': status_checks,
                'branch_protection': branch_protection
            }
            
        except GithubException as e:
            logger.error(f"Failed to check merge eligibility for PR {pr_number}: {e}")
            return {
                'eligible': False,
                'reason': f"Error checking eligibility: {str(e)}",
                'mergeable': False
            }
    
    def merge_pull_request(self, pr_number: int, merge_method: str = "merge", 
                          commit_title: Optional[str] = None, 
                          commit_message: Optional[str] = None) -> Dict[str, Any]:
        """
        Merge a pull request if it's eligible.
        
        Args:
            pr_number: Pull request number
            merge_method: Merge method ('merge', 'squash', 'rebase')
            commit_title: Custom commit title
            commit_message: Custom commit message
            
        Returns:
            Dictionary with merge result
        """
        if not self.repo:
            raise ValueError("Repository not set. Call set_repository() first.")
        
        try:
            # Check eligibility first
            eligibility = self.check_merge_eligibility(pr_number)
            if not eligibility['eligible']:
                return {
                    'success': False,
                    'reason': eligibility['reason'],
                    'pr_number': pr_number
                }
            
            pr = self.repo.get_pull(pr_number)
            
            # Prepare merge parameters
            merge_params = {
                'merge_method': merge_method
            }
            
            if commit_title:
                merge_params['commit_title'] = commit_title
            if commit_message:
                merge_params['commit_message'] = commit_message
            
            # Attempt to merge
            result = pr.merge(**merge_params)
            
            if result.merged:
                logger.info(f"Successfully merged PR #{pr_number}")
                return {
                    'success': True,
                    'pr_number': pr_number,
                    'merge_sha': result.sha,
                    'message': result.message
                }
            else:
                return {
                    'success': False,
                    'reason': "Merge was not successful",
                    'pr_number': pr_number,
                    'result': result
                }
                
        except GithubException as e:
            logger.error(f"Failed to merge PR {pr_number}: {e}")
            return {
                'success': False,
                'reason': f"GitHub API error: {str(e)}",
                'pr_number': pr_number
            }
    
    def auto_merge_eligible_prs(self, auto_merge_label: Optional[str] = None) -> Dict[str, Any]:
        """
        Automatically merge all eligible pull requests.
        
        Args:
            auto_merge_label: Only merge PRs with this label (optional)
            
        Returns:
            Dictionary with merge results summary
        """
        if not self.repo:
            raise ValueError("Repository not set. Call set_repository() first.")
        
        try:
            open_prs = self.repo.get_pulls(state='open')
            merge_results = []
            successful_merges = 0
            failed_merges = 0
            
            for pr in open_prs:
                # Check if PR has required label
                if auto_merge_label:
                    pr_labels = [label.name for label in pr.get_labels()]
                    if auto_merge_label not in pr_labels:
                        continue
                
                # Check eligibility
                eligibility = self.check_merge_eligibility(pr.number)
                
                if eligibility['eligible']:
                    # Attempt to merge
                    merge_result = self.merge_pull_request(pr.number)
                    merge_results.append({
                        'pr_number': pr.number,
                        'title': pr.title,
                        'merge_result': merge_result
                    })
                    
                    if merge_result['success']:
                        successful_merges += 1
                    else:
                        failed_merges += 1
                else:
                    merge_results.append({
                        'pr_number': pr.number,
                        'title': pr.title,
                        'merge_result': {
                            'success': False,
                            'reason': eligibility['reason']
                        }
                    })
                    failed_merges += 1
            
            return {
                'total_prs_checked': len(merge_results),
                'successful_merges': successful_merges,
                'failed_merges': failed_merges,
                'merge_results': merge_results
            }
            
        except GithubException as e:
            logger.error(f"Failed to auto-merge PRs: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _analyze_reviews(self, reviews) -> Dict[str, Any]:
        """Analyze review status for a pull request."""
        review_summary = {
            'total_reviews': reviews.totalCount,
            'approved': 0,
            'changes_requested': 0,
            'commented': 0,
            'pending': 0
        }
        
        for review in reviews:
            if review.state == 'APPROVED':
                review_summary['approved'] += 1
            elif review.state == 'CHANGES_REQUESTED':
                review_summary['changes_requested'] += 1
            elif review.state == 'COMMENTED':
                review_summary['commented'] += 1
            elif review.state == 'PENDING':
                review_summary['pending'] += 1
        
        return review_summary
    
    def _get_status_checks(self, pr: PullRequest) -> Dict[str, Any]:
        """Get status check information for a pull request."""
        try:
            # Get the latest commit
            commits = pr.get_commits()
            if commits.totalCount == 0:
                return {'all_passed': False, 'checks': []}
            
            latest_commit = commits[commits.totalCount - 1]
            status = latest_commit.get_statuses()
            
            checks = []
            all_passed = True
            
            for check in status:
                check_info = {
                    'name': check.context,
                    'state': check.state,
                    'description': check.description,
                    'target_url': check.target_url
                }
                checks.append(check_info)
                
                if check.state not in ['success', 'skipped']:
                    all_passed = False
            
            return {
                'all_passed': all_passed,
                'checks': checks
            }
            
        except GithubException:
            return {'all_passed': False, 'checks': []}
    
    def _get_branch_protection(self, branch_name: str) -> Dict[str, Any]:
        """Get branch protection rules for a branch."""
        try:
            branch = self.repo.get_branch(branch_name)
            protection = branch.get_protection()
            
            return {
                'protected': True,
                'required_status_checks': protection.required_status_checks,
                'enforce_admins': protection.enforce_admins,
                'required_pull_request_reviews': protection.required_pull_request_reviews,
                'restrictions': protection.restrictions,
                'all_requirements_met': True  # This would need more detailed logic
            }
            
        except GithubException:
            return {
                'protected': False,
                'all_requirements_met': True
            }
    
    def close(self):
        """Close the GitHub connection."""
        if self.github:
            self.github.close()


# Pydantic models for tool inputs
class ListPRsInput(BaseModel):
    """Input for listing pull requests."""
    state: str = Field(default="open", description="PR state: 'open', 'closed', or 'all'")
    limit: int = Field(default=50, description="Maximum number of PRs to return")
    repo_name: Optional[str] = Field(None, description="Repository name in format 'owner/repo'")


class GetPRDetailsInput(BaseModel):
    """Input for getting PR details."""
    pr_number: int = Field(..., description="Pull request number")
    repo_name: Optional[str] = Field(None, description="Repository name in format 'owner/repo'")


class CheckMergeEligibilityInput(BaseModel):
    """Input for checking merge eligibility."""
    pr_number: int = Field(..., description="Pull request number")
    repo_name: Optional[str] = Field(None, description="Repository name in format 'owner/repo'")


class MergePRInput(BaseModel):
    """Input for merging a pull request."""
    pr_number: int = Field(..., description="Pull request number")
    merge_method: str = Field(default="merge", description="Merge method: 'merge', 'squash', or 'rebase'")
    commit_title: Optional[str] = Field(None, description="Custom commit title")
    commit_message: Optional[str] = Field(None, description="Custom commit message")
    repo_name: Optional[str] = Field(None, description="Repository name in format 'owner/repo'")


class AutoMergeInput(BaseModel):
    """Input for auto-merging eligible PRs."""
    auto_merge_label: Optional[str] = Field(None, description="Only merge PRs with this label")
    repo_name: Optional[str] = Field(None, description="Repository name in format 'owner/repo'")


# Global agent instance
_merge_agent: Optional[GitHubMergeAgent] = None


def get_merge_agent(repo_name: Optional[str] = None) -> GitHubMergeAgent:
    """Get or create a GitHub merge agent instance."""
    global _merge_agent
    
    if _merge_agent is None:
        _merge_agent = GitHubMergeAgent(repo_name=repo_name)
    elif repo_name and _merge_agent.repo_name != repo_name:
        _merge_agent.set_repository(repo_name)
    
    return _merge_agent


async def list_pull_requests_tool(input_data: ListPRsInput) -> Dict[str, Any]:
    """Tool for listing pull requests."""
    try:
        agent = get_merge_agent(input_data.repo_name)
        prs = agent.list_pull_requests(state=input_data.state, limit=input_data.limit)
        
        return {
            'success': True,
            'pull_requests': prs,
            'count': len(prs)
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


async def get_pr_details_tool(input_data: GetPRDetailsInput) -> Dict[str, Any]:
    """Tool for getting PR details."""
    try:
        agent = get_merge_agent(input_data.repo_name)
        details = agent.get_pull_request_details(input_data.pr_number)
        
        if details:
            return {
                'success': True,
                'pr_details': details
            }
        else:
            return {
                'success': False,
                'error': f"PR #{input_data.pr_number} not found"
            }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


async def check_merge_eligibility_tool(input_data: CheckMergeEligibilityInput) -> Dict[str, Any]:
    """Tool for checking merge eligibility."""
    try:
        agent = get_merge_agent(input_data.repo_name)
        eligibility = agent.check_merge_eligibility(input_data.pr_number)
        
        return {
            'success': True,
            'eligibility': eligibility
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


async def merge_pr_tool(input_data: MergePRInput) -> Dict[str, Any]:
    """Tool for merging a pull request."""
    try:
        agent = get_merge_agent(input_data.repo_name)
        result = agent.merge_pull_request(
            pr_number=input_data.pr_number,
            merge_method=input_data.merge_method,
            commit_title=input_data.commit_title,
            commit_message=input_data.commit_message
        )
        
        return {
            'success': True,
            'merge_result': result
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


async def auto_merge_eligible_prs_tool(input_data: AutoMergeInput) -> Dict[str, Any]:
    """Tool for auto-merging eligible PRs."""
    try:
        agent = get_merge_agent(input_data.repo_name)
        result = agent.auto_merge_eligible_prs(auto_merge_label=input_data.auto_merge_label)
        
        return {
            'success': True,
            'auto_merge_result': result
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        } 