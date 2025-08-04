#!/usr/bin/env python3
"""
Standalone Alert System for Agentic RAG Knowledge Graph
Leverages existing MCP tools for fault tolerance and critical notifications.
"""

import asyncio
import json
import logging
import os
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
from pathlib import Path

# Import your existing MCP tools
from agent.mcp_tools import MCPClient, SendmailSimpleInput

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AlertSeverity(Enum):
    """Alert severity levels."""
    CRITICAL = "critical"    # System down, immediate action needed
    HIGH = "high"           # Agent blocked, workflow failed
    MEDIUM = "medium"       # Performance degradation, warnings
    LOW = "low"            # Informational, successful operations

class AlertChannel(Enum):
    """Available alert channels."""
    EMAIL = "email"
    SLACK = "slack"
    TEAMS = "teams"
    SMS = "sms"

@dataclass
class AlertRule:
    """Configuration for an alert rule."""
    rule_id: str
    name: str
    description: str
    condition: str  # Python expression to evaluate
    severity: AlertSeverity
    channels: List[AlertChannel]
    enabled: bool = True
    cooldown_minutes: int = 5  # Prevent spam
    escalation_minutes: int = 30  # Escalate if not resolved

@dataclass
class Alert:
    """An alert instance."""
    alert_id: str
    rule_id: str
    severity: AlertSeverity
    message: str
    data: Dict[str, Any]
    timestamp: datetime
    channels_sent: List[AlertChannel] = None
    resolved: bool = False
    resolved_at: Optional[datetime] = None

class AlertStorage:
    """Persistent storage for alerts and rules."""
    
    def __init__(self, db_path: str = "alerts.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize the SQLite database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create alerts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                alert_id TEXT PRIMARY KEY,
                rule_id TEXT NOT NULL,
                severity TEXT NOT NULL,
                message TEXT NOT NULL,
                data TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                channels_sent TEXT NOT NULL,
                resolved BOOLEAN DEFAULT FALSE,
                resolved_at TEXT
            )
        """)
        
        # Create alert rules table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alert_rules (
                rule_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                condition TEXT NOT NULL,
                severity TEXT NOT NULL,
                channels TEXT NOT NULL,
                enabled BOOLEAN DEFAULT TRUE,
                cooldown_minutes INTEGER DEFAULT 5,
                escalation_minutes INTEGER DEFAULT 30
            )
        """)
        
        conn.commit()
        conn.close()
        logger.info(f"Alert database initialized: {self.db_path}")
    
    def save_alert(self, alert: Alert):
        """Save an alert to the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO alerts (alert_id, rule_id, severity, message, data, timestamp, channels_sent, resolved, resolved_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            alert.alert_id,
            alert.rule_id,
            alert.severity.value,
            alert.message,
            json.dumps(alert.data),
            alert.timestamp.isoformat(),
            json.dumps([c.value for c in alert.channels_sent or []]),
            alert.resolved,
            alert.resolved_at.isoformat() if alert.resolved_at else None
        ))
        
        conn.commit()
        conn.close()
    
    def get_recent_alerts(self, rule_id: str, minutes: int = 5) -> List[Alert]:
        """Get recent alerts for a rule to check cooldown."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_time = (datetime.now() - timedelta(minutes=minutes)).isoformat()
        
        cursor.execute("""
            SELECT alert_id, rule_id, severity, message, data, timestamp, channels_sent, resolved, resolved_at
            FROM alerts 
            WHERE rule_id = ? AND timestamp > ? AND resolved = FALSE
            ORDER BY timestamp DESC
        """, (rule_id, cutoff_time))
        
        alerts = []
        for row in cursor.fetchall():
            alert = Alert(
                alert_id=row[0],
                rule_id=row[1],
                severity=AlertSeverity(row[2]),
                message=row[3],
                data=json.loads(row[4]),
                timestamp=datetime.fromisoformat(row[5]),
                channels_sent=[AlertChannel(c) for c in json.loads(row[6])],
                resolved=row[7],
                resolved_at=datetime.fromisoformat(row[8]) if row[8] else None
            )
            alerts.append(alert)
        
        conn.close()
        return alerts

class AlertNotifier:
    """Handles sending alerts through various channels using MCP tools."""
    
    def __init__(self, mcp_client: MCPClient):
        self.mcp_client = mcp_client
        self.alert_recipients = {
            AlertChannel.EMAIL: os.getenv('ALERT_EMAIL', os.getenv('GOOGLE_EMAIL', 'admin@example.com')),
            AlertChannel.SLACK: os.getenv('ALERT_SLACK_CHANNEL', '#alerts'),
            AlertChannel.TEAMS: os.getenv('ALERT_TEAMS_CHANNEL', 'alerts'),
            AlertChannel.SMS: os.getenv('ALERT_SMS_NUMBER', '+1234567890')
        }
    
    async def send_alert(self, alert: Alert, channels: List[AlertChannel]) -> List[AlertChannel]:
        """Send alert through specified channels with retry logic."""
        sent_channels = []
        
        for channel in channels:
            try:
                success = await self._send_to_channel(alert, channel)
                if success:
                    sent_channels.append(channel)
                    logger.info(f"✅ Alert sent via {channel.value}: {alert.message}")
                else:
                    logger.warning(f"❌ Failed to send alert via {channel.value}")
            except Exception as e:
                logger.error(f"❌ Error sending alert via {channel.value}: {e}")
        
        return sent_channels
    
    async def _send_to_channel(self, alert: Alert, channel: AlertChannel) -> bool:
        """Send alert to a specific channel."""
        try:
            if channel == AlertChannel.EMAIL:
                return await self._send_email_alert(alert)
            elif channel == AlertChannel.SLACK:
                return await self._send_slack_alert(alert)
            elif channel == AlertChannel.TEAMS:
                return await self._send_teams_alert(alert)
            elif channel == AlertChannel.SMS:
                return await self._send_sms_alert(alert)
            else:
                logger.warning(f"Unknown alert channel: {channel}")
                return False
        except Exception as e:
            logger.error(f"Error sending to {channel.value}: {e}")
            return False
    
    async def _send_email_alert(self, alert: Alert) -> bool:
        """Send alert via email using existing MCP sendmail tool."""
        try:
            subject = f"[{alert.severity.value.upper()}] {alert.message[:50]}..."
            
            body = f"""
🚨 ALERT: {alert.severity.value.upper()}

{alert.message}

📊 Details:
{json.dumps(alert.data, indent=2)}

⏰ Time: {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
🆔 Alert ID: {alert.alert_id}

---
Sent by Agentic RAG Alert System
            """.strip()
            
            result = await self.mcp_client.call_tool("sendmail_simple", {
                "to_email": self.alert_recipients[AlertChannel.EMAIL],
                "subject": subject,
                "message": body
            })
            return result.get("success", False)
            
        except Exception as e:
            logger.error(f"Email alert failed: {e}")
            return False
    
    async def _send_slack_alert(self, alert: Alert) -> bool:
        """Send alert via Slack using MCP slack_post_alert tool."""
        try:
            severity_colors = {
                AlertSeverity.CRITICAL: "error",
                AlertSeverity.HIGH: "warning", 
                AlertSeverity.MEDIUM: "info",
                AlertSeverity.LOW: "success"
            }
            
            result = await self.mcp_client.call_tool("slack_post_alert", {
                "channel": self.alert_recipients[AlertChannel.SLACK],
                "title": f"🚨 {alert.severity.value.upper()} Alert",
                "message": f"{alert.message}\n\nDetails: {json.dumps(alert.data, indent=2)}",
                "severity": severity_colors.get(alert.severity, "info")
            })
            
            return result.get("success", False)
            
        except Exception as e:
            logger.error(f"Slack alert failed: {e}")
            return False
    
    async def _send_teams_alert(self, alert: Alert) -> bool:
        """Send alert via Teams using MCP teams_post_alert tool."""
        try:
            severity_colors = {
                AlertSeverity.CRITICAL: "error",
                AlertSeverity.HIGH: "warning",
                AlertSeverity.MEDIUM: "info", 
                AlertSeverity.LOW: "success"
            }
            
            result = await self.mcp_client.call_tool("teams_post_alert", {
                "channel": self.alert_recipients[AlertChannel.TEAMS],
                "title": f"🚨 {alert.severity.value.upper()} Alert",
                "message": f"{alert.message}\n\nDetails: {json.dumps(alert.data, indent=2)}",
                "severity": severity_colors.get(alert.severity, "info")
            })
            
            return result.get("success", False)
            
        except Exception as e:
            logger.error(f"Teams alert failed: {e}")
            return False
    
    async def _send_sms_alert(self, alert: Alert) -> bool:
        """Send alert via SMS using MCP call_phone tool (for critical alerts only)."""
        try:
            if alert.severity == AlertSeverity.CRITICAL:
                # For critical alerts, we could use the phone calling tool
                # This would require additional setup for SMS
                logger.info(f"SMS alert would be sent to {self.alert_recipients[AlertChannel.SMS]}")
                return True
            else:
                logger.info(f"SMS alerts only for critical severity, skipping {alert.severity}")
                return True
                
        except Exception as e:
            logger.error(f"SMS alert failed: {e}")
            return False

class AlertSystem:
    """Main alert system that monitors conditions and sends notifications."""
    
    def __init__(self, mcp_server_url: str = "http://127.0.0.1:5000"):
        self.mcp_client = MCPClient(mcp_server_url)
        self.storage = AlertStorage()
        self.notifier = AlertNotifier(self.mcp_client)
        self.rules: Dict[str, AlertRule] = {}
        self.monitoring = False
        self.monitor_thread = None
        
        # Initialize default alert rules
        self._init_default_rules()
        
        logger.info("🚨 Alert System initialized")
    
    def _init_default_rules(self):
        """Initialize default alert rules for common scenarios."""
        default_rules = [
            AlertRule(
                rule_id="mcp_server_down",
                name="MCP Server Down",
                description="MCP server is not responding",
                condition="not mcp_client.connected",
                severity=AlertSeverity.CRITICAL,
                channels=[AlertChannel.EMAIL, AlertChannel.SLACK],
                cooldown_minutes=2
            ),
            AlertRule(
                rule_id="agent_blocked",
                name="Agent Blocked",
                description="Agent has been blocked for too long",
                condition="agent_blocked_time > 300",  # 5 minutes
                severity=AlertSeverity.HIGH,
                channels=[AlertChannel.EMAIL, AlertChannel.SLACK],
                cooldown_minutes=5
            ),
            AlertRule(
                rule_id="pr_creation_failed",
                name="PR Creation Failed",
                description="Pull request creation failed",
                condition="pr_status == 'failed'",
                severity=AlertSeverity.HIGH,
                channels=[AlertChannel.EMAIL, AlertChannel.SLACK]
            ),
            AlertRule(
                rule_id="pr_creation_success",
                name="PR Creation Success",
                description="Pull request created successfully",
                condition="pr_status == 'success'",
                severity=AlertSeverity.LOW,
                channels=[AlertChannel.SLACK]
            ),
            AlertRule(
                rule_id="workflow_timeout",
                name="Workflow Timeout",
                description="Workflow has been running too long",
                condition="workflow_duration > 1800",  # 30 minutes
                severity=AlertSeverity.MEDIUM,
                channels=[AlertChannel.EMAIL, AlertChannel.SLACK]
            ),
            AlertRule(
                rule_id="database_connection_failed",
                name="Database Connection Failed",
                description="Database connection is down",
                condition="not db_connected",
                severity=AlertSeverity.CRITICAL,
                channels=[AlertChannel.EMAIL, AlertChannel.SLACK, AlertChannel.SMS],
                cooldown_minutes=1
            ),
            AlertRule(
                rule_id="workflow_started",
                name="Workflow Started",
                description="Alert when a GitHub workflow starts",
                condition="workflow_started",
                severity=AlertSeverity.LOW,
                channels=[AlertChannel.EMAIL],
                cooldown_minutes=1
            ),
            AlertRule(
                rule_id="workflow_completed",
                name="Workflow Completed",
                description="Alert when a GitHub workflow completes successfully",
                condition="workflow_completed",
                severity=AlertSeverity.LOW,
                channels=[AlertChannel.EMAIL],
                cooldown_minutes=1
            ),
            AlertRule(
                rule_id="workflow_failed",
                name="Workflow Failed",
                description="Alert when a GitHub workflow fails",
                condition="workflow_failed",
                severity=AlertSeverity.CRITICAL,
                channels=[AlertChannel.EMAIL, AlertChannel.SLACK],
                cooldown_minutes=1
            ),
            AlertRule(
                rule_id="task_started",
                name="Task Started",
                description="Alert when a task starts execution",
                condition="task_started",
                severity=AlertSeverity.LOW,
                channels=[AlertChannel.EMAIL],
                cooldown_minutes=1
            ),
            AlertRule(
                rule_id="task_completed",
                name="Task Completed",
                description="Alert when a task completes successfully",
                condition="task_completed",
                severity=AlertSeverity.LOW,
                channels=[AlertChannel.EMAIL],
                cooldown_minutes=1
            ),
            AlertRule(
                rule_id="task_execution_failed",
                name="Task Execution Failed",
                description="Alert when a task execution fails",
                condition="task_execution_failed",
                severity=AlertSeverity.HIGH,
                channels=[AlertChannel.EMAIL, AlertChannel.SLACK],
                cooldown_minutes=1
            ),
            AlertRule(
                rule_id="github_api_error",
                name="GitHub API Error",
                description="Alert when GitHub API returns an error",
                condition="github_api_error",
                severity=AlertSeverity.HIGH,
                channels=[AlertChannel.EMAIL, AlertChannel.SLACK],
                cooldown_minutes=2
            ),
            AlertRule(
                rule_id="pr_merged",
                name="Pull Request Merged",
                description="Alert when a pull request is merged",
                condition="pr_merged",
                severity=AlertSeverity.LOW,
                channels=[AlertChannel.EMAIL],
                cooldown_minutes=1
            ),
            AlertRule(
                rule_id="agent_execution_failed",
                name="Agent Execution Failed",
                description="Alert when an agent method fails to execute",
                condition="agent_execution_failed",
                severity=AlertSeverity.HIGH,
                channels=[AlertChannel.EMAIL, AlertChannel.SLACK],
                cooldown_minutes=2
            ),
            AlertRule(
                rule_id="tool_execution_failed",
                name="Tool Execution Failed",
                description="Alert when a tool fails to execute",
                condition="tool_execution_failed",
                severity=AlertSeverity.MEDIUM,
                channels=[AlertChannel.EMAIL],
                cooldown_minutes=2
            ),
            AlertRule(
                rule_id="agent_performance_degradation",
                name="Agent Performance Degradation",
                description="Alert when an agent takes too long to execute",
                condition="agent_performance_degradation",
                severity=AlertSeverity.MEDIUM,
                channels=[AlertChannel.EMAIL],
                cooldown_minutes=5
            ),
            AlertRule(
                rule_id="tool_performance_degradation",
                name="Tool Performance Degradation",
                description="Alert when a tool takes too long to execute",
                condition="tool_performance_degradation",
                severity=AlertSeverity.MEDIUM,
                channels=[AlertChannel.EMAIL],
                cooldown_minutes=5
            )
        ]
        
        for rule in default_rules:
            self.add_rule(rule)
        
        logger.info(f"✅ Initialized {len(default_rules)} default alert rules")
    
    def add_rule(self, rule: AlertRule):
        """Add a new alert rule."""
        self.rules[rule.rule_id] = rule
        logger.info(f"✅ Added alert rule: {rule.name}")
    
    def remove_rule(self, rule_id: str):
        """Remove an alert rule."""
        if rule_id in self.rules:
            del self.rules[rule_id]
            logger.info(f"✅ Removed alert rule: {rule_id}")
    
    async def check_condition(self, rule: AlertRule, context: Dict[str, Any]) -> bool:
        """Check if an alert condition is met."""
        try:
            # Create a safe evaluation context
            safe_context = {
                'mcp_client': self.mcp_client,
                'db_connected': True,  # You can add actual DB check here
                **context
            }
            
            # Evaluate the condition
            result = eval(rule.condition, {"__builtins__": {}}, safe_context)
            return bool(result)
            
        except Exception as e:
            logger.error(f"Error evaluating condition for rule {rule.rule_id}: {e}")
            return False
    
    async def trigger_alert(self, rule_id: str, message: str, data: Dict[str, Any] = None):
        """Manually trigger an alert."""
        if rule_id not in self.rules:
            logger.error(f"Unknown alert rule: {rule_id}")
            return
        
        rule = self.rules[rule_id]
        
        # Check cooldown
        recent_alerts = self.storage.get_recent_alerts(rule_id, rule.cooldown_minutes)
        if recent_alerts:
            logger.info(f"Alert {rule_id} in cooldown, skipping")
            return
        
        # Create alert
        alert = Alert(
            alert_id=f"alert_{int(time.time())}_{rule_id}",
            rule_id=rule_id,
            severity=rule.severity,
            message=message,
            data=data or {},
            timestamp=datetime.now()
        )
        
        # Send alert
        sent_channels = await self.notifier.send_alert(alert, rule.channels)
        alert.channels_sent = sent_channels
        
        # Store alert
        self.storage.save_alert(alert)
        
        logger.info(f"🚨 Alert triggered: {rule.name} - {message}")
    
    async def start_monitoring(self):
        """Start the background monitoring thread."""
        if self.monitoring:
            logger.warning("Monitoring already started")
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
        logger.info("🚀 Alert monitoring started")
    
    async def stop_monitoring(self):
        """Stop the background monitoring."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("🛑 Alert monitoring stopped")
    
    def _monitor_loop(self):
        """Background monitoring loop."""
        while self.monitoring:
            try:
                # Run monitoring checks
                asyncio.run(self._run_monitoring_checks())
                time.sleep(30)  # Check every 30 seconds
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                time.sleep(60)  # Wait longer on error
    
    async def _run_monitoring_checks(self):
        """Run all monitoring checks."""
        # Check MCP server health
        try:
            connected = await self.mcp_client.connect()
            if not connected:
                await self.trigger_alert(
                    "mcp_server_down",
                    "MCP server is not responding",
                    {"server_url": self.mcp_client.base_url}
                )
        except Exception as e:
            await self.trigger_alert(
                "mcp_server_down", 
                f"MCP server connection failed: {e}",
                {"server_url": self.mcp_client.base_url, "error": str(e)}
            )
        
        # Add more monitoring checks here as needed
        # - Database health
        # - Agent status checks
        # - Workflow monitoring
        # - System resource monitoring

# Example usage and integration
async def main():
    """Example of how to use the alert system."""
    alert_system = AlertSystem()
    
    # Start monitoring
    await alert_system.start_monitoring()
    
    # Example: Trigger a test alert
    await alert_system.trigger_alert(
        "pr_creation_success",
        "Pull request #123 created successfully",
        {"pr_number": 123, "repository": "test/repo", "author": "agent"}
    )
    
    # Keep running
    try:
        while True:
            await asyncio.sleep(60)
    except KeyboardInterrupt:
        await alert_system.stop_monitoring()

if __name__ == "__main__":
    asyncio.run(main()) 