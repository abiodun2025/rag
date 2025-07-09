#!/usr/bin/env python3
"""
Debug script to examine schema generation for Cohere.
"""

import os
import json
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def debug_schema():
    """Debug the schema generation for tools."""

# Set up Cohere environment
os.environ['LLM_PROVIDER'] = 'cohere'
os.environ['LLM_CHOICE'] = 'command-r-plus'
os.environ['EMBEDDING_PROVIDER'] = 'cohere'
os.environ['EMBEDDING_MODEL'] = 'embed-english-v3.0'
    
    try:
        from agent.agent import rag_agent, initialize_cohere_schema_patching
        from agent.tools import EntityTimelineInput
        
        # Initialize schema patching
        initialize_cohere_schema_patching()
        
        # Get all tools
        tools = getattr(rag_agent, '_tools', {})
        logger.info(f"Found {len(tools)} tools")
        
        for tool_name, tool in tools.items():
            logger.info(f"\n=== Tool: {tool_name} ===")
            
            if hasattr(tool, 'function_schema'):
                schema = tool.function_schema
                logger.info(f"Function schema: {schema}")
                
                if hasattr(schema, 'parameters_json_schema'):
                    params_schema = schema.parameters_json_schema
                    logger.info(f"Parameters schema: {json.dumps(params_schema, indent=2)}")
                    
                    # Check for start_date specifically
                    if 'properties' in params_schema:
                        for prop_name, prop_schema in params_schema['properties'].items():
                            if prop_name in ['start_date', 'end_date']:
                                logger.info(f"Property {prop_name} schema: {json.dumps(prop_schema, indent=2)}")
                else:
                    logger.warning(f"No parameters_json_schema found for {tool_name}")
            else:
                logger.warning(f"No function_schema found for {tool_name}")
        
        # Also test the EntityTimelineInput model directly
        logger.info("\n=== EntityTimelineInput Model Schema ===")
        model_schema = EntityTimelineInput.model_json_schema()
        logger.info(f"Model schema: {json.dumps(model_schema, indent=2)}")
        
    except Exception as e:
        logger.error(f"Debug failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_schema() 