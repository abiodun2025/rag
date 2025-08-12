#!/usr/bin/env python3
"""
Secrets Detection Agent
Uses MCP server tools to scan for secrets, API keys, passwords, and tokens in files and directories.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecretsDetectionAgent:
    """Agent for detecting secrets and security vulnerabilities using MCP server tools."""
    
    def __init__(self, mcp_server_url: str = "http://127.0.0.1:5000"):
        """Initialize the secrets detection agent."""
        self.mcp_server_url = mcp_server_url
        self.agent_name = "Secrets Detection Agent"
        self.version = "1.0.0"
        self.description = "Scans files and directories for secrets, API keys, passwords, and tokens"
        
        logger.info(f"🔐 {self.agent_name} initialized (v{self.version})")
        logger.info(f"🔗 Connected to MCP server: {mcp_server_url}")
    
    async def scan_file_for_secrets(self, file_path: str) -> Dict[str, Any]:
        """Scan a specific file for secrets using MCP server tools."""
        try:
            logger.info(f"🔍 Scanning file for secrets: {file_path}")
            
            # Call MCP server tool
            result = await self._call_mcp_tool("scan_file_for_secrets", {
                "file_path": file_path
            })
            
            if result.get("success"):
                logger.info(f"✅ File scan completed: {result.get('scan_summary')}")
                return {
                    "success": True,
                    "scan_type": "file",
                    "file_path": file_path,
                    "results": result,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                logger.error(f"❌ File scan failed: {result.get('error')}")
                return {
                    "success": False,
                    "scan_type": "file",
                    "file_path": file_path,
                    "error": result.get('error'),
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"❌ File scan error: {e}")
            return {
                "success": False,
                "scan_type": "file",
                "file_path": file_path,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def scan_directory_for_secrets(self, directory_path: str, recursive: bool = True) -> Dict[str, Any]:
        """Scan a directory for files that might contain secrets."""
        try:
            logger.info(f"🔍 Scanning directory for secrets: {directory_path}")
            
            # Call MCP server tool
            result = await self._call_mcp_tool("scan_directory_for_secrets", {
                "directory_path": directory_path,
                "recursive": recursive
            })
            
            if result.get("success"):
                logger.info(f"✅ Directory scan completed: {result.get('scan_summary')}")
                return {
                    "success": True,
                    "scan_type": "directory",
                    "directory_path": directory_path,
                    "results": result,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                logger.error(f"❌ Directory scan failed: {result.get('error')}")
                return {
                    "success": False,
                    "scan_type": "directory",
                    "directory_path": directory_path,
                    "error": result.get('error'),
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"❌ Directory scan error: {e}")
            return {
                "success": False,
                "scan_type": "directory",
                "directory_path": directory_path,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def scan_env_files(self, directory_path: str) -> Dict[str, Any]:
        """Scan environment files for secrets."""
        try:
            logger.info(f"🔍 Scanning env files: {directory_path}")
            
            # Call MCP server tool
            result = await self._call_mcp_tool("scan_env_files", {
                "directory_path": directory_path
            })
            
            if result.get("success"):
                logger.info(f"✅ Env files scan completed: {result.get('scan_summary')}")
                return {
                    "success": True,
                    "scan_type": "env_files",
                    "directory_path": directory_path,
                    "results": result,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                logger.error(f"❌ Env files scan failed: {result.get('error')}")
                return {
                    "success": False,
                    "scan_type": "env_files",
                    "directory_path": directory_path,
                    "error": result.get('error'),
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"❌ Env files scan error: {e}")
            return {
                "success": False,
                "scan_type": "env_files",
                "directory_path": directory_path,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def generate_security_report(self, directory_path: str) -> Dict[str, Any]:
        """Generate a comprehensive security report."""
        try:
            logger.info(f"📊 Generating security report: {directory_path}")
            
            # Call MCP server tool
            result = await self._call_mcp_tool("generate_security_report", {
                "directory_path": directory_path
            })
            
            if result.get("success"):
                logger.info(f"✅ Security report generated successfully")
                return {
                    "success": True,
                    "report_type": "security",
                    "directory_path": directory_path,
                    "report": result.get("report"),
                    "timestamp": datetime.now().isoformat()
                }
            else:
                logger.error(f"❌ Security report generation failed: {result.get('error')}")
                return {
                    "success": False,
                    "report_type": "security",
                    "directory_path": directory_path,
                    "error": result.get('error'),
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"❌ Security report generation error: {e}")
            return {
                "success": False,
                "report_type": "security",
                "directory_path": directory_path,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def detect_api_keys(self, content: str = "", file_path: str = "") -> Dict[str, Any]:
        """Detect API keys in content or file."""
        try:
            logger.info(f"🔑 Detecting API keys")
            
            # Call MCP server tool
            result = await self._call_mcp_tool("detect_api_keys", {
                "content": content,
                "file_path": file_path
            })
            
            if result.get("success"):
                logger.info(f"✅ API key detection completed: {result.get('scan_summary')}")
                return {
                    "success": True,
                    "detection_type": "api_keys",
                    "results": result,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                logger.error(f"❌ API key detection failed: {result.get('error')}")
                return {
                    "success": False,
                    "detection_type": "api_keys",
                    "error": result.get('error'),
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"❌ API key detection error: {e}")
            return {
                "success": False,
                "detection_type": "api_keys",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def detect_passwords(self, content: str = "", file_path: str = "") -> Dict[str, Any]:
        """Detect passwords in content or file."""
        try:
            logger.info(f"🔒 Detecting passwords")
            
            # Call MCP server tool
            result = await self._call_mcp_tool("detect_passwords", {
                "content": content,
                "file_path": file_path
            })
            
            if result.get("success"):
                logger.info(f"✅ Password detection completed: {result.get('scan_summary')}")
                return {
                    "success": True,
                    "detection_type": "passwords",
                    "results": result,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                logger.error(f"❌ Password detection failed: {result.get('error')}")
                return {
                    "success": False,
                    "detection_type": "passwords",
                    "error": result.get('error'),
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"❌ Password detection error: {e}")
            return {
                "success": False,
                "detection_type": "passwords",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def detect_tokens(self, content: str = "", file_path: str = "") -> Dict[str, Any]:
        """Detect tokens in content or file."""
        try:
            logger.info(f"🎫 Detecting tokens")
            
            # Call MCP server tool
            result = await self._call_mcp_tool("detect_tokens", {
                "content": content,
                "file_path": file_path
            })
            
            if result.get("success"):
                logger.info(f"✅ Token detection completed: {result.get('scan_summary')}")
                return {
                    "success": True,
                    "detection_type": "tokens",
                    "results": result,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                logger.error(f"❌ Token detection failed: {result.get('error')}")
                return {
                    "success": False,
                    "detection_type": "tokens",
                    "error": result.get('error'),
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"❌ Token detection error: {e}")
            return {
                "success": False,
                "detection_type": "tokens",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def run_comprehensive_scan(self, directory_path: str) -> Dict[str, Any]:
        """Run a comprehensive security scan including all detection methods."""
        try:
            logger.info(f"🚀 Running comprehensive security scan: {directory_path}")
            
            # Run all scans in parallel
            tasks = [
                self.scan_directory_for_secrets(directory_path),
                self.scan_env_files(directory_path),
                self.generate_security_report(directory_path)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            scan_results = {
                "directory_scan": results[0] if not isinstance(results[0], Exception) else {"error": str(results[0])},
                "env_scan": results[1] if not isinstance(results[1], Exception) else {"error": str(results[1])},
                "security_report": results[2] if not isinstance(results[2], Exception) else {"error": str(results[2])}
            }
            
            # Calculate overall success
            overall_success = all(
                isinstance(result, dict) and result.get("success", False) 
                for result in results if not isinstance(result, Exception)
            )
            
            logger.info(f"✅ Comprehensive scan completed: {'Success' if overall_success else 'Partial success'}")
            
            return {
                "success": overall_success,
                "scan_type": "comprehensive",
                "directory_path": directory_path,
                "results": scan_results,
                "timestamp": datetime.now().isoformat(),
                "summary": {
                    "total_scans": len(tasks),
                    "successful_scans": sum(1 for r in results if isinstance(r, dict) and r.get("success")),
                    "failed_scans": sum(1 for r in results if isinstance(r, Exception))
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Comprehensive scan error: {e}")
            return {
                "success": False,
                "scan_type": "comprehensive",
                "directory_path": directory_path,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _call_mcp_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call an MCP server tool."""
        try:
            import aiohttp
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.mcp_server_url}/call",
                    json={
                        "tool": tool_name,
                        "arguments": arguments
                    },
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result
                    else:
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}: {response.reason}"
                        }
                        
        except Exception as e:
            logger.error(f"❌ MCP tool call failed: {e}")
            return {
                "success": False,
                "error": f"Failed to call MCP tool {tool_name}: {str(e)}"
            }
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about the agent."""
        return {
            "agent_name": self.agent_name,
            "version": self.version,
            "description": self.description,
            "mcp_server_url": self.mcp_server_url,
            "capabilities": [
                "File scanning for secrets",
                "Directory scanning for secrets",
                "Environment file scanning",
                "API key detection",
                "Password detection",
                "Token detection",
                "Security report generation",
                "Comprehensive security scanning"
            ],
            "timestamp": datetime.now().isoformat()
        }

# Example usage and testing
async def main():
    """Example usage of the Secrets Detection Agent."""
    agent = SecretsDetectionAgent()
    
    print("🔐 Secrets Detection Agent Demo")
    print("=" * 50)
    
    # Get agent info
    info = agent.get_agent_info()
    print(f"Agent: {info['agent_name']} v{info['version']}")
    print(f"Description: {info['description']}")
    print(f"MCP Server: {info['mcp_server_url']}")
    print()
    
    # Test file scanning
    print("🔍 Testing file scanning...")
    result = await agent.scan_file_for_secrets(".env")
    if result["success"]:
        print(f"✅ File scan successful: {result['results']['scan_summary']}")
        print(f"   Found {result['results']['total_secrets']} secrets")
    else:
        print(f"❌ File scan failed: {result['error']}")
    
    print()
    
    # Test directory scanning
    print("🔍 Testing directory scanning...")
    result = await agent.scan_directory_for_secrets(".", recursive=False)
    if result["success"]:
        print(f"✅ Directory scan successful: {result['results']['scan_summary']}")
        print(f"   Scanned {result['results']['files_scanned']} files")
    else:
        print(f"❌ Directory scan failed: {result['error']}")
    
    print()
    
    # Test comprehensive scan
    print("🚀 Testing comprehensive scan...")
    result = await agent.run_comprehensive_scan(".")
    if result["success"]:
        print(f"✅ Comprehensive scan successful")
        print(f"   Summary: {result['summary']}")
    else:
        print(f"❌ Comprehensive scan failed: {result['error']}")

if __name__ == "__main__":
    asyncio.run(main())
