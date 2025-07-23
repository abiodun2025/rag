#!/usr/bin/env python3
"""
MCP Server Scanner
Comprehensive analysis of MCP server tools and capabilities
"""

import asyncio
import json
import httpx
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MCPServerScanner:
    """Comprehensive MCP server scanner and analyzer"""
    
    def __init__(self, server_url: str = "http://127.0.0.1:5000"):
        self.server_url = server_url
        self.client = httpx.AsyncClient(timeout=30.0)
        self.scan_results = {}
        
    async def scan_server(self) -> Dict[str, Any]:
        """Perform comprehensive server scan"""
        logger.info(f"🔍 Starting comprehensive scan of MCP server: {self.server_url}")
        
        scan_results = {
            "server_info": {},
            "health_status": {},
            "tools_analysis": {},
            "capabilities": {},
            "recommendations": {},
            "scan_timestamp": datetime.now().isoformat()
        }
        
        try:
            # 1. Server Health Check
            scan_results["health_status"] = await self.check_server_health()
            
            # 2. Server Information
            scan_results["server_info"] = await self.get_server_info()
            
            # 3. Tools Discovery and Analysis
            scan_results["tools_analysis"] = await self.analyze_tools()
            
            # 4. Capability Assessment
            scan_results["capabilities"] = await self.assess_capabilities(scan_results["tools_analysis"])
            
            # 5. Generate Recommendations
            scan_results["recommendations"] = self.generate_recommendations(scan_results)
            
            self.scan_results = scan_results
            return scan_results
            
        except Exception as e:
            logger.error(f"❌ Scan failed: {e}")
            return {"error": str(e)}
        finally:
            await self.client.aclose()
    
    async def check_server_health(self) -> Dict[str, Any]:
        """Check server health and basic connectivity"""
        logger.info("🏥 Checking server health...")
        
        health_info = {
            "status": "unknown",
            "response_time_ms": 0,
            "endpoints": {},
            "errors": []
        }
        
        try:
            # Test health endpoint
            start_time = time.time()
            response = await self.client.get(f"{self.server_url}/health")
            response_time = (time.time() - start_time) * 1000
            
            health_info["endpoints"]["/health"] = {
                "status_code": response.status_code,
                "response_time_ms": response_time,
                "available": response.status_code == 200
            }
            
            if response.status_code == 200:
                health_info["status"] = "healthy"
                health_info["response_time_ms"] = response_time
                logger.info(f"✅ Server is healthy (response time: {response_time:.2f}ms)")
            else:
                health_info["status"] = "unhealthy"
                health_info["errors"].append(f"Health endpoint returned {response.status_code}")
                logger.warning(f"⚠️ Server health check failed: {response.status_code}")
                
        except Exception as e:
            health_info["status"] = "unreachable"
            health_info["errors"].append(str(e))
            logger.error(f"❌ Cannot connect to server: {e}")
        
        return health_info
    
    async def get_server_info(self) -> Dict[str, Any]:
        """Get server information and metadata"""
        logger.info("ℹ️ Gathering server information...")
        
        server_info = {
            "url": self.server_url,
            "protocol": "HTTP",
            "endpoints": [],
            "metadata": {}
        }
        
        # Test common endpoints
        endpoints_to_test = [
            "/health",
            "/tools", 
            "/call",
            "/info",
            "/status",
            "/version"
        ]
        
        for endpoint in endpoints_to_test:
            try:
                response = await self.client.get(f"{self.server_url}{endpoint}")
                server_info["endpoints"].append({
                    "path": endpoint,
                    "status_code": response.status_code,
                    "available": response.status_code == 200,
                    "content_type": response.headers.get("content-type", "unknown")
                })
                
                if response.status_code == 200:
                    logger.info(f"✅ Endpoint {endpoint} is available")
                else:
                    logger.info(f"⚠️ Endpoint {endpoint} returned {response.status_code}")
                    
            except Exception as e:
                server_info["endpoints"].append({
                    "path": endpoint,
                    "status_code": None,
                    "available": False,
                    "error": str(e)
                })
                logger.debug(f"❌ Endpoint {endpoint} failed: {e}")
        
        return server_info
    
    async def analyze_tools(self) -> Dict[str, Any]:
        """Analyze available tools and their capabilities"""
        logger.info("🔧 Analyzing available tools...")
        
        tools_analysis = {
            "total_tools": 0,
            "tools_by_category": {},
            "tools_details": [],
            "calling_capabilities": False,
            "communication_capabilities": False,
            "system_capabilities": False
        }
        
        try:
            # Get tools list
            response = await self.client.get(f"{self.server_url}/tools")
            if response.status_code == 200:
                data = response.json()
                tools = data.get("tools", []) if isinstance(data, dict) else data
                
                tools_analysis["total_tools"] = len(tools)
                logger.info(f"📋 Found {len(tools)} tools")
                
                # Analyze each tool
                for tool in tools:
                    tool_name = tool.get("name", "unknown")
                    tool_desc = tool.get("description", "")
                    
                    tool_analysis = {
                        "name": tool_name,
                        "description": tool_desc,
                        "category": self.categorize_tool(tool_name, tool_desc),
                        "capabilities": self.analyze_tool_capabilities(tool_name, tool_desc),
                        "test_result": None
                    }
                    
                    # Test the tool if it's safe to test
                    if self.is_safe_to_test(tool_name):
                        tool_analysis["test_result"] = await self.test_tool_safely(tool_name)
                    
                    tools_analysis["tools_details"].append(tool_analysis)
                    
                    # Update category counts
                    category = tool_analysis["category"]
                    if category not in tools_analysis["tools_by_category"]:
                        tools_analysis["tools_by_category"][category] = []
                    tools_analysis["tools_by_category"][category].append(tool_name)
                    
                    # Update capability flags
                    if "calling" in tool_name.lower() or "call" in tool_name.lower() or "phone" in tool_name.lower():
                        tools_analysis["calling_capabilities"] = True
                    if "email" in tool_name.lower() or "mail" in tool_name.lower() or "send" in tool_name.lower():
                        tools_analysis["communication_capabilities"] = True
                    if "desktop" in tool_name.lower() or "file" in tool_name.lower() or "system" in tool_name.lower():
                        tools_analysis["system_capabilities"] = True
                
            else:
                logger.error(f"❌ Failed to get tools: {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ Error analyzing tools: {e}")
        
        return tools_analysis
    
    def categorize_tool(self, tool_name: str, description: str) -> str:
        """Categorize a tool based on its name and description"""
        tool_lower = tool_name.lower()
        desc_lower = description.lower()
        
        if any(word in tool_lower or word in desc_lower for word in ["call", "phone", "dial", "voice"]):
            return "calling"
        elif any(word in tool_lower or word in desc_lower for word in ["email", "mail", "send", "message"]):
            return "communication"
        elif any(word in tool_lower or word in desc_lower for word in ["desktop", "file", "folder", "path"]):
            return "system"
        elif any(word in tool_lower or word in desc_lower for word in ["count", "calculate", "compute"]):
            return "utility"
        elif any(word in tool_lower or word in desc_lower for word in ["browser", "open", "url", "web"]):
            return "browser"
        else:
            return "other"
    
    def analyze_tool_capabilities(self, tool_name: str, description: str) -> List[str]:
        """Analyze what a tool can do"""
        capabilities = []
        tool_lower = tool_name.lower()
        desc_lower = description.lower()
        
        if "count" in tool_lower:
            capabilities.append("text_processing")
        if "desktop" in tool_lower:
            capabilities.append("file_system_access")
        if "email" in tool_lower or "mail" in tool_lower:
            capabilities.append("email_sending")
        if "browser" in tool_lower or "open" in tool_lower:
            capabilities.append("browser_control")
        if "call" in tool_lower or "phone" in tool_lower:
            capabilities.append("voice_calling")
        
        return capabilities
    
    def is_safe_to_test(self, tool_name: str) -> bool:
        """Check if it's safe to test a tool"""
        safe_tools = ["count_r", "get_desktop_path", "list_desktop_contents"]
        return tool_name in safe_tools
    
    async def test_tool_safely(self, tool_name: str) -> Dict[str, Any]:
        """Safely test a tool with minimal impact"""
        try:
            if tool_name == "count_r":
                result = await self.client.post(f"{self.server_url}/call", json={
                    "tool": "count_r",
                    "params": {"word": "test"}
                })
                if result.status_code == 200:
                    return {"status": "success", "response": result.json()}
                else:
                    return {"status": "failed", "error": f"HTTP {result.status_code}"}
            
            elif tool_name == "get_desktop_path":
                result = await self.client.post(f"{self.server_url}/call", json={
                    "tool": "get_desktop_path",
                    "params": {"random_string": "test"}
                })
                if result.status_code == 200:
                    return {"status": "success", "response": result.json()}
                else:
                    return {"status": "failed", "error": f"HTTP {result.status_code}"}
            
            elif tool_name == "list_desktop_contents":
                result = await self.client.post(f"{self.server_url}/call", json={
                    "tool": "list_desktop_contents",
                    "params": {"random_string": "test"}
                })
                if result.status_code == 200:
                    return {"status": "success", "response": result.json()}
                else:
                    return {"status": "failed", "error": f"HTTP {result.status_code}"}
            
            else:
                return {"status": "not_tested", "reason": "not_safe"}
                
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def assess_capabilities(self, tools_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall server capabilities"""
        logger.info("🎯 Assessing server capabilities...")
        
        capabilities = {
            "calling": {
                "available": tools_analysis.get("calling_capabilities", False),
                "tools": tools_analysis.get("tools_by_category", {}).get("calling", []),
                "readiness": "not_ready"
            },
            "communication": {
                "available": tools_analysis.get("communication_capabilities", False),
                "tools": tools_analysis.get("tools_by_category", {}).get("communication", []),
                "readiness": "ready"
            },
            "system": {
                "available": tools_analysis.get("system_capabilities", False),
                "tools": tools_analysis.get("tools_by_category", {}).get("system", []),
                "readiness": "ready"
            },
            "browser": {
                "available": "browser" in tools_analysis.get("tools_by_category", {}),
                "tools": tools_analysis.get("tools_by_category", {}).get("browser", []),
                "readiness": "ready"
            }
        }
        
        # Assess calling readiness
        if capabilities["calling"]["available"]:
            capabilities["calling"]["readiness"] = "ready"
        else:
            capabilities["calling"]["readiness"] = "needs_implementation"
        
        return capabilities
    
    def generate_recommendations(self, scan_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate recommendations based on scan results"""
        logger.info("💡 Generating recommendations...")
        
        recommendations = {
            "calling_implementation": [],
            "enhancements": [],
            "integration_notes": [],
            "next_steps": []
        }
        
        capabilities = scan_results.get("capabilities", {})
        
        # Calling recommendations
        if not capabilities.get("calling", {}).get("available", False):
            recommendations["calling_implementation"].extend([
                "Add calling tools to MCP server (e.g., make_call, dial_number)",
                "Implement voice calling capabilities using Twilio or similar service",
                "Add call management tools (answer_call, end_call, transfer_call)",
                "Include call recording and transcription capabilities"
            ])
        
        # Enhancement recommendations
        if capabilities.get("communication", {}).get("available", False):
            recommendations["enhancements"].append("Email capabilities are ready - can integrate with calling")
        
        if capabilities.get("system", {}).get("available", False):
            recommendations["enhancements"].append("System tools available - can enhance calling with file operations")
        
        # Integration notes
        recommendations["integration_notes"].extend([
            "Server is healthy and responsive",
            f"Found {scan_results.get('tools_analysis', {}).get('total_tools', 0)} total tools",
            "HTTP-based MCP server ready for integration"
        ])
        
        # Next steps
        if capabilities.get("calling", {}).get("readiness") == "needs_implementation":
            recommendations["next_steps"].extend([
                "1. Implement calling tools in MCP server",
                "2. Test calling functionality",
                "3. Integrate with existing communication tools",
                "4. Create calling agent that uses MCP tools"
            ])
        else:
            recommendations["next_steps"].extend([
                "1. Create calling agent that uses existing MCP tools",
                "2. Test calling workflows",
                "3. Integrate with RAG system"
            ])
        
        return recommendations
    
    def print_scan_report(self, scan_results: Dict[str, Any]):
        """Print formatted scan report"""
        print("\n" + "="*80)
        print("🔍 MCP SERVER SCAN REPORT")
        print("="*80)
        
        # Server Health
        health = scan_results.get("health_status", {})
        print(f"\n🏥 SERVER HEALTH:")
        print(f"   Status: {health.get('status', 'unknown')}")
        print(f"   Response Time: {health.get('response_time_ms', 0):.2f}ms")
        
        # Tools Summary
        tools_analysis = scan_results.get("tools_analysis", {})
        print(f"\n🔧 TOOLS SUMMARY:")
        print(f"   Total Tools: {tools_analysis.get('total_tools', 0)}")
        
        # Tools by Category
        categories = tools_analysis.get("tools_by_category", {})
        for category, tools in categories.items():
            print(f"   {category.title()}: {len(tools)} tools")
            for tool in tools:
                print(f"     - {tool}")
        
        # Capabilities Assessment
        capabilities = scan_results.get("capabilities", {})
        print(f"\n🎯 CAPABILITIES ASSESSMENT:")
        for cap_name, cap_info in capabilities.items():
            status = "✅" if cap_info.get("available", False) else "❌"
            readiness = cap_info.get("readiness", "unknown")
            print(f"   {status} {cap_name.title()}: {readiness}")
        
        # Recommendations
        recommendations = scan_results.get("recommendations", {})
        print(f"\n💡 KEY RECOMMENDATIONS:")
        
        if recommendations.get("calling_implementation"):
            print("   📞 Calling Implementation Needed:")
            for rec in recommendations["calling_implementation"][:3]:  # Show first 3
                print(f"     • {rec}")
        
        if recommendations.get("next_steps"):
            print("   🚀 Next Steps:")
            for step in recommendations["next_steps"][:3]:  # Show first 3
                print(f"     • {step}")
        
        print("\n" + "="*80)
        print("✅ Scan completed!")
        print("="*80)

async def main():
    """Main function to run the scanner"""
    scanner = MCPServerScanner()
    
    try:
        # Run comprehensive scan
        scan_results = await scanner.scan_server()
        
        if "error" in scan_results:
            print(f"❌ Scan failed: {scan_results['error']}")
            return
        
        # Print formatted report
        scanner.print_scan_report(scan_results)
        
        # Save detailed report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"mcp_server_scan_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(scan_results, f, indent=2)
        
        print(f"\n💾 Detailed scan report saved to: {filename}")
        
    except Exception as e:
        logger.error(f"❌ Scanner failed: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 