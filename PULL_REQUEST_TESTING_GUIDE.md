# Pull Request Agent Testing Guide

## Overview
This guide provides comprehensive instructions for testing the real-time pull request agent functionality in your agentic RAG system. The pull request agent includes tools for creating, reviewing, listing, and merging pull requests through the MCP bridge.

## Prerequisites

### 1. Start the MCP Bridge Server
First, ensure the MCP bridge server is running:

```bash
# Terminal 1: Start the MCP bridge server
python3 simple_mcp_bridge.py
```

The server should start on `http://127.0.0.1:5000`

### 2. Start the Smart Agent API (Optional)
For full integration testing, start the smart agent API:

```bash
# Terminal 2: Start the smart agent API
python3 -m uvicorn agent.api:app --host 0.0.0.0 --port 8058
```

## Testing Methods

### Method 1: Simple Quick Test
Run the simple test script for basic functionality verification:

```bash
python3 test_pull_request_simple.py
```

This will test:
- ✅ Creating a pull request
- ✅ Listing pull requests
- ✅ Reviewing a pull request

### Method 2: Interactive CLI Testing
Use the interactive CLI for hands-on testing:

```bash
python3 test_pull_request_cli.py
```

Available commands:
- `create <title> <description>` - Create a pull request
- `list [status] [limit]` - List pull requests
- `review <pr_id> <type> <comments>` - Review a pull request
- `merge <pr_id>` - Merge a pull request
- `code-review <pr_id>` - Perform code review
- `status` - Check server status
- `help` - Show available commands
- `quit` - Exit the test

### Method 3: Comprehensive Testing
Run the full comprehensive test suite:

```bash
python3 test_pull_request_agent.py
```

This includes:
- ✅ Direct MCP Bridge Testing
- ✅ Smart Agent Integration Testing
- ✅ Real-time Workflow Testing
- ✅ Performance Testing
- ✅ Error Handling Testing

## Available Pull Request Tools

### 1. `create_pull_request`
Creates a new pull request for code review.

**Parameters:**
- `title` (required): Pull request title
- `description`: Pull request description
- `source_branch`: Source branch name (default: "feature-branch")
- `target_branch`: Target branch name (default: "main")
- `repository`: Repository name (default: "default-repo")

**Example:**
```json
{
  "tool_name": "create_pull_request",
  "arguments": {
    "title": "Add authentication feature",
    "description": "Implements OAuth2 authentication",
    "source_branch": "feature/auth",
    "target_branch": "main",
    "repository": "my-app"
  }
}
```

### 2. `list_pull_requests`
Lists all pull requests in a repository.

**Parameters:**
- `repository`: Repository name (default: "default-repo")
- `status`: Filter by status - "open", "closed", or "all" (default: "all")
- `limit`: Maximum number of PRs to return (default: 10)

**Example:**
```json
{
  "tool_name": "list_pull_requests",
  "arguments": {
    "repository": "my-app",
    "status": "open",
    "limit": 5
  }
}
```

### 3. `review_pull_request`
Reviews a pull request.

**Parameters:**
- `pr_id` (required): Pull request ID
- `review_type`: Review type - "approve", "request_changes", or "comment" (default: "approve")
- `comments`: Array of review comments
- `reviewer`: Reviewer name (default: "Code Reviewer")

**Example:**
```json
{
  "tool_name": "review_pull_request",
  "arguments": {
    "pr_id": "PR_1234567890",
    "review_type": "approve",
    "comments": ["Great implementation!", "Please add tests"],
    "reviewer": "Senior Developer"
  }
}
```

### 4. `merge_pull_request`
Merges a pull request.

**Parameters:**
- `pr_id` (required): Pull request ID
- `merge_method`: Merge method - "merge", "squash", or "rebase" (default: "squash")
- `commit_message`: Custom commit message

**Example:**
```json
{
  "tool_name": "merge_pull_request",
  "arguments": {
    "pr_id": "PR_1234567890",
    "merge_method": "squash",
    "commit_message": "Merge authentication feature"
  }
}
```

### 5. `code_review`
Performs automated code review analysis.

**Parameters:**
- `pr_id` (required): Pull request ID
- `code_changes`: Array of code change objects
- `reviewer`: Reviewer name (default: "Code Reviewer")

**Example:**
```json
{
  "tool_name": "code_review",
  "arguments": {
    "pr_id": "PR_1234567890",
    "code_changes": [
      {
        "file": "auth.py",
        "changes": "Added OAuth2 authentication",
        "lines_added": 50,
        "lines_removed": 5
      }
    ],
    "reviewer": "Senior Developer"
  }
}
```

## Testing Scenarios

### Scenario 1: Basic Pull Request Workflow
1. Create a pull request
2. List all pull requests
3. Review the pull request
4. Merge the pull request

### Scenario 2: Code Review Workflow
1. Create a pull request with code changes
2. Perform automated code review
3. Add review comments
4. Request changes if needed

### Scenario 3: Multiple Pull Requests
1. Create multiple pull requests
2. List pull requests with different filters
3. Review each pull request
4. Track pull request status

### Scenario 4: Error Handling
1. Try to create PR without title
2. Try to review non-existent PR
3. Try to merge already merged PR
4. Test with invalid parameters

## Integration with Smart Agent

The pull request tools are integrated with the smart agent, allowing natural language requests:

### Example Smart Agent Requests:
- "Create a pull request for the authentication feature"
- "Review the latest pull request in my-app repository"
- "List all open pull requests"
- "Merge pull request PR_1234567890"

### Testing Smart Agent Integration:
```bash
# Start smart agent API
python3 -m uvicorn agent.api:app --host 0.0.0.0 --port 8058

# Test with curl
curl -X POST http://localhost:8058/smart-agent/process \
  -H "Content-Type: application/json" \
  -d '{
    "message": "create a pull request for the authentication feature",
    "user_id": "test_user",
    "session_id": null,
    "search_type": "hybrid"
  }'
```

## Performance Testing

### Response Time Benchmarks:
- **Create PR**: < 100ms
- **List PRs**: < 50ms
- **Review PR**: < 75ms
- **Merge PR**: < 100ms
- **Code Review**: < 200ms

### Load Testing:
```bash
# Run performance test
python3 test_pull_request_agent.py
```

## Troubleshooting

### Common Issues:

1. **Server Connection Error**
   ```
   ❌ Cannot connect to server: Connection refused
   ```
   **Solution**: Ensure MCP bridge server is running on port 5000

2. **Tool Not Found**
   ```
   ❌ Tool 'create_pull_request' not found
   ```
   **Solution**: Check that pull request tools are properly registered in the MCP bridge

3. **Invalid Parameters**
   ```
   ❌ Failed to create pull request: No pull request title provided
   ```
   **Solution**: Ensure all required parameters are provided

4. **Smart Agent Integration Issues**
   ```
   ❌ Intent not recognized
   ```
   **Solution**: Check smart agent intent detection for pull request keywords

### Debug Mode:
Enable debug logging in the MCP bridge:
```python
logging.basicConfig(level=logging.DEBUG)
```

## Expected Test Results

### Successful Test Run:
```
🔀 Real-Time Pull Request Agent Test
============================================================
Testing pull request creation, review, and management functionality

1️⃣ Testing Direct MCP Bridge Pull Request Tools
--------------------------------------------------

📝 Test 1.1: Create Pull Request
✅ Pull request created successfully!
   PR ID: PR_1734567890
   Title: Add new authentication feature
   URL: https://github.com/my-app/pull/PR_1734567890
   Status: open

📋 Test 1.2: List Pull Requests
✅ Found 1 pull requests
   - Add new authentication feature (ID: PR_1734567890)

🔍 Test 1.3: Review Pull Request
✅ Pull request reviewed successfully!
   Review ID: review_1734567891
   Review Type: approve
   Reviewer: Code Reviewer
   Comments: 2

🎉 Pull Request Agent testing completed!
📊 Overall Success Rate: 100.0%
```

## Next Steps

1. **Real GitHub Integration**: Replace simulated functions with actual GitHub API calls
2. **GitLab Support**: Add GitLab API integration
3. **Advanced Code Review**: Implement more sophisticated code analysis
4. **Automated Testing**: Add CI/CD integration for pull request workflows
5. **Webhook Support**: Add real-time notifications for pull request events

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the MCP bridge logs
3. Test individual tools using the CLI interface
4. Verify server connectivity and configuration