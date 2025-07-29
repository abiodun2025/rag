#!/usr/bin/env python3
"""
Dynamic Email CLI - Command Line Interface for LLM-Powered Email Composition
============================================================================

This script provides a simple command-line interface for composing emails
using the LLM-powered dynamic email composer.
"""

import asyncio
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.dynamic_email_composer import analyze_and_compose_email, compose_dynamic_email

class DynamicEmailCLI:
    """Command-line interface for dynamic email composition."""
    
    def __init__(self):
        self.session_id = f"cli_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    async def compose_email_interactive(self):
        """Interactive email composition."""
        print("🚀 Dynamic Email Composer CLI")
        print("=" * 50)
        print("📧 Compose emails using LLM-powered content generation!")
        print("💡 Just describe what you want to email and to whom.")
        print("🔧 Type 'help' for commands, 'quit' to exit.")
        print("=" * 50)
        
        while True:
            try:
                user_input = input("\n📝 Enter your email request: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                if user_input.lower() == 'help':
                    self.show_help()
                    continue
                
                if not user_input:
                    print("❌ Please enter a valid email request.")
                    continue
                
                print(f"\n🤖 Processing: {user_input}")
                print("⏳ Composing email with LLM...")
                
                result = await analyze_and_compose_email(user_input)
                
                if result.get("status") == "success":
                    print("✅ Email composed and sent successfully!")
                    print(f"📧 To: {result.get('to_email')}")
                    print(f"📝 Subject: {result.get('subject')}")
                    print(f"📄 Body Preview: {result.get('body_preview')}")
                    print(f"🎭 Tone: {result.get('tone')}")
                    print(f"⚡ Urgency: {result.get('urgency')}")
                    print(f"🕒 Sent at: {result.get('composed_at')}")
                else:
                    print(f"❌ Failed to compose email: {result.get('error')}")
                    print(f"💡 Tip: Make sure to include a valid email address in your request.")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def show_help(self):
        """Show help information."""
        print("\n📚 HELP - Dynamic Email Composer")
        print("-" * 40)
        print("💡 Just type your email request naturally!")
        print("\n📝 Examples:")
        print("• send email to john@company.com asking about the meeting")
        print("• email sarah@gmail.com about the project status")
        print("• write urgent email to support@service.com about system outage")
        print("• compose casual email to friend@email.com about weekend plans")
        print("• send formal email to client@business.com regarding proposal")
        print("\n🎭 Supported Tones:")
        print("• professional (default)")
        print("• casual")
        print("• formal")
        print("• friendly")
        print("• urgent")
        print("\n⚡ Urgency Levels:")
        print("• low")
        print("• normal (default)")
        print("• high")
        print("\n🔧 Commands:")
        print("• help - Show this help")
        print("• quit/exit/q - Exit the program")
    
    async def compose_email_direct(self, to_email: str, context: str, tone: str = "professional", urgency: str = "normal"):
        """Compose email with direct parameters."""
        try:
            result = await compose_dynamic_email(
                to_email=to_email,
                context=context,
                tone=tone,
                urgency=urgency
            )
            
            if result.get("status") == "success":
                print("✅ Email composed and sent successfully!")
                print(f"📧 To: {result.get('to_email')}")
                print(f"📝 Subject: {result.get('subject')}")
                print(f"📄 Body Preview: {result.get('body_preview')}")
                print(f"🎭 Tone: {result.get('tone')}")
                print(f"⚡ Urgency: {result.get('urgency')}")
                return result
            else:
                print(f"❌ Failed to compose email: {result.get('error')}")
                return result
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return {"status": "error", "error": str(e)}

async def main():
    """Main CLI function."""
    cli = DynamicEmailCLI()
    
    # Check if arguments were provided
    if len(sys.argv) > 1:
        if sys.argv[1] == "--help" or sys.argv[1] == "-h":
            cli.show_help()
            return
        
        # Direct email composition
        if len(sys.argv) >= 3:
            to_email = sys.argv[1]
            context = sys.argv[2]
            tone = sys.argv[3] if len(sys.argv) > 3 else "professional"
            urgency = sys.argv[4] if len(sys.argv) > 4 else "normal"
            
            print(f"📧 Composing email to {to_email}")
            print(f"📝 Context: {context}")
            print(f"🎭 Tone: {tone}")
            print(f"⚡ Urgency: {urgency}")
            print("-" * 40)
            
            await cli.compose_email_direct(to_email, context, tone, urgency)
        else:
            print("❌ Usage: python dynamic_email_cli.py <email> <context> [tone] [urgency]")
            print("💡 Or run without arguments for interactive mode.")
    else:
        # Interactive mode
        await cli.compose_email_interactive()

if __name__ == "__main__":
    asyncio.run(main()) 