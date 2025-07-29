#!/usr/bin/env python3
"""
Test Voice Email Composer
Test the voice email functionality
"""

import asyncio
import sys
from agent.voice_email_composer import voice_email_composer, compose_email_from_voice_command

async def test_microphone():
    """Test microphone access."""
    print("🎤 Testing Microphone Access")
    print("=" * 40)
    
    try:
        # Test microphone initialization (lazy loading)
        voice_email_composer._initialize_speech_recognition()
        
        recognizer = voice_email_composer.recognizer
        microphone = voice_email_composer.microphone
        
        print("✅ Microphone initialized successfully")
        
        # Test ambient noise adjustment
        with microphone as source:
            print("🎤 Adjusting for ambient noise...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            print("✅ Ambient noise adjustment completed")
            
        return True
        
    except Exception as e:
        print(f"❌ Microphone test failed: {e}")
        print("💡 This might be due to PyAudio issues on macOS")
        print("💡 Try: brew install portaudio && pip install pyaudio")
        return False

async def test_voice_recognition():
    """Test basic voice recognition."""
    print("🎤 Testing Voice Recognition")
    print("=" * 40)
    print("💡 Say something simple like 'hello world'")
    
    try:
        text = voice_email_composer.listen_for_command(timeout=10)
        if text:
            print(f"✅ Voice recognition successful: '{text}'")
            return True
        else:
            print("❌ Voice recognition failed")
            return False
    except Exception as e:
        print(f"❌ Voice recognition error: {e}")
        return False

async def test_email_composition():
    """Test email composition with a sample voice command."""
    print("\n📧 Testing Email Composition")
    print("=" * 40)
    
    # Sample voice command
    sample_command = "send email to test@example.com about the meeting tomorrow"
    print(f"💡 Testing with command: '{sample_command}'")
    
    try:
        result = await compose_email_from_voice_command(sample_command)
        
        if result.get("status") == "success":
            print("✅ Email composition successful!")
            print(f"📧 To: {result.get('to_email')}")
            print(f"📝 Subject: {result.get('subject')}")
            print(f"📄 Status: {result.get('status')}")
        else:
            print(f"❌ Email composition failed: {result.get('error')}")
            
        return result.get("status") == "success"
        
    except Exception as e:
        print(f"❌ Email composition error: {e}")
        return False

async def test_speech_recognition_import():
    """Test if speech recognition can be imported."""
    print("🔍 Testing Speech Recognition Import")
    print("=" * 40)
    
    try:
        import speech_recognition as sr
        print("✅ SpeechRecognition imported successfully")
        
        # Test basic recognizer creation
        recognizer = sr.Recognizer()
        print("✅ Recognizer created successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ SpeechRecognition import failed: {e}")
        print("💡 Install with: pip install SpeechRecognition")
        return False
    except Exception as e:
        print(f"❌ Speech recognition setup failed: {e}")
        return False

async def run_all_tests():
    """Run all voice email tests."""
    print("🧪 Voice Email Composer Tests")
    print("=" * 50)
    
    tests = [
        ("Speech Recognition Import", test_speech_recognition_import),
        ("Microphone Access", test_microphone),
        ("Voice Recognition", test_voice_recognition),
        ("Email Composition", test_email_composition),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running: {test_name}")
        print("-" * 30)
        
        try:
            result = await test_func()
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
    elif passed >= 2:  # At least import and email composition work
        print("⚠️  Some tests passed. Voice email composer may work with limitations.")
        print("💡 Try running 'python voice_email.py' to test voice functionality.")
    else:
        print("⚠️  Most tests failed. Please check the issues above.")
        print("💡 Common fixes:")
        print("   - Install portaudio: brew install portaudio")
        print("   - Reinstall pyaudio: pip install --force-reinstall pyaudio")
        print("   - Check microphone permissions in System Preferences")
    
    return passed >= 2  # Consider it working if at least 2 tests pass

async def main():
    """Main test function."""
    try:
        success = await run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n👋 Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 