#!/usr/bin/env python3
"""
Demo script for GitHub-Integrated Test Coverage Agent
Shows how the agent connects to GitHub and analyzes test coverage.
"""

import os
import json
from agent.github_coverage_agent import GitHubCoverageAgent, GitHubConfig

def main():
    print("🔗 GitHub-Integrated Test Coverage Agent Demo")
    print("=" * 60)
    
    # Set up GitHub configuration from environment
    token = os.getenv('GITHUB_TOKEN')
    owner = os.getenv('GITHUB_OWNER')
    repo = os.getenv('GITHUB_REPO')
    
    if not all([token, owner, repo]):
        print("❌ Missing GitHub configuration!")
        print("Please set: GITHUB_TOKEN, GITHUB_OWNER, GITHUB_REPO")
        return
    
    print(f"📁 Repository: {owner}/{repo}")
    print(f"🔑 Token: {token[:10]}...")
    print()
    
    # Initialize the agent
    config = GitHubConfig(token=token, owner=owner, repo=repo)
    agent = GitHubCoverageAgent(config)
    
    print("🎯 Demo 1: Testing GitHub Connection")
    print("-" * 40)
    
    # Test GitHub connection
    try:
        pr_info = agent._get_pr_info(1)  # Try to get PR #1
        if pr_info:
            print("✅ GitHub API connection successful!")
            print(f"📋 Found PR #{pr_info['number']}: {pr_info['title']}")
        else:
            print("⚠️ GitHub API connection works, but no PR #1 found")
    except Exception as e:
        print(f"❌ GitHub API connection failed: {e}")
        return
    
    print()
    print("🎯 Demo 2: Repository Analysis")
    print("-" * 40)
    
    # Analyze the current repository (local analysis)
    print("🔍 Analyzing current repository structure...")
    
    # Find test files
    import glob
    test_files = glob.glob("test_*.py")
    print(f"📁 Found {len(test_files)} test files:")
    for test_file in test_files[:5]:  # Show first 5
        print(f"   - {test_file}")
    if len(test_files) > 5:
        print(f"   ... and {len(test_files) - 5} more")
    
    # Run a simple test with coverage
    print("\n🧪 Running sample test with coverage...")
    import subprocess
    
    try:
        # Run a simple test
        result = subprocess.run([
            'python3', '-m', 'coverage', 'run', '-m', 'pytest', 'test_email_body_issue.py', '-q'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Test execution successful!")
            
            # Generate coverage report
            report_result = subprocess.run([
                'python3', '-m', 'coverage', 'report'
            ], capture_output=True, text=True)
            
            if report_result.returncode == 0:
                print("📊 Coverage Report:")
                print(report_result.stdout)
                
                # Parse coverage data
                coverage_data = agent._parse_python_coverage(report_result.stdout)
                if coverage_data:
                    print(f"\n📈 Parsed Coverage Data:")
                    print(f"   Total Lines: {coverage_data.total_lines}")
                    print(f"   Covered Lines: {coverage_data.covered_lines}")
                    print(f"   Coverage: {coverage_data.coverage_percentage:.1f}%")
                    
                    # Generate suggestions
                    suggestions = agent._generate_test_suggestions(
                        coverage_data, "test_email_body_issue.py", "py"
                    )
                    
                    if suggestions:
                        print(f"\n💡 Generated {len(suggestions)} test suggestions:")
                        for i, suggestion in enumerate(suggestions[:3], 1):
                            print(f"   {i}. {suggestion.description}")
                            print(f"      Type: {suggestion.type} | Priority: {suggestion.priority}")
                    else:
                        print("\n💡 No specific suggestions generated (good coverage!)")
                else:
                    print("❌ Failed to parse coverage data")
            else:
                print("❌ Failed to generate coverage report")
        else:
            print(f"❌ Test execution failed: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Error during test execution: {e}")
    
    print()
    print("🎯 Demo 3: GitHub Integration Features")
    print("-" * 40)
    
    print("🔗 The GitHub-Integrated Test Coverage Agent can:")
    print("   ✅ Connect to GitHub repositories")
    print("   ✅ Clone repositories automatically")
    print("   ✅ Detect project types (Python, Java, JS, Go)")
    print("   ✅ Run tests with coverage tools")
    print("   ✅ Parse coverage reports")
    print("   ✅ Generate intelligent test suggestions")
    print("   ✅ Analyze pull requests")
    print("   ✅ Provide actionable recommendations")
    
    print()
    print("🚀 Ready to use with your GitHub repositories!")
    print("   Run: python3 github_coverage_cli.py interactive")
    print("   Or: python3 github_coverage_cli.py repo main")
    print("   Or: python3 github_coverage_cli.py pr <number>")

if __name__ == "__main__":
    main()
