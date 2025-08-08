#!/usr/bin/env python3
"""
Code Review Service
==================

AI-powered code review service using Cohere API.
"""

import logging
import json
from typing import Dict, Any, List, Optional
import cohere

from app.config import settings

logger = logging.getLogger(__name__)


class CodeReviewService:
    """AI-powered code review service."""
    
    def __init__(self):
        self.cohere_client = cohere.Client(settings.cohere_api_key)
        
    async def review_code_changes(self, diff_content: str, files: List[str]) -> Dict[str, Any]:
        """Review code changes using AI."""
        try:
            logger.info("Starting AI code review")
            
            # Prepare the prompt for code review
            prompt = self._create_review_prompt(diff_content, files)
            
            # Generate review using Cohere
            response = self.cohere_client.generate(
                model="command",
                prompt=prompt,
                max_tokens=2000,
                temperature=0.3,
                k=0,
                stop_sequences=[],
                return_likelihoods='NONE'
            )
            
            # Parse the response
            review_text = response.generations[0].text.strip()
            
            # Extract comments and summary
            comments, summary = self._parse_review_response(review_text, files)
            
            logger.info(f"Generated {len(comments)} comments")
            
            return {
                "success": True,
                "comments": comments,
                "summary": summary,
                "raw_response": review_text
            }
            
        except Exception as e:
            logger.error(f"Code review failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _create_review_prompt(self, diff_content: str, files: List[str]) -> str:
        """Create the prompt for code review."""
        
        prompt = f"""You are an expert code reviewer. Review the following code changes and provide constructive feedback.

Code Changes:
{diff_content}

Files Modified: {', '.join(files)}

Please provide a code review with the following structure:

COMMENTS:
- For each issue found, provide a comment in this format:
  File: [filename]
  Line: [line_number or general]
  Severity: [Critical/High/Medium/Low/Info]
  Comment: [detailed explanation and suggestion]

SUMMARY:
[Overall assessment of the changes, highlighting key improvements and areas of concern]

Guidelines:
1. Focus on code quality, security, performance, and maintainability
2. Be constructive and specific
3. Suggest improvements when possible
4. Limit to 5 most important comments per file
5. Prioritize by severity (Critical > High > Medium > Low > Info)
6. Consider best practices for the programming language
7. Look for potential bugs, security issues, and performance problems

Review the code now:"""

        return prompt
    
    def _parse_review_response(self, review_text: str, files: List[str]) -> tuple[List[Dict[str, Any]], str]:
        """Parse the AI review response into structured comments and summary."""
        
        comments = []
        summary = ""
        
        try:
            # Split into sections
            sections = review_text.split('\n\n')
            
            for section in sections:
                if section.strip().startswith('COMMENTS:'):
                    # Parse comments
                    comment_lines = section.split('\n')[1:]  # Skip 'COMMENTS:' header
                    
                    current_comment = {}
                    
                    for line in comment_lines:
                        line = line.strip()
                        if not line or line.startswith('-'):
                            continue
                            
                        if line.startswith('File:'):
                            if current_comment:
                                comments.append(current_comment)
                            current_comment = {'file': line.split(':', 1)[1].strip()}
                        elif line.startswith('Line:'):
                            line_info = line.split(':', 1)[1].strip()
                            if line_info.lower() != 'general':
                                try:
                                    current_comment['line'] = int(line_info)
                                except ValueError:
                                    current_comment['line'] = 1
                        elif line.startswith('Severity:'):
                            current_comment['severity'] = line.split(':', 1)[1].strip()
                        elif line.startswith('Comment:'):
                            current_comment['comment'] = line.split(':', 1)[1].strip()
                    
                    # Add the last comment
                    if current_comment:
                        comments.append(current_comment)
                        
                elif section.strip().startswith('SUMMARY:'):
                    # Extract summary
                    summary_lines = section.split('\n')[1:]  # Skip 'SUMMARY:' header
                    summary = ' '.join(summary_lines).strip()
            
            # If parsing failed, create a simple comment
            if not comments and review_text:
                comments = [{
                    'file': files[0] if files else 'unknown',
                    'line': 1,
                    'severity': 'Info',
                    'comment': review_text[:500] + '...' if len(review_text) > 500 else review_text
                }]
                
        except Exception as e:
            logger.error(f"Failed to parse review response: {e}")
            # Fallback: create a simple comment
            comments = [{
                'file': files[0] if files else 'unknown',
                'line': 1,
                'severity': 'Info',
                'comment': review_text[:500] + '...' if len(review_text) > 500 else review_text
            }]
        
        return comments, summary
    
    async def review_code(self, diff_content: str, changed_files: List[str]) -> Dict[str, Any]:
        """Legacy method for backward compatibility."""
        return await self.review_code_changes(diff_content, changed_files) 