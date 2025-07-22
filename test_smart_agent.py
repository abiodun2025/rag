#!/usr/bin/env python3
"""
Test script for Smart Master Agent functionality.
"""

import asyncio
import json
import requests
from datetime import datetime

def test_smart_agent():
    """Test the smart master agent with natural language requests."""
    
    base_url = "http://localhost:8058"
    
    print("🧠 Smart Master Agent Test")
    print("=" * 50)
    
    # Test cases with natural language
    test_cases = [
        {
            "name": "Natural Desktop Save",
            "message": "Hello world, this is a test message",
            "expected_intent": "save_desktop"
        },
        {
            "name": "Remember Note",
            "message": "Remember this important meeting note for tomorrow",
            "expected_intent": "save_desktop"
        },
        {
            "name": "Project Save",
            "message": "Save this to project: Project milestone completed",
            "expected_intent": "save_project"
        },
        {
            "name": "Email Composition",
            "message": "Email john@example.com with subject 'Meeting' and body 'Let's meet tomorrow'",
            "expected_intent": "email"
        },
        {
            "name": "Web Search",
            "message": "What's the latest AI news?",
            "expected_intent": "web_search"
        },
        {
            "name": "Internal Search",
            "message": "Search for OpenAI funding information",
            "expected_intent": "search"
        },
        {
            "name": "Knowledge Graph",
            "message": "What's the relationship between OpenAI and Microsoft?",
            "expected_intent": "knowledge_graph"
        },
        {
            "name": "General Conversation",
            "message": "Hello, how are you doing today?",
            "expected_intent": "general"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}: {test_case['name']}")
        print(f"Message: {test_case['message']}")
        print(f"Expected Intent: {test_case['expected_intent']}")
        
        try:
            # Make request to smart agent
            response = requests.post(
                f"{base_url}/smart-agent/process",
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
                smart_result = result['smart_agent_result']
                intent_analysis = smart_result['intent_analysis']
                execution_result = smart_result['execution_result']
                
                print("✅ Success!")
                print(f"Session ID: {result['session_id']}")
                print(f"Processing Time: {result['processing_time_ms']:.2f}ms")
                print(f"Intent: {intent_analysis['intent']} (confidence: {intent_analysis['confidence']:.2f})")
                
                if execution_result['success']:
                    print(f"Result: {execution_result['message']}")
                    
                    # Show detailed results
                    result_data = execution_result['result']
                    if isinstance(result_data, dict):
                        action = result_data.get('action', 'unknown')
                        print(f"Action: {action}")
                        
                        if action == 'web_search' and result_data.get('results'):
                            print(f"Web Search Results: {len(result_data['results'])} items")
                            for j, item in enumerate(result_data['results'][:2], 1):
                                print(f"  {j}. {item.get('title', 'No title')}")
                                
                        elif action == 'internal_search' and result_data.get('results'):
                            print(f"Internal Search Results: {len(result_data['results'])} items")
                            
                        elif action == 'knowledge_graph_search' and result_data.get('results'):
                            print(f"Knowledge Graph Results: {len(result_data['results'])} items")
                            
                        elif action in ['saved_to_desktop', 'saved_to_project']:
                            print(f"File saved: {result_data.get('file_path', 'Unknown')}")
                            
                else:
                    print(f"❌ Error: {execution_result.get('error', 'Unknown error')}")
                
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
    
    # Test smart agent stats
    print(f"\n📊 Smart Agent Statistics")
    print("=" * 30)
    
    try:
        stats_response = requests.get(f"{base_url}/smart-agent/stats")
        if stats_response.status_code == 200:
            stats = stats_response.json()
            print("Agent Statistics:")
            for agent, stat in stats['agent_stats'].items():
                print(f"  {agent}: {stat['calls']} calls, {stat['success']} success, {stat['errors']} errors")
        else:
            print(f"❌ Stats Error: {stats_response.status_code}")
    except Exception as e:
        print(f"❌ Stats Exception: {e}")

if __name__ == "__main__":
    test_smart_agent() 