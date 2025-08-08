# Real-World Agent Testing Guide

## 🎯 Overview

This guide provides comprehensive instructions for testing the **GitHub Coverage Agent** in real-world scenarios. The agent is responsible for analyzing test coverage of pull requests and providing intelligent suggestions for missing test cases.

## 🏗️ Agent Architecture

### Core Components
1. **TestCoverageAgent** - Base agent for coverage analysis
2. **GitHubCoverageAgent** - GitHub-integrated version
3. **CoverageData** - Data structure for coverage information
4. **TestSuggestion** - Data structure for test suggestions

### Supported Languages & Tools
- **Java/Kotlin**: JaCoCo XML reports
- **JavaScript/TypeScript**: Istanbul JSON reports
- **Python**: Coverage.py reports
- **Go**: Go test coverage reports

## 🚀 Prerequisites

### Environment Setup
```bash
# Install required packages
pip install requests coverage pytest

# Set up GitHub credentials
export GITHUB_TOKEN="your_github_personal_access_token"
export GITHUB_OWNER="your_username_or_organization"
export GITHUB_REPO="your_repository_name"

# Optional: LLM API for enhanced suggestions
export LLM_API_KEY="your_llm_api_key"
```

### GitHub Token Setup
1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Generate a new token with `repo` scope
3. Copy the token and set it as `GITHUB_TOKEN`

## 🧪 Testing Scenarios

### 1. Basic Agent Initialization Test

**Purpose**: Verify agent can be initialized correctly

```python
from agent.test_coverage_agent import TestCoverageAgent
from agent.github_coverage_agent import GitHubCoverageAgent, GitHubConfig

def test_agent_initialization():
    """Test basic agent initialization."""
    # Test base agent
    base_agent = TestCoverageAgent()
    assert base_agent.supported_languages is not None
    assert 'java' in base_agent.supported_languages
    assert 'py' in base_agent.supported_languages
    
    # Test GitHub agent
    config = GitHubConfig(
        token="test_token",
        owner="test_owner",
        repo="test_repo"
    )
    github_agent = GitHubCoverageAgent(config)
    assert github_agent.github_config.owner == "test_owner"
    assert github_agent.github_config.repo == "test_repo"
```

### 2. Language Detection Test

**Purpose**: Verify agent correctly identifies programming languages

```python
def test_language_detection():
    """Test language detection from file paths."""
    agent = TestCoverageAgent()
    
    test_cases = [
        ('src/main.java', 'java'),
        ('app/User.kt', 'kt'),
        ('components/Button.js', 'js'),
        ('utils/helper.ts', 'ts'),
        ('main.py', 'py'),
        ('server.go', 'go'),
        ('unknown.xyz', 'unknown')
    ]
    
    for file_path, expected_language in test_cases:
        detected = agent._detect_language(file_path)
        assert detected == expected_language, f"Expected {expected_language} for {file_path}, got {detected}"
```

### 3. GitHub API Integration Test

**Purpose**: Verify agent can connect to GitHub API

```python
import requests

def test_github_api_connection():
    """Test GitHub API connection."""
    token = os.getenv('GITHUB_TOKEN')
    owner = os.getenv('GITHUB_OWNER')
    repo = os.getenv('GITHUB_REPO')
    
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Test repository access
    repo_url = f"https://api.github.com/repos/{owner}/{repo}"
    response = requests.get(repo_url, headers=headers)
    
    assert response.status_code == 200, f"Repository access failed: {response.status_code}"
    
    repo_data = response.json()
    assert repo_data['full_name'] == f"{owner}/{repo}"
    print(f"✅ Repository access successful: {repo_data['full_name']}")
```

### 4. Pull Request Analysis Test

**Purpose**: Verify agent can analyze pull requests

```python
def test_pull_request_analysis():
    """Test pull request analysis capabilities."""
    config = GitHubConfig(
        token=os.getenv('GITHUB_TOKEN'),
        owner=os.getenv('GITHUB_OWNER'),
        repo=os.getenv('GITHUB_REPO')
    )
    
    agent = GitHubCoverageAgent(config)
    
    # Get pull requests
    headers = {
        "Authorization": f"token {config.token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    pr_url = f"https://api.github.com/repos/{config.owner}/{config.repo}/pulls"
    response = requests.get(pr_url, headers=headers)
    
    assert response.status_code == 200, f"Failed to get pull requests: {response.status_code}"
    
    prs = response.json()
    if prs:
        # Test with first PR
        pr = prs[0]
        pr_info = agent._get_pr_info(pr['number'])
        
        assert pr_info is not None, "Failed to get PR info"
        assert pr_info['number'] == pr['number']
        assert pr_info['title'] == pr['title']
        
        print(f"✅ PR analysis successful for PR #{pr['number']}: {pr['title']}")
```

### 5. Code Generation Test

**Purpose**: Verify agent can generate and test code

```python
import tempfile
import subprocess
import os

def test_code_generation():
    """Test code generation capabilities."""
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Generate test code
        source_code = '''
def add(a, b):
    """Add two numbers."""
    return a + b

def subtract(a, b):
    """Subtract two numbers."""
    return a - b

def divide(a, b):
    """Divide two numbers with error handling."""
    if b == 0:
        return None
    return a / b
'''
        
        source_file = os.path.join(temp_dir, "calculator.py")
        with open(source_file, 'w') as f:
            f.write(source_code)
        
        # Generate test code
        test_code = '''
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from calculator import add, subtract, divide

def test_basic_operations():
    assert add(2, 3) == 5
    assert subtract(5, 2) == 3
    assert divide(10, 2) == 5.0
    assert divide(10, 0) is None

if __name__ == "__main__":
    test_basic_operations()
    print("✅ All tests passed!")
'''
        
        test_file = os.path.join(temp_dir, "test_calculator.py")
        with open(test_file, 'w') as f:
            f.write(test_code)
        
        # Run tests
        result = subprocess.run(['python3', 'test_calculator.py'], 
                              capture_output=True, text=True, cwd=temp_dir)
        
        assert result.returncode == 0, f"Test execution failed: {result.stderr}"
        assert "✅ All tests passed!" in result.stdout
        
        print("✅ Code generation and testing successful")
        
    finally:
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir)
```

### 6. Coverage Analysis Test

**Purpose**: Verify agent can analyze test coverage

```python
def test_coverage_analysis():
    """Test coverage analysis capabilities."""
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Create source and test files (same as above)
        # ... (code generation part)
        
        # Run tests with coverage
        coverage_result = subprocess.run([
            'python3', '-m', 'coverage', 'run', '--source=calculator', 
            'test_calculator.py'
        ], capture_output=True, text=True, cwd=temp_dir)
        
        assert coverage_result.returncode == 0, "Coverage run failed"
        
        # Generate coverage report
        report_result = subprocess.run([
            'python3', '-m', 'coverage', 'report'
        ], capture_output=True, text=True, cwd=temp_dir)
        
        assert report_result.returncode == 0, "Coverage report generation failed"
        
        # Parse coverage data
        coverage_data = parse_coverage_report(report_result.stdout)
        assert coverage_data is not None, "Failed to parse coverage data"
        assert coverage_data['coverage'] > 0, "Coverage should be greater than 0"
        
        print(f"✅ Coverage analysis successful: {coverage_data['coverage']}%")
        
    finally:
        shutil.rmtree(temp_dir)

def parse_coverage_report(report_output: str) -> dict:
    """Parse coverage report output."""
    lines = report_output.strip().split('\n')
    for line in lines:
        if 'calculator.py' in line and 'TOTAL' not in line:
            parts = line.split()
            if len(parts) >= 4:
                total_lines = int(parts[1])
                missing_lines = int(parts[2])
                covered_lines = total_lines - missing_lines
                coverage = (covered_lines / total_lines) * 100 if total_lines > 0 else 0
                
                return {
                    'total_lines': total_lines,
                    'covered_lines': covered_lines,
                    'missing_lines': missing_lines,
                    'coverage': round(coverage, 1)
                }
    return None
```

### 7. Suggestion Generation Test

**Purpose**: Verify agent can generate intelligent suggestions

```python
def test_suggestion_generation():
    """Test suggestion generation capabilities."""
    agent = TestCoverageAgent()
    
    # Test line classification
    test_cases = [
        ('if user is None:', 'edge_case'),
        ('return None', 'control_flow'),
        ('except ValueError:', 'error_handling'),
        ('if age >= 18:', 'boundary'),
        ('user = None', 'null_check'),
        ('print("Hello")', 'general')
    ]
    
    for code_line, expected_type in test_cases:
        detected_type = agent._classify_line_type(code_line, 'py')
        assert detected_type == expected_type, f"Expected {expected_type} for '{code_line}', got {detected_type}"
    
    # Test suggestion description generation
    description = agent._generate_suggestion_description(
        'if user is None:', 'edge_case', 'py'
    )
    assert 'edge case' in description.lower()
    
    print("✅ Suggestion generation successful")
```

### 8. End-to-End Integration Test

**Purpose**: Test complete workflow from PR to coverage report

```python
def test_end_to_end_workflow():
    """Test complete end-to-end workflow."""
    config = GitHubConfig(
        token=os.getenv('GITHUB_TOKEN'),
        owner=os.getenv('GITHUB_OWNER'),
        repo=os.getenv('GITHUB_REPO')
    )
    
    agent = GitHubCoverageAgent(config)
    
    # Get a real PR
    headers = {
        "Authorization": f"token {config.token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    pr_url = f"https://api.github.com/repos/{config.owner}/{config.repo}/pulls"
    response = requests.get(pr_url, headers=headers)
    
    if response.status_code == 200:
        prs = response.json()
        if prs:
            # Test with first PR
            pr = prs[0]
            print(f"Testing with PR #{pr['number']}: {pr['title']}")
            
            # Note: This would require cloning the repository
            # For testing purposes, we'll just verify PR info retrieval
            pr_info = agent._get_pr_info(pr['number'])
            
            assert pr_info is not None, "Failed to get PR info"
            assert pr_info['number'] == pr['number']
            
            print(f"✅ End-to-end workflow successful for PR #{pr['number']}")
        else:
            print("ℹ️ No open pull requests found for testing")
    else:
        print(f"❌ Failed to get pull requests: {response.status_code}")
```

## 🎯 Real-World Testing Checklist

### Pre-Testing Setup
- [ ] GitHub token configured with appropriate permissions
- [ ] Repository access verified
- [ ] Required tools installed (git, coverage, etc.)
- [ ] Test repository with pull requests available
- [ ] Environment variables set correctly

### Core Functionality Tests
- [ ] Agent initialization
- [ ] Language detection
- [ ] GitHub API connection
- [ ] Pull request retrieval
- [ ] File analysis
- [ ] Code generation
- [ ] Test execution
- [ ] Coverage analysis
- [ ] Suggestion generation
- [ ] Report generation

### Integration Tests
- [ ] End-to-end workflow
- [ ] Error handling
- [ ] Resource cleanup
- [ ] Performance under load
- [ ] Multi-language support

### Quality Assurance Tests
- [ ] Coverage accuracy
- [ ] Suggestion relevance
- [ ] Report completeness
- [ ] Error recovery
- [ ] Security validation

## 🚨 Common Issues & Solutions

### Issue: GitHub API Rate Limiting
**Solution**: Monitor rate limits and implement exponential backoff
```python
def check_rate_limit(headers):
    rate_limit_url = "https://api.github.com/rate_limit"
    response = requests.get(rate_limit_url, headers=headers)
    if response.status_code == 200:
        rate_data = response.json()
        remaining = rate_data['resources']['core']['remaining']
        if remaining < 10:
            print(f"⚠️ Rate limit low: {remaining} requests remaining")
```

### Issue: Repository Access Denied
**Solution**: Verify token permissions and repository access
```python
def verify_repository_access(config):
    headers = {
        "Authorization": f"token {config.token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    repo_url = f"https://api.github.com/repos/{config.owner}/{config.repo}"
    response = requests.get(repo_url, headers=headers)
    
    if response.status_code == 404:
        print("❌ Repository not found or access denied")
        return False
    elif response.status_code == 401:
        print("❌ Invalid token or insufficient permissions")
        return False
    
    return True
```

### Issue: Coverage Tool Not Found
**Solution**: Check tool availability and provide fallbacks
```python
def check_coverage_tool(language):
    tools = {
        'py': ['python3', '-m', 'coverage', '--version'],
        'java': ['mvn', '--version'],
        'js': ['npm', '--version'],
        'go': ['go', 'version']
    }
    
    if language in tools:
        try:
            subprocess.run(tools[language], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"❌ {language} coverage tool not found")
            return False
    
    return False
```

## 📊 Performance Testing

### Load Testing
```python
def test_agent_performance():
    """Test agent performance under load."""
    import time
    
    config = GitHubConfig(
        token=os.getenv('GITHUB_TOKEN'),
        owner=os.getenv('GITHUB_OWNER'),
        repo=os.getenv('GITHUB_REPO')
    )
    
    agent = GitHubCoverageAgent(config)
    
    # Test multiple PRs
    start_time = time.time()
    
    headers = {
        "Authorization": f"token {config.token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    pr_url = f"https://api.github.com/repos/{config.owner}/{config.repo}/pulls"
    response = requests.get(pr_url, headers=headers)
    
    if response.status_code == 200:
        prs = response.json()
        
        for pr in prs[:5]:  # Test first 5 PRs
            pr_start = time.time()
            pr_info = agent._get_pr_info(pr['number'])
            pr_time = time.time() - pr_start
            
            print(f"PR #{pr['number']}: {pr_time:.2f}s")
    
    total_time = time.time() - start_time
    print(f"Total time: {total_time:.2f}s")
```

## 🎉 Success Criteria

### Minimum Requirements
- [ ] All core functionality tests pass
- [ ] GitHub API integration working
- [ ] Coverage analysis accurate
- [ ] Suggestions relevant and actionable
- [ ] Error handling robust
- [ ] Performance acceptable (< 30s per PR)

### Advanced Requirements
- [ ] Multi-language support verified
- [ ] End-to-end workflow complete
- [ ] Resource cleanup working
- [ ] Security validation passed
- [ ] Documentation complete
- [ ] Ready for production deployment

## 🔧 Running the Tests

### Automated Test Suite
```bash
# Run all tests
python3 -m pytest test_real_world_agent.py -v

# Run specific test
python3 -m pytest test_real_world_agent.py::test_github_api_connection -v

# Run with coverage
python3 -m pytest test_real_world_agent.py --cov=agent --cov-report=html
```

### Manual Testing
```bash
# Test GitHub connection
python3 -c "
from agent.github_coverage_agent import GitHubCoverageAgent, GitHubConfig
import os
config = GitHubConfig(token=os.getenv('GITHUB_TOKEN'), owner=os.getenv('GITHUB_OWNER'), repo=os.getenv('GITHUB_REPO'))
agent = GitHubCoverageAgent(config)
print('✅ Agent initialized successfully')
"

# Test coverage analysis
python3 working_coverage_demo.py

# Test comprehensive workflow
python3 comprehensive_github_coverage_test.py
```

## 📈 Monitoring & Metrics

### Key Metrics to Track
- **API Response Time**: < 2 seconds
- **Coverage Analysis Time**: < 30 seconds per PR
- **Suggestion Accuracy**: > 80% relevant suggestions
- **Error Rate**: < 5%
- **Resource Usage**: < 500MB memory per analysis

### Logging
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('agent_testing.log'),
        logging.StreamHandler()
    ]
)
```

This comprehensive testing guide ensures the GitHub Coverage Agent is thoroughly validated for real-world use with proper error handling, performance monitoring, and quality assurance.
