# Email Reading Functionality Guide

This guide explains how to use the new email reading capabilities in the agentic RAG system.

## Overview

The system now supports comprehensive email management through Gmail API:
- **List emails**: View recent emails from your inbox
- **Read emails**: Read full content of specific emails
- **Search emails**: Search emails using Gmail search queries
- **Compose emails**: Send emails (existing functionality)

## Setup

### 1. Gmail API Credentials

You need to set up Gmail API credentials:

1. **Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)**
2. **Create a new project** or select an existing one
3. **Enable the Gmail API** for your project
4. **Create OAuth 2.0 Client ID credentials**:
   - Application type: **Desktop app**
   - Download the `credentials.json` file
5. **Place `credentials.json` in your project root directory**

### 2. First-Time Authorization

The first time you use email functionality:
- A browser window will open for OAuth consent
- Log in with your Gmail account
- Grant permissions for email access
- A `token.json` file will be created for future use

## Usage

### Via CLI

Start the CLI and use natural language commands:

```bash
python3 cli.py
```

**Examples:**
```
You: List my recent emails
You: Show me the last 10 emails
You: Search for emails from john@example.com
You: Find emails with subject "meeting"
You: Read email with ID 1234567890abcdef
You: Search for unread emails
You: Find emails from the last week
```

### Via API

Send requests to the API endpoint:

```bash
curl -X POST http://localhost:8058/chat/stream \
  -H "Content-Type: application/json" \
  -d '{
    "message": "List my recent emails",
    "user_id": "demo_user"
  }'
```

### Via Python Script

Use the test script to try the functionality:

```bash
python3 test_email_reading.py
```

## Email Tools

### 1. List Emails

**Purpose**: View recent emails from your inbox

**Parameters**:
- `max_results`: Maximum number of emails to return (default: 10)
- `query`: Optional Gmail search query

**Examples**:
```
You: List my recent emails
You: Show me the last 5 emails
You: List emails from my inbox
```

### 2. Read Email

**Purpose**: Read the full content of a specific email

**Parameters**:
- `email_id`: Gmail message ID to read

**Examples**:
```
You: Read email with ID 1234567890abcdef
You: Show me the content of email 1234567890abcdef
```

### 3. Search Emails

**Purpose**: Search emails using Gmail search queries

**Parameters**:
- `query`: Search query for emails
- `max_results`: Maximum number of emails to return (default: 10)

**Examples**:
```
You: Search for emails from john@example.com
You: Find emails with subject "meeting"
You: Search for unread emails
You: Find emails from the last week
You: Search for emails containing "project"
```

## Gmail Search Queries

You can use Gmail's powerful search operators:

### Basic Search
- `from:someone@example.com` - Emails from specific sender
- `to:someone@example.com` - Emails sent to specific recipient
- `subject:meeting` - Emails with "meeting" in subject
- `has:attachment` - Emails with attachments
- `is:unread` - Unread emails
- `is:read` - Read emails

### Time-based Search
- `newer_than:1d` - Emails from the last day
- `newer_than:1w` - Emails from the last week
- `newer_than:1m` - Emails from the last month
- `older_than:1d` - Emails older than 1 day

### Label-based Search
- `in:inbox` - Emails in inbox
- `in:sent` - Sent emails
- `in:trash` - Emails in trash
- `label:important` - Emails with "important" label

### Combined Queries
- `from:john@example.com is:unread` - Unread emails from John
- `subject:meeting newer_than:1w` - Meeting emails from last week
- `has:attachment from:boss@company.com` - Attachments from boss

## Response Format

### Email List Response
```json
{
  "status": "success",
  "emails": [
    {
      "id": "message_id",
      "threadId": "thread_id",
      "from": "sender@example.com",
      "subject": "Email Subject",
      "date": "Wed, 9 Jul 2025 14:30:00 +0000",
      "snippet": "Email preview text...",
      "labels": ["INBOX", "UNREAD"]
    }
  ],
  "count": 5
}
```

### Email Read Response
```json
{
  "status": "success",
  "email": {
    "id": "message_id",
    "threadId": "thread_id",
    "from": "sender@example.com",
    "to": "recipient@example.com",
    "subject": "Email Subject",
    "date": "Wed, 9 Jul 2025 14:30:00 +0000",
    "body": "Full email content...",
    "labels": ["INBOX", "UNREAD"]
  }
}
```

## Error Handling

Common errors and solutions:

### 1. Missing Credentials
```
Error: credentials.json not found
```
**Solution**: Download credentials from Google Cloud Console

### 2. Authentication Error
```
Error: Invalid credentials
```
**Solution**: Delete `token.json` and re-authenticate

### 3. Permission Error
```
Error: Insufficient permissions
```
**Solution**: Grant email access during OAuth consent

### 4. Rate Limiting
```
Error: Quota exceeded
```
**Solution**: Wait and try again later

## Security Considerations

1. **Credentials**: Keep `credentials.json` secure and don't commit to version control
2. **Tokens**: The `token.json` file contains sensitive access tokens
3. **Permissions**: Only grant necessary permissions during OAuth consent
4. **Scope**: The system only requests email read/write permissions

## Troubleshooting

### Browser Doesn't Open
- Check terminal for authorization URL
- Copy and paste the URL into your browser
- Complete the OAuth flow manually

### No Emails Found
- Check your Gmail inbox has emails
- Try different search queries
- Verify API permissions are correct

### Slow Performance
- Reduce `max_results` parameter
- Use more specific search queries
- Check your internet connection

## Examples

### List Recent Emails
```
You: Show me my recent emails
🤖 Assistant: I'll list your recent emails from your inbox.

📧 Recent Emails:
1. From: john@example.com
   Subject: Project Update
   Date: Wed, 9 Jul 2025 14:30:00 +0000
   Snippet: Here's the latest update on our project...

2. From: meeting@company.com
   Subject: Team Meeting Tomorrow
   Date: Wed, 9 Jul 2025 13:15:00 +0000
   Snippet: Reminder about tomorrow's team meeting...
```

### Search Emails
```
You: Find emails from john@example.com
🤖 Assistant: I'll search for emails from john@example.com.

🔍 Search Results for "from:john@example.com":
1. From: john@example.com
   Subject: Project Update
   Date: Wed, 9 Jul 2025 14:30:00 +0000
   Snippet: Here's the latest update on our project...

2. From: john@example.com
   Subject: Meeting Notes
   Date: Tue, 8 Jul 2025 16:45:00 +0000
   Snippet: Here are the notes from our meeting...
```

### Read Specific Email
```
You: Read email with ID 1234567890abcdef
🤖 Assistant: I'll read that email for you.

📧 Email Details:
From: john@example.com
To: you@example.com
Subject: Project Update
Date: Wed, 9 Jul 2025 14:30:00 +0000

Body:
Hi there,

Here's the latest update on our project. We've made significant progress...

Best regards,
John
```

## Next Steps

1. **Set up credentials**: Download `credentials.json` from Google Cloud Console
2. **Test functionality**: Run `python3 test_email_reading.py`
3. **Try CLI**: Use natural language commands in the CLI
4. **Explore search**: Try different Gmail search queries
5. **Integrate**: Use email functionality in your workflows

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Verify your Gmail API setup
3. Check the logs for detailed error messages
4. Ensure you have the latest version of the code 