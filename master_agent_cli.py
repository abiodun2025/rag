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
    print("  create_branch                   - Branch Agent only (creates branch + pushes to GitHub)")
    print("  branch_and_pr                   - Branch Agent + PR Agent")
    print("  full_branch_workflow            - Complete workflow (Branch + Push + PR + Report)")
    
    print("\n📋 Agent Responsibilities:")
    print("  - PR Agent: Creates pull requests")
    print("  - Report Agent: Generates local URL reports")
    print("  - Branch Agent: Handles branch operations (create, checkout, push, delete)")
    
    print("\n📋 Examples:")
    print("  interactive                     - Step-by-step workflow creation")
    print("  create create_pr 'My PR' my-branch")
    print("  create pr_with_report 'My Feature' feature-branch")
    print("  create create_branch 'New Feature' new-feature-branch")
    print("  create branch_and_pr 'Feature with PR' feature-pr-branch")
    print("  create full_branch_workflow 'Complete Feature' complete-feature-branch")
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
        elif workflow_type == "create_branch":
            parameters = {
                "title": title,
                "description": f"Created by Master Agent CLI\nBranch: {branch}",
                "branch_name": branch
            }
        elif workflow_type == "branch_and_pr":
            parameters = {
                "title": title,
                "description": f"""Created by Master Agent CLI

## Description
This workflow creates a branch and then a PR.

## Branch
Source: {branch}
Target: main

## Workflow Steps
1. Create Branch (Branch Agent)
2. Create Pull Request (PR Agent)

Created at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}""",
                "source_branch": branch,
                "target_branch": "main",
                "branch_name": branch
            }
        elif workflow_type == "full_branch_workflow":
            parameters = {
                "title": title,
                "description": f"""Created by Master Agent CLI

## Description
Complete branch workflow with push, PR, and report.

## Branch
Source: {branch}
Target: main

## Workflow Steps
1. Create Branch (Branch Agent)
2. Push Branch (Branch Agent)
3. Create Pull Request (PR Agent)
4. Generate Report (Report Agent)

Created at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}""",
                "source_branch": branch,
                "target_branch": "main",
                "branch_name": branch
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
    """Create a workflow interactively with step-by-step prompts."""
    print("\n📋 Step 1: Choose Workflow Type")
    print("Available types:")
    print("  1. create_pr          - PR Agent only (creates PR)")
    print("  2. pr_with_report     - PR Agent + Report Agent")
    print("  3. create_branch      - Branch Agent only (creates branch)")
    print("  4. branch_and_pr      - Branch Agent + PR Agent")
    print("  5. full_branch_workflow - Complete workflow (Branch + Push + PR + Report)")
    
    while True:
        try:
            choice = input("\nEnter your choice (1-5): ").strip()
            if choice == "1":
                workflow_type = "create_pr"
                break
            elif choice == "2":
                workflow_type = "pr_with_report"
                break
            elif choice == "3":
                workflow_type = "create_branch"
                break
            elif choice == "4":
                workflow_type = "branch_and_pr"
                break
            elif choice == "5":
                workflow_type = "full_branch_workflow"
                break
            else:
                print("❌ Invalid choice. Please enter 1-5.")
        except (ValueError, KeyboardInterrupt):
            print("\n❌ Cancelled workflow creation.")
            return
    
    print(f"\n📋 Step 2: Enter Workflow Details")
    
    # Get title
    title = input("Enter workflow title: ").strip()
    if not title:
        print("❌ Title is required.")
        return
    
    # Get branch name
    branch_name = input("Enter branch name: ").strip()
    if not branch_name:
        print("❌ Branch name is required.")
        return
    
    # Prepare parameters based on workflow type
    if workflow_type in ["create_pr", "pr_with_report"]:
        parameters = {
            "title": title,
            "description": f"Workflow: {title}",
            "source_branch": branch_name,
            "target_branch": "main"
        }
    elif workflow_type in ["create_branch", "branch_and_pr", "full_branch_workflow"]:
        parameters = {
            "title": title,
            "description": f"Workflow: {title}",
            "source_branch": branch_name,
            "target_branch": "main",
            "branch_name": branch_name
        }
    else:
        parameters = {
            "title": title,
            "branch_name": branch_name
        }
    
    # Confirm workflow creation
    print(f"\n📋 Confirm Workflow Creation:")
    print(f"Type: {workflow_type}")
    print(f"Title: {title}")
    print(f"Branch: {branch_name}")
    
    confirm = input("Create this workflow? (y/n): ").strip().lower()
    if confirm != 'y':
        print("❌ Workflow creation cancelled.")
        return
    
    # Create the workflow
    try:
        workflow_id = create_workflow(master, workflow_type, title, branch_name)
        if workflow_id:
            print(f"\n✅ Workflow created successfully!")
            print(f"   Workflow ID: {workflow_id}")
            print(f"   Monitor with: monitor {workflow_id}")
        else:
            print(f"\n❌ Failed to create workflow.")
        
    except Exception as e:
        print(f"❌ Failed to create workflow: {e}")

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
                    print("   Note: Use quotes for titles with spaces")
                    print("   Example: create create_branch \"My Feature Branch\" feature-branch")
                    continue
                
                workflow_type = parts[1]
                
                # Handle quoted titles properly
                if len(parts) >= 4:
                    # Check if title is quoted
                    if parts[2].startswith('"') and parts[2].endswith('"'):
                        title = parts[2][1:-1]  # Remove quotes
                        branch = parts[3]
                    elif parts[2].startswith('"'):
                        # Multi-word quoted title
                        title_parts = []
                        i = 2
                        while i < len(parts) and not parts[i].endswith('"'):
                            title_parts.append(parts[i])
                            i += 1
                        if i < len(parts):
                            title_parts.append(parts[i])
                            title = ' '.join(title_parts)[1:-1]  # Remove quotes
                            branch = parts[i + 1] if i + 1 < len(parts) else "feature-branch"
                        else:
                            print("❌ Unclosed quote in title")
                            continue
                    else:
                        # Simple single-word title
                        title = parts[2]
                        branch = parts[3]
                else:
                    print("❌ Usage: create <type> <title> <branch>")
                    continue
                
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