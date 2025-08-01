#!/usr/bin/env python3
"""
Debug script to examine diff content
"""

import sys
import os
import requests

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def examine_diff_content():
    """Examine the actual diff content from PR #6."""
    
    owner = "abiodun2025"
    repo = "rag"
    pr_number = 6
    
    # Get PR diff
    pr_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
    diff_url = f"{pr_url}.diff"
    
    headers = {"Authorization": f"token {os.getenv('GITHUB_TOKEN')}"}
    
    # Use Accept header to get diff format instead of JSON
    diff_headers = headers.copy()
    diff_headers['Accept'] = 'application/vnd.github.v3.diff'
    response = requests.get(diff_url, headers=diff_headers)
    if response.status_code == 200:
        diff_content = response.text
        print(f"✅ Diff fetched successfully ({len(diff_content)} characters)")
        
        # Print the first 1000 characters to see the format
        print("\n📝 First 1000 characters of diff:")
        print("=" * 50)
        print(diff_content[:1000])
        print("=" * 50)
        
        # Look for diff markers
        lines = diff_content.split('\n')
        print(f"\n🔍 Analyzing {len(lines)} lines...")
        
        # Find all diff markers
        diff_markers = []
        for i, line in enumerate(lines):
            if line.startswith('diff --git'):
                diff_markers.append((i, line))
        
        print(f"\n📁 Found {len(diff_markers)} diff markers:")
        for i, (line_num, marker) in enumerate(diff_markers, 1):
            print(f"   {i}. Line {line_num}: {marker}")
        
        # Test the extraction for the first file
        if diff_markers:
            first_marker = diff_markers[0][1]
            print(f"\n🔍 Testing extraction for first file...")
            print(f"   Marker: {first_marker}")
            
            # Extract the filename from the marker
            # Format: diff --git a/filename b/filename
            parts = first_marker.split()
            if len(parts) >= 3:
                filename_a = parts[2].replace('a/', '')
                filename_b = parts[3].replace('b/', '')
                print(f"   Filename A: {filename_a}")
                print(f"   Filename B: {filename_b}")
                
                # Test the current extraction method
                from agent.github_code_reviewer import GitHubCodeReviewer
                reviewer = GitHubCodeReviewer()
                
                file_diff = reviewer._extract_file_diff(diff_content, filename_a)
                if file_diff:
                    print(f"   ✅ Extraction successful ({len(file_diff)} characters)")
                    print(f"   📝 First 200 characters:")
                    print(file_diff[:200])
                else:
                    print(f"   ❌ Extraction failed")
                    
                    # Let's see what's happening
                    print(f"   🔍 Looking for the file in the diff...")
                    found_marker = False
                    for i, line in enumerate(lines):
                        if line.startswith(f'diff --git a/{filename_a} b/{filename_a}'):
                            found_marker = True
                            print(f"      Found marker at line {i}: {line}")
                            break
                    
                    if not found_marker:
                        print(f"      ❌ Marker not found in diff")
                        # Look for similar patterns
                        for i, line in enumerate(lines):
                            if 'diff --git' in line and filename_a in line:
                                print(f"      Found similar at line {i}: {line}")
                                break
    else:
        print(f"❌ Failed to fetch diff: {response.status_code}")

if __name__ == "__main__":
    examine_diff_content() 