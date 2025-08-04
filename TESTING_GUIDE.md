# 🧪 Alert System Testing Guide

Complete guide for testing the alert system functionality.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start Testing](#quick-start-testing)
3. [Comprehensive Testing](#comprehensive-testing)
4. [CLI Testing](#cli-testing)
5. [Manual Testing](#manual-testing)
6. [Integration Testing](#integration-testing)
7. [Troubleshooting](#troubleshooting)

---

## 🔧 Prerequisites

Before testing, ensure you have:

### 1. Environment Setup
```bash
# Set alert recipients
export ALERT_EMAIL="your-email@example.com"
export ALERT_SLACK_CHANNEL="#alerts"
export ALERT_TEAMS_CHANNEL="alerts"
export ALERT_SMS_NUMBER="+1234567890"

# MCP server
export MCP_SERVER_URL="http://127.0.0.1:5000"
```

### 2. MCP Server Running
```bash
# Start your MCP server (adjust path as needed)
python simple_mcp_server.py
# or
python github_mcp_bridge.py
```

### 3. Required Tools Available
Ensure your MCP server has these tools:
- `sendmail_simple` - For email alerts
- `slack_post_alert` - For Slack alerts (optional)
- `teams_post_alert` - For Teams alerts (optional)

---

## 🚀 Quick Start Testing

### Option 1: Quick Test Script
```bash
# Run the quick test
python quick_test.py
```

This will:
- Initialize the alert system
- Test MCP connection
- Send a test email alert
- Verify storage functionality
- Test different severity levels

### Option 2: CLI Test
```bash
# Test a specific alert
python alert_cli.py test pr_creation_success "Test alert" '{"test": true}'

# Test all channels
python alert_cli.py test-all

# List configured rules
python alert_cli.py list
```

---

## 🔍 Comprehensive Testing

### Run Full Test Suite
```bash
python test_alert_system.py
```

This comprehensive test suite includes:

| Test | Description |
|------|-------------|
| MCP Connection | Tests connection to MCP server |
| Alert Rules | Tests rule management |
| Email Alerts | Tests email functionality |
| Slack Alerts | Tests Slack notifications |
| Teams Alerts | Tests Teams notifications |
| Alert Storage | Tests database storage |
| Cooldown Protection | Tests spam prevention |
| Severity Levels | Tests all severity levels |
| Integration | Tests workflow integration |
| Monitoring | Tests background monitoring |

### Expected Output
```
🧪 Starting Alert System Tests
============================================================

🔍 Running: Test MCP Connection
✅ Test MCP Connection: PASS
   └─ Connected to MCP server, discovered 24 tools

🔍 Running: Test Alert Rules
✅ Test Alert Rules: PASS
   └─ Alert rules working, 11 rules configured

...

📊 TEST SUMMARY
============================================================
Total Tests: 10
Passed: 10
Failed: 0
Success Rate: 100.0%

🎉 All tests passed! Alert system is working correctly.
```

---

## 🖥️ CLI Testing

### 1. List Alert Rules
```bash
python alert_cli.py list
```

Expected output:
```
📋 Alert Rules:
================================================================================
Rule ID: mcp_server_down
Name: MCP Server Down
Description: MCP server is not responding
Severity: critical
Channels: ['email', 'slack']
Enabled: True
Cooldown: 2 minutes
----------------------------------------
...
```

### 2. Test Specific Alert
```bash
python alert_cli.py test pr_creation_success "Test PR created" '{"pr_number": 123}'
```

### 3. Test All Channels
```bash
python alert_cli.py test-all
```

### 4. Start Monitoring
```bash
python alert_cli.py monitor
```

### 5. Show Status
```bash
python alert_cli.py status
```

---

## 👐 Manual Testing

### 1. Test Email Alerts
```python
import asyncio
from alert_system import AlertSystem

async def test_email():
    alert_system = AlertSystem()
    
    # Test different alert types
    await alert_system.trigger_alert(
        "pr_creation_success",
        "Manual test: PR created successfully",
        {"pr_number": 123, "repository": "test/repo"}
    )
    
    await alert_system.trigger_alert(
        "agent_blocked",
        "Manual test: Agent is blocked",
        {"agent_id": "test_agent", "blocked_time": "10 minutes"}
    )

asyncio.run(test_email())
```

### 2. Test Slack Integration
```python
# Test Slack alert (if configured)
await alert_system.trigger_alert(
    "workflow_completed",
    "Manual test: Workflow completed",
    {"workflow_id": "test_123", "duration": "5 minutes"}
)
```

### 3. Test Cooldown Protection
```python
# Send multiple alerts quickly
for i in range(3):
    await alert_system.trigger_alert(
        "test_cooldown",
        f"Test alert {i+1}",
        {"iteration": i+1}
    )
    # Only the first alert should be sent due to cooldown
```

---

## 🔗 Integration Testing

### 1. Test with Master Agent
```python
import asyncio
from alert_integration import EnhancedMasterAgent

async def test_integration():
    # Create enhanced agent with alerts
    enhanced_agent = EnhancedMasterAgent()
    
    # Test workflow creation with alerts
    workflow_id = await enhanced_agent.create_workflow_with_alerts(
        "pr_with_report",
        {"title": "Integration Test PR", "body": "Testing alert integration"}
    )
    
    print(f"Created workflow: {workflow_id}")

asyncio.run(test_integration())
```

### 2. Test Workflow Integration
```python
from alert_integration import WorkflowAlertIntegration

async def test_workflow_alerts():
    alert_system = AlertSystem()
    workflow_alerts = WorkflowAlertIntegration(alert_system)
    
    # Simulate workflow lifecycle
    workflow_id = "test_workflow_123"
    
    # Workflow starts
    await workflow_alerts.on_workflow_start(
        workflow_id, "test_workflow", {"test": True}
    )
    
    # Workflow completes successfully
    await workflow_alerts.on_workflow_complete(
        workflow_id, "test_workflow", True, {"result": "success"}
    )

asyncio.run(test_workflow_alerts())
```

### 3. Test GitHub Integration
```python
from alert_integration import GitHubAlertIntegration

async def test_github_alerts():
    alert_system = AlertSystem()
    github_alerts = GitHubAlertIntegration(alert_system)
    
    # Test PR creation success
    await github_alerts.on_pr_created(
        123, "Test PR", "https://github.com/test/repo/pull/123",
        "test/repo", "agent"
    )
    
    # Test PR creation failure
    await github_alerts.on_pr_failed(
        "GitHub API error", {"title": "Test PR", "head": "feature/test"}
    )

asyncio.run(test_github_alerts())
```

---

## 🔧 Troubleshooting

### Common Issues and Solutions

#### 1. MCP Server Connection Failed
**Error**: `Connection error calling MCP tool`

**Solutions**:
```bash
# Check if MCP server is running
curl http://127.0.0.1:5000/health

# Start MCP server if needed
python simple_mcp_server.py

# Check environment variable
echo $MCP_SERVER_URL
```

#### 2. Email Not Sending
**Error**: `Email alert failed`

**Solutions**:
```bash
# Check Gmail credentials
echo $GMAIL_USER
echo $GMAIL_APP_PASSWORD

# Test MCP email tool directly
curl -X POST http://127.0.0.1:5000/call \
  -H "Content-Type: application/json" \
  -d '{"tool": "sendmail_simple", "arguments": {"to_email": "test@example.com", "subject": "Test", "message": "Test"}}'
```

#### 3. Slack Notifications Not Working
**Error**: `Slack alert failed`

**Solutions**:
```bash
# Check Slack configuration
echo $ALERT_SLACK_CHANNEL

# Test Slack tool directly
curl -X POST http://127.0.0.1:5000/call \
  -H "Content-Type: application/json" \
  -d '{"tool": "slack_post_alert", "arguments": {"channel": "#alerts", "title": "Test", "message": "Test", "severity": "info"}}'
```

#### 4. Database Issues
**Error**: `Alert storage test failed`

**Solutions**:
```bash
# Check database file
ls -la alerts.db

# Check database permissions
sqlite3 alerts.db ".tables"

# Reset database if needed
rm alerts.db
python quick_test.py  # This will recreate the database
```

#### 5. Import Errors
**Error**: `ModuleNotFoundError: No module named 'alert_system'`

**Solutions**:
```bash
# Ensure you're in the correct directory
pwd
ls alert_system.py

# Add current directory to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Or run with explicit path
python -c "import sys; sys.path.append('.'); from alert_system import AlertSystem"
```

### Debug Mode

Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Then run your tests
python quick_test.py
```

### Database Inspection

Check alert history:
```python
import sqlite3

conn = sqlite3.connect("alerts.db")
cursor = conn.cursor()

# View recent alerts
cursor.execute("""
    SELECT alert_id, rule_id, severity, message, timestamp 
    FROM alerts 
    ORDER BY timestamp DESC 
    LIMIT 10
""")

for row in cursor.fetchall():
    print(f"Alert: {row[0]} | Rule: {row[1]} | Severity: {row[2]} | Message: {row[3]} | Time: {row[4]}")

conn.close()
```

---

## 📊 Test Results Interpretation

### Success Indicators
- ✅ All tests pass
- 📧 Email alerts received
- 💬 Slack/Teams notifications received
- 💾 Alerts stored in database
- 🔄 Cooldown protection working

### Warning Signs
- ⚠️ Some channels not configured (Slack/Teams)
- ⚠️ MCP server not running (tests will continue)
- ⚠️ Email credentials not set

### Failure Indicators
- ❌ MCP connection completely failed
- ❌ Database errors
- ❌ Import errors
- ❌ No alerts being sent

---

## 🎯 Testing Checklist

Before considering the alert system ready:

- [ ] Quick test passes
- [ ] Comprehensive test suite passes
- [ ] Email alerts received
- [ ] Slack/Teams alerts received (if configured)
- [ ] Database storage working
- [ ] Cooldown protection working
- [ ] Integration tests pass
- [ ] Monitoring starts/stops correctly
- [ ] CLI commands work
- [ ] Alert rules can be added/removed

---

## 🚀 Next Steps After Testing

1. **Configure Production Settings**
   - Set up proper email/Slack credentials
   - Configure alert recipients
   - Set up monitoring schedules

2. **Integration**
   - Integrate with your master agent
   - Add alert calls to workflow execution
   - Set up GitHub integration

3. **Deployment**
   - Deploy as systemd service
   - Set up Docker container
   - Configure Kubernetes deployment

4. **Monitoring**
   - Set up alert system monitoring
   - Configure escalation procedures
   - Set up alert dashboards 