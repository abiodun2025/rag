#!/usr/bin/env python3
"""
Debug script to test diff analysis
"""

import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the reviewer
from agent.github_code_reviewer import GitHubCodeReviewer

def test_line_analysis():
    """Test the line analysis directly."""
    
    # Initialize the reviewer
    reviewer = GitHubCodeReviewer()
    
    print("🔍 Testing line analysis...")
    print("=" * 50)
    
    # Test lines that should trigger issues
    test_lines = [
        "result = eval(user_input)",
        "if password == \"admin123\":",
        "for i in range(len(username)):",
        "long_variable_name_that_makes_this_line_very_long_and_should_be_broken_into_multiple_lines_for_better_readability = \"This is a very long line that should be broken up\"",
        "def validate_user():",
        "file_content = open(\"config.txt\").read()",
        "admin_creds = {\"admin\": \"password123\", \"user\": \"123456\"}",
        "for user in admin_creds:",
        "for char in user:"
    ]
    
    total_issues = 0
    
    for i, line in enumerate(test_lines, 1):
        issues = reviewer._analyze_line_for_issues(line, i, 'added')
        print(f"Line {i}: '{line[:50]}...' -> {len(issues)} issues")
        total_issues += len(issues)
        
        for issue in issues:
            print(f"   - {issue.get('severity')}: {issue.get('message')}")
    
    print(f"\n📊 Total issues found: {total_issues}")
    
    # Test scoring
    if total_issues > 0:
        score = 100
        # This is a simplified scoring - the actual method groups by severity
        score -= total_issues * 5  # Assume average severity
        score = max(0, score)
        grade = reviewer._calculate_grade(score)
        print(f"📊 Estimated score: {score}, Grade: {grade}")
    else:
        print("❌ No issues found! This explains the 0 scores.")

def test_diff_parsing():
    """Test diff parsing with a simple diff."""
    
    reviewer = GitHubCodeReviewer()
    
    print("\n🔍 Testing diff parsing...")
    print("=" * 50)
    
    # Simple diff with just a few lines
    simple_diff = """diff --git a/test.py b/test.py
new file mode 100644
index 0000000..1234567
--- /dev/null
+++ b/test.py
@@ -0,0 +1,5 @@
+#!/usr/bin/env python3
+result = eval(user_input)
+if password == "admin123":
+for i in range(len(username)):
+long_variable_name_that_makes_this_line_very_long_and_should_be_broken_into_multiple_lines_for_better_readability = "This is a very long line"
+"""
    
    result = reviewer._analyze_diff_content(simple_diff, "test.py")
    
    print(f"📊 Analysis Result:")
    print(f"   Score: {result.get('score', 'N/A')}")
    print(f"   Grade: {result.get('grade', 'N/A')}")
    print(f"   Total Issues: {result.get('issues', {}).get('total', 'N/A')}")
    print(f"   Added Lines: {result.get('changes', {}).get('added_lines', 'N/A')}")
    
    issues = result.get('issues', {}).get('details', [])
    for i, issue in enumerate(issues, 1):
        print(f"   {i}. Line {issue.get('line')}: {issue.get('severity')} - {issue.get('message')}")

if __name__ == "__main__":
    test_line_analysis()
    test_diff_parsing() 