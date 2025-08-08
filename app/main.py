#!/usr/bin/env python3
"""
GitHub AI Code Review Agent - FastAPI Server
===========================================

A FastAPI server that provides webhook endpoints for automated code reviews
and manual review capabilities.
"""

import logging
import os
from datetime import datetime
from typing import Dict, Any, List

from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
import uvicorn

from app.config import settings
from app.github_client import GitHubClient
from app.code_review_service import CodeReviewService

# Configure logging
logging.basicConfig(level=getattr(logging, settings.log_level))
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="GitHub AI Code Review Agent",
    description="AI-powered code review agent for GitHub pull requests",
    version="1.0.0"
)

# Initialize services
github_client = GitHubClient()
code_review_service = CodeReviewService()


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "GitHub AI Code Review Agent",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Test GitHub client
        user_info = github_client.get_user_info()
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "github_client": "initialized",
                "code_review_service": "initialized"
            },
            "auth_method": user_info.get("auth_method", "unknown")
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/webhook/github")
async def github_webhook(request: Request):
    """Handle GitHub webhook events."""
    try:
        # Get webhook payload
        payload = await request.body()
        headers = request.headers
        
        # Verify webhook signature
        signature = headers.get("x-hub-signature-256", "")
        if not github_client.verify_webhook_signature(payload, signature):
            logger.warning("Invalid webhook signature")
            raise HTTPException(status_code=401, detail="Invalid signature")
        
        # Parse webhook event
        event_type = headers.get("x-github-event", "")
        webhook_data = await request.json()
        
        logger.info(f"Received {event_type} webhook")
        
        # Handle pull request events
        if event_type == "pull_request":
            return await handle_pull_request_webhook(webhook_data)
        
        # Handle other events
        return {"status": "received", "event": event_type}
        
    except Exception as e:
        logger.error(f"Webhook processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def handle_pull_request_webhook(webhook_data: Dict[str, Any]):
    """Handle pull request webhook events."""
    try:
        action = webhook_data.get("action")
        
        # Only process opened, synchronize, or reopened PRs
        if action not in ["opened", "synchronize", "reopened"]:
            return {"status": "ignored", "action": action}
        
        # Extract PR information
        pull_request = webhook_data.get("pull_request", {})
        repository = webhook_data.get("repository", {})
        
        owner = repository.get("owner", {}).get("login")
        repo_name = repository.get("name")
        pr_number = pull_request.get("number")
        
        if not all([owner, repo_name, pr_number]):
            logger.error("Missing required PR information")
            return {"status": "error", "message": "Missing PR information"}
        
        logger.info(f"Processing PR #{pr_number} in {owner}/{repo_name}")
        
        # Get PR diff
        diff_result = github_client.get_pull_request_diff(owner, repo_name, pr_number)
        
        if not diff_result["success"]:
            logger.error(f"Failed to get PR diff: {diff_result['error']}")
            return {"status": "error", "message": "Failed to get PR diff"}
        
        changed_files = diff_result["changed_files"]
        file_diffs = diff_result["file_diffs"]
        
        if not changed_files:
            logger.info("No code files changed")
            return {"status": "no_code_files"}
        
        # Review each file
        all_comments = []
        
        for filename in changed_files:
            if filename in file_diffs:
                logger.info(f"Reviewing {filename}")
                
                # Run AI review
                review_result = await code_review_service.review_code_changes(
                    diff_content=file_diffs[filename],
                    files=[filename]
                )
                
                if review_result["success"]:
                    comments = review_result["comments"]
                    
                    # Add file context to comments
                    for comment in comments:
                        comment["file"] = filename
                        comment["repo"] = f"{owner}/{repo_name}"
                        comment["pr_number"] = pr_number
                    
                    all_comments.extend(comments)
                    logger.info(f"Generated {len(comments)} comments for {filename}")
        
        # Post comments to GitHub
        if all_comments:
            logger.info(f"Posting {len(all_comments)} comments to GitHub")
            
            # Format comments for GitHub
            github_comments = []
            for comment in all_comments:
                github_comment = {
                    "body": comment["comment"],
                    "path": comment["file"],
                    "line": comment.get("line", 1)
                }
                github_comments.append(github_comment)
            
            # Post to GitHub
            post_result = github_client.post_review_comments(
                f"{owner}/{repo_name}", pr_number, github_comments
            )
            
            if post_result["success"]:
                logger.info(f"Successfully posted {post_result['total_comments']} comments")
                return {
                    "status": "success",
                    "files_reviewed": len(changed_files),
                    "comments_posted": post_result["total_comments"]
                }
            else:
                logger.error(f"Failed to post comments: {post_result['error']}")
                return {"status": "error", "message": "Failed to post comments"}
        
        return {"status": "success", "files_reviewed": len(changed_files), "comments_posted": 0}
        
    except Exception as e:
        logger.error(f"PR webhook processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/review/manual")
async def manual_review(request: Request):
    """Manual code review endpoint."""
    try:
        data = await request.json()
        
        diff_content = data.get("diff_content")
        files = data.get("files", [])
        
        if not diff_content:
            raise HTTPException(status_code=400, detail="diff_content is required")
        
        # Run AI review
        review_result = await code_review_service.review_code_changes(
            diff_content=diff_content,
            files=files
        )
        
        if review_result["success"]:
            return {
                "success": True,
                "comments": review_result["comments"],
                "summary": review_result.get("summary", ""),
                "files_reviewed": len(files)
            }
        else:
            raise HTTPException(status_code=500, detail=review_result["error"])
            
    except Exception as e:
        logger.error(f"Manual review failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    ) 