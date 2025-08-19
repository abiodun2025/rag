import os
import jwt
import time
import requests
import logging
from typing import List, Dict, Any, Optional
from github import Github, GithubException
from app.config import settings

logger = logging.getLogger(__name__)


class GitHubClient:
    """GitHub API client for handling PR operations with support for both Apps and Personal Access Tokens."""
    
    def __init__(self):
        # Check if we have a personal access token first
        self.personal_token = os.getenv('GITHUB_TOKEN')
        
        if self.personal_token:
            # Use Personal Access Token
            self.auth_method = 'personal_token'
            self.github = Github(self.personal_token)
            self.user = self.github.get_user()
            logger.info(f"✅ Using Personal Access Token for user: {self.user.login}")
        else:
            # Fall back to GitHub App
            self.auth_method = 'github_app'
            self.app_id = settings.github_app_id
            self.private_key = settings.github_private_key
            self.webhook_secret = settings.github_webhook_secret
            self._installation_token = None
            self._token_expires_at = 0
            logger.info("🔧 Using GitHub App authentication")
    
    def _generate_jwt(self) -> str:
        """Generate JWT token for GitHub App authentication."""
        if self.auth_method != 'github_app':
            raise ValueError("JWT generation only available for GitHub App authentication")
            
        try:
            payload = {
                'iat': int(time.time()),
                'exp': int(time.time()) + 600,  # 10 minutes
                'iss': self.app_id
            }
            
            # Handle private key format
            if self.private_key.startswith('-----BEGIN RSA PRIVATE KEY-----'):
                private_key = self.private_key
            else:
                # Assume it's a file path
                with open(self.private_key, 'r') as f:
                    private_key = f.read()
            
            token = jwt.encode(payload, private_key, algorithm='RS256')
            return token
            
        except Exception as e:
            logger.error(f"Failed to generate JWT: {e}")
            raise
    
    def _get_installation_token(self, installation_id: int) -> str:
        """Get installation access token."""
        if self.auth_method != 'github_app':
            raise ValueError("Installation tokens only available for GitHub App authentication")
            
        try:
            jwt_token = self._generate_jwt()
            headers = {
                'Authorization': f'Bearer {jwt_token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            url = f'https://api.github.com/app/installations/{installation_id}/access_tokens'
            response = requests.post(url, headers=headers)
            response.raise_for_status()
            
            token_data = response.json()
            return token_data['token']
            
        except Exception as e:
            logger.error(f"Failed to get installation token: {e}")
            raise
    
    def _get_github_client(self, installation_id: int = None) -> Github:
        """Get authenticated GitHub client."""
        if self.auth_method == 'personal_token':
            return self.github
        else:
            # GitHub App authentication
            if not installation_id:
                raise ValueError("Installation ID required for GitHub App authentication")
            token = self._get_installation_token(installation_id)
            return Github(token)
    
    def get_pull_request_diff(self, owner: str, repo: str, pr_number: int, installation_id: int = None) -> Dict[str, Any]:
        """Get pull request diff and changed files."""
        try:
            g = self._get_github_client(installation_id)
            repository = g.get_repo(f"{owner}/{repo}")
            pull_request = repository.get_pull(pr_number)
            
            # Get files changed
            files = pull_request.get_files()
            changed_files = []
            file_diffs = {}
            
            for file in files:
                if self._is_code_file(file.filename):
                    changed_files.append(file.filename)
                    file_diffs[file.filename] = file.patch
            
            return {
                'success': True,
                'changed_files': changed_files,
                'file_diffs': file_diffs,
                'pull_request': pull_request
            }
            
        except GithubException as e:
            logger.error(f"GitHub API error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
        except Exception as e:
            logger.error(f"Failed to get PR diff: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def post_review_comments(self, owner: str, repo: str, pr_number: int, 
                           comments: List[Dict[str, Any]], installation_id: int = None) -> Dict[str, Any]:
        """Post review comments to a pull request."""
        try:
            g = self._get_github_client(installation_id)
            repository = g.get_repo(f"{owner}/{repo}")
            pull_request = repository.get_pull(pr_number)
            
            posted_comments = []
            for comment in comments:
                try:
                    if comment.get('line') and comment.get('path'):
                        # Line-specific comment
                        review_comment = pull_request.create_review_comment(
                            body=comment['body'],
                            commit_id=comment.get('commit_id', pull_request.head.sha),
                            path=comment['path'],
                            line=comment['line']
                        )
                        posted_comments.append({
                            'id': review_comment.id,
                            'type': 'line_comment',
                            'path': comment['path'],
                            'line': comment['line']
                        })
                    else:
                        # General comment
                        issue_comment = pull_request.create_issue_comment(comment['body'])
                        posted_comments.append({
                            'id': issue_comment.id,
                            'type': 'general_comment'
                        })
                        
                except Exception as e:
                    logger.error(f"Failed to post comment: {e}")
                    continue
            
            return {
                'success': True,
                'posted_comments': posted_comments,
                'total_comments': len(posted_comments)
            }
            
        except GithubException as e:
            logger.error(f"GitHub API error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
        except Exception as e:
            logger.error(f"Failed to post comments: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _is_code_file(self, filename: str) -> bool:
        """Check if a file is a code file that should be reviewed."""
        code_extensions = {
            '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h', '.hpp',
            '.cs', '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.scala', '.clj',
            '.hs', '.ml', '.fs', '.vb', '.sql', '.sh', '.bash', '.zsh', '.fish',
            '.yaml', '.yml', '.json', '.xml', '.html', '.css', '.scss', '.sass',
            '.vue', '.svelte', '.r', '.m', '.pl', '.lua', '.dart', '.elm'
        }
        import os
        return os.path.splitext(filename)[1].lower() in code_extensions
    
    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """Verify GitHub webhook signature."""
        if self.auth_method == 'personal_token':
            # For personal tokens, we can skip webhook verification or use a simple check
            logger.warning("Webhook signature verification skipped for Personal Access Token")
            return True
        
        # GitHub App webhook verification
        if not self.webhook_secret:
            logger.error("No webhook secret configured")
            return False
        
        try:
            import hmac
            import hashlib
            
            # Remove 'sha256=' prefix if present
            if signature.startswith('sha256='):
                signature = signature[7:]
            
            # Calculate expected signature
            expected_signature = hmac.new(
                self.webhook_secret.encode('utf-8'),
                payload,
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
            
        except Exception as e:
            logger.error(f"Webhook signature verification failed: {e}")
            return False
    
    def get_user_info(self) -> Dict[str, Any]:
        """Get current user information."""
        if self.auth_method == 'personal_token':
            return {
                'login': self.user.login,
                'name': self.user.name,
                'email': self.user.email,
                'auth_method': 'personal_token'
            }
        else:
            return {
                'auth_method': 'github_app'
            } 