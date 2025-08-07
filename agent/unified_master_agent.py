"""
Unified Master Agent - Single orchestrator with multiple routing strategies.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import re

logger = logging.getLogger(__name__)

class RoutingMode(Enum):
    """Available routing modes."""
    KEYWORD = "keyword"      # Fast, predictable
    PATTERN = "pattern"      # Smart, flexible
    LLM = "llm"             # Intelligent, adaptive
    AUTO = "auto"           # Automatically choose best

class SubAgentType(Enum):
    """Types of specialized sub-agents."""
    EMAIL = "email"
    SEARCH = "search"
    STORAGE = "storage"
    DESKTOP_STORAGE = "desktop_storage"
    WEB_SEARCH = "web_search"
    KNOWLEDGE_GRAPH = "knowledge_graph"
    MCP_TOOLS = "mcp_tools"
    CALL = "call"
    GENERAL = "general"

@dataclass
class RoutingResult:
    """Result of routing analysis."""
    sub_agent: SubAgentType
    confidence: float
    routing_mode: RoutingMode
    extracted_data: Dict[str, Any]
    original_message: str

@dataclass
class TaskResult:
    """Result from a sub-agent task."""
    sub_agent: SubAgentType
    success: bool
    result: Any
    error: Optional[str] = None
    execution_time: float = 0.0

class UnifiedMasterAgent:
    """
    Unified Master Agent that combines multiple routing strategies
    and delegates to specialized sub-agents.
    """
    
    def __init__(self, default_mode: RoutingMode = RoutingMode.AUTO):
        self.default_mode = default_mode
        self.task_history = []
        self.agent_stats = {}
        self.llm_available = self._check_llm_availability()
        
        # Initialize sub-agents
        self.sub_agents = {
            SubAgentType.EMAIL: self._email_sub_agent,
            SubAgentType.SEARCH: self._search_sub_agent,
            SubAgentType.STORAGE: self._storage_sub_agent,
            SubAgentType.DESKTOP_STORAGE: self._desktop_storage_sub_agent,
            SubAgentType.WEB_SEARCH: self._web_search_sub_agent,
            SubAgentType.KNOWLEDGE_GRAPH: self._knowledge_graph_sub_agent,
            SubAgentType.MCP_TOOLS: self._mcp_tools_sub_agent,
            SubAgentType.CALL: self._call_sub_agent,
            SubAgentType.GENERAL: self._general_sub_agent,
        }
        
        logger.info(f"Unified Master Agent initialized with mode: {default_mode}")
        logger.info(f"LLM available: {self.llm_available}")
    
    def _check_llm_availability(self) -> bool:
        """Check if LLM is available for intelligent routing."""
        try:
            # Try to import and check LLM availability
            from .providers import get_llm_provider
            provider = get_llm_provider()
            return provider is not None
        except Exception as e:
            logger.warning(f"LLM not available: {e}")
            return False
    
    def _determine_best_mode(self) -> RoutingMode:
        """Automatically determine the best routing mode."""
        if self.llm_available:
            return RoutingMode.LLM
        else:
            return RoutingMode.PATTERN
    
    def _keyword_based_routing(self, message: str) -> RoutingResult:
        """Fast keyword-based routing."""
        message_lower = message.lower()
        
        # Storage tasks
        if any(keyword in message_lower for keyword in ["save", "store", "remember"]):
            if "desktop" in message_lower:
                return RoutingResult(
                    sub_agent=SubAgentType.DESKTOP_STORAGE,
                    confidence=0.9,
                    routing_mode=RoutingMode.KEYWORD,
                    extracted_data={"message": message, "location": "desktop"},
                    original_message=message
                )
            else:
                return RoutingResult(
                    sub_agent=SubAgentType.STORAGE,
                    confidence=0.8,
                    routing_mode=RoutingMode.KEYWORD,
                    extracted_data={"message": message, "location": "project"},
                    original_message=message
                )
        
        # Email tasks
        if any(keyword in message_lower for keyword in ["email", "compose", "send", "mail", "gmail"]):
            return RoutingResult(
                sub_agent=SubAgentType.EMAIL,
                confidence=0.9,
                routing_mode=RoutingMode.KEYWORD,
                extracted_data={"message": message},
                original_message=message
            )
        
        # Search tasks
        if any(keyword in message_lower for keyword in ["search", "find", "look up", "query", "what is"]):
            if any(keyword in message_lower for keyword in ["web", "internet", "current", "latest", "news"]):
                return RoutingResult(
                    sub_agent=SubAgentType.WEB_SEARCH,
                    confidence=0.8,
                    routing_mode=RoutingMode.KEYWORD,
                    extracted_data={"query": message},
                    original_message=message
                )
            else:
                return RoutingResult(
                    sub_agent=SubAgentType.SEARCH,
                    confidence=0.8,
                    routing_mode=RoutingMode.KEYWORD,
                    extracted_data={"query": message},
                    original_message=message
                )
        
        # Knowledge graph tasks
        if any(keyword in message_lower for keyword in ["graph", "relationship", "entity", "knowledge", "company"]):
            return RoutingResult(
                sub_agent=SubAgentType.KNOWLEDGE_GRAPH,
                confidence=0.8,
                routing_mode=RoutingMode.KEYWORD,
                extracted_data={"query": message},
                original_message=message
            )
        
        # Default to general
        return RoutingResult(
            sub_agent=SubAgentType.GENERAL,
            confidence=0.5,
            routing_mode=RoutingMode.KEYWORD,
            extracted_data={"message": message},
            original_message=message
        )
    
    def _pattern_based_routing(self, message: str) -> RoutingResult:
        """Smart pattern-based routing."""
        message_lower = message.lower()
        
        # Pattern matching for different intents
        patterns = {
            SubAgentType.DESKTOP_STORAGE: [
                r"save.*desktop", r"remember.*desktop", r"store.*desktop",
                r"note.*desktop", r"desktop.*save", r"desktop.*remember",
                r"put.*desktop", r"keep.*desktop"
            ],
            SubAgentType.STORAGE: [
                r"save.*project", r"remember.*project", r"store.*project",
                r"note.*project", r"project.*save", r"project.*remember"
            ],
            SubAgentType.EMAIL: [
                r"email.*to", r"send.*email", r"compose.*email", r"mail.*to",
                r"write.*email", r"send.*mail", r"send.*to",
                r"@.*\.com", r"@.*\.org", r"@.*\.net", r"@.*\.edu"
            ],
            SubAgentType.WEB_SEARCH: [
                r"search.*web", r"find.*internet", r"look.*up.*online",
                r"what.*latest", r"current.*news", r"recent.*information"
            ],
            SubAgentType.KNOWLEDGE_GRAPH: [
                r"relationship.*between", r"entity.*graph", r"knowledge.*graph",
                r"company.*relationship", r"graph.*query"
            ]
        }
        
        best_match = None
        best_confidence = 0.0
        
        for sub_agent, pattern_list in patterns.items():
            for pattern in pattern_list:
                if re.search(pattern, message_lower):
                    confidence = 0.8
                    if sub_agent == SubAgentType.EMAIL and "@" in message:
                        confidence = 0.95
                    if confidence > best_confidence:
                        best_match = sub_agent
                        best_confidence = confidence
        
        if best_match:
            return RoutingResult(
                sub_agent=best_match,
                confidence=best_confidence,
                routing_mode=RoutingMode.PATTERN,
                extracted_data={"message": message},
                original_message=message
            )
        
        # Fallback to keyword routing
        return self._keyword_based_routing(message)
    
    async def _llm_based_routing(self, message: str) -> RoutingResult:
        """Intelligent LLM-based routing."""
        try:
            # This would use the LLM to intelligently determine the best sub-agent
            # For now, fallback to pattern-based routing
            logger.info("LLM routing not implemented, falling back to pattern routing")
            return self._pattern_based_routing(message)
        except Exception as e:
            logger.warning(f"LLM routing failed: {e}, falling back to pattern routing")
            return self._pattern_based_routing(message)
    
    async def route_request(self, message: str, mode: RoutingMode = None) -> RoutingResult:
        """Route request using the specified or best available mode."""
        if mode is None:
            mode = self.default_mode
        
        if mode == RoutingMode.AUTO:
            mode = self._determine_best_mode()
        
        logger.info(f"Routing request with mode: {mode}")
        
        if mode == RoutingMode.LLM:
            return await self._llm_based_routing(message)
        elif mode == RoutingMode.PATTERN:
            return self._pattern_based_routing(message)
        else:
            return self._keyword_based_routing(message)
    
    async def execute_task(self, routing_result: RoutingResult, session_id: str, user_id: str = None) -> TaskResult:
        """Execute task using the appropriate sub-agent."""
        start_time = datetime.now()
        
        try:
            sub_agent_func = self.sub_agents.get(routing_result.sub_agent)
            if sub_agent_func:
                result = await sub_agent_func(routing_result.extracted_data, session_id, user_id)
                execution_time = (datetime.now() - start_time).total_seconds()
                
                # Update stats
                self._update_stats(routing_result.sub_agent, True)
                
                return TaskResult(
                    sub_agent=routing_result.sub_agent,
                    success=True,
                    result=result,
                    execution_time=execution_time
                )
            else:
                raise ValueError(f"Unknown sub-agent: {routing_result.sub_agent}")
                
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            self._update_stats(routing_result.sub_agent, False)
            
            return TaskResult(
                sub_agent=routing_result.sub_agent,
                success=False,
                result=None,
                error=str(e),
                execution_time=execution_time
            )
    
    def _update_stats(self, sub_agent: SubAgentType, success: bool):
        """Update agent statistics."""
        if sub_agent.value not in self.agent_stats:
            self.agent_stats[sub_agent.value] = {"calls": 0, "success": 0, "errors": 0}
        
        self.agent_stats[sub_agent.value]["calls"] += 1
        if success:
            self.agent_stats[sub_agent.value]["success"] += 1
        else:
            self.agent_stats[sub_agent.value]["errors"] += 1
    
    async def process_request(self, message: str, session_id: str, user_id: str = None, mode: RoutingMode = None) -> Dict[str, Any]:
        """Process a user request using the unified master agent."""
        start_time = datetime.now()
        
        logger.info(f"Unified Master Agent processing: {message}")
        
        # Route the request
        routing_result = await self.route_request(message, mode)
        logger.info(f"Routed to {routing_result.sub_agent.value} with confidence {routing_result.confidence}")
        
        # Execute the task
        task_result = await self.execute_task(routing_result, session_id, user_id)
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Prepare response
        response = {
            "session_id": session_id,
            "unified_agent_result": {
                "original_message": message,
                "session_id": session_id,
                "user_id": user_id,
                "routing_analysis": {
                    "sub_agent": routing_result.sub_agent.value,
                    "confidence": routing_result.confidence,
                    "routing_mode": routing_result.routing_mode.value,
                    "extracted_data": routing_result.extracted_data
                },
                "execution_result": {
                    "success": task_result.success,
                    "sub_agent": routing_result.sub_agent.value,
                    "result": task_result.result,
                    "error": task_result.error,
                    "execution_time": task_result.execution_time
                },
                "agent_stats": self.agent_stats
            },
            "processing_time_ms": processing_time * 1000,
            "status": "success" if task_result.success else "error"
        }
        
        logger.info(f"Unified Master Agent completed processing in {processing_time:.3f}s")
        return response
    
    # Sub-agent implementations (simplified for example)
    async def _email_sub_agent(self, data: Dict[str, Any], session_id: str, user_id: str) -> Dict[str, Any]:
        """Email sub-agent implementation."""
        return {"action": "email_composed", "data": data}
    
    async def _search_sub_agent(self, data: Dict[str, Any], session_id: str, user_id: str) -> Dict[str, Any]:
        """Search sub-agent implementation."""
        return {"action": "search_performed", "query": data.get("query")}
    
    async def _storage_sub_agent(self, data: Dict[str, Any], session_id: str, user_id: str) -> Dict[str, Any]:
        """Storage sub-agent implementation."""
        return {"action": "message_stored", "data": data}
    
    async def _desktop_storage_sub_agent(self, data: Dict[str, Any], session_id: str, user_id: str) -> Dict[str, Any]:
        """Desktop storage sub-agent implementation."""
        # Import and use the actual desktop storage functionality
        from .desktop_message_tools import save_desktop_message
        result = await save_desktop_message(data["message"], "user_message", session_id, user_id)
        return {"action": "desktop_message_saved", "result": result}
    
    async def _web_search_sub_agent(self, data: Dict[str, Any], session_id: str, user_id: str) -> Dict[str, Any]:
        """Web search sub-agent implementation."""
        return {"action": "web_search_performed", "query": data.get("query")}
    
    async def _knowledge_graph_sub_agent(self, data: Dict[str, Any], session_id: str, user_id: str) -> Dict[str, Any]:
        """Knowledge graph sub-agent implementation."""
        return {"action": "graph_query_performed", "query": data.get("query")}
    
    async def _mcp_tools_sub_agent(self, data: Dict[str, Any], session_id: str, user_id: str) -> Dict[str, Any]:
        """MCP tools sub-agent implementation."""
        return {"action": "mcp_tool_called", "data": data}
    
    async def _call_sub_agent(self, data: Dict[str, Any], session_id: str, user_id: str) -> Dict[str, Any]:
        """Call sub-agent implementation."""
        return {"action": "call_initiated", "data": data}
    
    async def _general_sub_agent(self, data: Dict[str, Any], session_id: str, user_id: str) -> Dict[str, Any]:
        """General sub-agent implementation."""
        return {"action": "general_response", "message": data.get("message")}

# Create a single instance
unified_master_agent = UnifiedMasterAgent() 