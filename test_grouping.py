#!/usr/bin/env python3
"""
Test script to test the issue grouping logic directly
"""
import os
from dotenv import load_dotenv
from agent.github_code_reviewer import GitHubCodeReviewer

# Load environment variables
load_dotenv()

def test_issue_grouping():
    """Test the issue grouping logic directly"""
    print("🔍 Testing issue grouping logic directly...")
    
    # Initialize the reviewer
    reviewer = GitHubCodeReviewer()
    
    # Read the test file content
    test_file_path = "test_repetitive_issues.py"
    if not os.path.exists(test_file_path):
        print(f"❌ Test file {test_file_path} not found")
        return
    
    with open(test_file_path, 'r') as f:
        file_content = f.read()
    
    print(f"📁 Test file: {test_file_path}")
    print(f"📏 File size: {len(file_content)} characters")
    print(f"📝 Lines: {len(file_content.split(chr(10)))}")
    
    # Create a mock diff content (simulating what GitHub would provide)
    lines = file_content.split('\n')
    diff_content = ""
    current_line = 1
    
    for line in lines:
        if line.strip():  # Skip empty lines
            diff_content += f"+{line}\n"
            current_line += 1
    
    print(f"\n🔍 Created diff with {len(diff_content.split(chr(10)))} lines")
    
    # Analyze the diff content
    print(f"\n3️⃣ Testing diff analysis...")
    try:
        analysis = reviewer._analyze_diff_content_senior(diff_content, test_file_path)
        if analysis["success"]:
            print(f"✅ Analysis complete: {analysis['total_issues']} issues found")
            
            # Show raw issues before grouping
            print(f"\n📋 Raw issues detected:")
            for i, issue in enumerate(analysis['issues']):
                print(f"   {i+1}. Line {issue['line']}: {issue['severity']} {issue['category']} - {issue['message']}")
            
            # Test the grouping logic
            if analysis['issues']:
                print(f"\n🔍 Testing issue grouping...")
                grouped_issues = reviewer._group_similar_issues(analysis['issues'])
                print(f"   Original issues: {len(analysis['issues'])}")
                print(f"   After grouping: {len(grouped_issues)}")
                
                print(f"\n📋 Grouped issues:")
                for i, issue in enumerate(grouped_issues):
                    count = issue.get('_consolidated_count', 1)
                    print(f"   {i+1}. Line {issue['line']}: {issue['severity']} {issue['category']} - {issue['message']} (consolidated: {count})")
                
                # Test diverse selection
                print(f"\n🎯 Testing diverse issue selection...")
                diverse_issues = reviewer._select_diverse_issues(grouped_issues, max_per_file=3)
                print(f"   Selected diverse issues: {len(diverse_issues)}")
                for i, issue in enumerate(diverse_issues):
                    print(f"   {i+1}. {issue['severity']} {issue['category']} - {issue['message']}")
                
                # Show what the final comments would look like
                print(f"\n💬 Final comments that would be created:")
                for i, issue in enumerate(diverse_issues):
                    severity = issue.get('severity', 'low')
                    category = issue.get('category', 'general')
                    message = issue.get('message', '')
                    suggestion = issue.get('suggestion', '')
                    
                    severity_emoji = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'}
                    emoji = severity_emoji.get(severity, '🟢')
                    
                    print(f"   {i+1}. {emoji} {severity.title()} {category.title()}: {message}")
                    print(f"      💡 Suggestion: {suggestion}")
                    print()
            else:
                print("❌ No issues found to test grouping")
                
        else:
            print(f"❌ Analysis failed: {analysis['error']}")
    except Exception as e:
        import traceback
        print(f"❌ Analysis error: {e}")
        print(f"📋 Traceback: {traceback.format_exc()}")
    
    print("\n🏁 Grouping test complete!")

if __name__ == "__main__":
    test_issue_grouping() 