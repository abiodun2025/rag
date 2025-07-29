# Terminal Usage Guide - Dynamic Email Composer

## 🚀 Quick Start

Your dynamic email composer is now working perfectly in the terminal! Here's how to use it:

## 📧 Basic Usage

```bash
python3 send_email.py "your email request"
```

## 📝 Examples

### Professional Emails
```bash
python3 send_email.py "send email to john@company.com asking about the quarterly report"
python3 send_email.py "email client@business.com regarding the proposal review"
python3 send_email.py "compose formal email to investor@venture.com about funding round"
```

### Urgent Emails
```bash
python3 send_email.py "send urgent email to support@service.com about critical system outage"
python3 send_email.py "write urgent email to emergency@hospital.com about patient transfer"
```

### Casual Emails
```bash
python3 send_email.py "send casual email to friend@gmail.com about weekend plans"
python3 send_email.py "email colleague@work.com about coffee chat"
```

### Personal Emails
```bash
python3 send_email.py "send friendly email to grandma@family.com telling her about my new job"
python3 send_email.py "write thank you email to mentor@career.com for their guidance"
```

## 🎭 Supported Tones

The system automatically detects the tone from your request:

- **Professional** (default) - Business-like but approachable
- **Casual** - Informal but respectful
- **Formal** - Highly professional
- **Friendly** - Warm and personable
- **Urgent** - Concise and direct

## ⚡ Urgency Levels

- **Low** - "when convenient", "no rush"
- **Normal** (default) - Standard communication
- **High** - "urgent", "asap", "immediately"

## 🔧 How It Works

1. **Input**: You provide a natural language email request
2. **Analysis**: System extracts email address, tone, urgency, and context
3. **LLM Generation**: Uses your configured LLM to create professional content
4. **Sending**: Sends via MCP tools (no Gmail credentials needed!)

## ✅ Success Example

```bash
$ python3 send_email.py "send email to test@example.com asking about project status"

🚀 Dynamic Email Composer
==================================================
📧 Processing: send email to test@example.com asking about project status
⏳ Composing email with LLM...

✅ Email composed and sent successfully!
==================================================
📧 To: test@example.com
📝 Subject: Checking in on Project Status
📄 Body Preview: Dear test@example.com,
I hope this email finds you well. I am writing to inquire about the status of...
🎭 Tone: professional
⚡ Urgency: normal
🕒 Sent at: 2025-07-28T12:11:32.617998
==================================================
🎉 Email sent via MCP tools!
```

## 🎯 Tips

1. **Include Email Address**: Always include the recipient's email address
2. **Be Specific**: Describe what you want to email about
3. **Use Natural Language**: Write as you would speak
4. **Mention Tone**: If you want a specific tone, include it in your request
5. **Indicate Urgency**: Use urgency words if needed

## 🚨 Troubleshooting

### No Email Address Found
```
❌ Failed to send email: No email address found in the request
💡 Make sure to include a valid email address in your request.
```

**Solution**: Include a valid email address in your request.

### MCP Server Not Running
```
❌ Failed to send email: MCP server connection failed
```

**Solution**: Make sure your MCP server is running.

### LLM Configuration Issues
```
❌ Failed to compose email: LLM configuration error
```

**Solution**: Check your LLM API key and configuration in environment variables.

## 🎉 Ready to Use!

Your dynamic email composer is now fully functional in the terminal. Just describe what you want to email and to whom, and the system will handle the rest!

**Example:**
```bash
python3 send_email.py "send email to john@company.com asking about the quarterly report"
```

The system will automatically:
- ✅ Extract the email address
- ✅ Detect the tone (professional)
- ✅ Generate a professional subject and body
- ✅ Send the email via MCP tools 