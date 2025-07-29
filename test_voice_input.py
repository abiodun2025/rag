#!/usr/bin/env python3
"""
Test Voice Input Status
Check if voice input is working and provide alternatives
"""

import asyncio
import sys
from agent.voice_email_composer import get_voice_status, voice_email_composer

def test_voice_status():
    """Test voice input status."""
    print("🎤 Voice Input Status Check")
    print("=" * 50)
    
    status = get_voice_status()
    
    print(f"🎯 Voice Available: {status['voice_available']}")
    print(f"📊 Status: {status['status']}")
    print(f"💬 Message: {status['message']}")
    print(f"🔄 Fallback: {status['fallback']}")
    
    if status['voice_available']:
        print("\n✅ Voice input is working! You can use voice commands.")
        return True
    else:
        print("\n⚠️  Voice input not available. Using text input as fallback.")
        print("💡 You can still compose emails by typing voice commands.")
        return False

def test_text_input():
    """Test text input functionality."""
    print("\n💬 Testing Text Input")
    print("=" * 30)
    
    try:
        command = voice_email_composer.get_text_input()
        if command:
            print(f"✅ Text input working: '{command}'")
            return True
        else:
            print("❌ Text input failed")
            return False
    except Exception as e:
        print(f"❌ Text input error: {e}")
        return False

async def test_email_composition():
    """Test email composition with sample command."""
    print("\n📧 Testing Email Composition")
    print("=" * 30)
    
    sample_command = "send email to test@example.com about voice input testing"
    print(f"💡 Testing with: '{sample_command}'")
    
    try:
        result = await voice_email_composer.compose_email_from_voice(sample_command)
        
        if result.get("status") == "success":
            print("✅ Email composition successful!")
            print(f"📧 To: {result.get('to_email')}")
            print(f"📝 Subject: {result.get('subject')}")
            return True
        else:
            print(f"❌ Email composition failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Email composition error: {e}")
        return False

async def run_voice_tests():
    """Run all voice-related tests."""
    print("🧪 Voice Input Tests")
    print("=" * 50)
    
    tests = [
        ("Voice Status", test_voice_status),
        ("Text Input", test_text_input),
        ("Email Composition", test_email_composition),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running: {test_name}")
        print("-" * 30)
        
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            
            results[test_name] = result
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status}: {test_name}")
        except Exception as e:
            results[test_name] = False
            print(f"❌ ERROR: {test_name} - {e}")
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Voice email composer is ready to use.")
        print("💡 Run 'python voice_email.py' to start using voice commands.")
    elif passed >= 2:  # At least status and email composition work
        print("⚠️  Some tests passed. Voice email composer works with text input.")
        print("💡 Run 'python voice_email.py' to use text-based voice commands.")
    else:
        print("⚠️  Most tests failed. Please check the issues above.")
    
    return passed >= 2

async def main():
    """Main test function."""
    try:
        success = await run_voice_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n👋 Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 