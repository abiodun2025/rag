#!/usr/bin/env python3
"""
Alert System Integration with Master Agent and Workflow System
Shows how to integrate alerts into existing agent workflows.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from alert_system import AlertSystem, AlertRule, AlertSeverity, AlertChannel

logger = logging.getLogger(__name__)

class AlertIntegration:
    """Integrates alert system with existing agent workflows."""
    
    def __init__(self, alert_system: AlertSystem):
        self.alert_system = alert_system
        self._setup_workflow_alerts()
    
    def _setup_workflow_alerts(self):
        """Setup alert rules specific to workflow monitoring."""
        workflow_rules = [
            AlertRule(
                rule_id="task_execution_failed",
                name="Task Execution Failed",
                description="A workflow task failed to execute",
                condition="task_status == 'failed'",
                severity=AlertSeverity.HIGH,
                channels=[AlertChannel.EMAIL, AlertChannel.SLACK],
                cooldown_minutes=2
            ),
            AlertRule(
                rule_id="agent_unresponsive",
                name="Agent Unresponsive",
                description="An agent has not responded for too long",
                condition="agent_last_heartbeat_age > 300",  # 5 minutes
                severity=AlertSeverity.HIGH,
                channels=[AlertChannel.EMAIL, AlertChannel.SLACK],
                cooldown_minutes=5
            ),
            AlertRule(
                rule_id="workflow_completed",
                name="Workflow Completed",
                description="A workflow completed successfully",
                condition="workflow_status == 'completed'",
                severity=AlertSeverity.LOW,
                channels=[AlertChannel.SLACK],
                cooldown_minutes=1
            ),
            AlertRule(
                rule_id="queue_overflow",
                name="Task Queue Overflow",
                description="Task queue has too many pending tasks",
                condition="pending_tasks_count > 50",
                severity=AlertSeverity.MEDIUM,
                channels=[AlertChannel.EMAIL, AlertChannel.SLACK],
                cooldown_minutes=10
            ),
            AlertRule(
                rule_id="github_api_error",
                name="GitHub API Error",
                description="GitHub API returned an error",
                condition="github_api_status_code >= 400",
                severity=AlertSeverity.HIGH,
                channels=[AlertChannel.EMAIL, AlertChannel.SLACK],
                cooldown_minutes=2
            )
        ]
        
        for rule in workflow_rules:
            self.alert_system.add_rule(rule)
        
        logger.info(f"✅ Added {len(workflow_rules)} workflow-specific alert rules")

class MasterAgentAlertIntegration:
    """Integrates alerts with the Master Agent."""
    
    def __init__(self, master_agent, alert_system: AlertSystem):
        self.master_agent = master_agent
        self.alert_system = alert_system
        self.integration = AlertIntegration(alert_system)
    
    async def monitor_master_agent(self):
        """Monitor master agent health and send alerts."""
        try:
            # Check agent statuses
            for agent_id, agent in self.master_agent.slave_agents.items():
                if agent.status != "available":
                    await self.alert_system.trigger_alert(
                        "agent_unresponsive",
                        f"Agent {agent.name} is not available",
                        {
                            "agent_id": agent_id,
                            "agent_name": agent.name,
                            "status": agent.status,
                            "last_heartbeat": agent.last_heartbeat
                        }
                    )
            
            # Check task queue
            pending_count = len([task for task in self.master_agent.tasks.values() 
                               if task.status == "pending"])
            
            if pending_count > 50:
                await self.alert_system.trigger_alert(
                    "queue_overflow",
                    f"Task queue has {pending_count} pending tasks",
                    {
                        "pending_tasks": pending_count,
                        "total_tasks": len(self.master_agent.tasks),
                        "available_agents": len([a for a in self.master_agent.slave_agents.values() 
                                               if a.status == "available"])
                    }
                )
            
            # Check for failed tasks
            failed_tasks = [task for task in self.master_agent.tasks.values() 
                          if task.status == "failed"]
            
            for task in failed_tasks:
                await self.alert_system.trigger_alert(
                    "task_execution_failed",
                    f"Task {task.task_id} failed: {task.error}",
                    {
                        "task_id": task.task_id,
                        "task_type": task.task_type,
                        "assigned_agent": task.assigned_agent,
                        "error": task.error,
                        "created_at": task.created_at
                    }
                )
        
        except Exception as e:
            logger.error(f"Error monitoring master agent: {e}")
            await self.alert_system.trigger_alert(
                "mcp_server_down",
                f"Master agent monitoring failed: {e}",
                {"error": str(e)}
            )

class WorkflowAlertIntegration:
    """Integrates alerts with workflow execution."""
    
    def __init__(self, alert_system: AlertSystem):
        self.alert_system = alert_system
    
    async def on_workflow_start(self, workflow_id: str, workflow_type: str, parameters: Dict[str, Any]):
        """Called when a workflow starts."""
        logger.info(f"🚀 Workflow {workflow_id} started: {workflow_type}")
    
    async def on_workflow_complete(self, workflow_id: str, workflow_type: str, 
                                 success: bool, result: Optional[Dict[str, Any]] = None):
        """Called when a workflow completes."""
        if success:
            await self.alert_system.trigger_alert(
                "workflow_completed",
                f"Workflow {workflow_id} completed successfully",
                {
                    "workflow_id": workflow_id,
                    "workflow_type": workflow_type,
                    "result": result
                }
            )
        else:
            await self.alert_system.trigger_alert(
                "task_execution_failed",
                f"Workflow {workflow_id} failed",
                {
                    "workflow_id": workflow_id,
                    "workflow_type": workflow_type,
                    "result": result
                }
            )
    
    async def on_task_start(self, task_id: str, task_type: str, assigned_agent: str):
        """Called when a task starts."""
        logger.info(f"🔄 Task {task_id} started on {assigned_agent}")
    
    async def on_task_complete(self, task_id: str, task_type: str, 
                             success: bool, result: Optional[Dict[str, Any]] = None,
                             error: Optional[str] = None):
        """Called when a task completes."""
        if success:
            logger.info(f"✅ Task {task_id} completed successfully")
        else:
            await self.alert_system.trigger_alert(
                "task_execution_failed",
                f"Task {task_id} failed: {error}",
                {
                    "task_id": task_id,
                    "task_type": task_type,
                    "error": error,
                    "result": result
                }
            )

class GitHubAlertIntegration:
    """Integrates alerts with GitHub operations."""
    
    def __init__(self, alert_system: AlertSystem):
        self.alert_system = alert_system
    
    async def on_pr_created(self, pr_number: int, title: str, url: str, 
                           repository: str, author: str):
        """Called when a pull request is created."""
        await self.alert_system.trigger_alert(
            "pr_creation_success",
            f"Pull request #{pr_number} created: {title}",
            {
                "pr_number": pr_number,
                "title": title,
                "url": url,
                "repository": repository,
                "author": author
            }
        )
    
    async def on_pr_failed(self, error: str, parameters: Dict[str, Any]):
        """Called when pull request creation fails."""
        await self.alert_system.trigger_alert(
            "pr_creation_failed",
            f"Pull request creation failed: {error}",
            {
                "error": error,
                "parameters": parameters
            }
        )
    
    async def on_pr_merged(self, pr_number: int, title: str, merged_by: str):
        """Called when a pull request is merged."""
        await self.alert_system.trigger_alert(
            "pr_creation_success",  # Reuse success rule
            f"Pull request #{pr_number} merged: {title}",
            {
                "pr_number": pr_number,
                "title": title,
                "merged_by": merged_by,
                "action": "merged"
            }
        )
    
    async def on_github_api_error(self, status_code: int, error_message: str, 
                                operation: str):
        """Called when GitHub API returns an error."""
        await self.alert_system.trigger_alert(
            "github_api_error",
            f"GitHub API error ({status_code}): {error_message}",
            {
                "status_code": status_code,
                "error_message": error_message,
                "operation": operation
            }
        )

# Example integration with your existing master agent
class EnhancedMasterAgent:
    """Enhanced master agent with alert integration."""
    
    def __init__(self, mcp_bridge_url: str = "http://127.0.0.1:5000"):
        # Initialize alert system
        self.alert_system = AlertSystem(mcp_bridge_url)
        
        # Initialize your existing master agent (you'll need to adapt this)
        # self.master_agent = MasterAgent(mcp_bridge_url)
        
        # Setup alert integrations
        self.workflow_alerts = WorkflowAlertIntegration(self.alert_system)
        self.github_alerts = GitHubAlertIntegration(self.alert_system)
        
        # Start alert monitoring
        asyncio.create_task(self.alert_system.start_monitoring())
        
        logger.info("🚀 Enhanced Master Agent with alerts initialized")
    
    async def create_workflow_with_alerts(self, workflow_type: str, 
                                        parameters: Dict[str, Any], 
                                        priority: int = 2) -> str:
        """Create workflow with alert monitoring."""
        try:
            # Create workflow (your existing logic)
            workflow_id = f"workflow_{int(datetime.now().timestamp())}"
            
            # Alert: Workflow started
            await self.workflow_alerts.on_workflow_start(workflow_id, workflow_type, parameters)
            
            # Your existing workflow creation logic here
            # workflow_id = self.master_agent.create_workflow(workflow_type, parameters, priority)
            
            logger.info(f"✅ Created workflow {workflow_id} with alert monitoring")
            return workflow_id
            
        except Exception as e:
            logger.error(f"❌ Failed to create workflow: {e}")
            await self.alert_system.trigger_alert(
                "task_execution_failed",
                f"Workflow creation failed: {e}",
                {"workflow_type": workflow_type, "parameters": parameters, "error": str(e)}
            )
            raise
    
    async def create_pull_request_with_alerts(self, title: str, body: str, 
                                            head: str, base: str = "main") -> Dict[str, Any]:
        """Create pull request with alert monitoring."""
        try:
            # Your existing PR creation logic here
            # result = await self.master_agent.create_pull_request(title, body, head, base)
            
            # Mock result for example
            result = {
                "success": True,
                "pr_number": 123,
                "url": "https://github.com/test/repo/pull/123"
            }
            
            if result.get("success"):
                await self.github_alerts.on_pr_created(
                    result["pr_number"],
                    title,
                    result["url"],
                    "test/repo",
                    "agent"
                )
            else:
                await self.github_alerts.on_pr_failed(
                    result.get("error", "Unknown error"),
                    {"title": title, "head": head, "base": base}
                )
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Failed to create PR: {e}")
            await self.github_alerts.on_pr_failed(str(e), {"title": title, "head": head, "base": base})
            raise

# Example usage
async def main():
    """Example of using the enhanced master agent with alerts."""
    enhanced_agent = EnhancedMasterAgent()
    
    # Create a workflow with alert monitoring
    workflow_id = await enhanced_agent.create_workflow_with_alerts(
        "pr_with_report",
        {"title": "Test PR", "body": "Test body", "head": "feature/test"}
    )
    
    # Create a pull request with alert monitoring
    pr_result = await enhanced_agent.create_pull_request_with_alerts(
        "Test Pull Request",
        "This is a test pull request",
        "feature/test"
    )
    
    # Keep running to see alerts
    try:
        while True:
            await asyncio.sleep(60)
    except KeyboardInterrupt:
        await enhanced_agent.alert_system.stop_monitoring()

if __name__ == "__main__":
    asyncio.run(main()) 