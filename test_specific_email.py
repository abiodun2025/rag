#!/usr/bin/env python3
"""
Test sending a specific email to mywork461@gmail.com
"""

import asyncio
from agent.smart_master_agent import smart_master_agent

async def test_specific_email():
    """Test sending the specific email."""
    
    print("📧 Testing Email to mywork461@gmail.com")
    print("=" * 60)
    
    # The specific email you requested
    message = "send email to mywork461@gmail.com with subject 'Meeting Tonight' and message 'We have a meeting tonight let me know if you coming thanks!'"
    
    print(f"📝 Email Request: {message}")
    print()
    
    try:
        result = await smart_master_agent.process_message(
            message=message,
            session_id="meeting-email-test",
            user_id="test_user"
        )
        
        intent = result['intent_analysis']['intent']
        confidence = result['intent_analysis']['confidence']
        action = result['execution_result']['result'].get('action', 'unknown')
        response_message = result['execution_result']['message']
        
        print(f"🎯 Intent Detection: {intent} (confidence: {confidence:.2f})")
        print(f"🔧 Action Executed: {action}")
        print(f"📧 Response: {response_message}")
        
        if action == 'email_sent':
            print("\n✅ SUCCESS: Email sent successfully to mywork461@gmail.com!")
            print("📋 Email Details:")
            print("   To: mywork461@gmail.com")
            print("   Subject: Meeting Tonight")
            print("   Message: We have a meeting tonight let me know if you coming thanks!")
        elif action == 'email_error':
            error = result['execution_result']['result'].get('error', 'Unknown error')
            print(f"\n❌ FAILED: Email error - {error}")
        else:
            print(f"\n⚠️  UNEXPECTED: Action was {action}")
            
    except Exception as e:
        print(f"\n❌ EXCEPTION: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Email test completed!")

if __name__ == "__main__":
    asyncio.run(test_specific_email()) 