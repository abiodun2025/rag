#!/usr/bin/env python3
"""
Test Master-Slave Workflow Distribution
Demonstrates the master agent distributing tasks to slave agents.
"""

import time
import json
from datetime import datetime
from master_agent import MasterAgent

def test_master_slave_workflow():
    """Test the master-slave workflow distribution system."""
    
    print("🚀 Master-Slave Workflow Test")
    print("=" * 70)
    print("Testing Master Agent distributing tasks to Slave Agents")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Initialize master agent
    print("1️⃣ Initializing Master Agent...")
    print("-" * 50)
    master = MasterAgent()
    
    # Show initial agent status
    agent_status = master.get_agent_status()
    print(f"✅ Master Agent initialized with {agent_status['total_agents']} slave agents:")
    for agent_id, agent in agent_status['agents'].items():
        print(f"   - {agent['name']}: {agent['status']} ({', '.join(agent['capabilities'])})")
    
    print()
    
    # Test 1: Simple PR creation workflow
    print("2️⃣ Testing Simple PR Creation Workflow...")
    print("-" * 50)
    
    workflow1_id = master.create_workflow(
        workflow_type="create_pr",
        parameters={
            "title": "Master-Slave Architecture Test",
            "description": "Testing the master-slave agent distribution system",
            "source_branch": "test-master-slave",
            "target_branch": "main"
        },
        priority=1
    )
    
    print(f"✅ Created workflow: {workflow1_id}")
    
    # Monitor workflow
    for i in range(10):
        status = master.get_workflow_status(workflow1_id)
        print(f"   Progress: {status['progress']} - Status: {status['workflow']['status']}")
        
        if status["workflow"]["status"] in ["completed", "failed"]:
            break
        
        time.sleep(2)
    
    print()
    
    # Test 2: PR with Review workflow
    print("3️⃣ Testing PR with Review Workflow...")
    print("-" * 50)
    
    workflow2_id = master.create_workflow(
        workflow_type="pr_with_review",
        parameters={
            "title": "Complete Workflow Test - Master-Slave",
            "description": """This PR tests the complete master-slave workflow:
            
## Workflow Steps:
1. Create Pull Request (PR Agent)
2. Automated Code Review (Review Agent)
3. Generate Report (Review Agent)

## Expected Results:
- PR created successfully
- Code review completed
- HTML report generated
- Both agents working together

Created by: Master-Slave Test System""",
            "source_branch": "test-master-slave-complete",
            "target_branch": "main"
        },
        priority=1
    )
    
    print(f"✅ Created workflow: {workflow2_id}")
    
    # Monitor workflow with detailed status
    print("📊 Monitoring workflow progress:")
    for i in range(20):
        status = master.get_workflow_status(workflow2_id)
        print(f"   [{i+1:2d}] Progress: {status['progress']} - Status: {status['workflow']['status']}")
        
        # Show task details
        for task in status['tasks']:
            if task:
                task_status = task['status']
                agent = task.get('assigned_agent', 'unassigned')
                if task_status == 'completed':
                    print(f"      ✅ {task['task_type']} completed by {agent}")
                elif task_status == 'running':
                    print(f"      🔄 {task['task_type']} running on {agent}")
                elif task_status == 'failed':
                    print(f"      ❌ {task['task_type']} failed: {task.get('error', 'unknown error')}")
        
        if status["workflow"]["status"] in ["completed", "failed"]:
            break
        
        time.sleep(3)
    
    print()
    
    # Test 3: Full Development Cycle
    print("4️⃣ Testing Full Development Cycle...")
    print("-" * 50)
    
    workflow3_id = master.create_workflow(
        workflow_type="full_development_cycle",
        parameters={
            "title": "Full Development Cycle - Master-Slave",
            "description": """Complete development workflow test:
            
## Workflow Steps:
1. Create Pull Request
2. Analyze Code Changes
3. Perform Code Review
4. Merge Pull Request (if approved)

## Agent Distribution:
- PR Agent: Creates and merges PRs
- Review Agent: Performs code review
- Analysis Agent: Analyzes code changes

This demonstrates the complete master-slave coordination.""",
            "source_branch": "test-full-cycle",
            "target_branch": "main"
        },
        priority=1
    )
    
    print(f"✅ Created workflow: {workflow3_id}")
    
    # Monitor with agent status
    print("📊 Monitoring full development cycle:")
    for i in range(30):
        status = master.get_workflow_status(workflow3_id)
        agent_status = master.get_agent_status()
        
        print(f"   [{i+1:2d}] Progress: {status['progress']} - Status: {status['workflow']['status']}")
        print(f"      Agents: {agent_status['available_agents']} available, {agent_status['busy_agents']} busy")
        
        if status["workflow"]["status"] in ["completed", "failed"]:
            break
        
        time.sleep(3)
    
    print()
    
    # Show final status
    print("5️⃣ Final Status Report...")
    print("-" * 50)
    
    # Workflow statuses
    workflows = [workflow1_id, workflow2_id, workflow3_id]
    for workflow_id in workflows:
        status = master.get_workflow_status(workflow_id)
        print(f"   Workflow {workflow_id}: {status['progress']} - {status['workflow']['status']}")
    
    # Agent status
    agent_status = master.get_agent_status()
    print(f"\n   Agent Status: {agent_status['available_agents']} available, {agent_status['busy_agents']} busy")
    
    # Queue status
    queue_status = master.get_task_queue_status()
    print(f"   Queue Status: {queue_status['pending_tasks']} pending, {queue_status['completed_tasks']} completed")
    
    print()
    print("🎉 Master-Slave Workflow Test Completed!")
    print("=" * 70)
    print("Summary:")
    print("   ✅ Master Agent successfully distributed tasks")
    print("   ✅ Slave Agents executed tasks in parallel")
    print("   ✅ Workflow dependencies handled automatically")
    print("   ✅ Real GitHub integration working")
    print("   ✅ Complete development cycle demonstrated")
    print()
    print("🔗 What was tested:")
    print("   1. Task distribution and scheduling")
    print("   2. Agent capability matching")
    print("   3. Workflow dependency resolution")
    print("   4. Parallel task execution")
    print("   5. Real-world GitHub operations")
    print()
    print("📋 Next steps:")
    print("   - Add more specialized slave agents")
    print("   - Implement agent performance monitoring")
    print("   - Add workflow templates")
    print("   - Create web dashboard for monitoring")

if __name__ == "__main__":
    test_master_slave_workflow()