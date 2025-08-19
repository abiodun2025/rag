#!/usr/bin/env python3
"""
Test script for the Interactive GitHub AI Agent
Demonstrates the agent's capabilities and expected behavior.
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_agent_initialization():
    """Test if the agent can be initialized properly."""
    print("🧪 Testing Interactive GitHub Agent Initialization...")
    
    try:
        from interactive_github_agent import InteractiveGitHubAgent
        
        # Check if required environment variables are set
        github_token = os.getenv('GITHUB_TOKEN')
        cohere_api_key = os.getenv('COHERE_API_KEY')
        
        print(f"✅ Cohere API Key: {'Configured' if cohere_api_key else 'Missing'}")
        print(f"✅ GitHub Token: {'Configured' if github_token else 'Missing'}")
        
        if not github_token:
            print("⚠️  GitHub token not found. Agent will not be able to access GitHub.")
            print("   Create a .env file with GITHUB_TOKEN=your_token_here")
            return False
        
        if not cohere_api_key:
            print("⚠️  Cohere API key not found. AI analysis will not work.")
            return False
        
        # Try to initialize the agent
        agent = InteractiveGitHubAgent()
        print("✅ Agent initialized successfully!")
        print(f"✅ Authenticated as: {agent.user.login}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to initialize agent: {e}")
        return False

def test_repository_listing():
    """Test repository listing functionality."""
    print("\n🧪 Testing Repository Listing...")
    
    try:
        from interactive_github_agent import InteractiveGitHubAgent
        
        agent = InteractiveGitHubAgent()
        repos = agent.list_repos()
        
        print(f"✅ Found {len(repos)} repositories")
        
        # Show first few repositories
        for i, repo in enumerate(repos[:5]):
            print(f"   📁 {repo['full_name']}")
            print(f"      Language: {repo['language'] or 'N/A'}")
            print(f"      Updated: {repo['updated_at'][:10]}")
            print(f"      Issues: {repo['open_issues_count']} | Stars: {repo['stargazers_count']}")
            print()
        
        if len(repos) > 5:
            print(f"   ... and {len(repos) - 5} more repositories")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to list repositories: {e}")
        return False

def test_pr_listing():
    """Test PR listing functionality."""
    print("\n🧪 Testing Pull Request Listing...")
    
    try:
        from interactive_github_agent import InteractiveGitHubAgent
        
        agent = InteractiveGitHubAgent()
        
        # Get first repository with PRs
        repos = agent.list_repos()
        repo_with_prs = None
        
        for repo in repos:
            if repo['open_issues_count'] > 0:  # Likely has PRs
                repo_with_prs = repo
                break
        
        if not repo_with_prs:
            print("⚠️  No repositories with open issues found for PR testing")
            return False
        
        # Select the repository
        if agent.select_repo(repo_with_prs['full_name']):
            print(f"✅ Selected repository: {agent.current_repo_name}")
            
            # List PRs
            prs = agent.list_prs()
            print(f"✅ Found {len(prs)} open pull requests")
            
            if prs:
                for pr in prs[:3]:  # Show first 3 PRs
                    print(f"   🔀 #{pr['number']}: {pr['title']}")
                    print(f"      Author: {pr['author']}")
                    print(f"      Branch: {pr['head_branch']} → {pr['base_branch']}")
                    print(f"      Changes: +{pr['additions']} -{pr['deletions']} ({pr['changed_files']} files)")
                    print()
                
                if len(prs) > 3:
                    print(f"   ... and {len(prs) - 3} more PRs")
            
            return True
        else:
            print(f"❌ Failed to select repository: {repo_with_prs['full_name']}")
            return False
            
    except Exception as e:
        print(f"❌ Failed to list PRs: {e}")
        return False

def test_ai_analysis():
    """Test AI code analysis functionality."""
    print("\n🧪 Testing AI Code Analysis...")
    
    try:
        from interactive_github_agent import InteractiveGitHubAgent
        
        agent = InteractiveGitHubAgent()
        
        # Test with sample code changes
        sample_patch = """diff --git a/test.py b/test.py
index 123..456 100644
--- a/test.py
+++ b/test.py
@@ -1,5 +1,8 @@
 def calculate_total(items):
-    total = 0
-    for item in items:
-        total += item
-    return total
+    if not items:
+        return 0
+    total = 0
+    for item in items:
+        total += item
+    return total
"""
        
        # Test AI analysis
        analysis = asyncio.run(agent.analyze_code_changes(sample_patch, "test.py"))
        
        print("✅ AI analysis completed!")
        print(f"   Score: {analysis.get('score', 'N/A')}/10")
        print(f"   Comments: {len(analysis.get('comments', []))}")
        print(f"   Summary: {analysis.get('summary', 'N/A')[:100]}...")
        
        if analysis.get('comments'):
            print("\n   Sample comments:")
            for i, comment in enumerate(analysis['comments'][:2]):
                print(f"      {i+1}. {comment.get('type', 'general')}: {comment.get('body', '')[:80]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to test AI analysis: {e}")
        return False

def test_comment_formatting():
    """Test comment formatting functionality."""
    print("\n🧪 Testing Comment Formatting...")
    
    try:
        from interactive_github_agent import InteractiveGitHubAgent
        
        agent = InteractiveGitHubAgent()
        
        # Test comment formatting
        sample_comment = {
            'type': 'security',
            'severity': 'critical',
            'body': 'Using eval() is dangerous and should be avoided.'
        }
        
        formatted = agent._format_comment(sample_comment, "test.py")
        
        print("✅ Comment formatting test:")
        print(formatted)
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to test comment formatting: {e}")
        return False

def show_demo_workflow():
    """Show a demo workflow of how the agent would be used."""
    print("\n🎬 Demo Workflow:")
    print("=" * 50)
    
    demo_steps = [
        "1. Start the interactive agent:",
        "   python interactive_github_agent.py",
        "",
        "2. List your repositories:",
        "   🤖 GitHub Agent > list-repos",
        "",
        "3. Select a repository:",
        "   🤖 GitHub Agent > select-repo my-project",
        "",
        "4. List open pull requests:",
        "   🤖 GitHub Agent > list-prs",
        "",
        "5. Get PR details:",
        "   🤖 GitHub Agent > pr-details 123",
        "",
        "6. Analyze and comment on a PR:",
        "   🤖 GitHub Agent > comment-pr 123",
        "",
        "7. Comment on specific file:",
        "   🤖 GitHub Agent > comment-file 123 src/main.py",
        "",
        "8. Exit the agent:",
        "   🤖 GitHub Agent > exit"
    ]
    
    for step in demo_steps:
        print(step)

def main():
    """Run all tests."""
    print("🤖 Interactive GitHub AI Agent - Test Suite")
    print("=" * 50)
    
    tests = [
        ("Agent Initialization", test_agent_initialization),
        ("Repository Listing", test_repository_listing),
        ("PR Listing", test_pr_listing),
        ("AI Analysis", test_ai_analysis),
        ("Comment Formatting", test_comment_formatting)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test '{test_name}' failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n📊 Test Results Summary:")
    print("=" * 30)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Your interactive agent is ready to use.")
    else:
        print("⚠️  Some tests failed. Check the setup guide for troubleshooting.")
    
    # Show demo workflow
    show_demo_workflow()
    
    print("\n🚀 Next Steps:")
    print("1. Create a .env file with your GitHub token")
    print("2. Run: python interactive_github_agent.py")
    print("3. Start exploring your repositories!")

if __name__ == "__main__":
    main() 