#!/usr/bin/env python3
"""
Comprehensive test script to check if all agents are working properly.
"""

import asyncio
import json
import logging
import sys
import time
from typing import Dict, Any, List
import requests
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AgentTester:
    """Test all agents in the system."""
    
    def __init__(self):
        self.base_url = "http://127.0.0.1:8000"
        self.test_results = {}
        self.session_id = f"test_session_{int(time.time())}"
        
    def print_header(self, title: str):
        """Print a formatted header."""
        print(f"\n{'='*60}")
        print(f"🧪 {title}")
        print(f"{'='*60}")
    
    def print_result(self, test_name: str, success: bool, details: str = ""):
        """Print test result."""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   {details}")
        self.test_results[test_name] = success
    
    async def test_health_check(self) -> bool:
        """Test API health check."""
        self.print_header("Testing API Health Check")
        
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.print_result("Health Check", True, f"Status: {data.get('status', 'unknown')}")
                return True
            else:
                self.print_result("Health Check", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.print_result("Health Check", False, f"Error: {e}")
            return False
    
    async def test_basic_rag_agent(self) -> bool:
        """Test basic RAG agent functionality."""
        self.print_header("Testing Basic RAG Agent")
        
        test_cases = [
            {
                "name": "Simple Query",
                "message": "What is artificial intelligence?",
                "expected_tools": ["vector_search", "graph_search", "hybrid_search"]
            },
            {
                "name": "Document Search",
                "message": "Search for documents about AI",
                "expected_tools": ["list_documents", "vector_search"]
            }
        ]
        
        all_passed = True
        
        for test_case in test_cases:
            try:
                response = requests.post(
                    f"{self.base_url}/chat",
                    json={
                        "message": test_case["message"],
                        "session_id": self.session_id,
                        "user_id": "test_user"
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    tools_used = [tool.name for tool in data.get("tool_calls", [])]
                    
                    # Check if expected tools were used
                    expected_found = any(tool in tools_used for tool in test_case["expected_tools"])
                    
                    self.print_result(
                        test_case["name"], 
                        expected_found,
                        f"Tools used: {tools_used}"
                    )
                    
                    if not expected_found:
                        all_passed = False
                else:
                    self.print_result(test_case["name"], False, f"HTTP {response.status_code}")
                    all_passed = False
                    
            except Exception as e:
                self.print_result(test_case["name"], False, f"Error: {e}")
                all_passed = False
        
        return all_passed
    
    async def test_master_agent(self) -> bool:
        """Test master agent functionality."""
        self.print_header("Testing Master Agent")
        
        test_cases = [
            {
                "name": "Message Storage",
                "message": "Save this message to the project",
                "expected_agent": "message_storage"
            },
            {
                "name": "Desktop Storage",
                "message": "Remember this on desktop",
                "expected_agent": "desktop_storage"
            },
            {
                "name": "Email Task",
                "message": "Send an email to test@example.com",
                "expected_agent": "email"
            },
            {
                "name": "Search Task",
                "message": "Search for information about AI",
                "expected_agent": "search"
            }
        ]
        
        all_passed = True
        
        for test_case in test_cases:
            try:
                response = requests.post(
                    f"{self.base_url}/master-agent/process",
                    json={
                        "message": test_case["message"],
                        "session_id": self.session_id,
                        "user_id": "test_user"
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    tasks = data.get("tasks", [])
                    
                    # Check if expected agent type was involved
                    agent_types = [task.get("agent_type") for task in tasks]
                    expected_found = test_case["expected_agent"] in agent_types
                    
                    self.print_result(
                        test_case["name"],
                        expected_found,
                        f"Agent types: {agent_types}"
                    )
                    
                    if not expected_found:
                        all_passed = False
                else:
                    self.print_result(test_case["name"], False, f"HTTP {response.status_code}")
                    all_passed = False
                    
            except Exception as e:
                self.print_result(test_case["name"], False, f"Error: {e}")
                all_passed = False
        
        return all_passed
    
    async def test_smart_master_agent(self) -> bool:
        """Test smart master agent functionality."""
        self.print_header("Testing Smart Master Agent")
        
        test_cases = [
            {
                "name": "Desktop Save Intent",
                "message": "Save this important note to my desktop",
                "expected_intent": "save_desktop"
            },
            {
                "name": "Project Save Intent",
                "message": "Remember this project information",
                "expected_intent": "save_project"
            },
            {
                "name": "Email Intent",
                "message": "Send an email to john@example.com about the meeting",
                "expected_intent": "email"
            },
            {
                "name": "Web Search Intent",
                "message": "What's the latest news about AI?",
                "expected_intent": "web_search"
            }
        ]
        
        all_passed = True
        
        for test_case in test_cases:
            try:
                response = requests.post(
                    f"{self.base_url}/smart-agent/process",
                    json={
                        "message": test_case["message"],
                        "session_id": self.session_id,
                        "user_id": "test_user"
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    intent = data.get("intent", {}).get("intent")
                    
                    expected_found = intent == test_case["expected_intent"]
                    
                    self.print_result(
                        test_case["name"],
                        expected_found,
                        f"Detected intent: {intent}"
                    )
                    
                    if not expected_found:
                        all_passed = False
                else:
                    self.print_result(test_case["name"], False, f"HTTP {response.status_code}")
                    all_passed = False
                    
            except Exception as e:
                self.print_result(test_case["name"], False, f"Error: {e}")
                all_passed = False
        
        return all_passed
    
    async def test_search_endpoints(self) -> bool:
        """Test search endpoints."""
        self.print_header("Testing Search Endpoints")
        
        search_query = "artificial intelligence"
        all_passed = True
        
        # Test vector search
        try:
            response = requests.post(
                f"{self.base_url}/search/vector",
                json={"query": search_query, "limit": 5},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                self.print_result("Vector Search", True, f"Found {len(results)} results")
            else:
                self.print_result("Vector Search", False, f"HTTP {response.status_code}")
                all_passed = False
                
        except Exception as e:
            self.print_result("Vector Search", False, f"Error: {e}")
            all_passed = False
        
        # Test graph search
        try:
            response = requests.post(
                f"{self.base_url}/search/graph",
                json={"query": search_query},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                self.print_result("Graph Search", True, f"Found {len(results)} results")
            else:
                self.print_result("Graph Search", False, f"HTTP {response.status_code}")
                all_passed = False
                
        except Exception as e:
            self.print_result("Graph Search", False, f"Error: {e}")
            all_passed = False
        
        # Test hybrid search
        try:
            response = requests.post(
                f"{self.base_url}/search/hybrid",
                json={"query": search_query, "limit": 5},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                self.print_result("Hybrid Search", True, f"Found {len(results)} results")
            else:
                self.print_result("Hybrid Search", False, f"HTTP {response.status_code}")
                all_passed = False
                
        except Exception as e:
            self.print_result("Hybrid Search", False, f"Error: {e}")
            all_passed = False
        
        return all_passed
    
    async def test_documents_endpoint(self) -> bool:
        """Test documents endpoint."""
        self.print_header("Testing Documents Endpoint")
        
        try:
            response = requests.get(f"{self.base_url}/documents?limit=5", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                documents = data.get("documents", [])
                self.print_result("Documents List", True, f"Found {len(documents)} documents")
                return True
            else:
                self.print_result("Documents List", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.print_result("Documents List", False, f"Error: {e}")
            return False
    
    async def test_mcp_tools(self) -> bool:
        """Test MCP tools functionality."""
        self.print_header("Testing MCP Tools")
        
        test_cases = [
            {
                "name": "Count R Letters",
                "message": "Count the letter 'r' in the word 'programming'",
                "expected_tool": "count_r_letters"
            },
            {
                "name": "Desktop Files",
                "message": "List files on my desktop",
                "expected_tool": "list_desktop_files"
            }
        ]
        
        all_passed = True
        
        for test_case in test_cases:
            try:
                response = requests.post(
                    f"{self.base_url}/chat",
                    json={
                        "message": test_case["message"],
                        "session_id": self.session_id,
                        "user_id": "test_user"
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    tools_used = [tool.name for tool in data.get("tool_calls", [])]
                    
                    expected_found = test_case["expected_tool"] in tools_used
                    
                    self.print_result(
                        test_case["name"],
                        expected_found,
                        f"Tools used: {tools_used}"
                    )
                    
                    if not expected_found:
                        all_passed = False
                else:
                    self.print_result(test_case["name"], False, f"HTTP {response.status_code}")
                    all_passed = False
                    
            except Exception as e:
                self.print_result(test_case["name"], False, f"Error: {e}")
                all_passed = False
        
        return all_passed
    
    def print_summary(self):
        """Print test summary."""
        self.print_header("Test Summary")
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result)
        failed_tests = total_tests - passed_tests
        
        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"📈 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ Failed Tests:")
            for test_name, result in self.test_results.items():
                if not result:
                    print(f"   - {test_name}")
        
        print(f"\n🎯 Overall Status: {'✅ ALL AGENTS WORKING' if failed_tests == 0 else '❌ SOME AGENTS FAILED'}")
    
    async def run_all_tests(self):
        """Run all tests."""
        print("🚀 Starting Comprehensive Agent Testing")
        print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Check if server is running
        if not await self.test_health_check():
            print("\n❌ Server is not running or not accessible!")
            print("💡 Please start the server with: python -m agent.api")
            return False
        
        # Run all tests
        tests = [
            ("Basic RAG Agent", self.test_basic_rag_agent),
            ("Master Agent", self.test_master_agent),
            ("Smart Master Agent", self.test_smart_master_agent),
            ("Search Endpoints", self.test_search_endpoints),
            ("Documents Endpoint", self.test_documents_endpoint),
            ("MCP Tools", self.test_mcp_tools),
        ]
        
        for test_name, test_func in tests:
            try:
                await test_func()
            except Exception as e:
                logger.error(f"Error running {test_name}: {e}")
                self.print_result(test_name, False, f"Exception: {e}")
        
        # Print summary
        self.print_summary()
        
        return all(self.test_results.values())

async def main():
    """Main function."""
    tester = AgentTester()
    success = await tester.run_all_tests()
    
    if success:
        print("\n🎉 All agents are working properly!")
        sys.exit(0)
    else:
        print("\n⚠️  Some agents have issues. Check the failed tests above.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 