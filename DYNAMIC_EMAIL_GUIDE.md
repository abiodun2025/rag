# Dynamic Email Composer Guide

## 🚀 LLM-Powered Email Composition

Your agent now has the ability to compose any email dynamically using LLM (Large Language Model) technology. This means you can simply describe what you want to email and to whom, and the agent will automatically generate professional email content.

## ✨ Features

- **🎯 Automatic Intent Detection** - Recognizes any email request
- **📧 Email Address Extraction** - Finds email addresses in any format
- **📝 Dynamic Content Generation** - Uses LLM to create professional email content
- **🎭 Multiple Tones** - Professional, casual, formal, friendly, urgent
- **⚡ Urgency Levels** - Low, normal, high priority
- **🤖 Smart Context Analysis** - Understands the purpose and context of your request

## 📧 How to Use

### Method 1: Natural Language Requests

Simply tell the agent what you want to email:

```
"send email to john@company.com asking about the quarterly report"
"email sarah@gmail.com about the meeting tomorrow"
"write urgent email to support@service.com about system outage"
"compose casual email to friend@email.com about weekend plans"
```

### Method 2: Direct Function Calls

```python
from agent.dynamic_email_composer import compose_dynamic_email

# Compose a professional email
result = await compose_dynamic_email(
    to_email="john@company.com",
    context="asking about the quarterly report",
    tone="professional",
    urgency="normal"
)
```

### Method 3: Smart Agent Integration

The smart master agent automatically uses the dynamic email composer:

```python
from agent.smart_master_agent import SmartMasterAgent

agent = SmartMasterAgent()
result = await agent.process_message(
    "send email to client@business.com about project timeline",
    session_id="your_session",
    user_id="your_user_id"
)
```

## 🎭 Supported Email Tones

### Professional (Default)
- Business-like but approachable
- Clear and concise
- Appropriate for work communications

### Casual
- Informal but respectful
- Conversational tone
- Good for friendly work emails

### Formal
- Highly professional
- Business language
- Appropriate for official communications

### Friendly
- Warm and personable
- Encouraging and positive
- Good for personal or warm business relationships

### Urgent
- Concise and direct
- Emphasizes urgency appropriately
- Clear next steps

## ⚡ Urgency Levels

### Low
- "When convenient"
- "No rush"
- "Take your time"

### Normal (Default)
- Standard business communication
- Regular priority

### High
- "Urgent"
- "ASAP"
- "Immediately"
- "Emergency"

## 📝 Example Requests

### Business Communications
```
"send email to manager@company.com about quarterly results and budget requests"
"email client@business.com regarding the proposal review"
"compose formal email to investor@venture.com about funding round"
```

### Personal Communications
```
"send friendly email to grandma@family.com telling her about my new job"
"email friend@gmail.com about weekend plans"
"write casual email to mentor@career.com thanking them for guidance"
```

### Technical Issues
```
"send urgent email to support@service.com about critical system outage"
"email dev@tech.com about API integration errors"
"compose email to team@project.com about sprint planning"
```

### Follow-ups and Apologies
```
"send follow-up email to client@business.com about missed deadline"
"write apology email to customer@service.com for the delay"
"email colleague@work.com thanking them for their help"
```

## 🔧 Technical Details

### Email Request Analysis

The system automatically analyzes your request to extract:

1. **Email Address** - Using regex pattern matching
2. **Tone** - Based on keywords in your request
3. **Urgency** - Detected from urgency indicators
4. **Purpose** - Meeting, follow-up, question, thank you, apology, etc.
5. **Context** - The main content of your request

### LLM Content Generation

The system uses your configured LLM model to:

1. **Generate Subject Lines** - Clear and appropriate
2. **Compose Email Body** - Professional and contextual
3. **Apply Tone** - Match the requested tone
4. **Handle Urgency** - Adjust content based on urgency level

### Email Sending

The composed email is sent using:

1. **Gmail API** - For Gmail accounts
2. **MCP Tools** - For system-level email sending
3. **SMTP** - For other email providers

## 🛠️ Configuration

### LLM Model

The system uses your configured LLM model from `agent/providers.py`:

```python
# Default configuration
LLM_CHOICE = "gpt-4-turbo-preview"  # or your preferred model
LLM_API_KEY = "your_api_key"
LLM_BASE_URL = "https://api.openai.com/v1"  # or your provider
```

### Email Templates

The system includes pre-built templates for each tone:

- Professional template
- Casual template  
- Formal template
- Friendly template
- Urgent template

## 🚨 Error Handling

The system handles various error scenarios:

- **No Email Address** - Prompts for valid email
- **LLM Generation Failure** - Falls back to basic email
- **Email Sending Failure** - Provides error details
- **Invalid Tone/Urgency** - Uses defaults

## 📊 Success Metrics

The system provides detailed feedback:

- Email composition success/failure
- Generated subject and body preview
- Detected tone and urgency
- Timestamp and message IDs
- Error details if applicable

## 🎯 Best Practices

1. **Be Specific** - Include the email address and context
2. **Use Natural Language** - Write as you would speak
3. **Include Purpose** - Mention what the email is about
4. **Specify Tone** - If you want a particular tone, mention it
5. **Indicate Urgency** - Use urgency words if needed

## 🔄 Integration

The dynamic email composer is integrated with:

- **Smart Master Agent** - Automatic email handling
- **CLI Interface** - Command-line email composition
- **API Endpoints** - REST API for email composition
- **MCP Tools** - System-level email sending

## 🎉 Ready to Use!

Your agent is now ready to handle any email request with LLM-powered content generation. Just describe what you want to email and to whom, and the agent will do the rest!

---

**Example Usage:**
```
User: "send email to john@company.com asking about the quarterly report"
Agent: ✅ Email composed and sent successfully!
       📧 To: john@company.com
       📝 Subject: Quarterly Report Inquiry
       📄 Body: Professional email content generated by LLM...
       🎭 Tone: professional
       ⚡ Urgency: normal
``` 