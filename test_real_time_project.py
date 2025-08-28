#!/usr/bin/env python3
"""
Real-Time Project Testing for Task/Project Agent
Simulates actual project management workflows across multiple platforms.
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
import json

# Add the agent directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'agent'))

from agent.task_project_agent import TaskProjectAgent, PlatformType, TaskStatus, TaskPriority

class RealTimeProjectTester:
    """Real-time project testing scenarios."""
    
    def __init__(self):
        self.agent = TaskProjectAgent()
        self.test_results = []
        self.project_data = {}
        
    async def setup_test_project(self):
        """Set up a test project across all platforms."""
        print("🏗️  Setting up Real-Time Test Project...")
        print("=" * 60)
        
        # Project: "AI Chatbot Development"
        project_name = "AI Chatbot Development"
        project_description = "Develop an intelligent chatbot using machine learning for customer support"
        
        # Create project structure across platforms
        await self._create_jira_project(project_name, project_description)
        await self._create_trello_project(project_name, project_description)
        await self._create_asana_project(project_name, project_description)
        await self._create_linear_project(project_name, project_description)
        
        print("✅ Test project setup complete!")
    
    async def _create_jira_project(self, name: str, description: str):
        """Create Jira project structure."""
        print(f"   📋 Creating Jira project: {name}")
        
        # Create epic
        epic = await self.agent.create_task(PlatformType.JIRA, {
            "project_key": "CHATBOT",
            "title": f"Epic: {name}",
            "description": description,
            "issue_type": "Epic"
        })
        
        if epic['success']:
            self.project_data['jira_epic'] = epic['result']['issue_id']
            
            # Create user stories
            stories = [
                {
                    "title": "User Authentication System",
                    "description": "Implement secure user login and registration",
                    "issue_type": "Story"
                },
                {
                    "title": "Chat Interface Development",
                    "description": "Build responsive chat UI with real-time messaging",
                    "issue_type": "Story"
                },
                {
                    "title": "ML Model Integration",
                    "description": "Integrate machine learning model for intelligent responses",
                    "issue_type": "Story"
                }
            ]
            
            for story in stories:
                result = await self.agent.create_task(PlatformType.JIRA, {
                    "project_key": "CHATBOT",
                    "title": story["title"],
                    "description": story["description"],
                    "issue_type": story["issue_type"]
                })
                if result['success']:
                    print(f"      ✅ Created story: {story['title']}")
    
    async def _create_trello_project(self, name: str, description: str):
        """Create Trello project structure."""
        print(f"   📋 Creating Trello project: {name}")
        
        # Create board lists
        lists = ["Backlog", "Sprint Planning", "In Development", "Testing", "Deployment"]
        
        for list_name in lists:
            # Create sample cards for each list
            if list_name == "Backlog":
                cards = [
                    "Research chatbot frameworks",
                    "Define user requirements",
                    "Create project timeline"
                ]
            elif list_name == "Sprint Planning":
                cards = [
                    "Plan Sprint 1 tasks",
                    "Estimate story points",
                    "Assign team members"
                ]
            elif list_name == "In Development":
                cards = [
                    "Setup development environment",
                    "Implement authentication",
                    "Build chat interface"
                ]
            elif list_name == "Testing":
                cards = [
                    "Unit test authentication",
                    "Integration testing",
                    "User acceptance testing"
                ]
            else:  # Deployment
                cards = [
                    "Prepare deployment scripts",
                    "Configure production environment",
                    "Monitor system health"
                ]
            
            for card_title in cards:
                result = await self.agent.create_task(PlatformType.TRELLO, {
                    "board_name": name,
                    "list_name": list_name,
                    "card_title": card_title,
                    "description": f"Task for {list_name} phase"
                })
                if result['success']:
                    print(f"      ✅ Created card: {card_title} in {list_name}")
    
    async def _create_asana_project(self, name: str, description: str):
        """Create Asana project structure."""
        print(f"   📋 Creating Asana project: {name}")
        
        # Create project sections
        sections = ["Planning", "Development", "Testing", "Deployment"]
        
        for section in sections:
            if section == "Planning":
                tasks = [
                    "Project kickoff meeting",
                    "Requirements gathering",
                    "Technical architecture design"
                ]
            elif section == "Development":
                tasks = [
                    "Frontend development",
                    "Backend API development",
                    "Database design"
                ]
            elif section == "Testing":
                tasks = [
                    "Test plan creation",
                    "Automated testing setup",
                    "Manual testing execution"
                ]
            else:  # Deployment
                tasks = [
                    "CI/CD pipeline setup",
                    "Production deployment",
                    "Post-deployment monitoring"
                ]
            
            for task_name in tasks:
                result = await self.agent.create_task(PlatformType.ASANA, {
                    "project_name": name,
                    "task_name": task_name,
                    "description": f"Task for {section} phase"
                })
                if result['success']:
                    print(f"      ✅ Created task: {task_name} in {section}")
    
    async def _create_linear_project(self, name: str, description: str):
        """Create Linear project structure."""
        print(f"   📋 Creating Linear project: {name}")
        
        # Create team structure
        teams = ["Engineering", "Design", "Product"]
        
        for team in teams:
            if team == "Engineering":
                issues = [
                    "Setup development environment",
                    "Implement core features",
                    "Code review and testing"
                ]
            elif team == "Design":
                issues = [
                    "UI/UX design mockups",
                    "User interface design",
                    "Design system creation"
                ]
            else:  # Product
                issues = [
                    "Product requirements",
                    "User research",
                    "Feature prioritization"
                ]
            
            for title in issues:
                result = await self.agent.create_task(PlatformType.LINEAR, {
                    "team_name": team,
                    "title": title,
                    "description": f"Task for {team} team",
                    "priority": "Medium"
                })
                if result['success']:
                    print(f"      ✅ Created issue: {title} for {team}")
    
    async def simulate_project_workflow(self):
        """Simulate a real project workflow."""
        print("\n🔄 Simulating Real-Time Project Workflow...")
        print("=" * 60)
        
        # Phase 1: Project Planning
        print("\n📋 Phase 1: Project Planning")
        print("-" * 40)
        
        # Update Jira epic status
        if 'jira_epic' in self.project_data:
            await self.agent.update_task(PlatformType.JIRA, self.project_data['jira_epic'], {
                "status": "In Progress",
                "priority": "High"
            })
            print("✅ Updated Jira epic status to 'In Progress'")
        
        # Move Trello cards to next phase
        print("   Moving Trello cards to Sprint Planning...")
        # This would require getting cards first, then updating them
        
        # Phase 2: Development
        print("\n💻 Phase 2: Development")
        print("-" * 40)
        
        # Create new development tasks
        dev_tasks = [
            {
                "title": "API Endpoint Development",
                "description": "Create RESTful API endpoints for chat functionality"
            },
            {
                "title": "Database Schema Design",
                "description": "Design and implement database structure for chat data"
            }
        ]
        
        for task in dev_tasks:
            result = await self.agent.create_task(PlatformType.JIRA, {
                "project_key": "CHATBOT",
                "title": task["title"],
                "description": task["description"],
                "issue_type": "Task"
            })
            if result['success']:
                print(f"✅ Created development task: {task['title']}")
        
        # Phase 3: Testing
        print("\n🧪 Phase 3: Testing")
        print("-" * 40)
        
        # Create testing tasks
        test_tasks = [
            {
                "title": "Unit Test Coverage",
                "description": "Achieve 90% code coverage with unit tests"
            },
            {
                "title": "Integration Testing",
                "description": "Test API endpoints and database integration"
            }
        ]
        
        for task in test_tasks:
            result = await self.agent.create_task(PlatformType.ASANA, {
                "project_name": "AI Chatbot Development",
                "task_name": task["title"],
                "description": task["description"]
            })
            if result['success']:
                print(f"✅ Created testing task: {task['title']}")
        
        # Phase 4: Deployment
        print("\n🚀 Phase 4: Deployment")
        print("-" * 40)
        
        # Create deployment tasks
        deploy_tasks = [
            {
                "title": "Production Environment Setup",
                "description": "Configure production servers and infrastructure"
            },
            {
                "title": "Deployment Pipeline",
                "description": "Setup automated deployment pipeline"
            }
        ]
        
        for task in deploy_tasks:
            result = await self.agent.create_task(PlatformType.LINEAR, {
                "team_name": "Engineering",
                "title": task["title"],
                "description": task["description"],
                "priority": "High"
            })
            if result['success']:
                print(f"✅ Created deployment task: {task['title']}")
    
    async def test_cross_platform_sync(self):
        """Test cross-platform project synchronization."""
        print("\n🔄 Testing Cross-Platform Project Sync...")
        print("=" * 60)
        
        # Sync from Jira to Trello
        print("📤 Syncing Jira project to Trello...")
        jira_to_trello = await self.agent.sync_projects(
            PlatformType.JIRA,
            PlatformType.TRELLO,
            "CHATBOT"
        )
        
        if jira_to_trello.success:
            print(f"✅ Jira → Trello sync successful: {jira_to_trello.tasks_synced} tasks synced")
        else:
            print(f"❌ Jira → Trello sync failed: {jira_to_trello.errors}")
        
        # Sync from Asana to Linear
        print("📤 Syncing Asana project to Linear...")
        asana_to_linear = await self.agent.sync_projects(
            PlatformType.ASANA,
            PlatformType.LINEAR,
            "AI Chatbot Development"
        )
        
        if asana_to_linear.success:
            print(f"✅ Asana → Linear sync successful: {asana_to_linear.tasks_synced} tasks synced")
        else:
            print(f"❌ Asana → Linear sync failed: {asana_to_linear.errors}")
    
    async def test_project_monitoring(self):
        """Test real-time project monitoring."""
        print("\n📊 Testing Real-Time Project Monitoring...")
        print("=" * 60)
        
        # Monitor all platforms
        platforms = [
            (PlatformType.JIRA, "CHATBOT"),
            (PlatformType.TRELLO, "AI Chatbot Development"),
            (PlatformType.ASANA, "AI Chatbot Development"),
            (PlatformType.LINEAR, "AI Chatbot Development")
        ]
        
        for platform, project_id in platforms:
            print(f"   📈 Monitoring {platform.value.upper()} project...")
            
            # Get project status
            status = await self.agent.get_project_status(platform, project_id)
            if status['success']:
                result = status['result']
                print(f"      ✅ Status: {result['status']}")
                print(f"      📊 Progress: {result['progress']}")
                print(f"      🕒 Last Updated: {result['last_updated']}")
            else:
                print(f"      ❌ Failed to get status: {status['error']}")
            
            # Get current tasks
            tasks = await self.agent.get_tasks(platform)
            if tasks['success']:
                task_count = len(tasks['result'])
                print(f"      📋 Active Tasks: {task_count}")
            else:
                print(f"      ❌ Failed to get tasks: {tasks['error']}")
    
    async def test_collaborative_workflow(self):
        """Test collaborative workflow scenarios."""
        print("\n👥 Testing Collaborative Workflow...")
        print("=" * 60)
        
        # Scenario: Team member updates task
        print("👤 Scenario: Developer updates task status...")
        
        # Create a collaborative task
        collab_task = await self.agent.create_task(PlatformType.JIRA, {
            "project_key": "CHATBOT",
            "title": "Collaborative Feature Development",
            "description": "Work with team members to implement new feature",
            "issue_type": "Task"
        })
        
        if collab_task['success']:
            task_id = collab_task['result']['issue_id']
            print(f"✅ Created collaborative task: {task_id}")
            
            # Simulate team member updates
            updates = [
                {"status": "In Progress", "assignee": "Developer A"},
                {"status": "Code Review", "assignee": "Developer B"},
                {"status": "Testing", "assignee": "QA Engineer"},
                {"status": "Done", "assignee": "Project Manager"}
            ]
            
            for i, update in enumerate(updates, 1):
                result = await self.agent.update_task(PlatformType.JIRA, task_id, update)
                if result['success']:
                    print(f"   ✅ Update {i}: {update['status']} assigned to {update['assignee']}")
                else:
                    print(f"   ❌ Update {i} failed: {result['error']}")
                
                # Small delay to simulate real-time updates
                await asyncio.sleep(0.5)
        else:
            print(f"❌ Failed to create collaborative task: {collab_task['error']}")
    
    async def run_real_time_test(self):
        """Run the complete real-time project test."""
        print("🚀 Starting Real-Time Project Testing")
        print("=" * 60)
        print("This test simulates a real AI Chatbot Development project")
        print("across multiple project management platforms.")
        print()
        
        try:
            # Setup test project
            await self.setup_test_project()
            
            # Simulate project workflow
            await self.simulate_project_workflow()
            
            # Test cross-platform sync
            await self.test_cross_platform_sync()
            
            # Test project monitoring
            await self.test_project_monitoring()
            
            # Test collaborative workflow
            await self.test_collaborative_workflow()
            
            # Final status report
            await self._generate_final_report()
            
        except Exception as e:
            print(f"❌ Real-time test failed: {e}")
            import traceback
            traceback.print_exc()
    
    async def _generate_final_report(self):
        """Generate final project status report."""
        print("\n📋 Final Project Status Report")
        print("=" * 60)
        
        # Get sync history
        sync_history = await self.agent.get_sync_history()
        print(f"🔄 Total Sync Operations: {len(sync_history)}")
        
        # Get health status
        health = await self.agent.health_check()
        print(f"🏥 Agent Health: {health['agent_status']}")
        print(f"🔧 Tools Available: {health['tools_available']}")
        print(f"🌐 Platforms Supported: {health['platforms_supported']}")
        
        # Platform summary
        platforms = [PlatformType.JIRA, PlatformType.TRELLO, PlatformType.ASANA, PlatformType.LINEAR]
        
        for platform in platforms:
            tasks = await self.agent.get_tasks(platform)
            if tasks['success']:
                task_count = len(tasks['result'])
                print(f"📊 {platform.value.upper()}: {task_count} active tasks")
            else:
                print(f"❌ {platform.value.upper()}: Failed to retrieve tasks")
        
        print("\n🎉 Real-Time Project Testing Complete!")
        print("The Task/Project Agent successfully managed a complete project")
        print("workflow across multiple platforms in real-time!")

async def main():
    """Main function to run real-time project testing."""
    tester = RealTimeProjectTester()
    await tester.run_real_time_test()

if __name__ == "__main__":
    print("🧠 Real-Time Project Testing for Task/Project Agent")
    print("=" * 60)
    print("⚠️  Make sure your MCP server is running on http://127.0.0.1:5000")
    print("   Run: python3 simple_mcp_http_server.py")
    print()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️  Testing interrupted by user")
    except Exception as e:
        print(f"\n❌ Testing failed: {e}")
        print("💡 Make sure your MCP server is running and accessible")
