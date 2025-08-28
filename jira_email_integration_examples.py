#!/usr/bin/env python3
"""
Jira Agent + Email Agent Integration Examples
Demonstrates real-world scenarios where Jira Agent pings Email Agent for notifications.
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
import json

# Add the agent directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'agent'))

from agent.jira_notification_agent import (
    JiraNotificationAgent, 
    EscalationRule, 
    EscalationLevel, 
    DailyDigestConfig
)
from agent.jira_real_integration import RealJiraIntegration, JiraConfig

class JiraEmailIntegrationExamples:
    """Examples of Jira Agent pinging Email Agent for various scenarios."""
    
    def __init__(self, mcp_server_url: str = "http://127.0.0.1:5000"):
        self.mcp_server_url = mcp_server_url
        self.notification_agent = JiraNotificationAgent(mcp_server_url)
        self.jira_agent = None
        self.examples_run = []
        
    async def setup_jira_connection(self, config_file: str = "jira_config.json"):
        """Setup connection to real Jira instance."""
        try:
            if not os.path.exists(config_file):
                print(f"⚠️  Jira config file not found: {config_file}")
                print("💡 Using mock Jira data for examples")
                return False
            
            with open(config_file, 'r') as f:
                config_data = json.load(f)
            
            jira_config = config_data.get('jira', {})
            
            # Check if credentials are configured
            if (jira_config.get('base_url') == 'https://your-domain.atlassian.net' or
                jira_config.get('username') == 'your-email@example.com' or
                jira_config.get('api_token') == 'your-api-token-here'):
                print("⚠️  Jira credentials not configured, using mock data")
                return False
            
            self.jira_agent = RealJiraIntegration(JiraConfig(
                base_url=jira_config['base_url'],
                username=jira_config['username'],
                api_token=jira_config['api_token'],
                project_key=jira_config['project_key']
            ))
            
            print("✅ Connected to real Jira instance")
            return True
            
        except Exception as e:
            print(f"⚠️  Jira connection failed: {e}, using mock data")
            return False
    
    async def example_1_critical_ticket_unassigned_24h(self):
        """Example 1: Jira Agent pings Email Agent when critical ticket is unassigned for 24h."""
        print("\n🚨 Example 1: Critical Ticket Unassigned for 24h")
        print("=" * 70)
        print("Scenario: A critical ticket has been unassigned for over 24 hours")
        print("Action: Jira Agent automatically pings Email Agent to send alert")
        print()
        
        try:
            # Simulate a critical unassigned ticket
            critical_ticket = {
                "key": "PROJ-123",
                "summary": "Critical System Failure - Database Connection Lost",
                "priority": "Highest",
                "status": "Open",
                "created": (datetime.now() - timedelta(hours=25)).isoformat(),
                "reporter": "System Monitor",
                "assignee": "Unassigned",
                "issue_type": "Bug"
            }
            
            print("📋 Ticket Details:")
            print(f"   🔑 Key: {critical_ticket['key']}")
            print(f"   📝 Summary: {critical_ticket['summary']}")
            print(f"   🎯 Priority: {critical_ticket['priority']}")
            print(f"   ⏰ Created: {critical_ticket['created']}")
            print(f"   👤 Assignee: {critical_ticket['assignee']}")
            print(f"   ⏰ Hours Unassigned: 25+ hours")
            print()
            
            # Jira Agent pings Email Agent for critical alert
            print("🔔 Jira Agent → Email Agent: Sending Critical Alert")
            print("-" * 50)
            
            result = await self.notification_agent.send_critical_ticket_alert(
                issue=critical_ticket,
                recipients=["pm@company.com", "techlead@company.com", "engineering-manager@company.com"],
                alert_type="unassigned"
            )
            
            if result.get("success"):
                print("✅ Critical ticket alert sent successfully!")
                print(f"   📧 Recipients: {len(result.get('alert_record', {}).get('recipients', []))}")
                print(f"   📝 Message: {result.get('message')}")
                print(f"   🚨 Alert Type: Unassigned Critical Ticket")
                print(f"   ⏰ Escalation: Automatic after 24h")
                
                self.examples_run.append({
                    "example": "Critical Ticket Unassigned 24h",
                    "status": "success",
                    "recipients": result.get('alert_record', {}).get('recipients', []),
                    "alert_type": "unassigned"
                })
                
            else:
                print(f"❌ Critical ticket alert failed: {result.get('error')}")
                self.examples_run.append({
                    "example": "Critical Ticket Unassigned 24h",
                    "status": "failed",
                    "error": result.get('error')
                })
            
            return result.get("success", False)
            
        except Exception as e:
            print(f"❌ Example 1 failed: {e}")
            self.examples_run.append({
                "example": "Critical Ticket Unassigned 24h",
                "status": "error",
                "error": str(e)
            })
            return False
    
    async def example_2_daily_digest_morning(self):
        """Example 2: Every morning, Jira Agent posts 'Today's assigned tickets' into Email."""
        print("\n📊 Example 2: Daily Morning Digest - Today's Assigned Tickets")
        print("=" * 70)
        print("Scenario: Every morning at 9 AM, generate and send project digest")
        print("Action: Jira Agent pings Email Agent to send daily digest to team")
        print()
        
        try:
            # Configure daily digest for morning delivery
            morning_config = DailyDigestConfig(
                enabled=True,
                send_time="09:00",
                recipients=[
                    "team@company.com",
                    "developers@company.com", 
                    "managers@company.com",
                    "stakeholders@company.com"
                ],
                include_unassigned=True,
                include_overdue=True,
                include_priority_summary=True,
                include_velocity_metrics=True
            )
            
            await self.notification_agent.update_daily_digest_config(morning_config)
            
            print("📅 Daily Digest Configuration:")
            print(f"   ⏰ Send Time: {morning_config.send_time}")
            print(f"   📧 Recipients: {len(morning_config.recipients)}")
            print(f"   📋 Include Unassigned: {morning_config.include_unassigned}")
            print(f"   ⏰ Include Overdue: {morning_config.include_overdue}")
            print(f"   🎯 Include Priority Summary: {morning_config.include_priority_summary}")
            print()
            
            # Simulate morning digest generation
            print("🔔 Jira Agent → Email Agent: Generating Morning Digest")
            print("-" * 50)
            
            # Create mock project data for digest
            mock_project_info = {
                "success": True,
                "project": {
                    "key": "PROJ",
                    "name": "AI Chatbot Development",
                    "lead": "John Developer"
                },
                "base_url": "https://company.atlassian.net"
            }
            
            mock_issues_result = {
                "success": True,
                "total": 15,
                "issues": [
                    {
                        "key": "PROJ-101",
                        "summary": "Implement User Authentication",
                        "status": "In Progress",
                        "assignee": "Alice Developer",
                        "priority": "High",
                        "created": (datetime.now() - timedelta(days=2)).isoformat()
                    },
                    {
                        "key": "PROJ-102", 
                        "summary": "Database Schema Design",
                        "status": "Done",
                        "assignee": "Bob Developer",
                        "priority": "Medium",
                        "created": (datetime.now() - timedelta(days=5)).isoformat()
                    },
                    {
                        "key": "PROJ-103",
                        "summary": "API Endpoint Development",
                        "status": "To Do",
                        "assignee": "Charlie Developer",
                        "priority": "High",
                        "created": (datetime.now() - timedelta(days=1)).isoformat()
                    },
                    {
                        "key": "PROJ-104",
                        "summary": "Frontend UI Components",
                        "status": "Open",
                        "assignee": "Unassigned",
                        "priority": "Medium",
                        "created": (datetime.now() - timedelta(hours=12)).isoformat()
                    },
                    {
                        "key": "PROJ-105",
                        "summary": "Testing Framework Setup",
                        "status": "In Progress",
                        "assignee": "Diana QA",
                        "priority": "Low",
                        "created": (datetime.now() - timedelta(days=3)).isoformat()
                    }
                ]
            }
            
            # Generate digest content
            digest_content = await self.notification_agent._generate_daily_digest_content(
                mock_project_info, mock_issues_result, None
            )
            
            print("📊 Digest Content Generated:")
            print(f"   📋 Total Issues: {mock_issues_result['total']}")
            print(f"   📧 Content Length: {len(digest_content)} characters")
            print(f"   🕐 Generated at: {datetime.now().strftime('%H:%M:%S')}")
            print()
            
            # Send digest to all recipients
            print("📧 Sending Daily Digest to Team...")
            email_results = []
            
            for recipient in morning_config.recipients:
                subject = f"📊 Daily Digest: {mock_project_info['project']['name']} - {datetime.now().strftime('%Y-%m-%d')}"
                
                result = await self.notification_agent.send_notification_email(
                    to_email=recipient,
                    subject=subject,
                    body=digest_content
                )
                
                email_results.append({
                    "recipient": recipient,
                    "result": result
                })
                
                if result.get("success"):
                    print(f"   ✅ Sent to: {recipient}")
                else:
                    print(f"   ❌ Failed to send to: {recipient}")
            
            # Summary
            successful_sends = len([r for r in email_results if r["result"].get("success")])
            print(f"\n📊 Daily Digest Summary:")
            print(f"   📧 Total Recipients: {len(morning_config.recipients)}")
            print(f"   ✅ Successful Sends: {successful_sends}")
            print(f"   ❌ Failed Sends: {len(morning_config.recipients) - successful_sends}")
            
            self.examples_run.append({
                "example": "Daily Morning Digest",
                "status": "success",
                "recipients": morning_config.recipients,
                "successful_sends": successful_sends,
                "content_length": len(digest_content)
            })
            
            return successful_sends > 0
            
        except Exception as e:
            print(f"❌ Example 2 failed: {e}")
            self.examples_run.append({
                "example": "Daily Morning Digest",
                "status": "error",
                "error": str(e)
            })
            return False
    
    async def example_3_escalation_rules_p1_bug_48h(self):
        """Example 3: If a P1 bug is open for >48 hours, escalate to engineering manager via Email Agent."""
        print("\n🚨 Example 3: P1 Bug Escalation After 48 Hours")
        print("=" * 70)
        print("Scenario: P1 (highest priority) bug has been open for over 48 hours")
        print("Action: Jira Agent automatically escalates to engineering manager via Email Agent")
        print()
        
        try:
            # Create escalation rule for P1 bugs
            p1_escalation_rule = EscalationRule(
                name="P1 Bug 48h Escalation",
                condition="P1 bug open > 48 hours",
                threshold_hours=48,
                escalation_level=EscalationLevel.CRITICAL,
                notify_roles=["Engineering Manager", "Tech Lead", "CTO"],
                notify_emails=[
                    "engineering-manager@company.com",
                    "tech-lead@company.com", 
                    "cto@company.com"
                ],
                message_template="🚨 CRITICAL ESCALATION: P1 Bug {issue_key} has been open for {hours_open} hours and requires immediate attention from engineering leadership."
            )
            
            # Add the escalation rule
            await self.notification_agent.add_escalation_rule(p1_escalation_rule)
            
            print("📋 P1 Bug Escalation Rule Created:")
            print(f"   📝 Name: {p1_escalation_rule.name}")
            print(f"   ⏰ Threshold: {p1_escalation_rule.threshold_hours} hours")
            print(f"   🎯 Level: {p1_escalation_rule.escalation_level.value}")
            print(f"   📧 Recipients: {len(p1_escalation_rule.notify_emails)}")
            print()
            
            # Simulate a P1 bug that's been open for 50 hours
            p1_bug = {
                "key": "PROJ-456",
                "summary": "Production Database Connection Failure - All Services Down",
                "priority": "Highest",
                "status": "Open",
                "created": (datetime.now() - timedelta(hours=50)).isoformat(),
                "issue_type": "Bug",
                "assignee": "Database Team",
                "reporter": "System Monitor"
            }
            
            print("🐛 P1 Bug Details:")
            print(f"   🔑 Key: {p1_bug['key']}")
            print(f"   📝 Summary: {p1_bug['summary']}")
            print(f"   🎯 Priority: {p1_bug['priority']}")
            print(f"   ⏰ Created: {p1_bug['created']}")
            print(f"   ⏰ Hours Open: 50+ hours")
            print(f"   🚨 Escalation Threshold: 48 hours EXCEEDED")
            print()
            
            # Jira Agent automatically escalates via Email Agent
            print("🔔 Jira Agent → Email Agent: Executing P1 Bug Escalation")
            print("-" * 50)
            
            # Execute escalation
            escalation_result = await self.notification_agent._execute_escalation(
                p1_escalation_rule, p1_bug, None
            )
            
            if "error" not in escalation_result:
                print("✅ P1 Bug escalation executed successfully!")
                print(f"   🚨 Escalation Level: {escalation_result.get('escalation_level')}")
                print(f"   ⏰ Hours Open: {escalation_result.get('hours_open', 'Unknown')}")
                print(f"   📧 Emails Sent: {len(escalation_result.get('email_results', []))}")
                print(f"   📝 Escalation Message: {escalation_result.get('message', 'N/A')}")
                
                # Show email results
                print(f"\n📧 Escalation Email Results:")
                for email_result in escalation_result.get('email_results', []):
                    recipient = email_result.get('email')
                    result = email_result.get('result', {})
                    if result.get('success'):
                        print(f"   ✅ {recipient}: Email sent successfully")
                    else:
                        print(f"   ❌ {recipient}: {result.get('error', 'Unknown error')}")
                
                self.examples_run.append({
                    "example": "P1 Bug 48h Escalation",
                    "status": "success",
                    "escalation_level": escalation_result.get('escalation_level'),
                    "recipients": p1_escalation_rule.notify_emails,
                    "hours_open": escalation_result.get('hours_open')
                })
                
            else:
                print(f"❌ P1 Bug escalation failed: {escalation_result.get('error')}")
                self.examples_run.append({
                    "example": "P1 Bug 48h Escalation",
                    "status": "failed",
                    "error": escalation_result.get('error')
                })
            
            return "error" not in escalation_result
            
        except Exception as e:
            print(f"❌ Example 3 failed: {e}")
            self.examples_run.append({
                "example": "P1 Bug 48h Escalation",
                "status": "error",
                "error": str(e)
            })
            return False
    
    async def example_4_automated_escalation_checker(self):
        """Example 4: Automated escalation checker that runs periodically."""
        print("\n🤖 Example 4: Automated Escalation Checker")
        print("=" * 70)
        print("Scenario: Automated system that checks for escalation conditions")
        print("Action: Jira Agent continuously monitors and escalates via Email Agent")
        print()
        
        try:
            # Simulate checking multiple issues for escalation
            issues_to_check = [
                {
                    "key": "PROJ-789",
                    "summary": "Security Vulnerability - SQL Injection Risk",
                    "priority": "Highest",
                    "status": "Open",
                    "created": (datetime.now() - timedelta(hours=72)).isoformat(),
                    "issue_type": "Bug",
                    "assignee": "Security Team"
                },
                {
                    "key": "PROJ-790",
                    "summary": "Performance Issue - Slow API Response",
                    "priority": "High",
                    "status": "Open",
                    "created": (datetime.now() - timedelta(hours=30)).isoformat(),
                    "issue_type": "Bug",
                    "assignee": "Unassigned"
                },
                {
                    "key": "PROJ-791",
                    "summary": "Feature Request - User Dashboard",
                    "priority": "Medium",
                    "status": "Open",
                    "created": (datetime.now() - timedelta(hours=120)).isoformat(),
                    "issue_type": "Story",
                    "assignee": "Frontend Team"
                }
            ]
            
            print("🔍 Checking Issues for Escalation Conditions...")
            print(f"   📋 Total Issues to Check: {len(issues_to_check)}")
            print()
            
            escalated_count = 0
            
            for issue in issues_to_check:
                print(f"🔍 Checking {issue['key']}: {issue['summary']}")
                print(f"   ⏰ Hours Open: {(datetime.now() - datetime.fromisoformat(issue['created'].replace('Z', '+00:00'))).total_seconds() / 3600:.1f}")
                print(f"   🎯 Priority: {issue['priority']}")
                print(f"   👤 Assignee: {issue['assignee']}")
                
                # Check if any escalation rules apply
                should_escalate = False
                escalation_reason = ""
                
                for rule in self.notification_agent.escalation_rules:
                    if rule.enabled:
                        # Simplified escalation check
                        hours_open = (datetime.now() - datetime.fromisoformat(issue['created'].replace('Z', '+00:00'))).total_seconds() / 3600
                        
                        if hours_open >= rule.threshold_hours:
                            if "P1" in rule.condition and issue['priority'] == "Highest":
                                should_escalate = True
                                escalation_reason = f"P1 bug open for {hours_open:.1f} hours"
                            elif "unassigned" in rule.condition and issue['assignee'] == "Unassigned":
                                should_escalate = True
                                escalation_reason = f"Unassigned for {hours_open:.1f} hours"
                            elif "overdue" in rule.condition and hours_open > 72:
                                should_escalate = True
                                escalation_reason = f"Overdue for {hours_open - 72:.1f} hours"
                
                if should_escalate:
                    print(f"   🚨 ESCALATION NEEDED: {escalation_reason}")
                    
                    # Send escalation email
                    escalation_email = f"""
🚨 ESCALATION ALERT
{'=' * 30}

Issue {issue['key']} requires escalation:

📋 Issue Details:
• Key: {issue['key']}
• Summary: {issue['summary']}
• Priority: {issue['priority']}
• Status: {issue['status']}
• Hours Open: {hours_open:.1f}
• Assignee: {issue['assignee']}

⚠️  Escalation Reason: {escalation_reason}

🔗 View Issue: [Jira Link]
⏰ Escalated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---
📧 Automated escalation by Jira Notification Agent
                    """
                    
                    # Send to appropriate recipients based on issue type
                    if issue['priority'] == "Highest":
                        recipients = ["engineering-manager@company.com", "cto@company.com"]
                    elif issue['assignee'] == "Unassigned":
                        recipients = ["pm@company.com", "tech-lead@company.com"]
                    else:
                        recipients = ["team-lead@company.com"]
                    
                    for recipient in recipients:
                        result = await self.notification_agent.send_notification_email(
                            to_email=recipient,
                            subject=f"🚨 ESCALATION: {issue['key']} - {escalation_reason}",
                            body=escalation_email
                        )
                        
                        if result.get("success"):
                            print(f"      📧 Escalation email sent to: {recipient}")
                        else:
                            print(f"      ❌ Failed to send escalation to: {recipient}")
                    
                    escalated_count += 1
                else:
                    print(f"   ✅ No escalation needed")
                
                print()
            
            print(f"📊 Escalation Check Summary:")
            print(f"   🔍 Issues Checked: {len(issues_to_check)}")
            print(f"   🚨 Issues Escalated: {escalated_count}")
            print(f"   ✅ Issues OK: {len(issues_to_check) - escalated_count}")
            
            self.examples_run.append({
                "example": "Automated Escalation Checker",
                "status": "success",
                "issues_checked": len(issues_to_check),
                "issues_escalated": escalated_count
            })
            
            return True
            
        except Exception as e:
            print(f"❌ Example 4 failed: {e}")
            self.examples_run.append({
                "example": "Automated Escalation Checker",
                "status": "error",
                "error": str(e)
            })
            return False
    
    async def run_all_examples(self):
        """Run all integration examples."""
        print("🔗 Jira Agent + Email Agent Integration Examples")
        print("=" * 80)
        print("This demonstrates real-world scenarios where the Jira Agent")
        print("automatically pings the Email Agent for notifications, daily")
        print("digests, and escalation rules.")
        print()
        
        try:
            # Run all examples
            await self.example_1_critical_ticket_unassigned_24h()
            await self.example_2_daily_digest_morning()
            await self.example_3_escalation_rules_p1_bug_48h()
            await self.example_4_automated_escalation_checker()
            
            # Generate comprehensive summary
            await self._generate_examples_summary()
            
        except Exception as e:
            print(f"❌ Examples execution failed: {e}")
            import traceback
            traceback.print_exc()
    
    async def _generate_examples_summary(self):
        """Generate comprehensive examples summary."""
        print("\n📊 Integration Examples Summary")
        print("=" * 80)
        
        total_examples = len(self.examples_run)
        successful_examples = len([e for e in self.examples_run if e.get("status") == "success"])
        failed_examples = total_examples - successful_examples
        
        print(f"📋 Total Examples: {total_examples}")
        print(f"✅ Successful: {successful_examples}")
        print(f"❌ Failed: {failed_examples}")
        print(f"📊 Success Rate: {(successful_examples/total_examples)*100:.1f}%")
        
        print("\n📋 Examples Executed:")
        print("-" * 50)
        
        for example in self.examples_run:
            status = "✅" if example.get("status") == "success" else "❌"
            print(f"{status} {example.get('example')}")
            
            if example.get("status") == "success":
                if "recipients" in example:
                    print(f"      📧 Recipients: {len(example['recipients'])}")
                if "escalation_level" in example:
                    print(f"      🚨 Level: {example['escalation_level']}")
                if "issues_escalated" in example:
                    print(f"      🔍 Issues Escalated: {example['issues_escalated']}")
            else:
                print(f"      ❌ Error: {example.get('error', 'Unknown error')}")
        
        print("\n🎯 Integration Capabilities Demonstrated:")
        print("-" * 50)
        
        if successful_examples >= 3:
            print("✅ Critical Ticket Alerts: FULLY OPERATIONAL")
            print("✅ Daily Digest System: FULLY OPERATIONAL") 
            print("✅ Escalation Rules: FULLY OPERATIONAL")
            print("✅ Automated Monitoring: FULLY OPERATIONAL")
            
            print("\n🚀 Your Jira Agent can now:")
            print("   • Automatically detect critical unassigned tickets")
            print("   • Send daily project digests to the entire team")
            print("   • Escalate P1 bugs after 48 hours automatically")
            print("   • Continuously monitor and escalate issues")
            print("   • Integrate seamlessly with your existing Email Agent")
            
            print("\n🔗 Key Integration Points:")
            print("   • Jira Agent → Email Agent: Critical ticket alerts")
            print("   • Jira Agent → Email Agent: Daily project digests")
            print("   • Jira Agent → Email Agent: Escalation notifications")
            print("   • Jira Agent → Email Agent: Automated monitoring alerts")
            
        else:
            print("⚠️  Some examples failed. Please check:")
            print("   • MCP server connectivity")
            print("   • Email tool availability")
            print("   • Jira integration configuration")
        
        print("\n🔗 Next Steps:")
        print("   1. Configure real email recipients for your team")
        print("   2. Set up escalation rules for your specific projects")
        print("   3. Schedule daily digest delivery times")
        print("   4. Test with actual Jira projects and issues")
        print("   5. Monitor notification delivery and effectiveness")

async def main():
    """Main function to run all integration examples."""
    examples = JiraEmailIntegrationExamples()
    
    # Try to connect to real Jira (optional)
    await examples.setup_jira_connection()
    
    # Run all examples
    await examples.run_all_examples()

if __name__ == "__main__":
    print("🔗 Jira Agent + Email Agent Integration Examples")
    print("=" * 80)
    print("⚠️  Before running these examples:")
    print("   1. Ensure your MCP server is running on http://127.0.0.1:5000")
    print("   2. Verify email tools (sendmail/sendmail_simple) are accessible")
    print("   3. Optionally configure jira_config.json for real Jira integration")
    print()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️  Examples interrupted by user")
    except Exception as e:
        print(f"\n❌ Examples failed: {e}")
        print("💡 Make sure your MCP server is running and email tools are accessible")
