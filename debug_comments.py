#!/usr/bin/env python3
"""
Debug script to test comment creation functionality
"""
import os
from dotenv import load_dotenv
from agent.github_code_reviewer import GitHubCodeReviewer

# Load environment variables
load_dotenv()

def test_comment_creation():
    """Test the comment creation step by step"""
    print("🔍 Testing comment creation functionality...")
    
    # Initialize the reviewer
    reviewer = GitHubCodeReviewer()
    
    # Test with a simple PR (you'll need to replace these with actual values)
    owner = "abiodun2025"  # Replace with actual owner
    repo = "rag"           # Replace with actual repo
    pr_number = 1          # Replace with actual PR number
    
    print(f"📋 Testing with PR: {owner}/{repo}#{pr_number}")
    
    # Step 1: Test PR details retrieval
    print("\n1️⃣ Testing PR details retrieval...")
    pr_result = reviewer.get_pull_request_details(owner, repo, pr_number)
    if pr_result["success"]:
        print(f"✅ PR details retrieved: {pr_result['pull_request']['title']}")
    else:
        print(f"❌ Failed to get PR details: {pr_result['error']}")
        return
    
    # Step 2: Test PR files retrieval
    print("\n2️⃣ Testing PR files retrieval...")
    files_result = reviewer.get_pull_request_files(owner, repo, pr_number)
    if files_result["success"]:
        print(f"✅ Found {len(files_result['files'])} changed files")
        for file_info in files_result['files'][:3]:  # Show first 3 files
            print(f"   📁 {file_info['filename']} (+{file_info['additions']}, -{file_info['deletions']})")
            if 'patch' in file_info:
                print(f"      Has patch: {len(file_info['patch'])} chars")
            else:
                print(f"      No patch content")
    else:
        print(f"❌ Failed to get PR files: {files_result['error']}")
        return
    
    # Step 3: Test diff analysis...
    print("\n3️⃣ Testing diff analysis...")
    if files_result['files']:
        first_file = files_result['files'][0]
        file_diff = reviewer._extract_file_diff_from_files(first_file)
        if file_diff:
            print(f"✅ Extracted diff for {first_file['filename']}")
            print(f"   Diff length: {len(file_diff)} chars")
            print(f"   Diff content preview:")
            print("   " + "="*50)
            for i, line in enumerate(file_diff.split('\n')[:10]):
                print(f"   {i:2d}: {line}")
            print("   " + "="*50)
            
            # Analyze the diff
            try:
                analysis = reviewer._analyze_diff_content_senior(file_diff, first_file['filename'])
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
                    
                else:
                    print(f"❌ Analysis failed: {analysis['error']}")
            except Exception as e:
                import traceback
                print(f"❌ Analysis error: {e}")
                print(f"📋 Traceback: {traceback.format_exc()}")
        else:
            print(f"❌ No diff content extracted")
    
    # Step 4: Test comment creation
    print("\n4️⃣ Testing comment creation...")
    if files_result['files']:
        # First, try to create a general comment on the PR
        print("   🔍 Testing general PR comment creation...")
        general_comment = "🔍 **General Test Comment**\n\nThis is a test comment to verify the commenting functionality works.\n\n💡 **Why this matters**: Testing the system.\n\n🔧 **Suggestion**: This is just a test."
        
        general_result = reviewer.create_pull_request_comment(
            owner, repo, pr_number, 
            general_comment
        )
        
        if general_result["success"]:
            print("   ✅ General comment created successfully!")
            print(f"      Comment URL: {general_result['comment']['html_url']}")
        else:
            print(f"   ❌ Failed to create general comment: {general_result['error']}")
        
        # Now try line-specific comments
        print("\n   🔍 Testing line-specific comment creation...")
        test_comment = "🔍 **Line-Specific Test Comment**\n\nThis is a test comment on a specific line.\n\n💡 **Why this matters**: Testing line-specific comments.\n\n🔧 **Suggestion**: This is just a test."
        
        # Try different line numbers
        test_lines = [1, 2, 3]
        
        for line_num in test_lines:
            print(f"      🔍 Trying to create comment on line {line_num}...")
            comment_result = reviewer.create_pull_request_comment(
                owner, repo, pr_number, 
                test_comment, 
                line=line_num,  # Comment on specific line
                file=files_result['files'][0]['filename']
            )
            
            if comment_result["success"]:
                print(f"      ✅ Comment created successfully on line {line_num}!")
                print(f"         Comment URL: {comment_result['comment']['html_url']}")
                break
            else:
                print(f"      ❌ Failed to create comment on line {line_num}: {comment_result['error']}")
                if "422" in str(comment_result['error']):
                    print(f"         This suggests line {line_num} is invalid for this file")
                elif "404" in str(comment_result['error']):
                    print(f"         This suggests the file or line doesn't exist")
                else:
                    print(f"         Unknown error type")
        else:
            print("   ❌ Failed to create line-specific comment on any line")
    
    print("\n🏁 Debug test complete!")

if __name__ == "__main__":
    test_comment_creation() 