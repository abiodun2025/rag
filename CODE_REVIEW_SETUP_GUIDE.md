# GitHub AI Code Review Agent - Setup Guide

## Overview

The GitHub AI Code Review Agent is an intelligent system that automatically reviews pull requests using AI-powered analysis. It listens to GitHub webhook events, analyzes code changes, and posts constructive feedback directly to pull requests.

## Features

- ✅ **Automatic PR Review**: Listens to GitHub webhook events
- ✅ **AI-Powered Analysis**: Uses Cohere API for intelligent code review
- ✅ **Line-by-Line Comments**: Posts specific feedback to relevant code lines
- ✅ **Security Focus**: Identifies potential security vulnerabilities
- ✅ **Best Practices**: Suggests improvements based on coding standards
- ✅ **Multi-Language Support**: Reviews Python, JavaScript, TypeScript, Java, and more
- ✅ **Webhook Security**: Verifies GitHub webhook signatures
- ✅ **Comprehensive Logging**: Tracks all review activity

## Architecture

```
GitHub PR Event → Webhook → FastAPI Server → AI Analysis → GitHub Comments
```

## Prerequisites

1. **Python 3.8+**
2. **GitHub App** (for authentication)
3. **Cohere API Key** (for AI analysis)
4. **Public URL** (for webhook delivery)

## Installation

### 1. Clone and Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd rag

# Install dependencies
pip install -r requirements.txt

# Install additional dependencies for code review
pip install fastapi uvicorn cohere PyGithub python-jose[cryptography] python-dotenv
```

### 2. Environment Configuration

Create a `.env` file in the project root:

```env
# GitHub App Configuration
GITHUB_APP_ID=your_github_app_id
GITHUB_PRIVATE_KEY=your_private_key_or_path_to_key_file
GITHUB_WEBHOOK_SECRET=your_webhook_secret

# Cohere API Configuration
COHERE_API_KEY=your_cohere_api_key

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=false
LOG_LEVEL=INFO
```

### 3. GitHub App Setup

#### Create a GitHub App

1. Go to [GitHub Developer Settings](https://github.com/settings/apps)
2. Click "New GitHub App"
3. Configure the app:
   - **App name**: `AI Code Review Agent`
   - **Homepage URL**: `https://your-domain.com`
   - **Webhook URL**: `https://your-domain.com/webhook/github`
   - **Webhook secret**: Generate a secure secret

#### Set Permissions

- **Repository permissions**:
  - `Pull requests`: Read & Write
  - `Contents`: Read
  - `Metadata`: Read

- **Subscribe to events**:
  - `Pull requests`

#### Generate Private Key

1. In your GitHub App settings, click "Generate private key"
2. Download the `.pem` file
3. Add the key content to your `.env` file or provide the file path

### 4. Cohere API Setup

1. Sign up at [Cohere](https://cohere.ai/)
2. Get your API key from the dashboard
3. Add it to your `.env` file

## Running the Agent

### Development Mode

```bash
# Run the server
python -m app.main

# Or using uvicorn directly
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Production Mode

```bash
# Using gunicorn (recommended for production)
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Using Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Testing

### Run the Test Suite

```bash
python test_code_review_agent.py
```

This will test:
- Environment configuration
- GitHub client initialization
- Code review service
- Webhook signature verification
- FastAPI app setup
- Manual code review functionality

### Manual Testing

#### Test Webhook Endpoint

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test manual review endpoint
curl -X POST http://localhost:8000/review \
  -H "Content-Type: application/json" \
  -d '{
    "owner": "testowner",
    "repo": "testrepo",
    "pr_number": 123,
    "diff_content": "diff --git a/test.py b/test.py\nindex 123..456 100644\n--- a/test.py\n+++ b/test.py\n@@ -1,3 +1,5 @@\n def hello():\n-    print(\"Hello\")\n+    print(\"Hello, World!\")\n+    return True",
    "changed_files": ["test.py"]
  }'
```

#### Test with ngrok (for local development)

```bash
# Install ngrok
npm install -g ngrok

# Expose your local server
ngrok http 8000

# Use the ngrok URL as your webhook URL in GitHub App settings
```

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GITHUB_APP_ID` | GitHub App ID | Yes |
| `GITHUB_PRIVATE_KEY` | Private key content or file path | Yes |
| `GITHUB_WEBHOOK_SECRET` | Webhook secret for signature verification | Yes |
| `COHERE_API_KEY` | Cohere API key for AI analysis | Yes |
| `HOST` | Server host (default: 0.0.0.0) | No |
| `PORT` | Server port (default: 8000) | No |
| `DEBUG` | Debug mode (default: false) | No |
| `LOG_LEVEL` | Logging level (default: INFO) | No |

### Code Review Settings

The AI review behavior can be customized in `app/code_review_service.py`:

- **Model**: Currently uses Cohere's "command" model
- **Temperature**: Controls creativity (0.3 for balanced reviews)
- **Max tokens**: Limits response length (1000 tokens)
- **Prompt template**: Customizable review instructions

## API Endpoints

### Health Check
- **GET** `/` - Basic health check
- **GET** `/health` - Detailed health status

### Webhook
- **POST** `/webhook/github` - GitHub webhook endpoint

### Manual Review
- **POST** `/review` - Manual code review (for testing)

## Monitoring and Logging

### Log Levels

- `DEBUG`: Detailed debugging information
- `INFO`: General operational messages
- `WARNING`: Warning messages
- `ERROR`: Error messages

### Key Log Events

- Webhook received and verified
- PR analysis started/completed
- Comments posted to GitHub
- Errors and exceptions

### Monitoring

Monitor these metrics:
- Webhook processing time
- AI analysis response time
- Comment posting success rate
- Error rates and types

## Troubleshooting

### Common Issues

#### 1. Webhook Signature Verification Fails

**Symptoms**: 401 errors in webhook logs

**Solutions**:
- Verify `GITHUB_WEBHOOK_SECRET` matches GitHub App settings
- Check webhook URL is correct
- Ensure HTTPS is used in production

#### 2. GitHub API Authentication Fails

**Symptoms**: 401/403 errors when posting comments

**Solutions**:
- Verify `GITHUB_APP_ID` and `GITHUB_PRIVATE_KEY`
- Check app has correct permissions
- Ensure app is installed on target repositories

#### 3. Cohere API Errors

**Symptoms**: AI analysis fails

**Solutions**:
- Verify `COHERE_API_KEY` is valid
- Check API quota and limits
- Ensure internet connectivity

#### 4. No Comments Posted

**Symptoms**: Webhook processes but no comments appear

**Solutions**:
- Check app has "Pull requests" write permission
- Verify installation ID in webhook payload
- Review logs for specific error messages

### Debug Mode

Enable debug logging:

```env
DEBUG=true
LOG_LEVEL=DEBUG
```

### Testing Webhook Locally

Use ngrok to expose your local server:

```bash
ngrok http 8000
```

Then use the ngrok URL as your webhook URL in GitHub App settings.

## Security Considerations

1. **Webhook Verification**: Always verify webhook signatures
2. **Private Key Security**: Store private keys securely
3. **HTTPS**: Use HTTPS in production
4. **Rate Limiting**: Implement rate limiting for webhook endpoints
5. **Input Validation**: Validate all webhook payloads
6. **Error Handling**: Don't expose sensitive information in error messages

## Performance Optimization

1. **Async Processing**: Use async/await for I/O operations
2. **Connection Pooling**: Reuse GitHub API connections
3. **Caching**: Cache frequently accessed data
4. **Load Balancing**: Use multiple workers in production
5. **Monitoring**: Monitor response times and error rates

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

[Your License Here]

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs
3. Create an issue in the repository
4. Contact the maintainers

---

**Happy coding! 🚀** 