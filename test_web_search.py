#!/usr/bin/env python3
"""
Test script for Web Search functionality.
"""

import asyncio
import requests
import json

def test_web_search():
    """Test web search functionality."""
    
    base_url = "http://localhost:8058"
    
    print("🌐 Web Search Test")
    print("=" * 40)
    
    # Test web search through master agent
    test_queries = [
        "latest AI news",
        "OpenAI funding",
        "artificial intelligence trends",
        "machine learning developments"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Test {i}: Web Search")
        print(f"Query: {query}")
        
        try:
            # Make request to master agent
            response = requests.post(
                f"{base_url}/master-agent/process",
                json={
                    "message": f"search the web for {query}",
                    "user_id": "test_user",
                    "session_id": None,
                    "search_type": "hybrid"
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                master_result = result['master_agent_result']
                
                print("✅ Success!")
                print(f"Processing Time: {result['processing_time_ms']:.2f}ms")
                
                # Show web search results
                for agent_result in master_result['results']:
                    if agent_result['agent'] == 'web_search':
                        print(f"  🔍 Web Search Results:")
                        if isinstance(agent_result['result'], dict):
                            result_data = agent_result['result']
                            print(f"    Message: {result_data.get('message', 'N/A')}")
                            print(f"    Total Results: {result_data.get('total_results', 0)}")
                            
                            # Show individual results
                            results = result_data.get('results', [])
                            for j, search_result in enumerate(results, 1):
                                print(f"    {j}. {search_result.get('title', 'No title')}")
                                print(f"       URL: {search_result.get('url', 'No URL')}")
                                print(f"       Source: {search_result.get('source', 'Unknown')}")
                                print(f"       Snippet: {search_result.get('snippet', 'No snippet')[:100]}...")
                                print()
                        else:
                            print(f"    Result: {agent_result['result']}")
                
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
    
    # Test direct web search tools
    print(f"\n🔧 Direct Web Search Tools Test")
    print("=" * 40)
    
    try:
        from agent.web_search_tools import web_search_tools
        
        async def test_direct_search():
            query = "latest AI developments"
            print(f"Testing direct search for: {query}")
            
            results = await web_search_tools.search_web(query, max_results=3)
            
            print(f"Found {len(results)} results:")
            for i, result in enumerate(results, 1):
                print(f"  {i}. {result.title}")
                print(f"     URL: {result.url}")
                print(f"     Source: {result.source}")
                print(f"     Snippet: {result.snippet[:100]}...")
                print()
        
        # Run the async test
        asyncio.run(test_direct_search())
        
    except Exception as e:
        print(f"❌ Direct search test failed: {e}")

if __name__ == "__main__":
    test_web_search() 