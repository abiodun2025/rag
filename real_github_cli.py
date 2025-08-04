#!/usr/bin/env python3
"""
Real GitHub CLI with Alert Integration
Command-line interface for testing real GitHub workflows with real-time alerts.
"""

import asyncio
import argparse
import logging
import os
import sys
from datetime import datetime
from typing import Dict, Any

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from real_github_alert_integration import EnhancedMasterAgentWithAlerts

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RealGitHubCLI:
    """CLI for real GitHub workflows with alerts."""
    
    def __init__(self):
        self.enhanced_agent = EnhancedMasterAgentWithAlerts()
    
    async def create_workflow(self, workflow_type: str, title: str, branch: str, description: str = None):
        """Create a real workflow with alerts."""
        try:
            if not description:
                description = f"Created by Real GitHub CLI\nBranch: {branch}\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            parameters = {
                "title": title,
                "description": description,
                "source_branch": branch,
                "target_branch": "main"
            }
            
            print(f"🚀 Creating workflow: {workflow_type}")
            print(f"   Title: {title}")
            print(f"   Branch: {branch}")
            print(f"   Description: {description[:100]}...")
            
            workflow_id = await self.enhanced_agent.create_workflow_with_alerts(
                workflow_type, parameters
            )
            
            print(f"\n✅ Workflow created: {workflow_id}")
            print("📧 Check your email for workflow start alert!")
            
            return workflow_id
            
        except Exception as e:
            print(f"❌ Failed to create workflow: {e}")
            return None
    
    async def create_pull_request(self, title: str, body: str, branch: str):
        """Create a real pull request with alerts."""
        try:
            print(f"📋 Creating pull request...")
            print(f"   Title: {title}")
            print(f"   Branch: {branch}")
            print(f"   Body: {body[:100]}...")
            
            result = await self.enhanced_agent.create_pull_request_with_alerts(
                title, body, branch
            )
            
            if result.get("success"):
                pr_data = result.get("result", {})
                pr_number = pr_data.get("number", "unknown")
                pr_url = pr_data.get("html_url", "")
                
                print(f"\n✅ Pull request created successfully!")
                print(f"   PR Number: #{pr_number}")
                print(f"   URL: {pr_url}")
                print("📧 Check your email for PR creation alert!")
                
                return result
            else:
                print(f"\n❌ Pull request creation failed: {result.get('error')}")
                return result
                
        except Exception as e:
            print(f"❌ Failed to create pull request: {e}")
            return None
    
    async def test_full_workflow(self):
        """Test a complete workflow with alerts."""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            branch_name = f"feature/real-alerts-{timestamp}"
            
            print("🎯 Testing Full Real GitHub Workflow with Alerts")
            print("=" * 60)
            
            # Step 1: Create workflow
            workflow_id = await self.create_workflow(
                "pr_with_report",
                f"Real Alert Integration Test {timestamp}",
                branch_name,
                f"""Real GitHub Alert Integration Test

## Description
This is a real workflow test with live alert monitoring.

## Features
- Real-time email alerts
- GitHub API integration
- Workflow monitoring
- Pull request creation

## Branch
Source: {branch_name}
Target: main

Created at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
            )
            
            if not workflow_id:
                return
            
            # Step 2: Create pull request
            pr_result = await self.create_pull_request(
                f"Real Alert Integration Test {timestamp}",
                f"""# Real Alert Integration Test

This pull request was created with real-time alert monitoring.

## What's happening:
1. ✅ Workflow started with alerts
2. ✅ Pull request created with alerts
3. 📧 Email notifications sent to your inbox

## Test Details:
- Branch: {branch_name}
- Workflow ID: {workflow_id}
- Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Alert System Features:
- Real-time email notifications
- GitHub API integration
- Workflow status monitoring
- Error handling and alerts

Check your email for real-time notifications! 🎉""",
                branch_name
            )
            
            if pr_result and pr_result.get("success"):
                print(f"\n🎉 Full workflow test completed successfully!")
                print(f"📧 You should have received multiple email alerts:")
                print(f"   1. Workflow started alert")
                print(f"   2. Pull request created alert")
                print(f"   3. Task completion alerts (if applicable)")
            else:
                print(f"\n⚠️  Workflow test completed with some issues")
                print(f"   Check the logs above for details")
                
        except Exception as e:
            print(f"❌ Full workflow test failed: {e}")
    
    async def monitor_workflow(self, workflow_id: str):
        """Monitor a workflow with alerts."""
        try:
            print(f"📊 Monitoring workflow: {workflow_id}")
            
            await self.enhanced_agent.monitor_workflow_with_alerts(workflow_id)
            
            print("✅ Workflow monitoring completed")
            
        except Exception as e:
            print(f"❌ Failed to monitor workflow: {e}")

def print_help():
    """Print help information."""
    print("""
🚀 Real GitHub CLI with Alert Integration
=========================================

This CLI allows you to test real GitHub workflows with real-time email alerts.

Commands:
  create-workflow <type> <title> <branch> [description]
    Create a workflow with alert monitoring
    
  create-pr <title> <body> <branch>
    Create a pull request with alert monitoring
    
  test-full
    Run a complete workflow test with alerts
    
  monitor <workflow_id>
    Monitor a workflow with alerts
    
  help
    Show this help message

Examples:
  python3 real_github_cli.py create-workflow pr_with_report "Test PR" feature/test
  python3 real_github_cli.py create-pr "New Feature" "Adds new functionality" feature/new
  python3 real_github_cli.py test-full
  python3 real_github_cli.py monitor workflow_abc123

Environment Variables:
  GITHUB_TOKEN: Your GitHub personal access token
  GITHUB_OWNER: GitHub repository owner (default: abiodun2025)
  GITHUB_REPO: GitHub repository name (default: rag)
  GOOGLE_EMAIL: Your Gmail address for alerts
  GOOGLE_PASSWORD: Your Gmail app password for alerts

Prerequisites:
  1. MCP server running on port 5000
  2. GitHub credentials configured
  3. Gmail credentials configured for alerts
""")

async def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(description="Real GitHub CLI with Alert Integration")
    parser.add_argument("command", help="Command to execute")
    parser.add_argument("args", nargs="*", help="Command arguments")
    
    args = parser.parse_args()
    
    cli = RealGitHubCLI()
    
    if args.command == "help":
        print_help()
        return
    
    elif args.command == "create-workflow":
        if len(args.args) < 3:
            print("❌ Usage: create-workflow <type> <title> <branch> [description]")
            return
        
        workflow_type = args.args[0]
        title = args.args[1]
        branch = args.args[2]
        description = args.args[3] if len(args.args) > 3 else None
        
        await cli.create_workflow(workflow_type, title, branch, description)
    
    elif args.command == "create-pr":
        if len(args.args) < 3:
            print("❌ Usage: create-pr <title> <body> <branch>")
            return
        
        title = args.args[0]
        body = args.args[1]
        branch = args.args[2]
        
        await cli.create_pull_request(title, body, branch)
    
    elif args.command == "test-full":
        await cli.test_full_workflow()
    
    elif args.command == "monitor":
        if len(args.args) < 1:
            print("❌ Usage: monitor <workflow_id>")
            return
        
        workflow_id = args.args[0]
        await cli.monitor_workflow(workflow_id)
    
    else:
        print(f"❌ Unknown command: {args.command}")
        print_help()

if __name__ == "__main__":
    asyncio.run(main()) 