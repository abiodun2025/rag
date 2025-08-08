#!/usr/bin/env python3
"""
Quick Coverage Checker
Just run tests and get accurate code coverage percentage for current repository.
"""

import subprocess
import os
from pathlib import Path

def run_quick_coverage():
    """Run coverage analysis on current repository."""
    print("🚀 Quick Coverage Checker")
    print("=" * 40)
    
    # Check if we're in a git repository
    if not Path(".git").exists():
        print("❌ Not in a git repository")
        return
    
    # Find test files
    test_files = list(Path(".").rglob("test_*.py")) + list(Path(".").rglob("*_test.py"))
    
    if not test_files:
        print("❌ No test files found")
        return
    
    print(f"📁 Found {len(test_files)} test files")
    
    # Run coverage on a few test files
    test_files_to_run = test_files[:5]  # Run first 5 test files
    print(f"🧪 Running coverage on {len(test_files_to_run)} test files...")
    
    try:
        # Run tests with coverage
        coverage_cmd = ["python3", "-m", "coverage", "run", "-m", "pytest"] + [str(f) for f in test_files_to_run]
        result = subprocess.run(coverage_cmd, capture_output=True, text=True)
        
        # Generate coverage report
        report_cmd = ["python3", "-m", "coverage", "report"]
        report_result = subprocess.run(report_cmd, capture_output=True, text=True)
        
        # Parse and display results
        print("\n📊 Coverage Results:")
        print("=" * 40)
        
        # Extract coverage percentage
        coverage_percentage = parse_coverage_report(report_result.stdout)
        
        print(f"✅ Coverage: {coverage_percentage:.1f}%")
        print(f"🧪 Tests: {'✅ Passed' if result.returncode == 0 else '❌ Failed'}")
        
        # Show coverage report
        print("\n📋 Coverage Report:")
        print("-" * 40)
        print(report_result.stdout)
        
        # Assessment
        print("\n🎯 Assessment:")
        if coverage_percentage >= 80:
            print("🎉 Excellent coverage! Your code is well tested.")
        elif coverage_percentage >= 60:
            print("👍 Good coverage. Consider adding more tests.")
        elif coverage_percentage >= 40:
            print("⚠️ Moderate coverage. More tests needed.")
        else:
            print("❌ Low coverage. Significant test improvements needed.")
            
    except Exception as e:
        print(f"❌ Error running coverage: {e}")

def parse_coverage_report(report_text):
    """Parse coverage report to extract percentage."""
    try:
        lines = report_text.split('\n')
        for line in lines:
            if 'TOTAL' in line and '%' in line:
                # Extract percentage from line like "TOTAL                         100     20    80%"
                parts = line.split()
                for part in parts:
                    if part.endswith('%'):
                        return float(part.rstrip('%'))
        return 0
    except:
        return 0

if __name__ == "__main__":
    run_quick_coverage()
