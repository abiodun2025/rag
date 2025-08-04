# Agent Monitoring Integration Guide

## 🎯 Overview

The Agent Monitoring Integration provides comprehensive monitoring capabilities for all agents in your ecosystem. It automatically tracks execution, performance, and failures, sending real-time alerts when issues occur.

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Your Agents   │───▶│  Agent Monitor   │───▶│  Alert System   │
│                 │    │                  │    │                 │
│ • SmartMaster   │    │ • Execution      │    │ • Email Alerts  │
│ • MasterAgent   │    │ • Performance    │    │ • Slack Alerts  │
│ • RAG Agent     │    │ • Error Tracking │    │ • Teams Alerts  │
│ • Tools         │    │ • Statistics     │    │ • SMS Alerts    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### 1. Initialize Monitoring

```python
from agent_monitoring_integration import integrate_monitoring_with_agents

# This automatically adds monitoring to all existing agents
integrate_monitoring_with_agents()
```

### 2. Use Existing Agents (Monitoring is Automatic)

```python
from agent.smart_master_agent import SmartMasterAgent
from agent.master_agent import MasterAgent

# Create agents - monitoring is automatically enabled
smart_agent = SmartMasterAgent()
master_agent = MasterAgent()

# Use normally - monitoring happens in background
intent_result = smart_agent.analyze_intent("save this to desktop")
tasks = await master_agent.analyze_request("send an email")
```

### 3. Check Monitoring Statistics

```python
from agent_monitoring_integration import get_agent_monitor

monitor = get_agent_monitor()
stats = monitor.get_agent_stats()

print(f"Success rate: {stats['summary']['success_rate']:.2f}%")
print(f"Total executions: {stats['summary']['total_executions']}")
```

## 📊 Supported Agents

### ✅ **SmartMasterAgent** (`agent/smart_master_agent.py`)
**Monitored Methods:**
- `analyze_intent()` - Intent detection
- `execute_intent()` - Intent execution
- `process_message()` - Message processing

**Alert Triggers:**
- Intent detection failures
- Execution timeouts (>30s)
- Processing errors

### ✅ **MasterAgent** (`agent/master_agent.py`)
**Monitored Methods:**
- `analyze_request()` - Request analysis
- `execute_tasks()` - Task execution
- `process_request()` - Request processing

**Alert Triggers:**
- Task analysis failures
- Task execution failures
- Coordination errors

### ✅ **RAG Agent** (`agent/agent.py`)
**Monitored Tools:**
- `vector_search()` - Vector search operations
- `graph_search()` - Graph search operations
- `hybrid_search()` - Hybrid search operations
- `web_search()` - Web search operations
- `compose_email()` - Email composition

**Alert Triggers:**
- Search failures
- Database connection issues
- Tool execution timeouts (>10s)
- Email composition errors

### ✅ **All Agent Tools**
**Monitored Operations:**
- Email tools (`email_tools.py`)
- Search tools (`web_search_tools.py`)
- Message tools (`message_tools.py`)
- Desktop tools (`desktop_message_tools.py`)
- Calling tools (`google_voice_calling.py`)

## 🔧 Manual Integration

### For New Agents

```python
from agent_monitoring_integration import monitor_agent, monitor_tool

class MyNewAgent:
    @monitor_agent("my_new_agent", AlertSeverity.HIGH)
    async def my_agent_method(self, data):
        # Your agent logic here
        return result
    
    @monitor_tool("my_tool", AlertSeverity.MEDIUM)
    async def my_tool_method(self, input_data):
        # Your tool logic here
        return result
```

### For Existing Methods

```python
from agent_monitoring_integration import get_agent_monitor

monitor = get_agent_monitor()

# Wrap existing method
original_method = my_agent.my_method

@monitor.monitor_agent_execution("my_agent", AlertSeverity.MEDIUM)
async def monitored_method(*args, **kwargs):
    return await original_method(*args, **kwargs)

my_agent.my_method = monitored_method
```

## 📈 Monitoring Features

### 1. **Execution Tracking**
- Start/end times for all agent methods
- Success/failure status
- Execution duration tracking
- Real-time status updates

### 2. **Performance Monitoring**
- **Agent threshold**: 30 seconds
- **Tool threshold**: 10 seconds
- Automatic alerts for slow execution
- Performance degradation detection

### 3. **Error Detection**
- Automatic exception catching
- Error message extraction
- Stack trace logging
- Failure pattern analysis

### 4. **Statistics Collection**
- Success rates per agent/method
- Average execution times
- Failure counts
- Performance trends

## 🚨 Alert Types

### **Agent Execution Failed**
- **Severity**: HIGH
- **Channels**: Email, Slack
- **Trigger**: Any agent method failure
- **Cooldown**: 2 minutes

### **Tool Execution Failed**
- **Severity**: MEDIUM
- **Channels**: Email
- **Trigger**: Any tool failure
- **Cooldown**: 2 minutes

### **Agent Performance Degradation**
- **Severity**: MEDIUM
- **Channels**: Email
- **Trigger**: Agent execution >30s
- **Cooldown**: 5 minutes

### **Tool Performance Degradation**
- **Severity**: MEDIUM
- **Channels**: Email
- **Trigger**: Tool execution >10s
- **Cooldown**: 5 minutes

## 📊 Statistics API

### Get All Statistics

```python
monitor = get_agent_monitor()
stats = monitor.get_agent_stats()

# Summary statistics
print(f"Total executions: {stats['summary']['total_executions']}")
print(f"Success rate: {stats['summary']['success_rate']:.2f}%")
print(f"Average execution time: {stats['summary']['average_execution_time']:.2f}s")

# Agent status
for agent_key, agent_data in stats['agent_stats'].items():
    print(f"{agent_key}: {agent_data['status']}")

# Execution times
for key, times in stats['execution_times'].items():
    avg_time = sum(t['execution_time'] for t in times) / len(times)
    print(f"{key}: {avg_time:.2f}s average")
```

### Real-time Monitoring

```python
import asyncio
from agent_monitoring_integration import get_agent_monitor

async def monitor_agents():
    monitor = get_agent_monitor()
    
    while True:
        stats = monitor.get_agent_stats()
        
        # Check for issues
        if stats['summary']['success_rate'] < 90:
            print("⚠️ Low success rate detected!")
        
        # Print current status
        for agent_key, agent_data in stats['agent_stats'].items():
            if agent_data['status'] == 'running':
                print(f"🔄 {agent_key} is currently running")
        
        await asyncio.sleep(10)  # Check every 10 seconds

# Start monitoring
asyncio.create_task(monitor_agents())
```

## 🧪 Testing

### Run Basic Tests

```bash
python3 test_agent_monitoring.py
```

### Test Specific Agents

```python
# Test SmartMasterAgent
from agent.smart_master_agent import SmartMasterAgent
smart_agent = SmartMasterAgent()

# This will be monitored automatically
intent_result = smart_agent.analyze_intent("save this to desktop")
print(f"Intent: {intent_result.intent}")

# Test MasterAgent
from agent.master_agent import MasterAgent
master_agent = MasterAgent()

# This will be monitored automatically
tasks = await master_agent.analyze_request("send an email")
print(f"Tasks: {len(tasks)}")
```

### Test Error Scenarios

```python
# Test error handling
@monitor_agent("test_agent", AlertSeverity.CRITICAL)
async def failing_function():
    raise Exception("Test error")

try:
    await failing_function()
except Exception as e:
    print(f"Error caught: {e}")
    # Alert will be sent automatically
```

## 🔧 Configuration

### Alert System Configuration

```python
# Configure alert system
from alert_system import AlertSystem

alert_system = AlertSystem(
    mcp_server_url="http://127.0.0.1:5000"
)

# Add custom rules
alert_system.add_rule(AlertRule(
    rule_id="custom_agent_rule",
    name="Custom Agent Rule",
    description="Custom monitoring rule",
    condition="custom_condition",
    severity=AlertSeverity.HIGH,
    channels=[AlertChannel.EMAIL],
    cooldown_minutes=5
))
```

### Performance Thresholds

```python
# Modify thresholds in agent_monitoring_integration.py
# Agent threshold (default: 30 seconds)
if execution_time > 30.0:
    # Trigger alert

# Tool threshold (default: 10 seconds)  
if execution_time > 10.0:
    # Trigger alert
```

## 📧 Email Alerts

You'll receive email alerts for:

1. **Agent failures** - When any agent method fails
2. **Tool failures** - When any tool fails
3. **Performance issues** - When execution takes too long
4. **System errors** - When critical errors occur

### Alert Email Format

```
Subject: [ALERT] Agent smart_master_agent.analyze_intent failed

Agent: smart_master_agent
Method: analyze_intent
Error: Connection timeout
Timestamp: 2025-08-04 11:30:15
Severity: HIGH

This alert was triggered because the agent method failed to execute.
Please check the agent logs for more details.
```

## 🔍 Troubleshooting

### Common Issues

1. **Import Errors**
   ```python
   # Make sure alert_system is in your path
   import sys
   sys.path.append('.')
   from alert_system import AlertSystem
   ```

2. **MCP Server Not Running**
   ```bash
   # Start MCP server
   python3 simple_mcp_http_server.py
   ```

3. **Email Not Sending**
   ```bash
   # Check email configuration
   echo $GOOGLE_EMAIL
   echo $GOOGLE_PASSWORD
   ```

### Debug Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# This will show detailed monitoring logs
monitor = get_agent_monitor()
```

## 🎯 Best Practices

1. **Initialize Early** - Call `integrate_monitoring_with_agents()` at startup
2. **Monitor Critical Paths** - Focus on high-severity methods
3. **Set Appropriate Thresholds** - Adjust based on your system's performance
4. **Review Alerts** - Check email regularly for issues
5. **Monitor Statistics** - Track success rates and performance trends

## 🚀 Production Deployment

### 1. **Start Monitoring**
```python
# In your main application
from agent_monitoring_integration import integrate_monitoring_with_agents

# Initialize monitoring
integrate_monitoring_with_agents()
```

### 2. **Configure Alerts**
```bash
# Set environment variables
export ALERT_EMAIL="your-email@example.com"
export GOOGLE_EMAIL="your-gmail@gmail.com"
export GOOGLE_PASSWORD="your-app-password"
```

### 3. **Monitor Continuously**
```python
# Add to your main loop
async def main():
    while True:
        stats = get_agent_monitor().get_agent_stats()
        if stats['summary']['success_rate'] < 95:
            # Take action
            pass
        await asyncio.sleep(60)
```

## 📚 API Reference

### AgentMonitor Class

```python
class AgentMonitor:
    def monitor_agent_execution(self, agent_name: str, severity: AlertSeverity)
    def monitor_tool_execution(self, tool_name: str, severity: AlertSeverity)
    def get_agent_stats(self) -> Dict[str, Any]
```

### Convenience Functions

```python
def monitor_agent(agent_name: str, severity: AlertSeverity)
def monitor_tool(tool_name: str, severity: AlertSeverity)
def get_agent_monitor() -> AgentMonitor
def integrate_monitoring_with_agents() -> bool
```

---

**🎉 Your agent ecosystem is now fully monitored with real-time alerts!** 