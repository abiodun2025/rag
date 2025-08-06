"""
GitHub AI Code Review Agent - Main Server Application
"""

import os
import json
import logging
from typing import Dict, Any, List
from datetime import datetime

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from dotenv import load_dotenv

from .github_client import GitHubClient
from .models import GitHubWebhookPayload, CodeReviewRequest, CodeReviewResponse
from .code_review_service import CodeReviewService
from .config import settings

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize services
github_client = GitHubClient()
code_review_service = CodeReviewService()

# Create FastAPI app
app = FastAPI(
    title="GitHub AI Code Review Agent",
    description="AI-powered code review agent for GitHub pull requests",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "message": "GitHub AI Code Review Agent",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "github_client": "initialized",
            "code_review_service": "initialized"
        }
    }


@app.post("/webhook/github")
async def github_webhook(request: Request):
    """
    Handle GitHub webhook events for pull requests.
    """
    try:
        # Get raw body for signature verification
        body = await request.body()
        
        # Get GitHub signature
        signature = request.headers.get("X-Hub-Signature-256", "")
        if not signature:
            logger.warning("No GitHub signature found in webhook")
            raise HTTPException(status_code=401, detail="Missing signature")
        
        # Verify webhook signature
        if not github_client.verify_webhook_signature(body, signature):
            logger.error("Invalid webhook signature")
            raise HTTPException(status_code=401, detail="Invalid signature")
        
        # Parse webhook payload
        try:
            payload = json.loads(body.decode('utf-8'))
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON payload: {e}")
            raise HTTPException(status_code=400, detail="Invalid JSON payload")
        
        # Check if this is a pull request event
        if not payload.get("pull_request"):
            logger.info("Not a pull request event, ignoring")
            return JSONResponse(content={"message": "Not a pull request event"}, status_code=200)
        
        # Check if this is a relevant action
        action = payload.get("action")
        if action not in ["opened", "synchronize", "reopened"]:
            logger.info(f"Pull request action '{action}' not relevant for code review")
            return JSONResponse(content={"message": f"Action '{action}' not relevant"}, status_code=200)
        
        # Extract PR information
        pr_data = payload["pull_request"]
        repo_data = payload["repository"]
        installation_id = payload.get("installation", {}).get("id")
        
        if not installation_id:
            logger.error("No installation ID found in webhook payload")
            raise HTTPException(status_code=400, detail="No installation ID")
        
        owner = repo_data["owner"]["login"]
        repo = repo_data["name"]
        pr_number = pr_data["number"]
        
        logger.info(f"Processing PR #{pr_number} in {owner}/{repo}")
        
        # Get PR diff and changed files
        diff_result = github_client.get_pull_request_diff(
            owner=owner,
            repo=repo,
            pr_number=pr_number,
            installation_id=installation_id
        )
        
        if not diff_result["success"]:
            logger.error(f"Failed to get PR diff: {diff_result.get('error')}")
            raise HTTPException(status_code=500, detail="Failed to get PR diff")
        
        changed_files = diff_result["changed_files"]
        file_diffs = diff_result["file_diffs"]
        
        if not changed_files:
            logger.info("No code files changed in this PR")
            return JSONResponse(content={"message": "No code files to review"}, status_code=200)
        
        logger.info(f"Found {len(changed_files)} code files to review")
        
        # Perform code review
        review_result = await code_review_service.review_pull_request(
            owner=owner,
            repo=repo,
            pr_number=pr_number,
            changed_files=changed_files,
            file_diffs=file_diffs,
            installation_id=installation_id
        )
        
        if not review_result["success"]:
            logger.error(f"Code review failed: {review_result.get('error')}")
            raise HTTPException(status_code=500, detail="Code review failed")
        
        logger.info(f"Code review completed successfully. Posted {len(review_result['comments'])} comments")
        
        return JSONResponse(content={
            "message": "Code review completed",
            "comments_posted": len(review_result["comments"]),
            "review_url": review_result.get("review_url")
        }, status_code=200)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in webhook handler: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/review", response_model=CodeReviewResponse)
async def manual_review(request: CodeReviewRequest):
    """
    Manual code review endpoint for testing.
    """
    try:
        logger.info(f"Manual review requested for PR #{request.pr_number} in {request.owner}/{request.repo}")
        
        # Perform code review
        review_result = await code_review_service.review_code(
            diff_content=request.diff_content,
            changed_files=request.changed_files
        )
        
        return CodeReviewResponse(
            success=review_result["success"],
            comments=review_result.get("comments", []),
            summary=review_result.get("summary", ""),
            error=review_result.get("error")
        )
        
    except Exception as e:
        logger.error(f"Manual review failed: {e}")
        return CodeReviewResponse(
            success=False,
            comments=[],
            summary="",
            error=str(e)
        )


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    ) 