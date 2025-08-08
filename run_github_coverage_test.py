#!/usr/bin/env python3
"""
Simple runner for GitHub Coverage Test
Sets up environment and runs comprehensive tests.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_requirements():
    """Check if required packages are installed."""
    print("🔍 Checking requirements...")
    
    required_packages = ['requests', 'coverage']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} is installed")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} is missing")
    
    if missing_packages:
        print(f"\n📦 Installing missing packages: {', '.join(missing_packages)}")
        for package in missing_packages:
            try:
                subprocess.run([sys.executable, '-m', 'pip', 'install', package], check=True)
                print(f"✅ Installed {package}")
            except subprocess.CalledProcessError:
                print(f"❌ Failed to install {package}")
                return False
    
    return True

def check_environment():
    """Check environment variables."""
    print("\n🔍 Checking environment variables...")
    
    token = os.getenv('GITHUB_TOKEN')
    owner = os.getenv('GITHUB_OWNER')
    repo = os.getenv('GITHUB_REPO')
    
    if not token:
        print("❌ GITHUB_TOKEN not set")
        print("💡 Set it with: export GITHUB_TOKEN='your_token'")
        return False
    
    if not owner:
        print("⚠️ GITHUB_OWNER not set, using default: abiodun2025")
        os.environ['GITHUB_OWNER'] = 'abiodun2025'
    
    if not repo:
        print("⚠️ GITHUB_REPO not set, using default: rag")
        os.environ['GITHUB_REPO'] = 'rag'
    
    print("✅ Environment variables configured")
    return True

def run_test():
    """Run the comprehensive test."""
    print("\n🚀 Running Comprehensive GitHub Coverage Test...")
    print("=" * 60)
    
    try:
        # Import and run the test
        from comprehensive_github_coverage_test import ComprehensiveGitHubCoverageTest
        
        test_suite = ComprehensiveGitHubCoverageTest()
        test_suite.run_all_tests()
        
        return True
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        return False

def main():
    """Main function."""
    print("🚀 GitHub Coverage Test Runner")
    print("=" * 40)
    
    # Check requirements
    if not check_requirements():
        print("❌ Requirements check failed")
        return 1
    
    # Check environment
    if not check_environment():
        print("❌ Environment check failed")
        return 1
    
    # Run test
    if not run_test():
        print("❌ Test execution failed")
        return 1
    
    print("\n🎉 Test runner completed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
