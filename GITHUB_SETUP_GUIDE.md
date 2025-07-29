# GitHub Setup Guide for Real Pull Requests

## Overview
This guide will help you set up GitHub integration to create real pull requests on your repository using the agentic RAG system.

## Prerequisites

### 1. GitHub Account
- You need a GitHub account with access to the repository where you want to create pull requests
- The repository must exist and you must have write access

### 2. GitHub Personal Access Token
You need to create a GitHub Personal Access Token with the following permissions:

#### Required Permissions:
- **`repo`** - Full control of private repositories
- **`public_repo`** - Access public repositories (if your repo is public)

#### Optional Permissions:
- **`workflow`** - Update GitHub Action workflows
- **`write:packages`** - Upload packages to GitHub Package Registry

## Step-by-Step Setup

### Step 1: Create GitHub Personal Access Token

1. **Go to GitHub Settings**
   - Visit [GitHub Settings](https://github.com/settings)
   - Click on "Developer settings" in the left sidebar
   - Click on "Personal access tokens"
   - Click on "Tokens (classic)"

2. **Generate New Token**
   - Click "Generate new token (classic)"
   - Give it a descriptive name like "Agentic RAG Pull Request Agent"
   - Set expiration (recommend 90 days for security)

3. **Select Permissions**
   - Check "repo" (Full control of private repositories)
   - If your repository is public, also check "public_repo"
   - Click "Generate token"

4. **Copy the Token**
   - **IMPORTANT**: Copy the token immediately - you won't see it again!
   - Store it securely (we'll use it in the next step)

### Step 2: Configure Environment Variables

You have three options to configure your GitHub credentials:

#### Option A: Environment Variables (Recommended)
Set these environment variables in your shell:

```bash
export GITHUB_TOKEN="your_github_token_here"
export GITHUB_OWNER="your_github_username_or_org"
export GITHUB_REPO="your_repository_name"
```

#### Option B: .env File
Create a `.env` file in your project root:

```bash
GITHUB_TOKEN=your_github_token_here
GITHUB_OWNER=your_github_username_or_org
GITHUB_REPO=your_repository_name
```

#### Option C: Interactive Setup
The script will prompt you for credentials if environment variables are not set.

### Step 3: Test the Setup

Run the test script to verify your configuration:

```bash
python3 real_github_pull_request.py
```

This will:
- Test your GitHub connection
- List existing pull requests
- Verify your permissions

### Step 4: Create Your First Real Pull Request

Use the interactive script to create a pull request:

```bash
python3 create_real_pull_request.py
```

## Repository Requirements

### Branch Setup
Before creating pull requests, ensure you have:

1. **Main Branch**: Usually `main` or `master`
2. **Feature Branch**: A branch with your changes
3. **Branch Protection**: Optional but recommended

### Example Git Workflow
```bash
# Clone your repository
git clone https://github.com/your-username/your-repo.git
cd your-repo

# Create a feature branch
git checkout -b feature/new-feature

# Make your changes
echo "# New Feature" >> README.md
git add README.md
git commit -m "Add new feature"

# Push the branch
git push origin feature/new-feature

# Now you can create a pull request using the script
python3 create_real_pull_request.py
```

## Usage Examples

### 1. Quick Pull Request Creation
```bash
# Set environment variables
export GITHUB_TOKEN="ghp_your_token_here"
export GITHUB_OWNER="your-username"
export GITHUB_REPO="your-repo"

# Run the script
python3 create_real_pull_request.py
```

### 2. Programmatic Pull Request Creation
```python
from real_github_pull_request import RealGitHubPullRequest, GitHubConfig

# Create config
config = GitHubConfig(
    token="your_token",
    owner="your_username", 
    repo="your_repo"
)

# Create client
github_pr = RealGitHubPullRequest(config)

# Create pull request
result = github_pr.create_pull_request(
    title="Add new feature",
    description="This PR adds a new feature to the application",
    source_branch="feature/new-feature",
    target_branch="main"
)

if result.get("success"):
    print(f"✅ PR created: {result['url']}")
else:
    print(f"❌ Failed: {result.get('error')}")
```

### 3. List Pull Requests
```python
# List open pull requests
result = github_pr.list_pull_requests(state="open", limit=10)

if result.get("success"):
    for pr in result['pull_requests']:
        print(f"#{pr['pr_number']}: {pr['title']}")
```

### 4. Review Pull Request
```python
# Review a pull request
result = github_pr.review_pull_request(
    pr_number=123,
    review_type="approve",
    comments=["Great work!", "Ready to merge"],
    reviewer="Code Reviewer"
)
```

## Security Best Practices

### 1. Token Security
- **Never commit tokens to version control**
- Use environment variables or secure secret management
- Rotate tokens regularly (every 90 days)
- Use the minimum required permissions

### 2. Repository Security
- Enable branch protection rules
- Require pull request reviews
- Use status checks for automated testing
- Restrict who can merge pull requests

### 3. Access Control
- Use organization-level access tokens when possible
- Limit token scope to specific repositories
- Monitor token usage in GitHub settings

## Troubleshooting

### Common Issues

#### 1. "Bad credentials" Error
```
❌ Failed to create pull request: 401 - Bad credentials
```
**Solution**: Check your GitHub token is valid and has the correct permissions

#### 2. "Repository not found" Error
```
❌ Failed to create pull request: 404 - Not Found
```
**Solution**: Verify the repository name and owner are correct

#### 3. "Branch not found" Error
```
❌ Failed to create pull request: 422 - Validation failed
```
**Solution**: Ensure the source branch exists and is pushed to GitHub

#### 4. "Permission denied" Error
```
❌ Failed to create pull request: 403 - Forbidden
```
**Solution**: Check you have write access to the repository

### Debug Mode
Enable debug logging to see detailed API requests:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Integration with MCP Bridge

To integrate real GitHub pull requests with your MCP bridge:

1. **Update the MCP bridge** to use the real GitHub implementation
2. **Replace simulated functions** with actual API calls
3. **Add error handling** for network issues and API limits
4. **Implement rate limiting** to respect GitHub API limits

### Example MCP Bridge Integration
```python
# In simple_mcp_bridge.py
from real_github_pull_request import RealGitHubPullRequest, GitHubConfig

class SimpleMCPBridge:
    def __init__(self):
        # Initialize GitHub client
        config = GitHubConfig(
            token=os.getenv('GITHUB_TOKEN'),
            owner=os.getenv('GITHUB_OWNER'),
            repo=os.getenv('GITHUB_REPO')
        )
        self.github_pr = RealGitHubPullRequest(config)
    
    def _create_pull_request(self, arguments: dict) -> dict:
        """Create a real pull request on GitHub."""
        return self.github_pr.create_pull_request(
            title=arguments.get("title"),
            description=arguments.get("description"),
            source_branch=arguments.get("source_branch"),
            target_branch=arguments.get("target_branch")
        )
```

## Next Steps

1. **Test the setup** with a simple pull request
2. **Integrate with your workflow** using the MCP bridge
3. **Add automation** for common pull request tasks
4. **Implement webhooks** for real-time updates
5. **Add advanced features** like automated reviews and CI/CD integration

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Verify your GitHub token permissions
3. Test with the GitHub API directly
4. Review GitHub's API documentation
5. Check the repository access and branch setup