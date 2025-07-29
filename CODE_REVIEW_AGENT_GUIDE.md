# Automated Code Review Agent Guide

## Overview
The Automated Code Review Agent is a powerful tool that automatically analyzes pull requests and generates detailed review reports with accessible links. It integrates with your existing GitHub pull request workflow and provides comprehensive code analysis.

## Features

### 🔍 **Comprehensive Code Analysis**
- **Security Analysis**: Detects SQL injection, XSS vulnerabilities, hardcoded credentials
- **Performance Analysis**: Identifies N+1 queries, infinite loops, memory leaks
- **Code Style Analysis**: Checks for long functions, magic numbers, naming conventions
- **Bug Detection**: Finds potential bugs like division by zero, unused imports

### 📊 **Detailed Reports**
- **HTML Reports**: Beautiful, interactive reports with color-coded findings
- **JSON Reports**: Machine-readable reports for integration
- **Scoring System**: 0-100 score based on code quality
- **Actionable Recommendations**: Specific suggestions for improvement

### 🔗 **Accessible Links**
- **Local File URLs**: Reports saved as local HTML files
- **Browser Integration**: One-click report opening
- **Review History**: Track all previous reviews
- **GitHub Integration**: Posts review comments directly to PRs

## Quick Start

### 1. **Start the MCP Bridge Server**
```bash
# Terminal 1: Start the MCP bridge server
GITHUB_TOKEN="your_token" GITHUB_OWNER="your_username" GITHUB_REPO="your_repo" python3 simple_mcp_bridge.py
```

### 2. **Test the Code Review Agent**
```bash
# Terminal 2: Test the functionality
python3 test_code_review_agent.py
```

### 3. **Review a Pull Request**
```bash
# Terminal 2: Review a specific PR
python3 test_code_review_agent.py real
```

## API Commands

### **Automated Code Review**
```bash
curl -X POST http://127.0.0.1:5000/call \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "automated_code_review",
    "arguments": {
      "pr_number": 1
    }
  }'
```

**Response:**
```json
{
  "success": true,
  "review_id": "review_abc12345",
  "pr_number": 1,
  "overall_score": 85.0,
  "findings_count": 3,
  "status": "approved",
  "report_url": "file:///path/to/review_abc12345.html",
  "summary": "Code review completed with minor suggestions",
  "recommendations": ["Add more comments", "Consider error handling"]
}
```

### **List All Reviews**
```bash
curl -X POST http://127.0.0.1:5000/call \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "list_code_reviews",
    "arguments": {}
  }'
```

### **Get Specific Review Report**
```bash
curl -X POST http://127.0.0.1:5000/call \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "get_code_review_report",
    "arguments": {
      "review_id": "review_abc12345"
    }
  }'
```

### **Open Review Report in Browser**
```bash
curl -X POST http://127.0.0.1:5000/call \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "open_review_report",
    "arguments": {
      "review_id": "review_abc12345"
    }
  }'
```

## Workflow Integration

### **Complete PR Workflow**
1. **Create Pull Request** → `create_pull_request`
2. **Automated Review** → `automated_code_review`
3. **Review Report** → `open_review_report`
4. **Address Issues** → Fix code based on findings
5. **Merge PR** → `merge_pull_request`

### **Example Workflow Script**
```bash
#!/bin/bash

# Create a pull request
PR_RESPONSE=$(curl -s -X POST http://127.0.0.1:5000/call \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "create_pull_request",
    "arguments": {
      "title": "Add new feature",
      "description": "Implements new functionality",
      "source_branch": "feature-branch",
      "target_branch": "main"
    }
  }')

# Extract PR number
PR_NUMBER=$(echo $PR_RESPONSE | jq -r '.pr_id')

# Perform automated code review
REVIEW_RESPONSE=$(curl -s -X POST http://127.0.0.1:5000/call \
  -H "Content-Type: application/json" \
  -d "{
    \"tool\": \"automated_code_review\",
    \"arguments\": {
      \"pr_number\": $PR_NUMBER
    }
  }")

# Extract review ID and open report
REVIEW_ID=$(echo $REVIEW_RESPONSE | jq -r '.review_id')
REPORT_URL=$(echo $REVIEW_RESPONSE | jq -r '.report_url')

echo "🔍 Code review completed for PR #$PR_NUMBER"
echo "📄 Report available at: $REPORT_URL"

# Open report in browser
curl -s -X POST http://127.0.0.1:5000/call \
  -H "Content-Type: application/json" \
  -d "{
    \"tool\": \"open_review_report\",
    \"arguments\": {
      \"review_id\": \"$REVIEW_ID\"
    }
  }"
```

## Report Structure

### **HTML Report Features**
- **Header**: PR number, repository, overall score, status
- **Summary**: Total findings by severity level
- **Recommendations**: Actionable improvement suggestions
- **Findings**: Detailed list of issues with:
  - Severity level (Critical, High, Medium, Low)
  - Issue type (Security, Performance, Style, Bug)
  - File location and line numbers
  - Code snippets for context
  - Specific suggestions for fixes
- **Links**: Direct link to GitHub PR

### **Report Scoring**
- **100/100**: No issues found
- **90-99**: Minor style suggestions
- **80-89**: Some performance considerations
- **70-79**: Security or bug concerns
- **<70**: Critical issues requiring attention

## Configuration

### **Environment Variables**
```bash
export GITHUB_TOKEN="your_github_token"
export GITHUB_OWNER="your_username"
export GITHUB_REPO="your_repository"
```

### **Report Storage**
- **Location**: `./review_reports/`
- **Files**: `{review_id}.json` and `{review_id}.html`
- **Access**: Local file URLs for browser viewing

## Advanced Usage

### **Custom Analysis Rules**
The code review agent can be extended with custom analysis rules:

```python
# Add custom security checks
def _custom_security_check(self, content: str, file_path: str) -> List[ReviewFinding]:
    findings = []
    # Add your custom security analysis logic
    return findings
```

### **Integration with CI/CD**
```yaml
# GitHub Actions example
- name: Automated Code Review
  run: |
    curl -X POST http://127.0.0.1:5000/call \
      -H "Content-Type: application/json" \
      -d '{
        "tool": "automated_code_review",
        "arguments": {
          "pr_number": ${{ github.event.pull_request.number }}
        }
      }'
```

### **Webhook Integration**
```python
# Flask webhook handler
@app.route('/webhook/pr', methods=['POST'])
def pr_webhook():
    data = request.json
    if data['action'] == 'opened':
        pr_number = data['pull_request']['number']
        # Trigger automated review
        review_pr(pr_number)
    return 'OK'
```

## Troubleshooting

### **Common Issues**

1. **Agent Not Loading**
   ```
   ❌ Code review agent not available
   ```
   **Solution**: Ensure `code_review_agent.py` is in the same directory

2. **GitHub API Errors**
   ```
   ❌ Failed to fetch PR details
   ```
   **Solution**: Check GitHub token permissions and repository access

3. **Report Not Opening**
   ```
   ❌ Failed to open review report
   ```
   **Solution**: Check if the report file exists in `./review_reports/`

### **Debug Mode**
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python3 simple_mcp_bridge.py
```

## Best Practices

### **Review Workflow**
1. **Always review before merging** - Use automated reviews for every PR
2. **Address critical issues first** - Fix security and high-priority bugs
3. **Use reports for documentation** - Keep review reports for reference
4. **Integrate with team workflow** - Share report URLs with team members

### **Code Quality**
1. **Regular reviews** - Review code frequently, not just before merge
2. **Learn from findings** - Use suggestions to improve coding practices
3. **Customize rules** - Adapt analysis rules to your project needs
4. **Monitor trends** - Track review scores over time

## Support

### **Getting Help**
- Check the logs for detailed error messages
- Verify GitHub token permissions
- Ensure all required files are present
- Test with the provided test scripts

### **Extending Functionality**
- Add new analysis rules to `code_review_agent.py`
- Customize report templates
- Integrate with additional tools
- Add new review types

---

**🎉 You now have a powerful automated code review system that integrates seamlessly with your GitHub workflow!**