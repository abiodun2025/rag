#!/usr/bin/env python3
"""
Simple test to check individual agent functionality and identify issues.
"""

import requests
import json
import time

def test_basic_agent_response():
    """Test basic agent response without expecting specific tools."""
    print("🧪 Testing Basic Agent Response")
    print("=" * 50)
    
    test_message = "Hello, can you help me?"
    
    try:
        response = requests.post(
            "http://127.0.0.1:8000/chat",
            json={
                "message": test_message,
                "session_id": "test_session",
                "user_id": "test_user"
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Response received")
            print(f"📝 Response: {data.get('response', 'No response')}")
            print(f"🔧 Tools used: {[tool.name for tool in data.get('tool_calls', [])]}")
            return True
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_master_agent_direct():
    """Test master agent directly."""
    print("\n🧪 Testing Master Agent Directly")
    print("=" * 50)
    
    test_message = "Save this message to desktop"
    
    try:
        response = requests.post(
            "http://127.0.0.1:8000/master-agent/process",
            json={
                "message": test_message,
                "session_id": "test_session",
                "user_id": "test_user"
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Master Agent Response:")
            print(json.dumps(data, indent=2))
            return True
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_smart_agent_direct():
    """Test smart master agent directly."""
    print("\n🧪 Testing Smart Master Agent Directly")
    print("=" * 50)
    
    test_message = "Save this important note to my desktop"
    
    try:
        response = requests.post(
            "http://127.0.0.1:8000/smart-agent/process",
            json={
                "message": test_message,
                "session_id": "test_session",
                "user_id": "test_user"
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Smart Agent Response:")
            print(json.dumps(data, indent=2))
            return True
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_health_and_info():
    """Test health and get server information."""
    print("\n🧪 Testing Server Health and Info")
    print("=" * 50)
    
    try:
        # Health check
        response = requests.get("http://127.0.0.1:8000/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health Status: {data}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
        
        # Try to get documents
        response = requests.get("http://127.0.0.1:8000/documents?limit=1", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Documents endpoint: {len(data.get('documents', []))} documents")
        else:
            print(f"❌ Documents endpoint failed: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Starting Agent Functionality Tests")
    print(f"⏰ Test started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("Health and Info", test_health_and_info),
        ("Basic Agent", test_basic_agent_response),
        ("Master Agent", test_master_agent_direct),
        ("Smart Agent", test_smart_agent_direct),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"🧪 Running: {test_name}")
        print(f"{'='*60}")
        
        try:
            success = test_func()
            results[test_name] = success
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"\n{status} {test_name}")
        except Exception as e:
            print(f"❌ FAIL {test_name} - Exception: {e}")
            results[test_name] = False
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 Test Summary")
    print(f"{'='*60}")
    
    total = len(results)
    passed = sum(1 for result in results.values() if result)
    failed = total - passed
    
    print(f"📊 Total Tests: {total}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Success Rate: {(passed/total)*100:.1f}%")
    
    if failed > 0:
        print(f"\n❌ Failed Tests:")
        for test_name, result in results.items():
            if not result:
                print(f"   - {test_name}")
    
    print(f"\n🎯 Overall Status: {'✅ AGENTS WORKING' if failed == 0 else '❌ AGENTS HAVE ISSUES'}")

if __name__ == "__main__":
    main() 