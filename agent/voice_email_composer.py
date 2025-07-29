"""
Voice Email Composer - Use voice commands to compose emails
"""

import asyncio
import logging
from typing import Optional, Dict, Any
from .dynamic_email_composer import analyze_and_compose_email

logger = logging.getLogger(__name__)

class VoiceEmailComposer:
    """Voice-enabled email composer using speech recognition."""
    
    def __init__(self):
        self.recognizer = None
        self.microphone = None
        self._initialized = False
        self._voice_available = False
        
        logger.info("🎤 Voice Email Composer initialized (lazy loading)")
    
    def _initialize_speech_recognition(self):
        """Initialize speech recognition components when needed."""
        if self._initialized:
            return
            
        try:
            import speech_recognition as sr
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            
            # Adjust for ambient noise
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
            self._initialized = True
            self._voice_available = True
            logger.info("✅ Speech recognition initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize speech recognition: {e}")
            self._voice_available = False
            # Don't raise the exception, just mark voice as unavailable
    
    def is_voice_available(self) -> bool:
        """Check if voice input is available."""
        if not self._initialized:
            self._initialize_speech_recognition()
        return self._voice_available
    
    def listen_for_command(self, timeout: int = 15) -> Optional[str]:
        """
        Listen for voice command.
        
        Args:
            timeout: Timeout in seconds
            
        Returns:
            Transcribed text or None if failed
        """
        try:
            # Initialize speech recognition if not already done
            if not self._initialized:
                self._initialize_speech_recognition()
            
            if not self._voice_available:
                print("❌ Voice input not available. Please use text input instead.")
                return None
            
            print(f"🎤 Listening for email command (timeout: {timeout}s)...")
            print("💡 Say something like: 'send email to john@company.com about the meeting'")
            
            with self.microphone as source:
                audio = self.recognizer.listen(source, timeout=timeout)
                
            # Convert speech to text using Google Speech Recognition
            text = self.recognizer.recognize_google(audio)
            print(f"🎤 You said: {text}")
            
            return text
            
        except Exception as e:
            print(f"❌ Error during speech recognition: {e}")
            return None
    
    def get_text_input(self) -> Optional[str]:
        """
        Get voice command as text input (fallback when voice is not available).
        
        Returns:
            Text command or None if cancelled
        """
        print("💬 Voice input not available. Please type your email command:")
        print("💡 Examples:")
        print("   • send email to john@company.com about the meeting")
        print("   • write urgent email to support@service.com about login issues")
        print("   • compose formal email to client@business.com regarding the proposal")
        print("   • send casual email to friend@gmail.com about weekend plans")
        print()
        
        try:
            command = input("🎤 Email Command: ").strip()
            if command:
                return command
            else:
                print("❌ No command entered")
                return None
        except KeyboardInterrupt:
            print("\n👋 Cancelled")
            return None
        except Exception as e:
            print(f"❌ Error reading input: {e}")
            return None
    
    async def compose_email_from_voice(self, voice_command: str) -> Dict[str, Any]:
        """
        Compose email from voice command using existing dynamic composer.
        
        Args:
            voice_command: The voice command text
            
        Returns:
            Dictionary with email composition result
        """
        try:
            print(f"📧 Processing voice command: {voice_command}")
            
            # Use existing dynamic email composer
            result = await analyze_and_compose_email(voice_command)
            
            if result.get("status") == "success":
                print("✅ Email composed and sent from voice command!")
                print(f"📧 To: {result.get('to_email')}")
                print(f"📝 Subject: {result.get('subject')}")
                print(f"📄 Body Preview: {result.get('body_preview', '')[:100]}...")
            else:
                print(f"❌ Failed to compose email: {result.get('error')}")
            
            return result
            
        except Exception as e:
            error_msg = f"Error processing voice email: {str(e)}"
            print(f"❌ {error_msg}")
            logger.error(error_msg)
            return {
                "status": "error",
                "error": error_msg
            }
    
    async def interactive_voice_email(self):
        """Interactive voice email composition session."""
        print("🎤 Voice Email Composer")
        print("=" * 50)
        
        # Check voice availability
        if self.is_voice_available():
            print("✅ Voice input is available!")
            print("💡 Voice Command Examples:")
            print("   • 'send email to john@company.com'")
            print("   • 'email sarah@gmail.com about the meeting'")
            print("   • 'write urgent email to support@service.com'")
            print("   • 'compose casual email to friend@gmail.com'")
            print("   • 'send formal email to client@business.com about quarterly report'")
        else:
            print("⚠️  Voice input not available - using text input")
            print("💡 Text Command Examples:")
            print("   • send email to john@company.com about the meeting")
            print("   • write urgent email to support@service.com about login issues")
            print("   • compose formal email to client@business.com regarding the proposal")
            print("   • send casual email to friend@gmail.com about weekend plans")
        
        print("=" * 50)
        
        while True:
            try:
                # Get voice or text command
                if self.is_voice_available():
                    voice_command = self.listen_for_command()
                else:
                    voice_command = self.get_text_input()
                
                if voice_command:
                    # Process the command
                    result = await self.compose_email_from_voice(voice_command)
                    
                    # Ask if user wants to continue
                    print("\n" + "=" * 50)
                    continue_choice = input("🎤 Compose another email? (y/n): ").strip().lower()
                    if continue_choice not in ['y', 'yes']:
                        print("👋 Goodbye!")
                        break
                else:
                    # Ask if user wants to try again
                    retry_choice = input("🎤 Try again? (y/n): ").strip().lower()
                    if retry_choice not in ['y', 'yes']:
                        print("👋 Goodbye!")
                        break
                        
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                break

# Global instance (lazy initialization)
voice_email_composer = VoiceEmailComposer()

async def compose_email_from_voice_command(voice_command: str) -> Dict[str, Any]:
    """
    Convenience function to compose email from voice command.
    
    Args:
        voice_command: The voice command text
        
    Returns:
        Dictionary with email composition result
    """
    return await voice_email_composer.compose_email_from_voice(voice_command)

async def start_voice_email_session():
    """Start an interactive voice email session."""
    await voice_email_composer.interactive_voice_email()

def get_voice_status() -> Dict[str, Any]:
    """
    Get the status of voice input capabilities.
    
    Returns:
        Dictionary with voice status information
    """
    composer = VoiceEmailComposer()
    voice_available = composer.is_voice_available()
    
    return {
        "voice_available": voice_available,
        "status": "available" if voice_available else "unavailable",
        "message": "Voice input is working!" if voice_available else "Voice input not available - using text input",
        "fallback": "text_input"
    } 