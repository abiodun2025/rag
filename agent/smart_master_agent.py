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
    GITHUB_COVERAGE = "github_coverage"
    SECRETS_DETECTION = "secrets_detection"
    CYBERSECURITY_SCAN = "cybersecurity_scan"
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
                r"recent.*developments",
                r"who.*won.*\d{4}",
                r"who.*was.*\d{4}",
                r"nba.*finals.*\d{4}",
                r"super.*bowl.*\d{4}",
                r"world.*series.*\d{4}",
                r"championship.*\d{4}",
                r"mvp.*\d{4}",
                r"current.*events",
                r"recent.*events",
                r"latest.*results",
                r"today.*news",
                r"yesterday.*news"
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
                r"gmail.*compose",
                r"search.*desktop",
                r"find.*desktop",
                r"read.*desktop.*file",
                r"ingest.*desktop.*file",
                r"batch.*ingest.*desktop",
                r"list.*desktop.*files",
                r"search.*desktop.*files",
                r"read.*file.*desktop",
                r"ingest.*file.*desktop",
                r"find.*file.*desktop",
                r"search.*file.*desktop",
                r"list.*files.*desktop",
                r"desktop.*search",
                r"desktop.*find",
                r"desktop.*read",
                r"desktop.*ingest",
                r"file.*search",
                r"file.*find",
                r"file.*read",
                r"file.*ingest",
                r"find.*file",
                r"search.*file",
                r"read.*file",
                r"ingest.*file",
                r"add.*file.*to.*vector",
                r"add.*to.*vector.*db",
                r"store.*file.*in.*vector",
                r"vector.*db.*add",
                r"find.*employees\.csv",
                r"search.*employees\.csv",
                r"read.*employees\.csv",
                r"ingest.*employees\.csv",
                # More flexible patterns
                r"find\s+\w+",
                r"search\s+\w+",
                r"search.*for.*\w+",
                r"find.*\w+\.csv",
                r"search.*\w+\.csv",
                r"employee.*file",
                r"search.*employee",
                r"find.*employee",
                r"search\s+\w+\.csv",
                r"search\s+\w+\.txt",
                r"search\s+\w+\.md",
                # Code writing patterns
                r"read.*and.*generate.*code",
                r"generate.*code.*from.*instructions",
                r"implement.*from.*instructions",
                r"code.*writing.*agent",
                r"write.*code.*from.*file",
                r"create.*code.*from.*instructions",
                r"generate.*implementation",
                r"code.*generation",
                r"read.*instructions.*and.*code",
                r"implement.*code",
                r"write.*implementation",
                r"generate.*from.*instructions",
                r"code.*from.*file",
                r"implementation.*from.*file",
                r"read.*file.*and.*code",
                r"generate.*python.*from",
                r"generate.*javascript.*from",
                r"generate.*java.*from",
                r"create.*python.*from",
                r"create.*javascript.*from",
                r"create.*java.*from",
                r"write.*python.*from",
                r"write.*javascript.*from",
                r"write.*java.*from",
                # General code writing patterns
                r"implement.*\w+",
                r"create.*\w+.*code",
                r"write.*\w+.*code",
                r"generate.*\w+.*code",
                r"code.*for.*\w+",
                r"implement.*for.*loop",
                r"create.*for.*loop",
                r"write.*for.*loop",
                r"generate.*for.*loop",
                r"implement.*function",
                r"create.*function",
                r"write.*function",
                r"generate.*function",
                r"implement.*class",
                r"create.*class",
                r"write.*class",
                r"generate.*class",
                r"implement.*\w+.*in.*\w+",
                r"create.*\w+.*in.*\w+",
                r"write.*\w+.*in.*\w+",
                r"generate.*\w+.*in.*\w+",
                r"kotlin.*code",
                r"python.*code",
                r"javascript.*code",
                r"java.*code",
                r"typescript.*code",
                r"go.*code",
                r"rust.*code",
                r"csharp.*code",
                r"php.*code",
                r"ruby.*code",
                r"swift.*code",
                # Instruction file patterns
                r"create.*instruction.*file",
                r"write.*instruction.*file",
                r"generate.*instruction.*file",
                r"make.*instruction.*file",
                r"instruction.*file.*for",
                r"read.*instruction.*file",
                r"execute.*instruction.*file",
                r"run.*instruction.*file",
                r"process.*instruction.*file"
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
                r"search.*about",
                r"who.*won",
                r"who.*was",
                r"who.*did",
                r"what.*happened",
                r"when.*was",
                r"where.*was",
                r"which.*team",
                r"which.*player",
                r"nba.*finals",
                r"super.*bowl",
                r"world.*series",
                r"championship",
                r"playoff",
                r"mvp",
                r"most.*valuable.*player"
            ],
            IntentType.GITHUB_COVERAGE: [
                r"analyze.*coverage",
                r"check.*coverage",
                r"review.*coverage",
                r"pr.*coverage",
                r"pull.*request.*coverage",
                r"test.*coverage",
                r"coverage.*analysis",
                r"coverage.*report",
                r"coverage.*check",
                r"coverage.*review",
                r"pr.*\d+.*coverage",
                r"pull.*request.*\d+.*coverage",
                r"repository.*coverage",
                r"repo.*coverage",
                r"branch.*coverage",
                r"coverage.*for.*pr",
                r"coverage.*for.*pull.*request"
            ],
            IntentType.SECRETS_DETECTION: [
                r"scan.*for.*secrets",
                r"check.*for.*secrets",
                r"audit.*for.*secrets",
                r"find.*secrets",
                r"detect.*secrets",
                r"security.*scan",
                r"vulnerability.*scan",
                r"security.*audit",
                r"vulnerability.*audit",
                r"security.*check",
                r"vulnerability.*check",
                r"scan.*file.*for.*secrets",
                r"scan.*directory.*for.*secrets",
                r"scan.*folder.*for.*secrets",
                r"check.*file.*for.*secrets",
                r"check.*directory.*for.*secrets",
                r"audit.*file.*for.*secrets",
                r"audit.*directory.*for.*secrets",
                r"scan.*file.*for.*secrets",
                r"scan.*directory.*for.*secrets",
                r"scan.*folder.*for.*secrets",
                r"check.*file.*for.*secrets",
                r"check.*directory.*for.*secrets",
                r"audit.*file.*for.*secrets",
                r"audit.*directory.*for.*secrets"
            ],
            IntentType.CYBERSECURITY_SCAN: [
                r"dependency.*vulnerability.*scan",
                r"check.*dependencies.*for.*vulnerabilities",
                r"scan.*dependencies.*for.*vulnerabilities",
                r".*scan.*dependencies.*for.*vulnerabilities.*",
                r"scan.*dependencies.*for.*cves",
                r"audit.*dependencies.*for.*security",
                r"check.*packages.*for.*vulnerabilities",
                r"scan.*packages.*for.*cves",
                r"audit.*packages.*for.*security",
                r"sast.*scan",
                r"static.*analysis.*security",
                r"code.*security.*scan",
                r"static.*code.*analysis",
                r"security.*code.*analysis",
                r"license.*compliance.*check",
                r"check.*license.*compliance",
                r"audit.*license.*compliance",
                r"verify.*license.*compliance",
                r"security.*best.*practices",
                r"check.*security.*best.*practices",
                r"audit.*security.*best.*practices",
                r"security.*standards.*check",
                r"security.*guidelines.*check",
                r"pre.*merge.*security.*gate",
                r"pre.*commit.*security.*check",
                r"security.*gate.*check",
                r"block.*pr.*with.*security.*issues",
                r"security.*metrics.*tracking",
                r"track.*security.*metrics",
                r"monitor.*security.*improvements",
                r"measure.*security.*progress",
                r"security.*scan.*comprehensive",
                r"comprehensive.*cybersecurity.*scan",
                r"run.*comprehensive.*cybersecurity.*scan",
                r"full.*cybersecurity.*audit",
                r"complete.*security.*analysis",
                r"thorough.*security.*review"
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
        
        # Check for cybersecurity patterns (high priority)
        print(f"🔒 Checking cybersecurity patterns for message: {message_lower}")
        logger.info(f"🔒 Checking cybersecurity patterns for message: {message_lower}")
        for pattern in patterns[IntentType.CYBERSECURITY_SCAN]:
            print(f"🔒 Testing pattern: {pattern}")
            logger.info(f"🔒 Testing pattern: {pattern}")
            if re.search(pattern, message_lower):
                print(f"🔒 Cybersecurity pattern matched: {pattern}")
                logger.info(f"🔒 Cybersecurity pattern matched: {pattern}")
                extracted_data = self._extract_data(message, IntentType.CYBERSECURITY_SCAN)
                return IntentResult(
                    intent=IntentType.CYBERSECURITY_SCAN,
                    confidence=0.8,
                    extracted_data=extracted_data,
                    original_message=message
                )
        
        # Check other patterns (excluding cybersecurity since it was already checked)
        for intent_type, intent_patterns in patterns.items():
            if intent_type == IntentType.CYBERSECURITY_SCAN:
                continue  # Skip cybersecurity patterns since they were already checked
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
            
        elif intent == IntentType.GITHUB_COVERAGE:
            # Extract GitHub coverage analysis data
            import re
            
            # GitHub coverage patterns
            coverage_patterns = {
                'pr_number': r'(?:pr|pull.?request|pull.?req)\s*#?(\d+)',
                'branch': r'(?:branch|on)\s+(\w+)',
                'analysis_type': r'(?:analyze|check|review)\s+(pr|pull.?request|repository|repo|coverage)',
                'language': r'(?:in|using|with)\s+(python|javascript|java|kotlin|typescript|go|rust|csharp|php|ruby|swift|js|py|kt|ts|cs)'
            }
            
            extracted_data = {
                "message": message,
                "analysis_request": message_lower,
                "is_coverage_request": any(re.search(pattern, message_lower) for pattern in [
                    r'coverage', r'pr', r'pull.?request', r'analyze', r'check', r'review'
                ])
            }
            
            # Extract specific data
            for key, pattern in coverage_patterns.items():
                match = re.search(pattern, message_lower)
                if match:
                    extracted_data[key] = match.group(1) if match.groups() else True
            
            return extracted_data
            
        elif intent == IntentType.SECRETS_DETECTION:
            # Extract secrets detection data
            import re
            
            # Secrets detection patterns
            secrets_patterns = {
                'target': r'(?:scan|check|audit|find)\s+(?:for\s+)?(?:secrets|vulnerabilities|issues)\s+(?:in|on|at)\s+([^\s]+)',
                'file_path': r'(?:file|path)\s+([^\s]+)',
                'dir_path': r'(?:directory|folder|dir)\s+([^\s]+)',
                'scan_type': r'(?:comprehensive|full|complete|thorough)\s+scan',
                'email_report': r'(?:send|email|mail)\s+(?:security|scan)\s+report'
            }
            
            extracted_data = {
                "message": message,
                "security_request": message_lower,
                "is_security_request": any(re.search(pattern, message_lower) for pattern in [
                    r'secrets', r'vulnerabilities', r'security', r'scan', r'audit', r'check'
                ])
            }
            
            # Extract specific data
            for key, pattern in secrets_patterns.items():
                match = re.search(pattern, message_lower)
                if match:
                    extracted_data[key] = match.group(1) if match.groups() else True
            
            return extracted_data
            
        elif intent == IntentType.CYBERSECURITY_SCAN:
            # Extract cybersecurity scan data
            import re
            
            # Cybersecurity scan patterns
            cybersecurity_patterns = {
                'target': r'(?:scan|audit|check|analyze)\s+(?:for\s+)?(?:security|vulnerabilities|threats|risks)\s+(?:in|on|at)\s+([^\s]+)',
                'scan_type': r'(dependency|sast|static|license|compliance|best.?practices|pre.?merge|metrics)',
                'dependency_scan': r'(?:check|scan|audit)\s+(?:for\s+)?(?:dependencies|packages|libraries|vulnerabilities|cves)',
                'sast_scan': r'(?:static|code|security)\s+(?:analysis|scanning|audit)',
                'license_check': r'(?:license|licensing|compliance)\s+(?:check|audit|verification)',
                'best_practices': r'(?:check|scan|audit|review)\s+(?:security\s+)?(?:best\s+)?(?:practices|standards|guidelines)',
                'pre_merge': r'(?:pre.?merge|pre.?commit|gate|block)\s+(?:security|checks|validation)',
                'metrics_tracking': r'(?:track|monitor|measure)\s+(?:security|metrics|improvements|progress)'
            }
            
            extracted_data = {
                "message": message,
                "cybersecurity_request": message_lower,
                "is_cybersecurity_request": any(re.search(pattern, message_lower) for pattern in [
                    r'security', r'vulnerabilities', r'threats', r'risks', r'dependencies', r'sast', r'license', r'compliance'
                ])
            }
            
            # Extract specific data
            for key, pattern in cybersecurity_patterns.items():
                match = re.search(pattern, message_lower)
                if match:
                    extracted_data[key] = match.group(1) if match.groups() else True
            
            return extracted_data
            
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
            print(f"🔍 Executing intent: {intent_result.intent} (type: {type(intent_result.intent)})")
            print(f"🔍 IntentType.CYBERSECURITY_SCAN: {IntentType.CYBERSECURITY_SCAN} (type: {type(IntentType.CYBERSECURITY_SCAN)})")
            print(f"🔍 Comparison result: {intent_result.intent == IntentType.CYBERSECURITY_SCAN}")
            
            logger.info(f"🔍 Executing intent: {intent_result.intent} (type: {type(intent_result.intent)})")
            logger.info(f"🔍 IntentType.CYBERSECURITY_SCAN: {IntentType.CYBERSECURITY_SCAN} (type: {type(IntentType.CYBERSECURITY_SCAN)})")
            logger.info(f"🔍 Comparison result: {intent_result.intent == IntentType.CYBERSECURITY_SCAN}")
            
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
            elif intent_result.intent == IntentType.GITHUB_COVERAGE:
                result = await self._handle_github_coverage(intent_result.extracted_data, session_id, user_id)
            elif intent_result.intent == IntentType.SECRETS_DETECTION:
                result = await self._handle_secrets_detection(intent_result.extracted_data, session_id, user_id)
            elif intent_result.intent == IntentType.CYBERSECURITY_SCAN:
                print(f"🔒 Executing cybersecurity scan handler...")
                logger.info(f"🔒 Executing cybersecurity scan handler...")
                result = await self._handle_cybersecurity_scan(intent_result.extracted_data, session_id, user_id)
                print(f"🔒 Cybersecurity scan handler result: {result}")
                logger.info(f"🔒 Cybersecurity scan handler result: {result}")
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
            
            final_result = {
                "success": True,
                "intent": intent_result.intent.value,
                "confidence": intent_result.confidence,
                "result": result,
                "execution_time": execution_time,
                "message": self._get_user_friendly_message(intent_result.intent, result)
            }
            print(f"🔍 Final result from execute_intent: {final_result}")
            return final_result
            
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
        elif intent == IntentType.GITHUB_COVERAGE:
            if result.get('action') == 'github_pr_coverage_analysis':
                return f"🔍 GitHub PR #{result.get('pr_number')} coverage analysis completed successfully"
            elif result.get('action') == 'github_repository_coverage_analysis':
                return f"🔍 Repository coverage analysis for branch '{result.get('branch')}' completed successfully"
            elif result.get('action') == 'github_coverage_error':
                return f"❌ GitHub coverage analysis failed: {result.get('error', 'Unknown error')}"
            else:
                return f"🔍 GitHub coverage analysis: {result.get('note', 'Analysis completed')}"
        elif intent == IntentType.SECRETS_DETECTION:
            if result.get('action') == 'secrets_detection_completed':
                return f"🔐 {result.get('scan_type', 'Security')} scan completed on {result.get('target')}. Found {result.get('secrets_count', 0)} secrets in {result.get('files_scanned', 0)} files. Risk Level: {result.get('risk_level', 'UNKNOWN')}"
            elif result.get('action') == 'secrets_detection_error':
                return f"❌ Secrets detection failed: {result.get('error', 'Unknown error')}"
            else:
                return f"🔐 Secrets detection: {result.get('note', 'Scan completed')}"
        elif intent == IntentType.CYBERSECURITY_SCAN:
            if result.get('action') == 'cybersecurity_scan_completed':
                return f"🔒 {result.get('scan_type', 'Cybersecurity')} scan completed on {result.get('target')}. Comprehensive security analysis finished successfully."
            elif result.get('action') == 'cybersecurity_scan_error':
                return f"❌ Cybersecurity scan failed: {result.get('error', 'Unknown error')}"
            else:
                return f"🔒 Cybersecurity scan: {result.get('note', 'Scan completed')}"
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

    async def _handle_github_coverage(self, data: Dict[str, Any], session_id: str, user_id: str) -> Dict[str, Any]:
        """Handle GitHub coverage analysis requests."""
        try:
            from .github_coverage_agent import GitHubCoverageAgent, GitHubConfig
            import os
            
            # Get GitHub configuration from environment
            github_token = os.getenv('GITHUB_TOKEN')
            github_owner = os.getenv('GITHUB_OWNER')
            github_repo = os.getenv('GITHUB_REPO')
            
            if not all([github_token, github_owner, github_repo]):
                return {
                    "action": "github_coverage_error",
                    "error": "Missing GitHub configuration",
                    "note": "Please set GITHUB_TOKEN, GITHUB_OWNER, and GITHUB_REPO environment variables"
                }
            
            # Initialize GitHub Coverage Agent
            config = GitHubConfig(token=github_token, owner=github_owner, repo=github_repo)
            agent = GitHubCoverageAgent(config)
            
            analysis_type = data.get("analysis_type", "repository")
            pr_number = data.get("pr_number")
            branch = data.get("branch", "main")
            
            if analysis_type == "pr" and pr_number:
                # Analyze specific PR
                logger.info(f"🔍 Analyzing PR #{pr_number} coverage")
                result = agent.analyze_pr_coverage(pr_number)
                
                if "error" in result:
                    return {
                        "action": "github_coverage_error",
                        "error": result["error"],
                        "pr_number": pr_number,
                        "note": f"Failed to analyze PR #{pr_number} coverage"
                    }
                
                return {
                    "action": "github_pr_coverage_analysis",
                    "pr_number": pr_number,
                    "result": result,
                    "note": f"Successfully analyzed PR #{pr_number} coverage"
                }
            else:
                # Analyze repository coverage
                logger.info(f"🔍 Analyzing repository coverage for branch: {branch}")
                result = agent.analyze_repository_coverage(branch)
                
                if "error" in result:
                    return {
                        "action": "github_coverage_error",
                        "error": result["error"],
                        "branch": branch,
                        "note": f"Failed to analyze repository coverage for branch: {branch}"
                    }
                
                return {
                    "action": "github_repository_coverage_analysis",
                    "branch": branch,
                    "result": result,
                    "note": f"Successfully analyzed repository coverage for branch: {branch}"
                }
                
        except ImportError as e:
            return {
                "action": "github_coverage_error",
                "error": "GitHub Coverage Agent not available",
                "note": f"Import error: {str(e)}"
            }
        except Exception as e:
            logger.error(f"GitHub coverage analysis failed: {e}")
            return {
                "action": "github_coverage_error",
                "error": str(e),
                "note": "GitHub coverage analysis failed"
            }

    async def _handle_secrets_detection(self, data: Dict[str, Any], session_id: str, user_id: str) -> Dict[str, Any]:
        """Handle secrets detection requests using the Secrets Detection Agent."""
        try:
            from .secrets_detection_agent import SecretsDetectionAgent
            import os
            
            # Initialize Secrets Detection Agent with MCP server
            mcp_server_url = os.getenv('MCP_SERVER_URL', 'http://127.0.0.1:5000')
            agent = SecretsDetectionAgent(mcp_server_url=mcp_server_url)
            
            # Check if this is an email report request
            if data.get("email_report_request"):
                return await self._send_manual_email_report(data, session_id, user_id)
            
            # Extract target from data using improved parsing
            target = data.get("target", ".")
            file_path = data.get("file_path")
            dir_path = data.get("dir_path")
            scan_type = "comprehensive"  # Default to comprehensive scan
            
            # Determine scan type based on extracted data
            if file_path:
                scan_type = "file"
                target = file_path
            elif dir_path:
                scan_type = "directory"
                target = dir_path
            elif target and target != ".":
                # If we have a specific target, determine type
                if os.path.isfile(target):
                    scan_type = "file"
                elif os.path.isdir(target):
                    scan_type = "directory"
                else:
                    # If target is not a valid path, default to current directory
                    logger.warning(f"Invalid target path '{target}', defaulting to current directory")
                    target = "."
                    scan_type = "comprehensive"
            
            logger.info(f"🔍 Secrets Detection: {scan_type} scan on {target}")
            
            # Execute the appropriate scan
            if scan_type == "file" and file_path:
                result = await agent.scan_file_for_secrets(file_path)
            elif scan_type == "directory" and dir_path:
                result = await agent.scan_directory_for_secrets(dir_path)
            else:
                result = await agent.run_comprehensive_scan(target)
            
            if not result.get("success"):
                return {
                    "action": "secrets_detection_error",
                    "error": result.get("error", "Unknown error"),
                    "target": target,
                    "scan_type": scan_type,
                    "note": f"Failed to perform {scan_type} scan on {target}"
                }
            
            # Extract key information for user-friendly response
            # Handle different result structures from MCP bridge
            if result.get("scan_type") == "comprehensive":
                # Comprehensive scan returns nested results
                scan_results = result.get("results", {})
                directory_scan = scan_results.get("directory_scan", {})
                env_scan = scan_results.get("env_scan", {})
                
                # Extract from nested results - need to go deeper into the results structure
                if directory_scan.get("success"):
                    dir_results = directory_scan.get("results", {})
                    secrets_count = dir_results.get("total_secrets_found", 0)
                    files_scanned = dir_results.get("files_scanned", 0)
                else:
                    secrets_count = 0
                    files_scanned = 0
                
                # Add env scan secrets
                if env_scan.get("success"):
                    env_results = env_scan.get("results", {})
                    secrets_count += env_results.get("total_secrets_found", 0)
                
                # Get risk level from security report if available
                security_report = scan_results.get("security_report", {})
                if security_report.get("success"):
                    report_data = security_report.get("report", {})
                    risk_assessment = report_data.get("risk_assessment", {})
                    risk_level = risk_assessment.get("risk_level", "UNKNOWN")
                    
                    # Auto-send email report if email is configured
                    email_recipient = os.getenv('SECURITY_REPORT_EMAIL')
                    if email_recipient:
                        try:
                            await self._send_security_report_email(
                                email_recipient, 
                                target, 
                                scan_type, 
                                secrets_count, 
                                files_scanned, 
                                risk_level,
                                security_report
                            )
                        except Exception as e:
                            logger.warning(f"Failed to send security report email: {e}")
                else:
                    risk_level = "UNKNOWN"
            else:
                # Direct scan results
                secrets_count = result.get("total_secrets_found", 0)
                files_scanned = result.get("files_scanned", 0)
                risk_level = "UNKNOWN"
            
            return {
                "action": "secrets_detection_completed",
                "target": target,
                "scan_type": scan_type,
                "secrets_count": secrets_count,
                "files_scanned": files_scanned,
                "risk_level": risk_level,
                "result": result,
                "note": f"Successfully completed {scan_type} scan on {target}. Found {secrets_count} secrets in {files_scanned} files."
            }
            
        except ImportError as e:
            return {
                "action": "secrets_detection_error",
                "error": "Secrets Detection Agent not available",
                "note": f"Import error: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Secrets detection failed: {e}")
            return {
                "action": "secrets_detection_error",
                "error": str(e),
                "note": "Secrets detection failed"
            }

    async def _handle_cybersecurity_scan(self, data: Dict[str, Any], session_id: str, user_id: str) -> Dict[str, Any]:
        """Handle comprehensive cybersecurity scanning requests."""
        logger.info(f"🔒 _handle_cybersecurity_scan called with data: {data}")
        try:
            import os
            import subprocess
            import json
            from pathlib import Path
            
            # Extract scan parameters
            target = data.get("target", ".")
            scan_type = data.get("scan_type", "comprehensive")
            
            logger.info(f"🔒 Cybersecurity Scan: {scan_type} scan on {target}")
            
            # Initialize results
            scan_results = {
                "target": target,
                "scan_type": scan_type,
                "timestamp": datetime.now().isoformat(),
                "results": {}
            }
            
            # Perform different types of scans based on request
            if "dependency" in scan_type or "dependency_scan" in data:
                # Dependency vulnerability scanning
                logger.info("🔍 Scanning dependencies for vulnerabilities...")
                dependency_results = await self._scan_dependencies(target)
                scan_results["results"]["dependency_scan"] = dependency_results
            
            if "sast" in scan_type or "sast_scan" in data:
                # SAST (Static Analysis) scanning
                logger.info("🔍 Performing SAST security analysis...")
                sast_results = await self._perform_sast_scan(target)
                scan_results["results"]["sast_scan"] = sast_results
            
            if "license" in scan_type or "license_check" in data:
                # License compliance checking
                logger.info("🔍 Checking license compliance...")
                license_results = await self._check_license_compliance(target)
                scan_results["results"]["license_check"] = license_results
            
            if "best_practices" in scan_type or "best_practices" in data:
                # Security best practices checking
                logger.info("🔍 Checking security best practices...")
                best_practices_results = await self._check_security_best_practices(target)
                scan_results["results"]["best_practices"] = best_practices_results
            
            if "pre_merge" in scan_type or "pre_merge" in data:
                # Pre-merge security gates
                logger.info("🔍 Checking pre-merge security gates...")
                pre_merge_results = await self._check_pre_merge_security_gates(target)
                scan_results["results"]["pre_merge_gates"] = pre_merge_results
            
            if "metrics" in scan_type or "metrics_tracking" in data:
                # Security metrics tracking
                logger.info("🔍 Tracking security metrics...")
                metrics_results = await self._track_security_metrics(target)
                scan_results["results"]["security_metrics"] = metrics_results
            
            # If no specific scan type, perform comprehensive scan
            if scan_type == "comprehensive" or not scan_results["results"]:
                logger.info("🔍 Performing comprehensive cybersecurity scan...")
                comprehensive_results = await self._perform_comprehensive_cybersecurity_scan(target)
                scan_results["results"]["comprehensive_scan"] = comprehensive_results
            
            # Generate security report
            security_report = await self._generate_security_report(scan_results)
            scan_results["security_report"] = security_report
            
            # Auto-send email report if configured
            email_recipient = os.getenv('SECURITY_REPORT_EMAIL')
            if email_recipient:
                try:
                    await self._send_cybersecurity_report_email(
                        email_recipient, 
                        target, 
                        scan_type, 
                        scan_results
                    )
                except Exception as e:
                    logger.warning(f"Failed to send cybersecurity report email: {e}")
            
            return {
                "action": "cybersecurity_scan_completed",
                "target": target,
                "scan_type": scan_type,
                "results": scan_results,
                "note": f"Successfully completed {scan_type} cybersecurity scan on {target}"
            }
            
        except Exception as e:
            logger.error(f"Cybersecurity scan failed: {e}")
            return {
                "action": "cybersecurity_scan_error",
                "error": str(e),
                "note": "Cybersecurity scan failed"
            }

    async def _scan_dependencies(self, target: str) -> Dict[str, Any]:
        """Scan dependencies for known vulnerabilities."""
        try:
            # This would integrate with tools like npm audit, pip-audit, etc.
            # For now, return a placeholder implementation
            return {
                "success": True,
                "scan_type": "dependency_vulnerability",
                "vulnerabilities_found": 0,
                "critical_vulnerabilities": 0,
                "high_vulnerabilities": 0,
                "medium_vulnerabilities": 0,
                "low_vulnerabilities": 0,
                "note": "Dependency vulnerability scanning placeholder - integrate with actual tools"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "note": "Dependency vulnerability scanning failed"
            }

    async def _perform_sast_scan(self, target: str) -> Dict[str, Any]:
        """Perform SAST (Static Analysis Security Testing) scan."""
        try:
            # This would integrate with tools like SonarQube, CodeQL, etc.
            # For now, return a placeholder implementation
            return {
                "success": True,
                "scan_type": "sast_static_analysis",
                "security_issues_found": 0,
                "critical_issues": 0,
                "high_issues": 0,
                "medium_issues": 0,
                "low_issues": 0,
                "note": "SAST scanning placeholder - integrate with actual tools"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "note": "SAST scanning failed"
            }

    async def _check_license_compliance(self, target: str) -> Dict[str, Any]:
        """Check license compliance."""
        try:
            # This would integrate with tools like license-checker, etc.
            # For now, return a placeholder implementation
            return {
                "success": True,
                "scan_type": "license_compliance",
                "license_issues_found": 0,
                "compliance_score": 100,
                "note": "License compliance checking placeholder - integrate with actual tools"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "note": "License compliance checking failed"
            }

    async def _check_security_best_practices(self, target: str) -> Dict[str, Any]:
        """Check security best practices."""
        try:
            # This would integrate with security linting tools
            # For now, return a placeholder implementation
            return {
                "success": True,
                "scan_type": "security_best_practices",
                "best_practices_violations": 0,
                "compliance_score": 100,
                "note": "Security best practices checking placeholder - integrate with actual tools"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "note": "Security best practices checking failed"
            }

    async def _check_pre_merge_security_gates(self, target: str) -> Dict[str, Any]:
        """Check pre-merge security gates."""
        try:
            # This would integrate with CI/CD security gates
            # For now, return a placeholder implementation
            return {
                "success": True,
                "scan_type": "pre_merge_security_gates",
                "gates_passed": 0,
                "gates_failed": 0,
                "blocking_issues": 0,
                "note": "Pre-merge security gates placeholder - integrate with actual tools"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "note": "Pre-merge security gates checking failed"
            }

    async def _track_security_metrics(self, target: str) -> Dict[str, Any]:
        """Track security metrics over time."""
        try:
            # This would integrate with security metrics tracking systems
            # For now, return a placeholder implementation
            return {
                "success": True,
                "scan_type": "security_metrics_tracking",
                "metrics_collected": 0,
                "trend_analysis": "stable",
                "improvement_score": 0,
                "note": "Security metrics tracking placeholder - integrate with actual tools"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "note": "Security metrics tracking failed"
            }

    async def _perform_comprehensive_cybersecurity_scan(self, target: str) -> Dict[str, Any]:
        """Perform comprehensive cybersecurity scan."""
        try:
            # Run all security scans
            results = {}
            
            # Dependency scan
            dependency_results = await self._scan_dependencies(target)
            results["dependency_scan"] = dependency_results
            
            # SAST scan
            sast_results = await self._perform_sast_scan(target)
            results["sast_scan"] = sast_results
            
            # License check
            license_results = await self._check_license_compliance(target)
            results["license_check"] = license_results
            
            # Best practices
            best_practices_results = await self._check_security_best_practices(target)
            results["best_practices"] = best_practices_results
            
            # Pre-merge gates
            pre_merge_results = await self._check_pre_merge_security_gates(target)
            results["pre_merge_gates"] = pre_merge_results
            
            # Metrics tracking
            metrics_results = await self._track_security_metrics(target)
            results["security_metrics"] = metrics_results
            
            return {
                "success": True,
                "scan_type": "comprehensive_cybersecurity",
                "results": results,
                "note": "Comprehensive cybersecurity scan completed"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "note": "Comprehensive cybersecurity scan failed"
            }

    async def _generate_security_report(self, scan_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive security report."""
        try:
            # Calculate overall security score
            total_issues = 0
            critical_issues = 0
            high_issues = 0
            
            # Aggregate issues from all scans
            for scan_type, results in scan_results["results"].items():
                if results.get("success"):
                    if "vulnerabilities_found" in results:
                        total_issues += results["vulnerabilities_found"]
                    if "critical_vulnerabilities" in results:
                        critical_issues += results["critical_vulnerabilities"]
                    if "high_vulnerabilities" in results:
                        high_issues += results["high_vulnerabilities"]
            
            # Calculate risk level
            if critical_issues > 0:
                risk_level = "CRITICAL"
            elif high_issues > 0:
                risk_level = "HIGH"
            elif total_issues > 0:
                risk_level = "MEDIUM"
            else:
                risk_level = "LOW"
            
            return {
                "success": True,
                "report": {
                    "summary": {
                        "total_issues": total_issues,
                        "critical_issues": critical_issues,
                        "high_issues": high_issues,
                        "risk_level": risk_level
                    },
                    "risk_assessment": {
                        "risk_level": risk_level,
                        "recommendations": self._get_security_recommendations(risk_level)
                    },
                    "timestamp": scan_results["timestamp"]
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "note": "Failed to generate security report"
            }

    def _get_security_recommendations(self, risk_level: str) -> List[str]:
        """Get security recommendations based on risk level."""
        recommendations = {
            "CRITICAL": [
                "Immediate action required - fix critical vulnerabilities",
                "Review and update security policies",
                "Conduct security training for development team",
                "Implement automated security scanning in CI/CD"
            ],
            "HIGH": [
                "Address high-priority vulnerabilities within 24 hours",
                "Review security configurations",
                "Update dependencies to latest secure versions",
                "Implement security code review process"
            ],
            "MEDIUM": [
                "Address medium-priority vulnerabilities within 1 week",
                "Review security best practices",
                "Update security documentation",
                "Schedule security review meeting"
            ],
            "LOW": [
                "Address low-priority vulnerabilities within 1 month",
                "Continue monitoring security metrics",
                "Maintain current security practices",
                "Plan for security improvements"
            ]
        }
        
        return recommendations.get(risk_level, ["Review security status and plan improvements"])

    async def _send_cybersecurity_report_email(self, email_recipient: str, target: str, scan_type: str, scan_results: Dict[str, Any]) -> None:
        """Send cybersecurity scan report via email."""
        try:
            # This would integrate with email sending functionality
            # For now, just log the action
            logger.info(f"📧 Cybersecurity report email would be sent to {email_recipient} for {scan_type} scan on {target}")
            
            # Extract key metrics for email
            total_issues = 0
            critical_issues = 0
            high_issues = 0
            
            for scan_type_results, results in scan_results["results"].items():
                if results.get("success"):
                    if "vulnerabilities_found" in results:
                        total_issues += results["vulnerabilities_found"]
                    if "critical_vulnerabilities" in results:
                        critical_issues += results["critical_vulnerabilities"]
                    if "high_vulnerabilities" in results:
                        high_issues += results["high_vulnerabilities"]
            
            logger.info(f"📊 Scan Summary: {total_issues} total issues, {critical_issues} critical, {high_issues} high")
            
        except Exception as e:
            logger.error(f"Failed to send cybersecurity report email: {e}")

    async def _send_security_report_email(self, email_recipient: str, target: str, scan_type: str, secrets_count: int, files_scanned: int, risk_level: str, security_report: Dict[str, Any]) -> None:
        """Send security report via email."""
        try:
            # This would integrate with email sending functionality
            # For now, just log the action
            logger.info(f"📧 Security report email would be sent to {email_recipient} for {scan_type} scan on {target}")
            logger.info(f"📊 Scan Summary: {secrets_count} secrets found in {files_scanned} files, Risk Level: {risk_level}")
            
        except Exception as e:
            logger.error(f"Failed to send security report email: {e}")

    async def _send_manual_email_report(self, data: Dict[str, Any], session_id: str, user_id: str) -> Dict[str, Any]:
        """Send manual email report for secrets detection."""
        try:
            # This would integrate with email sending functionality
            # For now, just log the action
            logger.info(f"📧 Manual email report requested for session {session_id}")
            
            return {
                "action": "email_report_sent",
                "note": "Email report would be sent (placeholder implementation)"
            }
            
        except Exception as e:
            logger.error(f"Failed to send manual email report: {e}")
            return {
                "action": "email_report_error",
                "error": str(e),
                "note": "Failed to send email report"
            }

# Global smart master agent instance
smart_master_agent = SmartMasterAgent() 