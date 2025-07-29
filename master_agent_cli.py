#!/usr/bin/env python3
"""
Master Agent CLI Interface
Command-line interface for the master agent to create and monitor workflows.
"""

import sys
import time
import json
from datetime import datetime
from master_agent import MasterAgent

def print_banner():
    """Print the CLI banner."""
    print("🚀 Master Agent CLI")
    print("=" * 50)
    print("Distribute workflows to slave agents")
    print("Type 'help' for available commands")
    print("=" * 50)

def print_help():
    """Print help information."""
    print("\n📋 Available Commands:")
    print("  create <type> <title> <branch>  - Create a new workflow")
    print("  interactive                      - Create workflow step by step")
    print("  status <workflow_id>            - Check workflow status")
    print("  agents                          - Show agent status")
    print("  queue                           - Show task queue status")
    print("  monitor <workflow_id>           - Monitor workflow in real-time")
    print("  list                            - List all workflows")
    print("  help                            - Show this help")
    print("  quit                            - Exit the CLI")
    print("\n📋 Workflow Types (Separation of Concerns):")
    print("  create_pr                       - PR Agent only (creates PR)")
    print("  pr_with_report                  - PR Agent + Report Agent")
    print("  full_development_cycle          - PR Agent + Report Agent + Merge")
    print("\n📋 Agent Responsibilities:")
    print("  - PR Agent: Creates pull requests")
    print("  - Report Agent: Generates local URL reports")
    print("  - Branch Agent: Handles branch operations")
    print("\n📋 Examples:")
    print("  interactive                     - Step-by-step workflow creation")
    print("  create pr_with_report 'My Feature' feature-branch")
    print("  create create_pr 'Simple PR' simple-branch")
    print("  create full_development_cycle 'Bug Fix' bugfix-branch")
    print("  status workflow_abc123")
    print("  monitor workflow_abc123")

def create_workflow(master, workflow_type, title, branch):
    """Create a new workflow."""
    try:
        if workflow_type == "create_pr":
            parameters = {
                "title": title,
                "description": f"Created by Master Agent CLI\nBranch: {branch}",
                "source_branch": branch,
                "target_branch": "main"
            }
        elif workflow_type == "pr_with_report":
            parameters = {
                "title": title,
                "description": f"""Created by Master Agent CLI

## Description
This PR was created using the master-slave workflow system.

## Branch
Source: {branch}
Target: main

## Workflow Steps
1. Create Pull Request (PR Agent)
2. Generate Report (Report Agent)

Created at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}""",
                "source_branch": branch,
                "target_branch": "main"
            }
        elif workflow_type == "full_development_cycle":
            parameters = {
                "title": title,
                "description": f"""Complete Development Cycle - Master Agent CLI

## Description
This PR demonstrates the complete master-slave development workflow.

## Branch
Source: {branch}
Target: main

## Workflow Steps
1. Create Pull Request (PR Agent)
2. Analyze Code Changes (Analysis Agent)
3. Perform Code Review (Review Agent)
4. Merge Pull Request (PR Agent)

## Agent Distribution
- PR Agent: Creates and merges PRs
- Review Agent: Performs code review
- Analysis Agent: Analyzes code changes

Created at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}""",
                "source_branch": branch,
                "target_branch": "main"
            }
        else:
            parameters = {
                "title": title,
                "description": f"Created by Master Agent CLI\nBranch: {branch}",
                "source_branch": branch,
                "target_branch": "main"
            }
        
        workflow_id = master.create_workflow(workflow_type, parameters)
        
        print(f"\n✅ Created workflow: {workflow_id}")
        print(f"   Type: {workflow_type}")
        print(f"   Title: {title}")
        print(f"   Branch: {branch}")
        
        # Wait a moment for tasks to start
        print(f"\n⏳ Starting workflow execution...")
        time.sleep(2)
        
        # Check initial status
        status = master.get_workflow_status(workflow_id)
        if "error" not in status:
            print(f"   Status: {status['workflow']['status']}")
            print(f"   Progress: {status['progress']}")
        
        print(f"\n🎉 Workflow is now running in the background!")
        print(f"   Use 'monitor {workflow_id}' to watch progress")
        print(f"   Use 'status {workflow_id}' to check status")
        print(f"   Use 'agents' to see agent status")
        print(f"\n🤖 Master Agent> Ready for next command!")
        
        return workflow_id
        
    except Exception as e:
        print(f"❌ Failed to create workflow: {e}")
        return None

def create_workflow_interactive(master):
    """Create a new workflow with interactive prompts."""
    print("\n🚀 Interactive Workflow Creation")
    print("=" * 40)
    
    # Step 1: Choose workflow type
    print("\n📋 Step 1: Choose Workflow Type")
    print("Available types:")
    print("  1. create_pr          - PR Agent only (creates PR)")
    print("  2. pr_with_report     - PR Agent + Report Agent")
    print("  3. full_development_cycle - PR Agent + Report Agent + Merge")
    
    while True:
        choice = input("\nEnter your choice (1-3): ").strip()
        workflow_types = {
            "1": "create_pr",
            "2": "pr_with_report", 
            "3": "full_development_cycle"
        }
        
        if choice in workflow_types:
            workflow_type = workflow_types[choice]
            print(f"✅ Selected: {workflow_type}")
            break
        else:
            print("❌ Invalid choice. Please enter 1-3.")
    
    # Step 2: Enter title
    print(f"\n📋 Step 2: Enter Pull Request Title")
    print(f"Workflow: {workflow_type}")
    
    while True:
        title = input("Enter title: ").strip()
        if title:
            print(f"✅ Title: {title}")
            break
        else:
            print("❌ Title cannot be empty. Please try again.")
    
    # Step 3: Enter branch name
    print(f"\n📋 Step 3: Enter Branch Name")
    print(f"Workflow: {workflow_type}")
    print(f"Title: {title}")
    
    while True:
        branch = input("Enter branch name: ").strip()
        if branch:
            print(f"✅ Branch: {branch}")
            break
        else:
            print("❌ Branch name cannot be empty. Please try again.")
    
    # Confirm and create
    print(f"\n🎯 Confirm Workflow Creation:")
    print(f"  Type: {workflow_type}")
    print(f"  Title: {title}")
    print(f"  Branch: {branch}")
    
    confirm = input("\nCreate this workflow? (y/n): ").strip().lower()
    if confirm in ['y', 'yes']:
        try:
            workflow_id = create_workflow(master, workflow_type, title, branch)
            print(f"\n✅ Workflow created successfully!")
            print(f"   Workflow ID: {workflow_id}")
            print(f"   Monitor with: monitor {workflow_id}")
            
            # Wait a moment for tasks to start
            print(f"\n⏳ Starting workflow execution...")
            time.sleep(2)
            
            # Check initial status
            status = master.get_workflow_status(workflow_id)
            if "error" not in status:
                print(f"   Status: {status['workflow']['status']}")
                print(f"   Progress: {status['progress']}")
            
            print(f"\n🎉 Workflow is now running in the background!")
            print(f"   Use 'monitor {workflow_id}' to watch progress")
            print(f"   Use 'status {workflow_id}' to check status")
            print(f"   Use 'agents' to see agent status")
            print(f"\n🤖 Master Agent> Ready for next command!")
            
            return workflow_id
        except Exception as e:
            print(f"\n❌ Failed to create workflow: {e}")
            return None
    else:
        print("\n❌ Workflow creation cancelled.")
        return None

def show_workflow_status(master, workflow_id):
    """Show workflow status."""
    try:
        status = master.get_workflow_status(workflow_id)
        
        if "error" in status:
            print(f"❌ {status['error']}")
            return
        
        workflow = status["workflow"]
        print(f"\n📊 Workflow Status: {workflow_id}")
        print(f"   Type: {workflow['workflow_type']}")
        print(f"   Status: {workflow['status']}")
        print(f"   Progress: {status['progress']}")
        print(f"   Created: {workflow['created_at']}")
        
        print(f"\n📋 Tasks:")
        for task in status['tasks']:
            if task:
                status_icon = {
                    'pending': '⏳',
                    'running': '🔄',
                    'completed': '✅',
                    'failed': '❌'
                }.get(task['status'], '❓')
                
                print(f"   {status_icon} {task['task_type']}: {task['status']}")
                if task['assigned_agent']:
                    print(f"      Agent: {task['assigned_agent']}")
                if task['error']:
                    print(f"      Error: {task['error']}")
                if task['result'] and task['result'].get('success'):
                    if task['task_type'] == 'create_pr':
                        pr_number = task['result'].get('pr_id') or task['result'].get('pr_number')
                        pr_url = task['result'].get('url') or task['result'].get('html_url')
                        print(f"      PR #{pr_number}: {pr_url}")
                    elif task['task_type'] == 'code_review':
                        report_url = task['result'].get('report_url')
                        score = task['result'].get('overall_score')
                        print(f"      Score: {score}/100")
                        print(f"      Report: {report_url}")
        
    except Exception as e:
        print(f"❌ Failed to get workflow status: {e}")

def show_agent_status(master):
    """Show agent status."""
    try:
        status = master.get_agent_status()
        
        print(f"\n🤖 Agent Status ({status['total_agents']} total)")
        print(f"   Available: {status['available_agents']}")
        print(f"   Busy: {status['busy_agents']}")
        
        print(f"\n📋 Agents:")
        for agent_id, agent in status['agents'].items():
            status_icon = {
                'available': '🟢',
                'busy': '🟡',
                'offline': '🔴'
            }.get(agent['status'], '❓')
            
            print(f"   {status_icon} {agent['name']}: {agent['status']}")
            if agent['current_task']:
                print(f"      Current task: {agent['current_task']}")
            print(f"      Capabilities: {', '.join(agent['capabilities'])}")
        
    except Exception as e:
        print(f"❌ Failed to get agent status: {e}")

def show_queue_status(master):
    """Show task queue status."""
    try:
        status = master.get_task_queue_status()
        
        print(f"\n📋 Task Queue Status")
        print(f"   Queue size: {status['queue_size']}")
        print(f"   Pending: {status['pending_tasks']}")
        print(f"   Running: {status['running_tasks']}")
        print(f"   Completed: {status['completed_tasks']}")
        print(f"   Failed: {status['failed_tasks']}")
        print(f"   Total: {status['total_tasks']}")
        
    except Exception as e:
        print(f"❌ Failed to get queue status: {e}")

def monitor_workflow(master, workflow_id):
    """Monitor workflow in real-time."""
    try:
        print(f"\n📊 Monitoring workflow: {workflow_id}")
        print("Press Ctrl+C to stop monitoring")
        print("-" * 50)
        
        while True:
            status = master.get_workflow_status(workflow_id)
            
            if "error" in status:
                print(f"❌ {status['error']}")
                break
            
            workflow = status["workflow"]
            timestamp = datetime.now().strftime('%H:%M:%S')
            
            # Clear line and print status
            print(f"\r[{timestamp}] {status['progress']} - {workflow['status']}", end='', flush=True)
            
            if workflow['status'] in ['completed', 'failed']:
                print(f"\n✅ Workflow {workflow['status']}!")
                break
            
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\n⏹️ Monitoring stopped")
    except Exception as e:
        print(f"\n❌ Monitoring failed: {e}")

def list_workflows(master):
    """List all workflows."""
    try:
        workflows = master.workflow_history
        
        if not workflows:
            print("📋 No workflows found")
            return
        
        print(f"\n📋 Workflows ({len(workflows)} total):")
        for workflow in workflows:
            status = master.get_workflow_status(workflow['workflow_id'])
            progress = status.get('progress', 'unknown')
            
            print(f"   {workflow['workflow_id']}: {workflow['workflow_type']}")
            print(f"      Status: {workflow['status']} - {progress}")
            print(f"      Created: {workflow['created_at']}")
        
    except Exception as e:
        print(f"❌ Failed to list workflows: {e}")

def main():
    """Main CLI loop."""
    print_banner()
    
    # Initialize master agent
    try:
        master = MasterAgent()
        print("✅ Master Agent initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize Master Agent: {e}")
        return
    
    print_help()
    
    # Main command loop
    while True:
        try:
            command = input("\n🤖 Master Agent> ").strip()
            
            if not command:
                continue
            
            parts = command.split()
            cmd = parts[0].lower()
            
            if cmd == 'quit' or cmd == 'exit':
                print("👋 Goodbye!")
                master.stop()
                break
            
            elif cmd == 'help':
                print_help()
            
            elif cmd == 'create':
                if len(parts) < 4:
                    print("❌ Usage: create <type> <title> <branch>")
                    continue
                
                workflow_type = parts[1]
                title = parts[2]
                branch = parts[3]
                
                create_workflow(master, workflow_type, title, branch)
            
            elif cmd == 'interactive':
                create_workflow_interactive(master)
            
            elif cmd == 'status':
                if len(parts) < 2:
                    print("❌ Usage: status <workflow_id>")
                    continue
                
                workflow_id = parts[1]
                show_workflow_status(master, workflow_id)
            
            elif cmd == 'agents':
                show_agent_status(master)
            
            elif cmd == 'queue':
                show_queue_status(master)
            
            elif cmd == 'monitor':
                if len(parts) < 2:
                    print("❌ Usage: monitor <workflow_id>")
                    continue
                
                workflow_id = parts[1]
                monitor_workflow(master, workflow_id)
            
            elif cmd == 'list':
                list_workflows(master)
            
            else:
                print(f"❌ Unknown command: {cmd}")
                print("Type 'help' for available commands")
        
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            master.stop()
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()