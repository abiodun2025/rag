#!/usr/bin/env python3
"""
Voice Email Composer CLI
Use voice commands to compose and send emails
"""

import asyncio
import sys
from agent.voice_email_composer import start_voice_email_session

async def main():
    """Main function to start voice email session."""
    try:
        await start_voice_email_session()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("🎤 Voice Email Composer")
    print("=" * 50)
    print("📧 Compose emails using voice commands!")
    print("🎯 Speak naturally and the AI will compose your email")
    print("=" * 50)
    
    asyncio.run(main()) 