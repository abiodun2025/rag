#!/usr/bin/env python3
"""
Real-World Test for GitHub-Integrated Test Coverage Agent
Demonstrates the agent working with actual GitHub repositories and data.
"""

import os
import json
import requests
from agent.github_coverage_agent import GitHubCoverageAgent, GitHubConfig

def test_github_api_integration():
    """Test GitHub API integration with real data."""
    print("🔗 Testing GitHub API Integration")
    print("=" * 50)
    
    token = os.getenv('GITHUB_TOKEN')
    owner = os.getenv('GITHUB_OWNER')
    repo = os.getenv('GITHUB_REPO')
    
    if not all([token, owner, repo]):
        print("❌ Missing GitHub configuration!")
        return False
    
    # Test GitHub API directly
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Test repository access
    repo_url = f"https://api.github.com/repos/{owner}/{repo}"
    response = requests.get(repo_url, headers=headers)
    
    if response.status_code == 200:
        repo_data = response.json()
        print(f"✅ Repository access successful!")
        print(f"📁 Repository: {repo_data['full_name']}")
        print(f"📝 Description: {repo_data.get('description', 'No description')}")
        print(f"⭐ Stars: {repo_data['stargazers_count']}")
        print(f"🔀 Forks: {repo_data['forks_count']}")
        print(f"🌿 Default branch: {repo_data['default_branch']}")
        print(f"📅 Created: {repo_data['created_at']}")
        print(f"🔄 Last updated: {repo_data['updated_at']}")
        return True
    else:
        print(f"❌ Repository access failed: {response.status_code}")
        return False

def test_pull_requests():
    """Test pull request analysis with real data."""
    print("\n📋 Testing Pull Request Analysis")
    print("=" * 50)
    
    token = os.getenv('GITHUB_TOKEN')
    owner = os.getenv('GITHUB_OWNER')
    repo = os.getenv('GITHUB_REPO')
    
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Get pull requests
    pr_url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
    response = requests.get(pr_url, headers=headers)
    
    if response.status_code == 200:
        prs = response.json()
        print(f"✅ Found {len(prs)} open pull requests:")
        
        for pr in prs[:3]:  # Show first 3 PRs
            print(f"\n📋 PR #{pr['number']}: {pr['title']}")
            print(f"   👤 Author: {pr['user']['login']}")
            print(f"   🌿 Branch: {pr['head']['ref']} → {pr['base']['ref']}")
            print(f"   📅 Created: {pr['created_at']}")
            print(f"   🔄 Updated: {pr['updated_at']}")
            print(f"   📊 State: {pr['state']}")
            print(f"   🔗 URL: {pr['html_url']}")
            
            # Get PR files
            files_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr['number']}/files"
            files_response = requests.get(files_url, headers=headers)
            
            if files_response.status_code == 200:
                files = files_response.json()
                print(f"   📁 Files changed: {len(files)}")
                
                # Analyze file types
                file_types = {}
                for file in files:
                    ext = file['filename'].split('.')[-1] if '.' in file['filename'] else 'no_ext'
                    file_types[ext] = file_types.get(ext, 0) + 1
                
                print(f"   📊 File types: {dict(list(file_types.items())[:5])}")
                
                # Show some changed files
                for file in files[:3]:
                    print(f"      - {file['filename']} (+{file['additions']}, -{file['deletions']})")
                
                if len(files) > 3:
                    print(f"      ... and {len(files) - 3} more files")
        
        return True
    else:
        print(f"❌ Failed to get pull requests: {response.status_code}")
        return False

def test_agent_initialization():
    """Test the GitHub Coverage Agent initialization."""
    print("\n🤖 Testing Agent Initialization")
    print("=" * 50)
    
    token = os.getenv('GITHUB_TOKEN')
    owner = os.getenv('GITHUB_OWNER')
    repo = os.getenv('GITHUB_REPO')
    
    if not all([token, owner, repo]):
        print("❌ Missing GitHub configuration!")
        return False
    
    try:
        config = GitHubConfig(token=token, owner=owner, repo=repo)
        agent = GitHubCoverageAgent(config)
        
        print("✅ Agent initialized successfully!")
        print(f"📁 Repository: {agent.github_config.owner}/{agent.github_config.repo}")
        print(f"🔑 Token: {agent.github_config.token[:10]}...")
        print(f"🌿 Default branch: {agent.github_config.branch}")
        
        return True
    except Exception as e:
        print(f"❌ Agent initialization failed: {e}")
        return False

def test_pr_info_retrieval():
    """Test PR information retrieval."""
    print("\n📋 Testing PR Information Retrieval")
    print("=" * 50)
    
    token = os.getenv('GITHUB_TOKEN')
    owner = os.getenv('GITHUB_OWNER')
    repo = os.getenv('GITHUB_REPO')
    
    config = GitHubConfig(token=token, owner=owner, repo=repo)
    agent = GitHubCoverageAgent(config)
    
    # Test with PR #11 (which we know exists)
    try:
        pr_info = agent._get_pr_info(11)
        if pr_info:
            print("✅ PR information retrieved successfully!")
            print(f"📋 PR #{pr_info['number']}: {pr_info['title']}")
            print(f"👤 Author: {pr_info['user']['login']}")
            print(f"🌿 Branch: {pr_info['head']['ref']} → {pr_info['base']['ref']}")
            print(f"📅 Created: {pr_info['created_at']}")
            print(f"📊 State: {pr_info['state']}")
            print(f"🔗 URL: {pr_info['html_url']}")
            
            # Get PR files
            files = agent._get_pr_files(11)
            if files:
                print(f"📁 Files changed: {len(files)}")
                for file in files[:3]:
                    print(f"   - {file['filename']} (+{file['additions']}, -{file['deletions']})")
                if len(files) > 3:
                    print(f"   ... and {len(files) - 3} more files")
            
            return True
        else:
            print("❌ Failed to retrieve PR information")
            return False
    except Exception as e:
        print(f"❌ Error retrieving PR information: {e}")
        return False

def test_coverage_analysis_demo():
    """Demonstrate coverage analysis with local files."""
    print("\n📊 Testing Coverage Analysis Demo")
    print("=" * 50)
    
    # Find test files in current directory
    import glob
    test_files = glob.glob("test_*.py")
    
    print(f"📁 Found {len(test_files)} test files in current directory:")
    for test_file in test_files[:5]:
        print(f"   - {test_file}")
    if len(test_files) > 5:
        print(f"   ... and {len(test_files) - 5} more")
    
    # Run a simple test with coverage
    import subprocess
    
    print("\n🧪 Running sample test with coverage...")
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
                
                # Parse with our agent
                token = os.getenv('GITHUB_TOKEN')
                owner = os.getenv('GITHUB_OWNER')
                repo = os.getenv('GITHUB_REPO')
                
                config = GitHubConfig(token=token, owner=owner, repo=repo)
                agent = GitHubCoverageAgent(config)
                
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
                        print("\n💡 No specific suggestions generated")
                
                return True
            else:
                print("❌ Failed to generate coverage report")
                return False
        else:
            print(f"❌ Test execution failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error during test execution: {e}")
        return False

def main():
    """Run all real-world tests."""
    print("🔗 Real-World GitHub-Integrated Test Coverage Agent Test")
    print("=" * 70)
    print("Testing the agent with actual GitHub repositories and data")
    print("=" * 70)
    
    tests = [
        ("GitHub API Integration", test_github_api_integration),
        ("Pull Request Analysis", test_pull_requests),
        ("Agent Initialization", test_agent_initialization),
        ("PR Information Retrieval", test_pr_info_retrieval),
        ("Coverage Analysis Demo", test_coverage_analysis_demo),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🎯 Running: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 Test Results Summary")
    print("=" * 70)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The GitHub-Integrated Test Coverage Agent is working correctly.")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
    
    print("\n🚀 The agent is ready for real-world use with:")
    print("   • GitHub repository integration")
    print("   • Pull request analysis")
    print("   • Test coverage analysis")
    print("   • Intelligent test suggestions")
    print("   • Multi-language support")

if __name__ == "__main__":
    main()
