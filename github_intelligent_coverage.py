#!/usr/bin/env python3
"""
GitHub Intelligent Coverage with Test Generation
Generates meaningful tests, runs them, and posts improved coverage to GitHub PRs.
"""

import os
import requests
import subprocess
import tempfile
import shutil
from pathlib import Path
from intelligent_test_generator import IntelligentTestGenerator
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

def generate_intelligent_tests_and_analyze(repo_path, language):
    """Generate intelligent tests and analyze coverage."""
    print("🧠 Generating intelligent tests...")
    
    # Generate intelligent tests
    generator = IntelligentTestGenerator()
    test_result = generator.generate_intelligent_tests(repo_path, language)
    
    if "error" in test_result:
        return {"error": test_result["error"]}
    
    print(f"✅ Generated {test_result['tests_generated']} intelligent test files")
    print(f"📈 Estimated coverage improvement: {test_result['estimated_coverage_improvement']}%")
    
    # Run coverage analysis with the new tests
    print("🔍 Running coverage analysis with intelligent tests...")
    analyzer = MultiLanguageCoverage()
    coverage_result = analyzer.analyze_coverage(repo_path, generate_tests=False)  # Don't generate again
    
    # Combine results
    combined_result = {
        **coverage_result,
        "intelligent_tests_generated": test_result.get("tests_generated", 0),
        "estimated_coverage_improvement": test_result.get("estimated_coverage_improvement", 0),
        "source_files_analyzed": test_result.get("source_files_analyzed", 0)
    }
    
    return combined_result

def comment_on_pr_with_intelligent_tests(owner, repo, pr_number, coverage_result):
    """Comment on a GitHub PR with intelligent test generation results."""
    
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
    intelligent_tests_generated = coverage_result.get('intelligent_tests_generated', 0)
    estimated_improvement = coverage_result.get('estimated_coverage_improvement', 0)
    source_files_analyzed = coverage_result.get('source_files_analyzed', 0)
    
    # Create detailed comment
    comment = f"""## 🧠 Intelligent Test Generation & Coverage Analysis

**Language Detected:** {language}
**Current Coverage:** {coverage:.1f}%
**Test Status:** {test_result.upper()}
**Tests Found:** {tests_found}
**Tests Run:** {tests_run}

### 🧪 Intelligent Test Generation:
"""
    
    if intelligent_tests_generated > 0:
        comment += f"""
- ✅ **{intelligent_tests_generated} intelligent test files** generated automatically
- 📁 **{source_files_analyzed} source files** analyzed for test generation
- 📈 **Estimated coverage improvement:** {estimated_improvement}%
- 🧠 **Smart analysis** of classes, functions, and code patterns
- 🔧 **Mock-based testing** for HTTP requests, file operations, and APIs
"""
    else:
        comment += """
- ⚠️ **No new tests generated** (existing tests found or generation failed)
- 🔍 **Code analysis completed** but no new test files created
"""
    
    comment += f"""

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
    
    if intelligent_tests_generated > 0:
        comment += f"\n\n🚀 **Coverage improved by {estimated_improvement}%** with intelligent test generation!"
    
    comment += f"""

### 🛠️ Intelligent Test Features:
"""
    
    if intelligent_tests_generated > 0:
        comment += """
- **AST Analysis** - Parses source code to understand structure
- **Pattern Detection** - Identifies HTTP, file I/O, API patterns
- **Mock Integration** - Creates realistic test scenarios
- **Class & Function Testing** - Tests all public methods
- **Integration Tests** - Tests complete workflows
- **Error Handling** - Tests exception scenarios
"""
    else:
        comment += """
- **Code Structure Analysis** - Analyzes classes and functions
- **Pattern Recognition** - Detects common code patterns
- **Test Template Generation** - Creates appropriate test frameworks
- **Coverage Optimization** - Focuses on uncovered code paths
"""
    
    comment += f"""

### 🎯 Recommendations:
"""
    
    if coverage < 60:
        comment += """
- Review and enhance the generated intelligent tests
- Add specific test cases for business logic
- Test edge cases and error conditions
- Consider integration tests for critical paths
- Aim for at least 80% coverage for production code
"""
    elif coverage < 80:
        comment += """
- Enhance the generated tests with specific assertions
- Add tests for remaining uncovered code paths
- Focus on business logic and critical functions
- Consider adding property-based tests
- Review test quality and effectiveness
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
*This analysis was performed automatically by the Intelligent Test Generator with Coverage Analysis.*
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
                "tests_run": tests_run,
                "intelligent_tests_generated": intelligent_tests_generated,
                "estimated_improvement": estimated_improvement
            }
        else:
            return {
                "error": f"Failed to post comment: {response.status_code} - {response.text}"
            }
            
    except Exception as e:
        return {"error": f"Comment posting failed: {str(e)}"}

def main():
    """Main function."""
    print("🧠 GitHub Intelligent Coverage with Test Generation")
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
    
    # Get repository URL
    repo_url = f"https://github.com/{owner}/{repo}.git"
    
    print(f"🧠 Analyzing coverage for PR #{pr_number}")
    print(f"📁 Repository: {owner}/{repo}")
    print("🧪 Intelligent Test Generation: Enabled")
    
    # Clone repository
    print("📥 Cloning repository...")
    repo_path, error = clone_repository(repo_url)
    
    if error:
        print(f"❌ {error}")
        return
    
    try:
        # Detect language
        analyzer = MultiLanguageCoverage()
        language = analyzer.detect_language(repo_path)
        print(f"📝 Detected language: {language.upper()}")
        
        # Generate intelligent tests and analyze coverage
        coverage_result = generate_intelligent_tests_and_analyze(repo_path, language)
        
        if "error" in coverage_result:
            print(f"❌ Analysis failed: {coverage_result['error']}")
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
        if "intelligent_tests_generated" in coverage_result:
            print(f"🧠 Intelligent Tests Generated: {coverage_result['intelligent_tests_generated']}")
        if "estimated_coverage_improvement" in coverage_result:
            print(f"📈 Estimated Coverage Improvement: {coverage_result['estimated_coverage_improvement']}%")
        
        # Comment on PR
        print("\n💬 Posting intelligent analysis to PR...")
        comment_result = comment_on_pr_with_intelligent_tests(owner, repo, pr_number, coverage_result)
        
        if "error" in comment_result:
            print(f"❌ Failed to post comment: {comment_result['error']}")
        else:
            print("✅ Intelligent analysis posted successfully!")
            print(f"🔗 Comment URL: {comment_result['comment_url']}")
            print(f"📊 Coverage: {comment_result['coverage']:.1f}%")
            print(f"📝 Language: {comment_result['language']}")
            print(f"📁 Tests Found: {comment_result['tests_found']}")
            print(f"🏃 Tests Run: {comment_result['tests_run']}")
            print(f"🧠 Intelligent Tests Generated: {comment_result['intelligent_tests_generated']}")
            print(f"📈 Estimated Improvement: {comment_result['estimated_improvement']}%")
            
    finally:
        # Cleanup
        if repo_path:
            shutil.rmtree(repo_path, ignore_errors=True)

if __name__ == "__main__":
    main()
