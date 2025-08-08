#!/usr/bin/env python3
"""
GitHub Multi-Language Coverage Commenter
Analyzes coverage for any programming language and comments on GitHub PRs.
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

def analyze_repository_coverage(repo_path):
    """Analyze coverage for a repository."""
    analyzer = MultiLanguageCoverage()
    return analyzer.analyze_coverage(repo_path)

def comment_on_pr(owner, repo, pr_number, coverage_result):
    """Comment on a GitHub PR with coverage results."""
    
    # Get GitHub token
    token = os.environ.get('GITHUB_TOKEN')
    if not token:
        return {"error": "GITHUB_TOKEN not set"}
    
    # Prepare comment
    language = coverage_result.get('language', 'unknown').upper()
    coverage = coverage_result.get('coverage', 0)
    test_result = coverage_result.get('test_result', 'unknown')
    
    # Create detailed comment
    comment = f"""## 🔍 Code Coverage Analysis

**Language Detected:** {language}
**Coverage:** {coverage:.1f}%
**Test Status:** {test_result.upper()}

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

### 🛠️ Recommendations:
"""
    
    if coverage < 60:
        comment += """
- Add unit tests for core functionality
- Test edge cases and error conditions
- Consider integration tests for critical paths
- Aim for at least 80% coverage for production code
"""
    elif coverage < 80:
        comment += """
- Add tests for remaining uncovered code paths
- Focus on business logic and critical functions
- Consider adding property-based tests
"""
    else:
        comment += """
- Maintain high coverage standards
- Consider adding performance tests
- Review test quality and effectiveness
"""
    
    comment += f"""

---
*This analysis was performed automatically by the Multi-Language Coverage Tool.*
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
                "language": language
            }
        else:
            return {
                "error": f"Failed to post comment: {response.status_code} - {response.text}"
            }
            
    except Exception as e:
        return {"error": f"Comment posting failed: {str(e)}"}

def main():
    """Main function."""
    print("🌍 GitHub Multi-Language Coverage Commenter")
    print("=" * 60)
    
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
    
    # Get repository URL
    repo_url = f"https://github.com/{owner}/{repo}.git"
    
    print(f"🔍 Analyzing coverage for PR #{pr_number}")
    print(f"📁 Repository: {owner}/{repo}")
    
    # Clone repository
    print("📥 Cloning repository...")
    repo_path, error = clone_repository(repo_url)
    
    if error:
        print(f"❌ {error}")
        return
    
    try:
        # Analyze coverage
        print("🔍 Analyzing coverage...")
        coverage_result = analyze_repository_coverage(repo_path)
        
        if "error" in coverage_result:
            print(f"❌ Coverage analysis failed: {coverage_result['error']}")
            return
        
        # Display results
        print("\n📊 Coverage Results:")
        print("=" * 40)
        print(f"📝 Language: {coverage_result['language'].upper()}")
        print(f"✅ Coverage: {coverage_result['coverage']:.1f}%")
        print(f"🧪 Test Result: {coverage_result['test_result']}")
        
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
            
    finally:
        # Cleanup
        if repo_path:
            shutil.rmtree(repo_path, ignore_errors=True)

if __name__ == "__main__":
    main()
