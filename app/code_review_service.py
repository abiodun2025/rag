"""
Code Review Service - AI-powered code analysis and comment generation
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import re

import cohere
from .models import CodeReviewComment, CohereReviewRequest, CohereReviewResponse
from .github_client import GitHubClient
from .config import settings

logger = logging.getLogger(__name__)


class CodeReviewService:
    """Service for AI-powered code review."""
    
    def __init__(self):
        self.cohere_client = cohere.Client(settings.cohere_api_key)
        self.github_client = GitHubClient()
        
        # Senior engineer prompt template
        self.review_prompt_template = """You are a senior software engineer conducting a code review. Analyze the following code changes and provide constructive feedback.

Code Changes:
{code_diff}

File: {file_path}

Please provide:
1. Specific line-by-line comments for issues found
2. Suggestions for improvements
3. Security concerns if any
4. Performance considerations
5. Best practices recommendations

Focus on:
- Code quality and readability
- Potential bugs or edge cases
- Security vulnerabilities
- Performance optimizations
- Maintainability and scalability
- Following language-specific best practices

Be constructive and helpful. If the code looks good, acknowledge that too.

Format your response as JSON with this structure:
{{
    "comments": [
        {{
            "line": <line_number>,
            "body": "<comment_text>",
            "type": "<suggestion|warning|error|praise>"
        }}
    ],
    "summary": "<overall_review_summary>",
    "score": <1-10_rating>
}}

Keep comments concise but informative. Respect the 1000 token limit."""

    async def review_pull_request(
        self,
        owner: str,
        repo: str,
        pr_number: int,
        changed_files: List[str],
        file_diffs: Dict[str, str],
        installation_id: int
    ) -> Dict[str, Any]:
        """
        Review a pull request and post comments to GitHub.
        """
        try:
            logger.info(f"Starting code review for PR #{pr_number}")
            
            all_comments = []
            review_summaries = []
            
            # Review each changed file
            for file_path in changed_files:
                if file_path not in file_diffs:
                    logger.warning(f"No diff found for file: {file_path}")
                    continue
                
                logger.info(f"Reviewing file: {file_path}")
                
                # Get file diff
                diff_content = file_diffs[file_path]
                
                # Analyze the file
                file_review = await self._analyze_file(file_path, diff_content)
                
                if file_review["success"]:
                    # Convert comments to GitHub format
                    github_comments = self._convert_to_github_comments(
                        file_path, file_review["comments"]
                    )
                    all_comments.extend(github_comments)
                    review_summaries.append(file_review["summary"])
                    
                    logger.info(f"Generated {len(github_comments)} comments for {file_path}")
                else:
                    logger.error(f"Failed to analyze {file_path}: {file_review.get('error')}")
            
            if not all_comments:
                logger.info("No comments generated for this PR")
                return {
                    "success": True,
                    "comments": [],
                    "summary": "No issues found in code review",
                    "review_url": None
                }
            
            # Post comments to GitHub
            logger.info(f"Posting {len(all_comments)} comments to GitHub")
            post_result = self.github_client.post_review_comments(
                owner=owner,
                repo=repo,
                pr_number=pr_number,
                comments=all_comments,
                installation_id=installation_id
            )
            
            if not post_result["success"]:
                logger.error(f"Failed to post comments: {post_result.get('error')}")
                return {
                    "success": False,
                    "error": f"Failed to post comments: {post_result.get('error')}",
                    "comments": all_comments
                }
            
            # Create overall summary
            overall_summary = self._create_overall_summary(review_summaries)
            
            logger.info(f"Code review completed successfully. Posted {len(all_comments)} comments")
            
            return {
                "success": True,
                "comments": all_comments,
                "summary": overall_summary,
                "review_url": post_result.get("review_url")
            }
            
        except Exception as e:
            logger.error(f"Code review failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "comments": []
            }

    async def review_code(
        self,
        diff_content: str,
        changed_files: List[str]
    ) -> Dict[str, Any]:
        """
        Review code changes without posting to GitHub (for testing).
        """
        try:
            logger.info("Starting manual code review")
            
            all_comments = []
            review_summaries = []
            
            # For manual review, we'll analyze the diff as a whole
            review_result = await self._analyze_diff(diff_content, changed_files)
            
            if review_result["success"]:
                all_comments = review_result["comments"]
                review_summaries = [review_result["summary"]]
                
                logger.info(f"Generated {len(all_comments)} comments")
            else:
                logger.error(f"Failed to analyze diff: {review_result.get('error')}")
                return {
                    "success": False,
                    "error": review_result.get("error"),
                    "comments": []
                }
            
            # Create overall summary
            overall_summary = self._create_overall_summary(review_summaries)
            
            return {
                "success": True,
                "comments": all_comments,
                "summary": overall_summary
            }
            
        except Exception as e:
            logger.error(f"Manual code review failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "comments": []
            }

    async def _analyze_file(self, file_path: str, diff_content: str) -> Dict[str, Any]:
        """
        Analyze a single file using AI.
        """
        try:
            # Prepare prompt
            prompt = self.review_prompt_template.format(
                code_diff=diff_content,
                file_path=file_path
            )
            
            # Call Cohere API
            response = self.cohere_client.generate(
                model="command",
                prompt=prompt,
                max_tokens=1000,
                temperature=0.3,
                k=0,
                stop_sequences=[],
                return_likelihoods="NONE"
            )
            
            # Parse response
            ai_response = response.generations[0].text.strip()
            
            # Try to parse JSON response
            try:
                parsed_response = json.loads(ai_response)
                comments = parsed_response.get("comments", [])
                summary = parsed_response.get("summary", "No summary provided")
                
                # Convert to our comment format
                review_comments = []
                for comment in comments:
                    review_comments.append(CodeReviewComment(
                        path=file_path,
                        line=comment.get("line", 1),
                        body=comment.get("body", ""),
                        position=None
                    ))
                
                return {
                    "success": True,
                    "comments": review_comments,
                    "summary": summary
                }
                
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse AI response as JSON: {ai_response}")
                # Fallback: create a general comment
                return {
                    "success": True,
                    "comments": [
                        CodeReviewComment(
                            path=file_path,
                            line=1,
                            body=f"AI Review: {ai_response[:500]}...",
                            position=None
                        )
                    ],
                    "summary": "AI review completed (fallback format)"
                }
                
        except Exception as e:
            logger.error(f"Failed to analyze file {file_path}: {e}")
            return {
                "success": False,
                "error": str(e),
                "comments": []
            }

    async def _analyze_diff(self, diff_content: str, changed_files: List[str]) -> Dict[str, Any]:
        """
        Analyze a complete diff using AI.
        """
        try:
            # Prepare prompt for overall diff
            prompt = f"""You are a senior software engineer conducting a code review. Analyze the following code changes and provide constructive feedback.

Changed Files: {', '.join(changed_files)}

Code Changes:
{diff_content}

Please provide:
1. Specific line-by-line comments for issues found
2. Suggestions for improvements
3. Security concerns if any
4. Performance considerations
5. Best practices recommendations

Format your response as JSON with this structure:
{{
    "comments": [
        {{
            "line": <line_number>,
            "body": "<comment_text>",
            "type": "<suggestion|warning|error|praise>"
        }}
    ],
    "summary": "<overall_review_summary>"
}}

Keep comments concise but informative. Respect the 1000 token limit."""

            # Call Cohere API
            response = self.cohere_client.generate(
                model="command",
                prompt=prompt,
                max_tokens=1000,
                temperature=0.3,
                k=0,
                stop_sequences=[],
                return_likelihoods="NONE"
            )
            
            # Parse response
            ai_response = response.generations[0].text.strip()
            
            try:
                parsed_response = json.loads(ai_response)
                comments = parsed_response.get("comments", [])
                summary = parsed_response.get("summary", "No summary provided")
                
                # Convert to our comment format
                review_comments = []
                for comment in comments:
                    # Try to determine file path from comment context
                    file_path = changed_files[0] if changed_files else "unknown"
                    review_comments.append(CodeReviewComment(
                        path=file_path,
                        line=comment.get("line", 1),
                        body=comment.get("body", ""),
                        position=None
                    ))
                
                return {
                    "success": True,
                    "comments": review_comments,
                    "summary": summary
                }
                
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse AI response as JSON: {ai_response}")
                return {
                    "success": True,
                    "comments": [
                        CodeReviewComment(
                            path=changed_files[0] if changed_files else "unknown",
                            line=1,
                            body=f"AI Review: {ai_response[:500]}...",
                            position=None
                        )
                    ],
                    "summary": "AI review completed (fallback format)"
                }
                
        except Exception as e:
            logger.error(f"Failed to analyze diff: {e}")
            return {
                "success": False,
                "error": str(e),
                "comments": []
            }

    def _convert_to_github_comments(
        self,
        file_path: str,
        comments: List[CodeReviewComment]
    ) -> List[Dict[str, Any]]:
        """
        Convert internal comments to GitHub API format.
        """
        github_comments = []
        
        for comment in comments:
            # Extract line number from diff context
            line_number = self._extract_line_number_from_diff(comment.line, file_path)
            
            if line_number:
                github_comments.append({
                    "path": file_path,
                    "line": line_number,
                    "body": comment.body
                })
        
        return github_comments

    def _extract_line_number_from_diff(self, suggested_line: int, file_path: str) -> Optional[int]:
        """
        Extract the actual line number from diff context.
        This is a simplified implementation - in practice, you'd need more sophisticated diff parsing.
        """
        # For now, return the suggested line number
        # In a full implementation, you'd parse the diff to find the correct line numbers
        return suggested_line

    def _create_overall_summary(self, summaries: List[str]) -> str:
        """
        Create an overall summary from individual file summaries.
        """
        if not summaries:
            return "No review summaries available"
        
        if len(summaries) == 1:
            return summaries[0]
        
        # Combine multiple summaries
        combined = " ".join(summaries)
        if len(combined) > 500:
            combined = combined[:497] + "..."
        
        return combined 