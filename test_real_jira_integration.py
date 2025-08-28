#!/usr/bin/env python3
"""
Real Jira Integration Testing
Demonstrates actual Jira instance connectivity and real-time project management.
"""

import asyncio
import sys
import os
import json
from datetime import datetime

# Add the agent directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'agent'))

from agent.jira_real_integration import RealJiraIntegration, JiraConfig

class RealJiraTester:
    """Test real Jira integration capabilities."""
    
    def __init__(self, config_file: str = "jira_config.json"):
        self.config_file = config_file
        self.jira = None
        self.config = None
        
    def load_config(self) -> bool:
        """Load Jira configuration from file."""
        try:
            if not os.path.exists(self.config_file):
                print(f"❌ Configuration file not found: {self.config_file}")
                print("💡 Please copy jira_config_template.json to jira_config.json and configure your credentials")
                return False
            
            with open(self.config_file, 'r') as f:
                config_data = json.load(f)
            
            jira_config = config_data.get('jira', {})
            
            # Check if credentials are configured
            if (jira_config.get('base_url') == 'https://your-domain.atlassian.net' or
                jira_config.get('username') == 'your-email@example.com' or
                jira_config.get('api_token') == 'your-api-token-here'):
                print("❌ Please configure your actual Jira credentials in jira_config.json")
                print("💡 Update the template values with your real Jira instance details")
                return False
            
            self.config = JiraConfig(
                base_url=jira_config['base_url'],
                username=jira_config['username'],
                api_token=jira_config['api_token'],
                project_key=jira_config['project_key'],
                verify_ssl=jira_config.get('verify_ssl', True)
            )
            
            print("✅ Jira configuration loaded successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to load configuration: {e}")
            return False
    
    async def test_connection(self):
        """Test connection to real Jira instance."""
        print("\n🔗 Testing Real Jira Connection...")
        print("=" * 50)
        
        try:
            self.jira = RealJiraIntegration(self.config)
            connection = await self.jira.test_connection()
            
            if connection['success']:
                print(f"✅ Connected to Jira successfully!")
                print(f"   👤 User: {connection['user']}")
                print(f"   📧 Email: {connection['email']}")
                print(f"   🆔 Account ID: {connection['account_id']}")
                return True
            else:
                print(f"❌ Connection failed: {connection['error']}")
                if 'details' in connection:
                    print(f"   Details: {connection['details']}")
                return False
                
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return False
    
    async def test_project_info(self):
        """Test getting real project information."""
        print("\n📋 Testing Project Information Retrieval...")
        print("=" * 50)
        
        try:
            project = await self.jira.get_project_info()
            
            if project['success']:
                proj_data = project['project']
                print(f"✅ Project retrieved successfully!")
                print(f"   🔑 Key: {proj_data['key']}")
                print(f"   📝 Name: {proj_data['name']}")
                print(f"   👥 Lead: {proj_data['lead']}")
                print(f"   🏷️  Category: {proj_data['category']}")
                print(f"   🔧 Type: {proj_data['project_type']}")
                return True
            else:
                print(f"❌ Failed to get project info: {project['error']}")
                return False
                
        except Exception as e:
            print(f"❌ Project info error: {e}")
            return False
    
    async def test_issue_creation(self):
        """Test creating real issues in Jira."""
        print("\n➕ Testing Real Issue Creation...")
        print("=" * 50)
        
        try:
            # Create a test issue
            issue_data = {
                "project_key": self.config.project_key,
                "summary": f"Test Issue - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "description": "This is a test issue created by the Task/Project Agent for real-time testing.",
                "issue_type": "Task",
                "priority": "Medium",
                "labels": ["test", "automation", "agent"],
                "components": ["Testing"]
            }
            
            result = await self.jira.create_real_issue(issue_data)
            
            if result['success']:
                print(f"✅ Issue created successfully!")
                print(f"   🔑 Issue Key: {result['issue']['key']}")
                print(f"   🆔 Issue ID: {result['issue']['id']}")
                print(f"   📝 Summary: {issue_data['summary']}")
                
                # Store the issue key for later testing
                self.test_issue_key = result['issue']['key']
                return True
            else:
                print(f"❌ Failed to create issue: {result['error']}")
                return False
                
        except Exception as e:
            print(f"❌ Issue creation error: {e}")
            return False
    
    async def test_issue_retrieval(self):
        """Test retrieving real issues from Jira."""
        print("\n📥 Testing Real Issue Retrieval...")
        print("=" * 50)
        
        try:
            # Get recent issues
            issues = await self.jira.get_real_issues()
            
            if issues['success']:
                print(f"✅ Retrieved {issues['total']} issues successfully!")
                print(f"   📊 Total Issues: {issues['total']}")
                print(f"   📋 Recent Issues:")
                
                for i, issue in enumerate(issues['issues'][:5], 1):  # Show first 5
                    print(f"      {i}. {issue['key']}: {issue['summary']}")
                    print(f"         Status: {issue['status']}, Assignee: {issue['assignee']}")
                    print(f"         Priority: {issue['priority']}")
                
                if len(issues['issues']) > 5:
                    print(f"      ... and {len(issues['issues']) - 5} more issues")
                
                return True
            else:
                print(f"❌ Failed to retrieve issues: {issues['error']}")
                return False
                
        except Exception as e:
            print(f"❌ Issue retrieval error: {e}")
            return False
    
    async def test_issue_update(self):
        """Test updating real issues in Jira."""
        print("\n✏️  Testing Real Issue Updates...")
        print("=" * 50)
        
        if not hasattr(self, 'test_issue_key'):
            print("❌ No test issue available for updating")
            return False
        
        try:
            # Update the test issue
            updates = {
                "summary": f"Updated Test Issue - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "description": "This issue has been updated by the Task/Project Agent to test real-time updates.",
                "priority": "High",
                "labels": ["test", "automation", "agent", "updated"]
            }
            
            result = await self.jira.update_real_issue(self.test_issue_key, updates)
            
            if result['success']:
                print(f"✅ Issue {self.test_issue_key} updated successfully!")
                print(f"   📝 New Summary: {updates['summary']}")
                print(f"   🏷️  New Labels: {', '.join(updates['labels'])}")
                print(f"   ⚡ Priority: {updates['priority']}")
                return True
            else:
                print(f"❌ Failed to update issue: {result['error']}")
                return False
                
        except Exception as e:
            print(f"❌ Issue update error: {e}")
            return False
    
    async def test_workflow_management(self):
        """Test Jira workflow and status management."""
        print("\n🔄 Testing Workflow Management...")
        print("=" * 50)
        
        try:
            # Get project workflow information
            workflow = await self.jira.get_project_workflow()
            
            if workflow['success']:
                print(f"✅ Workflow information retrieved successfully!")
                print(f"   🔑 Project: {workflow['project_key']}")
                print(f"   📋 Available Workflows:")
                
                for issue_type, statuses in workflow['workflows'].items():
                    print(f"      {issue_type}:")
                    for status in statuses:
                        print(f"         - {status['name']} ({status['category']})")
                
                return True
            else:
                print(f"❌ Failed to get workflow info: {workflow['error']}")
                return False
                
        except Exception as e:
            print(f"❌ Workflow error: {e}")
            return False
    
    async def test_advanced_search(self):
        """Test advanced JQL search capabilities."""
        print("\n🔍 Testing Advanced JQL Search...")
        print("=" * 50)
        
        try:
            # Test different JQL queries
            test_queries = [
                f"project = {self.config.project_key} AND status = 'To Do'",
                f"project = {self.config.project_key} AND priority = 'High'",
                f"project = {self.config.project_key} AND created >= -7d",
                f"project = {self.config.project_key} AND assignee = currentUser()"
            ]
            
            for i, jql in enumerate(test_queries, 1):
                print(f"   Query {i}: {jql}")
                
                result = await self.jira.search_issues_advanced(jql, max_results=10)
                
                if result['success']:
                    print(f"      ✅ Found {result['total']} issues")
                    if result['issues']:
                        print(f"      📋 Sample: {result['issues'][0]['key']} - {result['issues'][0]['summary']}")
                else:
                    print(f"      ❌ Search failed: {result['error']}")
                
                print()
            
            return True
            
        except Exception as e:
            print(f"❌ Advanced search error: {e}")
            return False
    
    async def test_real_time_monitoring(self):
        """Test real-time project monitoring capabilities."""
        print("\n📊 Testing Real-Time Project Monitoring...")
        print("=" * 50)
        
        try:
            # Get current project status
            issues = await self.jira.get_real_issues()
            
            if issues['success']:
                print(f"✅ Real-time monitoring active!")
                print(f"   📊 Project: {self.config.project_key}")
                print(f"   📋 Total Issues: {issues['total']}")
                
                # Analyze issue distribution
                status_counts = {}
                priority_counts = {}
                
                for issue in issues['issues']:
                    status = issue['status']
                    priority = issue['priority']
                    
                    status_counts[status] = status_counts.get(status, 0) + 1
                    priority_counts[priority] = priority_counts.get(priority, 0) + 1
                
                print(f"   📈 Status Distribution:")
                for status, count in status_counts.items():
                    print(f"      {status}: {count} issues")
                
                print(f"   🎯 Priority Distribution:")
                for priority, count in priority_counts.items():
                    print(f"      {priority}: {count} issues")
                
                return True
            else:
                print(f"❌ Monitoring failed: {issues['error']}")
                return False
                
        except Exception as e:
            print(f"❌ Monitoring error: {e}")
            return False
    
    async def run_comprehensive_test(self):
        """Run comprehensive real Jira integration testing."""
        print("🚀 Real Jira Integration Testing")
        print("=" * 60)
        print("This test demonstrates actual connectivity to real Jira instances")
        print("and real-time project management capabilities.")
        print()
        
        # Load configuration
        if not self.load_config():
            return
        
        try:
            # Test connection
            if not await self.test_connection():
                return
            
            # Test project information
            if not await self.test_project_info():
                return
            
            # Test issue creation
            if not await self.test_issue_creation():
                return
            
            # Test issue retrieval
            if not await self.test_issue_retrieval():
                return
            
            # Test issue updates
            if not await self.test_issue_update():
                return
            
            # Test workflow management
            if not await self.test_workflow_management():
                return
            
            # Test advanced search
            if not await self.test_advanced_search():
                return
            
            # Test real-time monitoring
            if not await self.test_real_time_monitoring():
                return
            
            # Final summary
            print("\n🎉 Real Jira Integration Testing Complete!")
            print("=" * 60)
            print("✅ All tests passed successfully!")
            print("🌐 The Task/Project Agent is now connected to your real Jira instance")
            print("📊 Real-time project management is fully operational")
            print("🔄 You can now manage actual projects, create real issues, and")
            print("   monitor project progress in real-time!")
            
        except Exception as e:
            print(f"❌ Comprehensive test failed: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            # Clean up
            if self.jira:
                await self.jira.close()

async def main():
    """Main function to run real Jira integration testing."""
    tester = RealJiraTester()
    await tester.run_comprehensive_test()

if __name__ == "__main__":
    print("🔗 Real Jira Integration Testing")
    print("=" * 60)
    print("⚠️  Before running this test:")
    print("   1. Copy jira_config_template.json to jira_config.json")
    print("   2. Configure your actual Jira credentials")
    print("   3. Ensure your Jira instance is accessible")
    print()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️  Testing interrupted by user")
    except Exception as e:
        print(f"\n❌ Testing failed: {e}")
        print("💡 Make sure your Jira configuration is correct and accessible")
