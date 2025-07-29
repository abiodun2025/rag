#!/usr/bin/env python3
"""
Test Dynamic Email Composer - LLM-Powered Email Generation
==========================================================

This script demonstrates the dynamic email composition functionality
using LLM to generate professional email content based on user requests.
"""

import asyncio
import os
import sys
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.dynamic_email_composer import (
    DynamicEmailComposer, 
    EmailRequest, 
    compose_dynamic_email, 
    analyze_and_compose_email
)

class DynamicEmailTester:
    """Test various dynamic email composition scenarios."""
    
    def __init__(self):
        self.composer = DynamicEmailComposer()
        self.test_scenarios = [
            {
                "name": "Professional Meeting Request",
                "message": "send email to john.doe@company.com asking to schedule a meeting next week to discuss the quarterly report",
                "expected_tone": "professional",
                "expected_purpose": "Meeting coordination"
            },
            {
                "name": "Casual Follow-up",
                "message": "send a casual email to sarah@gmail.com following up on our coffee chat yesterday",
                "expected_tone": "casual",
                "expected_purpose": "Follow up"
            },
            {
                "name": "Formal Business Inquiry",
                "message": "compose a formal email to ceo@startup.com asking about potential partnership opportunities",
                "expected_tone": "formal",
                "expected_purpose": "Question or inquiry"
            },
            {
                "name": "Urgent Issue",
                "message": "send urgent email to support@service.com about critical system outage affecting our production",
                "expected_tone": "urgent",
                "expected_purpose": "General communication"
            },
            {
                "name": "Friendly Thank You",
                "message": "write a friendly thank you email to mentor@career.com for their guidance on my project",
                "expected_tone": "friendly",
                "expected_purpose": "Thank you"
            },
            {
                "name": "Apology Email",
                "message": "send apology email to client@business.com for missing the deadline on the project",
                "expected_tone": "professional",
                "expected_purpose": "Apology"
            }
        ]
    
    async def test_email_request_analysis(self):
        """Test email request analysis functionality."""
        print("🔍 Testing Email Request Analysis...")
        print("=" * 50)
        
        for scenario in self.test_scenarios:
            print(f"\n📧 Testing: {scenario['name']}")
            print(f"Message: {scenario['message']}")
            
            try:
                request = await self.composer.analyze_email_request(scenario['message'])
                
                print(f"✅ Extracted Email: {request.to_email}")
                print(f"✅ Detected Tone: {request.tone}")
                print(f"✅ Detected Urgency: {request.urgency}")
                print(f"✅ Detected Purpose: {request.purpose}")
                
                # Validate expectations
                if request.tone == scenario['expected_tone']:
                    print(f"✅ Tone detection correct: {request.tone}")
                else:
                    print(f"⚠️  Tone detection mismatch: expected {scenario['expected_tone']}, got {request.tone}")
                
                if request.purpose == scenario['expected_purpose']:
                    print(f"✅ Purpose detection correct: {request.purpose}")
                else:
                    print(f"⚠️  Purpose detection mismatch: expected {scenario['expected_purpose']}, got {request.purpose}")
                
            except Exception as e:
                print(f"❌ Analysis failed: {e}")
        
        print("\n" + "=" * 50)
    
    async def test_dynamic_email_composition(self):
        """Test dynamic email composition with LLM."""
        print("\n🤖 Testing Dynamic Email Composition with LLM...")
        print("=" * 50)
        
        # Test with a simple scenario first
        test_message = "send email to test@example.com asking about the project status update"
        
        print(f"\n📧 Testing Composition: {test_message}")
        
        try:
            result = await analyze_and_compose_email(test_message)
            
            if result.get("status") == "success":
                print("✅ Email composition successful!")
                print(f"📧 To: {result.get('to_email')}")
                print(f"📝 Subject: {result.get('subject')}")
                print(f"📄 Body Preview: {result.get('body_preview')}")
                print(f"🎭 Tone: {result.get('tone')}")
                print(f"⚡ Urgency: {result.get('urgency')}")
                print(f"🕒 Composed at: {result.get('composed_at')}")
            else:
                print(f"❌ Email composition failed: {result.get('error')}")
                
        except Exception as e:
            print(f"❌ Composition test failed: {e}")
        
        print("\n" + "=" * 50)
    
    async def test_different_tones(self):
        """Test email composition with different tones."""
        print("\n🎭 Testing Different Email Tones...")
        print("=" * 50)
        
        tones = ["professional", "casual", "formal", "friendly", "urgent"]
        test_context = "asking about the quarterly report and next steps"
        
        for tone in tones:
            print(f"\n🎭 Testing {tone.upper()} tone...")
            
            try:
                result = await compose_dynamic_email(
                    to_email="test@example.com",
                    context=test_context,
                    tone=tone,
                    urgency="normal",
                    purpose="Question or inquiry"
                )
                
                if result.get("status") == "success":
                    print(f"✅ {tone.title()} email composed successfully!")
                    print(f"📝 Subject: {result.get('subject')}")
                    print(f"📄 Body Preview: {result.get('body_preview')}")
                else:
                    print(f"❌ {tone.title()} email failed: {result.get('error')}")
                    
            except Exception as e:
                print(f"❌ {tone.title()} tone test failed: {e}")
        
        print("\n" + "=" * 50)
    
    async def test_urgency_levels(self):
        """Test email composition with different urgency levels."""
        print("\n⚡ Testing Different Urgency Levels...")
        print("=" * 50)
        
        urgency_levels = ["low", "normal", "high"]
        test_context = "scheduling a follow-up meeting"
        
        for urgency in urgency_levels:
            print(f"\n⚡ Testing {urgency.upper()} urgency...")
            
            try:
                result = await compose_dynamic_email(
                    to_email="test@example.com",
                    context=test_context,
                    tone="professional",
                    urgency=urgency,
                    purpose="Meeting coordination"
                )
                
                if result.get("status") == "success":
                    print(f"✅ {urgency.title()} urgency email composed successfully!")
                    print(f"📝 Subject: {result.get('subject')}")
                    print(f"📄 Body Preview: {result.get('body_preview')}")
                else:
                    print(f"❌ {urgency.title()} urgency email failed: {result.get('error')}")
                    
            except Exception as e:
                print(f"❌ {urgency.title()} urgency test failed: {e}")
        
        print("\n" + "=" * 50)
    
    async def test_complex_scenarios(self):
        """Test complex email scenarios."""
        print("\n🎯 Testing Complex Email Scenarios...")
        print("=" * 50)
        
        complex_scenarios = [
            {
                "name": "Multi-topic Business Email",
                "message": "send professional email to manager@company.com covering quarterly results, team updates, and budget requests for next quarter",
                "expected_tone": "professional"
            },
            {
                "name": "Urgent Technical Issue",
                "message": "send urgent email to tech@company.com about critical database connection issues affecting all users",
                "expected_tone": "urgent"
            },
            {
                "name": "Friendly Networking",
                "message": "write friendly email to contact@network.com thanking them for the introduction and suggesting coffee meeting",
                "expected_tone": "friendly"
            }
        ]
        
        for scenario in complex_scenarios:
            print(f"\n🎯 Testing: {scenario['name']}")
            print(f"Message: {scenario['message']}")
            
            try:
                result = await analyze_and_compose_email(scenario['message'])
                
                if result.get("status") == "success":
                    print("✅ Complex scenario handled successfully!")
                    print(f"📧 To: {result.get('to_email')}")
                    print(f"📝 Subject: {result.get('subject')}")
                    print(f"📄 Body Preview: {result.get('body_preview')}")
                    print(f"🎭 Tone: {result.get('tone')}")
                else:
                    print(f"❌ Complex scenario failed: {result.get('error')}")
                    
            except Exception as e:
                print(f"❌ Complex scenario test failed: {e}")
        
        print("\n" + "=" * 50)
    
    async def run_all_tests(self):
        """Run all dynamic email composition tests."""
        print("🚀 Starting Dynamic Email Composer Tests")
        print("=" * 60)
        print(f"🕒 Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        try:
            # Test email request analysis
            await self.test_email_request_analysis()
            
            # Test dynamic email composition
            await self.test_dynamic_email_composition()
            
            # Test different tones
            await self.test_different_tones()
            
            # Test different urgency levels
            await self.test_urgency_levels()
            
            # Test complex scenarios
            await self.test_complex_scenarios()
            
            print("\n🎉 All Dynamic Email Composer Tests Completed!")
            print("=" * 60)
            print(f"🕒 Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("=" * 60)
            
        except Exception as e:
            print(f"\n❌ Test suite failed: {e}")
            raise

async def main():
    """Main test function."""
    tester = DynamicEmailTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main()) 