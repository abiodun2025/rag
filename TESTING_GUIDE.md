# 🧪 Testing Guide for All Branches

## Quick Start

1. **Setup Environment**:
   ```bash
   python setup_testing_environment.py
   ```

2. **Start MCP Server**:
   ```bash
   python simple_mcp_server.py &
   ```

3. **Run Comprehensive Tests**:
   ```bash
   python test_all_branches_comprehensive.py
   ```

4. **Diagnose Email Issues**:
   ```bash
   python diagnose_email_body_issue.py
   ```

## Environment Variables

Set these in your shell or .env file:
```bash
export GITHUB_TOKEN="your-github-token"
export GMAIL_USER="your-email@gmail.com"
export GMAIL_APP_PASSWORD="your-app-password"
```

## Common Issues

### MCP Server Not Running
- Start with: `python simple_mcp_server.py`
- Check port 5000 is available
- Verify server responds to health checks

### Email Body Issues
- Run: `python diagnose_email_body_issue.py`
- Check Gmail credentials
- Verify sendmail configuration

### Git Issues
- Configure git user: `git config --global user.name "Your Name"`
- Configure git email: `git config --global user.email "your-email@example.com"`

## Test Results

- Comprehensive results: `comprehensive_test_results.json`
- Test logs: `test_results.log`
- Coverage reports: `htmlcov/`

## Branch Testing

The comprehensive test script will:
1. Check all branches
2. Test each branch with commits
3. Run pytest with coverage
4. Run integration tests
5. Test branch-specific functionality
6. Generate detailed reports

## Troubleshooting

If tests fail:
1. Check prerequisites with diagnostic scripts
2. Verify environment variables
3. Ensure MCP server is running
4. Check git configuration
5. Review test logs for specific errors
