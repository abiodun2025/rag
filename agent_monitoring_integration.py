#!/usr/bin/env python3
"""
Agent Monitoring Integration for the entire agent ecosystem.
Provides easy-to-use monitoring hooks for all agents.
"""

import asyncio
import logging
import time
import traceback
from typing import Dict, Any, Optional, Callable
from functools import wraps
from datetime import datetime
import inspect

from alert_system import AlertSystem, AlertSeverity, AlertChannel

logger = logging.getLogger(__name__)

class AgentMonitor:
    """
    Central monitoring system for all agents in the ecosystem.
    Provides decorators and hooks for easy integration.
    """
    
    def __init__(self, alert_system: AlertSystem):
        self.alert_system = alert_system
        self.agent_stats = {}
        self.execution_times = {}
        
    def monitor_agent_execution(self, agent_name: str, severity: AlertSeverity = AlertSeverity.MEDIUM):
        """
        Decorator to monitor agent method execution.
        
        Usage:
            @monitor.monitor_agent_execution("smart_master_agent", AlertSeverity.HIGH)
            async def analyze_intent(self, message: str):
                # Your code here
        """
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                start_time = time.time()
                success = False
                error = None
                
                try:
                    # Track execution start
                    await self._track_agent_start(agent_name, func.__name__)
                    
                    # Execute the function
                    result = await func(*args, **kwargs)
                    success = True
                    
                    # Track successful completion
                    await self._track_agent_success(agent_name, func.__name__, result)
                    
                    return result
                    
                except Exception as e:
                    error = str(e)
                    logger.error(f"Agent {agent_name}.{func.__name__} failed: {error}")
                    
                    # Track failure and send alert
                    await self._track_agent_failure(agent_name, func.__name__, error, severity)
                    raise
                    
                finally:
                    # Track execution time
                    execution_time = time.time() - start_time
                    await self._track_execution_time(agent_name, func.__name__, execution_time, success)
                    
            return wrapper
        return decorator
    
    def monitor_tool_execution(self, tool_name: str, severity: AlertSeverity = AlertSeverity.MEDIUM):
        """
        Decorator to monitor tool execution within agents.
        
        Usage:
            @monitor.monitor_tool_execution("vector_search", AlertSeverity.HIGH)
            async def vector_search(self, query: str):
                # Your tool code here
        """
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                start_time = time.time()
                success = False
                error = None
                
                try:
                    # Track tool start
                    await self._track_tool_start(tool_name)
                    
                    # Execute the tool
                    result = await func(*args, **kwargs)
                    success = True
                    
                    # Track successful completion
                    await self._track_tool_success(tool_name, result)
                    
                    return result
                    
                except Exception as e:
                    error = str(e)
                    logger.error(f"Tool {tool_name} failed: {error}")
                    
                    # Track failure and send alert
                    await self._track_tool_failure(tool_name, error, severity)
                    raise
                    
                finally:
                    # Track execution time
                    execution_time = time.time() - start_time
                    await self._track_tool_execution_time(tool_name, execution_time, success)
                    
            return wrapper
        return decorator
    
    async def _track_agent_start(self, agent_name: str, method_name: str):
        """Track when an agent method starts execution."""
        key = f"{agent_name}.{method_name}"
        self.agent_stats[key] = {
            "start_time": datetime.now(),
            "status": "running"
        }
        logger.debug(f"🚀 Agent {key} started execution")
    
    async def _track_agent_success(self, agent_name: str, method_name: str, result: Any):
        """Track successful agent method completion."""
        key = f"{agent_name}.{method_name}"
        if key in self.agent_stats:
            self.agent_stats[key]["status"] = "completed"
            self.agent_stats[key]["end_time"] = datetime.now()
            self.agent_stats[key]["result"] = result
            
        logger.debug(f"✅ Agent {key} completed successfully")
    
    async def _track_agent_failure(self, agent_name: str, method_name: str, error: str, severity: AlertSeverity):
        """Track agent method failure and send alert."""
        key = f"{agent_name}.{method_name}"
        if key in self.agent_stats:
            self.agent_stats[key]["status"] = "failed"
            self.agent_stats[key]["end_time"] = datetime.now()
            self.agent_stats[key]["error"] = error
        
        # Send alert
        await self.alert_system.trigger_alert(
            rule_id="agent_execution_failed",
            message=f"Agent {agent_name}.{method_name} failed: {error}",
            data={
                "agent_name": agent_name,
                "method_name": method_name,
                "error": error,
                "timestamp": datetime.now().isoformat()
            }
        )
        
        logger.error(f"❌ Agent {key} failed: {error}")
    
    async def _track_tool_start(self, tool_name: str):
        """Track when a tool starts execution."""
        self.agent_stats[f"tool.{tool_name}"] = {
            "start_time": datetime.now(),
            "status": "running"
        }
        logger.debug(f"🔧 Tool {tool_name} started execution")
    
    async def _track_tool_success(self, tool_name: str, result: Any):
        """Track successful tool completion."""
        key = f"tool.{tool_name}"
        if key in self.agent_stats:
            self.agent_stats[key]["status"] = "completed"
            self.agent_stats[key]["end_time"] = datetime.now()
            self.agent_stats[key]["result"] = result
            
        logger.debug(f"✅ Tool {tool_name} completed successfully")
    
    async def _track_tool_failure(self, tool_name: str, error: str, severity: AlertSeverity):
        """Track tool failure and send alert."""
        key = f"tool.{tool_name}"
        if key in self.agent_stats:
            self.agent_stats[key]["status"] = "failed"
            self.agent_stats[key]["end_time"] = datetime.now()
            self.agent_stats[key]["error"] = error
        
        # Send alert
        await self.alert_system.trigger_alert(
            rule_id="tool_execution_failed",
            message=f"Tool {tool_name} failed: {error}",
            data={
                "tool_name": tool_name,
                "error": error,
                "timestamp": datetime.now().isoformat()
            }
        )
        
        logger.error(f"❌ Tool {tool_name} failed: {error}")
    
    async def _track_execution_time(self, agent_name: str, method_name: str, execution_time: float, success: bool):
        """Track execution time for performance monitoring."""
        key = f"{agent_name}.{method_name}"
        if key not in self.execution_times:
            self.execution_times[key] = []
        
        self.execution_times[key].append({
            "execution_time": execution_time,
            "success": success,
            "timestamp": datetime.now()
        })
        
        # Keep only last 100 executions
        if len(self.execution_times[key]) > 100:
            self.execution_times[key] = self.execution_times[key][-100:]
        
        # Alert if execution time is too high
        if execution_time > 30.0:  # 30 seconds threshold
            await self.alert_system.trigger_alert(
                rule_id="agent_performance_degradation",
                message=f"Agent {agent_name}.{method_name} took {execution_time:.2f}s to execute",
                data={
                    "agent_name": agent_name,
                    "method_name": method_name,
                    "execution_time": execution_time,
                    "threshold": 30.0,
                    "timestamp": datetime.now().isoformat()
                }
            )
    
    async def _track_tool_execution_time(self, tool_name: str, execution_time: float, success: bool):
        """Track tool execution time for performance monitoring."""
        key = f"tool.{tool_name}"
        if key not in self.execution_times:
            self.execution_times[key] = []
        
        self.execution_times[key].append({
            "execution_time": execution_time,
            "success": success,
            "timestamp": datetime.now()
        })
        
        # Keep only last 100 executions
        if len(self.execution_times[key]) > 100:
            self.execution_times[key] = self.execution_times[key][-100:]
        
        # Alert if execution time is too high
        if execution_time > 10.0:  # 10 seconds threshold for tools
            await self.alert_system.trigger_alert(
                rule_id="tool_performance_degradation",
                message=f"Tool {tool_name} took {execution_time:.2f}s to execute",
                data={
                    "tool_name": tool_name,
                    "execution_time": execution_time,
                    "threshold": 10.0,
                    "timestamp": datetime.now().isoformat()
                }
            )
    
    def get_agent_stats(self) -> Dict[str, Any]:
        """Get current agent statistics."""
        return {
            "agent_stats": self.agent_stats,
            "execution_times": self.execution_times,
            "summary": self._generate_summary()
        }
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate summary statistics."""
        total_executions = 0
        successful_executions = 0
        failed_executions = 0
        avg_execution_time = 0.0
        
        for key, times in self.execution_times.items():
            total_executions += len(times)
            successful_executions += sum(1 for t in times if t["success"])
            failed_executions += sum(1 for t in times if not t["success"])
            
            if times:
                avg_execution_time += sum(t["execution_time"] for t in times) / len(times)
        
        return {
            "total_executions": total_executions,
            "successful_executions": successful_executions,
            "failed_executions": failed_executions,
            "success_rate": (successful_executions / total_executions * 100) if total_executions > 0 else 0,
            "average_execution_time": avg_execution_time / len(self.execution_times) if self.execution_times else 0
        }

# Global monitor instance
_global_monitor = None

def get_agent_monitor() -> AgentMonitor:
    """Get the global agent monitor instance."""
    global _global_monitor
    if _global_monitor is None:
        # Initialize alert system
        alert_system = AlertSystem()
        _global_monitor = AgentMonitor(alert_system)
    return _global_monitor

# Convenience functions for easy integration
def monitor_agent(agent_name: str, severity: AlertSeverity = AlertSeverity.MEDIUM):
    """Convenience decorator for agent monitoring."""
    return get_agent_monitor().monitor_agent_execution(agent_name, severity)

def monitor_tool(tool_name: str, severity: AlertSeverity = AlertSeverity.MEDIUM):
    """Convenience decorator for tool monitoring."""
    return get_agent_monitor().monitor_tool_execution(tool_name, severity)

# Integration examples for existing agents
class SmartMasterAgentMonitor:
    """Monitoring integration for SmartMasterAgent."""
    
    @staticmethod
    def add_monitoring_to_smart_master_agent(agent_class):
        """Add monitoring to SmartMasterAgent methods."""
        monitor = get_agent_monitor()
        
        # Monitor key methods
        original_analyze_intent = agent_class.analyze_intent
        original_execute_intent = agent_class.execute_intent
        original_process_message = agent_class.process_message
        
        @monitor.monitor_agent_execution("smart_master_agent", AlertSeverity.HIGH)
        async def monitored_analyze_intent(self, message: str):
            return await original_analyze_intent(self, message)
        
        @monitor.monitor_agent_execution("smart_master_agent", AlertSeverity.HIGH)
        async def monitored_execute_intent(self, intent_result, session_id: str, user_id: str = None):
            return await original_execute_intent(self, intent_result, session_id, user_id)
        
        @monitor.monitor_agent_execution("smart_master_agent", AlertSeverity.HIGH)
        async def monitored_process_message(self, message: str, session_id: str, user_id: str = None):
            return await original_process_message(self, message, session_id, user_id)
        
        # Replace methods with monitored versions
        agent_class.analyze_intent = monitored_analyze_intent
        agent_class.execute_intent = monitored_execute_intent
        agent_class.process_message = monitored_process_message
        
        return agent_class

class MasterAgentMonitor:
    """Monitoring integration for MasterAgent."""
    
    @staticmethod
    def add_monitoring_to_master_agent(agent_class):
        """Add monitoring to MasterAgent methods."""
        monitor = get_agent_monitor()
        
        # Monitor key methods
        original_analyze_request = agent_class.analyze_request
        original_execute_tasks = agent_class.execute_tasks
        original_process_request = agent_class.process_request
        
        @monitor.monitor_agent_execution("master_agent", AlertSeverity.HIGH)
        async def monitored_analyze_request(self, user_message: str):
            return await original_analyze_request(self, user_message)
        
        @monitor.monitor_agent_execution("master_agent", AlertSeverity.HIGH)
        async def monitored_execute_tasks(self, tasks, session_id: str, user_id: str = None):
            return await original_execute_tasks(self, tasks, session_id, user_id)
        
        @monitor.monitor_agent_execution("master_agent", AlertSeverity.HIGH)
        async def monitored_process_request(self, user_message: str, session_id: str, user_id: str = None):
            return await original_process_request(self, user_message, session_id, user_id)
        
        # Replace methods with monitored versions
        agent_class.analyze_request = monitored_analyze_request
        agent_class.execute_tasks = monitored_execute_tasks
        agent_class.process_request = monitored_process_request
        
        return agent_class

class RAGAgentMonitor:
    """Monitoring integration for the main RAG agent."""
    
    @staticmethod
    def add_monitoring_to_rag_agent(agent_class):
        """Add monitoring to RAG agent tools."""
        monitor = get_agent_monitor()
        
        # Monitor key tools
        original_vector_search = agent_class.vector_search
        original_graph_search = agent_class.graph_search
        original_hybrid_search = agent_class.hybrid_search
        original_web_search = agent_class.web_search
        original_compose_email = agent_class.compose_email
        
        @monitor.monitor_tool_execution("vector_search", AlertSeverity.MEDIUM)
        async def monitored_vector_search(self, ctx, query: str, limit: int = 10):
            return await original_vector_search(self, ctx, query, limit)
        
        @monitor.monitor_tool_execution("graph_search", AlertSeverity.MEDIUM)
        async def monitored_graph_search(self, ctx, query: str):
            return await original_graph_search(self, ctx, query)
        
        @monitor.monitor_tool_execution("hybrid_search", AlertSeverity.MEDIUM)
        async def monitored_hybrid_search(self, ctx, query: str, limit: int = 10, text_weight: float = 0.3):
            return await original_hybrid_search(self, ctx, query, limit, text_weight)
        
        @monitor.monitor_tool_execution("web_search", AlertSeverity.MEDIUM)
        async def monitored_web_search(self, ctx, query: str, max_results: int = 5):
            return await original_web_search(self, ctx, query, max_results)
        
        @monitor.monitor_tool_execution("compose_email", AlertSeverity.HIGH)
        async def monitored_compose_email(self, ctx, to: str, subject: str, body: str):
            return await original_compose_email(self, ctx, to, subject, body)
        
        # Replace tools with monitored versions
        agent_class.vector_search = monitored_vector_search
        agent_class.graph_search = monitored_graph_search
        agent_class.hybrid_search = monitored_hybrid_search
        agent_class.web_search = monitored_web_search
        agent_class.compose_email = monitored_compose_email
        
        return agent_class

# Easy integration function
def integrate_monitoring_with_agents():
    """Integrate monitoring with all existing agents."""
    try:
        # Import agent classes
        from agent.smart_master_agent import SmartMasterAgent
        from agent.master_agent import MasterAgent
        from agent.agent import rag_agent
        
        # Add monitoring to each agent
        SmartMasterAgentMonitor.add_monitoring_to_smart_master_agent(SmartMasterAgent)
        MasterAgentMonitor.add_monitoring_to_master_agent(MasterAgent)
        RAGAgentMonitor.add_monitoring_to_rag_agent(rag_agent)
        
        logger.info("✅ Monitoring integrated with all agents")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to integrate monitoring: {e}")
        return False

# Usage example
if __name__ == "__main__":
    # Initialize monitoring
    integrate_monitoring_with_agents()
    
    # Get monitor instance
    monitor = get_agent_monitor()
    
    # Print stats
    print("Agent Monitoring System Ready!")
    print("Stats:", monitor.get_agent_stats()) 