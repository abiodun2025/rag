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
    """GitHub API client for handling PR operations."""
    
    def __init__(self):
        self.app_id = settings.github_app_id
        self.private_key = settings.github_private_key
        self.webhook_secret = settings.github_webhook_secret
        self._installation_token = None
        self._token_expires_at = 0
        
    def _generate_jwt(self) -> str:
        """Generate JWT token for GitHub App authentication."""
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
    
    def _get_github_client(self, installation_id: int) -> Github:
        """Get authenticated GitHub client."""
        token = self._get_installation_token(installation_id)
        return Github(token)
    
    def get_pull_request_diff(self, owner: str, repo: str, pr_number: int, installation_id: int) -> Dict[str, Any]:
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
                           comments: List[Dict[str, Any]], installation_id: int) -> Dict[str, Any]:
        """Post review comments to pull request."""
        try:
            g = self._get_github_client(installation_id)
            repository = g.get_repo(f"{owner}/{repo}")
            pull_request = repository.get_pull(pr_number)
            
            # Create review with comments
            review = pull_request.create_review(
                body="AI Code Review completed",
                comments=comments,
                event="COMMENT"
            )
            
            return {
                'success': True,
                'review_id': review.id,
                'review_url': review.html_url
            }
            
        except GithubException as e:
            logger.error(f"GitHub API error posting comments: {e}")
            return {
                'success': False,
                'error': str(e)
            }
        except Exception as e:
            logger.error(f"Failed to post review comments: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _is_code_file(self, filename: str) -> bool:
        """Check if file is a code file that should be reviewed."""
        code_extensions = {
            '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h', 
            '.cs', '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.scala',
            '.html', '.css', '.scss', '.sass', '.less', '.vue', '.svelte',
            '.sql', '.sh', '.bash', '.zsh', '.fish', '.ps1', '.bat',
            '.yaml', '.yml', '.json', '.xml', '.toml', '.ini', '.cfg',
            '.md', '.txt', '.rst'
        }
        
        # Ignore certain directories and files
        ignore_patterns = {
            'node_modules/', 'vendor/', '__pycache__/', '.git/',
            'package-lock.json', 'yarn.lock', 'poetry.lock',
            '.env', '.env.local', '.env.production'
        }
        
        filename_lower = filename.lower()
        
        # Check ignore patterns
        for pattern in ignore_patterns:
            if pattern in filename_lower:
                return False
        
        # Check if it's a code file
        return any(filename_lower.endswith(ext) for ext in code_extensions)
    
    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """Verify GitHub webhook signature."""
        try:
            import hmac
            import hashlib
            
            expected_signature = 'sha256=' + hmac.new(
                self.webhook_secret.encode('utf-8'),
                payload,
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(expected_signature, signature)
            
        except Exception as e:
            logger.error(f"Failed to verify webhook signature: {e}")
            return False 