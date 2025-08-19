# 🤖 Interactive GitHub AI Agent - Setup Guide

## 🚀 **Quick Setup**

### **1. Create Environment File**

Create a `.env` file in the project root with your credentials:

```bash
# Create .env file
touch .env
```

Add the following content to your `.env` file:

```env
# GitHub Configuration (REQUIRED for interactive agent)
GITHUB_TOKEN=your_github_personal_access_token_here

# Cohere API Configuration (Already configured)
COHERE_API_KEY=slWKgs6BU99wREgK8ba8x7b53YLD2U3xUkDBweI1

# GitHub App Configuration (for webhook-based agent)
GITHUB_APP_ID=your_github_app_id_here
GITHUB_PRIVATE_KEY=your_private_key_content_or_path_here
GITHUB_WEBHOOK_SECRET=your_webhook_secret_here

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=false
LOG_LEVEL=INFO
```

### **2. Get GitHub Personal Access Token**

1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Give it a name like "Interactive AI Agent"
4. Select these scopes:
   - `repo` (Full control of private repositories)
   - `read:org` (Read organization data)
   - `read:user` (Read user data)
5. Copy the token and replace `your_github_personal_access_token_here` in your `.env` file

### **3. Install Dependencies**

```bash
# Activate virtual environment
source venv/bin/activate

# Install PyGithub (if not already installed)
pip install PyGithub==1.59.1
```

## 🎯 **How to Use the Interactive Agent**

### **Start the Interactive Agent**

```bash
# Start interactive mode
python interactive_github_agent.py

# Or with specific repository
python interactive_github_agent.py --repo your-repo-name

# Or comment on specific PR
python interactive_github_agent.py --repo your-repo --pr 123
```

### **Available Commands**

Once the agent is running, you can use these commands:

#### **📋 Repository Management**
```bash
list-repos                    # List all your repositories
select-repo <repo_name>       # Select a repository to work with
status                        # Show current status
```

#### **🌿 Branch Management**
```bash
list-branches                 # List all branches in current repository
```

#### **🔀 Pull Request Management**
```bash
list-prs [open|closed|all]    # List pull requests (default: open)
pr-details <pr_number>        # Get detailed PR information
pr-files <pr_number>          # List files changed in a PR
```

#### **💬 AI Code Review**
```bash
comment-pr <pr_number>        # Analyze entire PR and post AI comments
comment-file <pr_number> <file> # Comment on specific file in PR
```

#### **🛠️ Utility**
```bash
help                          # Show help message
exit, quit                    # Exit the application
```

## 📊 **Example Usage**

### **1. List Your Repositories**
```bash
🤖 GitHub Agent > list-repos
```

### **2. Select a Repository**
```bash
🤖 GitHub Agent > select-repo my-awesome-project
```

### **3. List Open Pull Requests**
```bash
🤖 GitHub Agent > list-prs
```

### **4. Get PR Details**
```bash
🤖 GitHub Agent > pr-details 123
```

### **5. Analyze and Comment on a PR**
```bash
🤖 GitHub Agent > comment-pr 123
```

### **6. Comment on Specific File**
```bash
🤖 GitHub Agent > comment-file 123 src/main.py
```

## 🔍 **What the AI Analyzes**

The interactive agent provides **senior developer-level feedback** on:

### **🚨 Security Issues**
- `eval()` function usage
- Hardcoded credentials
- SQL injection risks
- Input validation problems

### **⚡ Performance Issues**
- Inefficient loops
- Missing optimizations
- Memory usage problems
- Algorithm improvements

### **🔧 Code Quality**
- Magic numbers
- Unused variables
- Poor error handling
- Code style issues

### **📝 Best Practices**
- Type hints
- Documentation
- Naming conventions
- Structure improvements

## 📱 **Example AI Comments**

The agent posts comments like this on GitHub:

```
🚨 **Security** 🔴

**CRITICAL SECURITY ISSUE**: Using `eval()` is extremely dangerous and should never be used with user input. This opens your application to code injection attacks.

**Recommendation**: Replace with `ast.literal_eval()` for safe evaluation of literals, or use `json.loads()` for JSON data.

```python
# Instead of: result = eval(user_input)
# Use: result = ast.literal_eval(user_input)  # for literals
# Or: result = json.loads(user_input)  # for JSON
```

*File: src/main.py*
```

## 🚀 **Quick Start Examples**

### **Example 1: Quick PR Review**
```bash
# Start agent and select repo
python interactive_github_agent.py --repo my-project

# In the interactive session:
🤖 GitHub Agent > list-prs
🤖 GitHub Agent > comment-pr 5
```

### **Example 2: Review Specific File**
```bash
# Comment on specific file in PR
🤖 GitHub Agent > comment-file 5 src/utils.py
```

### **Example 3: Check Repository Status**
```bash
🤖 GitHub Agent > status
🤖 GitHub Agent > list-branches
🤖 GitHub Agent > pr-details 10
```

## 🔧 **Troubleshooting**

### **"GITHUB_TOKEN not found" Error**
- Make sure you created the `.env` file
- Verify the token is correctly copied
- Check that the token has the right permissions

### **"Repository not found" Error**
- Make sure you have access to the repository
- Try using the full repository name (owner/repo)
- Check your GitHub token permissions

### **"Failed to post comment" Error**
- Verify you have write access to the repository
- Check that the PR exists and is open
- Ensure your token has `repo` scope

## 🎉 **Features**

✅ **Interactive CLI** - Easy-to-use command interface  
✅ **Repository Management** - List and select repositories  
✅ **PR Analysis** - View PR details and changed files  
✅ **AI Code Review** - Automatic analysis and commenting  
✅ **File-Specific Comments** - Target specific files in PRs  
✅ **Real GitHub Integration** - Posts actual comments on GitHub  
✅ **Senior Developer Feedback** - High-quality, actionable suggestions  

## 🚀 **Ready to Start!**

1. Create your `.env` file with GitHub token
2. Run: `python interactive_github_agent.py`
3. Start exploring your repositories!

**Your interactive GitHub AI agent is ready to revolutionize your code review workflow! 🎯** 