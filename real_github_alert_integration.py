#!/usr/bin/env python3
"""
Real GitHub Alert Integration
Connects alert system to actual GitHub workflows for real-time notifications.
"""

import asyncio
import logging
import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from alert_system import AlertSystem, AlertSeverity, AlertChannel

logger = logging.getLogger(__name__)

class RealGitHubAlertIntegration:
    """Real integration with GitHub workflows for live alerts."""
    
    def __init__(self):
        self.alert_system = AlertSystem()
        self.github_owner = os.getenv('GITHUB_OWNER', 'abiodun2025')
        self.github_repo = os.getenv('GITHUB_REPO', 'rag')
        self.github_token = os.getenv('GITHUB_TOKEN')
        
        logger.info(f"🔗 Real GitHub Alert Integration initialized for {self.github_owner}/{self.github_repo}")
    
    async def on_workflow_start(self, workflow_id: str, workflow_type: str, parameters: Dict[str, Any]):
        """Alert when a real workflow starts."""
        try:
            await self.alert_system.trigger_alert(
                "workflow_started",
                f"GitHub workflow {workflow_id} started: {workflow_type}",
                {
                    "workflow_id": workflow_id,
                    "workflow_type": workflow_type,
                    "parameters": parameters,
                    "repository": f"{self.github_owner}/{self.github_repo}",
                    "timestamp": datetime.now().isoformat()
                }
            )
            logger.info(f"🚀 Workflow {workflow_id} started - alert sent")
        except Exception as e:
            logger.error(f"Failed to send workflow start alert: {e}")
    
    async def on_workflow_complete(self, workflow_id: str, workflow_type: str, 
                                 success: bool, result: Optional[Dict[str, Any]] = None):
        """Alert when a real workflow completes."""
        try:
            if success:
                await self.alert_system.trigger_alert(
                    "workflow_completed",
                    f"GitHub workflow {workflow_id} completed successfully: {workflow_type}",
                    {
                        "workflow_id": workflow_id,
                        "workflow_type": workflow_type,
                        "result": result,
                        "repository": f"{self.github_owner}/{self.github_repo}",
                        "timestamp": datetime.now().isoformat()
                    }
                )
                logger.info(f"✅ Workflow {workflow_id} completed successfully - alert sent")
            else:
                await self.alert_system.trigger_alert(
                    "workflow_failed",
                    f"GitHub workflow {workflow_id} failed: {workflow_type}",
                    {
                        "workflow_id": workflow_id,
                        "workflow_type": workflow_type,
                        "result": result,
                        "repository": f"{self.github_owner}/{self.github_repo}",
                        "timestamp": datetime.now().isoformat()
                    }
                )
                logger.error(f"❌ Workflow {workflow_id} failed - alert sent")
        except Exception as e:
            logger.error(f"Failed to send workflow completion alert: {e}")
    
    async def on_pr_created(self, pr_number: int, title: str, url: str, 
                           source_branch: str, target_branch: str = "main"):
        """Alert when a real pull request is created."""
        try:
            await self.alert_system.trigger_alert(
                "pr_creation_success",
                f"Pull request #{pr_number} created: {title}",
                {
                    "pr_number": pr_number,
                    "title": title,
                    "url": url,
                    "source_branch": source_branch,
                    "target_branch": target_branch,
                    "repository": f"{self.github_owner}/{self.github_repo}",
                    "author": "agent",
                    "timestamp": datetime.now().isoformat()
                }
            )
            logger.info(f"📋 PR #{pr_number} created - alert sent")
        except Exception as e:
            logger.error(f"Failed to send PR creation alert: {e}")
    
    async def on_pr_failed(self, error: str, parameters: Dict[str, Any]):
        """Alert when pull request creation fails."""
        try:
            await self.alert_system.trigger_alert(
                "pr_creation_failed",
                f"Pull request creation failed: {error}",
                {
                    "error": error,
                    "parameters": parameters,
                    "repository": f"{self.github_owner}/{self.github_repo}",
                    "timestamp": datetime.now().isoformat()
                }
            )
            logger.error(f"❌ PR creation failed - alert sent")
        except Exception as e:
            logger.error(f"Failed to send PR failure alert: {e}")
    
    async def on_pr_merged(self, pr_number: int, title: str, merged_by: str = "agent"):
        """Alert when a pull request is merged."""
        try:
            await self.alert_system.trigger_alert(
                "pr_merged",
                f"Pull request #{pr_number} merged: {title}",
                {
                    "pr_number": pr_number,
                    "title": title,
                    "merged_by": merged_by,
                    "repository": f"{self.github_owner}/{self.github_repo}",
                    "timestamp": datetime.now().isoformat()
                }
            )
            logger.info(f"🔀 PR #{pr_number} merged - alert sent")
        except Exception as e:
            logger.error(f"Failed to send PR merge alert: {e}")
    
    async def on_task_start(self, task_id: str, task_type: str, assigned_agent: str):
        """Alert when a task starts."""
        try:
            await self.alert_system.trigger_alert(
                "task_started",
                f"Task {task_id} started on {assigned_agent}: {task_type}",
                {
                    "task_id": task_id,
                    "task_type": task_type,
                    "assigned_agent": assigned_agent,
                    "repository": f"{self.github_owner}/{self.github_repo}",
                    "timestamp": datetime.now().isoformat()
                }
            )
            logger.info(f"🔄 Task {task_id} started - alert sent")
        except Exception as e:
            logger.error(f"Failed to send task start alert: {e}")
    
    async def on_task_complete(self, task_id: str, task_type: str, 
                             success: bool, result: Optional[Dict[str, Any]] = None,
                             error: Optional[str] = None):
        """Alert when a task completes."""
        try:
            if success:
                await self.alert_system.trigger_alert(
                    "task_completed",
                    f"Task {task_id} completed successfully: {task_type}",
                    {
                        "task_id": task_id,
                        "task_type": task_type,
                        "result": result,
                        "repository": f"{self.github_owner}/{self.github_repo}",
                        "timestamp": datetime.now().isoformat()
                    }
                )
                logger.info(f"✅ Task {task_id} completed - alert sent")
            else:
                await self.alert_system.trigger_alert(
                    "task_execution_failed",
                    f"Task {task_id} failed: {error}",
                    {
                        "task_id": task_id,
                        "task_type": task_type,
                        "error": error,
                        "result": result,
                        "repository": f"{self.github_owner}/{self.github_repo}",
                        "timestamp": datetime.now().isoformat()
                    }
                )
                logger.error(f"❌ Task {task_id} failed - alert sent")
        except Exception as e:
            logger.error(f"Failed to send task completion alert: {e}")
    
    async def on_github_api_error(self, status_code: int, error_message: str, operation: str):
        """Alert when GitHub API returns an error."""
        try:
            await self.alert_system.trigger_alert(
                "github_api_error",
                f"GitHub API error ({status_code}): {error_message}",
                {
                    "status_code": status_code,
                    "error_message": error_message,
                    "operation": operation,
                    "repository": f"{self.github_owner}/{self.github_repo}",
                    "timestamp": datetime.now().isoformat()
                }
            )
            logger.error(f"🔗 GitHub API error - alert sent")
        except Exception as e:
            logger.error(f"Failed to send GitHub API error alert: {e}")

class EnhancedMasterAgentWithAlerts:
    """Enhanced master agent with real-time alert integration."""
    
    def __init__(self, mcp_bridge_url: str = "http://127.0.0.1:5000"):
        # Import your existing master agent
        try:
            from master_agent import MasterAgent
            self.master_agent = MasterAgent(mcp_bridge_url)
        except ImportError:
            logger.warning("MasterAgent not found, using mock implementation")
            self.master_agent = None
        
        # Initialize alert integration
        self.alert_integration = RealGitHubAlertIntegration()
        
        logger.info("🚀 Enhanced Master Agent with Real-Time Alerts initialized")
    
    async def create_workflow_with_alerts(self, workflow_type: str, 
                                        parameters: Dict[str, Any], 
                                        priority: int = 2) -> str:
        """Create workflow with real-time alert monitoring."""
        try:
            # Create workflow
            if self.master_agent:
                workflow_id = self.master_agent.create_workflow(workflow_type, parameters, priority)
            else:
                workflow_id = f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Alert: Workflow started
            await self.alert_integration.on_workflow_start(workflow_id, workflow_type, parameters)
            
            logger.info(f"✅ Created workflow {workflow_id} with alert monitoring")
            return workflow_id
            
        except Exception as e:
            logger.error(f"❌ Failed to create workflow: {e}")
            await self.alert_integration.on_workflow_complete(
                "unknown", workflow_type, False, {"error": str(e)}
            )
            raise
    
    async def create_pull_request_with_alerts(self, title: str, body: str, 
                                            head: str, base: str = "main") -> Dict[str, Any]:
        """Create pull request with real-time alert monitoring."""
        try:
            # Import your GitHub MCP bridge
            import requests
            
            # Create PR via MCP bridge
            response = requests.post(
                "http://127.0.0.1:5000/call",
                json={
                    "tool": "create_pull_request",
                    "arguments": {
                        "title": title,
                        "description": body,
                        "source_branch": head,
                        "target_branch": base
                    }
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get("success"):
                    # Extract PR details from response
                    pr_data = result.get("result", {})
                    pr_number = pr_data.get("number", 0)
                    pr_url = pr_data.get("html_url", "")
                    
                    # Alert: PR created successfully
                    await self.alert_integration.on_pr_created(
                        pr_number, title, pr_url, head, base
                    )
                    
                    logger.info(f"✅ Pull request #{pr_number} created with alert monitoring")
                    return result
                else:
                    # Alert: PR creation failed
                    await self.alert_integration.on_pr_failed(
                        result.get("error", "Unknown error"),
                        {"title": title, "head": head, "base": base}
                    )
                    
                    logger.error(f"❌ Pull request creation failed: {result.get('error')}")
                    return result
            else:
                # Alert: HTTP error
                await self.alert_integration.on_github_api_error(
                    response.status_code, f"HTTP {response.status_code}", "create_pull_request"
                )
                
                logger.error(f"❌ HTTP error creating PR: {response.status_code}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            logger.error(f"❌ Failed to create PR: {e}")
            await self.alert_integration.on_pr_failed(str(e), {"title": title, "head": head, "base": base})
            raise
    
    async def monitor_workflow_with_alerts(self, workflow_id: str):
        """Monitor workflow with real-time alerts."""
        try:
            if not self.master_agent:
                logger.warning("MasterAgent not available for monitoring")
                return
            
            # Get workflow status
            status = self.master_agent.get_workflow_status(workflow_id)
            
            if "error" not in status:
                workflow_status = status.get("workflow", {}).get("status", "unknown")
                
                if workflow_status == "completed":
                    await self.alert_integration.on_workflow_complete(
                        workflow_id, "unknown", True, status
                    )
                elif workflow_status == "failed":
                    await self.alert_integration.on_workflow_complete(
                        workflow_id, "unknown", False, status
                    )
                
                logger.info(f"📊 Workflow {workflow_id} status: {workflow_status}")
            else:
                logger.error(f"❌ Failed to get workflow status: {status.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ Failed to monitor workflow: {e}")

# Example usage for real GitHub workflows
async def main():
    """Example of using the enhanced master agent with real GitHub alerts."""
    enhanced_agent = EnhancedMasterAgentWithAlerts()
    
    # Create a real workflow with alerts
    workflow_id = await enhanced_agent.create_workflow_with_alerts(
        "pr_with_report",
        {
            "title": "Real GitHub Integration Test",
            "description": "Testing real-time alerts with actual GitHub workflows",
            "source_branch": "feature/real-alerts",
            "target_branch": "main"
        }
    )
    
    print(f"🎉 Created workflow {workflow_id} with real-time alerts!")
    print("Check your email for workflow start notifications.")
    
    # Create a real pull request with alerts
    pr_result = await enhanced_agent.create_pull_request_with_alerts(
        "Real GitHub Alert Integration",
        "This PR was created with real-time alert monitoring",
        "feature/real-alerts"
    )
    
    if pr_result.get("success"):
        print("🎉 Pull request created with real-time alerts!")
        print("Check your email for PR creation notifications.")
    else:
        print(f"❌ Pull request creation failed: {pr_result.get('error')}")

if __name__ == "__main__":
    asyncio.run(main()) 