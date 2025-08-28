#!/usr/bin/env python3
"""
Test script for the Task/Project Agent.
Demonstrates integration with MCP server and project management tools.
"""

import asyncio
import sys
import os

# Add the agent directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'agent'))

from agent.task_project_agent import TaskProjectAgent, PlatformType, TaskStatus, TaskPriority

async def test_task_project_agent():
    """Test the Task/Project Agent functionality."""
    print("🚀 Testing Task/Project Agent with MCP Server")
    print("=" * 60)
    
    # Initialize the agent
    agent = TaskProjectAgent()
    
    # Test 1: Health Check
    print("\n1️⃣ Testing Agent Health Check...")
    health = await agent.health_check()
    print(f"✅ Health Status: {health['agent_status']}")
    print(f"   MCP Server: {'🟢 Healthy' if health['mcp_server_healthy'] else '🔴 Unhealthy'}")
    print(f"   Tools Available: {health['tools_available']}")
    print(f"   Platforms Supported: {health['platforms_supported']}")
    
    # Test 2: Get Available Tools
    print("\n2️⃣ Testing MCP Tools Discovery...")
    tools = await agent.get_available_tools()
    print(f"✅ Found {len(tools)} MCP tools:")
    for tool in tools[:5]:  # Show first 5 tools
        print(f"   - {tool['name']}: {tool['description']}")
    if len(tools) > 5:
        print(f"   ... and {len(tools) - 5} more tools")
    
    # Test 3: Platform Information
    print("\n3️⃣ Testing Platform Information...")
    for platform in PlatformType:
        info = await agent.get_platform_info(platform)
        if info['success']:
            print(f"✅ {platform.value.upper()}: {info['name']}")
            print(f"   Capabilities: {', '.join(info['capabilities'])}")
        else:
            print(f"❌ {platform.value.upper()}: {info['error']}")
    
    # Test 4: Create Tasks on Different Platforms
    print("\n4️⃣ Testing Task Creation...")
    
    # Jira Task
    print("   Creating Jira task...")
    jira_task = await agent.create_task(PlatformType.JIRA, {
        "project_key": "TEST",
        "title": "Test Jira Issue",
        "description": "This is a test issue created by the Task/Project Agent",
        "issue_type": "Task"
    })
    if jira_task['success']:
        print(f"   ✅ Jira task created: {jira_task['result']['issue_id']}")
    else:
        print(f"   ❌ Jira task failed: {jira_task['error']}")
    
    # Trello Card
    print("   Creating Trello card...")
    trello_card = await agent.create_task(PlatformType.TRELLO, {
        "board_name": "Test Board",
        "list_name": "To Do",
        "card_title": "Test Trello Card",
        "description": "This is a test card created by the Task/Project Agent"
    })
    if trello_card['success']:
        print(f"   ✅ Trello card created: {trello_card['result']['card_id']}")
    else:
        print(f"   ❌ Trello card failed: {trello_card['error']}")
    
    # Asana Task
    print("   Creating Asana task...")
    asana_task = await agent.create_task(PlatformType.ASANA, {
        "project_name": "Test Project",
        "task_name": "Test Asana Task",
        "description": "This is a test task created by the Task/Project Agent"
    })
    if asana_task['success']:
        print(f"   ✅ Asana task created: {asana_task['result']['task_id']}")
    else:
        print(f"   ❌ Asana task failed: {asana_task['error']}")
    
    # Linear Issue
    print("   Creating Linear issue...")
    linear_issue = await agent.create_task(PlatformType.LINEAR, {
        "team_name": "Engineering",
        "title": "Test Linear Issue",
        "description": "This is a test issue created by the Task/Project Agent",
        "priority": "Medium"
    })
    if linear_issue['success']:
        print(f"   ✅ Linear issue created: {linear_issue['result']['issue_id']}")
    else:
        print(f"   ❌ Linear issue failed: {linear_issue['error']}")
    
    # Test 5: Get Tasks
    print("\n5️⃣ Testing Task Retrieval...")
    
    for platform in PlatformType:
        print(f"   Getting tasks from {platform.value.upper()}...")
        tasks = await agent.get_tasks(platform)
        if tasks['success']:
            task_count = len(tasks['result'])
            print(f"   ✅ Found {task_count} tasks in {platform.value.upper()}")
        else:
            print(f"   ❌ Failed to get tasks from {platform.value.upper()}: {tasks['error']}")
    
    # Test 6: Project Sync
    print("\n6️⃣ Testing Project Synchronization...")
    
    print("   Syncing from Jira to Trello...")
    sync_result = await agent.sync_projects(
        PlatformType.JIRA,
        PlatformType.TRELLO,
        "TEST-PROJ"
    )
    
    if sync_result.success:
        print(f"   ✅ Sync successful: {sync_result.tasks_synced} tasks synced")
        print(f"   Sync ID: {sync_result.sync_id}")
    else:
        print(f"   ❌ Sync failed: {sync_result.errors}")
    
    # Test 7: Project Status
    print("\n7️⃣ Testing Project Status...")
    
    for platform in PlatformType:
        print(f"   Getting status from {platform.value.upper()}...")
        status = await agent.get_project_status(platform, "TEST-PROJ")
        if status['success']:
            print(f"   ✅ {platform.value.upper()} Status: {status['result']['status']}")
            print(f"      Progress: {status['result']['progress']}")
        else:
            print(f"   ❌ Failed to get status from {platform.value.upper()}: {status['error']}")
    
    # Test 8: Bulk Operations
    print("\n8️⃣ Testing Bulk Operations...")
    
    bulk_tasks = [
        {
            "project_key": "BULK",
            "title": "Bulk Task 1",
            "description": "First bulk task",
            "issue_type": "Task"
        },
        {
            "project_key": "BULK",
            "title": "Bulk Task 2", 
            "description": "Second bulk task",
            "issue_type": "Bug"
        }
    ]
    
    print("   Creating bulk tasks in Jira...")
    bulk_result = await agent.bulk_create_tasks(PlatformType.JIRA, bulk_tasks)
    if bulk_result['success']:
        print(f"   ✅ Bulk creation successful: {bulk_result['successful']}/{bulk_result['total_tasks']} tasks created")
    else:
        print(f"   ❌ Bulk creation failed")
    
    # Test 9: Cache and History
    print("\n9️⃣ Testing Cache and History...")
    
    sync_history = await agent.get_sync_history()
    print(f"   Sync operations performed: {len(sync_history)}")
    
    cache_clear = await agent.clear_cache()
    print(f"   Cache cleared: {cache_clear['message']}")
    
    # Final Health Check
    print("\n🔍 Final Health Check...")
    final_health = await agent.health_check()
    print(f"✅ Final Status: {final_health['agent_status']}")
    print(f"   Sync Operations: {final_health['sync_operations']}")
    print(f"   Cache Size: {final_health['cache_size']}")
    
    print("\n🎉 Task/Project Agent Testing Complete!")
    print("=" * 60)

async def test_specific_platform(platform: PlatformType):
    """Test a specific platform in detail."""
    print(f"\n🔧 Testing {platform.value.upper()} Platform in Detail")
    print("-" * 40)
    
    agent = TaskProjectAgent()
    
    # Test platform info
    info = await agent.get_platform_info(platform)
    if info['success']:
        print(f"Platform: {info['name']}")
        print(f"Capabilities: {', '.join(info['capabilities'])}")
        
        # Test task creation
        task_data = {
            "title": f"Detailed Test {platform.value.title()}",
            "description": f"This is a detailed test of {platform.value} functionality"
        }
        
        # Add platform-specific data
        if platform == PlatformType.JIRA:
            task_data.update({
                "project_key": "DETAIL",
                "issue_type": "Task"
            })
        elif platform == PlatformType.TRELLO:
            task_data.update({
                "board_name": "Detail Test Board",
                "list_name": "To Do"
            })
        elif platform == PlatformType.ASANA:
            task_data.update({
                "project_name": "Detail Test Project"
            })
        elif platform == PlatformType.LINEAR:
            task_data.update({
                "team_name": "Engineering",
                "priority": "High"
            })
        
        result = await agent.create_task(platform, task_data)
        if result['success']:
            print(f"✅ Task created successfully: {result['result']}")
        else:
            print(f"❌ Task creation failed: {result['error']}")
    else:
        print(f"❌ Platform info failed: {info['error']}")

def main():
    """Main test function."""
    print("🧠 Task/Project Agent Test Suite")
    print("=" * 60)
    
    # Check if MCP server is running
    print("⚠️  Make sure your MCP server is running on http://127.0.0.1:5000")
    print("   Run: python3 simple_mcp_http_server.py")
    print()
    
    # Run comprehensive tests
    try:
        asyncio.run(test_task_project_agent())
    except Exception as e:
        print(f"❌ Test failed: {e}")
        print("\n💡 Make sure your MCP server is running and accessible")
    
    # Test specific platforms
    print("\n🔍 Testing Individual Platforms...")
    for platform in PlatformType:
        try:
            asyncio.run(test_specific_platform(platform))
        except Exception as e:
            print(f"❌ {platform.value.upper()} test failed: {e}")

if __name__ == "__main__":
    main()
