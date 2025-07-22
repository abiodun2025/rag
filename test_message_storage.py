#!/usr/bin/env python3
"""
Message Storage Test Script
==========================

This script tests the message storage functionality of the agent.
"""

import asyncio
import aiohttp
import json
import os
from pathlib import Path

async def test_message_storage():
    """Test message storage functionality via API."""
    print("📝 Testing Message Storage...")
    
    test_cases = [
        {
            "name": "Save Simple Message",
            "message": "Save this message: Hello, this is a test message for storage.",
            "expected": "Agent should save the message to storage"
        },
        {
            "name": "Save Important Note",
            "message": "Please save this important note: Meeting scheduled for tomorrow at 2 PM with the AI team.",
            "expected": "Agent should save the important note"
        },
        {
            "name": "Save Conversation",
            "message": "Save our conversation about AI project updates.",
            "expected": "Agent should save the conversation"
        },
        {
            "name": "List Saved Messages",
            "message": "Show me all saved messages from today.",
            "expected": "Agent should list saved messages"
        }
    ]
    
    async with aiohttp.ClientSession() as session:
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📧 Test Case {i}: {test_case['name']}")
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
                        print(f"🤖 Agent should respond with message storage capabilities")
                        
                        # Read the response
                        response_text = await response.text()
                        print(f"📄 Response length: {len(response_text)} characters")
                        
                        # Check if response mentions storage
                        storage_keywords = ["save", "storage", "message", "conversation", "store"]
                        found_keywords = [kw for kw in storage_keywords if kw in response_text.lower()]
                        
                        if found_keywords:
                            print(f"✅ Agent mentioned storage: {found_keywords}")
                        else:
                            print("⚠️  Agent didn't mention storage in response")
                            
                    else:
                        print(f"❌ Request failed with status {response.status}")
                        
            except Exception as e:
                print(f"❌ Connection error: {e}")

def test_message_storage_directly():
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

def show_storage_structure():
    """Show the storage directory structure."""
    print("\n📁 Message Storage Structure:")
    print("=" * 50)
    
    messages_dir = Path("messages")
    if messages_dir.exists():
        print(f"✅ Messages directory exists: {messages_dir.absolute()}")
        
        # Show directory structure
        for file_path in messages_dir.rglob("*.json"):
            print(f"📄 {file_path}")
            
            # Show file content preview
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    print(f"   📝 Content: {data.get('content', data.get('user_message', ''))[:50]}...")
                    print(f"   🕒 Timestamp: {data.get('timestamp', 'N/A')}")
                    print(f"   🏷️  Type: {data.get('message_type', 'N/A')}")
            except Exception as e:
                print(f"   ❌ Error reading file: {e}")
    else:
        print("❌ Messages directory not found")
        print("💡 Messages will be created when you test the functionality")

def show_cli_instructions():
    """Show CLI testing instructions."""
    print("\n💻 CLI Testing Instructions:")
    print("=" * 50)
    
    print("1. Start the API server:")
    print("   python3 -m uvicorn agent.api:app --host 0.0.0.0 --port 8058")
    print("\n2. In another terminal, start the CLI:")
    print("   python3 cli.py")
    print("\n3. Try these message storage commands:")
    print("   - 'Save this message: Hello world'")
    print("   - 'Save this important note about AI'")
    print("   - 'Save our conversation about tech companies'")
    print("   - 'Show me all saved messages'")
    print("   - 'List messages from today'")

def main():
    """Main test function."""
    print("📝 Message Storage Test Suite")
    print("=" * 50)
    
    print("This test demonstrates the message storage functionality.")
    print("The agent can save messages and conversations to a local directory.")
    
    # Test message storage directly
    print("\n🧪 Testing Message Storage Tools...")
    tools_ok = test_message_storage_directly()
    
    # Show storage structure
    show_storage_structure()
    
    # Test via API
    print("\n🌐 Testing via API...")
    try:
        asyncio.run(test_message_storage())
    except Exception as e:
        print(f"❌ API test failed: {e}")
        print("💡 Make sure the API server is running:")
        print("   python3 -m uvicorn agent.api:app --host 0.0.0.0 --port 8058")
    
    # CLI instructions
    show_cli_instructions()
    
    print("\n" + "="*50)
    print("✅ Test Complete!")
    print("="*50)
    print("\n📝 Next Steps:")
    print("1. Test via CLI with message storage commands")
    print("2. Check the 'messages/' directory for saved files")
    print("3. Try different message types and metadata")

if __name__ == "__main__":
    main() 