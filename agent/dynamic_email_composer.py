"""
Dynamic Email Composer using LLM
================================

This module provides dynamic email composition using LLM to generate
professional email content based on user requests and context.
"""

import asyncio
import re
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
from pydantic import BaseModel

from .providers import get_llm_model
# from .email_tools import compose_email  # Commented out to use MCP tools instead

logger = logging.getLogger(__name__)

class EmailRequest(BaseModel):
    """Email request data structure."""
    to_email: str
    subject: Optional[str] = None
    body: Optional[str] = None
    context: Optional[str] = None
    tone: Optional[str] = "professional"
    urgency: Optional[str] = "normal"
    purpose: Optional[str] = None
    original_message: Optional[str] = None

class DynamicEmailComposer:
    """Dynamic email composer using LLM for content generation."""
    
    def __init__(self):
        self.llm_model = get_llm_model()
        self.email_templates = {
            "professional": self._get_professional_template(),
            "casual": self._get_casual_template(),
            "formal": self._get_formal_template(),
            "friendly": self._get_friendly_template(),
            "urgent": self._get_urgent_template()
        }
    
    def _get_professional_template(self) -> str:
        return """
You are a professional email composer. Create a well-structured email based on the following information:

RECIPIENT: {to_email}
CONTEXT: {context}
ORIGINAL REQUEST: {original_message}
PURPOSE: {purpose}
TONE: Professional but approachable
URGENCY: {urgency}

Requirements:
- Write a clear, concise subject line
- Compose a professional email body
- Use appropriate greeting and closing
- Keep it under 200 words unless more detail is needed
- Be specific and actionable
- Maintain professional tone

Format your response as:
SUBJECT: [subject line]
BODY: [email body]
"""
    
    def _get_casual_template(self) -> str:
        return """
You are composing a casual, friendly email. Create a relaxed email based on the following information:

RECIPIENT: {to_email}
CONTEXT: {context}
ORIGINAL REQUEST: {original_message}
PURPOSE: {purpose}
TONE: Casual and friendly
URGENCY: {urgency}

Requirements:
- Write a friendly subject line
- Compose a casual email body
- Use informal but respectful language
- Keep it conversational
- Be warm and approachable

Format your response as:
SUBJECT: [subject line]
BODY: [email body]
"""
    
    def _get_formal_template(self) -> str:
        return """
You are composing a formal business email. Create a highly professional email based on the following information:

RECIPIENT: {to_email}
CONTEXT: {context}
ORIGINAL REQUEST: {original_message}
PURPOSE: {purpose}
TONE: Formal and business-like
URGENCY: {urgency}

Requirements:
- Write a formal subject line
- Compose a professional email body
- Use formal business language
- Include proper salutations and closings
- Be precise and detailed
- Maintain formal tone throughout

Format your response as:
SUBJECT: [subject line]
BODY: [email body]
"""
    
    def _get_friendly_template(self) -> str:
        return """
You are composing a friendly, warm email. Create a personable email based on the following information:

RECIPIENT: {to_email}
CONTEXT: {context}
ORIGINAL REQUEST: {original_message}
PURPOSE: {purpose}
TONE: Friendly and warm
URGENCY: {urgency}

Requirements:
- Write a friendly subject line
- Compose a warm email body
- Use friendly, personable language
- Show genuine interest and warmth
- Be encouraging and positive
- Keep it personal and engaging

Format your response as:
SUBJECT: [subject line]
BODY: [email body]
"""
    
    def _get_urgent_template(self) -> str:
        return """
You are composing an urgent email. Create a concise, urgent email based on the following information:

RECIPIENT: {to_email}
CONTEXT: {context}
ORIGINAL REQUEST: {original_message}
PURPOSE: {purpose}
TONE: Urgent but professional
URGENCY: High priority

Requirements:
- Write a clear, urgent subject line
- Compose a concise email body
- Emphasize urgency appropriately
- Be direct and actionable
- Include clear next steps
- Keep it brief but complete

Format your response as:
SUBJECT: [subject line]
BODY: [email body]
"""
    
    async def compose_dynamic_email(self, request: EmailRequest) -> Dict[str, Any]:
        """
        Compose a dynamic email using LLM based on the request.
        
        Args:
            request: EmailRequest object with all necessary information
            
        Returns:
            Dict containing the composed email details
        """
        try:
            # Determine the appropriate template based on tone
            template = self.email_templates.get(request.tone, self.email_templates["professional"])
            
            # Prepare context for LLM
            context = self._prepare_context(request)
            
            # Generate email content using LLM
            prompt = template.format(
                to_email=request.to_email,
                context=context,
                original_message=request.original_message or "",
                purpose=request.purpose or "General communication",
                urgency=request.urgency
            )
            
            # Get LLM response
            response = await self.llm_model.generate(prompt)
            email_content = response.choices[0].message.content
            
            # Parse the response
            subject, body = self._parse_llm_response(email_content)
            
            # Validate and clean the content
            subject = self._clean_subject(subject)
            body = self._clean_body(body)
            
            # Compose and send the email using MCP tools
            from .mcp_tools import sendmail_simple_tool, SendmailSimpleInput
            
            input_data = SendmailSimpleInput(
                to_email=request.to_email,
                subject=subject,
                message=body
            )
            
            result = await sendmail_simple_tool(input_data)
            
            return {
                "status": "success",
                "email_sent": True,
                "to_email": request.to_email,
                "subject": subject,
                "body": body,
                "body_preview": body[:100] + "..." if len(body) > 100 else body,
                "tone": request.tone,
                "urgency": request.urgency,
                "composed_at": datetime.now().isoformat(),
                "message_id": result.get("result", "sent"),
                "thread_id": result.get("result", "sent")
            }
            
        except Exception as e:
            logger.error(f"Dynamic email composition failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "email_sent": False
            }
    
    def _prepare_context(self, request: EmailRequest) -> str:
        """Prepare context information for the LLM."""
        context_parts = []
        
        if request.context:
            context_parts.append(f"Context: {request.context}")
        
        if request.purpose:
            context_parts.append(f"Purpose: {request.purpose}")
        
        # Extract additional context from original message
        if request.original_message:
            # Remove email address and common command words
            cleaned_message = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '', request.original_message)
            cleaned_message = re.sub(r'\b(send|email|mail|to|write|compose|ask|tell)\b', '', cleaned_message, flags=re.IGNORECASE)
            cleaned_message = cleaned_message.strip()
            
            if cleaned_message and len(cleaned_message) > 5:
                context_parts.append(f"Request details: {cleaned_message}")
        
        return " | ".join(context_parts) if context_parts else "General communication"
    
    def _parse_llm_response(self, response: str) -> tuple[str, str]:
        """Parse the LLM response to extract subject and body."""
        subject = ""
        body = ""
        
        lines = response.strip().split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('SUBJECT:'):
                current_section = 'subject'
                subject = line.replace('SUBJECT:', '').strip()
            elif line.startswith('BODY:'):
                current_section = 'body'
                body = line.replace('BODY:', '').strip()
            elif current_section == 'body':
                body += '\n' + line
            elif current_section == 'subject' and not subject:
                subject = line
        
        # Fallback if parsing fails
        if not subject and not body:
            # Try to extract subject from first line
            lines = response.strip().split('\n')
            if lines:
                subject = lines[0][:50]  # First 50 chars as subject
                body = '\n'.join(lines[1:]) if len(lines) > 1 else "Please see the subject for details."
        
        return subject, body
    
    def _clean_subject(self, subject: str) -> str:
        """Clean and validate the subject line."""
        if not subject:
            return "Message from Agentic RAG System"
        
        # Remove any remaining formatting
        subject = re.sub(r'^SUBJECT:\s*', '', subject, flags=re.IGNORECASE)
        subject = subject.strip()
        
        # Limit length
        if len(subject) > 100:
            subject = subject[:97] + "..."
        
        return subject
    
    def _clean_body(self, body: str) -> str:
        """Clean and validate the email body."""
        if not body:
            return "This is an automated message from the Agentic RAG System."
        
        # Remove any remaining formatting
        body = re.sub(r'^BODY:\s*', '', body, flags=re.IGNORECASE)
        body = body.strip()
        
        # Ensure proper line breaks
        body = body.replace('\n\n\n', '\n\n')
        
        return body
    
    async def analyze_email_request(self, message: str) -> EmailRequest:
        """
        Analyze a natural language email request and extract structured data.
        
        Args:
            message: Natural language email request
            
        Returns:
            EmailRequest object with extracted information
        """
        # Extract email address
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, message)
        to_email = email_match.group() if email_match else ""
        
        # Determine tone
        tone = "professional"
        if any(word in message.lower() for word in ["casual", "friendly", "informal"]):
            tone = "casual"
        elif any(word in message.lower() for word in ["formal", "business", "official"]):
            tone = "formal"
        elif any(word in message.lower() for word in ["urgent", "asap", "immediately"]):
            tone = "urgent"
        
        # Determine urgency
        urgency = "normal"
        if any(word in message.lower() for word in ["urgent", "asap", "immediately", "emergency"]):
            urgency = "high"
        elif any(word in message.lower() for word in ["when convenient", "no rush", "take your time"]):
            urgency = "low"
        
        # Extract purpose
        purpose = "General communication"
        if "meeting" in message.lower():
            purpose = "Meeting coordination"
        elif "follow up" in message.lower():
            purpose = "Follow up"
        elif "question" in message.lower() or "ask" in message.lower():
            purpose = "Question or inquiry"
        elif "thank" in message.lower():
            purpose = "Thank you"
        elif "apologize" in message.lower() or "sorry" in message.lower():
            purpose = "Apology"
        
        return EmailRequest(
            to_email=to_email,
            context=message,
            tone=tone,
            urgency=urgency,
            purpose=purpose,
            original_message=message
        )

# Global instance
dynamic_composer = DynamicEmailComposer()

async def compose_dynamic_email(to_email: str, context: str, tone: str = "professional", 
                               urgency: str = "normal", purpose: str = None) -> Dict[str, Any]:
    """
    Convenience function to compose a dynamic email.
    
    Args:
        to_email: Recipient email address
        context: Context or message content
        tone: Email tone (professional, casual, formal, friendly, urgent)
        urgency: Urgency level (low, normal, high)
        purpose: Purpose of the email
        
    Returns:
        Dict containing the email composition result
    """
    request = EmailRequest(
        to_email=to_email,
        context=context,
        tone=tone,
        urgency=urgency,
        purpose=purpose
    )
    
    return await dynamic_composer.compose_dynamic_email(request)

async def analyze_and_compose_email(message: str) -> Dict[str, Any]:
    """
    Analyze a natural language email request and compose the email.
    
    Args:
        message: Natural language email request
        
    Returns:
        Dict containing the email composition result
    """
    request = await dynamic_composer.analyze_email_request(message)
    
    if not request.to_email:
        return {
            "status": "error",
            "error": "No email address found in the request",
            "note": "Please include a valid email address in your request."
        }
    
    return await dynamic_composer.compose_dynamic_email(request) 