#!/usr/bin/env python3
"""
Create a Pull Request Now
Quick script to create a PR using the master agent.
"""

import time
from master_agent import MasterAgent

def create_pull_request():
    """Create a pull request using the master agent."""
    print("🚀 Creating Pull Request with Master Agent")
    print("=" * 50)
    
    try:
        # Initialize master agent
        print("1️⃣ Initializing Master Agent...")
        master = MasterAgent()
        
        # Show agent status
        agent_status = master.get_agent_status()
        print(f"✅ Master Agent initialized with {agent_status['total_agents']} slave agents")
        
        # Create PR workflow
        print("\n2️⃣ Creating Pull Request...")
        workflow_id = master.create_workflow(
            workflow_type="pr_with_review",
            parameters={
                "title": "Master-Slave System Implementation",
                "description": """# Master-Slave Workflow System

This PR implements the master-slave workflow distribution system.

## Features
- ✅ Master Agent coordination
- ✅ Slave Agent task distribution
- ✅ Automated PR creation
- ✅ Code review automation
- ✅ Real-time monitoring

## Workflow Steps
1. Create Pull Request (PR Agent)
2. Automated Code Review (Review Agent)
3. Generate Report (Review Agent)

Created by: Master Agent System""",
                "source_branch": "master-slave-implementation",
                "target_branch": "main"
            },
            priority=1
        )
        
        print(f"✅ Created workflow: {workflow_id}")
        
        # Monitor the workflow
        print("\n3️⃣ Monitoring workflow progress...")
        for i in range(30):
            status = master.get_workflow_status(workflow_id)
            print(f"   [{i+1:2d}] Progress: {status['progress']} - Status: {status['workflow']['status']}")
            
            # Show task details
            for task in status['tasks']:
                if task:
                    task_status = task['status']
                    agent = task.get('assigned_agent', 'unassigned')
                    if task_status == 'completed':
                        print(f"      ✅ {task['task_type']} completed by {agent}")
                        if task['result'] and task['result'].get('success'):
                            if task['task_type'] == 'create_pr':
                                pr_number = task['result'].get('pr_id') or task['result'].get('pr_number')
                                pr_url = task['result'].get('url') or task['result'].get('html_url')
                                print(f"         PR #{pr_number}: {pr_url}")
                            elif task['task_type'] == 'code_review':
                                report_url = task['result'].get('report_url')
                                score = task['result'].get('overall_score')
                                print(f"         Score: {score}/100")
                                print(f"         Report: {report_url}")
                    elif task_status == 'running':
                        print(f"      🔄 {task['task_type']} running on {agent}")
                    elif task_status == 'failed':
                        print(f"      ❌ {task['task_type']} failed: {task.get('error', 'unknown error')}")
            
            if status["workflow"]["status"] in ["completed", "failed"]:
                break
            
            time.sleep(3)
        
        # Final status
        final_status = master.get_workflow_status(workflow_id)
        print(f"\n🎉 Workflow {final_status['workflow']['status']}!")
        print(f"   Final Progress: {final_status['progress']}")
        
        # Show results
        for task in final_status['tasks']:
            if task and task['status'] == 'completed' and task['result']:
                if task['task_type'] == 'create_pr':
                    pr_number = task['result'].get('pr_id') or task['result'].get('pr_number')
                    pr_url = task['result'].get('url') or task['result'].get('html_url')
                    print(f"\n🔗 Pull Request Created:")
                    print(f"   PR #{pr_number}: {pr_url}")
                elif task['task_type'] == 'code_review':
                    report_url = task['result'].get('report_url')
                    score = task['result'].get('overall_score')
                    print(f"\n📊 Code Review Completed:")
                    print(f"   Score: {score}/100")
                    print(f"   Report: {report_url}")
        
        print("\n✅ Pull Request creation completed!")
        
    except Exception as e:
        print(f"❌ Failed to create pull request: {e}")
    finally:
        if 'master' in locals():
            master.stop()

if __name__ == "__main__":
    create_pull_request()