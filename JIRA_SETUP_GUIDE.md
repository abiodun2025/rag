# 🔐 Jira Account Access Setup Guide

## Overview

This guide explains how the Jira Agent securely accesses your Jira account and what you need to configure.

## 🔑 **Authentication Methods**

### **✅ Method 1: API Token (Recommended)**

#### **For Jira Cloud:**
1. **Go to [Atlassian Account Settings](https://id.atlassian.com/manage-profile/security/api-tokens)**
2. **Click "Create API token"**
3. **Give it a descriptive label** (e.g., "Task/Project Agent - Jira Integration")
4. **Copy the generated token** (starts with `ATATT...`)
5. **Store it securely** - you won't see it again!

#### **For Jira Server:**
1. **Log into your Jira instance**
2. **Go to Profile → Personal Access Tokens**
3. **Click "Create token"**
4. **Set appropriate expiration** (90 days recommended)
5. **Copy the generated token**

### **✅ Method 2: Username + Password (Less Secure)**
- **Direct username/password** authentication
- **Not recommended** for production use
- **May require 2FA bypass** configuration
- **Higher security risk** if credentials are compromised

## 🛠️ **Configuration Setup**

### **Step 1: Copy Configuration Template**
```bash
cp jira_config_template.json jira_config.json
```

### **Step 2: Edit with Your Real Credentials**
```json
{
  "jira": {
    "base_url": "https://your-company.atlassian.net",
    "username": "your-email@company.com",
    "api_token": "ATATT3xFfGF0...your-actual-token...",
    "project_key": "PROJ",
    "verify_ssl": true,
    "timeout": 30,
    "max_results": 100
  }
}
```

### **Step 3: Required Information**

| Field | Description | Example | Required |
|-------|-------------|---------|----------|
| `base_url` | Your Jira instance URL | `https://company.atlassian.net` | ✅ Yes |
| `username` | Your Jira email address | `developer@company.com` | ✅ Yes |
| `api_token` | Your API token | `ATATT3xFfGF0...` | ✅ Yes |
| `project_key` | Your project key | `PROJ`, `DEV`, `TEST` | ✅ Yes |
| `verify_ssl` | SSL certificate verification | `true` | ⚠️ Optional |
| `timeout` | API request timeout (seconds) | `30` | ⚠️ Optional |
| `max_results` | Max issues per request | `100` | ⚠️ Optional |

## 🔒 **Security Best Practices**

### **✅ API Token Security:**
- **Never commit** `jira_config.json` to version control
- **Add to `.gitignore`** to prevent accidental commits
- **Use environment variables** for production deployments
- **Rotate tokens regularly** (every 90 days recommended)
- **Limit token permissions** to minimum required access
- **Monitor token usage** for unusual activity

### **✅ Network Security:**
- **Use HTTPS** for all connections (never HTTP)
- **Verify SSL certificates** in production environments
- **Use VPN** if accessing internal/on-premise Jira instances
- **Monitor API usage** for unusual patterns
- **Implement rate limiting** if needed

### **✅ Access Control:**
- **Use dedicated service account** for automation (recommended)
- **Limit project access** to only necessary projects
- **Review permissions** regularly
- **Use least privilege principle**

## 🧪 **Testing Your Connection**

### **Step 1: Test Basic Connection**
```bash
python3 test_jira_connection.py
```

**Expected Output:**
```
🔗 Testing Jira Connection
==================================================
✅ Configuration loaded successfully
   🌐 Base URL: https://your-company.atlassian.net
   👤 Username: your-email@company.com
   🔑 API Token: ATATT3xFfG...
   🔑 Project Key: PROJ

🔗 Testing connection to Jira...
✅ Connected to Jira successfully!
   👤 User: John Developer
   📧 Email: john@company.com
   🆔 Account ID: 123456:abcdef...

📋 Testing project access...
✅ Project access successful!
   🔑 Project Key: PROJ
   📝 Project Name: My Project
   👥 Project Lead: John Developer
   🏷️  Category: Software Development

🎉 All tests passed! Your Jira Agent is ready to use.
```

### **Step 2: Test Notification Agent**
```bash
python3 test_jira_notification_agent.py
```

### **Step 3: Test Integration Examples**
```bash
python3 jira_email_integration_examples.py
```

## 🚨 **Troubleshooting Common Issues**

### **❌ Connection Failed - HTTP 401**
```
❌ Connection failed: HTTP 401
```
**Solutions:**
- Check your username/email is correct
- Verify your API token is valid and not expired
- Ensure your account has access to Jira
- Check if your account is active

### **❌ Connection Failed - HTTP 403**
```
❌ Connection failed: HTTP 403
```
**Solutions:**
- Verify your account has permission to access the project
- Check if the project is private and you have access
- Ensure your API token has sufficient permissions
- Contact your Jira administrator

### **❌ Connection Failed - HTTP 404**
```
❌ Connection failed: HTTP 404
```
**Solutions:**
- Check your Jira URL is correct
- Verify the project key exists
- Ensure you're using the right Jira instance
- Check if the project has been deleted or renamed

### **❌ SSL Certificate Verification Failed**
```
❌ SSL certificate verification failed
```
**Solutions:**
- Set `"verify_ssl": false` in your config (for testing only)
- Check if your Jira instance uses self-signed certificates
- Verify your system's CA certificates are up to date
- Use proper SSL certificates in production

### **❌ Network Connection Issues**
```
❌ Network connection issues
```
**Solutions:**
- Check your internet connection
- Verify firewall settings allow outbound HTTPS
- Check if VPN is required for Jira access
- Test connectivity to the Jira URL from your machine

## 🔧 **Advanced Configuration**

### **Environment Variables (Production)**
```bash
# Set environment variables instead of config file
export JIRA_BASE_URL="https://your-company.atlassian.net"
export JIRA_USERNAME="your-email@company.com"
export JIRA_API_TOKEN="your-api-token"
export JIRA_PROJECT_KEY="PROJ"
```

### **Multiple Jira Instances**
```json
{
  "jira_instances": {
    "production": {
      "base_url": "https://prod.company.atlassian.net",
      "username": "prod-user@company.com",
      "api_token": "prod-token",
      "project_key": "PROD"
    },
    "staging": {
      "base_url": "https://staging.company.atlassian.net",
      "username": "staging-user@company.com",
      "api_token": "staging-token",
      "project_key": "STAGE"
    }
  }
}
```

### **Custom Escalation Rules**
```json
{
  "escalation_rules": [
    {
      "name": "Critical Bug Escalation",
      "condition": "P1 bug open > 48 hours",
      "threshold_hours": 48,
      "escalation_level": "critical",
      "notify_emails": ["engineering-manager@company.com", "cto@company.com"]
    },
    {
      "name": "Unassigned Ticket Alert",
      "condition": "Critical ticket unassigned > 24 hours",
      "threshold_hours": 24,
      "escalation_level": "high",
      "notify_emails": ["pm@company.com", "tech-lead@company.com"]
    }
  ]
}
```

## 📊 **Monitoring and Maintenance**

### **✅ Regular Tasks:**
- **Monitor API usage** and rate limits
- **Check token expiration** and rotate as needed
- **Review access permissions** quarterly
- **Update SSL certificates** when needed
- **Monitor for unusual activity**

### **✅ Health Checks:**
```python
# Run health check
health = await jira_agent.health_check()
print(f"Status: {health['status']}")
print(f"Last Check: {health['timestamp']}")
```

## 🎯 **Next Steps After Setup**

1. **✅ Test your connection** with `test_jira_connection.py`
2. **✅ Verify project access** and permissions
3. **✅ Test notification agent** with `test_jira_notification_agent.py`
4. **✅ Run integration examples** with `jira_email_integration_examples.py`
5. **✅ Configure escalation rules** for your projects
6. **✅ Set up daily digest** recipients and timing
7. **✅ Monitor and adjust** based on usage

## 🔗 **Support and Resources**

### **Jira API Documentation:**
- [Jira Cloud REST API](https://developer.atlassian.com/cloud/jira/platform/rest/v3/)
- [Jira Server REST API](https://docs.atlassian.com/software/jira/docs/api/REST/9.0.0/)

### **Atlassian Support:**
- [Atlassian Community](https://community.atlassian.com/)
- [Atlassian Support](https://support.atlassian.com/)

### **Security Resources:**
- [Atlassian Security](https://www.atlassian.com/trust/security)
- [API Token Best Practices](https://developer.atlassian.com/cloud/jira/platform/rest/v3/intro/#authentication)

---

## 🎉 **You're Ready!**

Once you've completed this setup:
- ✅ **Your Jira Agent has secure access** to your Jira instance
- ✅ **Real-time project management** is fully operational
- ✅ **Automated notifications and escalations** are configured
- ✅ **Daily digests and monitoring** are active

**🚀 Start managing your Jira projects in real-time with the Task/Project Agent!**
