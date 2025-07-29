# Minimal Email Composition Guide

## 🚀 Ultra-Simple Email Requests

Your agent can compose professional emails with **minimal information**! Just provide an email address and optionally a tone, and the agent will generate appropriate content.

## 📧 Minimal Request Examples

### Just Email Address
```bash
python3 compose_email.py "john@company.com"
python3 compose_email.py "sarah@gmail.com"
python3 compose_email.py "client@business.com"
```

### Email Address + Tone
```bash
python3 compose_email.py "casual friend@gmail.com"
python3 compose_email.py "formal investor@venture.com"
python3 compose_email.py "urgent support@service.com"
python3 compose_email.py "friendly grandma@family.com"
```

### Minimal Commands
```bash
python3 compose_email.py "email john@company.com"
python3 compose_email.py "send to sarah@gmail.com"
python3 compose_email.py "write to client@business.com"
```

### Tone + Email
```bash
python3 compose_email.py "professional manager@work.com"
python3 compose_email.py "casual colleague@office.com"
python3 compose_email.py "urgent emergency@hospital.com"
```

## 🎭 Automatic Tone Detection

The agent automatically detects tone from minimal keywords:

- **Professional** (default) - No tone specified
- **Casual** - "casual", "friendly", "informal"
- **Formal** - "formal", "business", "official"
- **Urgent** - "urgent", "asap", "emergency"
- **Friendly** - "friendly", "warm", "personal"

## ✅ Test Results

All these minimal requests work perfectly:

```bash
# Just email address
python3 compose_email.py "john@company.com"
✅ Subject: Follow-up on Your Recent Inquiry
✅ Tone: professional

# Email + tone
python3 compose_email.py "casual friend@gmail.com"
✅ Subject: Just catching up!
✅ Tone: casual

# Minimal command
python3 compose_email.py "email sarah@gmail.com"
✅ Subject: Connecting with [Your Name]
✅ Tone: professional

# Urgent minimal
python3 compose_email.py "urgent to support@service.com"
✅ Subject: Urgent Attention Required
✅ Tone: urgent
```

## 🎯 How It Works

1. **Extract Email** - Finds email address in your request
2. **Detect Tone** - Identifies tone from keywords or uses professional default
3. **Generate Content** - LLM creates appropriate subject and body
4. **Send Email** - Sends via MCP tools

## 💡 Tips for Minimal Requests

- **Just email address** = Professional tone
- **Add tone word** = Specific tone (casual, formal, urgent, friendly)
- **Any email format** = Works with any valid email address
- **No context needed** = Agent generates appropriate content

## 🎉 Ready to Use!

Your agent can now compose emails with **minimal information**:

```bash
# Ultra-minimal
python3 compose_email.py "john@company.com"

# With tone
python3 compose_email.py "casual friend@gmail.com"

# Minimal command
python3 compose_email.py "email client@business.com"
```

The agent will automatically:
- ✅ Extract the email address
- ✅ Detect appropriate tone
- ✅ Generate professional content
- ✅ Send the email

**Perfect for quick, professional communication!** 🚀📧 