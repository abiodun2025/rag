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
    EmailComposeInput,   # <-- Import the email input model
    save_message_tool,   # <-- Import the message save tool
    save_conversation_tool, # <-- Import the conversation save tool
    list_messages_tool,  # <-- Import the message list tool
    SaveMessageInput,    # <-- Import the message save input model
    SaveConversationInput, # <-- Import the conversation save input model
    ListMessagesInput,    # <-- Import the message list input model
    list_emails_tool,
    read_email_tool,
    search_emails_tool,
    save_desktop_message_tool,  # <-- Import the desktop message save tool
    save_desktop_conversation_tool, # <-- Import the desktop conversation save tool
    list_desktop_messages_tool  # <-- Import the desktop message list tool
)
from .mcp_tools import (
    count_r_tool,
    list_desktop_contents_tool,
    get_desktop_path_tool,
    open_gmail_tool,
    open_gmail_compose_tool,
    sendmail_tool,
    sendmail_simple_tool,
    generic_mcp_tool,
    list_mcp_tools,
    CountRInput,
    DesktopContentsInput,
    DesktopPathInput,
    OpenGmailInput,
    OpenGmailComposeInput,
    SendmailInput,
    SendmailSimpleInput,
    MCPToolInput,
    mcp_client
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


@rag_agent.tool
async def save_message(
    ctx: RunContext[AgentDependencies],
    message: str,
    message_type: str = "user_message",
    metadata: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Save a message to the storage directory.
    
    This tool saves messages to a local directory with metadata including
    timestamps, user information, and message types. Messages are organized
    by date for easy retrieval.
    
    Args:
        message: The message content to save
        message_type: Type of message (user_message, agent_response, etc.)
        metadata: Additional metadata to store with the message
    
    Returns:
        Save status and file path information
    """
    logger.debug("Save message tool called with message type: '%s'", message_type)
    input_data = SaveMessageInput(
        message=message,
        message_type=message_type,
        metadata=metadata or {}
    )
    try:
        result = await save_message_tool(input_data)
        return result
    except Exception as e:
        logger.error("Save message failed: %s", e)
        return {"status": "error", "error": str(e)}


@rag_agent.tool
async def save_conversation(
    ctx: RunContext[AgentDependencies],
    user_message: str,
    agent_response: str,
    metadata: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Save a complete conversation (user message + agent response).
    
    This tool saves both the user's message and the agent's response together
    as a conversation pair. This is useful for maintaining conversation history
    and analyzing interaction patterns.
    
    Args:
        user_message: The user's message
        agent_response: The agent's response
        metadata: Additional metadata to store with the conversation
    
    Returns:
        Save status and file path information
    """
    logger.debug("Save conversation tool called")
    input_data = SaveConversationInput(
        user_message=user_message,
        agent_response=agent_response,
        metadata=metadata or {}
    )
    try:
        result = await save_conversation_tool(input_data)
        return result
    except Exception as e:
        logger.error("Save conversation failed: %s", e)
        return {"status": "error", "error": str(e)}


@rag_agent.tool
async def list_messages(
    ctx: RunContext[AgentDependencies],
    user_id: str = "",
    message_type: str = "",
    limit: int = 50
) -> Dict[str, Any]:
    """
    List saved messages with optional filtering.
    
    This tool retrieves previously saved messages with optional filtering
    by user ID or message type. Useful for reviewing conversation history
    or analyzing message patterns.
    
    Args:
        user_id: Filter by user ID (optional)
        message_type: Filter by message type (optional)
        limit: Maximum number of results to return (1-100)
    
    Returns:
        List of messages with metadata and file paths
    """
    logger.debug("List messages tool called with filters: user_id='%s', message_type='%s', limit=%d", 
                user_id, message_type, limit)
    input_data = ListMessagesInput(
        user_id=user_id or "",
        message_type=message_type or "",
        limit=limit
    )
    try:
        result = await list_messages_tool(input_data)
        return result
    except Exception as e:
        logger.error("List messages failed: %s", e)
        return {"status": "error", "error": str(e)}


@rag_agent.tool
async def list_emails(
    ctx: RunContext[AgentDependencies],
    max_results: int = 10,
    query: str = ""
) -> List[Dict[str, Any]]:
    """
    List recent emails from Gmail inbox.
    This tool retrieves the latest emails from your Gmail inbox.
    Args:
        max_results: Maximum number of emails to return (1-100)
        query: Optional Gmail search query (e.g., 'from:someone@example.com', 'subject:meeting')
    Returns:
        List of email summaries with IDs and metadata
    """
    logger.debug("List emails tool called with max_results: %d, query: '%s'", max_results, query)
    logger.debug("Session ID: %s", ctx.deps.session_id)
    input_data = list_emails_tool(max_results=max_results, query=query)
    try:
        results = await list_emails_tool(input_data)
        return results
    except Exception as e:
        logger.error("List emails failed: %s", e)
        return {"status": "error", "error": str(e)}


@rag_agent.tool
async def read_email(
    ctx: RunContext[AgentDependencies],
    email_id: str
) -> Dict[str, Any]:
    """
    Read a specific email by ID.
    This tool retrieves the full content of a specific email from your Gmail inbox.
    Args:
        email_id: Gmail message ID to read
    Returns:
        Full email content and metadata
    """
    logger.debug("Read email tool called with email_id: '%s'", email_id)
    logger.debug("Session ID: %s", ctx.deps.session_id)
    input_data = read_email_tool(email_id=email_id)
    try:
        email_data = await read_email_tool(input_data)
        return email_data
    except Exception as e:
        logger.error("Read email failed: %s", e)
        return {"status": "error", "error": str(e)}


@rag_agent.tool
async def search_emails(
    ctx: RunContext[AgentDependencies],
    query: str,
    max_results: int = 10
) -> List[Dict[str, Any]]:
    """
    Search emails with a specific query.
    This tool performs a search across your Gmail inbox for emails matching a query.
    Args:
        query: Search query for emails
        max_results: Maximum number of emails to return (1-100)
    Returns:
        List of email summaries matching the query
    """
    logger.debug("Search emails tool called with query: '%s', max_results: %d", query, max_results)
    logger.debug("Session ID: %s", ctx.deps.session_id)
    input_data = search_emails_tool(query=query, max_results=max_results)
    try:
        results = await search_emails_tool(input_data)
        return results
    except Exception as e:
        logger.error("Search emails failed: %s", e)
        return {"status": "error", "error": str(e)}


# Desktop Message Tools
@rag_agent.tool
async def save_desktop_message(
    ctx: RunContext[AgentDependencies],
    message: str,
    message_type: str = "user_message",
    metadata: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Save a message to the Desktop directory.
    
    This tool saves individual messages to the Desktop directory for easy access.
    Messages are organized by date and include metadata for better organization.
    
    Args:
        message: The message content to save
        message_type: Type of message (e.g., 'user_message', 'note', 'reminder')
        metadata: Additional metadata for the message
    
    Returns:
        Save status and file path
    """
    logger.debug("Save desktop message tool called with message: '%s', type: %s", message, message_type)
    logger.debug("Session ID: %s", ctx.deps.session_id)
    
    input_data = SaveMessageInput(
        message=message,
        message_type=message_type,
        metadata=metadata or {}
    )
    
    try:
        result = await save_desktop_message_tool(input_data)
        logger.debug("Save desktop message result: %s", result)
        return result
    except Exception as e:
        logger.error("Save desktop message failed: %s", e)
        return {"status": "error", "error": str(e)}


@rag_agent.tool
async def save_to_desktop(
    ctx: RunContext[AgentDependencies],
    message: str,
    message_type: str = "user_message",
    metadata: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Save a message to the Desktop directory (user-friendly alias).
    
    This is a user-friendly way to save messages to your Desktop.
    Just say "save to desktop" followed by your message.
    
    Args:
        message: The message content to save
        message_type: Type of message (e.g., 'user_message', 'note', 'reminder')
        metadata: Additional metadata for the message
    
    Returns:
        Save status and file path
    """
    logger.debug("Save to desktop tool called with message: '%s', type: %s", message, message_type)
    logger.debug("Session ID: %s", ctx.deps.session_id)
    
    input_data = SaveMessageInput(
        message=message,
        message_type=message_type,
        metadata=metadata or {}
    )
    
    try:
        result = await save_desktop_message_tool(input_data)
        logger.debug("Save to desktop result: %s", result)
        return result
    except Exception as e:
        logger.error("Save to desktop failed: %s", e)
        return {"status": "error", "error": str(e)}


@rag_agent.tool
async def save_to_project(
    ctx: RunContext[AgentDependencies],
    message: str,
    message_type: str = "user_message",
    metadata: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Save a message to the project directory (user-friendly alias).
    
    This is a user-friendly way to save messages to the project directory.
    Just say "save to project" followed by your message.
    
    Args:
        message: The message content to save
        message_type: Type of message (e.g., 'user_message', 'note', 'reminder')
        metadata: Additional metadata for the message
    
    Returns:
        Save status and file path
    """
    logger.debug("Save to project tool called with message: '%s', type: %s", message, message_type)
    logger.debug("Session ID: %s", ctx.deps.session_id)
    
    input_data = SaveMessageInput(
        message=message,
        message_type=message_type,
        metadata=metadata or {}
    )
    
    try:
        result = await save_message_tool(input_data)
        logger.debug("Save to project result: %s", result)
        return result
    except Exception as e:
        logger.error("Save to project failed: %s", e)
        return {"status": "error", "error": str(e)}


@rag_agent.tool
async def save_desktop_conversation(
    ctx: RunContext[AgentDependencies],
    user_message: str,
    agent_response: str,
    metadata: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Save a complete conversation to the Desktop directory.
    
    This tool saves both the user's message and the agent's response as a conversation.
    Useful for keeping track of important discussions and decisions.
    
    Args:
        user_message: The user's message
        agent_response: The agent's response
        metadata: Additional metadata for the conversation
    
    Returns:
        Save status and file path
    """
    logger.debug("Save desktop conversation tool called")
    logger.debug("Session ID: %s", ctx.deps.session_id)
    
    input_data = SaveConversationInput(
        user_message=user_message,
        agent_response=agent_response,
        metadata=metadata or {}
    )
    
    try:
        result = await save_desktop_conversation_tool(input_data)
        logger.debug("Save desktop conversation result: %s", result)
        return result
    except Exception as e:
        logger.error("Save desktop conversation failed: %s", e)
        return {"status": "error", "error": str(e)}


@rag_agent.tool
async def list_desktop_messages(
    ctx: RunContext[AgentDependencies],
    user_id: str = "",
    message_type: str = "",
    limit: int = 50
) -> Dict[str, Any]:
    """
    List saved messages from the Desktop directory.
    
    This tool lists messages saved to the Desktop directory with optional filtering.
    Useful for finding previously saved messages and conversations.
    
    Args:
        user_id: Filter by user ID (optional)
        message_type: Filter by message type (optional)
        limit: Maximum number of messages to return
    
    Returns:
        List of saved messages with metadata
    """
    logger.debug("List desktop messages tool called with limit: %d", limit)
    logger.debug("Session ID: %s", ctx.deps.session_id)
    
    input_data = ListMessagesInput(
        user_id=user_id,
        message_type=message_type,
        limit=limit
    )
    
    try:
        result = await list_desktop_messages_tool(input_data)
        logger.debug("List desktop messages result: %s", result)
        return result
    except Exception as e:
        logger.error("List desktop messages failed: %s", e)
        return {"status": "error", "error": str(e)}


@rag_agent.tool
async def show_desktop_messages(
    ctx: RunContext[AgentDependencies],
    limit: int = 10
) -> Dict[str, Any]:
    """
    Show saved messages from the Desktop directory (user-friendly alias).
    
    This is a user-friendly way to see messages saved to your Desktop.
    Just say "show desktop messages" to see your saved messages.
    
    Args:
        limit: Maximum number of messages to show
    
    Returns:
        List of saved messages with metadata
    """
    logger.debug("Show desktop messages tool called with limit: %d", limit)
    logger.debug("Session ID: %s", ctx.deps.session_id)
    
    input_data = ListMessagesInput(
        user_id="",
        message_type="",
        limit=limit
    )
    
    try:
        result = await list_desktop_messages_tool(input_data)
        logger.debug("Show desktop messages result: %s", result)
        return result
    except Exception as e:
        logger.error("Show desktop messages failed: %s", e)
        return {"status": "error", "error": str(e)}


@rag_agent.tool
async def show_project_messages(
    ctx: RunContext[AgentDependencies],
    limit: int = 10
) -> Dict[str, Any]:
    """
    Show saved messages from the project directory (user-friendly alias).
    
    This is a user-friendly way to see messages saved to the project directory.
    Just say "show project messages" to see your saved messages.
    
    Args:
        limit: Maximum number of messages to show
    
    Returns:
        List of saved messages with metadata
    """
    logger.debug("Show project messages tool called with limit: %d", limit)
    logger.debug("Session ID: %s", ctx.deps.session_id)
    
    input_data = ListMessagesInput(
        user_id="",
        message_type="",
        limit=limit
    )
    
    try:
        result = await list_messages_tool(input_data)
        logger.debug("Show project messages result: %s", result)
        return result
    except Exception as e:
        logger.error("Show project messages failed: %s", e)
        return {"status": "error", "error": str(e)}


# ============================================================================
# MCP (Model Context Protocol) Tools Integration
# ============================================================================

@rag_agent.tool
async def count_r_letters(
    ctx: RunContext[AgentDependencies],
    word: str
) -> Dict[str, Any]:
    """
    Count 'r' letters in a word using the MCP server.
    
    This tool connects to your count-r MCP server to count the number of 'r' letters
    in any given word. Useful for text analysis and character counting.
    
    Args:
        word: The word to count 'r' letters in
    
    Returns:
        Dictionary with the count result from the MCP server
    """
    logger.debug("Count R letters tool called with word: %s", word)
    logger.debug("Session ID: %s", ctx.deps.session_id)
    
    input_data = CountRInput(word=word)
    
    try:
        result = await count_r_tool(input_data)
        logger.debug("Count R letters result: %s", result)
        return result
    except Exception as e:
        logger.error("Count R letters failed: %s", e)
        return {"status": "error", "error": str(e)}


@rag_agent.tool
async def list_desktop_files(
    ctx: RunContext[AgentDependencies],
    random_string: str = "dummy"
) -> Dict[str, Any]:
    """
    List desktop files and folders using the MCP server.
    
    This tool connects to your count-r MCP server to list all files and folders
    on your Desktop. Useful for file management and organization.
    
    Args:
        random_string: Dummy parameter for no-parameter tools
    
    Returns:
        Dictionary with the desktop contents from the MCP server
    """
    logger.debug("List desktop files tool called")
    logger.debug("Session ID: %s", ctx.deps.session_id)
    
    input_data = DesktopContentsInput(random_string=random_string)
    
    try:
        result = await list_desktop_contents_tool(input_data)
        logger.debug("List desktop files result: %s", result)
        return result
    except Exception as e:
        logger.error("List desktop files failed: %s", e)
        return {"status": "error", "error": str(e)}


@rag_agent.tool
async def get_desktop_directory(
    ctx: RunContext[AgentDependencies],
    random_string: str = "dummy"
) -> Dict[str, Any]:
    """
    Get desktop path using the MCP server.
    
    This tool connects to your count-r MCP server to get the full path
    to your Desktop directory. Useful for file operations and path resolution.
    
    Args:
        random_string: Dummy parameter for no-parameter tools
    
    Returns:
        Dictionary with the desktop path from the MCP server
    """
    logger.debug("Get desktop directory tool called")
    logger.debug("Session ID: %s", ctx.deps.session_id)
    
    input_data = DesktopPathInput(random_string=random_string)
    
    try:
        result = await get_desktop_path_tool(input_data)
        logger.debug("Get desktop directory result: %s", result)
        return result
    except Exception as e:
        logger.error("Get desktop directory failed: %s", e)
        return {"status": "error", "error": str(e)}


@rag_agent.tool
async def open_gmail_browser(
    ctx: RunContext[AgentDependencies],
    random_string: str = "dummy"
) -> Dict[str, Any]:
    """
    Open Gmail in browser using the MCP server.
    
    This tool connects to your count-r MCP server to open Gmail
    in your default web browser. Useful for quick email access.
    
    Args:
        random_string: Dummy parameter for no-parameter tools
    
    Returns:
        Dictionary with the result from the MCP server
    """
    logger.debug("Open Gmail browser tool called")
    logger.debug("Session ID: %s", ctx.deps.session_id)
    
    input_data = OpenGmailInput(random_string=random_string)
    
    try:
        result = await open_gmail_tool(input_data)
        logger.debug("Open Gmail browser result: %s", result)
        return result
    except Exception as e:
        logger.error("Open Gmail browser failed: %s", e)
        return {"status": "error", "error": str(e)}


@rag_agent.tool
async def open_gmail_compose_window(
    ctx: RunContext[AgentDependencies],
    random_string: str = "dummy"
) -> Dict[str, Any]:
    """
    Open Gmail compose window using the MCP server.
    
    This tool connects to your count-r MCP server to open Gmail's
    compose window in your default web browser. Useful for writing emails.
    
    Args:
        random_string: Dummy parameter for no-parameter tools
    
    Returns:
        Dictionary with the result from the MCP server
    """
    logger.debug("Open Gmail compose window tool called")
    logger.debug("Session ID: %s", ctx.deps.session_id)
    
    input_data = OpenGmailComposeInput(random_string=random_string)
    
    try:
        result = await open_gmail_compose_tool(input_data)
        logger.debug("Open Gmail compose window result: %s", result)
        return result
    except Exception as e:
        logger.error("Open Gmail compose window failed: %s", e)
        return {"status": "error", "error": str(e)}


# Temporarily disabled due to schema issues
# @rag_agent.tool
# async def send_email_via_sendmail(
#     ctx: RunContext[AgentDependencies],
#     to_email: str,
#     subject: str,
#     body: str,
#     from_email: Optional[str] = None
# ) -> Dict[str, Any]:
#     """
#     Send email via sendmail using the MCP server.
#     
#     This tool connects to your count-r MCP server to send emails
#     using the system's sendmail command. Useful for automated email sending.
#     
#     Args:
#         to_email: Recipient email address
#         subject: Email subject
#         body: Email body content
#         from_email: Sender email address (optional)
#     
#     Returns:
#         Dictionary with the result from the MCP server
#     """
#     logger.debug("Send email via sendmail tool called to: %s", to_email)
#     logger.debug("Session ID: %s", ctx.deps.session_id)
#     
#     input_data = SendmailInput(
#         to_email=to_email,
#         subject=subject,
#         body=body,
#         from_email=from_email if from_email else ""
#     )
#     
#     try:
#         result = await sendmail_tool(input_data)
#         logger.debug("Send email via sendmail result: %s", result)
#         return result
#     except Exception as e:
#         logger.error("Send email via sendmail failed: %s", e)
#         return {"status": "error", "error": str(e)}


# Temporarily disabled due to schema issues
# @rag_agent.tool
# async def send_simple_email(
#     ctx: RunContext[AgentDependencies],
#     to_email: str,
#     subject: str,
#     message: str
# ) -> Dict[str, Any]:
#     """
#     Send simple email using the MCP server.
#     
#     This tool connects to your count-r MCP server to send simple emails
#     using the system's sendmail command. Simplified version of email sending.
#     
#     Args:
#         to_email: Recipient email address
#         subject: Email subject
#         message: Email message
#     
#     Returns:
#         Dictionary with the result from the MCP server
#     """
#     logger.debug("Send simple email tool called to: %s", to_email)
#     logger.debug("Session ID: %s", ctx.deps.session_id)
#     
#     input_data = SendmailSimpleInput(
#         to_email=to_email,
#         subject=subject,
#         message=message
#     )
#     
#     try:
#         result = await sendmail_simple_tool(input_data)
#         logger.debug("Send simple email result: %s", result)
#         return result
#     except Exception as e:
#         logger.error("Send simple email failed: %s", e)
#         return {"status": "error", "error": str(e)}


@rag_agent.tool
async def call_mcp_tool(
    ctx: RunContext[AgentDependencies],
    tool_name: str,
    parameters: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Call any tool from your MCP server.
    
    This is a generic tool that can call any function available on your
    count-r MCP server. Useful for accessing tools not explicitly defined.
    
    Args:
        tool_name: Name of the MCP tool to call
        parameters: Dictionary of parameters for the tool
    
    Returns:
        Dictionary with the result from the MCP server
    """
    logger.debug("Call MCP tool called: %s", tool_name)
    logger.debug("Session ID: %s", ctx.deps.session_id)
    
    if parameters is None:
        parameters = {}
    
    input_data = MCPToolInput(tool_name=tool_name, parameters=parameters)
    
    try:
        result = await generic_mcp_tool(input_data)
        logger.debug("Call MCP tool result: %s", result)
        return result
    except Exception as e:
        logger.error("Call MCP tool failed: %s", e)
        return {"status": "error", "error": str(e)}


@rag_agent.tool
async def list_available_mcp_tools(
    ctx: RunContext[AgentDependencies]
) -> Dict[str, Any]:
    """
    List all available tools from your MCP server.
    
    This tool connects to your count-r MCP server to discover and list
    all available tools. Useful for exploring what tools are available.
    
    Returns:
        Dictionary with the list of available tools from the MCP server
    """
    logger.debug("List available MCP tools called")
    logger.debug("Session ID: %s", ctx.deps.session_id)
    
    try:
        result = await list_mcp_tools()
        logger.debug("List available MCP tools result: %s", result)
        return result
    except Exception as e:
        logger.error("List available MCP tools failed: %s", e)
        return {"status": "error", "error": str(e)}