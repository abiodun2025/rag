"""
Smart Master Agent - Automatically identifies user intent and delegates tasks seamlessly.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import re

logger = logging.getLogger(__name__)

class IntentType(Enum):
    """Types of user intents."""
    SAVE_DESKTOP = "save_desktop"
    SAVE_PROJECT = "save_project"
    EMAIL = "email"
    SEARCH = "search"
    WEB_SEARCH = "web_search"
    KNOWLEDGE_GRAPH = "knowledge_graph"
    MCP_TOOLS = "mcp_tools"
    CALL = "call"
    GENERAL = "general"

@dataclass
class IntentResult:
    """Result of intent analysis."""
    intent: IntentType
    confidence: float
    extracted_data: Dict[str, Any]
    original_message: str

class SmartMasterAgent:
    """
    Smart Master Agent that automatically identifies user intent
    and delegates tasks seamlessly without requiring specific keywords.
    """
    
    def __init__(self):
        self.task_history = []
        self.agent_stats = {}
        logger.info("Smart Master Agent initialized")
    
    def analyze_intent(self, message: str) -> IntentResult:
        """
        Analyze user message to determine intent automatically.
        
        Args:
            message: The user's message
            
        Returns:
            IntentResult with identified intent and confidence
        """
        message_lower = message.lower()
        
        # Pattern matching for different intents
        patterns = {
            IntentType.SAVE_DESKTOP: [
                r"save.*desktop",
                r"remember.*desktop", 
                r"store.*desktop",
                r"note.*desktop",
                r"desktop.*save",
                r"desktop.*remember"
            ],
            IntentType.SAVE_PROJECT: [
                r"save.*project",
                r"remember.*project",
                r"store.*project", 
                r"note.*project",
                r"project.*save",
                r"project.*remember"
            ],
            IntentType.EMAIL: [
                r"email.*to",
                r"send.*email",
                r"compose.*email",
                r"mail.*to",
                r"write.*email",
                r"send.*mail",
                r"send.*to",
                r"@.*\.com",
                r"@.*\.org",
                r"@.*\.net",
                r"@.*\.edu",
                r"@.*\.gov",
                r"@.*\.io",
                r"@.*\.ai",
                r"@.*\.co",
                r"@.*\.uk",
                r"@.*\.de",
                r"@.*\.fr",
                r"@.*\.jp",
                r"@.*\.cn",
                r"@.*\.in",
                r"@.*\.br",
                r"@.*\.ru",
                r"@.*\.au",
                r"@.*\.ca",
                r"@.*\.mx",
                r"@.*\.es",
                r"@.*\.it",
                r"@.*\.nl",
                r"@.*\.se",
                r"@.*\.no",
                r"@.*\.dk",
                r"@.*\.fi",
                r"@.*\.pl",
                r"@.*\.cz",
                r"@.*\.hu",
                r"@.*\.ro",
                r"@.*\.bg",
                r"@.*\.hr",
                r"@.*\.si",
                r"@.*\.sk",
                r"@.*\.ee",
                r"@.*\.lv",
                r"@.*\.lt",
                r"@.*\.mt",
                r"@.*\.cy",
                r"@.*\.gr",
                r"@.*\.pt",
                r"@.*\.ie",
                r"@.*\.be",
                r"@.*\.at",
                r"@.*\.ch",
                r"@.*\.li",
                r"@.*\.lu",
                r"@.*\.mc",
                r"@.*\.ad",
                r"@.*\.sm",
                r"@.*\.va",
                r"@.*\.mt",
                r"@.*\.me",
                r"@.*\.rs",
                r"@.*\.ba",
                r"@.*\.mk",
                r"@.*\.al",
                r"@.*\.xk",
                r"@.*\.tr",
                r"@.*\.ge",
                r"@.*\.am",
                r"@.*\.az",
                r"@.*\.by",
                r"@.*\.md",
                r"@.*\.ua",
                r"@.*\.kz",
                r"@.*\.uz",
                r"@.*\.kg",
                r"@.*\.tj",
                r"@.*\.tm",
                r"@.*\.af",
                r"@.*\.pk",
                r"@.*\.bd",
                r"@.*\.lk",
                r"@.*\.np",
                r"@.*\.bt",
                r"@.*\.mm",
                r"@.*\.kh",
                r"@.*\.la",
                r"@.*\.vn",
                r"@.*\.th",
                r"@.*\.my",
                r"@.*\.sg",
                r"@.*\.id",
                r"@.*\.ph",
                r"@.*\.tw",
                r"@.*\.hk",
                r"@.*\.mo",
                r"@.*\.kr",
                r"@.*\.jp",
                r"@.*\.cn",
                r"@.*\.mn",
                r"@.*\.nz",
                r"@.*\.fj",
                r"@.*\.pg",
                r"@.*\.sb",
                r"@.*\.vu",
                r"@.*\.nc",
                r"@.*\.pf",
                r"@.*\.wf",
                r"@.*\.to",
                r"@.*\.ws",
                r"@.*\.ki",
                r"@.*\.tv",
                r"@.*\.nr",
                r"@.*\.pw",
                r"@.*\.fm",
                r"@.*\.mh",
                r"@.*\.ck",
                r"@.*\.nu",
                r"@.*\.tk",
                r"@.*\.as",
                r"@.*\.gu",
                r"@.*\.mp",
                r"@.*\.vi",
                r"@.*\.pr",
                r"@.*\.do",
                r"@.*\.ht",
                r"@.*\.jm",
                r"@.*\.bb",
                r"@.*\.tt",
                r"@.*\.gd",
                r"@.*\.lc",
                r"@.*\.vc",
                r"@.*\.ag",
                r"@.*\.dm",
                r"@.*\.kn",
                r"@.*\.ai",
                r"@.*\.ms",
                r"@.*\.tc",
                r"@.*\.vg",
                r"@.*\.ky",
                r"@.*\.bm",
                r"@.*\.fk",
                r"@.*\.gs",
                r"@.*\.io",
                r"@.*\.sh",
                r"@.*\.ac",
                r"@.*\.ta",
                r"@.*\.st",
                r"@.*\.cv",
                r"@.*\.gw",
                r"@.*\.gn",
                r"@.*\.sl",
                r"@.*\.lr",
                r"@.*\.ci",
                r"@.*\.gh",
                r"@.*\.tg",
                r"@.*\.bj",
                r"@.*\.ng",
                r"@.*\.cm",
                r"@.*\.gq",
                r"@.*\.ga",
                r"@.*\.cg",
                r"@.*\.cd",
                r"@.*\.ao",
                r"@.*\.zm",
                r"@.*\.zw",
                r"@.*\.mw",
                r"@.*\.mz",
                r"@.*\.sz",
                r"@.*\.ls",
                r"@.*\.bw",
                r"@.*\.na",
                r"@.*\.za",
                r"@.*\.mg",
                r"@.*\.mu",
                r"@.*\.sc",
                r"@.*\.km",
                r"@.*\.yt",
                r"@.*\.re",
                r"@.*\.dj",
                r"@.*\.so",
                r"@.*\.et",
                r"@.*\.er",
                r"@.*\.sd",
                r"@.*\.ss",
                r"@.*\.ke",
                r"@.*\.ug",
                r"@.*\.rw",
                r"@.*\.bi",
                r"@.*\.tz",
                r"@.*\.mw",
                r"@.*\.zm",
                r"@.*\.zw",
                r"@.*\.bw",
                r"@.*\.na",
                r"@.*\.za",
                r"@.*\.ls",
                r"@.*\.sz",
                r"@.*\.mz",
                r"@.*\.mg",
                r"@.*\.mu",
                r"@.*\.sc",
                r"@.*\.km",
                r"@.*\.yt",
                r"@.*\.re",
                r"@.*\.dj",
                r"@.*\.so",
                r"@.*\.et",
                r"@.*\.er",
                r"@.*\.sd",
                r"@.*\.ss",
                r"@.*\.ke",
                r"@.*\.ug",
                r"@.*\.rw",
                r"@.*\.bi",
                r"@.*\.tz",
                r"@.*\.mw",
                r"@.*\.zm",
                r"@.*\.zw",
                r"@.*\.bw",
                r"@.*\.na",
                r"@.*\.za",
                r"@.*\.ls",
                r"@.*\.sz",
                r"@.*\.mz",
                r"@.*\.mg",
                r"@.*\.mu",
                r"@.*\.sc",
                r"@.*\.km",
                r"@.*\.yt",
                r"@.*\.re",
                r"@.*\.dj",
                r"@.*\.so",
                r"@.*\.et",
                r"@.*\.er",
                r"@.*\.sd",
                r"@.*\.ss",
                r"@.*\.ke",
                r"@.*\.ug",
                r"@.*\.rw",
                r"@.*\.bi",
                r"@.*\.tz"
            ],
            IntentType.WEB_SEARCH: [
                r"search.*web",
                r"web.*search",
                r"internet.*search",
                r"latest.*news",
                r"current.*news",
                r"what.*happening",
                r"trending.*now",
                r"recent.*developments"
            ],
            IntentType.KNOWLEDGE_GRAPH: [
                r"relationship.*between",
                r"connection.*between",
                r"how.*related",
                r"what.*relationship",
                r"graph.*query",
                r"knowledge.*graph",
                r"entity.*relationship",
                r"search.*knowledge.*graph",
                r"search.*graph",
                r"graph.*search",
                r"knowledge.*graph.*search"
            ],
            IntentType.MCP_TOOLS: [
                r"count.*r.*letter",
                r"list.*desktop",
                r"get.*desktop.*path",
                r"open.*gmail",
                r"mcp.*tool",
                r"count-r",
                r"desktop.*content",
                r"gmail.*compose"
            ],
            IntentType.CALL: [
                r"call.*\d+",
                r"dial.*\d+",
                r"phone.*\d+",
                r"ring.*\d+",
                r"call.*number",
                r"dial.*number",
                r"phone.*number",
                r"call.*\+\d+",
                r"dial.*\+\d+",
                r"phone.*\+\d+",
                r"call.*\(\d+\)",
                r"dial.*\(\d+\)",
                r"phone.*\(\d+\)",
                r"call.*\d{3}[-.\s]?\d{3}[-.\s]?\d{4}",
                r"dial.*\d{3}[-.\s]?\d{3}[-.\s]?\d{4}",
                r"phone.*\d{3}[-.\s]?\d{3}[-.\s]?\d{4}"
            ],
            IntentType.SEARCH: [
                r"search.*for",
                r"find.*information",
                r"look.*up",
                r"what.*is",
                r"who.*is",
                r"how.*to",
                r"tell.*me.*about",
                r"information.*about",
                r"details.*about",
                r"who.*owns",
                r"who.*owner",
                r"what.*company",
                r"what.*business",
                r"find.*out.*about",
                r"search.*about"
            ]
        }
        
        # Check for email patterns first (highest priority)
        for pattern in patterns[IntentType.EMAIL]:
            if re.search(pattern, message_lower):
                extracted_data = self._extract_data(message, IntentType.EMAIL)
                return IntentResult(
                    intent=IntentType.EMAIL,
                    confidence=0.9,
                    extracted_data=extracted_data,
                    original_message=message
                )
        
        # Check other patterns
        for intent_type, intent_patterns in patterns.items():
            for pattern in intent_patterns:
                if re.search(pattern, message_lower):
                    extracted_data = self._extract_data(message, intent_type)
                    confidence = 0.8 if intent_type != IntentType.GENERAL else 0.3
                    return IntentResult(
                        intent=intent_type,
                        confidence=confidence,
                        extracted_data=extracted_data,
                        original_message=message
                    )
        
        # Default to general intent
        return IntentResult(
            intent=IntentType.GENERAL,
            confidence=0.3,
            extracted_data=self._extract_data(message, IntentType.GENERAL),
            original_message=message
        )
    
    def _extract_data(self, message: str, intent: IntentType) -> Dict[str, Any]:
        """
        Extract relevant data from message based on intent.
        
        Args:
            message: The user's message
            intent: The identified intent
            
        Returns:
            Dictionary with extracted data
        """
        message_lower = message.lower()
        
        if intent == IntentType.EMAIL:
            # Extract email address
            import re
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            email_match = re.search(email_pattern, message)
            to_email = email_match.group(0) if email_match else None
            
            # Extract subject and body from the message
            subject = "Message from Agentic RAG System"
            body = "This is an automated message from the Agentic RAG System."
            
            # If no email found, try to extract from common patterns
            if not to_email:
                # Look for patterns like "send to user@domain.com" or "email user@domain.com"
                send_patterns = [
                    r'send.*to\s+([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})',
                    r'email\s+([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})',
                    r'mail\s+([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})',
                    r'to\s+([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})'
                ]
                
                for pattern in send_patterns:
                    match = re.search(pattern, message_lower)
                    if match:
                        to_email = match.group(1)
                        break
            
            # Extract the actual message content after the email address
            if to_email:
                # Find the position of the email address
                email_pos = message.find(to_email)
                if email_pos != -1:
                    # Get everything after the email address
                    after_email = message[email_pos + len(to_email):].strip()
                    
                    # Remove common email-related words
                    after_email = re.sub(r'^(send|email|mail|to)\s+', '', after_email, flags=re.IGNORECASE)
                    after_email = after_email.strip()
                    
                    if after_email:
                        # Use the first part as subject, rest as body
                        parts = after_email.split('\n', 1)
                        if len(parts) > 1:
                            subject = parts[0].strip()
                            body = parts[1].strip()
                        else:
                            # If no newline, use the whole thing as body
                            body = after_email
                            subject = "Message from Agentic RAG System"
                    else:
                        # If no content after email, try to extract from before
                        before_email = message[:email_pos].strip()
                        before_email = re.sub(r'(send|email|mail)\s+', '', before_email, flags=re.IGNORECASE)
                        before_email = before_email.strip()
                        
                        if before_email:
                            body = before_email
                            subject = "Message from Agentic RAG System"
            
            return {
                "to_email": to_email,
                "subject": subject,
                "body": body,
                "message": message
            }
            
        elif intent == IntentType.SAVE_DESKTOP:
            return {
                "message": message,
                "type": "desktop_message"
            }
            
        elif intent == IntentType.SAVE_PROJECT:
            return {
                "message": message,
                "type": "project_message"
            }
            
        elif intent == IntentType.WEB_SEARCH:
            # Extract search query
            query = message
            # Remove common search prefixes
            prefixes = ["search for", "find", "look up", "what is", "tell me about"]
            for prefix in prefixes:
                if message_lower.startswith(prefix):
                    query = message[len(prefix):].strip()
                    break
            return {
                "query": query,
                "message": message
            }
            
        elif intent == IntentType.KNOWLEDGE_GRAPH:
            # Extract search query from knowledge graph request
            query = message
            # Remove common knowledge graph prefixes
            prefixes = [
                "search the knowledge graph for information about",
                "search the knowledge graph for",
                "knowledge graph search for",
                "search knowledge graph for",
                "find in knowledge graph",
                "query knowledge graph for",
                "search graph for"
            ]
            for prefix in prefixes:
                if message_lower.startswith(prefix):
                    query = message[len(prefix):].strip()
                    break
            return {
                "query": query,
                "message": message
            }
            
        elif intent == IntentType.MCP_TOOLS:
            return {
                "message": message,
                "tool_request": message_lower
            }
            
        elif intent == IntentType.CALL:
            # Extract phone number from message
            import re
            
            # Phone number patterns
            phone_patterns = [
                r'\+?1?\s*\(?(\d{3})\)?[-.\s]?(\d{3})[-.\s]?(\d{4})',  # (123) 456-7890, +1 123 456 7890
                r'\+?(\d{1,3})\s*(\d{3})\s*(\d{3})\s*(\d{4})',       # +1 123 456 7890
                r'(\d{3})[-.\s]?(\d{3})[-.\s]?(\d{4})',              # 123-456-7890
                r'\+?(\d{10,15})',                                    # +1234567890
            ]
            
            phone_number = None
            for pattern in phone_patterns:
                match = re.search(pattern, message)
                if match:
                    if len(match.groups()) == 3:
                        # Format: (123) 456-7890 or 123-456-7890
                        phone_number = f"+1{match.group(1)}{match.group(2)}{match.group(3)}"
                    elif len(match.groups()) == 4:
                        # Format: +1 123 456 7890
                        phone_number = f"+{match.group(1)}{match.group(2)}{match.group(3)}{match.group(4)}"
                    else:
                        # Format: +1234567890
                        phone_number = f"+{match.group(1)}"
                    break
            
            # If no phone number found, try to extract any sequence of digits
            if not phone_number:
                digits_match = re.search(r'(\d{7,15})', message)
                if digits_match:
                    digits = digits_match.group(1)
                    if len(digits) == 10:
                        phone_number = f"+1{digits}"
                    elif len(digits) >= 10:
                        phone_number = f"+{digits}"
            
            return {
                "phone_number": phone_number,
                "message": message,
                "call_request": message_lower
            }
            
        elif intent == IntentType.SEARCH:
            # Extract search query
            query = message
            # Remove common search prefixes
            prefixes = ["search for", "find", "look up", "what is", "tell me about", "information about", "details about"]
            for prefix in prefixes:
                if message_lower.startswith(prefix):
                    query = message[len(prefix):].strip()
                    break
            return {
                "query": query,
                "message": message
            }
            
        else:  # IntentType.GENERAL
            return {
                "message": message,
                "general_query": message
            }
    
    async def execute_intent(self, intent_result: IntentResult, session_id: str, user_id: str = None) -> Dict[str, Any]:
        """
        Execute the identified intent.
        
        Args:
            intent_result: The identified intent
            session_id: Session ID
            user_id: User ID
            
        Returns:
            Execution result
        """
        start_time = datetime.now()
        
        try:
            if intent_result.intent == IntentType.SAVE_DESKTOP:
                result = await self._save_to_desktop(intent_result.extracted_data, session_id, user_id)
            elif intent_result.intent == IntentType.SAVE_PROJECT:
                result = await self._save_to_project(intent_result.extracted_data, session_id, user_id)
            elif intent_result.intent == IntentType.EMAIL:
                result = await self._handle_email(intent_result.extracted_data, session_id, user_id)
            elif intent_result.intent == IntentType.WEB_SEARCH:
                result = await self._web_search(intent_result.extracted_data, session_id, user_id)
            elif intent_result.intent == IntentType.SEARCH:
                result = await self._internal_search(intent_result.extracted_data, session_id, user_id)
            elif intent_result.intent == IntentType.KNOWLEDGE_GRAPH:
                result = await self._knowledge_graph_search(intent_result.extracted_data, session_id, user_id)
            elif intent_result.intent == IntentType.MCP_TOOLS:
                result = await self._handle_mcp_tools(intent_result.extracted_data, session_id, user_id)
            elif intent_result.intent == IntentType.CALL:
                result = await self._handle_call(intent_result.extracted_data, session_id, user_id)
            else:  # GENERAL
                result = await self._general_response(intent_result.extracted_data, session_id, user_id)
            
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            # Update stats
            intent_name = intent_result.intent.value
            if intent_name not in self.agent_stats:
                self.agent_stats[intent_name] = {"calls": 0, "success": 0, "errors": 0}
            self.agent_stats[intent_name]["calls"] += 1
            self.agent_stats[intent_name]["success"] += 1
            
            return {
                "success": True,
                "intent": intent_result.intent.value,
                "confidence": intent_result.confidence,
                "result": result,
                "execution_time": execution_time,
                "message": self._get_user_friendly_message(intent_result.intent, result)
            }
            
        except Exception as e:
            logger.error(f"Intent execution failed: {e}")
            
            # Update error stats
            intent_name = intent_result.intent.value
            if intent_name not in self.agent_stats:
                self.agent_stats[intent_name] = {"calls": 0, "success": 0, "errors": 0}
            self.agent_stats[intent_name]["calls"] += 1
            self.agent_stats[intent_name]["errors"] += 1
            
            return {
                "success": False,
                "intent": intent_result.intent.value,
                "confidence": intent_result.confidence,
                "error": str(e),
                "execution_time": 0,
                "message": f"I encountered an error while processing your request: {str(e)}"
            }
    
    async def _save_to_desktop(self, data: Dict[str, Any], session_id: str, user_id: str) -> Dict[str, Any]:
        """Save message to desktop."""
        from .desktop_message_tools import desktop_storage
        
        content = data.get("message", "")
        result = desktop_storage.save_message(
            message=content,
            message_type="user_message",
            metadata={"source": "smart_master_agent", "session_id": session_id}
        )
        
        return {
            "action": "saved_to_desktop",
            "file_path": result.get("file_path", ""),
            "message_id": result.get("message_id", "")
        }
    
    async def _save_to_project(self, data: Dict[str, Any], session_id: str, user_id: str) -> Dict[str, Any]:
        """Save message to project."""
        from .message_tools import message_storage
        
        content = data.get("message", "")
        result = message_storage.save_message(
            message=content,
            message_type="user_message",
            metadata={"source": "smart_master_agent", "session_id": session_id}
        )
        
        return {
            "action": "saved_to_project",
            "file_path": result.get("file_path", ""),
            "message_id": result.get("message_id", "")
        }
    
    async def _handle_email(self, data: Dict[str, Any], session_id: str, user_id: str) -> Dict[str, Any]:
        """Handle email composition using MCP tools."""
        try:
            from .mcp_tools import sendmail_simple_tool, SendmailSimpleInput
            
            to_email = data.get("to_email")
            subject = data.get("subject", "Message from Agentic RAG System")
            body = data.get("body", "This is an automated message from the Agentic RAG System.")
            
            if not to_email:
                return {
                    "action": "email_error",
                    "error": "No email address provided",
                    "note": "Please provide a valid email address"
                }
            
            # Use MCP tool to send email
            input_data = SendmailSimpleInput(
                to_email=to_email,
                subject=subject,
                message=body
            )
            
            result = await sendmail_simple_tool(input_data)
            
            if result.get("success"):
                return {
                    "action": "email_sent",
                    "to_email": to_email,
                    "subject": subject,
                    "result": result.get("result", "Email sent successfully"),
                    "note": "Email sent using MCP server tools"
                }
            else:
                return {
                    "action": "email_error",
                    "to_email": to_email,
                    "error": result.get("error", "Unknown error"),
                    "note": "Failed to send email via MCP server"
                }
                
        except Exception as e:
            logger.error(f"Email handling failed: {e}")
            return {
                "action": "email_error",
                "error": str(e),
                "note": "Email handling failed - MCP server may not be running"
            }
    
    async def _web_search(self, data: Dict[str, Any], session_id: str, user_id: str) -> Dict[str, Any]:
        """Perform web search."""
        from .web_search_tools import web_search_tools
        
        query = data.get("query", "")
        results = await web_search_tools.search_web(query, max_results=5)
        
        formatted_results = []
        for result in results:
            formatted_results.append({
                "title": result.title,
                "url": result.url,
                "snippet": result.snippet,
                "source": result.source
            })
        
        return {
            "action": "web_search",
            "query": query,
            "results": formatted_results,
            "total_results": len(formatted_results)
        }
    
    async def _internal_search(self, data: Dict[str, Any], session_id: str, user_id: str) -> Dict[str, Any]:
        """Perform internal search with web search fallback."""
        from .tools import vector_search_tool, web_search_tool, WebSearchInput
        from .schemas import VectorSearchInput
        
        query = data.get("query", "")
        search_input = VectorSearchInput(query=query, limit=5)
        results = await vector_search_tool(search_input)
        
        # If internal search returns no results, try web search as fallback
        if not results or len(results) == 0:
            logger.info(f"No internal results found for '{query}', trying web search fallback")
            
            try:
                # Use the web_search_tool from tools.py
                web_search_input = WebSearchInput(query=query, max_results=5)
                web_results = await web_search_tool(web_search_input)
                
                if web_results:
                    return {
                        "action": "internal_search_with_web_fallback",
                        "internal_results": [],
                        "web_results": web_results,
                        "total_results": len(web_results),
                        "message": f"No internal results found, but I found {len(web_results)} web results for you! 🌐"
                    }
                else:
                    return {
                        "action": "internal_search_with_web_fallback",
                        "internal_results": [],
                        "web_results": [],
                        "total_results": 0,
                        "message": "No results found in internal knowledge base or web search."
                    }
            except Exception as e:
                logger.error(f"Web search fallback failed: {e}")
                return {
                    "action": "internal_search_with_web_fallback",
                    "internal_results": [],
                    "web_results": [],
                    "total_results": 0,
                    "message": "No internal results found, and web search fallback failed."
                }
        
        # Return internal results if found
        return {
            "action": "internal_search",
            "internal_results": results,
            "web_results": [],
            "total_results": len(results),
            "message": f"Found {len(results)} internal results for your search"
        }
    
    async def _knowledge_graph_search(self, data: Dict[str, Any], session_id: str, user_id: str) -> Dict[str, Any]:
        """Perform knowledge graph search with web search fallback."""
        from .tools import graph_search_tool, web_search_tool, WebSearchInput
        from .schemas import GraphSearchInput
        
        query = data.get("query", "")
        search_input = GraphSearchInput(query=query)
        results = await graph_search_tool(search_input)
        
        # If knowledge graph search returns no results, try web search as fallback
        if not results or len(results) == 0:
            logger.info(f"No knowledge graph results found for '{query}', trying web search fallback")
            
            try:
                # Use the web_search_tool from tools.py
                web_search_input = WebSearchInput(query=query, max_results=5)
                web_results = await web_search_tool(web_search_input)
                
                if web_results:
                    return {
                        "action": "knowledge_graph_search_with_web_fallback",
                        "graph_results": [],
                        "web_results": web_results,
                        "total_results": len(web_results),
                        "message": f"No knowledge graph results found, but I found {len(web_results)} web results for you! 🌐"
                    }
                else:
                    return {
                        "action": "knowledge_graph_search_with_web_fallback",
                        "graph_results": [],
                        "web_results": [],
                        "total_results": 0,
                        "message": "No results found in knowledge graph or web search."
                    }
            except Exception as e:
                logger.error(f"Web search fallback failed: {e}")
                return {
                    "action": "knowledge_graph_search_with_web_fallback",
                    "graph_results": [],
                    "web_results": [],
                    "total_results": 0,
                    "message": "No knowledge graph results found, and web search fallback failed."
                }
        
        # Return knowledge graph results if found
        return {
            "action": "knowledge_graph_search",
            "graph_results": results,
            "web_results": [],
            "total_results": len(results),
            "message": f"Found {len(results)} knowledge graph results for your search"
        }
    
    async def _handle_mcp_tools(self, data: Dict[str, Any], session_id: str, user_id: str) -> Dict[str, Any]:
        """Handle MCP tools requests."""
        try:
            from .mcp_tools import (
                count_r_tool, list_desktop_contents_tool, get_desktop_path_tool,
                open_gmail_tool, open_gmail_compose_tool, sendmail_simple_tool,
                list_mcp_tools, generic_mcp_tool,
                CountRInput, DesktopContentsInput, DesktopPathInput, 
                OpenGmailInput, OpenGmailComposeInput, SendmailSimpleInput, MCPToolInput
            )
            
            message = data.get("message", "").lower()
            
            # Count R letters
            if "count" in message and "r" in message and "letter" in message:
                # Extract word from message
                import re
                word_match = re.search(r'count.*r.*letters.*in.*the.*word\s+(\w+)', message)
                if word_match:
                    word = word_match.group(1)
                    input_data = CountRInput(word=word)
                    result = await count_r_tool(input_data)
                    return {
                        "action": "mcp_count_r",
                        "word": word,
                        "result": result,
                        "note": "Used MCP server to count 'r' letters"
                    }
            
            # List desktop files
            elif "list" in message and "desktop" in message and ("file" in message or "content" in message):
                input_data = DesktopContentsInput()
                result = await list_desktop_contents_tool(input_data)
                return {
                    "action": "mcp_list_desktop",
                    "result": result,
                    "note": "Used MCP server to list desktop contents"
                }
            
            # Get desktop path
            elif "get" in message and "desktop" in message and "path" in message:
                input_data = DesktopPathInput()
                result = await get_desktop_path_tool(input_data)
                return {
                    "action": "mcp_get_desktop_path",
                    "result": result,
                    "note": "Used MCP server to get desktop path"
                }
            
            # Open Gmail
            elif "open" in message and "gmail" in message:
                if "compose" in message:
                    input_data = OpenGmailComposeInput()
                    result = await open_gmail_compose_tool(input_data)
                    return {
                        "action": "mcp_open_gmail_compose",
                        "result": result,
                        "note": "Used MCP server to open Gmail compose"
                    }
                else:
                    input_data = OpenGmailInput()
                    result = await open_gmail_tool(input_data)
                    return {
                        "action": "mcp_open_gmail",
                        "result": result,
                        "note": "Used MCP server to open Gmail"
                    }
            
            # List available MCP tools
            elif "list" in message and "available" in message and "mcp" in message and "tool" in message:
                result = await list_mcp_tools()
                return {
                    "action": "mcp_list_tools",
                    "result": result,
                    "note": "Used MCP server to list available tools"
                }
            
            # Generic MCP tool call
            elif "call" in message and "mcp" in message and "tool" in message:
                # Extract tool name and parameters
                import re
                tool_match = re.search(r'call.*mcp.*tool\s+(\w+)', message)
                if tool_match:
                    tool_name = tool_match.group(1)
                    # For now, use default parameters
                    input_data = MCPToolInput(tool_name=tool_name, parameters={})
                    result = await generic_mcp_tool(input_data)
                    return {
                        "action": "mcp_generic_call",
                        "tool_name": tool_name,
                        "result": result,
                        "note": f"Used MCP server to call {tool_name}"
                    }
            
            # Default response for MCP tools
            else:
                result = await list_mcp_tools()
                return {
                    "action": "mcp_tools_info",
                    "result": result,
                    "note": "MCP tools are available. Use specific commands to call them."
                }
                
        except Exception as e:
            logger.error(f"MCP tools handling failed: {e}")
            return {
                "action": "mcp_error",
                "error": str(e),
                "note": "MCP tools failed - server may not be running"
            }

    async def _handle_call(self, data: Dict[str, Any], session_id: str, user_id: str) -> Dict[str, Any]:
        """Handle phone call requests."""
        from .real_google_voice_calling import real_google_voice_caller
        import subprocess
        
        phone_number = data.get("phone_number")
        if not phone_number:
            return {
                "action": "call_error",
                "error": "No phone number found",
                "note": "Please provide a valid phone number"
            }
        
        try:
            # Use real Google Voice calling directly
            result = real_google_voice_caller.make_real_call(phone_number, "Smart Agent")
            
            if result["success"]:
                return {
                    "action": "call_initiated",
                    "phone_number": result["phone_number"],
                    "method": result["method"],
                    "note": result["message"],
                    "instructions": result.get("instructions", []),
                    "real_call_note": result["note"]
                }
            else:
                # Fallback to system dialer
                subprocess.run(['open', f'tel:{phone_number}'], check=True)
                return {
                    "action": "call_fallback",
                    "phone_number": phone_number,
                    "method": "system_dialer",
                    "note": f"Call initiated to {phone_number} via system dialer",
                    "fallback_reason": "Real calling failed, using system dialer"
                }
                
        except Exception as e:
            try:
                # Emergency fallback to system dialer
                subprocess.run(['open', f'tel:{phone_number}'], check=True)
                return {
                    "action": "call_emergency_fallback",
                    "phone_number": phone_number,
                    "method": "system_dialer",
                    "note": f"Call initiated to {phone_number} via system dialer (emergency fallback)",
                    "error": str(e)
                }
            except:
                return {
                    "action": "call_error",
                    "phone_number": phone_number,
                    "error": "Failed to initiate call",
                    "note": f"All calling methods failed. Try manually dialing {phone_number}"
                }

    async def _general_response(self, data: Dict[str, Any], session_id: str, user_id: str) -> Dict[str, Any]:
        """Handle general conversation."""
        return {
            "action": "general_response",
            "message": data.get("message", ""),
            "note": "General conversation - I'm here to help!"
        }
    
    def _get_user_friendly_message(self, intent: IntentType, result: Dict[str, Any]) -> str:
        """Generate user-friendly message based on intent and result."""
        if intent == IntentType.SAVE_DESKTOP:
            return f"✅ Saved to Desktop: {result.get('file_path', '')}"
        elif intent == IntentType.SAVE_PROJECT:
            return f"✅ Saved to Project: {result.get('file_path', '')}"
        elif intent == IntentType.EMAIL:
            if result.get('action') == 'email_sent':
                return f"📧 Email sent successfully to {result.get('to_email', 'recipient')}"
            elif result.get('action') == 'email_error':
                return f"❌ Email error: {result.get('error', 'Unknown error')}"
            else:
                return f"📧 Email composition ready for {result.get('to_email', 'recipient')}"
        elif intent == IntentType.MCP_TOOLS:
            if result.get('action', '').startswith('mcp_'):
                return f"🔧 {result.get('note', 'MCP tool executed')}"
            else:
                return f"🔧 MCP tools available - {result.get('note', 'Use specific commands')}"
        elif intent == IntentType.CALL:
            if result.get('action') == 'call_initiated':
                message = f"📞 {result.get('note', 'Call initiated')}"
                # Add MCP server note if available
                mcp_note = result.get('mcp_note', '')
                if mcp_note:
                    message += f"\n🔧 {mcp_note}"
                # Add instructions if available
                instructions = result.get('instructions', [])
                if instructions:
                    message += "\n\n📋 Instructions:\n" + "\n".join(instructions)
                return message
            elif result.get('action') == 'call_fallback':
                message = f"📞 {result.get('note', 'Call fallback activated')}"
                fallback_reason = result.get('fallback_reason', '')
                if fallback_reason:
                    message += f"\n⚠️ {fallback_reason}"
                instructions = result.get('instructions', [])
                if instructions:
                    message += "\n\n📋 Instructions:\n" + "\n".join(instructions)
                return message
            elif result.get('action') == 'call_emergency_fallback':
                message = f"📞 {result.get('note', 'Emergency call fallback')}"
                error = result.get('error', '')
                if error:
                    message += f"\n⚠️ Error: {error}"
                return message
            elif result.get('action') == 'call_error':
                return f"❌ {result.get('error', 'Call failed')}"
            else:
                return f"📞 Call processed: {result.get('note', 'Call action completed')}"
        elif intent == IntentType.WEB_SEARCH:
            count = result.get('total_results', 0)
            return f"🌐 Found {count} web results for your search"
        elif intent == IntentType.SEARCH:
            # Handle web search fallback case
            if result.get('action') == 'internal_search_with_web_fallback':
                web_count = result.get('total_results', 0)
                return f"✅ 🔍 No internal results found, but I found {web_count} web results for you! 🌐"
            elif result.get('action') == 'knowledge_graph_search_with_web_fallback':
                web_count = result.get('total_results', 0)
                return f"🧠 No knowledge graph results found, but I found {web_count} web results for you! 🌐"
            else:
                count = result.get('total_results', 0)
                return f"✅ 🔍 Found {count} internal results for your search"
        else:
            return result.get('message', 'Operation completed')
    
    async def process_message(self, message: str, session_id: str, user_id: str = None) -> Dict[str, Any]:
        """
        Process a user message intelligently.
        
        Args:
            message: User message
            session_id: Session ID
            user_id: User ID
            
        Returns:
            Processing result
        """
        logger.info(f"Smart Master Agent processing: {message}")
        
        # Analyze intent
        intent_result = self.analyze_intent(message)
        logger.info(f"Identified intent: {intent_result.intent.value} (confidence: {intent_result.confidence:.2f})")
        
        # Execute intent
        result = await self.execute_intent(intent_result, session_id, user_id)
        
        # Compile summary
        summary = {
            "original_message": message,
            "session_id": session_id,
            "user_id": user_id,
            "intent_analysis": {
                "intent": intent_result.intent.value,
                "confidence": intent_result.confidence,
                "extracted_data": intent_result.extracted_data
            },
            "execution_result": result,
            "agent_stats": self.agent_stats
        }
        
        logger.info(f"Smart Master Agent completed processing")
        return summary

# Global smart master agent instance
smart_master_agent = SmartMasterAgent() 