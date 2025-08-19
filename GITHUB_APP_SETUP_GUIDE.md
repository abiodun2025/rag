# GitHub App Setup Guide for Code Review Agent

## Overview

This guide will help you set up a GitHub App to work with your original code review agent design. The agent is designed to use GitHub Apps for secure, automated code reviews via webhooks.

## Prerequisites

- A GitHub account
- Access to repositories you want to review
- Python 3.7+ installed
- Your code review agent running

## Step 1: Create a GitHub App

### 1.1 Go to GitHub App Settings
1. Log in to your GitHub account
2. Go to: https://github.com/settings/apps
3. Click **"New GitHub App"**

### 1.2 Configure Basic App Information
Fill in the following details:

**App name:** `AI Code Review Agent` (or your preferred name)
**Description:** `AI-powered code review agent for automated pull request reviews`
**Homepage URL:** `http://localhost:8000` (for development)
**Webhook URL:** `http://localhost:8000/webhook/github` (for development)
**Webhook secret:** Generate a random secret (you'll need this later)

### 1.3 Set App Permissions

#### Repository Permissions:
- **Contents:** `Read & write` (to read code and post comments)
- **Issues:** `Read & write` (to post review comments)
- **Pull requests:** `Read & write` (to access PR data and post reviews)
- **Metadata:** `Read-only` (to access repository metadata)

#### User Permissions:
- **Email addresses:** `Read-only` (to identify users)

### 1.4 Set App Events
Select these events to trigger webhooks:
- ✅ **Pull request** (when PRs are created, updated, or closed)
- ✅ **Push** (optional, for additional triggers)

### 1.5 Create the App
Click **"Create GitHub App"**

## Step 2: Get App Credentials

### 2.1 App ID
After creating the app, you'll see the **App ID** on the app page. Copy this number.

### 2.2 Generate Private Key
1. Scroll down to **"Private keys"** section
2. Click **"Generate private key"**
3. Download the `.pem` file
4. **IMPORTANT:** Save this file securely - you won't be able to download it again!

### 2.3 Webhook Secret
Use the webhook secret you created in Step 1.2, or generate a new one.

## Step 3: Install the App

### 3.1 Install on Your Account
1. Go to your app's page
2. Click **"Install App"**
3. Choose **"Install"** to install on your account
4. Select repositories you want to review

### 3.2 Get Installation ID
After installation, note the **Installation ID** from the URL or app page.

## Step 4: Configure Environment Variables

### 4.1 Update Your .env File
Replace the placeholder values in your `.env` file:

```bash
# GitHub App Configuration
GITHUB_APP_ID=your_app_id_here
GITHUB_PRIVATE_KEY=-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA...
... (your private key content)
-----END RSA PRIVATE KEY-----
GITHUB_WEBHOOK_SECRET=your_webhook_secret_here

# Cohere API Configuration
COHERE_API_KEY=slWKgs6BU99wREgK8ba8x7b53YLD2U3xUkDBweI1

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=false
LOG_LEVEL=INFO
```

### 4.2 Private Key Format
You can either:
- **Option A:** Put the entire private key content in the .env file
- **Option B:** Save the .pem file and reference its path

For Option B, update the config to use a file path:
```bash
GITHUB_PRIVATE_KEY=/path/to/your/private-key.pem
```

## Step 5: Test the Setup

### 5.1 Test Environment Configuration
```bash
python code_review_cli.py test-env
```

### 5.2 Test GitHub Client
```bash
python code_review_cli.py test-github
```

### 5.3 Test All Components
```bash
python code_review_cli.py test-all
```

## Step 6: Start the Server

### 6.1 Development Mode
```bash
python code_review_cli.py server --host 127.0.0.1 --port 8000
```

### 6.2 Production Mode
```bash
python code_review_cli.py server --host 0.0.0.0 --port 8000
```

## Step 7: Configure Webhooks

### 7.1 For Development (ngrok)
If testing locally, use ngrok to expose your server:

```bash
# Install ngrok
brew install ngrok

# Expose your server
ngrok http 8000

# Update your GitHub App webhook URL with the ngrok URL
# Example: https://abc123.ngrok.io/webhook/github
```

### 7.2 For Production
Update your GitHub App webhook URL to your production server:
- **Webhook URL:** `https://your-domain.com/webhook/github`
- **Webhook Secret:** Use the same secret from your .env file

## Step 8: Test Webhook Integration

### 8.1 Create a Test PR
1. Create a new pull request in a repository where the app is installed
2. The webhook should trigger automatically
3. Check your server logs for webhook events

### 8.2 Manual Review Test
```bash
python code_review_cli.py review
```

## Troubleshooting

### Common Issues

#### 1. "Invalid webhook signature"
- Check that your webhook secret matches in both GitHub App and .env file
- Ensure the webhook URL is correct

#### 2. "Failed to generate JWT"
- Verify your private key format is correct
- Check that GITHUB_APP_ID is set correctly

#### 3. "Installation not found"
- Make sure the app is installed on the repository
- Verify the installation ID is correct

#### 4. "Permission denied"
- Check that the app has the required permissions
- Ensure the app is installed on the target repository

### Debug Commands

```bash
# Test individual components
python code_review_cli.py test-env
python code_review_cli.py test-github
python code_review_cli.py test-service
python code_review_cli.py test-webhook
python code_review_cli.py test-app

# Run all tests
python code_review_cli.py test-all

# Start server with debug logging
LOG_LEVEL=DEBUG python code_review_cli.py server
```

## Security Best Practices

### 1. Private Key Security
- Never commit private keys to version control
- Use environment variables or secure file storage
- Rotate keys regularly

### 2. Webhook Security
- Use strong webhook secrets
- Verify webhook signatures
- Use HTTPS in production

### 3. App Permissions
- Grant minimum required permissions
- Review app access regularly
- Uninstall from unused repositories

## Production Deployment

### 1. Server Requirements
- HTTPS enabled
- Valid SSL certificate
- Proper firewall configuration
- Process management (systemd, supervisor, etc.)

### 2. Environment Variables
- Use production environment variables
- Secure secret management
- Database for storing app state (if needed)

### 3. Monitoring
- Log monitoring
- Health checks
- Error alerting
- Performance monitoring

---

**Your original design is production-ready and much more sophisticated than the simple token-based approach!** 🚀 