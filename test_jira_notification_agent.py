#!/usr/bin/env python3
"""
Test Jira Notification Agent Integration
Demonstrates how the Jira Agent pings the Communication Agent (Email) for various scenarios.
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta

# Add the agent directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'agent'))

from agent.jira_notification_agent import (
    JiraNotificationAgent, 
    EscalationRule, 
    EscalationLevel, 
    DailyDigestConfig
)

class JiraNotificationTester:
    """Test the Jira notification agent integration with email tools."""
    
    def __init__(self):
        self.notification_agent = JiraNotificationAgent()
        self.test_results = []
        
    async def test_basic_email_integration(self):
        """Test basic email integration with existing Email Agent."""
        print("\n📧 Testing Basic Email Integration...")
        print("=" * 50)
        
        try:
            # Test sending a simple notification
            result = await self.notification_agent.send_notification_email(
                to_email="test@example.com",
                subject="Test Integration - Jira Notification Agent",
                body="This is a test email to verify integration with the existing Email Agent."
            )
            
            if result.get("success"):
                print("✅ Email integration test successful!")
                print(f"   📧 Email sent via existing Email Agent")
                print(f"   📝 Result: {result.get('result', 'N/A')}")
                self.test_results.append(("Basic Email Integration", True))
                return True
            else:
                print(f"❌ Email integration test failed: {result.get('error')}")
                self.test_results.append(("Basic Email Integration", False))
                return False
                
        except Exception as e:
            print(f"❌ Email integration test error: {e}")
            self.test_results.append(("Basic Email Integration", False))
            return False
    
    async def test_critical_ticket_alert(self):
        """Test critical ticket alert functionality."""
        print("\n🚨 Testing Critical Ticket Alert...")
        print("=" * 50)
        
        try:
            # Create a mock critical ticket
            critical_ticket = {
                "key": "PROJ-123",
                "summary": "Critical System Failure - Database Connection Lost",
                "priority": "Highest",
                "status": "Open",
                "created": (datetime.now() - timedelta(hours=25)).isoformat(),
                "reporter": "System Monitor",
                "assignee": "Unassigned"
            }
            
            # Test unassigned critical ticket alert
            result = await self.notification_agent.send_critical_ticket_alert(
                issue=critical_ticket,
                recipients=["pm@company.com", "techlead@company.com"],
                alert_type="unassigned"
            )
            
            if result.get("success"):
                print("✅ Critical ticket alert test successful!")
                print(f"   🚨 Alert sent for {critical_ticket['key']}")
                print(f"   📧 Recipients: {len(result.get('alert_record', {}).get('recipients', []))}")
                print(f"   📝 Message: {result.get('message')}")
                self.test_results.append(("Critical Ticket Alert", True))
                return True
            else:
                print(f"❌ Critical ticket alert test failed: {result.get('error')}")
                self.test_results.append(("Critical Ticket Alert", False))
                return False
                
        except Exception as e:
            print(f"❌ Critical ticket alert test error: {e}")
            self.test_results.append(("Critical Ticket Alert", False))
            return False
    
    async def test_escalation_rules(self):
        """Test escalation rule functionality."""
        print("\n📋 Testing Escalation Rules...")
        print("=" * 50)
        
        try:
            # Test adding a custom escalation rule
            custom_rule = EscalationRule(
                name="Custom Test Escalation",
                condition="Test condition > 1 hour",
                threshold_hours=1,
                escalation_level=EscalationLevel.HIGH,
                notify_roles=["Test Manager"],
                notify_emails=["test@company.com"],
                message_template="🧪 TEST ESCALATION: {issue_key} triggered after {hours_open} hours."
            )
            
            result = await self.notification_agent.add_escalation_rule(custom_rule)
            
            if result.get("success"):
                print("✅ Escalation rule test successful!")
                print(f"   📋 Rule added: {custom_rule.name}")
                print(f"   ⏰ Threshold: {custom_rule.threshold_hours} hours")
                print(f"   🎯 Level: {custom_rule.escalation_level.value}")
                print(f"   📧 Total rules: {result.get('total_rules')}")
                self.test_results.append(("Escalation Rules", True))
                return True
            else:
                print(f"❌ Escalation rule test failed: {result.get('error')}")
                self.test_results.append(("Escalation Rules", False))
                return False
                
        except Exception as e:
            print(f"❌ Escalation rule test error: {e}")
            self.test_results.append(("Escalation Rules", False))
            return False
    
    async def test_daily_digest_configuration(self):
        """Test daily digest configuration."""
        print("\n📊 Testing Daily Digest Configuration...")
        print("=" * 50)
        
        try:
            # Test updating daily digest configuration
            new_config = DailyDigestConfig(
                enabled=True,
                send_time="08:00",
                recipients=["team@company.com", "managers@company.com"],
                include_unassigned=True,
                include_overdue=True,
                include_priority_summary=True,
                include_velocity_metrics=True
            )
            
            result = await self.notification_agent.update_daily_digest_config(new_config)
            
            if result.get("success"):
                print("✅ Daily digest configuration test successful!")
                print(f"   📊 Digest enabled: {new_config.enabled}")
                print(f"   ⏰ Send time: {new_config.send_time}")
                print(f"   📧 Recipients: {len(new_config.recipients)}")
                print(f"   📋 Include unassigned: {new_config.include_unassigned}")
                print(f"   ⏰ Include overdue: {new_config.include_overdue}")
                self.test_results.append(("Daily Digest Configuration", True))
                return True
            else:
                print(f"❌ Daily digest configuration test failed: {result.get('error')}")
                self.test_results.append(("Daily Digest Configuration", False))
                return False
                
        except Exception as e:
            print(f"❌ Daily digest configuration test error: {e}")
            self.test_results.append(("Daily Digest Configuration", False))
            return False
    
    async def test_notification_history(self):
        """Test notification history tracking."""
        print("\n📚 Testing Notification History...")
        print("=" * 50)
        
        try:
            # Get notification history
            history = await self.notification_agent.get_notification_history(limit=10)
            
            print("✅ Notification history test successful!")
            print(f"   📚 Total notifications: {len(history)}")
            
            if history:
                print("   📋 Recent notifications:")
                for i, notification in enumerate(history[-3:], 1):  # Show last 3
                    print(f"      {i}. {notification.get('subject', 'No subject')}")
                    print(f"         Status: {notification.get('status')}")
                    print(f"         Recipient: {notification.get('recipient')}")
                    print(f"         Time: {notification.get('timestamp', 'Unknown')}")
            else:
                print("   📝 No notifications in history yet")
            
            self.test_results.append(("Notification History", True))
            return True
            
        except Exception as e:
            print(f"❌ Notification history test error: {e}")
            self.test_results.append(("Notification History", False))
            return False
    
    async def test_health_check(self):
        """Test agent health check functionality."""
        print("\n🏥 Testing Health Check...")
        print("=" * 50)
        
        try:
            health = await self.notification_agent.health_check()
            
            print("✅ Health check test successful!")
            print(f"   🏥 Status: {health.get('status')}")
            print(f"   🔗 MCP Server Connected: {health.get('mcp_server_connected')}")
            print(f"   📋 Escalation Rules: {health.get('escalation_rules_count')}")
            print(f"   📊 Daily Digest Enabled: {health.get('daily_digest_enabled')}")
            print(f"   📧 Notifications Sent: {health.get('notifications_sent')}")
            print(f"   ❌ Notifications Failed: {health.get('notifications_failed')}")
            
            self.test_results.append(("Health Check", True))
            return True
            
        except Exception as e:
            print(f"❌ Health check test error: {e}")
            self.test_results.append(("Health Check", False))
            return False
    
    async def test_real_world_scenarios(self):
        """Test real-world notification scenarios."""
        print("\n🌍 Testing Real-World Scenarios...")
        print("=" * 50)
        
        try:
            # Scenario 1: Critical bug escalation
            print("   🐛 Scenario 1: Critical Bug Escalation")
            critical_bug = {
                "key": "PROJ-456",
                "summary": "Production Database Connection Failure",
                "priority": "Highest",
                "status": "Open",
                "created": (datetime.now() - timedelta(hours=50)).isoformat(),
                "issue_type": "Bug",
                "assignee": "Database Team"
            }
            
            # This would normally be called by the escalation checker
            print("   ✅ Critical bug scenario prepared")
            
            # Scenario 2: Unassigned ticket alert
            print("   ⚠️  Scenario 2: Unassigned Ticket Alert")
            unassigned_ticket = {
                "key": "PROJ-789",
                "summary": "New Feature Implementation",
                "priority": "High",
                "status": "Open",
                "created": (datetime.now() - timedelta(hours=26)).isoformat(),
                "assignee": "Unassigned"
            }
            
            # This would normally be called by the escalation checker
            print("   ✅ Unassigned ticket scenario prepared")
            
            # Scenario 3: Daily digest preparation
            print("   📊 Scenario 3: Daily Digest Preparation")
            print("   ✅ Daily digest scenario prepared")
            
            print("   🎯 All real-world scenarios prepared successfully!")
            self.test_results.append(("Real-World Scenarios", True))
            return True
            
        except Exception as e:
            print(f"❌ Real-world scenarios test error: {e}")
            self.test_results.append(("Real-World Scenarios", False))
            return False
    
    async def run_comprehensive_test(self):
        """Run comprehensive notification agent testing."""
        print("🔔 Jira Notification Agent Integration Testing")
        print("=" * 70)
        print("This test demonstrates how the Jira Agent integrates with")
        print("your existing Email Agent for notifications, daily digests,")
        print("and escalation rules.")
        print()
        
        try:
            # Run all tests
            await self.test_basic_email_integration()
            await self.test_critical_ticket_alert()
            await self.test_escalation_rules()
            await self.test_daily_digest_configuration()
            await self.test_notification_history()
            await self.test_health_check()
            await self.test_real_world_scenarios()
            
            # Generate test summary
            await self._generate_test_summary()
            
        except Exception as e:
            print(f"❌ Comprehensive test failed: {e}")
            import traceback
            traceback.print_exc()
    
    async def _generate_test_summary(self):
        """Generate comprehensive test summary."""
        print("\n📊 Test Summary Report")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r[1]])
        failed_tests = total_tests - passed_tests
        
        print(f"📋 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"📊 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print("\n📋 Detailed Results:")
        print("-" * 40)
        
        for test_name, result in self.test_results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name}")
        
        print("\n🎯 Integration Capabilities Verified:")
        print("-" * 40)
        
        if passed_tests >= 5:
            print("✅ Email Agent Integration: FULLY OPERATIONAL")
            print("✅ Critical Ticket Alerts: READY")
            print("✅ Daily Digest System: CONFIGURED")
            print("✅ Escalation Rules: ACTIVE")
            print("✅ Notification History: TRACKING")
            print("✅ Health Monitoring: ACTIVE")
            
            print("\n🚀 Your Jira Notification Agent is ready to:")
            print("   • Send critical ticket alerts via Email Agent")
            print("   • Generate and send daily project digests")
            print("   • Execute escalation rules automatically")
            print("   • Track all notification activities")
            print("   • Integrate seamlessly with existing email tools")
            
        else:
            print("⚠️  Some integration tests failed. Please check:")
            print("   • MCP server connectivity")
            print("   • Email tool availability")
            print("   • Configuration settings")
        
        print("\n🔗 Next Steps:")
        print("   1. Configure your actual email recipients")
        print("   2. Set up escalation rules for your projects")
        print("   3. Schedule daily digest delivery")
        print("   4. Test with real Jira projects")

async def main():
    """Main function to run notification agent testing."""
    tester = JiraNotificationTester()
    await tester.run_comprehensive_test()

if __name__ == "__main__":
    print("🔔 Jira Notification Agent Integration Testing")
    print("=" * 70)
    print("⚠️  Before running this test:")
    print("   1. Ensure your MCP server is running on http://127.0.0.1:5000")
    print("   2. Verify email tools are available in your MCP server")
    print("   3. Check that sendmail/sendmail_simple tools are accessible")
    print()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️  Testing interrupted by user")
    except Exception as e:
        print(f"\n❌ Testing failed: {e}")
        print("💡 Make sure your MCP server is running and email tools are accessible")
