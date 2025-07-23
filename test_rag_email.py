#!/usr/bin/env python3
"""
Test email sending through the RAG agent using the MCP bridge
"""

import requests
import json
import uuid

def test_rag_email():
    """Test email sending through the RAG agent"""
    
    print("📧 Testing Email via RAG Agent + MCP Bridge")
    print("=" * 60)
    
    # Test data for RAG agent
    test_data = {
        "message": "send email to mywork461@gmail.com We have a meeting tonight let me know if you coming thanks!",
        "session_id": str(uuid.uuid4())
    }
    
    print(f"📝 Sending request to RAG agent:")
    print(f"   Message: {test_data['message']}")
    print(f"   Session ID: {test_data['session_id']}")
    print()
    
    try:
        # Send request to RAG agent
        response = requests.post(
            "http://localhost:8058/chat",
            headers={"Content-Type": "application/json"},
            json=test_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ RAG Agent Response:")
            print(json.dumps(result, indent=2))
            
            if "response" in result:
                print(f"\n🤖 Agent Response: {result['response']}")
                
                # Check if email was sent successfully
                if "email sent successfully" in result['response'].lower():
                    print("\n🎉 Email sent successfully through RAG agent!")
                    print("📧 Check your email at mywork461@gmail.com")
                else:
                    print("\n❓ Email status unclear from agent response")
            else:
                print("\n❌ No response field in agent response")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to RAG agent. Is it running on http://localhost:8058?")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_rag_email() 