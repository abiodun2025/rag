# Message Storage Agent Guide

## Overview
Your agentic RAG system now includes message storage capabilities that allow the agent to save messages and conversations to a local directory. This feature is useful for record keeping, conversation history, and analysis.

## Features

### ✅ **Message Storage Capabilities**
- **Save Individual Messages**: Store single messages with metadata
- **Save Conversations**: Store complete user-agent conversation pairs
- **List Messages**: Retrieve and filter saved messages
- **Organized Storage**: Messages are organized by date (YYYY/MM/DD/)
- **Rich Metadata**: Each message includes timestamps, user info, and custom metadata

### ✅ **Storage Structure**
```
messages/
├── 2025/
│   └── 07/
│       └── 09/
│           ├── 2025-07-09T14:19:34.185537_test_message_20739c65.json
│           └── 2025-07-09T14:19:34.185997_conversation_78ad12da.json
```

## How to Use

### **1. Save a Message**
```
Save this message: Hello, this is an important note.
Save this important note about AI project updates.
Please save this message for later reference.
```

### **2. Save a Conversation**
```
Save our conversation about tech companies.
Save this conversation about AI updates.
Please save our discussion about the meeting.
```

### **3. List Saved Messages**
```
Show me all saved messages from today.
List messages from yesterday.
Display all saved conversations.
Show me messages about AI.
```

## Testing the Functionality

### **Quick Test**
```bash
python3 test_message_storage.py
```

This will:
- Test message storage tools directly
- Show the storage directory structure
- Test via API
- Provide CLI instructions

### **Interactive Testing**
```bash
# Terminal 1: Start API server
python3 -m uvicorn agent.api:app --host 0.0.0.0 --port 8058

# Terminal 2: Start CLI
python3 cli.py
```

Then try these commands:
```
Save this message: Hello world
Save this important note about AI
Save our conversation about tech companies
Show me all saved messages
List messages from today
```

## Message Storage Tools

### **1. save_message**
Saves a single message with metadata.

**Parameters:**
- `message`: The message content to save
- `message_type`: Type of message (default: "user_message")
- `metadata`: Additional metadata (optional)

**Example:**
```python
result = await save_message(
    message="Important meeting notes",
    message_type="meeting_notes",
    metadata={"priority": "high", "attendees": ["John", "Jane"]}
)
```

### **2. save_conversation**
Saves a complete conversation (user message + agent response).

**Parameters:**
- `user_message`: The user's message
- `agent_response`: The agent's response
- `metadata`: Additional metadata (optional)

**Example:**
```python
result = await save_conversation(
    user_message="What is AI?",
    agent_response="AI stands for Artificial Intelligence...",
    metadata={"topic": "AI", "difficulty": "beginner"}
)
```

### **3. list_messages**
Lists saved messages with optional filtering.

**Parameters:**
- `user_id`: Filter by user ID (optional)
- `message_type`: Filter by message type (optional)
- `limit`: Maximum number of results (default: 50)

**Example:**
```python
result = await list_messages(
    user_id="user123",
    message_type="meeting_notes",
    limit=20
)
```

## File Format

### **Individual Message Format**
```json
{
  "message_id": "20739c65-1b01-453a-8ef5-eac2ccf4a689",
  "timestamp": "2025-07-09T14:19:34.185537",
  "message_type": "test_message",
  "content": "This is a test message from the agent.",
  "user_id": null,
  "session_id": null,
  "metadata": {
    "test": true,
    "source": "test_script"
  }
}
```

### **Conversation Format**
```json
{
  "conversation_id": "78ad12da-c358-4729-bb02-86bf84282890",
  "timestamp": "2025-07-09T14:19:34.185997",
  "user_id": null,
  "session_id": null,
  "user_message": "What is AI?",
  "agent_response": "AI stands for Artificial Intelligence...",
  "metadata": {
    "topic": "AI",
    "test": true
  }
}
```

## Use Cases

### **1. Meeting Notes**
```
Save this message: Meeting with AI team scheduled for tomorrow at 2 PM.
Save our conversation about the Q4 project timeline.
```

### **2. Research Notes**
```
Save this important note about OpenAI's latest developments.
Save our discussion about AI safety concerns.
```

### **3. Task Management**
```
Save this message: Follow up with John about the API integration.
Save our conversation about the deployment schedule.
```

### **4. Learning History**
```
Save our conversation about machine learning concepts.
Save this note about neural network architectures.
```

## Agent Integration

The message storage tools are fully integrated into your agent:

- **Automatic Recognition**: The agent understands when you want to save messages
- **Context Awareness**: The agent can save conversations with proper context
- **Metadata Support**: The agent can add relevant metadata automatically
- **Error Handling**: Graceful error handling for storage issues

## File Management

### **Storage Location**
- Base directory: `messages/`
- Organized by date: `YYYY/MM/DD/`
- File naming: `timestamp_type_id.json`

### **Backup and Cleanup**
- Messages are stored as JSON files
- Easy to backup or migrate
- Can be processed by other tools
- Consider regular cleanup for old messages

## Security and Privacy

### **Local Storage**
- All messages are stored locally
- No external dependencies
- Full control over data

### **Privacy Considerations**
- Messages may contain sensitive information
- Consider encryption for sensitive data
- Regular cleanup of old messages
- Be mindful of what you ask the agent to save

## Troubleshooting

### **Common Issues:**

1. **"Messages directory not found"**
   - The directory is created automatically
   - Check file permissions

2. **"Save failed" errors**
   - Check disk space
   - Verify file permissions
   - Check for special characters in messages

3. **"List messages failed"**
   - Ensure messages directory exists
   - Check file permissions
   - Verify JSON file integrity

## Next Steps

1. **Test the functionality** with the provided test script
2. **Try interactive commands** via CLI
3. **Explore the saved files** in the messages directory
4. **Customize metadata** for your specific use cases
5. **Set up regular backups** of important messages

## Example Workflow

```
User: "Save this message: Important meeting with AI team tomorrow at 2 PM"
Agent: [Saves message with timestamp and metadata]

User: "Save our conversation about the project timeline"
Agent: [Saves both user message and agent response]

User: "Show me all saved messages from today"
Agent: [Lists all messages saved today with details]
```

Your agent now has powerful message storage capabilities! 🚀 