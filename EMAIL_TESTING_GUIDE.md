# Email Agent Testing Guide

## Overview
Your agentic RAG system now includes email composition and sending capabilities using Gmail API. This guide will help you test the email functionality.

## Current Status ✅
- ✅ Email tools are properly integrated into the agent
- ✅ Agent understands email requests and responds appropriately
- ✅ Email composition tool is registered and functional
- ❌ Gmail credentials are missing (needed for actual email sending)

## Testing Methods

### 1. **Quick Test (No Gmail Setup Required)**
Test if the agent understands email requests:

```bash
python3 test_email_agent_simple.py
```

This will verify that:
- Agent recognizes email requests
- Agent responds appropriately to email commands
- Email tool is properly integrated

### 2. **Interactive CLI Testing**
Start the CLI and test email functionality interactively:

```bash
# Terminal 1: Start API server
python3 -m uvicorn agent.api:app --host 0.0.0.0 --port 8058

# Terminal 2: Start CLI
python3 cli.py
```

Then try these commands in the CLI:
```
Send an email to test@example.com with subject Test and body Hello
Compose an email to john@company.com about AI updates
Send an email to tech@startup.com with subject Meeting Request
```

### 3. **Full Email Functionality (Requires Gmail Setup)**

#### Step 1: Install Gmail API Packages
```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

#### Step 2: Set Up Gmail API Credentials
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Gmail API:
   - Go to "APIs & Services" > "Library"
   - Search for "Gmail API"
   - Click "Enable"
4. Create OAuth 2.0 credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth 2.0 Client IDs"
   - Choose "Desktop application"
   - Download the credentials as `credentials.json`
5. Place `credentials.json` in your project directory

#### Step 3: Test Full Email Functionality
```bash
python3 test_email_setup.py
```

This will:
- Check Gmail setup
- Test email tools directly
- Test via API
- Provide detailed feedback

## Expected Behavior

### Without Gmail Credentials:
- Agent understands email requests
- Agent attempts to use email tool
- Tool returns error about missing credentials
- Agent explains the issue to user

### With Gmail Credentials:
- Agent composes and sends emails
- First run will open browser for OAuth authentication
- Subsequent runs will use cached token
- Emails are sent via Gmail API

## Test Commands

### Basic Email Commands:
```
Send an email to test@example.com with subject Test and body Hello
Compose an email to john@company.com about AI updates
Send an email to tech@startup.com with subject Meeting Request
```

### Email with Context:
```
Compose an email to john@company.com about AI project updates. Subject should be 'AI Project Update' and include information about our progress.
Send an email to tech@startup.com with subject 'Meeting Request' and body 'I would like to schedule a meeting to discuss AI integration opportunities.'
```

## Troubleshooting

### Common Issues:

1. **"Missing credentials.json"**
   - Follow the Gmail API setup instructions above
   - Ensure `credentials.json` is in the project root

2. **"Module not found" errors**
   - Install Gmail packages: `pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib`

3. **API server not running**
   - Start with: `python3 -m uvicorn agent.api:app --host 0.0.0.0 --port 8058`

4. **OAuth authentication issues**
   - Delete `token.pickle` if it exists
   - Re-run the email tool to trigger new authentication

## File Structure
```
agentic-rag-knowledge-graph/
├── agent/
│   ├── email_tools.py          # Gmail API integration
│   ├── tools.py                # Email tool registration
│   └── agent.py                # Email tool in agent
├── credentials.json            # Gmail API credentials (you need to add this)
├── test_email_setup.py         # Comprehensive test script
├── test_email_agent_simple.py  # Simple understanding test
└── EMAIL_TESTING_GUIDE.md     # This guide
```

## Next Steps

1. **For Testing Understanding**: Use `test_email_agent_simple.py`
2. **For Full Functionality**: Set up Gmail credentials and use `test_email_setup.py`
3. **For Interactive Testing**: Use the CLI with email commands
4. **For Production**: Ensure proper Gmail API setup and error handling

## Security Notes

- `credentials.json` contains sensitive information - don't commit to version control
- Add `credentials.json` and `token.pickle` to `.gitignore`
- Use environment variables for production deployments
- Consider using service accounts for production email sending 