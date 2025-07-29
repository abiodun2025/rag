#!/usr/bin/env python3
"""
Master Agent for Workflow Distribution
Coordinates and distributes tasks to slave agents for PR creation and code review.
"""

import os
import json
import requests
import logging
import uuid
import threading
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path
import queue

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class WorkflowTask:
    """A single workflow task to be executed by a slave agent."""
    task_id: str
    task_type: str  # "create_pr", "code_review", "merge_pr", "analyze_code"
    priority: int  # 1=high, 2=medium, 3=low
    parameters: Dict[str, Any]
    status: str  # "pending", "running", "completed", "failed"
    assigned_agent: Optional[str] = None
    created_at: str = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    result: Optional[Dict] = None
    error: Optional[str] = None

@dataclass
class SlaveAgent:
    """Information about a slave agent."""
    agent_id: str
    name: str
    capabilities: List[str]  # ["create_pr", "code_review", "merge_pr", "analyze_code"]
    status: str  # "available", "busy", "offline"
    current_task: Optional[str] = None
    last_heartbeat: str = None
    performance_score: float = 1.0

class MasterAgent:
    """Master agent that coordinates workflow distribution to slave agents."""
    
    def __init__(self, mcp_bridge_url: str = "http://127.0.0.1:5000"):
        self.mcp_bridge_url = mcp_bridge_url
        self.tasks = {}  # task_id -> WorkflowTask
        self.slave_agents = {}  # agent_id -> SlaveAgent
        self.task_queue = queue.PriorityQueue()
        self.workflow_history = []
        
        # Initialize slave agents
        self._initialize_slave_agents()
        
        # Start background task manager
        self.running = True
        self.task_manager_thread = threading.Thread(target=self._task_manager_loop)
        self.task_manager_thread.daemon = True
        self.task_manager_thread.start()
        
        logger.info("🚀 Master Agent initialized and ready to distribute workflows")
    
    def _initialize_slave_agents(self):
        """Initialize the available slave agents with clear separation of concerns."""
        # PR Agent - Only creates pull requests
        self.slave_agents["pr_agent"] = SlaveAgent(
            agent_id="pr_agent",
            name="Pull Request Agent",
            capabilities=["create_pr", "merge_pr", "list_prs"],
            status="available",
            last_heartbeat=datetime.now().isoformat()
        )
        
        # Report Agent - Only generates reports in local URLs
        self.slave_agents["report_agent"] = SlaveAgent(
            agent_id="report_agent",
            name="Report Agent",
            capabilities=["generate_report", "create_local_url", "save_report"],
            status="available",
            last_heartbeat=datetime.now().isoformat()
        )
        
        # Branch Agent - Only handles branch operations
        self.slave_agents["branch_agent"] = SlaveAgent(
            agent_id="branch_agent",
            name="Branch Agent",
            capabilities=["create_branch", "create_branch_from_base", "checkout_branch", "push_branch", "delete_branch", "list_branches"],
            status="available",
            last_heartbeat=datetime.now().isoformat()
        )
        
        logger.info(f"✅ Initialized {len(self.slave_agents)} slave agents with separation of concerns")
        logger.info("   - PR Agent: Creates pull requests")
        logger.info("   - Report Agent: Generates local URL reports")
        logger.info("   - Branch Agent: Handles branch operations")
    
    def create_workflow(self, workflow_type: str, parameters: Dict[str, Any], priority: int = 2) -> str:
        """Create a new workflow with multiple tasks."""
        workflow_id = f"workflow_{uuid.uuid4().hex[:8]}"
        
        logger.info(f"🔧 Creating workflow {workflow_id}: {workflow_type}")
        
        if workflow_type == "pr_with_report":
            # Create PR and generate a report
            tasks = [
                WorkflowTask(
                    task_id=f"{workflow_id}_create_pr",
                    task_type="create_pr",
                    priority=priority,
                    parameters=parameters,
                    status="pending",
                    created_at=datetime.now().isoformat()
                ),
                WorkflowTask(
                    task_id=f"{workflow_id}_generate_report",
                    task_type="generate_report",
                    priority=priority + 1,
                    parameters={"pr_number": "{{PR_NUMBER}}"},
                    status="pending",
                    created_at=datetime.now().isoformat()
                )
            ]
        elif workflow_type == "create_branch":
            # Create a new branch and push it to GitHub
            tasks = [
                WorkflowTask(
                    task_id=f"{workflow_id}_create_branch",
                    task_type="create_branch",
                    priority=priority,
                    parameters=parameters,
                    status="pending",
                    created_at=datetime.now().isoformat()
                ),
                WorkflowTask(
                    task_id=f"{workflow_id}_push_branch",
                    task_type="push_branch",
                    priority=priority + 1,
                    parameters=parameters,
                    status="pending",
                    created_at=datetime.now().isoformat()
                )
            ]
        elif workflow_type == "branch_and_pr":
            # Create branch and then create PR
            tasks = [
                WorkflowTask(
                    task_id=f"{workflow_id}_create_branch",
                    task_type="create_branch",
                    priority=priority,
                    parameters=parameters,
                    status="pending",
                    created_at=datetime.now().isoformat()
                ),
                WorkflowTask(
                    task_id=f"{workflow_id}_create_pr",
                    task_type="create_pr",
                    priority=priority + 1,
                    parameters=parameters,
                    status="pending",
                    created_at=datetime.now().isoformat()
                )
            ]
        elif workflow_type == "full_branch_workflow":
            # Complete branch workflow: create branch, push, create PR, generate report
            tasks = [
                WorkflowTask(
                    task_id=f"{workflow_id}_create_branch",
                    task_type="create_branch",
                    priority=priority,
                    parameters=parameters,
                    status="pending",
                    created_at=datetime.now().isoformat()
                ),
                WorkflowTask(
                    task_id=f"{workflow_id}_push_branch",
                    task_type="push_branch",
                    priority=priority + 1,
                    parameters=parameters,
                    status="pending",
                    created_at=datetime.now().isoformat()
                ),
                WorkflowTask(
                    task_id=f"{workflow_id}_create_pr",
                    task_type="create_pr",
                    priority=priority + 2,
                    parameters=parameters,
                    status="pending",
                    created_at=datetime.now().isoformat()
                ),
                WorkflowTask(
                    task_id=f"{workflow_id}_generate_report",
                    task_type="generate_report",
                    priority=priority + 3,
                    parameters={"pr_number": "{{PR_NUMBER}}"},
                    status="pending",
                    created_at=datetime.now().isoformat()
                )
            ]
        else:
            raise ValueError(f"Unknown workflow type: {workflow_type}")
        
        # Add tasks to queue and tracking
        for task in tasks:
            self.tasks[task.task_id] = task
            self.task_queue.put((task.priority, task.task_id))
        
        # Store workflow
        workflow = {
            "workflow_id": workflow_id,
            "workflow_type": workflow_type,
            "tasks": [task.task_id for task in tasks],
            "status": "created",
            "created_at": datetime.now().isoformat(),
            "parameters": parameters
        }
        self.workflow_history.append(workflow)
        
        logger.info(f"✅ Created workflow {workflow_id} with {len(tasks)} tasks")
        return workflow_id
    
    def _task_manager_loop(self):
        """Background loop that manages task distribution."""
        while self.running:
            try:
                if not self.task_queue.empty():
                    priority, task_id = self.task_queue.get()
                    task = self.tasks.get(task_id)
                    
                    if task and task.status == "pending":
                        self._assign_task_to_agent(task)
                
                # Update agent statuses
                self._update_agent_statuses()
                
                time.sleep(1)  # Check every second
                
            except Exception as e:
                logger.error(f"❌ Task manager error: {e}")
                time.sleep(5)
    
    def _assign_task_to_agent(self, task: WorkflowTask):
        """Assign a task to the best available agent."""
        available_agents = [
            agent for agent in self.slave_agents.values()
            if agent.status == "available" and task.task_type in agent.capabilities
        ]
        
        if not available_agents:
            logger.warning(f"⚠️ No available agents for task {task.task_id}")
            return
        
        # Select best agent based on performance score and current load
        best_agent = max(available_agents, key=lambda a: a.performance_score)
        
        # Update task and agent status
        task.status = "running"
        task.assigned_agent = best_agent.agent_id
        task.started_at = datetime.now().isoformat()
        best_agent.status = "busy"
        best_agent.current_task = task.task_id
        
        logger.info(f"📋 Assigned task {task.task_id} to {best_agent.name}")
        
        # Execute task in background
        threading.Thread(target=self._execute_task, args=(task,)).start()
    
    def _execute_task(self, task: WorkflowTask):
        """Execute a task using the MCP bridge."""
        try:
            logger.info(f"🚀 Executing task {task.task_id} via {task.assigned_agent}")
            
            # Map task types to MCP tools
            tool_mapping = {
                "create_pr": "create_pull_request",
                "merge_pr": "merge_pull_request", 
                "list_prs": "list_pull_requests",
                "generate_report": "generate_report",
                "create_local_url": "create_local_url",
                "save_report": "save_report",
                "create_branch": "create_branch",
                "create_branch_from_base": "create_branch_from_base",
                "checkout_branch": "checkout_branch",
                "push_branch": "push_branch",
                "delete_branch": "delete_branch",
                "list_branches": "list_branches"
            }
            
            tool_name = tool_mapping.get(task.task_type, task.task_type)
            
            # Execute via MCP bridge
            response = requests.post(
                f"{self.mcp_bridge_url}/call",
                json={
                    "tool": tool_name,
                    "arguments": task.parameters
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                task.status = "completed"
                task.result = result
                task.completed_at = datetime.now().isoformat()
                
                logger.info(f"✅ Task {task.task_id} completed successfully")
                
                # Handle task dependencies
                self._handle_task_dependencies(task)
                
            else:
                task.status = "failed"
                task.error = f"HTTP {response.status_code}"
                logger.error(f"❌ Task {task.task_id} failed: HTTP {response.status_code}")
            
        except Exception as e:
            task.status = "failed"
            task.error = str(e)
            logger.error(f"❌ Task {task.task_id} failed: {e}")
        
        finally:
            # Free up the agent
            if task.assigned_agent:
                agent = self.slave_agents.get(task.assigned_agent)
                if agent:
                    agent.status = "available"
                    agent.current_task = None
    
    def _handle_task_dependencies(self, completed_task: WorkflowTask):
        """Handle dependencies between tasks (e.g., PR number from create_pr to review_pr)."""
        for task_id, task in self.tasks.items():
            if task.status == "pending" and "{{PR_NUMBER}}" in str(task.parameters):
                # This task is waiting for a PR number
                if completed_task.task_type == "create_pr" and completed_task.result:
                    pr_number = completed_task.result.get("pr_id") or completed_task.result.get("pr_number")
                    if pr_number:
                        # Update the waiting task's parameters
                        task.parameters["pr_number"] = pr_number
                        # Remove the wait flag
                        task.parameters.pop("wait_for_pr", None)
                        task.parameters.pop("wait_for_approval", None)
                        
                        logger.info(f"🔗 Updated task {task_id} with PR number {pr_number}")
    
    def _update_agent_statuses(self):
        """Update agent statuses and performance scores."""
        for agent in self.slave_agents.values():
            agent.last_heartbeat = datetime.now().isoformat()
    
    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get the status of a workflow."""
        workflow = next((w for w in self.workflow_history if w["workflow_id"] == workflow_id), None)
        if not workflow:
            return {"error": "Workflow not found"}
        
        tasks = [self.tasks.get(task_id) for task_id in workflow["tasks"]]
        completed_tasks = [t for t in tasks if t and t.status == "completed"]
        failed_tasks = [t for t in tasks if t and t.status == "failed"]
        
        if failed_tasks:
            workflow["status"] = "failed"
        elif len(completed_tasks) == len(tasks):
            workflow["status"] = "completed"
        else:
            workflow["status"] = "running"
        
        return {
            "workflow": workflow,
            "tasks": [t.__dict__ if t else None for t in tasks],
            "progress": f"{len(completed_tasks)}/{len(tasks)} tasks completed"
        }
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all slave agents."""
        return {
            "agents": {agent_id: agent.__dict__ for agent_id, agent in self.slave_agents.items()},
            "total_agents": len(self.slave_agents),
            "available_agents": len([a for a in self.slave_agents.values() if a.status == "available"]),
            "busy_agents": len([a for a in self.slave_agents.values() if a.status == "busy"])
        }
    
    def get_task_queue_status(self) -> Dict[str, Any]:
        """Get status of the task queue."""
        pending_tasks = [t for t in self.tasks.values() if t.status == "pending"]
        running_tasks = [t for t in self.tasks.values() if t.status == "running"]
        completed_tasks = [t for t in self.tasks.values() if t.status == "completed"]
        failed_tasks = [t for t in self.tasks.values() if t.status == "failed"]
        
        return {
            "queue_size": self.task_queue.qsize(),
            "pending_tasks": len(pending_tasks),
            "running_tasks": len(running_tasks),
            "completed_tasks": len(completed_tasks),
            "failed_tasks": len(failed_tasks),
            "total_tasks": len(self.tasks)
        }
    
    def stop(self):
        """Stop the master agent."""
        self.running = False
        logger.info("🛑 Master Agent stopped")

def main():
    """Main function to run the master agent."""
    master = MasterAgent()
    
    try:
        # Example: Create a workflow
        workflow_id = master.create_workflow(
            workflow_type="pr_with_report",
            parameters={
                "title": "Test Master-Slave Workflow",
                "description": "Testing the master-slave agent architecture",
                "source_branch": "test-master-slave",
                "target_branch": "main"
            },
            priority=1
        )
        
        print(f"🚀 Created workflow: {workflow_id}")
        
        # Monitor the workflow
        while True:
            status = master.get_workflow_status(workflow_id)
            print(f"📊 Workflow Status: {status['progress']}")
            
            if status["workflow"]["status"] in ["completed", "failed"]:
                break
            
            time.sleep(5)
        
        print("✅ Workflow completed!")
        
    except KeyboardInterrupt:
        print("\n🛑 Stopping master agent...")
    finally:
        master.stop()

if __name__ == "__main__":
    main()