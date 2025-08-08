#!/usr/bin/env python3
"""
Simple GitHub Coverage Commenter
Comment on GitHub PRs with coverage results.
"""

import os
import requests
import subprocess
from pathlib import Path

def get_coverage_percentage():
    """Get current repository coverage percentage."""
    try:
        # Run coverage on test files
        test_files = list(Path(".").rglob("test_*.py")) + list(Path(".").rglob("*_test.py"))
        test_files_to_run = test_files[:5]
        
        coverage_cmd = ["python3", "-m", "coverage", "run", "-m", "pytest"] + [str(f) for f in test_files_to_run]
        subprocess.run(coverage_cmd, capture_output=True)
        
        # Get coverage report
        report_cmd = ["python3", "-m", "coverage", "report"]
        result = subprocess.run(report_cmd, capture_output=True, text=True)
        
        # Parse percentage
        lines = result.stdout.split('\n')
        for line in lines:
            if 'TOTAL' in line and '%' in line:
                parts = line.split()
                for part in parts:
                    if part.endswith('%'):
                        return float(part.rstrip('%'))
        return 0
    except:
        return 0

def comment_on_pr(pr_number, coverage_percentage):
    """Comment on GitHub PR with coverage results."""
    
    # Get GitHub token and repo info
    token = os.getenv('GITHUB_TOKEN')
    owner = os.getenv('GITHUB_OWNER', 'abiodun2025')
    repo = os.getenv('GITHUB_REPO', 'rag')
    
    if not token:
        print("❌ GITHUB_TOKEN not set")
        return
    
    # Create comment
    if coverage_percentage >= 80:
        emoji = "🎉"
        status = "Excellent"
    elif coverage_percentage >= 60:
        emoji = "👍"
        status = "Good"
    elif coverage_percentage >= 40:
        emoji = "⚠️"
        status = "Moderate"
    else:
        emoji = "❌"
        status = "Low"
    
    comment = f"""## {emoji} Code Coverage Report

**Coverage: {coverage_percentage:.1f}%** ({status})

### Assessment:
- **Test Coverage**: {coverage_percentage:.1f}%
- **Status**: {status}

### Recommendations:
"""
    
    if coverage_percentage < 40:
        comment += "- 🔴 **Critical**: Add comprehensive tests immediately\n"
        comment += "- Focus on core functionality first\n"
        comment += "- Consider using TDD approach\n"
    elif coverage_percentage < 60:
        comment += "- 🟡 **Important**: Add more test cases\n"
        comment += "- Cover edge cases and error scenarios\n"
        comment += "- Test integration points\n"
    elif coverage_percentage < 80:
        comment += "- 🟢 **Good**: Minor improvements needed\n"
        comment += "- Add tests for uncovered edge cases\n"
        comment += "- Consider integration tests\n"
    else:
        comment += "- 🟢 **Excellent**: Well tested code!\n"
        comment += "- Maintain this high coverage level\n"
        comment += "- Consider adding performance tests\n"
    
    comment += f"""
---
*This report was generated automatically by the Coverage Bot* 🤖
"""
    
    # Post comment to GitHub
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{pr_number}/comments"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {"body": comment}
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 201:
        print(f"✅ Coverage comment posted to PR #{pr_number}")
        print(f"📊 Coverage: {coverage_percentage:.1f}%")
    else:
        print(f"❌ Failed to post comment: {response.status_code}")
        print(response.text)

def main():
    """Main function."""
    print("🤖 GitHub Coverage Commenter")
    print("=" * 40)
    
    # Get PR number
    pr_number = input("Enter PR number: ").strip()
    if not pr_number:
        print("❌ PR number required")
        return
    
    try:
        pr_number = int(pr_number)
    except ValueError:
        print("❌ Invalid PR number")
        return
    
    # Get coverage
    print("🔍 Calculating coverage...")
    coverage = get_coverage_percentage()
    
    if coverage == 0:
        print("❌ Could not calculate coverage")
        return
    
    # Comment on PR
    comment_on_pr(pr_number, coverage)

if __name__ == "__main__":
    main()
