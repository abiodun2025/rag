#!/usr/bin/env python3
"""
MCP Performance Testing Agent
Connects to your MCP server and performs comprehensive workflow testing
"""

import asyncio
import time
import json
import statistics
from typing import Dict, List, Any, Optional
import httpx
import logging
from dataclasses import dataclass
from datetime import datetime
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class TestResult:
    """Test result data structure"""
    tool_name: str
    success: bool
    response_time_ms: float
    error_message: Optional[str] = None
    response_data: Optional[Dict] = None
    timestamp: str = None

class MCPPerformanceAgent:
    """Performance testing agent for MCP server workflows"""
    
    def __init__(self, mcp_server_url: str = "http://127.0.0.1:5000"):
        self.mcp_server_url = mcp_server_url
        self.client = httpx.AsyncClient(timeout=30.0)
        self.test_results: List[TestResult] = []
        self.session_id = str(uuid.uuid4())
        
    async def check_server_health(self) -> bool:
        """Check if MCP server is running and healthy"""
        try:
            response = await self.client.get(f"{self.mcp_server_url}/health")
            if response.status_code == 200:
                logger.info("✅ MCP server is healthy and running")
                return True
            else:
                logger.error(f"❌ MCP server health check failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Cannot connect to MCP server: {e}")
            return False
    
    async def get_available_tools(self) -> List[Dict]:
        """Get list of available tools from MCP server"""
        try:
            response = await self.client.get(f"{self.mcp_server_url}/tools")
            if response.status_code == 200:
                data = response.json()
                # Handle both direct array and {"tools": [...]} format
                if isinstance(data, dict) and "tools" in data:
                    tools = data["tools"]
                else:
                    tools = data
                logger.info(f"🔧 Found {len(tools)} tools available")
                return tools
            else:
                logger.error(f"❌ Failed to get tools: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"❌ Error getting tools: {e}")
            return []
    
    async def call_tool(self, tool_name: str, params: Dict) -> TestResult:
        """Call a specific tool and measure performance"""
        start_time = time.time()
        timestamp = datetime.now().isoformat()
        
        try:
            payload = {
                "tool": tool_name,
                "params": params
            }
            
            response = await self.client.post(
                f"{self.mcp_server_url}/call",
                json=payload
            )
            
            response_time_ms = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                result_data = response.json()
                logger.info(f"✅ {tool_name}: {response_time_ms:.2f}ms")
                return TestResult(
                    tool_name=tool_name,
                    success=True,
                    response_time_ms=response_time_ms,
                    response_data=result_data,
                    timestamp=timestamp
                )
            else:
                logger.error(f"❌ {tool_name}: HTTP {response.status_code}")
                return TestResult(
                    tool_name=tool_name,
                    success=False,
                    response_time_ms=response_time_ms,
                    error_message=f"HTTP {response.status_code}: {response.text}",
                    timestamp=timestamp
                )
                
        except Exception as e:
            response_time_ms = (time.time() - start_time) * 1000
            logger.error(f"❌ {tool_name}: Exception - {e}")
            return TestResult(
                tool_name=tool_name,
                success=False,
                response_time_ms=response_time_ms,
                error_message=str(e),
                timestamp=timestamp
            )
    
    async def test_count_r_workflow(self, iterations: int = 10) -> List[TestResult]:
        """Test count_r tool with various inputs"""
        logger.info(f"🧪 Testing count_r workflow ({iterations} iterations)")
        
        test_words = [
            "hello", "world", "performance", "testing", "mcp", "server",
            "abcdefghijklmnopqrstuvwxyz", "rrrrrrrrrr", "no_r_letters",
            "supercalifragilisticexpialidocious", "test"
        ]
        
        results = []
        for i in range(iterations):
            word = test_words[i % len(test_words)]
            result = await self.call_tool("count_r", {"word": word})
            results.append(result)
            await asyncio.sleep(0.1)  # Small delay between calls
            
        return results
    
    async def test_desktop_workflow(self, iterations: int = 5) -> List[TestResult]:
        """Test desktop-related tools"""
        logger.info(f"🧪 Testing desktop workflow ({iterations} iterations)")
        
        results = []
        
        # Test get_desktop_path
        for i in range(iterations):
            result = await self.call_tool("get_desktop_path", {"random_string": f"test_{i}"})
            results.append(result)
            await asyncio.sleep(0.1)
        
        # Test list_desktop_contents
        for i in range(iterations):
            result = await self.call_tool("list_desktop_contents", {"random_string": f"test_{i}"})
            results.append(result)
            await asyncio.sleep(0.1)
            
        return results
    
    async def test_gmail_workflow(self, iterations: int = 3) -> List[TestResult]:
        """Test Gmail-related tools"""
        logger.info(f"🧪 Testing Gmail workflow ({iterations} iterations)")
        
        results = []
        
        # Test open_gmail
        for i in range(iterations):
            result = await self.call_tool("open_gmail", {"random_string": f"test_{i}"})
            results.append(result)
            await asyncio.sleep(0.1)
        
        # Test open_gmail_compose
        for i in range(iterations):
            result = await self.call_tool("open_gmail_compose", {"random_string": f"test_{i}"})
            results.append(result)
            await asyncio.sleep(0.1)
            
        return results
    
    async def test_email_workflow(self, iterations: int = 3) -> List[TestResult]:
        """Test email sending workflow"""
        logger.info(f"🧪 Testing email workflow ({iterations} iterations)")
        
        results = []
        
        # Test sendmail_simple
        for i in range(iterations):
            result = await self.call_tool("sendmail_simple", {
                "to_email": "test@example.com",
                "subject": f"Performance Test {i+1}",
                "message": f"This is performance test email #{i+1} from MCP agent at {datetime.now()}"
            })
            results.append(result)
            await asyncio.sleep(0.5)  # Longer delay for email operations
        
        # Test sendmail with full parameters
        for i in range(iterations):
            result = await self.call_tool("sendmail", {
                "to_email": "test@example.com",
                "subject": f"Full Email Test {i+1}",
                "body": f"This is a full email test #{i+1} with body content at {datetime.now()}",
                "from_email": "performance-test@example.com"
            })
            results.append(result)
            await asyncio.sleep(0.5)
            
        return results
    
    async def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run comprehensive performance test of all workflows"""
        logger.info("🚀 Starting comprehensive MCP server performance test")
        
        # Check server health first
        if not await self.check_server_health():
            return {"error": "MCP server is not available"}
        
        # Get available tools
        tools = await self.get_available_tools()
        logger.info(f"📋 Available tools: {[tool.get('name', 'unknown') for tool in tools]}")
        
        # Run all workflow tests
        test_suites = [
            ("count_r", await self.test_count_r_workflow(15)),
            ("desktop", await self.test_desktop_workflow(8)),
            ("gmail", await self.test_gmail_workflow(5)),
            ("email", await self.test_email_workflow(4))
        ]
        
        # Collect all results
        all_results = []
        for suite_name, results in test_suites:
            all_results.extend(results)
            self.test_results.extend(results)
        
        # Generate performance report
        report = self.generate_performance_report(all_results, tools)
        
        logger.info("✅ Comprehensive performance test completed")
        return report
    
    def generate_performance_report(self, results: List[TestResult], tools: List[Dict]) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        
        # Group results by tool
        tool_results = {}
        for result in results:
            if result.tool_name not in tool_results:
                tool_results[result.tool_name] = []
            tool_results[result.tool_name].append(result)
        
        # Calculate statistics for each tool
        tool_stats = {}
        for tool_name, tool_result_list in tool_results.items():
            successful_results = [r for r in tool_result_list if r.success]
            failed_results = [r for r in tool_result_list if not r.success]
            
            if successful_results:
                response_times = [r.response_time_ms for r in successful_results]
                tool_stats[tool_name] = {
                    "total_calls": len(tool_result_list),
                    "successful_calls": len(successful_results),
                    "failed_calls": len(failed_results),
                    "success_rate": len(successful_results) / len(tool_result_list) * 100,
                    "avg_response_time_ms": statistics.mean(response_times),
                    "min_response_time_ms": min(response_times),
                    "max_response_time_ms": max(response_times),
                    "median_response_time_ms": statistics.median(response_times),
                    "std_deviation_ms": statistics.stdev(response_times) if len(response_times) > 1 else 0,
                    "errors": [r.error_message for r in failed_results] if failed_results else []
                }
            else:
                tool_stats[tool_name] = {
                    "total_calls": len(tool_result_list),
                    "successful_calls": 0,
                    "failed_calls": len(failed_results),
                    "success_rate": 0,
                    "errors": [r.error_message for r in failed_results]
                }
        
        # Overall statistics
        all_response_times = [r.response_time_ms for r in results if r.success]
        overall_stats = {
            "total_tests": len(results),
            "successful_tests": len([r for r in results if r.success]),
            "failed_tests": len([r for r in results if not r.success]),
            "overall_success_rate": len([r for r in results if r.success]) / len(results) * 100 if results else 0,
            "avg_response_time_ms": statistics.mean(all_response_times) if all_response_times else 0,
            "total_duration_ms": sum(r.response_time_ms for r in results),
            "test_session_id": self.session_id,
            "timestamp": datetime.now().isoformat()
        }
        
        return {
            "overall_stats": overall_stats,
            "tool_statistics": tool_stats,
            "available_tools": [tool.get('name', 'unknown') for tool in tools],
            "detailed_results": [
                {
                    "tool_name": r.tool_name,
                    "success": r.success,
                    "response_time_ms": r.response_time_ms,
                    "timestamp": r.timestamp,
                    "error": r.error_message
                } for r in results
            ]
        }
    
    def print_performance_report(self, report: Dict[str, Any]):
        """Print formatted performance report"""
        print("\n" + "="*80)
        print("📊 MCP SERVER PERFORMANCE TEST REPORT")
        print("="*80)
        
        overall = report["overall_stats"]
        print(f"\n🎯 OVERALL STATISTICS:")
        print(f"   Total Tests: {overall['total_tests']}")
        print(f"   Successful: {overall['successful_tests']}")
        print(f"   Failed: {overall['failed_tests']}")
        print(f"   Success Rate: {overall['overall_success_rate']:.1f}%")
        print(f"   Average Response Time: {overall['avg_response_time_ms']:.2f}ms")
        print(f"   Total Duration: {overall['total_duration_ms']:.2f}ms")
        print(f"   Session ID: {overall['test_session_id']}")
        
        print(f"\n🔧 TOOL PERFORMANCE BREAKDOWN:")
        print("-" * 60)
        
        for tool_name, stats in report["tool_statistics"].items():
            print(f"\n📋 {tool_name.upper()}:")
            print(f"   Calls: {stats['total_calls']} | Success: {stats['successful_calls']} | Failed: {stats['failed_calls']}")
            print(f"   Success Rate: {stats['success_rate']:.1f}%")
            
            if stats['successful_calls'] > 0:
                print(f"   Response Time (ms): Avg={stats['avg_response_time_ms']:.2f} | "
                      f"Min={stats['min_response_time_ms']:.2f} | "
                      f"Max={stats['max_response_time_ms']:.2f} | "
                      f"Median={stats['median_response_time_ms']:.2f}")
                if stats['std_deviation_ms'] > 0:
                    print(f"   Standard Deviation: {stats['std_deviation_ms']:.2f}ms")
            
            if stats['errors']:
                print(f"   Errors: {len(stats['errors'])} unique errors")
                for error in stats['errors'][:3]:  # Show first 3 errors
                    print(f"     - {error[:100]}...")
        
        print("\n" + "="*80)
        print("✅ Performance test completed!")
        print("="*80)
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

async def main():
    """Main function to run the performance test"""
    agent = MCPPerformanceAgent()
    
    try:
        # Run comprehensive test
        report = await agent.run_comprehensive_test()
        
        if "error" in report:
            print(f"❌ {report['error']}")
            return
        
        # Print formatted report
        agent.print_performance_report(report)
        
        # Save detailed report to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"mcp_performance_report_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n💾 Detailed report saved to: {filename}")
        
    except Exception as e:
        logger.error(f"❌ Performance test failed: {e}")
    finally:
        await agent.close()

if __name__ == "__main__":
    asyncio.run(main()) 