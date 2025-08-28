#!/usr/bin/env python3
"""
Task/Project Agent - Manages and syncs projects across multiple platforms.
Integrates with Jira, Trello, Asana, and Linear through MCP tools.
"""

import asyncio
import logging
import json
import httpx
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import re

logger = logging.getLogger(__name__)

class PlatformType(Enum):
    """Supported project management platforms."""
    JIRA = "jira"
    TRELLO = "trello"
    ASANA = "asana"
    LINEAR = "linear"

class TaskStatus(Enum):
    """Task status values."""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"
    BLOCKED = "blocked"

class TaskPriority(Enum):
    """Task priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

@dataclass
class ProjectTask:
    """Represents a task across different platforms."""
    task_id: str
    title: str
    description: str
    status: TaskStatus
    priority: TaskPriority
    assignee: Optional[str] = None
    due_date: Optional[str] = None
    platform: Optional[PlatformType] = None
    platform_specific_id: Optional[str] = None
    tags: List[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

@dataclass
class SyncResult:
    """Result of a sync operation."""
    success: bool
    source_platform: PlatformType
    target_platform: PlatformType
    tasks_synced: int
    errors: List[str] = None
    sync_id: Optional[str] = None

class TaskProjectAgent:
    """
    Task/Project Agent that manages projects across multiple platforms.
    Uses MCP tools to interact with Jira, Trello, Asana, and Linear.
    """
    
    def __init__(self, mcp_server_url: str = "http://127.0.0.1:5000"):
        self.mcp_server_url = mcp_server_url
        self.client = httpx.AsyncClient(timeout=30.0)
        self.platform_configs = {}
        self.sync_history = []
        self.task_cache = {}
        
        # Initialize platform configurations
        self._init_platform_configs()
        logger.info(f"Task/Project Agent initialized with MCP server: {mcp_server_url}")
    
    def _init_platform_configs(self):
        """Initialize platform configurations."""
        self.platform_configs = {
            PlatformType.JIRA: {
                "name": "Jira",
                "issue_types": ["Task", "Bug", "Story", "Epic"],
                "statuses": ["To Do", "In Progress", "Review", "Done"],
                "priorities": ["Low", "Medium", "High", "Highest"]
            },
            PlatformType.TRELLO: {
                "name": "Trello",
                "list_names": ["To Do", "In Progress", "Review", "Done"],
                "card_types": ["Task", "Bug", "Feature"]
            },
            PlatformType.ASANA: {
                "name": "Asana",
                "task_types": ["Task", "Milestone", "Goal"],
                "statuses": ["Not Started", "In Progress", "Completed"]
            },
            PlatformType.LINEAR: {
                "name": "Linear",
                "issue_types": ["Issue", "Bug", "Feature", "Milestone"],
                "priorities": ["No priority", "Low", "Medium", "High", "Urgent"],
                "teams": ["Engineering", "Design", "Product", "Marketing"]
            }
        }
    
    async def check_mcp_server_health(self) -> bool:
        """Check if MCP server is healthy."""
        try:
            response = await self.client.get(f"{self.mcp_server_url}/health")
            if response.status_code == 200:
                data = response.json()
                return data.get("status") == "healthy"
            return False
        except Exception as e:
            logger.error(f"Failed to check MCP server health: {e}")
            return False
    
    async def get_available_tools(self) -> List[Dict]:
        """Get available MCP tools."""
        try:
            response = await self.client.get(f"{self.mcp_server_url}/tools")
            if response.status_code == 200:
                data = response.json()
                return data.get("tools", [])
            return []
        except Exception as e:
            logger.error(f"Failed to get available tools: {e}")
            return []
    
    async def call_mcp_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call an MCP tool."""
        try:
            payload = {
                "tool": tool_name,
                "arguments": arguments
            }
            
            response = await self.client.post(
                f"{self.mcp_server_url}/call",
                json=payload,
                timeout=30.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
        except Exception as e:
            logger.error(f"Failed to call MCP tool {tool_name}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def create_task(self, platform: PlatformType, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a task on the specified platform."""
        try:
            if platform == PlatformType.JIRA:
                return await self.call_mcp_tool("jira_create_issue", {
                    "project_key": task_data.get("project_key", "PROJ"),
                    "summary": task_data.get("title", ""),
                    "description": task_data.get("description", ""),
                    "issue_type": task_data.get("issue_type", "Task")
                })
            elif platform == PlatformType.TRELLO:
                return await self.call_mcp_tool("trello_create_card", {
                    "board_name": task_data.get("board_name", "Project Board"),
                    "list_name": task_data.get("list_name", "To Do"),
                    "card_title": task_data.get("title", ""),
                    "description": task_data.get("description", "")
                })
            elif platform == PlatformType.ASANA:
                return await self.call_mcp_tool("asana_create_task", {
                    "project_name": task_data.get("project_name", "Default Project"),
                    "task_name": task_data.get("title", ""),
                    "description": task_data.get("description", "")
                })
            elif platform == PlatformType.LINEAR:
                return await self.call_mcp_tool("linear_create_issue", {
                    "team_name": task_data.get("team_name", "Engineering"),
                    "title": task_data.get("title", ""),
                    "description": task_data.get("description", ""),
                    "priority": task_data.get("priority", "Medium")
                })
            else:
                return {
                    "success": False,
                    "error": f"Unsupported platform: {platform.value}"
                }
        except Exception as e:
            logger.error(f"Failed to create task on {platform.value}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_tasks(self, platform: PlatformType, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get tasks from the specified platform."""
        try:
            if platform == PlatformType.JIRA:
                return await self.call_mcp_tool("jira_get_issues", {
                    "project_key": filters.get("project_key") if filters else None,
                    "status": filters.get("status") if filters else None
                })
            elif platform == PlatformType.TRELLO:
                return await self.call_mcp_tool("trello_get_cards", {
                    "board_name": filters.get("board_name") if filters else None
                })
            elif platform == PlatformType.ASANA:
                return await self.call_mcp_tool("asana_get_tasks", {
                    "project_name": filters.get("project_name") if filters else None
                })
            elif platform == PlatformType.LINEAR:
                return await self.call_mcp_tool("linear_get_issues", {
                    "team_name": filters.get("team_name") if filters else None
                })
            else:
                return {
                    "success": False,
                    "error": f"Unsupported platform: {platform.value}"
                }
        except Exception as e:
            logger.error(f"Failed to get tasks from {platform.value}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def update_task(self, platform: PlatformType, task_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update a task on the specified platform."""
        try:
            if platform == PlatformType.JIRA:
                return await self.call_mcp_tool("jira_update_issue", {
                    "issue_id": task_id,
                    "updates": updates
                })
            elif platform == PlatformType.TRELLO:
                return await self.call_mcp_tool("trello_update_card", {
                    "card_id": task_id,
                    "updates": updates
                })
            elif platform == PlatformType.ASANA:
                return await self.call_mcp_tool("asana_update_task", {
                    "task_id": task_id,
                    "updates": updates
                })
            elif platform == PlatformType.LINEAR:
                return await self.call_mcp_tool("linear_update_issue", {
                    "issue_id": task_id,
                    "updates": updates
                })
            else:
                return {
                    "success": False,
                    "error": f"Unsupported platform: {platform.value}"
                }
        except Exception as e:
            logger.error(f"Failed to update task on {platform.value}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def sync_projects(self, source_platform: PlatformType, target_platform: PlatformType, 
                           project_id: str) -> SyncResult:
        """Sync projects between different platforms."""
        try:
            # Get tasks from source platform
            source_tasks = await self.get_tasks(source_platform, {"project_id": project_id})
            if not source_tasks.get("success"):
                return SyncResult(
                    success=False,
                    source_platform=source_platform,
                    target_platform=target_platform,
                    tasks_synced=0,
                    errors=[f"Failed to get tasks from {source_platform.value}: {source_tasks.get('error')}"]
                )
            
            # Start sync process
            sync_result = await self.call_mcp_tool("sync_projects", {
                "source_platform": source_platform.value,
                "target_platform": target_platform.value,
                "project_id": project_id
            })
            
            if sync_result.get("success"):
                sync_id = sync_result.get("result", {}).get("sync_id")
                self.sync_history.append({
                    "sync_id": sync_id,
                    "source_platform": source_platform.value,
                    "target_platform": target_platform.value,
                    "project_id": project_id,
                    "timestamp": datetime.now().isoformat()
                })
                
                return SyncResult(
                    success=True,
                    source_platform=source_platform,
                    target_platform=target_platform,
                    tasks_synced=len(source_tasks.get("result", [])),
                    sync_id=sync_id
                )
            else:
                return SyncResult(
                    success=False,
                    source_platform=source_platform,
                    target_platform=target_platform,
                    tasks_synced=0,
                    errors=[sync_result.get("error", "Unknown sync error")]
                )
                
        except Exception as e:
            logger.error(f"Failed to sync projects: {e}")
            return SyncResult(
                success=False,
                source_platform=source_platform,
                target_platform=target_platform,
                tasks_synced=0,
                errors=[str(e)]
            )
    
    async def get_project_status(self, platform: PlatformType, project_id: str) -> Dict[str, Any]:
        """Get project status from a specific platform."""
        try:
            result = await self.call_mcp_tool("get_project_status", {
                "platform": platform.value,
                "project_id": project_id
            })
            return result
        except Exception as e:
            logger.error(f"Failed to get project status: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def bulk_create_tasks(self, platform: PlatformType, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create multiple tasks on the specified platform."""
        results = []
        success_count = 0
        error_count = 0
        
        for task_data in tasks:
            result = await self.create_task(platform, task_data)
            if result.get("success"):
                success_count += 1
            else:
                error_count += 1
            results.append(result)
        
        return {
            "success": True,
            "total_tasks": len(tasks),
            "successful": success_count,
            "failed": error_count,
            "results": results
        }
    
    async def get_platform_info(self, platform: PlatformType) -> Dict[str, Any]:
        """Get information about a specific platform."""
        if platform in self.platform_configs:
            config = self.platform_configs[platform]
            return {
                "success": True,
                "platform": platform.value,
                "name": config["name"],
                "capabilities": list(config.keys()),
                "config": config
            }
        else:
            return {
                "success": False,
                "error": f"Platform {platform.value} not configured"
            }
    
    async def get_sync_history(self) -> List[Dict[str, Any]]:
        """Get sync operation history."""
        return self.sync_history
    
    async def clear_cache(self) -> Dict[str, Any]:
        """Clear the task cache."""
        cache_size = len(self.task_cache)
        self.task_cache.clear()
        return {
            "success": True,
            "message": f"Cache cleared. Removed {cache_size} cached items."
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform a comprehensive health check."""
        mcp_healthy = await self.check_mcp_server_health()
        tools_available = await self.get_available_tools()
        
        return {
            "agent_status": "healthy" if mcp_healthy else "degraded",
            "mcp_server_healthy": mcp_healthy,
            "tools_available": len(tools_available),
            "platforms_supported": len(self.platform_configs),
            "cache_size": len(self.task_cache),
            "sync_operations": len(self.sync_history),
            "timestamp": datetime.now().isoformat()
        }

# Example usage and testing
async def main():
    """Example usage of the TaskProjectAgent."""
    agent = TaskProjectAgent()
    
    # Check health
    health = await agent.health_check()
    print(f"Agent Health: {health}")
    
    # Get available tools
    tools = await agent.get_available_tools()
    print(f"Available Tools: {len(tools)}")
    
    # Create a sample task
    task_result = await agent.create_task(PlatformType.JIRA, {
        "project_key": "TEST",
        "title": "Test Task",
        "description": "This is a test task created by the agent",
        "issue_type": "Task"
    })
    print(f"Task Creation Result: {task_result}")
    
    # Get tasks
    tasks = await agent.get_tasks(PlatformType.JIRA)
    print(f"Jira Tasks: {tasks}")

if __name__ == "__main__":
    asyncio.run(main())
