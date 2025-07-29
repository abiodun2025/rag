# Master-Slave Workflow Distribution System

## 🚀 Overview

The Master-Slave Workflow Distribution System allows the smart agent to act as a master that distributes tasks to specialized slave agents. This enables parallel processing, better resource utilization, and automated workflow coordination.

## 🏗️ Architecture

### Master Agent
- **Role**: Workflow coordinator and task distributor
- **Responsibilities**:
  - Create and manage workflows
  - Distribute tasks to appropriate slave agents
  - Handle task dependencies and sequencing
  - Monitor workflow progress
  - Manage agent availability and performance

### Slave Agents
- **Pull Request Agent**: Creates and merges pull requests
- **Code Review Agent**: Performs automated code reviews
- **Code Analysis Agent**: Analyzes code for security and performance issues

## 📋 Workflow Types

### 1. Simple PR Creation
```python
workflow_type = "create_pr"
```
- Creates a single pull request
- Assigned to: PR Agent

### 2. PR with Review
```python
workflow_type = "pr_with_review"
```
- Creates a pull request
- Performs automated code review
- Generates review report
- Assigned to: PR Agent → Review Agent

### 3. Full Development Cycle
```python
workflow_type = "full_development_cycle"
```
- Creates pull request
- Analyzes code changes
- Performs code review
- Merges pull request (if approved)
- Assigned to: PR Agent → Analysis Agent → Review Agent → PR Agent

## 🛠️ Usage

### 1. Programmatic Usage

```python
from master_agent import MasterAgent

# Initialize master agent
master = MasterAgent()

# Create a workflow
workflow_id = master.create_workflow(
    workflow_type="pr_with_review",
    parameters={
        "title": "My Feature",
        "description": "Feature description",
        "source_branch": "feature-branch",
        "target_branch": "main"
    },
    priority=1
)

# Monitor workflow
status = master.get_workflow_status(workflow_id)
print(f"Progress: {status['progress']}")
```

### 2. CLI Usage

```bash
# Start the CLI
python3 master_agent_cli.py

# Available commands
create pr_with_review "My Feature" feature-branch
status workflow_abc123
monitor workflow_abc123
agents
queue
list
```

### 3. Test Scripts

```bash
# Run comprehensive test
python3 test_master_slave_workflow.py

# Test specific workflows
python3 test_complete_workflow.py
```

## 🔧 Configuration

### Environment Variables
```bash
export GITHUB_TOKEN="your_github_token"
export GITHUB_OWNER="your_username"
export GITHUB_REPO="your_repository"
```

### MCP Bridge Configuration
The master agent connects to the MCP bridge at `http://127.0.0.1:5000` by default.

## 📊 Monitoring

### Workflow Status
```python
status = master.get_workflow_status(workflow_id)
print(f"Status: {status['workflow']['status']}")
print(f"Progress: {status['progress']}")
```

### Agent Status
```python
agent_status = master.get_agent_status()
print(f"Available agents: {agent_status['available_agents']}")
print(f"Busy agents: {agent_status['busy_agents']}")
```

### Task Queue Status
```python
queue_status = master.get_task_queue_status()
print(f"Pending tasks: {queue_status['pending_tasks']}")
print(f"Completed tasks: {queue_status['completed_tasks']}")
```

## 🔄 Task Dependencies

The system automatically handles task dependencies:

1. **PR Number Resolution**: When a task needs a PR number from a previous task
2. **Sequential Execution**: Tasks are executed in priority order
3. **Parallel Execution**: Independent tasks can run simultaneously

Example dependency chain:
```
create_pr → [PR_NUMBER] → code_review
```

## 🎯 Agent Capabilities

### Pull Request Agent
- `create_pr`: Create new pull requests
- `merge_pr`: Merge pull requests
- `list_prs`: List existing pull requests

### Code Review Agent
- `code_review`: Perform automated code reviews
- `analyze_code`: Analyze code for issues
- `generate_reports`: Generate HTML review reports

### Code Analysis Agent
- `analyze_code`: Analyze code changes
- `security_scan`: Security vulnerability scanning
- `performance_analysis`: Performance issue detection

## 📈 Performance Features

### Priority Queue
- Tasks are executed based on priority (1=high, 2=medium, 3=low)
- Higher priority tasks are processed first

### Agent Selection
- Tasks are assigned to the best available agent
- Selection based on capabilities and performance score

### Parallel Processing
- Multiple tasks can run simultaneously
- Independent workflows can execute in parallel

## 🔍 Error Handling

### Task Failures
- Failed tasks are logged with error details
- Workflow status is updated accordingly
- Agents are freed up for new tasks

### Agent Failures
- Agents are marked as offline if they fail
- Tasks are reassigned to available agents
- System continues operating with remaining agents

## 📝 Logging

The system provides comprehensive logging:

```python
import logging
logging.basicConfig(level=logging.INFO)

# Logs include:
# - Task assignment
# - Task completion
# - Agent status changes
# - Workflow progress
# - Error details
```

## 🚀 Getting Started

### 1. Start the MCP Bridge
```bash
GITHUB_TOKEN="your_token" GITHUB_OWNER="your_username" GITHUB_REPO="your_repo" python3 simple_mcp_bridge.py
```

### 2. Run the Master Agent
```bash
python3 master_agent_cli.py
```

### 3. Create Your First Workflow
```bash
create pr_with_review "My First Feature" feature-branch
```

### 4. Monitor Progress
```bash
monitor workflow_abc123
```

## 🔮 Future Enhancements

### Planned Features
- **Web Dashboard**: Real-time monitoring interface
- **Agent Performance Metrics**: Track agent efficiency
- **Workflow Templates**: Predefined workflow patterns
- **Dynamic Agent Scaling**: Add/remove agents dynamically
- **Advanced Scheduling**: Time-based task scheduling
- **Integration APIs**: Connect with external systems

### Custom Agent Development
```python
# Example: Adding a custom agent
class CustomAgent:
    def __init__(self):
        self.capabilities = ["custom_task"]
        self.status = "available"
    
    def execute_task(self, parameters):
        # Custom task implementation
        pass
```

## 🐛 Troubleshooting

### Common Issues

1. **Agent Not Available**
   - Check if MCP bridge is running
   - Verify agent capabilities match task requirements

2. **Workflow Stuck**
   - Check task dependencies
   - Verify PR numbers are correctly passed

3. **GitHub API Errors**
   - Verify GitHub token and permissions
   - Check repository access

### Debug Commands
```bash
# Check agent status
agents

# Check task queue
queue

# List all workflows
list

# Get detailed workflow status
status workflow_id
```

## 📚 Examples

### Complete Development Workflow
```python
# Create a complete development cycle
workflow_id = master.create_workflow(
    workflow_type="full_development_cycle",
    parameters={
        "title": "Bug Fix Implementation",
        "description": "Fixes critical bug in authentication system",
        "source_branch": "bugfix-auth",
        "target_branch": "main"
    },
    priority=1
)
```

### Code Review Only
```python
# Review an existing PR
workflow_id = master.create_workflow(
    workflow_type="code_review",
    parameters={
        "pr_number": 123
    },
    priority=2
)
```

## 🎉 Success Metrics

The master-slave system provides:
- ✅ **Parallel Processing**: Multiple tasks run simultaneously
- ✅ **Automatic Coordination**: Dependencies handled automatically
- ✅ **Real-time Monitoring**: Live progress tracking
- ✅ **Error Recovery**: Graceful handling of failures
- ✅ **Scalable Architecture**: Easy to add new agents
- ✅ **Real GitHub Integration**: Actual PR creation and review

This system transforms the development workflow from manual coordination to automated, intelligent task distribution! 🚀