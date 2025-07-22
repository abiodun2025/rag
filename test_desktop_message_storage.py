#!/usr/bin/env python3
"""
Test script for Desktop Message Storage functionality.
"""

import asyncio
import json
import os
from datetime import datetime
from pathlib import Path

# Import the desktop storage module
from agent.desktop_message_tools import desktop_storage

def test_desktop_storage():
    """Test the desktop message storage functionality."""
    
    print("🧪 Desktop Message Storage Test")
    print("=" * 50)
    
    # Test 1: Save a message
    print("\n📝 Test 1: Saving a message to Desktop...")
    result = desktop_storage.save_message(
        message="Hello from desktop storage test!",
        message_type="test_message",
        metadata={"test": True, "source": "test_script"}
    )
    print(f"✅ Save result: {result}")
    
    # Test 2: Save a conversation
    print("\n💬 Test 2: Saving a conversation to Desktop...")
    result = desktop_storage.save_conversation(
        user_message="What is AI?",
        agent_response="AI stands for Artificial Intelligence. It refers to the simulation of human intelligence in machines.",
        metadata={"topic": "AI", "test": True}
    )
    print(f"✅ Conversation save result: {result}")
    
    # Test 3: List messages
    print("\n📋 Test 3: Listing messages from Desktop...")
    result = desktop_storage.list_messages(limit=5)
    print(f"✅ List result: {result}")
    
    # Test 4: Check Desktop directory
    print("\n📁 Test 4: Checking Desktop directory...")
    desktop_dir = Path("/Users/ola/Desktop/save_message")
    if desktop_dir.exists():
        print(f"✅ Desktop directory exists: {desktop_dir}")
        
        # Count files
        json_files = list(desktop_dir.rglob("*.json"))
        print(f"📄 Found {len(json_files)} message files")
        
        # Show recent files
        if json_files:
            print("\n📄 Recent files:")
            for file_path in sorted(json_files, key=lambda x: x.stat().st_mtime, reverse=True)[:3]:
                print(f"   {file_path}")
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                        content = data.get('content', data.get('user_message', 'N/A'))
                        print(f"   📝 Content: {content[:50]}...")
                        print(f"   🕒 Timestamp: {data.get('timestamp', 'N/A')}")
                except Exception as e:
                    print(f"   ❌ Error reading file: {e}")
    else:
        print(f"❌ Desktop directory does not exist: {desktop_dir}")
    
    print("\n" + "=" * 50)
    print("✅ Desktop Message Storage Test Complete!")
    print("\n📝 Next Steps:")
    print("1. Check your Desktop for the 'save_message' folder")
    print("2. Test via CLI: python3 cli.py")
    print("3. Try: 'save_desktop_message: Hello world'")
    print("4. Try: 'list_desktop_messages'")

if __name__ == "__main__":
    test_desktop_storage() 