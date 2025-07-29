#!/usr/bin/env python3
"""
Voice Email Composer Demo
Demonstrates voice-to-email functionality with text input fallback
"""

import asyncio
import sys
from agent.dynamic_email_composer import analyze_and_compose_email

async def demo_voice_email():
    """Demo voice email composition with text input."""
    print("🎤 Voice Email Composer Demo")
    print("=" * 50)
    print("📧 This demo shows how voice-to-email would work")
    print("💡 For now, we'll use text input to simulate voice commands")
    print("🎯 The email composition and sending works perfectly!")
    print("=" * 50)
    
    # Sample voice commands (simulated)
    demo_commands = [
        "send email to john@company.com about the meeting tomorrow",
        "write urgent email to support@service.com about login issues",
        "compose formal email to client@business.com regarding the proposal",
        "send casual email to friend@gmail.com about weekend plans"
    ]
    
    print("\n💡 Demo Voice Commands:")
    for i, command in enumerate(demo_commands, 1):
        print(f"   {i}. '{command}'")
    
    print("\n" + "=" * 50)
    print("🎯 Let's simulate voice commands with text input")
    print("=" * 50)
    
    while True:
        try:
            print("\n💬 Enter a voice command (or 'demo' for examples, 'quit' to exit):")
            user_input = input("🎤 Voice Command: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            elif user_input.lower() == 'demo':
                print("\n💡 Demo Commands:")
                for i, command in enumerate(demo_commands, 1):
                    print(f"   {i}. '{command}'")
                continue
            elif not user_input:
                continue
            
            # Simulate voice processing
            print(f"🎤 Processing voice command: '{user_input}'")
            print("🔄 Converting speech to text...")
            print("🧠 Analyzing intent...")
            print("📧 Composing email...")
            
            # Process the command
            result = await analyze_and_compose_email(user_input)
            
            if result.get("status") == "success":
                print("\n✅ Email composed and sent successfully!")
                print(f"📧 To: {result.get('to_email')}")
                print(f"📝 Subject: {result.get('subject')}")
                print(f"📄 Body Preview: {result.get('body_preview', '')[:150]}...")
                print(f"🎯 Tone: {result.get('tone', 'professional')}")
                print(f"⚡ Urgency: {result.get('urgency', 'normal')}")
            else:
                print(f"\n❌ Failed to compose email: {result.get('error')}")
            
            # Ask if user wants to continue
            print("\n" + "=" * 50)
            continue_choice = input("🎤 Compose another email? (y/n): ").strip().lower()
            if continue_choice not in ['y', 'yes']:
                print("👋 Goodbye!")
                break
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

async def test_voice_commands():
    """Test various voice command patterns."""
    print("🧪 Testing Voice Command Patterns")
    print("=" * 50)
    
    test_commands = [
        # Simple commands
        "send email to test@example.com",
        "email user@gmail.com about the project",
        
        # Detailed commands
        "write urgent email to support@service.com about my account being locked",
        "compose formal email to ceo@company.com regarding the quarterly results",
        
        # Professional commands
        "send professional email to client@business.com about the contract renewal",
        "write business email to vendor@supplier.com regarding payment terms",
        
        # Casual commands
        "send casual email to friend@gmail.com about the weekend party",
        "compose friendly email to family@home.com about the vacation plans"
    ]
    
    results = []
    
    for i, command in enumerate(test_commands, 1):
        print(f"\n🔍 Test {i}/{len(test_commands)}: '{command}'")
        print("-" * 40)
        
        try:
            result = await analyze_and_compose_email(command)
            
            if result.get("status") == "success":
                print(f"✅ Success: {result.get('to_email')} - {result.get('subject')}")
                results.append(True)
            else:
                print(f"❌ Failed: {result.get('error')}")
                results.append(False)
                
        except Exception as e:
            print(f"❌ Error: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    print(f"🎯 Overall: {passed}/{total} voice commands processed successfully")
    
    if passed == total:
        print("🎉 All voice command patterns work perfectly!")
    elif passed >= total * 0.8:
        print("✅ Most voice command patterns work well!")
    else:
        print("⚠️  Some voice command patterns need improvement")
    
    return passed == total

async def main():
    """Main function."""
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        await test_voice_commands()
    else:
        await demo_voice_email()

if __name__ == "__main__":
    asyncio.run(main()) 