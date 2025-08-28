#!/usr/bin/env python3
"""
Jira Notification Agent - Integrates with existing Email Agent for notifications
Handles critical ticket alerts, daily digests, and escalation rules.
"""

import asyncio
import logging
import json
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import httpx

logger = logging.getLogger(__name__)

class EscalationLevel(Enum):
    """Escalation levels for different urgency."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class NotificationType(Enum):
    """Types of notifications."""
    CRITICAL_TICKET = "critical_ticket"
    DAILY_DIGEST = "daily_digest"
    ESCALATION = "escalation"
    REMINDER = "reminder"
    STATUS_CHANGE = "status_change"

@dataclass
class EscalationRule:
    """Rule for automatic escalation."""
    name: str
    condition: str
    threshold_hours: int
    escalation_level: EscalationLevel
    notify_roles: List[str]
    notify_emails: List[str]
    message_template: str
    enabled: bool = True

@dataclass
class DailyDigestConfig:
    """Configuration for daily digest emails."""
    enabled: bool = True
    send_time: str = "09:00"  # 9 AM
    recipients: List[str] = None
    include_unassigned: bool = True
    include_overdue: bool = True
    include_priority_summary: bool = True
    include_velocity_metrics: bool = True

class JiraNotificationAgent:
    """Jira notification agent using existing Email Agent from MCP."""
    
    def __init__(self, mcp_server_url: str = "http://127.0.0.1:5000"):
        self.mcp_server_url = mcp_server_url
        self.client = httpx.AsyncClient(timeout=30.0)
        self.escalation_rules = []
        self.daily_digest_config = DailyDigestConfig()
        self.notification_history = []
        self._init_default_rules()
        
        logger.info(f"Jira Notification Agent initialized with MCP server: {mcp_server_url}")
    
    def _init_default_rules(self):
        """Initialize default escalation rules."""
        self.escalation_rules = [
            EscalationRule(
                name="Critical Bug Escalation",
                condition="P1 bug open > 48 hours",
                threshold_hours=48,
                escalation_level=EscalationLevel.CRITICAL,
                notify_roles=["Engineering Manager", "Tech Lead"],
                notify_emails=["manager@company.com", "techlead@company.com"],
                message_template="🚨 CRITICAL ESCALATION: P1 Bug {issue_key} has been open for {hours_open} hours and requires immediate attention."
            ),
            EscalationRule(
                name="Unassigned Ticket Alert",
                condition="Critical ticket unassigned > 24 hours",
                threshold_hours=24,
                escalation_level=EscalationLevel.HIGH,
                notify_roles=["Project Manager", "Team Lead"],
                notify_emails=["pm@company.com", "teamlead@company.com"],
                message_template="⚠️  HIGH PRIORITY: Critical ticket {issue_key} has been unassigned for {hours_open} hours."
            ),
            EscalationRule(
                name="Overdue Task Reminder",
                condition="High priority task overdue > 72 hours",
                threshold_hours=72,
                escalation_level=EscalationLevel.MEDIUM,
                notify_roles=["Team Lead"],
                notify_emails=["teamlead@company.com"],
                message_template="📅 REMINDER: High priority task {issue_key} is overdue by {hours_overdue} hours."
            )
        ]
    
    async def call_mcp_email_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call email tools from the MCP server."""
        try:
            payload = {
                "tool_name": tool_name,
                "arguments": arguments
            }
            
            response = await self.client.post(
                f"{self.mcp_server_url}/call",
                json=payload
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to call MCP email tool: HTTP {response.status_code}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Error calling MCP email tool: {e}")
            return {"success": False, "error": str(e)}
    
    async def send_notification_email(self, to_email: str, subject: str, body: str, 
                                    from_email: str = None) -> Dict[str, Any]:
        """Send notification email using existing Email Agent."""
        try:
            arguments = {
                "to_email": to_email,
                "subject": subject,
                "body": body
            }
            
            if from_email:
                arguments["from_email"] = from_email
            
            result = await self.call_mcp_email_tool("sendmail", arguments)
            
            if result.get("success"):
                logger.info(f"📧 Notification email sent to {to_email}: {subject}")
                self._log_notification(to_email, subject, "email_sent")
            else:
                logger.error(f"📧 Failed to send notification email: {result.get('error')}")
                self._log_notification(to_email, subject, "email_failed", result.get('error'))
            
            return result
            
        except Exception as e:
            logger.error(f"Error sending notification email: {e}")
            return {"success": False, "error": str(e)}
    
    def _log_notification(self, recipient: str, subject: str, status: str, error: str = None):
        """Log notification attempts."""
        notification = {
            "timestamp": datetime.now().isoformat(),
            "recipient": recipient,
            "subject": subject,
            "status": status,
            "error": error
        }
        self.notification_history.append(notification)
        
        # Keep only last 1000 notifications
        if len(self.notification_history) > 1000:
            self.notification_history = self.notification_history[-1000:]
    
    async def check_critical_ticket_escalation(self, jira_agent, project_key: str = None) -> List[Dict[str, Any]]:
        """Check for critical tickets that need escalation."""
        try:
            # Get issues from Jira
            issues_result = await jira_agent.get_real_issues(project_key)
            if not issues_result.get("success"):
                logger.error(f"Failed to get issues for escalation check: {issues_result.get('error')}")
                return []
            
            escalated_issues = []
            current_time = datetime.now()
            
            for issue in issues_result.get("issues", []):
                # Check each escalation rule
                for rule in self.escalation_rules:
                    if not rule.enabled:
                        continue
                    
                    should_escalate = await self._evaluate_escalation_rule(rule, issue, current_time)
                    if should_escalate:
                        escalation_result = await self._execute_escalation(rule, issue, jira_agent)
                        escalated_issues.append(escalation_result)
            
            return escalated_issues
            
        except Exception as e:
            logger.error(f"Error checking critical ticket escalation: {e}")
            return []
    
    async def _evaluate_escalation_rule(self, rule: EscalationRule, issue: Dict[str, Any], 
                                       current_time: datetime) -> bool:
        """Evaluate if an escalation rule should trigger."""
        try:
            # Parse issue creation time
            created_str = issue.get("created")
            if not created_str:
                return False
            
            created_time = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
            hours_open = (current_time - created_time).total_seconds() / 3600
            
            # Check if threshold is met
            if hours_open >= rule.threshold_hours:
                # Additional condition checks based on rule type
                if "P1" in rule.condition and "bug" in rule.condition.lower():
                    # Check if it's a P1 bug
                    priority = issue.get("priority", "").lower()
                    issue_type = issue.get("issue_type", "").lower()
                    return priority == "highest" and "bug" in issue_type
                
                elif "unassigned" in rule.condition:
                    # Check if ticket is unassigned
                    assignee = issue.get("assignee", "")
                    return not assignee or assignee == "Unassigned"
                
                elif "overdue" in rule.condition:
                    # Check if task is overdue
                    due_date = issue.get("due_date")
                    if due_date:
                        due_datetime = datetime.fromisoformat(due_date.replace("Z", "+00:00"))
                        return current_time > due_datetime
                
                # Default: just check time threshold
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error evaluating escalation rule: {e}")
            return False
    
    async def _execute_escalation(self, rule: EscalationRule, issue: Dict[str, Any], 
                                 jira_agent) -> Dict[str, Any]:
        """Execute escalation for a rule and issue."""
        try:
            # Calculate time metrics
            created_str = issue.get("created")
            created_time = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
            current_time = datetime.now()
            hours_open = (current_time - created_time).total_seconds() / 3600
            
            # Format message
            message = rule.message_template.format(
                issue_key=issue.get("key", "UNKNOWN"),
                hours_open=int(hours_open),
                hours_overdue=max(0, int(hours_open - rule.threshold_hours)),
                issue_summary=issue.get("summary", "No summary"),
                priority=issue.get("priority", "No priority"),
                status=issue.get("status", "Unknown status")
            )
            
            # Send escalation emails
            escalation_results = []
            for email in rule.notify_emails:
                subject = f"🚨 ESCALATION: {rule.name} - {issue.get('key', 'UNKNOWN')}"
                result = await self.send_notification_email(
                    to_email=email,
                    subject=subject,
                    body=message
                )
                escalation_results.append({
                    "email": email,
                    "result": result
                })
            
            # Log escalation
            escalation_record = {
                "timestamp": current_time.isoformat(),
                "rule_name": rule.name,
                "issue_key": issue.get("key"),
                "escalation_level": rule.escalation_level.value,
                "hours_open": hours_open,
                "message": message,
                "email_results": escalation_results
            }
            
            logger.info(f"🚨 Escalation executed: {rule.name} for {issue.get('key')}")
            return escalation_record
            
        except Exception as e:
            logger.error(f"Error executing escalation: {e}")
            return {"error": str(e)}
    
    async def send_daily_digest(self, jira_agent, project_key: str = None, 
                               recipients: List[str] = None) -> Dict[str, Any]:
        """Send daily digest email with project status."""
        try:
            if not self.daily_digest_config.enabled:
                logger.info("Daily digest is disabled")
                return {"success": False, "message": "Daily digest is disabled"}
            
            # Get project information
            project_info = await jira_agent.get_project_info(project_key)
            if not project_info.get("success"):
                return {"success": False, "error": "Failed to get project info"}
            
            # Get all issues
            issues_result = await jira_agent.get_real_issues(project_key)
            if not issues_result.get("success"):
                return {"success": False, "error": "Failed to get issues"}
            
            # Generate digest content
            digest_content = await self._generate_daily_digest_content(
                project_info, issues_result, jira_agent
            )
            
            # Send to recipients
            recipients = recipients or self.daily_digest_config.recipients or ["team@company.com"]
            email_results = []
            
            for recipient in recipients:
                subject = f"📊 Daily Digest: {project_info['project']['name']} - {datetime.now().strftime('%Y-%m-%d')}"
                result = await self.send_notification_email(
                    to_email=recipient,
                    subject=subject,
                    body=digest_content
                )
                email_results.append({
                    "recipient": recipient,
                    "result": result
                })
            
            # Log digest
            digest_record = {
                "timestamp": datetime.now().isoformat(),
                "project_key": project_key,
                "recipients": recipients,
                "email_results": email_results,
                "content_length": len(digest_content)
            }
            
            logger.info(f"📊 Daily digest sent to {len(recipients)} recipients")
            return {
                "success": True,
                "message": f"Daily digest sent to {len(recipients)} recipients",
                "digest_record": digest_record
            }
            
        except Exception as e:
            logger.error(f"Error sending daily digest: {e}")
            return {"success": False, "error": str(e)}
    
    async def _generate_daily_digest_content(self, project_info: Dict[str, Any], 
                                           issues_result: Dict[str, Any], 
                                           jira_agent) -> str:
        """Generate daily digest email content."""
        try:
            project = project_info['project']
            issues = issues_result['issues']
            
            # Calculate metrics
            total_issues = len(issues)
            status_counts = {}
            priority_counts = {}
            unassigned_count = 0
            overdue_count = 0
            
            for issue in issues:
                status = issue.get("status", "Unknown")
                priority = issue.get("priority", "No Priority")
                assignee = issue.get("assignee", "")
                
                status_counts[status] = status_counts.get(status, 0) + 1
                priority_counts[priority] = priority_counts.get(priority, 0) + 1
                
                if not assignee or assignee == "Unassigned":
                    unassigned_count += 1
                
                # Check if overdue (simplified check)
                created_str = issue.get("created")
                if created_str:
                    try:
                        created_time = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
                        hours_open = (datetime.now() - created_time).total_seconds() / 3600
                        if hours_open > 72:  # 3 days
                            overdue_count += 1
                    except:
                        pass
            
            # Generate digest content
            content = f"""
🚀 Daily Project Digest: {project['name']}
{'=' * 60}
📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}
🔑 Project Key: {project['key']}
👥 Project Lead: {project.get('lead', 'Not specified')}

📊 PROJECT OVERVIEW
{'=' * 30}
📋 Total Issues: {total_issues}
⚠️  Unassigned: {unassigned_count}
⏰ Overdue: {overdue_count}

📈 STATUS DISTRIBUTION
{'=' * 30}"""
            
            for status, count in sorted(status_counts.items()):
                content += f"\n{status}: {count} issues"
            
            content += f"""

🎯 PRIORITY DISTRIBUTION
{'=' * 30}"""
            
            for priority, count in sorted(priority_counts.items()):
                content += f"\n{priority}: {count} issues"
            
            # Add recent issues
            content += f"""

🆕 RECENT ISSUES (Last 5)
{'=' * 30}"""
            
            recent_issues = sorted(issues, key=lambda x: x.get("created", ""), reverse=True)[:5]
            for issue in recent_issues:
                content += f"\n• {issue.get('key')}: {issue.get('summary', 'No summary')}"
                content += f"\n  Status: {issue.get('status')} | Priority: {issue.get('priority')}"
                content += f"\n  Assignee: {issue.get('assignee', 'Unassigned')}"
            
            # Add unassigned issues if any
            if unassigned_count > 0:
                content += f"""

⚠️  UNASSIGNED ISSUES
{'=' * 30}"""
                
                unassigned_issues = [i for i in issues if not i.get("assignee") or i.get("assignee") == "Unassigned"]
                for issue in unassigned_issues[:3]:  # Show first 3
                    content += f"\n• {issue.get('key')}: {issue.get('summary', 'No summary')}"
                    content += f"\n  Priority: {issue.get('priority')} | Status: {issue.get('status')}"
            
            content += f"""

---
📧 This digest was automatically generated by the Jira Notification Agent
🔗 View project: {project_info.get('base_url', 'N/A')}/browse/{project['key']}
            """
            
            return content.strip()
            
        except Exception as e:
            logger.error(f"Error generating daily digest content: {e}")
            return f"Error generating daily digest: {str(e)}"
    
    async def send_critical_ticket_alert(self, issue: Dict[str, Any], 
                                       recipients: List[str], 
                                       alert_type: str = "unassigned") -> Dict[str, Any]:
        """Send critical ticket alert email."""
        try:
            # Determine alert subject and content based on type
            if alert_type == "unassigned":
                subject = f"⚠️  CRITICAL: Unassigned Ticket {issue.get('key')} - Requires Immediate Attention"
                content = f"""
🚨 CRITICAL TICKET ALERT
{'=' * 40}

A critical ticket has been unassigned for over 24 hours and requires immediate attention.

📋 TICKET DETAILS
{'=' * 20}
🔑 Issue Key: {issue.get('key')}
📝 Summary: {issue.get('summary', 'No summary')}
🎯 Priority: {issue.get('priority', 'Not set')}
📊 Status: {issue.get('status', 'Unknown')}
⏰ Created: {issue.get('created', 'Unknown')}
👤 Reporter: {issue.get('reporter', 'Unknown')}

⚠️  ACTION REQUIRED
{'=' * 20}
• Assign this ticket to an appropriate team member
• Review priority and urgency
• Update status if needed
• Set due date if not already set

🔗 View Ticket: [Jira Link]
⏰ This alert was triggered after 24 hours of being unassigned

---
📧 Sent by Jira Notification Agent
                """
            
            elif alert_type == "overdue":
                subject = f"⏰ OVERDUE: High Priority Task {issue.get('key')} - Past Due"
                content = f"""
⏰ OVERDUE TASK ALERT
{'=' * 30}

A high priority task is overdue and requires immediate attention.

📋 TASK DETAILS
{'=' * 20}
🔑 Issue Key: {issue.get('key')}
📝 Summary: {issue.get('summary', 'No summary')}
🎯 Priority: {issue.get('priority', 'Not set')}
📊 Status: {issue.get('status', 'Unknown')}
⏰ Created: {issue.get('created', 'Unknown')}
👤 Assignee: {issue.get('assignee', 'Unassigned')}

⚠️  ACTION REQUIRED
{'=' * 20}
• Review current status and blockers
• Update progress and timeline
• Escalate if additional resources needed
• Communicate with stakeholders

🔗 View Task: [Jira Link]
⏰ This alert was triggered due to overdue status

---
📧 Sent by Jira Notification Agent
                """
            
            else:
                subject = f"⚠️  ALERT: {issue.get('key')} - Requires Attention"
                content = f"""
⚠️  GENERAL ALERT
{'=' * 20}

A ticket requires your attention.

📋 TICKET DETAILS
{'=' * 20}
🔑 Issue Key: {issue.get('key')}
📝 Summary: {issue.get('summary', 'No summary')}
🎯 Priority: {issue.get('priority', 'Not set')}
📊 Status: {issue.get('status', 'Unknown')}

🔗 View Ticket: [Jira Link]

---
📧 Sent by Jira Notification Agent
                """
            
            # Send emails
            email_results = []
            for recipient in recipients:
                result = await self.send_notification_email(
                    to_email=recipient,
                    subject=subject,
                    body=content
                )
                email_results.append({
                    "recipient": recipient,
                    "result": result
                })
            
            # Log alert
            alert_record = {
                "timestamp": datetime.now().isoformat(),
                "issue_key": issue.get("key"),
                "alert_type": alert_type,
                "recipients": recipients,
                "email_results": email_results
            }
            
            logger.info(f"⚠️  Critical ticket alert sent for {issue.get('key')}")
            return {
                "success": True,
                "message": f"Critical ticket alert sent to {len(recipients)} recipients",
                "alert_record": alert_record
            }
            
        except Exception as e:
            logger.error(f"Error sending critical ticket alert: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_notification_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get notification history."""
        return self.notification_history[-limit:] if limit > 0 else self.notification_history
    
    async def add_escalation_rule(self, rule: EscalationRule) -> Dict[str, Any]:
        """Add a new escalation rule."""
        try:
            self.escalation_rules.append(rule)
            logger.info(f"Added escalation rule: {rule.name}")
            return {
                "success": True,
                "message": f"Escalation rule '{rule.name}' added successfully",
                "total_rules": len(self.escalation_rules)
            }
        except Exception as e:
            logger.error(f"Error adding escalation rule: {e}")
            return {"success": False, "error": str(e)}
    
    async def update_daily_digest_config(self, config: DailyDigestConfig) -> Dict[str, Any]:
        """Update daily digest configuration."""
        try:
            self.daily_digest_config = config
            logger.info("Daily digest configuration updated")
            return {
                "success": True,
                "message": "Daily digest configuration updated successfully"
            }
        except Exception as e:
            logger.error(f"Error updating daily digest config: {e}")
            return {"success": False, "error": str(e)}
    
    async def health_check(self) -> Dict[str, Any]:
        """Check agent health and status."""
        try:
            # Test MCP server connection
            mcp_health = await self.call_mcp_email_tool("health_check", {})
            
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "mcp_server_connected": mcp_health.get("success", False),
                "escalation_rules_count": len(self.escalation_rules),
                "daily_digest_enabled": self.daily_digest_config.enabled,
                "notifications_sent": len([n for n in self.notification_history if n["status"] == "email_sent"]),
                "notifications_failed": len([n for n in self.notification_history if n["status"] == "email_failed"])
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

# Example usage
async def main():
    """Example usage of Jira Notification Agent."""
    agent = JiraNotificationAgent()
    
    # Test health check
    health = await agent.health_check()
    print(f"Agent Health: {health}")
    
    # Test email sending
    result = await agent.send_notification_email(
        to_email="test@example.com",
        subject="Test Notification",
        body="This is a test notification from the Jira Notification Agent."
    )
    print(f"Email Result: {result}")

if __name__ == "__main__":
    print("🔔 Jira Notification Agent")
    print("=" * 40)
    print("This agent integrates with your existing Email Agent")
    print("to handle Jira notifications, daily digests, and escalations.")
    print()
    
    # Don't run main() without proper configuration
    print("⚠️  Configure your MCP server and email settings before testing")
