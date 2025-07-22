# User-Friendly CLI Commands for Message Storage

## 🎯 **Simple Commands for Different Storage Locations**

### **Save Messages to Desktop:**
```
You: save to desktop:"Hello world, this goes to my Desktop"
You: save to desktop:"Meeting notes for tomorrow"
You: save to desktop:"Important reminder about the project"
```

### **Save Messages to Project Directory:**
```
You: save to project:"This goes to the project folder"
You: save to project:"Development notes"
You: save to project:"Code review comments"
```

### **View Saved Messages:**

**Show Desktop Messages:**
```
You: show desktop messages
You: show desktop messages (limit 5)
```

**Show Project Messages:**
```
You: show project messages
You: show project messages (limit 10)
```

## 📁 **Storage Locations:**

### **Desktop Storage:**
- **Location**: `/Users/ola/Desktop/save_message/`
- **Organization**: By date (YYYY/MM/DD)
- **Format**: JSON files with metadata

### **Project Storage:**
- **Location**: `messages/` (in project directory)
- **Organization**: By date (YYYY/MM/DD)
- **Format**: JSON files with metadata

## 🔧 **Advanced Commands (Still Available):**

### **Technical Commands:**
```
You: save_desktop_message:"Technical command"
You: save_message:"Project storage command"
You: list_desktop_messages
You: list_messages
```

## 💡 **Examples:**

### **Scenario 1: Quick Note to Desktop**
```
You: save to desktop:"Remember to call John tomorrow at 2 PM"
🤖 Assistant: Message saved to Desktop.
```

### **Scenario 2: Project Documentation**
```
You: save to project:"API endpoint /users returns user data in JSON format"
🤖 Assistant: Message saved to project directory.
```

### **Scenario 3: Check What's Saved**
```
You: show desktop messages
🤖 Assistant: Here are your saved desktop messages:
- "Remember to call John tomorrow at 2 PM"
- "Meeting notes for tomorrow"
```

## 🎯 **Key Benefits:**

1. **Easy to Remember**: Simple commands like "save to desktop"
2. **Clear Intent**: You know exactly where your message will be saved
3. **Quick Access**: Desktop messages are easy to find in Finder
4. **Organized**: Both locations organize files by date automatically

## 🚀 **Getting Started:**

1. **Start the CLI**: `python3 cli.py`
2. **Try a simple command**: `save to desktop:"Hello world"`
3. **Check your Desktop**: Look for the `save_message` folder
4. **View saved messages**: `show desktop messages`

## 📝 **File Format:**

Each saved message creates a JSON file with:
- Message content
- Timestamp
- Message type
- Unique ID
- Metadata (if provided)

Example:
```json
{
  "message": "Hello world",
  "message_type": "user_message",
  "timestamp": "2025-07-09T22:38:20.938646",
  "id": "bdb65be1-088e-4a5d-a1f8-9b8ded1d20b5",
  "metadata": {}
}
``` 