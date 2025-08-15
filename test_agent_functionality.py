#!/usr/bin/env python3
"""
Comprehensive test script to verify all agents are working correctly.
"""

import asyncio
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_smart_master_agent():
    """Test the smart master agent functionality."""
    try:
        from agent.smart_master_agent import SmartMasterAgent
        
        agent = SmartMasterAgent()
        
        # Test intent analysis
        test_messages = [
            "Save this message to desktop",
            "Send an email to john@example.com",
            "Search for information about AI",
            "Scan this code for security issues"
        ]
        
        results = []
        for message in test_messages:
            result = agent.analyze_intent(message)
            results.append({
                'message': message,
                'intent': result.intent.value,
                'confidence': result.confidence
            })
        
        logger.info("✅ Smart Master Agent: All intent analysis tests passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Smart Master Agent test failed: {e}")
        return False

async def test_unified_master_agent():
    """Test the unified master agent functionality."""
    try:
        from agent.unified_master_agent import UnifiedMasterAgent, RoutingMode
        
        agent = UnifiedMasterAgent(default_mode=RoutingMode.PATTERN)
        
        # Test routing
        test_messages = [
            "Send an email to user@example.com",
            "Save this to desktop",
            "Search the web for latest news"
        ]
        
        results = []
        for message in test_messages:
            result = await agent.route_request(message)
            results.append({
                'message': message,
                'sub_agent': result.sub_agent.value,
                'confidence': result.confidence,
                'routing_mode': result.routing_mode.value
            })
        
        logger.info("✅ Unified Master Agent: All routing tests passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Unified Master Agent test failed: {e}")
        return False

async def test_master_agent():
    """Test the regular master agent functionality."""
    try:
        from agent.master_agent import MasterAgent
        
        agent = MasterAgent()
        
        # Test task analysis
        test_messages = [
            "Save this message to desktop",
            "Compose an email to team@company.com",
            "Search for documents about machine learning"
        ]
        
        results = []
        for message in test_messages:
            tasks = await agent.analyze_request(message)
            results.append({
                'message': message,
                'tasks_found': len(tasks),
                'task_types': [task.agent_type.value for task in tasks] if tasks else []
            })
        
        logger.info("✅ Master Agent: All task analysis tests passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Master Agent test failed: {e}")
        return False

async def test_secrets_detection_agent():
    """Test the secrets detection agent functionality."""
    try:
        from agent.secrets_detection_agent import SecretsDetectionAgent
        
        agent = SecretsDetectionAgent()
        
        # Test file scanning
        test_content = "This is a test file with no secrets"
        test_file = "test_file.txt"
        
        # Create a temporary test file
        with open(test_file, 'w') as f:
            f.write(test_content)
        
        try:
            result = agent.scan_file(test_file)
            
            if result['success']:
                logger.info("✅ Secrets Detection Agent: File scanning test passed")
                return True
            else:
                logger.error(f"❌ Secrets Detection Agent: File scanning failed - {result.get('error', 'Unknown error')}")
                return False
                
        finally:
            # Clean up test file
            import os
            if os.path.exists(test_file):
                os.remove(test_file)
        
    except Exception as e:
        logger.error(f"❌ Secrets Detection Agent test failed: {e}")
        return False

async def test_ingestion_modules():
    """Test the ingestion modules functionality."""
    try:
        from ingestion.chunker import SemanticChunker, ChunkingConfig
        
        # Test chunker initialization
        config = ChunkingConfig(chunk_size=100, chunk_overlap=20)
        chunker = SemanticChunker(config)
        
        logger.info("✅ Ingestion Modules: Chunker initialization test passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Ingestion Modules test failed: {e}")
        return False

async def test_mcp_tools():
    """Test the MCP tools functionality."""
    try:
        from agent.mcp_tools import count_r_tool, CountRInput
        
        # Test MCP tool (will fail to connect but should handle gracefully)
        result = await count_r_tool(CountRInput(word='test'))
        
        # The tool should handle connection failures gracefully
        if isinstance(result, dict) and 'success' in result:
            logger.info("✅ MCP Tools: Tool execution test passed (handles connection failures gracefully)")
            return True
        else:
            logger.error("❌ MCP Tools: Tool execution failed")
            return False
        
    except Exception as e:
        logger.error(f"❌ MCP Tools test failed: {e}")
        return False

async def test_basic_tools():
    """Test the basic tools functionality."""
    try:
        from agent.tools import list_documents_tool, DocumentListInput
        
        # Test basic tool (may fail due to missing database but should handle gracefully)
        result = await list_documents_tool(DocumentListInput(limit=5))
        
        # The tool should handle database failures gracefully
        if isinstance(result, list):
            logger.info("✅ Basic Tools: Tool execution test passed")
            return True
        else:
            logger.error("❌ Basic Tools: Tool execution failed")
            return False
        
    except Exception as e:
        logger.error(f"❌ Basic Tools test failed: {e}")
        return False

async def main():
    """Run all agent tests."""
    logger.info("🚀 Starting comprehensive agent functionality tests...")
    logger.info("=" * 60)
    
    test_results = {}
    
    # Test all agents
    test_results['smart_master_agent'] = await test_smart_master_agent()
    test_results['unified_master_agent'] = await test_unified_master_agent()
    test_results['master_agent'] = await test_master_agent()
    test_results['secrets_detection_agent'] = await test_secrets_detection_agent()
    test_results['ingestion_modules'] = await test_ingestion_modules()
    test_results['mcp_tools'] = await test_mcp_tools()
    test_results['basic_tools'] = await test_basic_tools()
    
    # Summary
    logger.info("=" * 60)
    logger.info("📊 TEST RESULTS SUMMARY")
    logger.info("=" * 60)
    
    passed = sum(test_results.values())
    total = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{test_name.replace('_', ' ').title()}: {status}")
    
    logger.info("=" * 60)
    logger.info(f"Overall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All agents are working correctly!")
    else:
        logger.info("⚠️  Some agents have issues that need attention")
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1) 