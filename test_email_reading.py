#!/usr/bin/env python3
"""
Test script for email reading functionality.
This script demonstrates how to use the new email reading tools.
"""

import asyncio
import json
import sys
import os
from typing import Dict, Any

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.email_tools import list_emails, read_email, search_emails, compose_email

def print_separator(title: str):
    """Print a formatted separator with title"""
    print("\n" + "="*60)
    print(f"🧪 {title}")
    print("="*60)

def print_email_summary(email_data: Dict[str, Any], index: int = None):
    """Print a formatted email summary"""
    prefix = f"{index}. " if index is not None else ""
    print(f"\n{prefix}📧 Email ID: {email_data['id']}")
    print(f"   From: {email_data.get('from', 'N/A')}")
    print(f"   Subject: {email_data.get('subject', 'N/A')}")
    print(f"   Date: {email_data.get('date', 'N/A')}")
    print(f"   Snippet: {email_data.get('snippet', 'N/A')[:100]}...")
    print(f"   Labels: {', '.join(email_data.get('labels', []))}")

def print_email_full(email_data: Dict[str, Any]):
    """Print full email content"""
    print(f"\n📧 Email ID: {email_data['id']}")
    print(f"From: {email_data.get('from', 'N/A')}")
    print(f"To: {email_data.get('to', 'N/A')}")
    print(f"Subject: {email_data.get('subject', 'N/A')}")
    print(f"Date: {email_data.get('date', 'N/A')}")
    print(f"Labels: {', '.join(email_data.get('labels', []))}")
    print(f"\nBody:\n{email_data.get('body', 'No body content')}")

async def test_list_emails():
    """Test listing recent emails"""
    print_separator("Testing List Emails")
    
    try:
        print("📋 Listing recent emails from inbox...")
        result = list_emails(max_results=5)
        
        if result['status'] == 'success':
            emails = result['emails']
            print(f"✅ Found {len(emails)} emails")
            
            for i, email_data in enumerate(emails, 1):
                print_email_summary(email_data, i)
                
            return emails
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
            return []
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return []

async def test_search_emails():
    """Test searching emails"""
    print_separator("Testing Email Search")
    
    try:
        # Test different search queries
        search_queries = [
            "is:unread",
            "from:gmail.com",
            "subject:test",
            "newer_than:1d"
        ]
        
        for query in search_queries:
            print(f"\n🔍 Searching for: '{query}'")
            result = search_emails(query=query, max_results=3)
            
            if result['status'] == 'success':
                emails = result['emails']
                print(f"✅ Found {len(emails)} emails matching '{query}'")
                
                for i, email_data in enumerate(emails, 1):
                    print_email_summary(email_data, i)
            else:
                print(f"❌ Error: {result.get('error', 'Unknown error')}")
                
    except Exception as e:
        print(f"❌ Exception: {e}")

async def test_read_email(email_id: str):
    """Test reading a specific email"""
    print_separator(f"Testing Read Email (ID: {email_id})")
    
    try:
        print(f"📖 Reading email with ID: {email_id}")
        result = read_email(email_id=email_id)
        
        if result['status'] == 'success':
            email_data = result['email']
            print_email_full(email_data)
            return email_data
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

async def test_compose_email():
    """Test composing and sending an email"""
    print_separator("Testing Email Composition")
    
    try:
        print("📝 Composing test email...")
        result = compose_email(
            to="test@example.com",
            subject="Test Email from Agent",
            body="This is a test email sent from the agent's email reading functionality."
        )
        
        if result['status'] == 'sent':
            print(f"✅ Email sent successfully!")
            print(f"   Message ID: {result.get('message_id')}")
            print(f"   Thread ID: {result.get('thread_id')}")
            return result
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

async def main():
    """Main test function"""
    print("🚀 Email Reading Functionality Test")
    print("="*60)
    
    # Check if credentials exist
    if not os.path.exists('credentials.json'):
        print("❌ credentials.json not found!")
        print("Please download your Gmail API credentials from Google Cloud Console")
        print("and place them in the project root directory.")
        return
    
    print("✅ credentials.json found")
    
    # Test 1: List recent emails
    emails = await test_list_emails()
    
    # Test 2: Search emails
    await test_search_emails()
    
    # Test 3: Read a specific email (if we have any)
    if emails:
        first_email_id = emails[0]['id']
        await test_read_email(first_email_id)
    else:
        print("\n⚠️  No emails found to read. Make sure you have emails in your inbox.")
    
    # Test 4: Compose email (optional - uncomment to test)
    # await test_compose_email()
    
    print("\n" + "="*60)
    print("✅ Email reading functionality test completed!")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main()) 