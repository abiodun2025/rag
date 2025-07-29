#!/usr/bin/env python3
"""
Dynamic Email Composer Demo
===========================

This script demonstrates how to use the LLM-powered dynamic email composer
to handle any email request with automatic content generation.
"""

import asyncio
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.dynamic_email_composer import analyze_and_compose_email
from agent.smart_master_agent import SmartMasterAgent

class DynamicEmailDemo:
    """Demonstrate dynamic email composition capabilities."""
    
    def __init__(self):
        self.smart_agent = SmartMasterAgent()
        self.session_id = f"demo_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.user_id = "demo_user"
    
    async def demo_simple_email(self):
        """Demonstrate simple email composition."""
        print("📧 Demo 1: Simple Email Request")
        print("-" * 40)
        
        message = "send email to john@company.com asking about the quarterly report"
        print(f"User: {message}")
        
        try:
            result = await analyze_and_compose_email(message)
            
            if result.get("status") == "success":
                print("✅ Email composed and sent successfully!")
                print(f"📧 To: {result.get('to_email')}")
                print(f"📝 Subject: {result.get('subject')}")
                print(f"📄 Body Preview: {result.get('body_preview')}")
                print(f"🎭 Tone: {result.get('tone')}")
                print(f"⚡ Urgency: {result.get('urgency')}")
            else:
                print(f"❌ Failed: {result.get('error')}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    async def demo_smart_agent_email(self):
        """Demonstrate email through smart master agent."""
        print("\n🤖 Demo 2: Smart Agent Email Handling")
        print("-" * 40)
        
        message = "compose a professional email to sarah@gmail.com asking to schedule a meeting next week"
        print(f"User: {message}")
        
        try:
            result = await self.smart_agent.process_message(message, self.session_id, self.user_id)
            
            print(f"🤖 Agent Response: {result.get('response', 'No response')}")
            print(f"🎯 Action: {result.get('action', 'Unknown')}")
            
            if result.get('action') == 'email_sent':
                details = result.get('details', {})
                print(f"✅ Email sent successfully!")
                print(f"📧 To: {details.get('recipient')}")
                print(f"📝 Subject: {details.get('subject')}")
                print(f"🎭 Tone: {details.get('tone')}")
                print(f"⚡ Urgency: {details.get('urgency')}")
            else:
                print(f"❌ Email action failed: {result.get('note', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    async def demo_different_tones(self):
        """Demonstrate different email tones."""
        print("\n🎭 Demo 3: Different Email Tones")
        print("-" * 40)
        
        tone_examples = [
            {
                "tone": "professional",
                "message": "send professional email to client@business.com about project timeline"
            },
            {
                "tone": "casual", 
                "message": "send casual email to friend@gmail.com about weekend plans"
            },
            {
                "tone": "urgent",
                "message": "send urgent email to support@service.com about system outage"
            }
        ]
        
        for example in tone_examples:
            print(f"\n🎭 {example['tone'].title()} Tone:")
            print(f"User: {example['message']}")
            
            try:
                result = await analyze_and_compose_email(example['message'])
                
                if result.get("status") == "success":
                    print(f"✅ {example['tone'].title()} email composed!")
                    print(f"📝 Subject: {result.get('subject')}")
                    print(f"📄 Preview: {result.get('body_preview')}")
                else:
                    print(f"❌ Failed: {result.get('error')}")
                    
            except Exception as e:
                print(f"❌ Error: {e}")
    
    async def demo_complex_scenarios(self):
        """Demonstrate complex email scenarios."""
        print("\n🎯 Demo 4: Complex Email Scenarios")
        print("-" * 40)
        
        complex_scenarios = [
            {
                "name": "Multi-topic Business Email",
                "message": "send email to manager@company.com covering quarterly results, team updates, and budget requests"
            },
            {
                "name": "Apology Email",
                "message": "write apology email to client@business.com for missing the deadline"
            },
            {
                "name": "Thank You Email",
                "message": "send thank you email to mentor@career.com for their guidance"
            }
        ]
        
        for scenario in complex_scenarios:
            print(f"\n🎯 {scenario['name']}:")
            print(f"User: {scenario['message']}")
            
            try:
                result = await analyze_and_compose_email(scenario['message'])
                
                if result.get("status") == "success":
                    print(f"✅ Complex scenario handled!")
                    print(f"📝 Subject: {result.get('subject')}")
                    print(f"📄 Preview: {result.get('body_preview')}")
                    print(f"🎭 Tone: {result.get('tone')}")
                else:
                    print(f"❌ Failed: {result.get('error')}")
                    
            except Exception as e:
                print(f"❌ Error: {e}")
    
    async def run_demo(self):
        """Run the complete dynamic email demo."""
        print("🚀 Dynamic Email Composer Demo")
        print("=" * 60)
        print(f"🕒 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        try:
            await self.demo_simple_email()
            await self.demo_smart_agent_email()
            await self.demo_different_tones()
            await self.demo_complex_scenarios()
            
            print("\n🎉 Demo Completed Successfully!")
            print("=" * 60)
            print("✨ Your agent can now handle any email request with LLM-powered content generation!")
            print("📧 Just say: 'send email to [address] [your request]'")
            print("=" * 60)
            
        except Exception as e:
            print(f"\n❌ Demo failed: {e}")
            raise

async def main():
    """Main demo function."""
    demo = DynamicEmailDemo()
    await demo.run_demo()

if __name__ == "__main__":
    asyncio.run(main()) 