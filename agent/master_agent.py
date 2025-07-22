"""
Master Agent for coordinating and delegating tasks to specialized agents.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)

class AgentType(Enum):
    """Types of specialized agents."""
    MESSAGE_STORAGE = "message_storage"
    DESKTOP_STORAGE = "desktop_storage"
    EMAIL = "email"
    SEARCH = "search"
    KNOWLEDGE_GRAPH = "knowledge_graph"
    WEB_SEARCH = "web_search"
    GENERAL = "general"

@dataclass
class TaskRequest:
    """Request for a specific agent task."""
    agent_type: AgentType
    task: str
    parameters: Dict[str, Any]
    priority: int = 1
    user_message: str = ""

@dataclass
class TaskResult:
    """Result from an agent task."""
    agent_type: AgentType
    success: bool
    result: Any
    error: Optional[str] = None
    execution_time: float = 0.0

class MasterAgent:
    """
    Master agent that coordinates and delegates tasks to specialized agents.
    
    This agent analyzes user requests and routes them to the appropriate
    specialized agent for execution.
    """
    
    def __init__(self):
        self.task_history = []
        self.agent_stats = {}
        logger.info("Master agent initialized")
    
    async def analyze_request(self, user_message: str) -> List[TaskRequest]:
        """
        Analyze user request and determine which agents to involve.
        
        Args:
            user_message: The user's request
            
        Returns:
            List of task requests for different agents
        """
        tasks = []
        message_lower = user_message.lower()
        
        # Message storage tasks
        if any(keyword in message_lower for keyword in ["save", "store", "remember"]):
            if "desktop" in message_lower:
                tasks.append(TaskRequest(
                    agent_type=AgentType.DESKTOP_STORAGE,
                    task="save_message",
                    parameters={"message": user_message, "location": "desktop"},
                    priority=1,
                    user_message=user_message
                ))
            else:
                tasks.append(TaskRequest(
                    agent_type=AgentType.MESSAGE_STORAGE,
                    task="save_message", 
                    parameters={"message": user_message, "location": "project"},
                    priority=1,
                    user_message=user_message
                ))
        
        # Email tasks
        if any(keyword in message_lower for keyword in ["email", "compose", "send", "mail", "gmail"]):
            tasks.append(TaskRequest(
                agent_type=AgentType.EMAIL,
                task="compose_email",
                parameters={"message": user_message},
                priority=2,
                user_message=user_message
            ))
        
        # Search tasks
        if any(keyword in message_lower for keyword in ["search", "find", "look up", "query", "what is"]):
            if any(keyword in message_lower for keyword in ["web", "internet", "current", "latest", "news"]):
                tasks.append(TaskRequest(
                    agent_type=AgentType.WEB_SEARCH,
                    task="web_search",
                    parameters={"query": user_message},
                    priority=3,
                    user_message=user_message
                ))
            else:
                tasks.append(TaskRequest(
                    agent_type=AgentType.SEARCH,
                    task="search",
                    parameters={"query": user_message},
                    priority=3,
                    user_message=user_message
                ))
        
        # Knowledge graph tasks
        if any(keyword in message_lower for keyword in ["graph", "relationship", "entity", "knowledge", "company", "relationship between"]):
            tasks.append(TaskRequest(
                agent_type=AgentType.KNOWLEDGE_GRAPH,
                task="query_graph",
                parameters={"query": user_message},
                priority=4,
                user_message=user_message
            ))
        
        # If no specific task identified, use general agent
        if not tasks:
            tasks.append(TaskRequest(
                agent_type=AgentType.GENERAL,
                task="general_response",
                parameters={"message": user_message},
                priority=5,
                user_message=user_message
            ))
        
        return tasks
    
    async def execute_tasks(self, tasks: List[TaskRequest], session_id: str, user_id: str = None) -> List[TaskResult]:
        """
        Execute tasks using appropriate agents.
        
        Args:
            tasks: List of task requests
            session_id: Session ID for the request
            user_id: User ID for the request
            
        Returns:
            List of task results
        """
        results = []
        
        for task in sorted(tasks, key=lambda x: x.priority):
            try:
                logger.info(f"Master agent executing task: {task.agent_type.value} - {task.task}")
                start_time = datetime.now()
                
                if task.agent_type == AgentType.DESKTOP_STORAGE:
                    result = await self._execute_desktop_storage_task(task, session_id, user_id)
                elif task.agent_type == AgentType.MESSAGE_STORAGE:
                    result = await self._execute_message_storage_task(task, session_id, user_id)
                elif task.agent_type == AgentType.EMAIL:
                    result = await self._execute_email_task(task, session_id, user_id)
                elif task.agent_type == AgentType.SEARCH:
                    result = await self._execute_search_task(task, session_id, user_id)
                elif task.agent_type == AgentType.KNOWLEDGE_GRAPH:
                    result = await self._execute_knowledge_graph_task(task, session_id, user_id)
                elif task.agent_type == AgentType.WEB_SEARCH:
                    result = await self._execute_web_search_task(task, session_id, user_id)
                elif task.agent_type == AgentType.GENERAL:
                    result = await self._execute_general_task(task, session_id, user_id)
                else:
                    result = TaskResult(
                        agent_type=task.agent_type,
                        success=False,
                        result=None,
                        error=f"Unknown agent type: {task.agent_type}"
                    )
                
                end_time = datetime.now()
                execution_time = (end_time - start_time).total_seconds()
                result.execution_time = execution_time
                
                results.append(result)
                self.task_history.append((task, result))
                
                # Update agent stats
                if task.agent_type.value not in self.agent_stats:
                    self.agent_stats[task.agent_type.value] = {"calls": 0, "success": 0, "errors": 0}
                self.agent_stats[task.agent_type.value]["calls"] += 1
                if result.success:
                    self.agent_stats[task.agent_type.value]["success"] += 1
                else:
                    self.agent_stats[task.agent_type.value]["errors"] += 1
                
            except Exception as e:
                logger.error(f"Task execution failed: {e}")
                results.append(TaskResult(
                    agent_type=task.agent_type,
                    success=False,
                    result=None,
                    error=str(e)
                ))
        
        return results
    
    async def _execute_desktop_storage_task(self, task: TaskRequest, session_id: str, user_id: str) -> TaskResult:
        """Execute desktop storage tasks."""
        from .desktop_message_tools import desktop_storage
        
        try:
            if task.task == "save_message":
                message = task.parameters.get("message", "")
                result = desktop_storage.save_message(
                    message=message,
                    message_type="user_message",
                    metadata={"source": "master_agent", "session_id": session_id}
                )
                return TaskResult(
                    agent_type=task.agent_type,
                    success=True,
                    result=f"Message saved to Desktop: {result}"
                )
            else:
                return TaskResult(
                    agent_type=task.agent_type,
                    success=False,
                    result=None,
                    error=f"Unknown desktop storage task: {task.task}"
                )
        except Exception as e:
            return TaskResult(
                agent_type=task.agent_type,
                success=False,
                result=None,
                error=str(e)
            )
    
    async def _execute_message_storage_task(self, task: TaskRequest, session_id: str, user_id: str) -> TaskResult:
        """Execute message storage tasks."""
        from .message_tools import message_storage
        
        try:
            if task.task == "save_message":
                message = task.parameters.get("message", "")
                result = message_storage.save_message(
                    message=message,
                    message_type="user_message",
                    metadata={"source": "master_agent", "session_id": session_id}
                )
                return TaskResult(
                    agent_type=task.agent_type,
                    success=True,
                    result=f"Message saved to project: {result}"
                )
            else:
                return TaskResult(
                    agent_type=task.agent_type,
                    success=False,
                    result=None,
                    error=f"Unknown message storage task: {task.task}"
                )
        except Exception as e:
            return TaskResult(
                agent_type=task.agent_type,
                success=False,
                result=None,
                error=str(e)
            )
    
    async def _execute_email_task(self, task: TaskRequest, session_id: str, user_id: str) -> TaskResult:
        """Execute email tasks."""
        try:
            if task.task == "compose_email":
                # This would integrate with your email tools
                return TaskResult(
                    agent_type=task.agent_type,
                    success=True,
                    result="Email composition task identified - use compose_email tool"
                )
            else:
                return TaskResult(
                    agent_type=task.agent_type,
                    success=False,
                    result=None,
                    error=f"Unknown email task: {task.task}"
                )
        except Exception as e:
            return TaskResult(
                agent_type=task.agent_type,
                success=False,
                result=None,
                error=str(e)
            )
    
    async def _execute_search_task(self, task: TaskRequest, session_id: str, user_id: str) -> TaskResult:
        """Execute search tasks."""
        try:
            if task.task == "search":
                query = task.parameters.get("query", "")
                
                # Use the existing search tools from your system
                from .tools import vector_search_tool
                from .schemas import VectorSearchInput
                
                try:
                    # Perform vector search
                    search_input = VectorSearchInput(query=query, limit=5)
                    results = await vector_search_tool(search_input)
                    
                    return TaskResult(
                        agent_type=task.agent_type,
                        success=True,
                        result={
                            "message": f"Search completed for: {query}",
                            "results": results,
                            "total_results": len(results) if results else 0
                        }
                    )
                except Exception as search_error:
                    logger.error(f"Search failed: {search_error}")
                    return TaskResult(
                        agent_type=task.agent_type,
                        success=True,
                        result={
                            "message": f"Search task identified for query: {query}",
                            "note": "Search functionality available but encountered an error"
                        }
                    )
            else:
                return TaskResult(
                    agent_type=task.agent_type,
                    success=False,
                    result=None,
                    error=f"Unknown search task: {task.task}"
                )
        except Exception as e:
            return TaskResult(
                agent_type=task.agent_type,
                success=False,
                result=None,
                error=str(e)
            )
    
    async def _execute_knowledge_graph_task(self, task: TaskRequest, session_id: str, user_id: str) -> TaskResult:
        """Execute knowledge graph tasks."""
        try:
            if task.task == "query_graph":
                query = task.parameters.get("query", "")
                
                # Use the existing graph search tools from your system
                from .tools import graph_search_tool
                from .schemas import GraphSearchInput
                
                try:
                    # Perform graph search
                    search_input = GraphSearchInput(query=query)
                    results = await graph_search_tool(search_input)
                    
                    return TaskResult(
                        agent_type=task.agent_type,
                        success=True,
                        result={
                            "message": f"Knowledge graph query completed for: {query}",
                            "results": results,
                            "total_results": len(results) if results else 0
                        }
                    )
                except Exception as graph_error:
                    logger.error(f"Graph search failed: {graph_error}")
                    return TaskResult(
                        agent_type=task.agent_type,
                        success=True,
                        result={
                            "message": f"Knowledge graph query identified: {query}",
                            "note": "Graph search functionality available but encountered an error"
                        }
                    )
            else:
                return TaskResult(
                    agent_type=task.agent_type,
                    success=False,
                    result=None,
                    error=f"Unknown knowledge graph task: {task.task}"
                )
        except Exception as e:
            return TaskResult(
                agent_type=task.agent_type,
                success=False,
                result=None,
                error=str(e)
            )
    
    async def _execute_web_search_task(self, task: TaskRequest, session_id: str, user_id: str) -> TaskResult:
        """Execute web search tasks."""
        from .web_search_tools import web_search_tools
        
        try:
            if task.task == "web_search":
                query = task.parameters.get("query", "")
                
                # Perform actual web search
                results = await web_search_tools.search_web(query, max_results=5)
                
                # Format results for display
                formatted_results = []
                for result in results:
                    formatted_results.append({
                        "title": result.title,
                        "url": result.url,
                        "snippet": result.snippet,
                        "source": result.source
                    })
                
                return TaskResult(
                    agent_type=task.agent_type,
                    success=True,
                    result={
                        "message": f"Web search completed for: {query}",
                        "results": formatted_results,
                        "total_results": len(formatted_results)
                    }
                )
            else:
                return TaskResult(
                    agent_type=task.agent_type,
                    success=False,
                    result=None,
                    error=f"Unknown web search task: {task.task}"
                )
        except Exception as e:
            return TaskResult(
                agent_type=task.agent_type,
                success=False,
                result=None,
                error=str(e)
            )
    
    async def _execute_general_task(self, task: TaskRequest, session_id: str, user_id: str) -> TaskResult:
        """Execute general tasks."""
        try:
            if task.task == "general_response":
                message = task.parameters.get("message", "")
                return TaskResult(
                    agent_type=task.agent_type,
                    success=True,
                    result=f"General response task identified: {message}"
                )
            else:
                return TaskResult(
                    agent_type=task.agent_type,
                    success=False,
                    result=None,
                    error=f"Unknown general task: {task.task}"
                )
        except Exception as e:
            return TaskResult(
                agent_type=task.agent_type,
                success=False,
                result=None,
                error=str(e)
            )
    
    async def process_request(self, user_message: str, session_id: str, user_id: str = None) -> Dict[str, Any]:
        """
        Process a user request through the master agent.
        
        Args:
            user_message: The user's request
            session_id: Session ID for the request
            user_id: User ID for the request
            
        Returns:
            Summary of all agent actions and results
        """
        logger.info(f"Master agent processing request: {user_message}")
        
        # Analyze the request
        tasks = await self.analyze_request(user_message)
        logger.info(f"Identified {len(tasks)} tasks to execute")
        
        # Execute tasks
        results = await self.execute_tasks(tasks, session_id, user_id)
        
        # Compile summary
        summary = {
            "original_request": user_message,
            "session_id": session_id,
            "user_id": user_id,
            "tasks_executed": len(tasks),
            "successful_tasks": len([r for r in results if r.success]),
            "failed_tasks": len([r for r in results if not r.success]),
            "total_execution_time": sum(r.execution_time for r in results),
            "agent_stats": self.agent_stats,
            "results": [
                {
                    "agent": result.agent_type.value,
                    "success": result.success,
                    "result": result.result,
                    "error": result.error,
                    "execution_time": result.execution_time
                }
                for result in results
            ]
        }
        
        logger.info(f"Master agent completed processing. Summary: {summary}")
        return summary

# Global master agent instance
master_agent = MasterAgent() 