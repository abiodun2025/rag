# Master Agent Guide

## Overview

The Master Agent is a sophisticated coordinator that analyzes user requests and delegates tasks to appropriate specialized agents. It acts as an intelligent router that understands different types of requests and routes them to the best-suited agent for execution.

## Architecture

```
User Request → Master Agent → Task Analysis → Agent Delegation → Results Aggregation
```

### Agent Types

The Master Agent can delegate to these specialized agents:

1. **Desktop Storage Agent** (`desktop_storage`)
   - Handles saving messages to Desktop directory
   - Keywords: "save", "store", "desktop"

2. **Message Storage Agent** (`message_storage`)
   - Handles saving messages to project directory
   - Keywords: "save", "store", "remember"

3. **Email Agent** (`email`)
   - Handles email composition and sending
   - Keywords: "email", "compose", "send", "mail", "gmail"

4. **Search Agent** (`search`)
   - Handles internal knowledge search
   - Keywords: "search", "find", "look up", "query", "what is"

5. **Web Search Agent** (`web_search`)
   - Handles web/internet searches
   - Keywords: "web", "internet", "current", "latest", "news"

6. **Knowledge Graph Agent** (`knowledge_graph`)
   - Handles knowledge graph queries
   - Keywords: "graph", "relationship", "entity", "knowledge", "company"

7. **General Agent** (`general`)
   - Handles general conversation and responses
   - Fallback for unrecognized requests

## Usage

### Via API

```bash
# Process a request through master agent
curl -X POST http://localhost:8058/master-agent/process \
  -H "Content-Type: application/json" \
  -d '{
    "message": "save to desktop: Hello world",
    "user_id": "test_user",
    "session_id": null,
    "search_type": "hybrid"
  }'
```

### Via CLI

```bash
# Start CLI
python3 cli.py

# Enter master agent mode
master

# Use master agent commands
🎯 Master Agent > save to desktop: Hello world
🎯 Master Agent > compose an email to test@example.com
🎯 Master Agent > search for OpenAI funding
🎯 Master Agent > what is the relationship between OpenAI and Microsoft
```

### Via Python

```python
import requests

# Process request through master agent
response = requests.post(
    "http://localhost:8058/master-agent/process",
    json={
        "message": "save to desktop: Hello world",
        "user_id": "test_user",
        "session_id": None,
        "search_type": "hybrid"
    }
)

result = response.json()
print(f"Tasks executed: {result['master_agent_result']['tasks_executed']}")
print(f"Successful tasks: {result['master_agent_result']['successful_tasks']}")
```

## Example Requests

### Storage Requests

```bash
# Save to Desktop
"save to desktop: Important meeting notes for tomorrow"

# Save to Project
"save to project: Project milestone completed"
```

### Email Requests

```bash
# Compose email
"compose an email to john@example.com with subject 'Meeting' and body 'Let\'s meet tomorrow'"

# Send email
"send email to team@company.com about the new project"
```

### Search Requests

```bash
# Internal search
"search for OpenAI funding information"

# Web search
"search the web for latest AI news"

# Knowledge graph query
"what is the relationship between OpenAI and Microsoft"
```

### General Requests

```bash
# General conversation
"Hello, how are you doing today?"

# Help request
"Can you help me with something?"
```

## Response Format

The master agent returns a comprehensive response with:

```json
{
  "session_id": "uuid",
  "master_agent_result": {
    "original_request": "user message",
    "session_id": "uuid",
    "user_id": "user_id",
    "tasks_executed": 2,
    "successful_tasks": 2,
    "failed_tasks": 0,
    "total_execution_time": 0.5,
    "agent_stats": {
      "desktop_storage": {"calls": 1, "success": 1, "errors": 0}
    },
    "results": [
      {
        "agent": "desktop_storage",
        "success": true,
        "result": "Message saved to Desktop: {...}",
        "error": null,
        "execution_time": 0.3
      }
    ]
  },
  "processing_time_ms": 0.5,
  "status": "success"
}
```

## Statistics

Get master agent statistics:

```bash
# Via API
curl http://localhost:8058/master-agent/stats

# Response
{
  "agent_stats": {
    "desktop_storage": {"calls": 5, "success": 5, "errors": 0},
    "message_storage": {"calls": 3, "success": 3, "errors": 0},
    "email": {"calls": 2, "success": 2, "errors": 0}
  },
  "task_history_count": 10,
  "status": "success"
}
```

## Testing

Run the test script to verify functionality:

```bash
python3 test_master_agent.py
```

This will test all agent types with various request types.

## Key Features

1. **Intelligent Task Analysis**: Automatically identifies the type of request
2. **Priority-based Execution**: Executes tasks in priority order
3. **Error Handling**: Graceful handling of agent failures
4. **Statistics Tracking**: Monitors agent performance and usage
5. **Session Management**: Maintains conversation context
6. **Multi-agent Coordination**: Can involve multiple agents for complex requests

## Configuration

The master agent can be configured by modifying:

- `agent/master_agent.py`: Core logic and agent definitions
- `agent/api.py`: API endpoints
- `cli.py`: CLI integration

## Troubleshooting

### Common Issues

1. **Agent not responding**: Check if the specific agent service is running
2. **API errors**: Verify the API server is running on port 8058
3. **Permission errors**: Check file permissions for storage operations

### Debug Mode

Enable debug logging to see detailed execution:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Future Enhancements

1. **Learning Capabilities**: Master agent learns from user preferences
2. **Advanced Routing**: More sophisticated task analysis
3. **Agent Communication**: Direct agent-to-agent communication
4. **Performance Optimization**: Parallel task execution
5. **Custom Agents**: User-defined specialized agents

## Integration

The master agent integrates with your existing:

- Message storage system
- Email tools
- Search capabilities
- Knowledge graph
- CLI interface
- API endpoints

This creates a unified interface for all your agent capabilities while maintaining the specialized functionality of each individual agent. 