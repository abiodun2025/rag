#!/usr/bin/env python3
"""
Simple Email CLI - Send emails using LLM-powered composition
============================================================

Usage: python email.py "your email request"

Examples:
  python email.py "send email to john@company.com asking about the quarterly report"
  python email.py "email sarah@gmail.com about the meeting tomorrow"
  python email.py "write urgent email to support@service.com about system outage"
"""

import asyncio
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def send_email():
    """Send email using dynamic composer."""
    if len(sys.argv) < 2 or sys.argv[1] in ['--help', '-h', 'help']:
        print("🚀 Dynamic Email Composer - Terminal Usage")
        print("=" * 50)
        print("Usage: python3 compose_email.py 'your email request'")
        print("\n📝 Examples:")
        print("  python3 compose_email.py 'send email to john@company.com asking about the quarterly report'")
        print("  python3 compose_email.py 'email sarah@gmail.com about the meeting tomorrow'")
        print("  python3 compose_email.py 'write urgent email to support@service.com about system outage'")
        print("  python3 compose_email.py 'send casual email to friend@gmail.com about weekend plans'")
        print("\n🎭 Supported Tones:")
        print("  • Professional (default)")
        print("  • Casual")
        print("  • Formal") 
        print("  • Friendly")
        print("  • Urgent")
        print("\n⚡ Urgency Levels:")
        print("  • Low (when convenient)")
        print("  • Normal (default)")
        print("  • High (urgent, asap)")
        return
    
    # Get the email request from command line arguments
    message = " ".join(sys.argv[1:])
    
    print("🚀 Dynamic Email Composer")
    print("=" * 50)
    print(f"📧 Processing: {message}")
    print("⏳ Composing email with LLM...")
    
    try:
        from agent.dynamic_email_composer import analyze_and_compose_email
        
        result = await analyze_and_compose_email(message)
        
        if result.get("status") == "success":
            print("\n✅ Email composed and sent successfully!")
            print("=" * 50)
            print(f"📧 To: {result.get('to_email')}")
            print(f"📝 Subject: {result.get('subject')}")
            print(f"📄 Body Preview: {result.get('body_preview')}")
            print(f"🎭 Tone: {result.get('tone')}")
            print(f"⚡ Urgency: {result.get('urgency')}")
            print(f"🕒 Sent at: {result.get('composed_at')}")
            print("=" * 50)
            print("🎉 Email sent via MCP tools!")
        else:
            print(f"\n❌ Failed to send email: {result.get('error')}")
            print("💡 Make sure to include a valid email address in your request.")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("💡 Check that your email request includes a valid email address.")

if __name__ == "__main__":
    asyncio.run(send_email()) 