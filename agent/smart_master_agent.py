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
                r"@.*\.com",
                r"@.*\.org",
                r"@.*\.net"
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
            ],
            IntentType.MCP_TOOLS: [
                r"count.*r.*letters",
                r"count.*letters.*r",
                r"list.*desktop.*files",
                r"list.*desktop.*contents",
                r"get.*desktop.*path",
                r"open.*gmail",
                r"open.*gmail.*compose",
                r"send.*email.*via.*sendmail",
                r"send.*simple.*email",
                r"call.*mcp.*tool",
                r"list.*available.*mcp.*tools",
                r"mcp.*tool",
                r"mcp.*server"
            ],
            IntentType.SEARCH: [
                r"search.*for",
                r"find.*information",
                r"look.*up",
                r"what.*is",
                r"tell.*me.*about",
                r"information.*about",
                r"who.*is",
                r"what.*are",
                r"how.*does",
                r"when.*did",
                r"where.*is",
                r"why.*does"
            ]
        }
        
        # Check each intent pattern
        best_match = None
        highest_confidence = 0.0
        
        for intent, pattern_list in patterns.items():
            for pattern in pattern_list:
                if re.search(pattern, message_lower):
                    confidence = len(re.findall(pattern, message_lower)) * 0.3
                    
                    # Boost confidence for more specific patterns
                    if intent == IntentType.EMAIL and any(word in message_lower for word in ["@", "email", "mail"]):
                        confidence += 0.4
                    elif intent == IntentType.SAVE_DESKTOP and "desktop" in message_lower:
                        confidence += 0.4
                    elif intent == IntentType.SAVE_PROJECT and "project" in message_lower:
                        confidence += 0.4
                    elif intent == IntentType.WEB_SEARCH and any(word in message_lower for word in ["web", "internet", "latest", "current"]):
                        confidence += 0.4
                    
                    if confidence > highest_confidence:
                        highest_confidence = confidence
                        best_match = intent
        
        # If no specific intent found, determine based on content
        if not best_match:
            if any(word in message_lower for word in ["save", "remember", "store", "note"]):
                # Default to desktop save if saving intent detected
                best_match = IntentType.SAVE_DESKTOP
                highest_confidence = 0.6
            elif any(word in message_lower for word in ["search", "find", "look", "what", "tell", "who", "how", "when", "where", "why"]):
                # Default to web search for search-like queries
                best_match = IntentType.WEB_SEARCH
                highest_confidence = 0.7
            else:
                # Default to general conversation
                best_match = IntentType.GENERAL
                highest_confidence = 0.3
        
        # Extract relevant data based on intent
        extracted_data = self._extract_data(message, best_match)
        
        return IntentResult(
            intent=best_match,
            confidence=min(highest_confidence, 1.0),
            extracted_data=extracted_data,
            original_message=message
        )
    
    def _extract_data(self, message: str, intent: IntentType) -> Dict[str, Any]:
        """Extract relevant data from message based on intent."""
        data = {"original_message": message}
        
        if intent == IntentType.SAVE_DESKTOP:
            # Extract the content to save
            data["content"] = message
            data["location"] = "desktop"
            
        elif intent == IntentType.SAVE_PROJECT:
            data["content"] = message
            data["location"] = "project"
            
        elif intent == IntentType.EMAIL:
            # Extract email components
            email_pattern = r"(\w+@[\w\.-]+\.\w+)"
            emails = re.findall(email_pattern, message)
            data["to_email"] = emails[0] if emails else None
            
            # Extract subject and body
            subject_match = re.search(r"subject[:\s]+([^,]+)", message, re.IGNORECASE)
            data["subject"] = subject_match.group(1).strip() if subject_match else "No subject"
            
            body_match = re.search(r"body[:\s]+([^,]+)", message, re.IGNORECASE)
            data["body"] = body_match.group(1).strip() if body_match else "No body"
            
        elif intent == IntentType.WEB_SEARCH:
            # Extract search query
            search_words = ["search", "find", "look", "what", "tell", "latest", "current"]
            query = message
            for word in search_words:
                if word in message.lower():
                    query = message.lower().split(word, 1)[1].strip()
                    break
            data["query"] = query
            
        elif intent == IntentType.SEARCH:
            # Extract search query
            search_words = ["search for", "find", "look up", "what is", "tell me about", "who is", "what are", "how does", "when did", "where is", "why does"]
            query = message
            for phrase in search_words:
                if phrase in message.lower():
                    query = message.lower().split(phrase, 1)[1].strip()
                    break
            data["query"] = query
            
        elif intent == IntentType.KNOWLEDGE_GRAPH:
            data["query"] = message
            
        else:  # GENERAL
            data["message"] = message
        
        return data
    
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
        
        content = data.get("content", "")
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
        
        content = data.get("content", "")
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