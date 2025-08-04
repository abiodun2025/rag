# 🚨 Alert System Guide
## Standalone Alert System for Agentic RAG Knowledge Graph

A comprehensive alert system that leverages your existing MCP tools for fault tolerance and critical notifications.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Architecture](#architecture)
4. [Installation & Setup](#installation--setup)
5. [Configuration](#configuration)
6. [Usage](#usage)
7. [Integration](#integration)
8. [Alert Rules](#alert-rules)
9. [Notification Channels](#notification-channels)
10. [CLI Commands](#cli-commands)
11. [Examples](#examples)
12. [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

The Alert System provides real-time monitoring and notification capabilities for your Agentic RAG system. It integrates seamlessly with your existing MCP tools to send alerts via email, Slack, Teams, and SMS when critical events occur.

### Key Benefits:
- **Fault Tolerance**: Multiple notification channels with fallback
- **Real-time Monitoring**: Continuous system health checks
- **Configurable Rules**: Flexible alert conditions and thresholds
- **Integration Ready**: Works with existing master agent and workflows
- **Persistent Storage**: SQLite database for alert history

---

## ✨ Features

### 🔔 Alert Severity Levels
- **CRITICAL**: System down, immediate action needed
- **HIGH**: Agent blocked, workflow failed
- **MEDIUM**: Performance degradation, warnings
- **LOW**: Informational, successful operations

### 📡 Notification Channels
- **Email**: Via existing MCP `sendmail_simple` tool
- **Slack**: Via MCP `slack_post_alert` tool
- **Teams**: Via MCP `teams_post_alert` tool
- **SMS**: Via MCP `call_phone` tool (critical alerts only)

### 🛡️ Fault Tolerance Features
- **Multiple Channel Redundancy**: If one channel fails, try others
- **Retry Logic**: Exponential backoff for failed notifications
- **Cooldown Protection**: Prevent alert spam
- **Self-Monitoring**: Alert system monitors itself
- **Persistent Storage**: All alerts stored in SQLite database

---

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Alert System  │    │   MCP Client    │    │   MCP Server    │
│                 │    │                 │    │                 │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │Alert Rules  │ │    │ │HTTP Client  │ │    │ │Email Tools  │ │
│ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │AlertStorage │ │    │ │Tool Discovery│ │    │ │Slack Tools  │ │
│ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │AlertNotifier│ │    │ │Tool Execution│ │    │ │Teams Tools  │ │
│ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  SQLite DB      │    │   HTTP/JSON     │    │  External APIs  │
│  (alerts.db)    │    │   Protocol      │    │  (Gmail, Slack) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8+
- Your existing MCP server running on port 5000
- Access to email, Slack, and/or Teams APIs

### 1. Environment Variables
Set up your alert recipients:

```bash
# Alert recipients
export ALERT_EMAIL="admin@example.com"
export ALERT_SLACK_CHANNEL="#alerts"
export ALERT_TEAMS_CHANNEL="alerts"
export ALERT_SMS_NUMBER="+1234567890"

# MCP server
export MCP_SERVER_URL="http://127.0.0.1:5000"
```

### 2. Dependencies
The alert system uses your existing dependencies:
- `httpx` (for MCP client)
- `sqlite3` (built-in)
- `asyncio` (built-in)

### 3. Verify MCP Tools
Ensure your MCP server has these tools available:
- `sendmail_simple` - For email alerts
- `slack_post_alert` - For Slack alerts
- `teams_post_alert` - For Teams alerts
- `call_phone` - For SMS alerts (optional)

---

## ⚙️ Configuration

### Configuration File
Use `alert_config.json` to configure the system:

```json
{
  "alert_system": {
    "mcp_server_url": "http://127.0.0.1:5000",
    "database_path": "alerts.db",
    "monitoring_interval_seconds": 30
  },
  "recipients": {
    "email": "admin@example.com",
    "slack_channel": "#alerts",
    "teams_channel": "alerts"
  }
}
```

### Alert Rules
Rules define when alerts should be triggered:

```json
{
  "rule_id": "mcp_server_down",
  "name": "MCP Server Down",
  "description": "MCP server is not responding",
  "condition": "not mcp_client.connected",
  "severity": "critical",
  "channels": ["email", "slack"],
  "enabled": true,
  "cooldown_minutes": 2
}
```

---

## 📖 Usage

### Basic Usage

```python
from alert_system import AlertSystem

# Initialize alert system
alert_system = AlertSystem()

# Start monitoring
await alert_system.start_monitoring()

# Manually trigger an alert
await alert_system.trigger_alert(
    "pr_creation_success",
    "Pull request #123 created successfully",
    {"pr_number": 123, "repository": "test/repo"}
)
```

### Integration with Master Agent

```python
from alert_integration import EnhancedMasterAgent

# Create enhanced master agent with alerts
enhanced_agent = EnhancedMasterAgent()

# Create workflow with alert monitoring
workflow_id = await enhanced_agent.create_workflow_with_alerts(
    "pr_with_report",
    {"title": "Test PR", "body": "Test body"}
)
```

---

## 🔗 Integration

### 1. Master Agent Integration
The alert system integrates with your existing master agent:

```python
# Monitor master agent health
master_alert_integration = MasterAgentAlertIntegration(master_agent, alert_system)
await master_alert_integration.monitor_master_agent()
```

### 2. Workflow Integration
Monitor workflow execution:

```python
workflow_alerts = WorkflowAlertIntegration(alert_system)

# Called when workflow starts
await workflow_alerts.on_workflow_start(workflow_id, workflow_type, parameters)

# Called when workflow completes
await workflow_alerts.on_workflow_complete(workflow_id, workflow_type, success, result)
```

### 3. GitHub Integration
Monitor GitHub operations:

```python
github_alerts = GitHubAlertIntegration(alert_system)

# Called when PR is created
await github_alerts.on_pr_created(pr_number, title, url, repository, author)

# Called when PR creation fails
await github_alerts.on_pr_failed(error, parameters)
```

---

## 📋 Alert Rules

### Default Rules Included

| Rule ID | Name | Severity | Description |
|---------|------|----------|-------------|
| `mcp_server_down` | MCP Server Down | CRITICAL | MCP server not responding |
| `agent_blocked` | Agent Blocked | HIGH | Agent blocked for too long |
| `pr_creation_failed` | PR Creation Failed | HIGH | Pull request creation failed |
| `pr_creation_success` | PR Creation Success | LOW | Pull request created successfully |
| `workflow_timeout` | Workflow Timeout | MEDIUM | Workflow running too long |
| `database_connection_failed` | Database Connection Failed | CRITICAL | Database connection down |
| `task_execution_failed` | Task Execution Failed | HIGH | Workflow task failed |
| `agent_unresponsive` | Agent Unresponsive | HIGH | Agent not responding |
| `workflow_completed` | Workflow Completed | LOW | Workflow completed successfully |
| `queue_overflow` | Task Queue Overflow | MEDIUM | Too many pending tasks |
| `github_api_error` | GitHub API Error | HIGH | GitHub API error |

### Custom Rules
Create custom alert rules:

```python
from alert_system import AlertRule, AlertSeverity, AlertChannel

custom_rule = AlertRule(
    rule_id="custom_rule",
    name="Custom Alert",
    description="Custom alert condition",
    condition="custom_metric > 100",
    severity=AlertSeverity.MEDIUM,
    channels=[AlertChannel.EMAIL, AlertChannel.SLACK],
    cooldown_minutes=5
)

alert_system.add_rule(custom_rule)
```

---

## 📡 Notification Channels

### Email Alerts
Uses your existing MCP `sendmail_simple` tool:

```python
# Email alert format
Subject: [CRITICAL] MCP server is not responding...

🚨 ALERT: CRITICAL

MCP server is not responding

📊 Details:
{
  "server_url": "http://127.0.0.1:5000",
  "error": "Connection refused"
}

⏰ Time: 2025-01-28 10:30:00
🆔 Alert ID: alert_1706452200_mcp_server_down

---
Sent by Agentic RAG Alert System
```

### Slack Alerts
Uses MCP `slack_post_alert` tool with color coding:
- **CRITICAL**: Red (error)
- **HIGH**: Orange (warning)
- **MEDIUM**: Blue (info)
- **LOW**: Green (success)

### Teams Alerts
Uses MCP `teams_post_alert` tool with similar color coding.

### SMS Alerts
Uses MCP `call_phone` tool (for critical alerts only).

---

## 🖥️ CLI Commands

### List Alert Rules
```bash
python alert_cli.py list
```

### Test an Alert
```bash
python alert_cli.py test pr_creation_success "Test PR created" '{"pr_number": 123}'
```

### Start Monitoring
```bash
python alert_cli.py monitor
```

### Test All Channels
```bash
python alert_cli.py test-all
```

### Show Status
```bash
python alert_cli.py status
```

### Add Custom Rule
```bash
# Create rule.json file first
python alert_cli.py add --file rule.json
```

### Remove Rule
```bash
python alert_cli.py remove mcp_server_down
```

---

## 💡 Examples

### Example 1: Basic Alert System
```python
import asyncio
from alert_system import AlertSystem

async def main():
    # Initialize alert system
    alert_system = AlertSystem()
    
    # Start monitoring
    await alert_system.start_monitoring()
    
    # Test alerts
    await alert_system.trigger_alert(
        "pr_creation_success",
        "Pull request #123 created successfully",
        {"pr_number": 123, "repository": "test/repo"}
    )
    
    # Keep running
    try:
        while True:
            await asyncio.sleep(60)
    except KeyboardInterrupt:
        await alert_system.stop_monitoring()

asyncio.run(main())
```

### Example 2: Integration with Workflow
```python
from alert_integration import WorkflowAlertIntegration

# Setup workflow alerts
workflow_alerts = WorkflowAlertIntegration(alert_system)

# In your workflow execution
async def execute_workflow(workflow_id, workflow_type, parameters):
    try:
        # Notify workflow start
        await workflow_alerts.on_workflow_start(workflow_id, workflow_type, parameters)
        
        # Execute workflow
        result = await your_workflow_execution()
        
        # Notify success
        await workflow_alerts.on_workflow_complete(workflow_id, workflow_type, True, result)
        
    except Exception as e:
        # Notify failure
        await workflow_alerts.on_workflow_complete(workflow_id, workflow_type, False, {"error": str(e)})
```

### Example 3: Custom Monitoring
```python
# Add custom monitoring logic
async def custom_monitoring():
    while True:
        # Check system resources
        cpu_usage = get_cpu_usage()
        if cpu_usage > 90:
            await alert_system.trigger_alert(
                "high_cpu_usage",
                f"CPU usage is {cpu_usage}%",
                {"cpu_usage": cpu_usage, "threshold": 90}
            )
        
        await asyncio.sleep(60)
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. MCP Server Connection Failed
**Error**: `Connection error calling MCP tool`
**Solution**: 
- Verify MCP server is running on port 5000
- Check `MCP_SERVER_URL` environment variable
- Ensure MCP server has required tools

#### 2. Email Not Sending
**Error**: `Email alert failed`
**Solution**:
- Verify Gmail credentials are set
- Check `ALERT_EMAIL` environment variable
- Ensure MCP `sendmail_simple` tool is working

#### 3. Slack Notifications Not Working
**Error**: `Slack alert failed`
**Solution**:
- Verify Slack webhook is configured
- Check `ALERT_SLACK_CHANNEL` environment variable
- Ensure MCP `slack_post_alert` tool is available

#### 4. Alert Spam
**Issue**: Too many alerts being sent
**Solution**:
- Increase `cooldown_minutes` in alert rules
- Check alert conditions are not too broad
- Review recent alerts in database

### Debug Mode
Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Database Inspection
Check alert history:

```python
import sqlite3

conn = sqlite3.connect("alerts.db")
cursor = conn.cursor()
cursor.execute("SELECT * FROM alerts ORDER BY timestamp DESC LIMIT 10")
alerts = cursor.fetchall()
for alert in alerts:
    print(alert)
conn.close()
```

---

## 📊 Monitoring Dashboard

The alert system provides a SQLite database (`alerts.db`) with the following tables:

### Alerts Table
```sql
CREATE TABLE alerts (
    alert_id TEXT PRIMARY KEY,
    rule_id TEXT NOT NULL,
    severity TEXT NOT NULL,
    message TEXT NOT NULL,
    data TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    channels_sent TEXT NOT NULL,
    resolved BOOLEAN DEFAULT FALSE,
    resolved_at TEXT
);
```

### Alert Rules Table
```sql
CREATE TABLE alert_rules (
    rule_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    condition TEXT NOT NULL,
    severity TEXT NOT NULL,
    channels TEXT NOT NULL,
    enabled BOOLEAN DEFAULT TRUE,
    cooldown_minutes INTEGER DEFAULT 5,
    escalation_minutes INTEGER DEFAULT 30
);
```

---

## 🚀 Production Deployment

### 1. Systemd Service (Linux)
Create `/etc/systemd/system/alert-system.service`:

```ini
[Unit]
Description=Agentic RAG Alert System
After=network.target

[Service]
Type=simple
User=rag-user
WorkingDirectory=/path/to/your/project
Environment=ALERT_EMAIL=admin@example.com
Environment=ALERT_SLACK_CHANNEL=#alerts
ExecStart=/usr/bin/python3 alert_system.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 2. Docker Deployment
Create `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "alert_system.py"]
```

### 3. Kubernetes Deployment
Create `alert-system-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: alert-system
spec:
  replicas: 1
  selector:
    matchLabels:
      app: alert-system
  template:
    metadata:
      labels:
        app: alert-system
    spec:
      containers:
      - name: alert-system
        image: your-registry/alert-system:latest
        env:
        - name: ALERT_EMAIL
          value: "admin@example.com"
        - name: ALERT_SLACK_CHANNEL
          value: "#alerts"
```

---

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review alert system logs
3. Inspect the SQLite database
4. Test individual MCP tools

The alert system is designed to be self-monitoring and will alert you if it encounters issues with its own operation. 