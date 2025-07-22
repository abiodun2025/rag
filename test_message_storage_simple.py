#!/usr/bin/env python3
"""
Simple Message Storage Test
==========================

This script tests the message storage functionality after fixing Cohere API issues.
"""

import asyncio
import aiohttp
import json
from pathlib import Path

async def test_basic_message_storage():
    """Test basic message storage functionality."""
    print("🧪 Testing Basic Message Storage...")
    
    test_cases = [
        {
            "name": "Simple Message Save",
            "message": "Save this message: Hello, this is a test message.",
            "expected": "Agent should save the message"
        },
        {
            "name": "Important Note Save",
            "message": "Please save this important note: Meeting tomorrow at 2 PM.",
            "expected": "Agent should save the important note"
        }
    ]
    
    async with aiohttp.ClientSession() as session:
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📝 Test Case {i}: {test_case['name']}")
            print("-" * 50)
            
            payload = {
                "message": test_case["message"],
                "session_id": None,
                "user_id": "test_user",
                "search_type": "hybrid"
            }
            
            try:
                async with session.post(
                    "http://localhost:8058/chat/stream",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 200:
                        print(f"✅ Request sent successfully")
                        print(f"📝 Test message: {test_case['message']}")
                        
                        # Read the response
                        response_text = await response.text()
                        print(f"📄 Response length: {len(response_text)} characters")
                        
                        # Check if response mentions storage
                        storage_keywords = ["save", "storage", "message", "saved"]
                        found_keywords = [kw for kw in storage_keywords if kw in response_text.lower()]
                        
                        if found_keywords:
                            print(f"✅ Agent mentioned storage: {found_keywords}")
                        else:
                            print("⚠️  Agent didn't mention storage in response")
                            
                    else:
                        print(f"❌ Request failed with status {response.status}")
                        
            except Exception as e:
                print(f"❌ Connection error: {e}")

def test_direct_message_storage():
    """Test message storage tools directly."""
    print("\n🧪 Testing Message Storage Tools Directly...")
    
    try:
        from agent.message_tools import message_storage
        
        # Test 1: Save a simple message
        print("📤 Testing save_message...")
        result = message_storage.save_message(
            message="This is a test message from the agent.",
            message_type="test_message",
            metadata={"test": True, "source": "test_script"}
        )
        print(f"✅ Save result: {result}")
        
        # Test 2: Save a conversation
        print("\n📤 Testing save_conversation...")
        conv_result = message_storage.save_conversation(
            user_message="What is AI?",
            agent_response="AI stands for Artificial Intelligence. It refers to the simulation of human intelligence in machines.",
            metadata={"topic": "AI", "test": True}
        )
        print(f"✅ Conversation save result: {conv_result}")
        
        # Test 3: List messages
        print("\n📋 Testing list_messages...")
        list_result = message_storage.list_messages(limit=10)
        print(f"✅ List result: {list_result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing message storage: {e}")
        return False

def show_storage_files():
    """Show the storage files that were created."""
    print("\n📁 Message Storage Files:")
    print("=" * 50)
    
    messages_dir = Path("messages")
    if messages_dir.exists():
        print(f"✅ Messages directory exists: {messages_dir.absolute()}")
        
        # Count files
        json_files = list(messages_dir.rglob("*.json"))
        print(f"📄 Found {len(json_files)} message files")
        
        # Show recent files
        for file_path in json_files[-3:]:  # Show last 3 files
            print(f"📄 {file_path}")
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    content = data.get('content', data.get('user_message', ''))
                    print(f"   📝 Content: {content[:50]}...")
                    print(f"   🕒 Timestamp: {data.get('timestamp', 'N/A')}")
            except Exception as e:
                print(f"   ❌ Error reading file: {e}")
    else:
        print("❌ Messages directory not found")

def main():
    """Main test function."""
    print("🧪 Message Storage Test (Fixed)")
    print("=" * 50)
    
    print("This test verifies the message storage functionality after fixing Cohere API issues.")
    
    # Test direct message storage
    print("\n🧪 Testing Direct Message Storage...")
    direct_ok = test_direct_message_storage()
    
    # Show storage files
    show_storage_files()
    
    # Test via API
    print("\n🌐 Testing via API...")
    try:
        asyncio.run(test_basic_message_storage())
    except Exception as e:
        print(f"❌ API test failed: {e}")
        print("💡 Make sure the API server is running:")
        print("   python3 -m uvicorn agent.api:app --host 0.0.0.0 --port 8058")
    
    print("\n" + "="*50)
    print("✅ Test Complete!")
    print("="*50)
    print("\n📝 Next Steps:")
    print("1. Test via CLI: python3 cli.py")
    print("2. Try: 'Save this message: Hello world'")
    print("3. Check the 'messages/' directory for saved files")

if __name__ == "__main__":
    main() 