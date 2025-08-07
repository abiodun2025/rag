#!/usr/bin/env python3
"""
Test Real GitHub Alerts
Demonstrates real-time alerts for GitHub workflows with your current setup.
"""

import asyncio
import logging
import os
import sys
from datetime import datetime
from typing import Dict, Any

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from real_github_alert_integration import RealGitHubAlertIntegration, EnhancedMasterAgentWithAlerts

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_real_github_alerts():
    """Test real GitHub alerts with your current setup."""
    
    print("🚀 Testing Real GitHub Alert Integration")
    print("=" * 50)
    
    # Initialize alert integration
    alert_integration = RealGitHubAlertIntegration()
    
    print("1. Testing workflow start alert...")
    await alert_integration.on_workflow_start(
        "workflow_abc123",
        "pr_with_report",
        {
            "title": "Real GitHub Integration Test",
            "description": "Testing real-time alerts with actual GitHub workflows",
            "source_branch": "feature/real-alerts",
            "target_branch": "main"
        }
    )
    
    print("2. Testing task start alert...")
    await alert_integration.on_task_start(
        "task_abc123_create_pr",
        "create_pr",
        "PR Agent"
    )
    
    print("3. Testing PR creation success alert...")
    await alert_integration.on_pr_created(
        123,
        "Real GitHub Alert Integration Test",
        "https://github.com/abiodun2025/rag/pull/123",
        "feature/real-alerts",
        "main"
    )
    
    print("4. Testing task completion alert...")
    await alert_integration.on_task_complete(
        "task_abc123_create_pr",
        "create_pr",
        True,
        {
            "pr_number": 123,
            "url": "https://github.com/abiodun2025/rag/pull/123",
            "status": "created"
        }
    )
    
    print("5. Testing workflow completion alert...")
    await alert_integration.on_workflow_complete(
        "workflow_abc123",
        "pr_with_report",
        True,
        {
            "workflow_id": "workflow_abc123",
            "status": "completed",
            "tasks_completed": 2,
            "pr_created": True
        }
    )
    
    print("\n✅ All real GitHub alert tests completed!")
    print("📧 Check your email for the following alerts:")
    print("   1. Workflow started")
    print("   2. Task started")
    print("   3. Pull request created")
    print("   4. Task completed")
    print("   5. Workflow completed")

async def test_enhanced_master_agent():
    """Test enhanced master agent with alerts."""
    
    print("\n🔧 Testing Enhanced Master Agent with Alerts")
    print("=" * 50)
    
    enhanced_agent = EnhancedMasterAgentWithAlerts()
    
    print("1. Creating workflow with alerts...")
    workflow_id = await enhanced_agent.create_workflow_with_alerts(
        "pr_with_report",
        {
            "title": "Enhanced Master Agent Test",
            "description": "Testing enhanced master agent with real-time alerts",
            "source_branch": "feature/enhanced-agent",
            "target_branch": "main"
        }
    )
    
    print(f"✅ Workflow created: {workflow_id}")
    
    print("2. Creating pull request with alerts...")
    pr_result = await enhanced_agent.create_pull_request_with_alerts(
        "Enhanced Master Agent Integration",
        "This PR was created with enhanced master agent and real-time alerts",
        "feature/enhanced-agent"
    )
    
    if pr_result and pr_result.get("success"):
        print("✅ Pull request created with alerts!")
    else:
        print(f"⚠️  Pull request creation had issues: {pr_result}")
    
    print("\n🎉 Enhanced master agent test completed!")

async def test_error_scenarios():
    """Test error scenarios with alerts."""
    
    print("\n⚠️  Testing Error Scenarios with Alerts")
    print("=" * 50)
    
    alert_integration = RealGitHubAlertIntegration()
    
    print("1. Testing PR creation failure...")
    await alert_integration.on_pr_failed(
        "Branch 'feature/nonexistent' does not exist",
        {
            "title": "Test PR",
            "head": "feature/nonexistent",
            "base": "main"
        }
    )
    
    print("2. Testing GitHub API error...")
    await alert_integration.on_github_api_error(
        404,
        "Repository not found",
        "create_pull_request"
    )
    
    print("3. Testing task failure...")
    await alert_integration.on_task_complete(
        "task_abc123_create_pr",
        "create_pr",
        False,
        None,
        "GitHub API rate limit exceeded"
    )
    
    print("4. Testing workflow failure...")
    await alert_integration.on_workflow_complete(
        "workflow_abc123",
        "pr_with_report",
        False,
        {
            "error": "Task execution failed",
            "failed_task": "task_abc123_create_pr"
        }
    )
    
    print("\n✅ Error scenario tests completed!")
    print("📧 Check your email for error alerts")

async def main():
    """Main test function."""
    print("🎯 Real GitHub Alert Integration Test Suite")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Email: {os.getenv('GOOGLE_EMAIL', 'Not set')}")
    print(f"GitHub Owner: {os.getenv('GITHUB_OWNER', 'abiodun2025')}")
    print(f"GitHub Repo: {os.getenv('GITHUB_REPO', 'rag')}")
    print("=" * 60)
    
    try:
        # Test 1: Basic alert integration
        await test_real_github_alerts()
        
        # Test 2: Enhanced master agent
        await test_enhanced_master_agent()
        
        # Test 3: Error scenarios
        await test_error_scenarios()
        
        print("\n🎉 All tests completed successfully!")
        print("\n📧 Summary of alerts sent:")
        print("   ✅ Workflow lifecycle alerts (start, complete)")
        print("   ✅ Task lifecycle alerts (start, complete)")
        print("   ✅ Pull request alerts (created, failed)")
        print("   ✅ Error alerts (API errors, task failures)")
        print("\n🔧 Next steps:")
        print("   1. Check your email for all alert notifications")
        print("   2. Set up your real GitHub token for actual PR creation")
        print("   3. Use the real_github_cli.py for live workflow testing")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        logger.exception("Test error")

if __name__ == "__main__":
    asyncio.run(main()) 