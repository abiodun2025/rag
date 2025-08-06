from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class GitHubWebhookPayload(BaseModel):
    """GitHub webhook payload model."""
    action: str
    pull_request: Dict[str, Any]
    repository: Dict[str, Any]
    sender: Dict[str, Any]


class CodeReviewRequest(BaseModel):
    """Code review request model."""
    owner: str
    repo: str
    pr_number: int
    diff_content: str
    changed_files: List[str]


class CodeReviewComment(BaseModel):
    """Code review comment model."""
    path: str
    line: int
    body: str
    position: Optional[int] = None


class CodeReviewResponse(BaseModel):
    """Code review response model."""
    success: bool
    comments: List[CodeReviewComment]
    summary: str
    error: Optional[str] = None


class CohereReviewRequest(BaseModel):
    """Cohere API review request model."""
    diff_content: str
    file_path: str
    max_tokens: int = 1000


class CohereReviewResponse(BaseModel):
    """Cohere API review response model."""
    suggestions: List[Dict[str, Any]]
    summary: str
    score: int 