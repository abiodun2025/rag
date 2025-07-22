#!/usr/bin/env python3
"""
Test script for Master Agent functionality.
"""

import asyncio
import json
import requests
from datetime import datetime

def test_master_agent():
    """Test the master agent with different types of requests."""
    
    base_url = "http://localhost:8058"
    
    print("🧪 Master Agent Test")
    print("=" * 50)
    
    # Test cases
    test_cases = [
        {
            "name": "Desktop Storage Task",
            "message": "save to desktop: Hello world, this is a test message",
            "expected_agent": "desktop_storage"
        },
        {
            "name": "Project Storage Task", 
            "message": "save to project: This is a project note",
            "expected_agent": "message_storage"
        },
        {
            "name": "Email Task",
            "message": "compose an email to test@example.com with subject 'Test' and body 'Hello'",
            "expected_agent": "email"
        },
        {
            "name": "Search Task",
            "message": "search for OpenAI funding information",
            "expected_agent": "search"
        },
        {
            "name": "Web Search Task",
            "message": "search the web for latest AI news",
            "expected_agent": "web_search"
        },
        {
            "name": "Knowledge Graph Task",
            "message": "what is the relationship between OpenAI and Microsoft",
            "expected_agent": "knowledge_graph"
        },
        {
            "name": "General Task",
            "message": "Hello, how are you doing today?",
            "expected_agent": "general"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}: {test_case['name']}")
        print(f"Message: {test_case['message']}")
        print(f"Expected Agent: {test_case['expected_agent']}")
        
        try:
            # Make request to master agent
            response = requests.post(
                f"{base_url}/master-agent/process",
                json={
                    "message": test_case['message'],
                    "user_id": "test_user",
                    "session_id": None,
                    "search_type": "hybrid"
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Success!")
                print(f"Session ID: {result['session_id']}")
                print(f"Processing Time: {result['processing_time_ms']:.2f}ms")
                
                # Show which agents were used
                master_result = result['master_agent_result']
                print(f"Tasks Executed: {master_result['tasks_executed']}")
                print(f"Successful Tasks: {master_result['successful_tasks']}")
                print(f"Failed Tasks: {master_result['failed_tasks']}")
                
                for agent_result in master_result['results']:
                    print(f"  - {agent_result['agent']}: {'✅' if agent_result['success'] else '❌'}")
                    if agent_result['success']:
                        print(f"    Result: {agent_result['result']}")
                    else:
                        print(f"    Error: {agent_result['error']}")
                
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
    
    # Test master agent stats
    print(f"\n📊 Master Agent Statistics")
    print("=" * 30)
    
    try:
        stats_response = requests.get(f"{base_url}/master-agent/stats")
        if stats_response.status_code == 200:
            stats = stats_response.json()
            print("Agent Statistics:")
            for agent, stat in stats['agent_stats'].items():
                print(f"  {agent}: {stat['calls']} calls, {stat['success']} success, {stat['errors']} errors")
            print(f"Task History Count: {stats['task_history_count']}")
        else:
            print(f"❌ Stats Error: {stats_response.status_code}")
    except Exception as e:
        print(f"❌ Stats Exception: {e}")

if __name__ == "__main__":
    test_master_agent() 