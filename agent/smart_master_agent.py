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

from .models import Message
from .message_tools import message_storage
from .mcp_tools import MCPClient
from .email_composer import email_composer
from .content_generator import content_generator
from .academic_writer import academic_writer  # Add academic writer import
from .research_enhanced_writer import research_enhanced_writer  # Add research-enhanced writer import

logger = logging.getLogger(__name__)

class IntentType(Enum):
    """Types of user intents."""
    SAVE_DESKTOP = "save_desktop"
    SAVE_PROJECT = "save_project"
    EMAIL = "email"
    CONTENT_GENERATION = "content_generation"
    ACADEMIC_WRITING = "academic_writing"  # Add academic writing intent
    RESEARCH_WRITING = "research_writing"  # Add research-enhanced writing intent


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
        
        # Intent patterns with confidence scores
        intent_patterns = {
            IntentType.SAVE_DESKTOP: [
                (r"save.*desktop", 0.9),
                (r"store.*desktop", 0.8),
                (r"backup.*desktop", 0.8),
                (r"save.*message.*desktop", 0.9),
                (r"store.*message.*desktop", 0.8)
            ],
            IntentType.SAVE_PROJECT: [
                (r"save.*project", 0.9),
                (r"store.*project", 0.8),
                (r"save.*message.*project", 0.9),
                (r"store.*message.*project", 0.8)
            ],
            IntentType.EMAIL: [
                (r"send.*email", 0.9),
                (r"write.*email", 0.9),
                (r"compose.*email", 0.9),
                (r"email.*to", 0.8),
                (r"send.*mail", 0.8),
                (r"write.*mail", 0.8),
                (r"compose.*mail", 0.8),
                (r"mail.*to", 0.7),
                (r"thank.*email", 0.8),
                (r"greeting.*email", 0.8),
                (r"follow.*up.*email", 0.8),
                (r"meeting.*email", 0.8),
                (r"schedule.*meeting", 0.8),
                (r"meeting.*for", 0.8),
                (r"meeting.*at", 0.8)
            ],
            IntentType.CONTENT_GENERATION: [
                (r"write.*about", 0.9),
                (r"generate.*content.*about", 0.9),
                (r"create.*content.*about", 0.9),
                (r"compose.*about", 0.8),
                (r"write.*on", 0.8),
                (r"generate.*text.*about", 0.8),
                (r"create.*text.*about", 0.8),
                (r"write.*essay.*about", 0.8),
                (r"generate.*article.*about", 0.8),
                (r"create.*article.*about", 0.8),
                (r"write.*blog.*about", 0.8),
                (r"create.*blog.*about", 0.8),
                (r"write.*report.*about", 0.8),
                (r"generate.*report.*about", 0.8),
                (r"write.*story.*about", 0.8),
                (r"create.*story.*about", 0.8),
                (r"explain.*about", 0.7),
                (r"discuss.*about", 0.7),
                (r"describe.*about", 0.7),
                (r"tell.*me.*about", 0.7),
                (r"write.*paragraphs.*about", 0.8),
                (r"generate.*paragraphs.*about", 0.8),
                (r"create.*paragraphs.*about", 0.8)
            ],
            IntentType.ACADEMIC_WRITING: [
                (r"write.*academic.*essay", 0.9),
                (r"write.*research.*paper", 0.9),
                (r"write.*thesis", 0.9),
                (r"write.*dissertation", 0.9),
                (r"write.*academic.*paper", 0.9),
                (r"write.*scholarly.*paper", 0.9),
                (r"write.*argumentative.*essay", 0.9),
                (r"write.*analytical.*essay", 0.9),
                (r"write.*expository.*essay", 0.9),
                (r"write.*narrative.*essay", 0.9),
                (r"write.*compare.*contrast.*essay", 0.9),
                (r"write.*academic.*article", 0.8),
                (r"write.*academic.*report", 0.8),
                (r"write.*academic.*content", 0.8),
                (r"academic.*writing", 0.8),
                (r"scholarly.*writing", 0.8),
                (r"research.*writing", 0.8),
                (r"academic.*essay.*about", 0.9),
                (r"research.*paper.*about", 0.9),
                (r"thesis.*about", 0.9),
                (r"dissertation.*about", 0.9),
                (r"argumentative.*essay.*about", 0.9),
                (r"analytical.*essay.*about", 0.9),
                (r"expository.*essay.*about", 0.9),
                (r"narrative.*essay.*about", 0.9),
                (r"compare.*contrast.*essay.*about", 0.9)
            ],
            IntentType.RESEARCH_WRITING: [
                (r"research.*essay.*about", 0.9),
                (r"research.*paper.*about", 0.9),
                (r"research.*argumentative.*essay", 0.9),
                (r"research.*analytical.*essay", 0.9),
                (r"research.*expository.*essay", 0.9),
                (r"research.*narrative.*essay", 0.9),
                (r"research.*compare.*contrast.*essay", 0.9),
                (r"research.*thesis.*about", 0.9),
                (r"research.*dissertation.*about", 0.9),
                (r"research.*article.*about", 0.8),
                (r"research.*report.*about", 0.8),
                (r"research.*content.*about", 0.8),
                (r"research.*enhanced.*essay", 0.9),
                (r"research.*enhanced.*paper", 0.9),
                (r"research.*enhanced.*writing", 0.8),
                (r"write.*research.*enhanced.*essay", 0.9),
                (r"write.*research.*enhanced.*paper", 0.9),
                (r"write.*research.*enhanced.*content", 0.8),
                (r"research.*essay.*on", 0.9),
                (r"research.*paper.*on", 0.9),
                (r"research.*argumentative.*essay.*on", 0.9),
                (r"research.*analytical.*essay.*on", 0.9),
                (r"research.*expository.*essay.*on", 0.9),
                (r"research.*narrative.*essay.*on", 0.9),
                (r"research.*compare.*contrast.*essay.*on", 0.9)
            ],


            IntentType.SEARCH: [
                (r"search.*for", 0.9),
                (r"find.*information.*about", 0.8),
                (r"look.*up", 0.8),
                (r"search.*about", 0.8),
                (r"find.*about", 0.8)
            ],
            IntentType.WEB_SEARCH: [
                (r"web.*search", 0.9),
                (r"search.*web", 0.9),
                (r"internet.*search", 0.8),
                (r"online.*search", 0.8),
                (r"google.*search", 0.8),
                (r"search.*online", 0.8)
            ],
            IntentType.KNOWLEDGE_GRAPH: [
                (r"knowledge.*graph", 0.9),
                (r"graph.*query", 0.8),
                (r"neo4j.*query", 0.8),
                (r"graph.*search", 0.8),
                (r"knowledge.*base", 0.8)
            ],
            IntentType.MCP_TOOLS: [
                (r"mcp.*tools", 0.9),
                (r"available.*tools", 0.8),
                (r"list.*tools", 0.8),
                (r"show.*tools", 0.8),
                (r"what.*tools", 0.8)
            ],
            IntentType.CALL: [
                (r"call.*phone", 0.9),
                (r"make.*call", 0.9),
                (r"phone.*call", 0.8),
                (r"dial.*number", 0.8),
                (r"call.*number", 0.8)
            ]
        }
        
        # Check for email patterns first (highest priority)
        for pattern in intent_patterns[IntentType.EMAIL]:
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
            
        elif intent == IntentType.CONTENT_GENERATION:
            # Extract topic and style from content generation request
            import re
            
            # Extract the topic (what to write about)
            topic = message
            
            # Remove common content generation prefixes
            prefixes = [
                "write about", "generate content about", "create content about", "compose about",
                "write on", "generate text about", "create text about", "write essay about",
                "write article about", "generate article about", "write blog about", "create blog about",
                "write report about", "generate report about", "write story about", "create story about",
                "explain about", "discuss about", "describe about", "tell me about",
                "write paragraphs about", "generate paragraphs about", "create paragraphs about"
            ]
            
            for prefix in prefixes:
                if message_lower.startswith(prefix):
                    topic = message[len(prefix):].strip()
                    break
            
            # Detect style preferences
            style = "auto"  # Default to auto-detection
            length = "medium"  # Default to medium length
            
            # Check for style indicators
            if any(word in message_lower for word in ["professional", "business", "formal", "corporate"]):
                style = "professional"
            elif any(word in message_lower for word in ["creative", "story", "fiction", "imaginative", "artistic"]):
                style = "creative"
            elif any(word in message_lower for word in ["analytical", "data", "research", "analysis", "technical"]):
                style = "analytical"
            elif any(word in message_lower for word in ["conversational", "casual", "friendly", "personal"]):
                style = "conversational"
            
            # Check for length indicators
            if any(word in message_lower for word in ["short", "brief", "quick"]):
                length = "short"
            elif any(word in message_lower for word in ["long", "detailed", "extensive", "comprehensive"]):
                length = "long"
            elif any(word in message_lower for word in ["very long", "extensive", "comprehensive"]):
                length = "extensive"
            
            return {
                "topic": topic,
                "style": style,
                "length": length,
                "message": message
            }
        elif intent == IntentType.ACADEMIC_WRITING:
            # Extract topic and academic parameters from academic writing request
            import re
            
            # Extract the topic (what to write about)
            topic = message
            
            # Remove common academic writing prefixes
            prefixes = [
                "write academic essay about", "write research paper about", "write thesis about", "write dissertation about",
                "write academic paper about", "write scholarly paper about", "write argumentative essay about",
                "write analytical essay about", "write expository essay about", "write narrative essay about",
                "write compare contrast essay about", "write academic article about", "write academic report about",
                "write academic content about", "academic writing about", "scholarly writing about", "research writing about",
                "write academic essay on", "write research paper on", "write thesis on", "write dissertation on",
                "write academic paper on", "write scholarly paper on", "write argumentative essay on",
                "write analytical essay on", "write expository essay on", "write narrative essay on",
                "write compare contrast essay on", "write academic article on", "write academic report on",
                "write academic content on", "academic writing on", "scholarly writing on", "research writing on"
            ]
            
            for prefix in prefixes:
                if message_lower.startswith(prefix):
                    topic = message[len(prefix):].strip()
                    break
            
            # Detect content type
            content_type = "essay"  # Default
            if "research paper" in message_lower:
                content_type = "research_paper"
            elif "thesis" in message_lower:
                content_type = "thesis"
            elif "dissertation" in message_lower:
                content_type = "dissertation"
            elif "article" in message_lower:
                content_type = "article"
            elif "report" in message_lower:
                content_type = "report"
            
            # Detect style
            style = "auto"  # Default to auto-detection
            if "argumentative" in message_lower:
                style = "argumentative"
            elif "analytical" in message_lower:
                style = "analytical"
            elif "expository" in message_lower:
                style = "expository"
            elif "narrative" in message_lower:
                style = "narrative"
            elif "compare" in message_lower and "contrast" in message_lower:
                style = "compare_contrast"
            elif "research" in message_lower and "paper" in message_lower:
                style = "research"
            
            # Detect length
            length = "medium"  # Default
            if "short" in message_lower:
                length = "short"
            elif "long" in message_lower:
                length = "long"
            elif "extensive" in message_lower:
                length = "extensive"
            
            # Detect academic level
            academic_level = "undergraduate"  # Default
            if "high school" in message_lower or "high_school" in message_lower:
                academic_level = "high_school"
            elif "graduate" in message_lower:
                academic_level = "graduate"
            elif "doctoral" in message_lower or "doctorate" in message_lower:
                academic_level = "doctoral"
            
            return {
                "topic": topic,
                "content_type": content_type,
                "style": style,
                "length": length,
                "academic_level": academic_level,
                "message": message
            }
        elif intent == IntentType.RESEARCH_WRITING:
            # Extract topic and research parameters from research-enhanced writing request
            import re
            
            # Extract the topic (what to write about)
            topic = message
            
            # Remove common research writing prefixes
            prefixes = [
                "research essay about", "research paper about", "research thesis about", "research dissertation about",
                "research academic paper about", "research scholarly paper about", "research argumentative essay about",
                "research analytical essay about", "research expository essay about", "research narrative essay about",
                "research compare contrast essay about", "research academic article about", "research academic report about",
                "research academic content about", "research enhanced essay about", "research enhanced paper about",
                "research enhanced writing about", "write research enhanced essay about", "write research enhanced paper about",
                "write research enhanced content about", "research essay on", "research paper on", "research thesis on",
                "research dissertation on", "research academic paper on", "research scholarly paper on",
                "research argumentative essay on", "research analytical essay on", "research expository essay on",
                "research narrative essay on", "research compare contrast essay on", "research academic article on",
                "research academic report on", "research academic content on", "research enhanced essay on",
                "research enhanced paper on", "research enhanced writing on", "write research enhanced essay on",
                "write research enhanced paper on", "write research enhanced content on"
            ]
            
            for prefix in prefixes:
                if message_lower.startswith(prefix):
                    topic = message[len(prefix):].strip()
                    break
            
            # Detect content type
            content_type = "essay"  # Default
            if "research paper" in message_lower:
                content_type = "research_paper"
            elif "thesis" in message_lower:
                content_type = "thesis"
            elif "dissertation" in message_lower:
                content_type = "dissertation"
            elif "article" in message_lower:
                content_type = "article"
            elif "report" in message_lower:
                content_type = "report"
            
            # Detect style
            style = "auto"  # Default to auto-detection
            if "argumentative" in message_lower:
                style = "argumentative"
            elif "analytical" in message_lower:
                style = "analytical"
            elif "expository" in message_lower:
                style = "expository"
            elif "narrative" in message_lower:
                style = "narrative"
            elif "compare" in message_lower and "contrast" in message_lower:
                style = "compare_contrast"
            elif "research" in message_lower and "paper" in message_lower:
                style = "research"
            
            # Detect length
            length = "medium"  # Default
            if "short" in message_lower:
                length = "short"
            elif "long" in message_lower:
                length = "long"
            elif "extensive" in message_lower:
                length = "extensive"
            
            # Detect academic level
            academic_level = "undergraduate"  # Default
            if "high school" in message_lower or "high_school" in message_lower:
                academic_level = "high_school"
            elif "graduate" in message_lower:
                academic_level = "graduate"
            elif "doctoral" in message_lower or "doctorate" in message_lower:
                academic_level = "doctoral"
            
            return {
                "topic": topic,
                "content_type": content_type,
                "style": style,
                "length": length,
                "academic_level": academic_level,
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
            # Extract code writing specific data
            import re
            
            # Check for code writing patterns
            code_patterns = {
                'file_name': r'(?:from|in|read|generate|create|write|implement)\s+(\w+\.(?:md|txt|py|js|java|kt|ts|go|rs|cs|php|rb|swift))',
                'language': r'(?:in|using|with)\s+(python|javascript|java|kotlin|typescript|go|rust|csharp|php|ruby|swift|js|py|kt|ts|cs)',
                'code_type': r'(?:implement|create|write|generate)\s+(\w+(?:\s+\w+)*)',
                'for_loop': r'(?:implement|create|write|generate)\s+(?:a\s+)?(?:simple\s+)?(?:for\s+loop)',
                'function': r'(?:implement|create|write|generate)\s+(?:a\s+)?(?:function)',
                'class': r'(?:implement|create|write|generate)\s+(?:a\s+)?(?:class)'
            }
            
            extracted_data = {
                "message": message,
                "tool_request": message_lower,
                "is_code_request": any(re.search(pattern, message_lower) for pattern in [
                    r'code', r'loop', r'function', r'class', r'implement', r'create', r'write', r'generate'
                ])
            }
            
            # Extract specific data
            for key, pattern in code_patterns.items():
                match = re.search(pattern, message_lower)
                if match:
                    extracted_data[key] = match.group(1) if match.groups() else True
            
            # Special handling for "implement for loop"
            if re.search(r'implement\s+for\s+loop', message_lower):
                extracted_data['code_type'] = 'for loop'
                extracted_data['is_code_request'] = True
                
                # Try to extract language
                lang_match = re.search(r'(?:in|using|with)\s+(python|javascript|java|kotlin|typescript|go|rust|csharp|php|ruby|swift|js|py|kt|ts|cs)', message_lower)
                if lang_match:
                    extracted_data['language'] = lang_match.group(1)
                else:
                    # Default to Kotlin for simple requests
                    extracted_data['language'] = 'kotlin'
            
            return extracted_data
            
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
            elif intent_result.intent == IntentType.CONTENT_GENERATION:
                result = await self._handle_content_generation(intent_result.extracted_data, session_id, user_id)
            elif intent_result.intent == IntentType.ACADEMIC_WRITING:
                result = await self._handle_academic_writing(intent_result.extracted_data, session_id, user_id)
            elif intent_result.intent == IntentType.RESEARCH_WRITING:
                result = await self._handle_research_writing(intent_result.extracted_data, session_id, user_id)


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
        """Handle intelligent email composition using MCP tools."""
        try:
            from .mcp_tools import sendmail_simple_tool, SendmailSimpleInput
            from .email_composer import email_composer

            to_email = data.get("to_email")
            original_message = data.get("message", "")

            if not to_email:
                return {
                    "action": "email_error",
                    "error": "No email address provided",
                    "note": "Please provide a valid email address"
                }

            # Use intelligent email composer to generate professional email
            composed_email = email_composer.compose_email(
                user_message=original_message,
                to_email=to_email,
                context={"session_id": session_id, "user_id": user_id}
            )

            subject = composed_email.get("subject", "Message from Smart Agent")
            body = composed_email.get("body", "This is an automated message from the Smart Agent System.")
            intent = composed_email.get("intent", "general")
            tone = composed_email.get("tone", "professional")

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
                    "body": body,
                    "intent": intent,
                    "tone": tone,
                    "result": result.get("result", "Email sent successfully"),
                    "note": f"Intelligent email composed and sent using {tone} tone"
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

    async def _handle_content_generation(self, data: Dict[str, Any], session_id: str, user_id: str) -> Dict[str, Any]:
        """Handle ChatGPT-like content generation."""
        try:
            from .content_generator import content_generator

            topic = data.get("topic", "")
            style = data.get("style", "auto")
            length = data.get("length", "medium")

            if not topic:
                return {
                    "action": "content_error",
                    "error": "No topic provided",
                    "note": "Please provide a topic to generate content about"
                }

            # Generate content using the content generator
            result = content_generator.generate_content(
                topic=topic,
                style=style,
                length=length,
                context={"session_id": session_id, "user_id": user_id}
            )

            if "error" in result:
                return {
                    "action": "content_error",
                    "error": result["error"],
                    "note": "Content generation failed"
                }

            return {
                "action": "content_generated",
                "topic": result["topic"],
                "style": result["style"],
                "length": result["length"],
                "content": result["content"],
                "paragraph_count": result["paragraph_count"],
                "word_count": result["word_count"],
                "note": f"Generated {result['paragraph_count']} paragraphs ({result['word_count']} words) in {result['style']} style"
            }

        except Exception as e:
            logger.error(f"Content generation failed: {e}")
            return {
                "action": "content_error",
                "error": str(e),
                "note": "Content generation failed"
            }

    async def _handle_academic_writing(self, data: Dict[str, Any], session_id: str, user_id: str) -> Dict[str, Any]:
        """Handle academic writing requests."""
        try:
            from .academic_writer import academic_writer

            topic = data.get("topic", "")
            content_type = data.get("content_type", "essay")
            style = data.get("style", "auto")
            length = data.get("length", "medium")
            academic_level = data.get("academic_level", "undergraduate")

            if not topic:
                return {
                    "action": "academic_error",
                    "error": "No topic provided",
                    "note": "Please provide a topic to write about"
                }

            # Generate academic content using the academic writer
            result = academic_writer.write_academic_content(
                topic=topic,
                content_type=content_type,
                style=style,
                length=length,
                academic_level=academic_level,
                context={"session_id": session_id, "user_id": user_id}
            )

            if "error" in result:
                return {
                    "action": "academic_error",
                    "error": result["error"],
                    "note": "Academic writing failed"
                }

            return {
                "action": "academic_generated",
                "topic": result["topic"],
                "content_type": result["content_type"],
                "style": result["style"],
                "length": result["length"],
                "academic_level": result["academic_level"],
                "content": result["content"],
                "word_count": result["word_count"],
                "estimated_pages": result["estimated_pages"],
                "note": f"Generated {result['content_type']} ({result['word_count']} words, ~{result['estimated_pages']} pages) in {result['style']} style for {result['academic_level']} level"
            }

        except Exception as e:
            logger.error(f"Academic writing failed: {e}")
            return {
                "action": "academic_error",
                "error": str(e),
                "note": "Academic writing failed"
            }

    async def _handle_research_writing(self, data: Dict[str, Any], session_id: str, user_id: str) -> Dict[str, Any]:
        """Handle research-enhanced writing requests."""
        try:
            from .research_enhanced_writer import research_enhanced_writer

            topic = data.get("topic", "")
            content_type = data.get("content_type", "essay")
            style = data.get("style", "auto")
            length = data.get("length", "medium")
            academic_level = data.get("academic_level", "undergraduate")

            if not topic:
                return {
                    "action": "research_error",
                    "error": "No topic provided",
                    "note": "Please provide a topic to research and write about"
                }

            # Generate research-enhanced content using the research-enhanced writer
            result = await research_enhanced_writer.write_research_enhanced_essay(
                topic=topic,
                content_type=content_type,
                style=style,
                length=length,
                academic_level=academic_level
            )

            if "error" in result:
                return {
                    "action": "research_error",
                    "error": result["error"],
                    "note": "Research-enhanced writing failed"
                }

            return {
                "action": "research_generated",
                "topic": result["topic"],
                "content_type": result["content_type"],
                "style": result["style"],
                "length": result["length"],
                "academic_level": result["academic_level"],
                "content": result["content"],
                "word_count": result["word_count"],
                "estimated_pages": result["estimated_pages"],
                "sources_count": result.get("sources_count", 0),
                "note": f"Generated research-enhanced {result['content_type']} ({result['word_count']} words, ~{result['estimated_pages']} pages) with {result.get('sources_count', 0)} sources in {result['style']} style for {result['academic_level']} level"
            }

        except Exception as e:
            logger.error(f"Research-enhanced writing failed: {e}")
            return {
                "action": "research_error",
                "error": str(e),
                "note": "Research-enhanced writing failed"
            }


    

    
    async def _web_search(self, data: Dict[str, Any], session_id: str, user_id: str) -> Dict[str, Any]:
        """Perform web search."""
        from .tools import web_search_tool, WebSearchInput
        
        query = data.get("query", "")
        search_input = WebSearchInput(query=query, max_results=5)
        results = await web_search_tool(search_input)
        
        formatted_results = []
        for result in results:
            formatted_results.append({
                "title": result.get("title", ""),
                "url": result.get("url", ""),
                "snippet": result.get("content", ""),
                "source": result.get("source", "web_search")
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
            
            # Search desktop files - more flexible patterns
            elif ("search" in message or "find" in message):
                import re
                # Try different patterns - more flexible
                search_patterns = [
                    r'search.*desktop.*file.*for\s+(.+)',
                    r'find.*desktop.*file\s+(.+)',
                    r'search.*file\s+(.+)',
                    r'find.*file\s+(.+)',
                    r'search.*for\s+(.+)',
                    r'find\s+(.+)',
                    r'search\s+(.+)',
                    r'search.*employee.*file',
                    r'search.*for.*employee.*file'
                ]
                
                filename = None
                for pattern in search_patterns:
                    match = re.search(pattern, message)
                    if match:
                        filename = match.group(1).strip()
                        break
                
                # Handle special cases
                if not filename:
                    if "employee" in message and "file" in message:
                        filename = "employees.csv"  # Default to employees.csv for employee file searches
                    elif "find" in message and len(message.split()) >= 2:
                        # Extract the word after "find"
                        parts = message.split()
                        filename = parts[1].strip()
                    elif "search" in message and len(message.split()) >= 2:
                        # Extract the word after "search"
                        parts = message.split()
                        filename = parts[1].strip()
                
                if filename:
                    # Use generic MCP tool call for search_desktop_files
                    input_data = MCPToolInput(tool_name="search_desktop_files", parameters={"filename": filename})
                    result = await generic_mcp_tool(input_data)
                    return {
                        "action": "mcp_search_desktop_files",
                        "search_term": filename,
                        "result": result,
                        "note": f"Used MCP server to search for '{filename}' on desktop"
                    }
            

            
            # Read desktop file
            elif "read" in message and "desktop" in message and "file" in message:
                import re
                file_match = re.search(r'read.*desktop.*file\s+(.+)', message)
                if file_match:
                    filename = file_match.group(1).strip()
                    # Use generic MCP tool call for read_desktop_file
                    input_data = MCPToolInput(tool_name="read_desktop_file", parameters={"filename": filename})
                    result = await generic_mcp_tool(input_data)
                    return {
                        "action": "mcp_read_desktop_file",
                        "filename": filename,
                        "result": result,
                        "note": f"Used MCP server to read '{filename}' from desktop"
                    }
            
            # Ingest desktop file
            elif ("ingest" in message or "add" in message or "store" in message) and ("desktop" in message or "file" in message or "vector" in message):
                import re
                # Try different patterns for ingest
                ingest_patterns = [
                    r'ingest.*desktop.*file\s+(.+)',
                    r'add.*file.*to.*vector.*db\s+(.+)',
                    r'store.*file.*in.*vector\s+(.+)',
                    r'ingest.*file\s+(.+)',
                    r'add.*to.*vector.*db\s+(.+)',
                    r'ingest\s+(.+)',
                    r'add\s+(.+)'
                ]
                
                filename = None
                for pattern in ingest_patterns:
                    match = re.search(pattern, message)
                    if match:
                        filename = match.group(1).strip()
                        break
                
                if filename:
                    # Use generic MCP tool call for ingest_desktop_file
                    input_data = MCPToolInput(tool_name="ingest_desktop_file", parameters={"filename": filename})
                    result = await generic_mcp_tool(input_data)
                    return {
                        "action": "mcp_ingest_desktop_file",
                        "filename": filename,
                        "result": result,
                        "note": f"Used MCP server to ingest '{filename}' from desktop into vector database"
                    }
            
            # Batch ingest desktop files
            elif "batch" in message and "ingest" in message and "desktop" in message:
                # Use generic MCP tool call for batch_ingest_desktop
                input_data = MCPToolInput(tool_name="batch_ingest_desktop", parameters={})
                result = await generic_mcp_tool(input_data)
                return {
                    "action": "mcp_batch_ingest_desktop",
                    "result": result,
                    "note": "Used MCP server to batch ingest all supported files from desktop"
                }
            
            # Code writing patterns
            elif any(phrase in message for phrase in ["generate code", "write code", "implement code", "code generation", "read and generate"]) or data.get("is_code_request", False):
                import re
                import os
                
                # Extract file name and language
                file_match = re.search(r'from\s+(\w+\.\w+)', message)
                language_match = re.search(r'(python|javascript|java|kotlin|typescript|go|rust|csharp|php|ruby|swift|js|py|kt|ts|cs)', message)
                
                file_name = file_match.group(1) if file_match else ""
                language = language_match.group(1) if language_match else data.get("language", "kotlin")
                
                # Handle simple code requests like "implement for loop"
                if not file_name and data.get("is_code_request", False):
                    # Create a simple instruction file for the request
                    code_type = data.get("code_type", "simple code")
                    language = data.get("language", "kotlin")
                    
                    # Create a simple instruction content
                    instruction_content = f"""Title: {code_type.title()}

Requirements:
- Create a simple {language} program
- Demonstrate {code_type}
- Include basic examples and explanations

Features:
- {code_type}
- Basic implementation
- Educational examples

Constraints:
- Keep it simple and educational
- Include comments explaining the code
- Make it runnable as a standalone program
"""
                    
                    # Write the instruction to a temporary file
                    import tempfile
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
                        f.write(instruction_content)
                        file_name = f.name
                
                # Determine output file name
                if file_name:
                    base_name = os.path.splitext(file_name)[0]
                    if language == "python":
                        output_file = f"{base_name}_implementation.py"
                    elif language in ["javascript", "js"]:
                        output_file = f"{base_name}_implementation.js"
                    elif language == "java":
                        output_file = f"{base_name}_implementation.java"
                    else:
                        output_file = f"{base_name}_implementation.{language}"
                else:
                    output_file = f"generated_code.{language}"
                
                # Call the code writing agent
                input_data = MCPToolInput(
                    tool_name="read_and_generate_code", 
                    parameters={
                        "file_name": file_name,
                        "language": language,
                        "output_file": output_file,
                        "include_tests": True,
                        "include_docs": True
                    }
                )
                result = await generic_mcp_tool(input_data)
                
                return {
                    "action": "mcp_code_generation",
                    "source_file": file_name,
                    "language": language,
                    "output_file": output_file,
                    "result": result,
                    "note": f"Generated {language} code from instructions in {file_name}",
                    "project_folder": result.get("project_folder"),
                    "project_created": result.get("project_folder") is not None
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
            
            # Instruction file patterns
            elif any(phrase in message for phrase in ["create instruction file", "write instruction file", "generate instruction file", "make instruction file"]):
                import re
                
                # Extract instruction details
                title_match = re.search(r'(?:create|write|generate|make).*instruction.*file.*for\s+(.+)', message)
                title = title_match.group(1).strip() if title_match else "Instruction File"
                
                # Extract action type
                action_type = "code_generation"  # Default
                if "code" in message or "program" in message:
                    action_type = "code_generation"
                elif "file" in message and ("operation" in message or "search" in message):
                    action_type = "file_operation"
                elif "web" in message and "search" in message:
                    action_type = "web_search"
                elif "email" in message:
                    action_type = "email"
                elif "phone" in message or "call" in message:
                    action_type = "phone_call"
                
                # Extract language
                language_match = re.search(r'(python|javascript|java|kotlin|typescript|go|rust|csharp|php|ruby|swift|js|py|kt|ts|cs)', message)
                language = language_match.group(1) if language_match else "python"
                
                # Create instruction file
                input_data = MCPToolInput(
                    tool_name="create_instruction_file",
                    parameters={
                        "file_name": f"{title.lower().replace(' ', '_')}_instruction.md",
                        "title": title,
                        "action_type": action_type,
                        "description": f"Instruction for {title}",
                        "requirements": [f"Complete {title}"],
                        "features": [f"{title} functionality"],
                        "constraints": ["Must be working and complete"],
                        "language": language,
                        "priority": "high",
                        "tags": [action_type, language]
                    }
                )
                result = await generic_mcp_tool(input_data)
                
                return {
                    "action": "mcp_create_instruction_file",
                    "title": title,
                    "action_type": action_type,
                    "language": language,
                    "result": result,
                    "note": f"Created instruction file for {action_type} action"
                }
            
            # Read and execute instruction file
            elif any(phrase in message for phrase in ["read instruction file", "execute instruction file", "run instruction file", "process instruction file"]):
                import re
                
                # Extract file name
                file_match = re.search(r'(?:read|execute|run|process).*instruction.*file\s+(.+)', message)
                file_name = file_match.group(1).strip() if file_match else ""
                
                if not file_name:
                    # Try to find any .md file mentioned
                    md_match = re.search(r'(\w+\.md)', message)
                    file_name = md_match.group(1) if md_match else ""
                
                if file_name:
                    # Read and execute instruction file
                    input_data = MCPToolInput(
                        tool_name="read_and_execute_instruction",
                        parameters={
                            "file_name": file_name,
                            "auto_execute": True
                        }
                    )
                    result = await generic_mcp_tool(input_data)
                    
                    return {
                        "action": "mcp_read_and_execute_instruction",
                        "file_name": file_name,
                        "result": result,
                        "note": f"Read and executed instruction file '{file_name}'"
                    }
                else:
                    return {
                        "action": "mcp_instruction_error",
                        "error": "No instruction file specified",
                        "note": "Please specify which instruction file to read and execute"
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
        elif intent == IntentType.CONTENT_GENERATION:
            if result.get('action') == 'content_generated':
                return f"📝 Generated {result.get('paragraph_count', 0)} paragraphs ({result.get('word_count', 0)} words) about '{result.get('topic', 'topic')}' in {result.get('style', 'informative')} style"
            elif result.get('action') == 'content_error':
                return f"❌ Content generation error: {result.get('error', 'Unknown error')}"
            else:
                return f"📝 Content generation completed for '{result.get('topic', 'topic')}'"
        elif intent == IntentType.ACADEMIC_WRITING:
            if result.get('action') == 'academic_generated':
                return f"📝 Generated {result.get('content_type', 'essay')} ({result.get('word_count', 0)} words, ~{result.get('estimated_pages', 0)} pages) about '{result.get('topic', 'topic')}' in {result.get('style', 'informative')} style for {result.get('academic_level', 'undergraduate')} level"
            elif result.get('action') == 'academic_error':
                return f"❌ Academic writing error: {result.get('error', 'Unknown error')}"
            else:
                return f"📝 Academic writing completed for '{result.get('topic', 'topic')}'"
        elif intent == IntentType.RESEARCH_WRITING:
            if result.get('action') == 'research_generated':
                return f"📝 Generated {result.get('content_type', 'essay')} ({result.get('word_count', 0)} words, ~{result.get('estimated_pages', 0)} pages) about '{result.get('topic', 'topic')}' in {result.get('style', 'informative')} style for {result.get('academic_level', 'undergraduate')} level"
            elif result.get('action') == 'research_error':
                return f"❌ Research writing error: {result.get('error', 'Unknown error')}"
            else:
                return f"📝 Research writing completed for '{result.get('topic', 'topic')}'"



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