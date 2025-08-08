#!/usr/bin/env python3
"""
GitHub Multi-Language Coverage Commenter with Test Generation
Analyzes coverage for any programming language, generates tests, and comments on GitHub PRs.
"""

import os
import requests
import subprocess
import tempfile
import shutil
from pathlib import Path
from multi_language_coverage import MultiLanguageCoverage

def clone_repository(repo_url, branch="main"):
    """Clone a GitHub repository."""
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Clone repository
        clone_cmd = ["git", "clone", "--depth", "1", "-b", branch, repo_url, temp_dir]
        result = subprocess.run(clone_cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            return None, f"Failed to clone repository: {result.stderr}"
        
        return temp_dir, None
        
    except Exception as e:
        return None, f"Clone failed: {str(e)}"

def analyze_repository_coverage(repo_path, generate_tests=True):
    """Analyze coverage for a repository with optional test generation."""
    analyzer = MultiLanguageCoverage()
    return analyzer.analyze_coverage(repo_path, generate_tests=generate_tests)

def comment_on_pr(owner, repo, pr_number, coverage_result):
    """Comment on a GitHub PR with coverage results and test generation info."""
    
    # Get GitHub token
    token = os.environ.get('GITHUB_TOKEN')
    if not token:
        return {"error": "GITHUB_TOKEN not set"}
    
    # Prepare comment
    language = coverage_result.get('language', 'unknown').upper()
    coverage = coverage_result.get('coverage', 0)
    test_result = coverage_result.get('test_result', 'unknown')
    tests_found = coverage_result.get('tests_found', 0)
    tests_run = coverage_result.get('tests_run', 0)
    
    # Create detailed comment
    comment = f"""## 🔍 Code Coverage Analysis with Test Generation

**Language Detected:** {language}
**Coverage:** {coverage:.1f}%
**Test Status:** {test_result.upper()}
**Tests Found:** {tests_found}
**Tests Run:** {tests_run}

### 📊 Coverage Assessment:
"""
    
    if coverage >= 80:
        comment += "🎉 **Excellent coverage!** Your code is well tested."
    elif coverage >= 60:
        comment += "👍 **Good coverage.** Consider adding more tests for edge cases."
    elif coverage >= 40:
        comment += "⚠️ **Moderate coverage.** More tests needed for better reliability."
    else:
        comment += "❌ **Low coverage.** Significant test improvements needed."
    
    comment += f"""

### 🧪 Test Generation:
"""
    
    if tests_found > 0:
        comment += f"- ✅ **{tests_found} test files** found in the repository"
        comment += f"- 🏃 **{tests_run} tests** executed during analysis"
        if tests_run < tests_found:
            comment += f"- ⚠️ Only {tests_run}/{tests_found} tests were run (limited for performance)"
    else:
        comment += "- ❌ **No test files found** - consider adding tests"
    
    comment += f"""

### 🛠️ Recommendations:
"""
    
    if coverage < 60:
        comment += """
- Add unit tests for core functionality
- Test edge cases and error conditions
- Consider integration tests for critical paths
- Aim for at least 80% coverage for production code
- Use the auto-generated tests as a starting point
"""
    elif coverage < 80:
        comment += """
- Add tests for remaining uncovered code paths
- Focus on business logic and critical functions
- Consider adding property-based tests
- Review and enhance auto-generated tests
"""
    else:
        comment += """
- Maintain high coverage standards
- Consider adding performance tests
- Review test quality and effectiveness
- Optimize test execution time
"""
    
    # Add test output if available
    if "test_output" in coverage_result and coverage_result["test_output"]:
        test_output = coverage_result["test_output"]
        # Truncate if too long
        if len(test_output) > 1000:
            test_output = test_output[:1000] + "..."
        
        comment += f"""

### 📋 Test Execution Output:
```
{test_output}
```
"""
    
    comment += f"""

---
*This analysis was performed automatically by the Multi-Language Coverage Tool with Test Generation.*
"""
    
    # Post comment to GitHub
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{pr_number}/comments"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {"body": comment}
    
    try:
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 201:
            return {
                "success": True,
                "comment_url": response.json()["html_url"],
                "coverage": coverage,
                "language": language,
                "tests_found": tests_found,
                "tests_run": tests_run
            }
        else:
            return {
                "error": f"Failed to post comment: {response.status_code} - {response.text}"
            }
            
    except Exception as e:
        return {"error": f"Comment posting failed: {str(e)}"}

def main():
    """Main function."""
    print("🌍 GitHub Multi-Language Coverage Commenter with Test Generation")
    print("=" * 70)
    
    # Get GitHub configuration
    owner = os.environ.get('GITHUB_OWNER')
    repo = os.environ.get('GITHUB_REPO')
    
    if not owner or not repo:
        print("❌ Please set GITHUB_OWNER and GITHUB_REPO environment variables")
        return
    
    # Get PR number
    try:
        pr_number = input("Enter PR number: ").strip()
        if not pr_number:
            print("❌ PR number is required")
            return
        pr_number = int(pr_number)
    except ValueError:
        print("❌ Invalid PR number")
        return
    
    # Ask about test generation
    generate_tests = input("Generate tests automatically? (y/n): ").strip().lower() == 'y'
    
    # Get repository URL
    repo_url = f"https://github.com/{owner}/{repo}.git"
    
    print(f"🔍 Analyzing coverage for PR #{pr_number}")
    print(f"📁 Repository: {owner}/{repo}")
    print(f"🧪 Test Generation: {'Enabled' if generate_tests else 'Disabled'}")
    
    # Clone repository
    print("📥 Cloning repository...")
    repo_path, error = clone_repository(repo_url)
    
    if error:
        print(f"❌ {error}")
        return
    
    try:
        # Analyze coverage with test generation
        print("🔍 Analyzing coverage...")
        coverage_result = analyze_repository_coverage(repo_path, generate_tests=generate_tests)
        
        if "error" in coverage_result:
            print(f"❌ Coverage analysis failed: {coverage_result['error']}")
            return
        
        # Display results
        print("\n📊 Coverage Results:")
        print("=" * 50)
        print(f"📝 Language: {coverage_result['language'].upper()}")
        print(f"✅ Coverage: {coverage_result['coverage']:.1f}%")
        print(f"🧪 Test Result: {coverage_result['test_result']}")
        
        if "tests_found" in coverage_result:
            print(f"📁 Tests Found: {coverage_result['tests_found']}")
        if "tests_run" in coverage_result:
            print(f"🏃 Tests Run: {coverage_result['tests_run']}")
        
        # Comment on PR
        print("\n💬 Posting comment to PR...")
        comment_result = comment_on_pr(owner, repo, pr_number, coverage_result)
        
        if "error" in comment_result:
            print(f"❌ Failed to post comment: {comment_result['error']}")
        else:
            print("✅ Comment posted successfully!")
            print(f"🔗 Comment URL: {comment_result['comment_url']}")
            print(f"📊 Coverage: {comment_result['coverage']:.1f}%")
            print(f"📝 Language: {comment_result['language']}")
            print(f"📁 Tests Found: {comment_result['tests_found']}")
            print(f"🏃 Tests Run: {comment_result['tests_run']}")
            
    finally:
        # Cleanup
        if repo_path:
            shutil.rmtree(repo_path, ignore_errors=True)

if __name__ == "__main__":
    main()
