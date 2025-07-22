# Gmail API Setup Guide

## Overview
This guide will help you set up Gmail API credentials so your agent can actually send emails through your Gmail account.

## Step-by-Step Setup

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" at the top
3. Click "New Project"
4. Enter a project name (e.g., "Email Agent Project")
5. Click "Create"

### Step 2: Enable Gmail API

1. In your project, go to "APIs & Services" > "Library"
2. Search for "Gmail API"
3. Click on "Gmail API"
4. Click "Enable"

### Step 3: Create OAuth 2.0 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth 2.0 Client IDs"
3. If prompted, configure the OAuth consent screen:
   - User Type: External
   - App name: "Email Agent"
   - User support email: Your email
   - Developer contact information: Your email
   - Save and continue through the steps
4. Back to credentials, click "Create Credentials" > "OAuth 2.0 Client IDs"
5. Application type: "Desktop application"
6. Name: "Email Agent Desktop"
7. Click "Create"
8. Download the JSON file (click the download button)
9. Rename the downloaded file to `credentials.json`
10. Place `credentials.json` in your project directory

### Step 4: Test the Setup

Run the test script to verify everything is working:

```bash
python3 test_email_setup.py
```

## Expected Behavior

### First Run (Authentication)
- The script will open your browser
- You'll be asked to sign in to your Google account
- You'll see a warning about the app not being verified (this is normal for development)
- Click "Advanced" > "Go to [Project Name] (unsafe)"
- Click "Allow"
- The browser will close and return to the terminal

### Subsequent Runs
- The script will use cached authentication
- No browser popup needed
- Emails will be sent directly

## Troubleshooting

### Common Issues:

1. **"credentials.json not found"**
   - Make sure you downloaded the credentials file
   - Ensure it's named exactly `credentials.json`
   - Place it in the project root directory

2. **"App not verified" warning**
   - This is normal for development
   - Click "Advanced" > "Go to [Project Name] (unsafe)"
   - This is safe for personal use

3. **Authentication errors**
   - Delete `token.pickle` if it exists
   - Re-run the script to trigger new authentication

4. **"Quota exceeded" errors**
   - Gmail API has daily limits
   - Check your Google Cloud Console for quota usage

## Security Notes

- `credentials.json` contains sensitive information
- Add it to `.gitignore` to prevent accidental commits
- For production, use service accounts instead of OAuth

## Testing Email Functionality

Once set up, test with:

```bash
# Test the setup
python3 test_email_setup.py

# Test via CLI
python3 cli.py
# Then try: "Send an email to test@example.com with subject Test and body Hello"
```

## File Structure After Setup

```
agentic-rag-knowledge-graph/
├── credentials.json          # Gmail API credentials (you'll add this)
├── token.pickle             # Cached authentication (auto-generated)
├── agent/
│   ├── email_tools.py       # Gmail integration
│   └── ...
└── ...
```

## Next Steps

1. Follow the setup steps above
2. Test with `python3 test_email_setup.py`
3. Try sending emails via CLI
4. Your agent will now be able to send real emails! 