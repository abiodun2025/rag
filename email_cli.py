#!/usr/bin/env python3
"""Simple CLI for dynamic email composition."""

import asyncio
import sys
from agent.dynamic_email_composer import analyze_and_compose_email

async def main():
    if len(sys.argv) < 2:
        print("Usage: python email_cli.py 'your email request'")
        print("Example: python email_cli.py 'send email to test@example.com asking about project status'")
        return
    
    message = " ".join(sys.argv[1:])
    print(f"📧 Processing: {message}")
    
    try:
        result = await analyze_and_compose_email(message)
        if result.get("status") == "success":
            print("✅ Email sent successfully!")
            print(f"📧 To: {result.get('to_email')}")
            print(f"📝 Subject: {result.get('subject')}")
            print(f"📄 Body: {result.get('body_preview')}")
        else:
            print(f"❌ Failed: {result.get('error')}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 