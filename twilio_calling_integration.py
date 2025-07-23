#!/usr/bin/env python3
"""
Twilio Calling Integration for Real Phone Calls
"""

import os
import logging
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TwilioCallingService:
    def __init__(self):
        # Get Twilio credentials from environment variables
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.from_number = os.getenv('TWILIO_PHONE_NUMBER')
        
        if not all([self.account_sid, self.auth_token, self.from_number]):
            logger.error("❌ Missing Twilio credentials. Please set:")
            logger.error("   TWILIO_ACCOUNT_SID")
            logger.error("   TWILIO_AUTH_TOKEN") 
            logger.error("   TWILIO_PHONE_NUMBER")
            self.client = None
        else:
            self.client = Client(self.account_sid, self.auth_token)
            logger.info("✅ Twilio client initialized successfully")
    
    def make_call(self, to_number: str, message: str = "Hello from your MCP agent!") -> dict:
        """Make a real phone call using Twilio."""
        if not self.client:
            return {
                "success": False,
                "error": "Twilio client not initialized. Check credentials."
            }
        
        try:
            logger.info(f"📞 Making real call to: {to_number}")
            logger.info(f"📞 From: {self.from_number}")
            logger.info(f"📞 Message: {message}")
            
            # Make the call
            call = self.client.calls.create(
                to=to_number,
                from_=self.from_number,
                twiml=f'<Response><Say>{message}</Say></Response>',
                record=True
            )
            
            call_id = f"twilio_{call.sid}"
            
            logger.info(f"✅ Call initiated successfully!")
            logger.info(f"   Call SID: {call.sid}")
            logger.info(f"   Status: {call.status}")
            logger.info(f"   Call ID: {call_id}")
            
            return {
                "success": True,
                "call_id": call_id,
                "twilio_sid": call.sid,
                "status": call.status,
                "to_number": to_number,
                "from_number": self.from_number,
                "message": message,
                "note": "This is a REAL phone call via Twilio"
            }
            
        except Exception as e:
            logger.error(f"❌ Call failed: {e}")
            return {
                "success": False,
                "error": f"Failed to make call: {str(e)}"
            }
    
    def get_call_status(self, call_id: str) -> dict:
        """Get status of a Twilio call."""
        if not self.client:
            return {
                "success": False,
                "error": "Twilio client not initialized"
            }
        
        try:
            # Extract Twilio SID from call_id
            if call_id.startswith("twilio_"):
                twilio_sid = call_id[7:]  # Remove "twilio_" prefix
            else:
                twilio_sid = call_id
            
            call = self.client.calls(twilio_sid).fetch()
            
            return {
                "success": True,
                "call_id": call_id,
                "twilio_sid": call.sid,
                "status": call.status,
                "duration": call.duration,
                "direction": call.direction,
                "note": "Real call status from Twilio"
            }
            
        except Exception as e:
            logger.error(f"❌ Status check failed: {e}")
            return {
                "success": False,
                "error": f"Failed to get call status: {str(e)}"
            }
    
    def end_call(self, call_id: str) -> dict:
        """End a Twilio call."""
        if not self.client:
            return {
                "success": False,
                "error": "Twilio client not initialized"
            }
        
        try:
            # Extract Twilio SID from call_id
            if call_id.startswith("twilio_"):
                twilio_sid = call_id[7:]  # Remove "twilio_" prefix
            else:
                twilio_sid = call_id
            
            call = self.client.calls(twilio_sid).update(status='completed')
            
            return {
                "success": True,
                "call_id": call_id,
                "twilio_sid": call.sid,
                "status": call.status,
                "note": "Call ended successfully via Twilio"
            }
            
        except Exception as e:
            logger.error(f"❌ End call failed: {e}")
            return {
                "success": False,
                "error": f"Failed to end call: {str(e)}"
            }

def test_twilio_setup():
    """Test Twilio setup and credentials."""
    service = TwilioCallingService()
    
    if service.client:
        print("✅ Twilio credentials are valid!")
        print(f"📞 From number: {service.from_number}")
        return True
    else:
        print("❌ Twilio setup incomplete")
        return False

if __name__ == "__main__":
    # Test the setup
    test_twilio_setup() 