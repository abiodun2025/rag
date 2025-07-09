#!/usr/bin/env python3
"""
Gmail API Credentials Setup Script
==================================

This script helps you set up Gmail API credentials for the email agent.

Steps:
1. Go to https://console.cloud.google.com/
2. Create a new project or select existing one
3. Enable Gmail API
4. Create credentials (OAuth 2.0 Client ID)
5. Download credentials.json and place it in this directory
"""

import os
import sys

def check_credentials():
    """Check if credentials.json exists."""
    if os.path.exists('credentials.json'):
        print("✅ credentials.json found!")
        return True
    else:
        print("❌ credentials.json not found!")
        print("\nTo get credentials.json:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Create a new project or select existing one")
        print("3. Enable Gmail API (APIs & Services > Library > Gmail API)")
        print("4. Create credentials (APIs & Services > Credentials > Create Credentials > OAuth 2.0 Client ID)")
        print("5. Download the JSON file and rename it to 'credentials.json'")
        print("6. Place it in this directory")
        return False

def test_gmail_connection():
    """Test Gmail API connection."""
    try:
        from agent.email_tools import get_gmail_service
        service = get_gmail_service()
        print("✅ Gmail API connection successful!")
        return True
    except Exception as e:
        print(f"❌ Gmail API connection failed: {e}")
        return False

if __name__ == "__main__":
    print("Gmail API Credentials Setup")
    print("=" * 30)
    
    if check_credentials():
        print("\nTesting Gmail API connection...")
        test_gmail_connection()
    else:
        print("\nPlease follow the instructions above to get credentials.json") 