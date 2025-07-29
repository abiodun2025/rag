#!/usr/bin/env python3
"""
Real GitHub Pull Request Implementation
Creates actual pull requests on GitHub repositories using the GitHub API.
"""

import os
import requests
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class GitHubConfig:
    """GitHub configuration for API access."""
    token: str
    owner: str
    repo: str
    base_url: str = "https://api.github.com"

class RealGitHubPullRequest:
    """Real GitHub pull request implementation."""
    
    def __init__(self, config: GitHubConfig):
        self.config = config
        self.headers = {
            "Authorization": f"token {config.token}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json"
        }
    
    def create_pull_request(self, title: str, description: str, 
                          source_branch: str, target_branch: str = "main") -> Dict[str, Any]:
        """Create a real pull request on GitHub."""
        try:
            url = f"{self.config.base_url}/repos/{self.config.owner}/{self.config.repo}/pulls"
            
            payload = {
                "title": title,
                "body": description,
                "head": source_branch,
                "base": target_branch,
                "draft": False
            }
            
            logger.info(f"🔀 CREATING REAL PULL REQUEST:")
            logger.info(f"   Repository: {self.config.owner}/{self.config.repo}")
            logger.info(f"   Title: {title}")
            logger.info(f"   Source: {source_branch}")
            logger.info(f"   Target: {target_branch}")
            
            response = requests.post(url, headers=self.headers, json=payload)
            
            if response.status_code == 201:
                pr_data = response.json()
                logger.info(f"✅ REAL pull request created successfully!")
                logger.info(f"   PR Number: {pr_data['number']}")
                logger.info(f"   URL: {pr_data['html_url']}")
                
                return {
                    "success": True,
                    "tool_name": "create_pull_request",
                    "result": f"Pull request '{title}' created successfully",
                    "pr_id": str(pr_data['number']),
                    "pr_number": pr_data['number'],
                    "title": pr_data['title'],
                    "description": pr_data['body'],
                    "source_branch": source_branch,
                    "target_branch": target_branch,
                    "repository": f"{self.config.owner}/{self.config.repo}",
                    "status": pr_data['state'],
                    "created_at": pr_data['created_at'],
                    "url": pr_data['html_url'],
                    "api_url": pr_data['url'],
                    "note": "This is a REAL pull request created on GitHub"
                }
            else:
                error_msg = f"Failed to create pull request: {response.status_code}"
                try:
                    error_data = response.json()
                    if 'message' in error_data:
                        error_msg += f" - {error_data['message']}"
                except:
                    pass
                
                logger.error(f"❌ {error_msg}")
                return {
                    "success": False,
                    "tool_name": "create_pull_request",
                    "error": error_msg,
                    "status_code": response.status_code
                }
                
        except Exception as e:
            logger.error(f"🔀 CREATE PULL REQUEST FAILED: {e}")
            return {
                "success": False,
                "tool_name": "create_pull_request",
                "error": f"Failed to create pull request: {str(e)}"
            }
    
    def list_pull_requests(self, state: str = "all", limit: int = 10) -> Dict[str, Any]:
        """List real pull requests from GitHub."""
        try:
            url = f"{self.config.base_url}/repos/{self.config.owner}/{self.config.repo}/pulls"
            params = {
                "state": state,
                "per_page": min(limit, 100),  # GitHub API limit
                "sort": "updated",
                "direction": "desc"
            }
            
            logger.info(f"📋 LISTING REAL PULL REQUESTS:")
            logger.info(f"   Repository: {self.config.owner}/{self.config.repo}")
            logger.info(f"   State: {state}")
            
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                prs_data = response.json()
                logger.info(f"✅ Found {len(prs_data)} pull requests")
                
                pull_requests = []
                for pr in prs_data:
                    pull_requests.append({
                        "pr_id": str(pr['number']),
                        "pr_number": pr['number'],
                        "title": pr['title'],
                        "author": pr['user']['login'],
                        "status": pr['state'],
                        "created_at": pr['created_at'],
                        "updated_at": pr['updated_at'],
                        "reviewers": [r['login'] for r in pr.get('requested_reviewers', [])],
                        "comments_count": pr['comments'],
                        "commits_count": pr['commits'],
                        "url": pr['html_url'],
                        "api_url": pr['url']
                    })
                
                return {
                    "success": True,
                    "tool_name": "list_pull_requests",
                    "result": f"Found {len(pull_requests)} pull requests",
                    "repository": f"{self.config.owner}/{self.config.repo}",
                    "status": state,
                    "pull_requests": pull_requests,
                    "total_count": len(pull_requests),
                    "note": "These are REAL pull requests from GitHub"
                }
            else:
                error_msg = f"Failed to list pull requests: {response.status_code}"
                try:
                    error_data = response.json()
                    if 'message' in error_data:
                        error_msg += f" - {error_data['message']}"
                except:
                    pass
                
                logger.error(f"❌ {error_msg}")
                return {
                    "success": False,
                    "tool_name": "list_pull_requests",
                    "error": error_msg,
                    "status_code": response.status_code
                }
                
        except Exception as e:
            logger.error(f"📋 LIST PULL REQUESTS FAILED: {e}")
            return {
                "success": False,
                "tool_name": "list_pull_requests",
                "error": f"Failed to list pull requests: {str(e)}"
            }
    
    def review_pull_request(self, pr_number: int, review_type: str, 
                          comments: List[str], reviewer: str = "Code Reviewer") -> Dict[str, Any]:
        """Review a real pull request on GitHub."""
        try:
            url = f"{self.config.base_url}/repos/{self.config.owner}/{self.config.repo}/pulls/{pr_number}/reviews"
            
            # Convert review type to GitHub API format
            event_map = {
                "approve": "APPROVE",
                "request_changes": "REQUEST_CHANGES", 
                "comment": "COMMENT"
            }
            event = event_map.get(review_type.lower(), "COMMENT")
            
            # Format comments for GitHub API
            body = "\n\n".join(comments) if comments else "No comments provided"
            
            payload = {
                "event": event,
                "body": body
            }
            
            logger.info(f"🔍 REVIEWING REAL PULL REQUEST:")
            logger.info(f"   PR Number: {pr_number}")
            logger.info(f"   Type: {review_type} ({event})")
            logger.info(f"   Reviewer: {reviewer}")
            
            response = requests.post(url, headers=self.headers, json=payload)
            
            if response.status_code == 200:
                review_data = response.json()
                logger.info(f"✅ REAL pull request reviewed successfully!")
                
                return {
                    "success": True,
                    "tool_name": "review_pull_request",
                    "result": f"Pull request #{pr_number} reviewed successfully",
                    "pr_id": str(pr_number),
                    "pr_number": pr_number,
                    "review_id": str(review_data['id']),
                    "review_type": review_type,
                    "event": event,
                    "comments": comments,
                    "reviewer": reviewer,
                    "reviewed_at": review_data['submitted_at'],
                    "status": "completed",
                    "url": review_data['html_url'],
                    "note": "This is a REAL pull request review on GitHub"
                }
            else:
                error_msg = f"Failed to review pull request: {response.status_code}"
                try:
                    error_data = response.json()
                    if 'message' in error_data:
                        error_msg += f" - {error_data['message']}"
                except:
                    pass
                
                logger.error(f"❌ {error_msg}")
                return {
                    "success": False,
                    "tool_name": "review_pull_request",
                    "error": error_msg,
                    "status_code": response.status_code
                }
                
        except Exception as e:
            logger.error(f"🔍 REVIEW PULL REQUEST FAILED: {e}")
            return {
                "success": False,
                "tool_name": "review_pull_request",
                "error": f"Failed to review pull request: {str(e)}"
            }
    
    def merge_pull_request(self, pr_number: int, merge_method: str = "squash", 
                          commit_message: str = "") -> Dict[str, Any]:
        """Merge a real pull request on GitHub."""
        try:
            url = f"{self.config.base_url}/repos/{self.config.owner}/{self.config.repo}/pulls/{pr_number}/merge"
            
            payload = {
                "merge_method": merge_method
            }
            
            if commit_message:
                payload["commit_message"] = commit_message
            
            logger.info(f"🔀 MERGING REAL PULL REQUEST:")
            logger.info(f"   PR Number: {pr_number}")
            logger.info(f"   Method: {merge_method}")
            
            response = requests.put(url, headers=self.headers, json=payload)
            
            if response.status_code == 200:
                merge_data = response.json()
                logger.info(f"✅ REAL pull request merged successfully!")
                
                return {
                    "success": True,
                    "tool_name": "merge_pull_request",
                    "result": f"Pull request #{pr_number} merged successfully",
                    "pr_id": str(pr_number),
                    "pr_number": pr_number,
                    "merge_id": str(merge_data.get('sha', '')),
                    "merge_method": merge_method,
                    "commit_message": merge_data.get('message', commit_message),
                    "merged_at": merge_data.get('merged_at', datetime.now().isoformat()),
                    "status": "merged",
                    "note": "This is a REAL pull request merge on GitHub"
                }
            else:
                error_msg = f"Failed to merge pull request: {response.status_code}"
                try:
                    error_data = response.json()
                    if 'message' in error_data:
                        error_msg += f" - {error_data['message']}"
                except:
                    pass
                
                logger.error(f"❌ {error_msg}")
                return {
                    "success": False,
                    "tool_name": "merge_pull_request",
                    "error": error_msg,
                    "status_code": response.status_code
                }
                
        except Exception as e:
            logger.error(f"🔀 MERGE PULL REQUEST FAILED: {e}")
            return {
                "success": False,
                "tool_name": "merge_pull_request",
                "error": f"Failed to merge pull request: {str(e)}"
            }
    
    def get_pull_request(self, pr_number: int) -> Dict[str, Any]:
        """Get details of a specific pull request."""
        try:
            url = f"{self.config.base_url}/repos/{self.config.owner}/{self.config.repo}/pulls/{pr_number}"
            
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                pr_data = response.json()
                return {
                    "success": True,
                    "pr_number": pr_data['number'],
                    "title": pr_data['title'],
                    "body": pr_data['body'],
                    "state": pr_data['state'],
                    "merged": pr_data['merged'],
                    "mergeable": pr_data['mergeable'],
                    "created_at": pr_data['created_at'],
                    "updated_at": pr_data['updated_at'],
                    "url": pr_data['html_url']
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to get pull request: {response.status_code}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get pull request: {str(e)}"
            }

def create_github_config_from_env() -> Optional[GitHubConfig]:
    """Create GitHub config from environment variables."""
    token = os.getenv('GITHUB_TOKEN')
    owner = os.getenv('GITHUB_OWNER')
    repo = os.getenv('GITHUB_REPO')
    
    if not token:
        logger.error("❌ GITHUB_TOKEN environment variable not set")
        return None
    
    if not owner:
        logger.error("❌ GITHUB_OWNER environment variable not set")
        return None
    
    if not repo:
        logger.error("❌ GITHUB_REPO environment variable not set")
        return None
    
    return GitHubConfig(token=token, owner=owner, repo=repo)

def create_github_config_interactive() -> Optional[GitHubConfig]:
    """Create GitHub config interactively."""
    print("🔧 GitHub Configuration Setup")
    print("=" * 40)
    
    token = input("Enter your GitHub Personal Access Token: ").strip()
    if not token:
        print("❌ Token is required")
        return None
    
    owner = input("Enter repository owner (username or organization): ").strip()
    if not owner:
        print("❌ Owner is required")
        return None
    
    repo = input("Enter repository name: ").strip()
    if not repo:
        print("❌ Repository name is required")
        return None
    
    return GitHubConfig(token=token, owner=owner, repo=repo)

if __name__ == "__main__":
    # Test the real GitHub pull request functionality
    print("🧪 Testing Real GitHub Pull Request")
    print("=" * 50)
    
    # Try to get config from environment, otherwise ask interactively
    config = create_github_config_from_env()
    if not config:
        config = create_github_config_interactive()
    
    if not config:
        print("❌ Failed to create GitHub configuration")
        exit(1)
    
    # Create the GitHub PR client
    github_pr = RealGitHubPullRequest(config)
    
    # Test listing pull requests
    print("\n📋 Testing: List Pull Requests")
    result = github_pr.list_pull_requests(state="open", limit=5)
    
    if result.get("success"):
        print(f"✅ Success! Found {result['total_count']} pull requests")
        for pr in result['pull_requests']:
            print(f"   - #{pr['pr_number']}: {pr['title']}")
    else:
        print(f"❌ Failed: {result.get('error')}")
    
    # Test creating a pull request (commented out for safety)
    print("\n📝 Testing: Create Pull Request (commented out for safety)")
    print("Uncomment the code below to test creating a real pull request")
    
    # Uncomment to test creating a real pull request:
    # result = github_pr.create_pull_request(
    #     title="Test PR from Real GitHub Implementation",
    #     description="This is a test pull request created by the real GitHub implementation",
    #     source_branch="test-branch",
    #     target_branch="main"
    # )
    # 
    # if result.get("success"):
    #     print(f"✅ Success! Created PR #{result['pr_number']}")
    #     print(f"   URL: {result['url']}")
    # else:
    #     print(f"❌ Failed: {result.get('error')}")
    
    print("\n🎉 Test completed!")