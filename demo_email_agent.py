#!/usr/bin/env python3
"""
Email Agent Demo - Show how the agent handles any email request
===============================================================

This script demonstrates the agent's ability to handle any type of email request
with automatic intent detection, email extraction, and composition.
"""

import asyncio
import os
import sys
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.smart_master_agent import SmartMasterAgent

class EmailAgentDemo:
    """Demonstrate email agent capabilities."""
    
    def __init__(self):
        self.smart_agent = SmartMasterAgent()
        self.session_id = f"demo_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.user_id = "demo_user"
    
    async def demo_email_requests(self):
        """Demonstrate various email request scenarios."""
        print("📧 EMAIL AGENT DEMONSTRATION")
        print("=" * 60)
        print("The agent can handle ANY email request automatically!\n")
        
        # Example email requests
        examples = [
            "send email to john@gmail.com",
            "email sarah@company.com about the meeting tomorrow",
            "write an email to client@business.org asking for proposal review",
            "compose email to team@startup.io regarding the new feature launch",
            "urgently email emergency@hospital.com about patient transfer",
            "send a friendly email to grandma@family.com telling her about my new job",
            "email dev@tech.com about the API integration - we're getting 500 errors",
            "compose email to investor@venture.com regarding Series A funding",
            "email team@project.com about sprint planning - please prepare updates",
            "send email to manager@work.com regarding project update - discuss timeline"
        ]
        
        print("🎯 EXAMPLE EMAIL REQUESTS THE AGENT CAN HANDLE:")
        for i, example in enumerate(examples, 1):
            print(f"{i:2d}. '{example}'")
        
        print(f"\n✨ FEATURES:")
        print("✅ Automatic intent detection")
        print("✅ Email address extraction")
        print("✅ Subject and body composition")
        print("✅ Natural language processing")
        print("✅ Professional email formatting")
        print("✅ MCP integration for sending")
        
        print(f"\n🚀 HOW IT WORKS:")
        print("1. You type any email request in natural language")
        print("2. Agent automatically detects it's an email request")
        print("3. Agent extracts email address, subject, and body")
        print("4. Agent composes a professional email")
        print("5. Agent sends the email via MCP tools")
        
        return examples
    
    async def interactive_demo(self):
        """Interactive demo where user can test email requests."""
        print(f"\n🎮 INTERACTIVE DEMO")
        print("=" * 60)
        print("Try your own email requests! Type 'quit' to exit.\n")
        
        while True:
            try:
                # Get user input
                user_input = input("📝 Enter your email request: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 Thanks for trying the email agent!")
                    break
                
                if not user_input:
                    print("❌ Please enter a valid email request.")
                    continue
                
                print(f"\n🔍 Processing: '{user_input}'")
                
                # Analyze intent
                intent_result = self.smart_agent.analyze_intent(user_input)
                print(f"🎯 Detected Intent: {intent_result.intent.value} (confidence: {intent_result.confidence:.2f})")
                
                if intent_result.intent.value == "email":
                    # Extract data
                    extracted_data = intent_result.extracted_data
                    print(f"📊 Extracted Data:")
                    print(f"   📧 To: {extracted_data.get('to_email', 'Not found')}")
                    print(f"   📋 Subject: {extracted_data.get('subject', 'Not found')}")
                    print(f"   📝 Body: {extracted_data.get('body', 'Not found')}")
                    
                    # Process with smart agent
                    print(f"\n🚀 Processing with Smart Agent...")
                    result = await self.smart_agent.process_message(
                        message=user_input,
                        session_id=self.session_id,
                        user_id=self.user_id
                    )
                    
                    print(f"📊 Result:")
                    print(f"   Action: {result.get('action', 'unknown')}")
                    print(f"   Note: {result.get('note', 'No note')}")
                    
                    if result.get('action') == 'email_sent':
                        print(f"   ✅ Email sent successfully!")
                        print(f"   📧 Recipient: {result.get('to_email')}")
                        print(f"   📋 Subject: {result.get('subject')}")
                        print(f"   📝 Body Preview: {result.get('body_preview', 'No body')}")
                    else:
                        print(f"   ❌ Email not sent: {result.get('error', 'Unknown error')}")
                        print(f"   💡 Note: This is expected if MCP server is not running")
                else:
                    print(f"❌ Not detected as email request. Detected as: {intent_result.intent.value}")
                    print(f"💡 Try including an email address in your request")
                
                print("-" * 60)
                
            except KeyboardInterrupt:
                print(f"\n👋 Demo interrupted. Thanks for trying!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                print("💡 Try a different email request")
    
    async def show_capabilities(self):
        """Show the agent's email capabilities."""
        print(f"\n🔧 AGENT CAPABILITIES")
        print("=" * 60)
        
        capabilities = [
            "🎯 Intent Detection: Automatically identifies email requests",
            "📧 Email Extraction: Finds email addresses in any format",
            "📋 Subject Generation: Creates appropriate subjects from context",
            "📝 Body Composition: Writes professional email content",
            "🌐 Domain Support: Works with any email domain (.com, .org, .io, etc.)",
            "💼 Business Context: Handles professional and personal emails",
            "🚨 Urgency Detection: Recognizes urgent requests",
            "👥 Multiple Recipients: Can handle multiple email addresses",
            "🔧 Technical Content: Processes technical and business content",
            "🎨 Natural Language: Understands conversational requests"
        ]
        
        for capability in capabilities:
            print(f"   {capability}")
        
        print(f"\n📚 SUPPORTED PATTERNS:")
        patterns = [
            "send email to [address]",
            "email [address] about [topic]",
            "write an email to [address] asking [request]",
            "compose email to [address] regarding [subject]",
            "urgently email [address] about [urgent matter]",
            "send a friendly email to [address] telling [content]",
            "email [address] about [technical issue]",
            "compose email to [address] regarding [business matter]"
        ]
        
        for pattern in patterns:
            print(f"   • {pattern}")

async def main():
    """Main demonstration function."""
    demo = EmailAgentDemo()
    
    # Show capabilities
    await demo.show_capabilities()
    
    # Show example requests
    await demo.demo_email_requests()
    
    # Interactive demo
    await demo.interactive_demo()
    
    print(f"\n🎉 DEMONSTRATION COMPLETE!")
    print("=" * 60)
    print("The agent is ready to handle any email request!")
    print("Just type naturally and the agent will do the rest.")

if __name__ == "__main__":
    asyncio.run(main()) 