# 🎤 Voice Email Composer Guide

## Overview

The Voice Email Composer allows you to compose and send emails using natural voice commands. Simply speak your email request, and the AI will automatically compose and send the email for you.

## 🚀 Quick Start

### 1. Test the System
```bash
python test_voice_email.py
```

### 2. Start Voice Email Session
```bash
python voice_email.py
```

### 3. Speak Your Email Request
When prompted, speak naturally about the email you want to send.

## 💡 Voice Command Examples

### Simple Commands
```
🎤 "send email to john@company.com"
🎤 "email sarah@gmail.com about the meeting"
🎤 "write urgent email to support@service.com"
🎤 "compose casual email to friend@gmail.com"
```

### Detailed Commands
```
🎤 "send email to client@business.com about the quarterly report and budget requests"
🎤 "write formal email to investor@venture.com regarding funding round"
🎤 "send friendly email to grandma@family.com telling her about my new job"
🎤 "compose urgent email to team@startup.com about the deadline extension"
```

### Professional Commands
```
🎤 "send professional email to ceo@corporation.com regarding partnership proposal"
🎤 "write formal email to hr@company.com about vacation request"
🎤 "compose business email to vendor@supplier.com about contract renewal"
```

## 🎯 How It Works

1. **Voice Recognition**: Your speech is converted to text using Google Speech Recognition
2. **Intent Analysis**: The AI analyzes your request to extract:
   - Recipient email address
   - Email tone (formal, casual, urgent, etc.)
   - Purpose and context
   - Urgency level
3. **Email Composition**: The AI generates a professional email with:
   - Appropriate subject line
   - Well-structured body
   - Proper tone and formatting
4. **Email Sending**: The email is sent using MCP tools

## 🔧 Technical Details

### Dependencies
- `SpeechRecognition`: For voice-to-text conversion
- `pyaudio`: For microphone access
- `agent.dynamic_email_composer`: For email composition
- `agent.mcp_tools`: For email sending

### System Requirements
- Microphone access
- Internet connection (for speech recognition)
- Python 3.7+

## 📋 Voice Command Patterns

### Basic Pattern
```
[action] email to [email_address] [about/regarding] [topic]
```

### Examples
- `send email to john@example.com about the meeting`
- `write email to sarah@gmail.com regarding the project`
- `compose email to support@service.com about my account`

### Tone Indicators
- **Formal**: "formal email", "professional email", "business email"
- **Casual**: "casual email", "friendly email", "personal email"
- **Urgent**: "urgent email", "immediate email", "asap email"

## 🎤 Voice Tips

### For Better Recognition
1. **Speak clearly** and at a normal pace
2. **Use a quiet environment** to reduce background noise
3. **Speak complete sentences** rather than fragments
4. **Include the email address** in your command
5. **Mention the topic** or purpose of the email

### Example Good Commands
```
✅ "send email to john@company.com about tomorrow's meeting"
✅ "write urgent email to support@service.com about my login issue"
✅ "compose formal email to client@business.com regarding the proposal"
```

### Example Avoid Commands
```
❌ "email john" (missing email address)
❌ "send email" (missing recipient and topic)
❌ "write to company" (too vague)
```

## 🔍 Troubleshooting

### Microphone Issues
```bash
# Test microphone access
python -c "
import speech_recognition as sr
r = sr.Recognizer()
with sr.Microphone() as source:
    print('Test your microphone...')
    audio = r.listen(source)
    text = r.recognize_google(audio)
    print(f'You said: {text}')
"
```

### Speech Recognition Issues
- **"Could not understand audio"**: Speak more clearly or reduce background noise
- **"No speech detected"**: Check microphone permissions and speak louder
- **"Speech recognition service error"**: Check internet connection

### Email Composition Issues
- **Missing email address**: Include the full email address in your command
- **Vague topic**: Be more specific about what the email should be about
- **Wrong tone**: Use tone indicators like "formal", "casual", or "urgent"

## 🎯 Advanced Usage

### Integration with Smart Agent
```python
from agent.voice_email_composer import compose_email_from_voice_command
from agent.smart_master_agent import smart_master_agent

# Use voice commands with smart agent
voice_command = "send email to client@company.com about the proposal"
result = await smart_master_agent.process_message(voice_command, "voice_session", "user")
```

### Custom Voice Commands
You can extend the system to handle custom voice commands by modifying the `VoiceEmailComposer` class.

### Batch Email Processing
```python
# Process multiple voice commands
commands = [
    "send email to team@company.com about weekly update",
    "write urgent email to manager@company.com about deadline",
    "compose casual email to friend@gmail.com about weekend plans"
]

for command in commands:
    result = await compose_email_from_voice_command(command)
    print(f"Email sent: {result.get('to_email')}")
```

## 📊 Performance Tips

1. **Calibrate microphone** in a quiet environment
2. **Use consistent speech patterns** for better recognition
3. **Keep commands concise** but complete
4. **Test with simple commands** first before complex ones

## 🔒 Privacy & Security

- Voice commands are processed by Google Speech Recognition
- Email content is generated locally using your LLM
- No voice data is stored permanently
- Email addresses and content are processed securely

## 🆘 Support

If you encounter issues:

1. **Run the test script**: `python test_voice_email.py`
2. **Check microphone permissions** in system settings
3. **Verify internet connection** for speech recognition
4. **Test with simple commands** first
5. **Check the logs** for detailed error messages

## 🎉 Success Stories

Users have successfully used voice commands for:
- ✅ Sending meeting confirmations
- ✅ Writing follow-up emails
- ✅ Composing urgent notifications
- ✅ Sending casual updates to friends
- ✅ Writing formal business communications

---

**Ready to try?** Run `python voice_email.py` and start speaking your email requests! 