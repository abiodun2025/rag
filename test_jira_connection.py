#!/usr/bin/env python3
"""
Test Jira Connection
Simple script to verify your Jira credentials and connection.
"""

import os
import json
import sys
from datetime import datetime

# Add the agent directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'agent'))

from agent.jira_real_integration import RealJiraIntegration, JiraConfig

async def test_jira_connection():
    """Test connection to Jira with your credentials."""
    
    print("🔗 Testing Jira Connection")
    print("=" * 50)
    
    # Check if config file exists
    config_file = "jira_config.json"
    if not os.path.exists(config_file):
        print(f"❌ Configuration file not found: {config_file}")
        print("💡 Please create jira_config.json with your Jira credentials")
        print("   Example:")
        print("   {")
        print('     "jira": {')
        print('       "base_url": "https://your-company.atlassian.net",')
        print('       "username": "your-email@company.com",')
        print('       "api_token": "your-api-token",')
        print('       "project_key": "PROJ"')
        print("     }")
        print("   }")
        return False
    
    try:
        # Load configuration
        with open(config_file, 'r') as f:
            config_data = json.load(f)
        
        jira_config = config_data.get('jira', {})
        
        # Check if credentials are configured
        if (jira_config.get('base_url') == 'https://your-domain.atlassian.net' or
            jira_config.get('username') == 'your-email@example.com' or
            jira_config.get('api_token') == 'your-api-token-here'):
            print("❌ Please configure your actual Jira credentials in jira_config.json")
            print("💡 Update the template values with your real Jira instance details")
            return False
        
        print("✅ Configuration loaded successfully")
        print(f"   🌐 Base URL: {jira_config['base_url']}")
        print(f"   👤 Username: {jira_config['username']}")
        print(f"   🔑 API Token: {jira_config['api_token'][:10]}...")
        print(f"   🔑 Project Key: {jira_config['project_key']}")
        print()
        
        # Create Jira integration instance
        config = JiraConfig(
            base_url=jira_config['base_url'],
            username=jira_config['username'],
            api_token=jira_config['api_token'],
            project_key=jira_config['project_key'],
            verify_ssl=jira_config.get('verify_ssl', True)
        )
        
        jira = RealJiraIntegration(config)
        
        # Test connection
        print("🔗 Testing connection to Jira...")
        connection = await jira.test_connection()
        
        if connection['success']:
            print("✅ Connected to Jira successfully!")
            print(f"   👤 User: {connection['user']}")
            print(f"   📧 Email: {connection['email']}")
            print(f"   🆔 Account ID: {connection['account_id']}")
            print()
            
            # Test project access
            print("📋 Testing project access...")
            project = await jira.get_project_info()
            
            if project['success']:
                proj_data = project['project']
                print("✅ Project access successful!")
                print(f"   🔑 Project Key: {proj_data['key']}")
                print(f"   📝 Project Name: {proj_data['name']}")
                print(f"   👥 Project Lead: {proj_data['lead']}")
                print(f"   🏷️  Category: {proj_data['category']}")
                print()
                
                # Test issue retrieval
                print("📥 Testing issue retrieval...")
                issues = await jira.get_real_issues()
                
                if issues['success']:
                    print("✅ Issue retrieval successful!")
                    print(f"   📋 Total Issues: {issues['total']}")
                    print(f"   📊 Recent Issues:")
                    
                    for i, issue in enumerate(issues['issues'][:3], 1):
                        print(f"      {i}. {issue['key']}: {issue['summary']}")
                        print(f"         Status: {issue['status']}, Priority: {issue['priority']}")
                    
                    print()
                    print("🎉 All tests passed! Your Jira Agent is ready to use.")
                    return True
                else:
                    print(f"❌ Issue retrieval failed: {issues['error']}")
                    return False
            else:
                print(f"❌ Project access failed: {project['error']}")
                return False
                
        else:
            print(f"❌ Connection failed: {connection['error']}")
            if 'details' in connection:
                print(f"   Details: {connection['details']}")
            
            print("\n🔍 Troubleshooting Tips:")
            print("   1. Check your Jira URL is correct")
            print("   2. Verify your username/email is correct")
            print("   3. Ensure your API token is valid and not expired")
            print("   4. Check if your Jira instance requires VPN access")
            print("   5. Verify your account has access to the project")
            return False
            
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        print("\n🔍 Common Issues:")
        print("   1. Network connectivity to Jira instance")
        print("   2. SSL certificate verification")
        print("   3. Firewall or proxy blocking connection")
        print("   4. Jira instance maintenance or downtime")
        return False
    
    finally:
        if 'jira' in locals():
            await jira.close()

async def main():
    """Main function to test Jira connection."""
    success = await test_jira_connection()
    
    if success:
        print("\n🚀 Next Steps:")
        print("   1. Your Jira Agent is now connected and ready!")
        print("   2. Test the notification agent: python3 test_jira_notification_agent.py")
        print("   3. Run integration examples: python3 jira_email_integration_examples.py")
        print("   4. Start using real-time project management!")
    else:
        print("\n⚠️  Please fix the connection issues before proceeding.")
        print("   Check the troubleshooting tips above.")

if __name__ == "__main__":
    print("🔗 Jira Connection Test")
    print("=" * 50)
    print("This script tests your Jira credentials and connection.")
    print("Make sure you have configured jira_config.json first.")
    print()
    
    try:
        import asyncio
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        print("💡 Make sure you have the required dependencies installed")
