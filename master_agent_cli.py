#!/usr/bin/env python3
"""
Master Agent CLI Interface
Command-line interface for the master agent to create and monitor workflows.
"""

import sys
import time
import json
import requests
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
    print("  branches                         - List all available branches")
    print("  check-commits <branch>          - Check if branch has new commits")
    print("  prs                              - List existing pull requests")
    print("  status <workflow_id>            - Check workflow status")
    print("  agents                          - Show agent status")
    print("  queue                           - Show task queue status")
    print("  monitor <workflow_id>           - Monitor workflow in real-time")
    print("  list                            - List all workflows")
    print("  help                            - Show this help")
    print("  quit                            - Exit the CLI")
    print("\n📋 Workflow Types (PRs Only):")
    print("  create_pr                       - PR Agent only (creates PR)")
    print("  pr_with_report                  - PR Agent + Report Agent")
    print("\n📋 Agent Responsibilities:")
    print("  - PR Agent: Creates pull requests")
    print("  - Report Agent: Generates local URL reports")
    print("\n📋 Examples:")
    print("  interactive                     - Step-by-step workflow creation")
    print("  create pr_with_report 'My Feature' feature-branch")
    print("  create create_pr 'Simple PR' simple-branch")
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
    
    while True:
        choice = input("\nEnter your choice (1-2): ").strip()
        workflow_types = {
            "1": "create_pr",
            "2": "pr_with_report"
        }
        
        if choice in workflow_types:
            workflow_type = workflow_types[choice]
            print(f"✅ Selected: {workflow_type}")
            break
        else:
            print("❌ Invalid choice. Please enter 1-2.")
    
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
    
    # Step 3: List available branches with commit status
    print(f"\n📋 Step 3: Available Branches")
    print(f"Workflow: {workflow_type}")
    print(f"Title: {title}")
    
    try:
        print("\n🔍 Fetching available branches with commit status...")
        response = master._execute_branch_listing()
        if response and response.get("success"):
            branches = response.get("branches", [])
            print(f"\n✅ Found {len(branches)} branches:")
            print("=" * 70)
            
            # Check commit status for each branch
            for i, branch in enumerate(branches, 1):
                branch_name = branch["name"]
                protection = "🔒" if branch.get("protected") else "🔓"
                
                # Skip main branch for commit checking
                if branch_name == "main":
                    print(f"   {i:2d}. {protection} {branch_name} (main branch)")
                    continue
                
                # Check if branch has new commits
                try:
                    commit_response = requests.post(
                        "http://127.0.0.1:5000/call",
                        json={
                            "tool": "check_branch_commits",
                            "arguments": {"source_branch": branch_name, "target_branch": "main"}
                        },
                        timeout=10
                    )
                    
                    if commit_response.status_code == 200:
                        commit_result = commit_response.json()
                        if commit_result.get("success"):
                            details = commit_result.get("details", {})
                            has_commits = details.get("has_new_commits", False)
                            
                            if has_commits:
                                ahead_by = details.get("ahead_by", 0)
                                print(f"   {i:2d}. {protection} {branch_name} ✅ {ahead_by} new commits")
                            else:
                                print(f"   {i:2d}. {protection} {branch_name} ⚠️  no new commits")
                        else:
                            print(f"   {i:2d}. {protection} {branch_name} ❌ error checking commits")
                    else:
                        print(f"   {i:2d}. {protection} {branch_name} ❌ HTTP error")
                        
                except Exception as e:
                    print(f"   {i:2d}. {protection} {branch_name} ❌ exception: {e}")
                
                # Show commit SHA if available
                if branch.get("commit_sha"):
                    sha_short = branch["commit_sha"][:8]
                    print(f"       🔗 SHA: {sha_short}")
                
                print()  # Empty line for readability
            
            print("=" * 70)
            print("💡 Legend: ✅ = Ready for PR | ⚠️ = Needs commits | ❌ = Error")
        else:
            print("⚠️  Could not fetch branches. You can still enter a branch name manually.")
    except Exception as e:
        print(f"⚠️  Error fetching branches: {e}")
        print("   You can still enter a branch name manually.")
    
    # Step 4: Enter branch name
    print(f"\n📋 Step 4: Enter Branch Name")
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
            print(f"   {workflow['workflow_id']}: {workflow['workflow_type']}")
            print(f"      Status: {workflow['status']} - {status.get('progress', 'unknown')}")
            print(f"      Created: {workflow['created_at']}")
        
    except Exception as e:
        print(f"❌ Failed to list workflows: {e}")

def list_branches(master):
    """List all available branches with commit status."""
    try:
        print("\n🔍 Fetching available branches...")
        response = master._execute_branch_listing()
        
        if response and response.get("success"):
            branches = response.get("branches", [])
            print(f"\n✅ Found {len(branches)} branches:")
            print("=" * 80)
            
            # Check commit status for each branch
            for i, branch in enumerate(branches, 1):
                branch_name = branch["name"]
                protection = "🔒" if branch.get("protected") else "🔓"
                
                # Skip main branch for commit checking
                if branch_name == "main":
                    print(f"{i:2d}. {protection} {branch_name} (main branch)")
                    continue
                
                # Check if branch has new commits
                try:
                    commit_response = requests.post(
                        "http://127.0.0.1:5000/call",
                        json={
                            "tool": "check_branch_commits",
                            "arguments": {"source_branch": branch_name, "target_branch": "main"}
                        },
                        timeout=10
                    )
                    
                    if commit_response.status_code == 200:
                        commit_result = commit_response.json()
                        if commit_result.get("success"):
                            details = commit_result.get("details", {})
                            has_commits = details.get("has_new_commits", False)
                            
                            if has_commits:
                                ahead_by = details.get("ahead_by", 0)
                                print(f"{i:2d}. {protection} {branch_name} ✅ {ahead_by} new commits")
                            else:
                                print(f"{i:2d}. {protection} {branch_name} ⚠️  no new commits")
                        else:
                            print(f"{i:2d}. {protection} {branch_name} ❌ error checking commits")
                    else:
                        print(f"{i:2d}. {protection} {branch_name} ❌ HTTP error")
                        
                except Exception as e:
                    print(f"{i:2d}. {protection} {branch_name} ❌ exception: {e}")
                
                # Show commit details if available
                if branch.get("commit_sha"):
                    sha_short = branch["commit_sha"][:8]
                    print(f"    🔗 SHA: {sha_short}")
                
                print()  # Empty line for readability
            
            # Summary
            print("=" * 80)
            print("💡 Legend:")
            print("   ✅ = Ready for PR creation (has new commits)")
            print("   ⚠️  = Needs commits first (no new commits)")
            print("   ❌ = Error checking commit status")
            print("   🔓 = Unprotected branch")
            print("   🔒 = Protected branch")
            
        else:
            error_msg = response.get("error", "Unknown error") if response else "No response"
            print(f"❌ Failed to fetch branches: {error_msg}")
    except Exception as e:
        print(f"❌ Error listing branches: {e}")

def check_branch_commits(master, branch_name):
    """Check if a branch has new commits compared to main."""
    try:
        print(f"\n🔍 Checking commits for branch: {branch_name}")
        
        response = requests.post(
            "http://127.0.0.1:5000/call",
            json={
                "tool": "check_branch_commits",
                "arguments": {"source_branch": branch_name, "target_branch": "main"}
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                details = result.get("details", {})
                has_commits = details.get("has_new_commits", False)
                message = details.get("message", "")
                
                print(f"📊 Branch: {branch_name}")
                print(f"   Status: {'✅ Has new commits' if has_commits else '⚠️  No new commits'}")
                print(f"   Details: {message}")
                
                if has_commits:
                    ahead_by = details.get("ahead_by", 0)
                    behind_by = details.get("behind_by", 0)
                    total_commits = details.get("total_commits", 0)
                    print(f"   📈 Ahead by: {ahead_by} commits")
                    print(f"   📉 Behind by: {behind_by} commits")
                    print(f"   📊 Total commits: {total_commits}")
                    print(f"   💡 This branch is ready for PR creation!")
                else:
                    print(f"   💡 Make commits to {branch_name} before creating a pull request")
                
                # Show commit SHAs
                source_sha = details.get("source_sha", "")
                target_sha = details.get("target_sha", "")
                if source_sha and target_sha:
                    print(f"   🔗 Source SHA: {source_sha[:8]}")
                    print(f"   🔗 Target SHA: {target_sha[:8]}")
                
            else:
                print(f"❌ Error: {result.get('error')}")
        else:
            print(f"❌ HTTP error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error checking branch commits: {e}")

def list_prs(master):
    """List existing pull requests."""
    try:
        print("\n🔍 Fetching existing pull requests...")
        
        response = requests.post(
            "http://127.0.0.1:5000/call",
            json={
                "tool": "list_pull_requests",
                "arguments": {"state": "open"}
            },
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                prs = result.get("pull_requests", [])
                
                if not prs:
                    print("✅ No open pull requests found")
                    return
                
                print(f"\n✅ Found {len(prs)} open pull request(s):")
                print("=" * 80)
                
                for i, pr in enumerate(prs, 1):
                    title = pr.get("title", "No title")
                    number = pr.get("number", "N/A")
                    state = pr.get("state", "unknown")
                    source_branch = pr.get("head", {}).get("ref", "unknown")
                    target_branch = pr.get("base", {}).get("ref", "unknown")
                    created_at = pr.get("created_at", "")
                    updated_at = pr.get("updated_at", "")
                    
                    # Format dates
                    if created_at:
                        created_date = created_at.split('T')[0] if 'T' in created_at else created_at
                    else:
                        created_date = "Unknown"
                    
                    if updated_at:
                        updated_date = updated_at.split('T')[0] if 'T' in updated_at else updated_at
                    else:
                        updated_date = "Unknown"
                    
                    print(f"   {i:2d}. #{number} {title}")
                    print(f"       🔄 {source_branch} → {target_branch}")
                    print(f"       📅 Created: {created_date} | Updated: {updated_date}")
                    print(f"       📊 State: {state.upper()}")
                    
                    # Show labels if any
                    labels = pr.get("labels", [])
                    if labels:
                        label_names = [label.get("name", "") for label in labels]
                        print(f"       🏷️  Labels: {', '.join(label_names)}")
                    
                    print()  # Empty line for readability
                
                print("=" * 80)
                print("💡 Legend: 🔄 = Branch flow | 📅 = Dates | 📊 = Status | 🏷️ = Labels")
                
            else:
                print(f"❌ Error: {result.get('error')}")
        else:
            print(f"❌ HTTP error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error listing pull requests: {e}")

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
            
            elif cmd == 'branches':
                list_branches(master)
            
            elif cmd == 'check-commits':
                if len(parts) < 2:
                    print("❌ Usage: check-commits <branch_name>")
                    continue
                
                branch_name = parts[1]
                check_branch_commits(master, branch_name)
            
            elif cmd == 'prs':
                list_prs(master)
            
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