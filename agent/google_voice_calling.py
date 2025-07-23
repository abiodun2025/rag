"""
Google Voice Calling Integration for Smart Agent
"""

import webbrowser
import subprocess
import time
from typing import Optional

class GoogleVoiceCaller:
    """Google Voice calling service integration."""
    
    def __init__(self):
        self.base_url = "https://voice.google.com"
        self.calls_url = "https://voice.google.com/calls"
        
    def make_call(self, phone_number: str) -> dict:
        """
        Make a call using Google Voice.
        
        Args:
            phone_number: Phone number to call
            
        Returns:
            Dictionary with call result
        """
        try:
            # Clean up phone number
            clean_number = self._clean_phone_number(phone_number)
            
            # Open Google Voice in browser
            webbrowser.open(self.base_url)
            
            # Wait a moment for browser to open
            time.sleep(1)
            
            return {
                "success": True,
                "phone_number": clean_number,
                "method": "google_voice",
                "message": f"📞 Google Voice opened! Dial {clean_number} for FREE calling",
                "instructions": [
                    "1. Wait for Google Voice to load",
                    "2. Click the 'Calls' tab",
                    "3. Click the phone icon to make a new call",
                    "4. Enter the number: " + clean_number,
                    "5. Click 'Call' button",
                    "6. Talk for FREE! 🎉"
                ]
            }
            
        except Exception as e:
            return {
                "success": False,
                "phone_number": phone_number,
                "error": str(e),
                "message": f"❌ Failed to open Google Voice: {str(e)}"
            }
    
    def _clean_phone_number(self, phone_number: str) -> str:
        """Clean and format phone number."""
        # Remove all non-digits
        digits = ''.join(filter(str.isdigit, phone_number))
        
        # Format based on length
        if len(digits) == 10:
            # US number without country code
            return f"+1{digits}"
        elif len(digits) == 11 and digits.startswith('1'):
            # US number with country code
            return f"+{digits}"
        elif len(digits) >= 10:
            # International number
            return f"+{digits}"
        else:
            # Return as is if can't determine format
            return phone_number
    
    def open_voice_with_number(self, phone_number: str) -> dict:
        """
        Try to open Google Voice with number pre-filled (if possible).
        
        Args:
            phone_number: Phone number to call
            
        Returns:
            Dictionary with result
        """
        try:
            clean_number = self._clean_phone_number(phone_number)
            
            # Try to use tel: protocol which might work with some browsers
            tel_url = f"tel:{clean_number}"
            
            # Open Google Voice first
            webbrowser.open(self.base_url)
            time.sleep(1)
            
            # Try to open tel: link (might work with some browsers)
            try:
                webbrowser.open(tel_url)
            except:
                pass
            
            return {
                "success": True,
                "phone_number": clean_number,
                "method": "google_voice_with_tel",
                "message": f"📞 Google Voice opened with number {clean_number}",
                "instructions": [
                    "1. Google Voice should be open in your browser",
                    "2. If the number didn't auto-fill, manually enter: " + clean_number,
                    "3. Click 'Call' to make FREE call",
                    "4. Enjoy your conversation! 🎉"
                ]
            }
            
        except Exception as e:
            return {
                "success": False,
                "phone_number": phone_number,
                "error": str(e),
                "message": f"❌ Failed to open Google Voice: {str(e)}"
            }

# Global instance
google_voice_caller = GoogleVoiceCaller() 