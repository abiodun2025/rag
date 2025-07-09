# Debug Logging Guide

This document explains how to use the comprehensive debugging features added to the Agentic RAG system.

## Overview

The system now includes extensive debug logging capabilities that help you troubleshoot:

- API requests and responses
- Agent execution and tool calls
- Database operations
- Graph operations
- Embedding generation
- Error details with full stack traces
- Performance timing information

## Quick Start

### 1. Enable Debug Logging

```python
# Import the debug setup
from debug_setup import setup_debug_logging

# Enable comprehensive debug logging (file + console)
log_file = setup_debug_logging()
print(f"Debug logs will be written to: {log_file}")
```

### 2. Console-Only Debug Logging

```python
# For development and quick debugging
from debug_setup import setup_console_debug_logging

setup_console_debug_logging()
```

### 3. Environment Variable

You can also set the environment variable:

```bash
export LOG_LEVEL=DEBUG
```

## Debug Logging Features

### 1. API Request/Response Logging

The system now logs detailed information about all API requests:

```
DEBUG - agent.api - Chat endpoint called with request: ChatRequest(...)
DEBUG - agent.api - Session ID: abc123, User ID: user456
DEBUG - agent.api - Getting or creating session
DEBUG - agent.api - Using session ID: abc123
DEBUG - agent.api - Executing agent with message: 'What are Google's AI initiatives?'
DEBUG - agent.api - Agent execution completed in 2456.78 ms
DEBUG - agent.api - Response length: 1234 characters
DEBUG - agent.api - Tools used: 3
DEBUG - agent.api - Chat endpoint completed in 2489.12 ms total
```

### 2. Agent Execution Logging

Detailed logging of agent execution steps:

```
DEBUG - agent.agent - Vector search tool called with query: 'Google AI initiatives', limit: 10
DEBUG - agent.agent - Session ID: abc123
DEBUG - agent.agent - Calling vector_search_tool with input: VectorSearchInput(...)
DEBUG - agent.agent - Vector search completed in 1234.56 ms, found 8 results
DEBUG - agent.agent - Converted 8 results for agent
```

### 3. Tool Execution Logging

Each tool call is logged with timing and results:

```
DEBUG - agent.tools - Vector search tool called with input: VectorSearchInput(...)
DEBUG - agent.tools - Generating embedding for vector search
DEBUG - agent.tools - Generating embedding for text (length: 25): 'Google AI initiatives'
DEBUG - agent.tools - Using embedding model: text-embedding-3-small
DEBUG - agent.tools - Embedding generated successfully in 234.56 ms, vector length: 1536
DEBUG - agent.tools - Performing vector search with embedding length: 1536, limit: 10
DEBUG - agent.tools - Vector search completed in 567.89 ms, found 8 raw results
DEBUG - agent.tools - Converted 8 results to ChunkResult models
```

### 4. Database Operations Logging

Database operations are logged with timing:

```
DEBUG - agent.db_utils - Database connection pool initialized
DEBUG - agent.db_utils - Executing query: SELECT * FROM chunks WHERE ...
DEBUG - agent.db_utils - Query completed in 45.67 ms
```

### 5. Graph Operations Logging

Knowledge graph operations are logged:

```
DEBUG - agent.graph_utils - Graphiti client initialized successfully with LLM: gpt-4-turbo-preview
DEBUG - agent.graph_utils - Adding episode to knowledge graph
DEBUG - agent.graph_utils - Added episode abc123 to knowledge graph
```

### 6. Error Logging

Errors include full stack traces and context:

```
ERROR - agent.api - Chat endpoint failed: Connection timeout
DEBUG - agent.api - Chat endpoint error details
Traceback (most recent call last):
  File "agent/api.py", line 123, in chat
    result = await rag_agent.run(message, deps=deps)
  ...
```

## CLI Debug Mode

The CLI now includes debug output:

```bash
python cli.py
```

You'll see debug information like:

```
DEBUG: Sending message to http://localhost:8058/chat/stream
DEBUG: Message: 'What are Google's AI initiatives?'
DEBUG: Session ID: None
DEBUG: Request data: {'message': 'What are Google's AI initiatives?', ...}
DEBUG: Making POST request
DEBUG: Response status: 200
DEBUG: Starting to read response stream
DEBUG: Received data type: session
DEBUG: Session ID set to: abc123
DEBUG: Received data type: text
DEBUG: Received data type: tools
DEBUG: Tools used: 3 tools
DEBUG: Stream ended
DEBUG: Stream processing completed, 15 lines processed
DEBUG: Full response length: 1234 characters
```

## Performance Monitoring

The system logs performance metrics:

- Request/response timing
- Tool execution timing
- Database query timing
- Embedding generation timing
- Overall endpoint timing

Example:
```
DEBUG - agent.api - Agent execution completed in 2456.78 ms
DEBUG - agent.tools - Vector search completed in 567.89 ms, found 8 raw results
DEBUG - agent.tools - Embedding generated successfully in 234.56 ms, vector length: 1536
```

## Log File Structure

When using file logging, logs are saved to:

```
logs/
├── rag_debug_20241201_143022.log
├── rag_debug_20241201_150145.log
└── ...
```

Each log file contains:
- Timestamp for each log entry
- Logger name (module)
- Log level
- Detailed message
- Stack traces for errors

## Debug Setup Functions

### `setup_debug_logging()`

Sets up comprehensive debug logging with both console and file output.

**Returns:** Path to the log file

### `setup_console_debug_logging()`

Sets up debug logging for console output only (no file logging).

### `get_debug_logger(name)`

Gets a logger configured for debug output.

**Parameters:**
- `name`: Logger name (usually `__name__`)

**Returns:** Configured logger

### `log_system_info()`

Logs system information including:
- Python version
- Platform
- Working directory
- Environment variables (with sensitive data masked)

## Environment Variables

The following environment variables are logged (with sensitive data masked):

- `LOG_LEVEL`
- `LLM_CHOICE`
- `LLM_API_KEY` (masked)
- `LLM_BASE_URL`
- `EMBEDDING_MODEL`
- `EMBEDDING_API_KEY` (masked)
- `EMBEDDING_BASE_URL`
- `DATABASE_URL`
- `NEO4J_URI`
- `NEO4J_USERNAME`
- `NEO4J_PASSWORD` (masked)
- `APP_ENV`
- `APP_HOST`
- `APP_PORT`

## Best Practices

### 1. Use File Logging for Production Debugging

```python
# For production debugging
log_file = setup_debug_logging()
print(f"Debug logs: {log_file}")
```

### 2. Use Console Logging for Development

```python
# For development
setup_console_debug_logging()
```

### 3. Monitor Performance

Look for timing logs to identify bottlenecks:

```
DEBUG - agent.api - Agent execution completed in 2456.78 ms
DEBUG - agent.tools - Vector search completed in 567.89 ms
```

### 4. Check Error Logs

Always check the full stack trace in error logs:

```
ERROR - agent.api - Chat endpoint failed: Connection timeout
DEBUG - agent.api - Chat endpoint error details
[Full stack trace follows]
```

### 5. Monitor Tool Usage

Track which tools are being used and their performance:

```
DEBUG - agent.agent - Vector search tool called with query: '...'
DEBUG - agent.agent - Graph search tool called with query: '...'
DEBUG - agent.agent - Hybrid search tool called with query: '...'
```

## Troubleshooting

### 1. No Debug Logs Appearing

Check that debug logging is enabled:

```python
import logging
print(f"Root logger level: {logging.getLogger().level}")
print(f"Agent logger level: {logging.getLogger('agent').level}")
```

### 2. Too Much Log Output

Filter specific loggers:

```python
# Only enable debug for specific modules
logging.getLogger('agent.api').setLevel(logging.DEBUG)
logging.getLogger('agent.tools').setLevel(logging.DEBUG)
```

### 3. Log File Not Created

Check permissions and directory:

```python
import os
print(f"Current directory: {os.getcwd()}")
print(f"Logs directory exists: {os.path.exists('logs')}")
```

### 4. Performance Issues

Look for slow operations in the logs:

```
DEBUG - agent.tools - Vector search completed in 5000.00 ms  # Too slow!
DEBUG - agent.tools - Embedding generated successfully in 2000.00 ms  # Too slow!
```

## Integration with Existing Code

The debug logging is designed to be non-intrusive. Existing code will continue to work without changes, but you can add debug logs:

```python
import logging
logger = logging.getLogger(__name__)

def my_function():
    logger.debug("Entering my_function")
    # ... your code ...
    logger.debug("Exiting my_function")
```

## Conclusion

The comprehensive debug logging system provides detailed visibility into the Agentic RAG system's operation. Use it to:

- Troubleshoot issues
- Monitor performance
- Understand system behavior
- Optimize operations

Remember to disable debug logging in production or use appropriate log levels to avoid performance impact. 