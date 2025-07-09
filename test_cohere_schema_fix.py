#!/usr/bin/env python3
"""
Test script to verify Cohere schema validation fix.
"""

import os
import asyncio
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_cohere_schema_validation():
    """Test that Cohere can properly validate tool schemas."""
    
    # Set up Cohere environment
    os.environ['LLM_PROVIDER'] = 'cohere'
    os.environ['LLM_CHOICE'] = 'command-r-plus'
    os.environ['EMBEDDING_PROVIDER'] = 'cohere'
    os.environ['EMBEDDING_MODEL'] = 'embed-english-v3.0'
    
    # Check required environment variables
    required_vars = ['LLM_API_KEY', 'EMBEDDING_API_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        logger.error("Please set these variables in your .env file")
        return False
    
    try:
        # Import after setting environment variables
        from agent.agent import rag_agent, initialize_cohere_schema_patching
        from agent.tools import EntityTimelineInput, VectorSearchInput, HybridSearchInput
        
        # Initialize schema patching after agent is imported
        initialize_cohere_schema_patching()
        
        logger.info("Testing tool input model validation...")
        
        # Test EntityTimelineInput with explicit type annotations
        timeline_input = EntityTimelineInput(
            entity_name="Microsoft",
            start_date="2023-01-01",
            end_date="2024-01-01"
        )
        logger.info(f"✓ EntityTimelineInput validation passed: {timeline_input}")
        
        # Test VectorSearchInput with explicit type annotations
        vector_input = VectorSearchInput(
            query="AI technology",
            limit=5
        )
        logger.info(f"✓ VectorSearchInput validation passed: {vector_input}")
        
        # Test HybridSearchInput with explicit type annotations
        hybrid_input = HybridSearchInput(
            query="machine learning",
            limit=10,
            text_weight=0.5
        )
        logger.info(f"✓ HybridSearchInput validation passed: {hybrid_input}")
        
        # Test agent initialization
        logger.info("Testing agent initialization...")
        logger.info(f"Agent model: {rag_agent.model}")
        logger.info("✓ Agent initialization successful")
        
        # Test a simple agent call
        logger.info("Testing simple agent call...")
        try:
            response = await rag_agent.run(
                "Hello, can you help me search for information about Microsoft?",
                deps={"session_id": "test-session-123"}
            )
            logger.info("✓ Agent call successful")
            logger.info(f"Response: {response}")
        except Exception as e:
            logger.error(f"✗ Agent call failed: {e}")
            return False
        
        logger.info("✓ All schema validation tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"✗ Schema validation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_cohere_schema_validation())
    if success:
        print("\n🎉 Cohere schema validation fix verified successfully!")
    else:
        print("\n❌ Schema validation test failed!")
        exit(1) 