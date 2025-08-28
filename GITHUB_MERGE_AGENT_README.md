# GitHub Merge Agent

A powerful agent that automatically merges reviewed pull requests on GitHub. This agent integrates with your existing RAG system and provides intelligent, safe merging of pull requests that meet all requirements.

## Features

- **Smart Merge Eligibility Checking**: Automatically analyzes PRs for reviews, status checks, and branch protection rules
- **Safe Auto-Merging**: Only merges PRs that meet all criteria
- **Comprehensive PR Analysis**: Detailed information about PR status, reviews, and mergeability
- **Flexible Configuration**: Support for different merge methods and custom commit messages
- **Label-Based Filtering**: Optional filtering by labels for controlled auto-merging
- **Integration Ready**: Works with your existing agent system and provides CLI tools

## Installation

1. **Install Dependencies**:
   ```bash
   pip install PyGithub python-dotenv
   ```

2. **Set Environment Variables**:
   ```bash
   export GITHUB_TOKEN="your_github_personal_access_token"
   export GITHUB_REPO="owner/repository_name"
   ```

   Or create a `.env` file:
   ```env
   GITHUB_TOKEN=your_github_personal_access_token
   GITHUB_REPO=owner/repository_name
   ```

3. **GitHub Token Permissions**:
   Your GitHub Personal Access Token needs these permissions:
   - `repo` (Full control of private repositories)
   - `read:org` (Read organization data)
   - `read:user` (Read user data)

## Usage

### CLI Interface

The agent provides a comprehensive CLI for testing and direct usage:

```bash
# List open pull requests
python github_merge_cli.py --action list --limit 10

# Get details for a specific PR
python github_merge_cli.py --action details --pr-number 123

# Check merge eligibility
python github_merge_cli.py --action check --pr-number 123

# Merge a PR (if eligible)
python github_merge_cli.py --action merge --pr-number 123 --merge-method squash

# Auto-merge all eligible PRs
python github_merge_cli.py --action auto-merge

# Auto-merge only PRs with a specific label
python github_merge_cli.py --action auto-merge --auto-merge-label "ready-to-merge"
```

### Python API

```python
from agent.github_merge_agent import GitHubMergeAgent

# Initialize the agent
agent = GitHubMergeAgent(
    token="your_token",
    repo_name="owner/repo"
)

# List pull requests
prs = agent.list_pull_requests(state="open", limit=20)

# Check merge eligibility
eligibility = agent.check_merge_eligibility(pr_number=123)

# Merge a PR
result = agent.merge_pull_request(
    pr_number=123,
    merge_method="squash",
    commit_title="Custom commit title"
)

# Auto-merge all eligible PRs
auto_merge_result = agent.auto_merge_eligible_prs()
```

### Integration with Main Agent

The GitHub merge tools are automatically available in your main agent system:

```python
# These tools are now available in your agent:
# - list_github_pull_requests
# - get_github_pr_details  
# - check_github_pr_merge_eligibility
# - merge_github_pr
# - auto_merge_github_prs
```

## How It Works

### Merge Eligibility Criteria

The agent checks these criteria before merging:

1. **PR State**: Must be open and not in draft
2. **Reviews**: Must have at least one approval
3. **Status Checks**: All required status checks must pass
4. **Branch Protection**: Must meet branch protection requirements
5. **Mergeability**: GitHub must mark the PR as mergeable

### Safety Features

- **Pre-Merge Validation**: Always checks eligibility before attempting to merge
- **Error Handling**: Comprehensive error handling and logging
- **Dry Run Capability**: Can check eligibility without actually merging
- **Label Filtering**: Optional label-based filtering for controlled auto-merging

### Merge Methods

Supports all GitHub merge methods:
- **merge**: Creates a merge commit
- **squash**: Squashes all commits into one
- **rebase**: Replays commits on top of the base branch

## Configuration

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `GITHUB_TOKEN` | GitHub Personal Access Token | `ghp_abc123...` |
| `GITHUB_REPO` | Repository name | `owner/repository` |

### Repository Setup

For optimal functionality, ensure your repository has:

1. **Branch Protection Rules**: Set up on main/master branch
2. **Required Status Checks**: Configure CI/CD checks
3. **Required Reviews**: Set minimum number of approvals
4. **Labels**: Optional labels for controlled auto-merging

## Testing

Run the test suite to verify everything works:

```bash
python test_github_merge_agent.py
```

This will test:
- Agent initialization
- PR listing
- Merge eligibility checking
- PR details retrieval
- Auto-merge functionality

## Examples

### Basic Auto-Merge Workflow

```python
from agent.github_merge_agent import GitHubMergeAgent

# Initialize agent
agent = GitHubMergeAgent()

# Check all open PRs and merge eligible ones
result = agent.auto_merge_eligible_prs()

print(f"Processed {result['total_prs_checked']} PRs")
print(f"Successfully merged: {result['successful_merges']}")
print(f"Failed merges: {result['failed_merges']}")
```

### Selective Merging with Labels

```python
# Only merge PRs with "ready-to-merge" label
result = agent.auto_merge_eligible_prs(auto_merge_label="ready-to-merge")
```

### Custom Merge Messages

```python
# Merge with custom commit message
result = agent.merge_pull_request(
    pr_number=123,
    merge_method="squash",
    commit_title="Feature: Add new functionality",
    commit_message="Implements user-requested feature with comprehensive testing"
)
```

## Troubleshooting

### Common Issues

1. **Authentication Errors**:
   - Verify your GitHub token is valid and has correct permissions
   - Check that the token hasn't expired

2. **Repository Access**:
   - Ensure the token has access to the specified repository
   - Check repository visibility (public/private)

3. **Branch Protection**:
   - Some repositories have strict branch protection rules
   - The agent respects these rules and won't override them

4. **Rate Limiting**:
   - GitHub API has rate limits
   - The agent handles rate limiting gracefully

### Debug Mode

Enable debug logging to see detailed information:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Security Considerations

- **Token Security**: Never commit your GitHub token to version control
- **Repository Access**: Use tokens with minimal required permissions
- **Auto-Merge Safety**: The agent only merges PRs that meet all safety criteria
- **Audit Trail**: All merge actions are logged and traceable

## Contributing

To extend the GitHub merge agent:

1. **Add New Tools**: Extend the `GitHubMergeAgent` class
2. **Integrate with Main Agent**: Add new tools to `agent.py`
3. **Update CLI**: Add new actions to `github_merge_cli.py`
4. **Add Tests**: Include tests in `test_github_merge_agent.py`

## License

This project is part of your RAG system and follows the same licensing terms.

---

**Note**: This agent is designed for production use but should be tested thoroughly in your specific environment before deploying to critical repositories. 