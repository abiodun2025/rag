"""
Main Pydantic AI agent for agentic RAG with knowledge graph.
"""

import os
import logging
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime
import copy
import json
import time

from pydantic_ai import Agent, RunContext
from dotenv import load_dotenv

from .prompts import SYSTEM_PROMPT
from .providers import get_llm_model, get_llm_provider, get_llm_model_name
from .schemas import ProviderType, convert_to_provider_format, convert_from_provider_format
from .tools import (
    vector_search_tool,
    graph_search_tool,
    hybrid_search_tool,
    get_document_tool,
    list_documents_tool,
    get_entity_relationships_tool,
    get_entity_timeline_tool,
    VectorSearchInput,
    GraphSearchInput,
    HybridSearchInput,
    DocumentInput,
    DocumentListInput,
    EntityRelationshipInput,
    EntityTimelineInput,
    web_search_tool,  # <-- Import the tool
    WebSearchInput,    # <-- Import the input model
    compose_email_tool, # <-- Import the email tool
    EmailComposeInput   # <-- Import the email input model
)

# Load environment variables
load_dotenv()
print("DEBUG >>> NEO4J_PASSWORD:", os.getenv("NEO4J_PASSWORD"))
logger = logging.getLogger(__name__)

# Enhanced debug logging setup
def setup_agent_debug_logging():
    """Setup enhanced debug logging for the agent."""
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("Debug logging enabled for RAG agent")
        logger.debug("Environment variables loaded")
        logger.debug("LLM model: %s", os.getenv('LLM_CHOICE', 'gpt-4-turbo-preview'))
        logger.debug("Embedding model: %s", os.getenv('EMBEDDING_MODEL', 'text-embedding-3-small'))

# Initialize debug logging
setup_agent_debug_logging()


@dataclass
class AgentDependencies:
    """Dependencies for the agent."""
    session_id: str
    user_id: Optional[str] = None
    search_preferences: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.search_preferences is None:
            self.search_preferences = {
                "use_vector": True,
                "use_graph": True,
                "default_limit": 10
            }


def patch_schema_for_cohere(schema):
    """Recursively patch schema to replace anyOf string/null with type 'string' (Cohere v1 quirk)."""
    if isinstance(schema, dict):
        # Patch properties
        if 'properties' in schema:
            for k, v in schema['properties'].items():
                schema['properties'][k] = patch_schema_for_cohere(v)
        # Patch anyOf string/null
        if 'anyOf' in schema:
            anyof = schema['anyOf']
            if (
                len(anyof) == 2 and
                {'type': 'string'} in anyof and
                {'type': 'null'} in anyof
            ):
                new_schema = copy.deepcopy(schema)
                new_schema.pop('anyOf')
                new_schema['type'] = 'string'
                # Remove default: null if present
                if 'default' in new_schema and new_schema['default'] is None:
                    del new_schema['default']
                return new_schema
        # Recurse into nested schemas
        for k, v in schema.items():
            schema[k] = patch_schema_for_cohere(v)
    elif isinstance(schema, list):
        return [patch_schema_for_cohere(item) for item in schema]
    return schema


# Initialize the agent with flexible model configuration
def get_agent_model():
    """Get the model string for the agent based on provider."""
    provider = get_llm_provider()
    model_choice = get_llm_model_name()
    
    if provider.lower() == 'cohere':
        # Set CO_API_KEY for pydantic_ai's Cohere provider
        llm_api_key = os.getenv('LLM_API_KEY')
        if llm_api_key:
            os.environ['CO_API_KEY'] = llm_api_key
        # Use pydantic_ai's built-in Cohere support
        return f"cohere:{model_choice}"
    else:
        # For other providers, use the model name directly
        return model_choice

rag_agent = Agent(
    get_agent_model(),
    deps_type=AgentDependencies,
    system_prompt=SYSTEM_PROMPT
)

# Patch all tool schemas for Cohere compatibility after all tools are registered
def patch_all_tool_schemas_for_cohere():
    """Patch all registered tool schemas for Cohere compatibility."""
    if get_llm_provider().lower() != 'cohere':
        return
    
    logger.debug("Patching tool schemas for Cohere compatibility")
    
    # Get all registered tools
    tools = getattr(rag_agent, '_tools', {})
    if not tools:
        logger.warning("No tools found to patch - this might be because tools are not yet registered")
        return
    
    logger.info(f"Found {len(tools)} tools to patch")
    
    for tool_name, tool in tools.items():
        try:
            if hasattr(tool, 'function_schema') and hasattr(tool.function_schema, 'parameters_json_schema'):
                orig_schema = tool.function_schema.parameters_json_schema
                patched_schema = patch_schema_for_cohere(copy.deepcopy(orig_schema))
                tool.function_schema.parameters_json_schema = patched_schema
                logger.debug(f"Patched schema for tool: {tool_name}")
        except Exception as e:
            logger.warning(f"Failed to patch tool {tool_name}: {e}")

# Function to patch schemas after agent is fully initialized
def initialize_cohere_schema_patching():
    """Initialize Cohere schema patching after all tools are registered."""
    # Force tool registration by accessing the agent
    _ = rag_agent._tools
    patch_all_tool_schemas_for_cohere()

# Schema patching removed - fixed at model level

# Register tools with proper docstrings (no description parameter)
@rag_agent.tool
async def vector_search(
    ctx: RunContext[AgentDependencies],
    query: str,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Search for relevant information using semantic similarity.
    
    This tool performs vector similarity search across document chunks
    to find semantically related content. Returns the most relevant results
    regardless of similarity score.
    
    Args:
        query: Search query to find similar content
        limit: Maximum number of results to return (1-50)
    
    Returns:
        List of matching chunks ordered by similarity (best first)
    """
    logger.debug("Vector search tool called with query: '%s', limit: %d", query, limit)
    logger.debug("Session ID: %s", ctx.deps.session_id)
    
    input_data = VectorSearchInput(
        query=query,
        limit=limit
    )
    
    logger.debug("Calling vector_search_tool with input: %s", input_data)
    start_time = datetime.now()
    
    try:
        results = await vector_search_tool(input_data)
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds() * 1000
        
        logger.debug("Vector search completed in %.2f ms, found %d results", duration, len(results))
        
        # Convert results to dict for agent
        converted_results = [
            {
                "content": r.content,
                "score": r.score,
                "document_title": r.document_title,
                "document_source": r.document_source,
                "chunk_id": r.chunk_id
            }
            for r in results
        ]
        
        logger.debug("Converted %d results for agent", len(converted_results))
        return converted_results
        
    except Exception as e:
        logger.error("Vector search failed: %s", e)
        logger.debug("Vector search error details", exc_info=True)
        raise


@rag_agent.tool
async def graph_search(
    ctx: RunContext[AgentDependencies],
    query: str
) -> List[Dict[str, Any]]:
    """
    Search the knowledge graph for facts and relationships.
    
    This tool queries the knowledge graph to find specific facts, relationships 
    between entities, and temporal information. Best for finding specific facts,
    relationships between companies/people/technologies, and time-based information.
    
    Args:
        query: Search query to find facts and relationships
    
    Returns:
        List of facts with associated episodes and temporal data
    """
    logger.debug("Graph search tool called with query: '%s'", query)
    logger.debug("Session ID: %s", ctx.deps.session_id)
    
    input_data = GraphSearchInput(query=query)
    
    logger.debug("Calling graph_search_tool with input: %s", input_data)
    start_time = datetime.now()
    
    try:
        results = await graph_search_tool(input_data)
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds() * 1000
        
        logger.debug("Graph search completed in %.2f ms, found %d results", duration, len(results))
        
        # Convert results to dict for agent with schema mapping
        provider = ProviderType.COHERE  # Default to Cohere for now
        converted_results = []
        
        for r in results:
            # Create base result dict
            result_dict = {
                "fact": r.fact,
                "uuid": r.uuid,
                "valid_at": r.valid_at,
                "invalid_at": r.invalid_at,
                "source_node_uuid": r.source_node_uuid
            }
            
            # Convert to provider format to ensure compatibility
            provider_data = convert_to_provider_format(result_dict, provider)
            
            # Convert back to database format for agent consumption
            db_data = convert_from_provider_format(provider_data, provider, "relationship")
            
            converted_results.append(db_data)
        
        logger.debug("Converted %d graph results for agent", len(converted_results))
        return converted_results
        
    except Exception as e:
        logger.error("Graph search failed: %s", e)
        logger.debug("Graph search error details", exc_info=True)
        raise


@rag_agent.tool
async def hybrid_search(
    ctx: RunContext[AgentDependencies],
    query: str,
    limit: int = 10,
    text_weight: float = 0.3
) -> List[Dict[str, Any]]:
    """
    Perform both vector and keyword search for comprehensive results.
    
    This tool combines semantic similarity search with keyword matching
    for the best coverage. It ranks results using both vector similarity
    and text matching scores. Best for combining semantic and exact matching.
    
    Args:
        query: Search query for hybrid search
        limit: Maximum number of results to return (1-50)
        text_weight: Weight for text similarity vs vector similarity (0.0-1.0)
    
    Returns:
        List of chunks ranked by combined relevance score
    """
    logger.debug("Hybrid search tool called with query: '%s', limit: %d, text_weight: %.2f", query, limit, text_weight)
    logger.debug("Session ID: %s", ctx.deps.session_id)
    
    input_data = HybridSearchInput(
        query=query,
        limit=limit,
        text_weight=text_weight
    )
    
    logger.debug("Calling hybrid_search_tool with input: %s", input_data)
    start_time = datetime.now()
    
    try:
        results = await hybrid_search_tool(input_data)
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds() * 1000
        
        logger.debug("Hybrid search completed in %.2f ms, found %d results", duration, len(results))
        
        # Convert results to dict for agent
        converted_results = [
            {
                "content": r.content,
                "score": r.score,
                "document_title": r.document_title,
                "document_source": r.document_source,
                "chunk_id": r.chunk_id
            }
            for r in results
        ]
        
        logger.debug("Converted %d hybrid results for agent", len(converted_results))
        return converted_results
        
    except Exception as e:
        logger.error("Hybrid search failed: %s", e)
        logger.debug("Hybrid search error details", exc_info=True)
        raise


@rag_agent.tool
async def get_document(
    ctx: RunContext[AgentDependencies],
    document_id: str
) -> Optional[Dict[str, Any]]:
    """
    Retrieve the complete content of a specific document.
    
    This tool fetches the full document content along with all its chunks
    and metadata. Best for getting comprehensive information from a specific
    source when you need the complete context.
    
    Args:
        document_id: UUID of the document to retrieve
    
    Returns:
        Complete document data with content and metadata, or None if not found
    """
    input_data = DocumentInput(document_id=document_id)
    
    document = await get_document_tool(input_data)
    
    if document:
        # Format for agent consumption
        return {
            "id": document["id"],
            "title": document["title"],
            "source": document["source"],
            "content": document["content"],
            "chunk_count": len(document.get("chunks", [])),
            "created_at": document["created_at"]
        }
    
    return None


@rag_agent.tool
async def list_documents(
    ctx: RunContext[AgentDependencies],
    limit: int = 20,
    offset: int = 0
) -> List[Dict[str, Any]]:
    """
    List available documents with their metadata.
    
    This tool provides an overview of all documents in the knowledge base,
    including titles, sources, and chunk counts. Best for understanding
    what information sources are available.
    
    Args:
        limit: Maximum number of documents to return (1-100)
        offset: Number of documents to skip for pagination
    
    Returns:
        List of documents with metadata and chunk counts
    """
    input_data = DocumentListInput(limit=limit, offset=offset)
    
    documents = await list_documents_tool(input_data)
    
    # Convert to dict for agent
    return [
        {
            "id": d.id,
            "title": d.title,
            "source": d.source,
            "chunk_count": d.chunk_count,
            "created_at": d.created_at.isoformat()
        }
        for d in documents
    ]


@rag_agent.tool
async def get_entity_relationships(
    ctx: RunContext[AgentDependencies],
    entity_name: str,
    depth: int = 2
) -> Dict[str, Any]:
    """
    Get all relationships for a specific entity in the knowledge graph.
    
    This tool explores the knowledge graph to find how a specific entity
    (company, person, technology) relates to other entities. Best for
    understanding how companies or technologies relate to each other.
    
    Args:
        entity_name: Name of the entity to explore (e.g., "Google", "OpenAI")
        depth: Maximum traversal depth for relationships (1-5)
    
    Returns:
        Entity relationships and connected entities with relationship types
    """
    input_data = EntityRelationshipInput(
        entity_name=entity_name,
        depth=depth
    )
    
    return await get_entity_relationships_tool(input_data)


@rag_agent.tool
async def get_entity_timeline(
    ctx: RunContext[AgentDependencies],
    entity_name: str,
    start_date: str = "",
    end_date: str = ""
) -> List[Dict[str, Any]]:
    """
    Get the timeline of facts for a specific entity.
    
    This tool retrieves chronological information about an entity,
    showing how information has evolved over time. Best for understanding
    how information about an entity has developed or changed.
    
    Args:
        entity_name: Name of the entity (e.g., "Microsoft", "AI")
        start_date: Start date in ISO format (YYYY-MM-DD), optional
        end_date: End date in ISO format (YYYY-MM-DD), optional
    
    Returns:
        Chronological list of facts about the entity with timestamps
    """
    input_data = EntityTimelineInput(
        entity_name=entity_name,
        start_date=start_date,
        end_date=end_date
    )
    
    return await get_entity_timeline_tool(input_data)


@rag_agent.tool
async def web_search(
    ctx: RunContext[AgentDependencies],
    query: str,
    max_results: int = 5
) -> List[Dict[str, Any]]:
    """
    Search the web for current information when local knowledge is insufficient.
    This tool performs web searches to find up-to-date information that may not be
    available in the local knowledge base. Use this when you need recent information
    or when local search results are insufficient.
    Args:
        query: Search query for web search
        max_results: Maximum number of results to return (1-10)
    Returns:
        List of web search results with titles, content, and URLs
    """
    logger.debug("Web search tool called with query: '%s', max_results: %d", query, max_results)
    logger.debug("Session ID: %s", ctx.deps.session_id)
    input_data = WebSearchInput(
        query=query,
        max_results=max_results
    )
    logger.debug("Calling web_search_tool with input: %s", input_data)
    start_time = datetime.now()
    try:
        results = await web_search_tool(input_data)
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds() * 1000
        logger.debug("Web search completed in %.2f ms, found %d results", duration, len(results))
        return results
    except Exception as e:
        logger.error("Web search failed: %s", e)
        logger.debug("Web search error details", exc_info=True)
        return []


@rag_agent.tool
async def compose_email(
    ctx: RunContext[AgentDependencies],
    to: str,
    subject: str,
    body: str
) -> Dict[str, Any]:
    """
    Compose and send an email using Gmail.
    This tool allows you to send an email to any recipient with a subject and body.
    Args:
        to: Recipient email address
        subject: Email subject
        body: Email body text
    Returns:
        Status and message ID or error
    """
    logger.debug("Compose email tool called with to: '%s', subject: '%s'", to, subject)
    input_data = EmailComposeInput(to=to, subject=subject, body=body)
    try:
        result = await compose_email_tool(input_data)
        return result
    except Exception as e:
        logger.error("Compose email failed: %s", e)
        return {"status": "error", "error": str(e)}