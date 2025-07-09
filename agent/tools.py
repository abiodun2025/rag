"""
Tools for the Pydantic AI agent.
"""

import os
import logging
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import asyncio

from pydantic import BaseModel, Field
from dotenv import load_dotenv

from .db_utils import (
    vector_search,
    hybrid_search,
    get_document,
    list_documents,
    get_document_chunks
)
from .graph_utils import (
    search_knowledge_graph,
    get_entity_relationships,
    graph_client
)
from .models import ChunkResult, GraphSearchResult, DocumentMetadata
from .providers import get_embedding_client, get_embedding_model
from .schemas import ProviderType, convert_to_provider_format, convert_from_provider_format
from duckduckgo_search import DDGS  # <-- Add this import
from agent.email_tools import compose_and_send_email

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Initialize embedding client with flexible provider
embedding_client = get_embedding_client()
EMBEDDING_MODEL = get_embedding_model()


async def generate_embedding(text: str) -> List[float]:
    """
    Generate embedding for text using OpenAI.
    
    Args:
        text: Text to embed
    
    Returns:
        Embedding vector
    """
    logger.debug("Generating embedding for text (length: %d): '%s'", len(text), text[:100] + "..." if len(text) > 100 else text)
    logger.debug("Using embedding model: %s", EMBEDDING_MODEL)
    
    start_time = datetime.now()
    try:
        response = await embedding_client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=text
        )
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds() * 1000
        
        embedding = response.data[0].embedding
        logger.debug("Embedding generated successfully in %.2f ms, vector length: %d", duration, len(embedding))
        return embedding
    except Exception as e:
        logger.error("Failed to generate embedding: %s", e)
        logger.debug("Embedding generation error details", exc_info=True)
        raise


# Tool Input Models
class VectorSearchInput(BaseModel):
    """Input for vector search tool."""
    query: str = Field(..., description="Search query")
    limit: int = Field(default=10, description="Maximum number of results")


class GraphSearchInput(BaseModel):
    """Input for graph search tool."""
    query: str = Field(..., description="Search query")


class HybridSearchInput(BaseModel):
    """Input for hybrid search tool."""
    query: str = Field(..., description="Search query")
    limit: int = Field(default=10, description="Maximum number of results")
    text_weight: float = Field(default=0.3, description="Weight for text similarity (0-1)")


class DocumentInput(BaseModel):
    """Input for document retrieval."""
    document_id: str = Field(..., description="Document ID to retrieve")


class DocumentListInput(BaseModel):
    """Input for listing documents."""
    limit: int = Field(default=20, description="Maximum number of documents")
    offset: int = Field(default=0, description="Number of documents to skip")


class EntityRelationshipInput(BaseModel):
    """Input for entity relationship query."""
    entity_name: str = Field(..., description="Name of the entity")
    depth: int = Field(default=2, description="Maximum traversal depth")


class EntityTimelineInput(BaseModel):
    """Input for entity timeline query."""
    entity_name: str = Field(..., description="Name of the entity")
    start_date: str = Field("", description="Start date (ISO format)")
    end_date: str = Field("", description="End date (ISO format)")


class WebSearchInput(BaseModel):
    """Input for web search tool."""
    query: str = Field(..., description="Search query for web search")
    max_results: int = Field(default=5, description="Maximum number of results to return")


class EmailComposeInput(BaseModel):
    to: str = Field(..., description="Recipient email address")
    subject: str = Field(..., description="Email subject")
    body: str = Field(..., description="Email body text")


# Tool Implementation Functions
async def vector_search_tool(input_data: VectorSearchInput) -> List[ChunkResult]:
    """
    Perform vector similarity search.
    
    Args:
        input_data: Search parameters
    
    Returns:
        List of matching chunks
    """
    logger.debug("Vector search tool called with input: %s", input_data)
    
    try:
        # Generate embedding for the query
        logger.debug("Generating embedding for vector search")
        embedding = await generate_embedding(input_data.query)
        
        # Perform vector search
        logger.debug("Performing vector search with embedding length: %d, limit: %d", len(embedding), input_data.limit)
        start_time = datetime.now()
        
        results = await vector_search(
            embedding=embedding,
            limit=input_data.limit
        )
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds() * 1000
        logger.debug("Vector search completed in %.2f ms, found %d raw results", duration, len(results))

        # Convert to ChunkResult models
        chunk_results = [
            ChunkResult(
                chunk_id=str(r["chunk_id"]),
                document_id=str(r["document_id"]),
                content=r["content"],
                score=r["similarity"],
                metadata=r["metadata"],
                document_title=r["document_title"],
                document_source=r["document_source"]
            )
            for r in results
        ]
        
        logger.debug("Converted %d results to ChunkResult models", len(chunk_results))
        return chunk_results
        
    except Exception as e:
        logger.error("Vector search failed: %s", e)
        logger.debug("Vector search error details", exc_info=True)
        return []


async def graph_search_tool(input_data: GraphSearchInput) -> List[GraphSearchResult]:
    """
    Search the knowledge graph.
    
    Args:
        input_data: Search parameters
    
    Returns:
        List of graph search results
    """
    logger.debug("Graph search tool called with input: %s", input_data)
    
    try:
        logger.debug("Performing knowledge graph search")
        start_time = datetime.now()
        
        results = await search_knowledge_graph(
            query=input_data.query
        )
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds() * 1000
        logger.debug("Knowledge graph search completed in %.2f ms, found %d raw results", duration, len(results))
        
        # Convert database results to provider format for Cohere compatibility
        provider = ProviderType.COHERE  # Default to Cohere for now
        converted_results = []
        
        for r in results:
            # Convert database format to provider format
            provider_data = convert_to_provider_format(r, provider)
            
            # Convert back to database format for GraphSearchResult
            db_data = convert_from_provider_format(provider_data, provider, "relationship")
            
            graph_results = GraphSearchResult(
                fact=db_data.get("fact", r.get("fact", "")),
                uuid=db_data.get("uuid", r.get("uuid", "")),
                valid_at=db_data.get("valid_at", r.get("valid_at")),
                invalid_at=db_data.get("invalid_at", r.get("invalid_at")),
                source_node_uuid=db_data.get("source_node_uuid", r.get("source_node_uuid"))
            )
            converted_results.append(graph_results)
        
        logger.debug("Converted %d results to GraphSearchResult models", len(converted_results))
        return converted_results
        
    except Exception as e:
        logger.error("Graph search failed: %s", e)
        logger.debug("Graph search error details", exc_info=True)
        return []


async def hybrid_search_tool(input_data: HybridSearchInput) -> List[ChunkResult]:
    """
    Perform hybrid search (vector + keyword).
    
    Args:
        input_data: Search parameters
    
    Returns:
        List of matching chunks
    """
    logger.debug("Hybrid search tool called with input: %s", input_data)
    
    try:
        # Generate embedding for the query
        logger.debug("Generating embedding for hybrid search")
        embedding = await generate_embedding(input_data.query)
        
        # Perform hybrid search
        logger.debug("Performing hybrid search with embedding length: %d, limit: %d, text_weight: %.2f", 
                    len(embedding), input_data.limit, input_data.text_weight)
        start_time = datetime.now()
        
        results = await hybrid_search(
            embedding=embedding,
            query_text=input_data.query,
            limit=input_data.limit,
            text_weight=input_data.text_weight
        )
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds() * 1000
        logger.debug("Hybrid search completed in %.2f ms, found %d raw results", duration, len(results))
        
        # Convert to ChunkResult models
        chunk_results = [
            ChunkResult(
                chunk_id=str(r["chunk_id"]),
                document_id=str(r["document_id"]),
                content=r["content"],
                score=r["combined_score"],
                metadata=r["metadata"],
                document_title=r["document_title"],
                document_source=r["document_source"]
            )
            for r in results
        ]
        
        logger.debug("Converted %d results to ChunkResult models", len(chunk_results))
        return chunk_results
        
    except Exception as e:
        logger.error("Hybrid search failed: %s", e)
        logger.debug("Hybrid search error details", exc_info=True)
        return []


async def web_search_tool(input_data: WebSearchInput) -> List[Dict[str, Any]]:
    """
    Perform web search using DuckDuckGo as a fallback when local knowledge is insufficient.
    Args:
        input_data: Web search parameters
    Returns:
        List of web search results
    """
    logger.debug("Web search tool called with input: %s", input_data)
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(
                input_data.query,
                max_results=input_data.max_results
            ))
        formatted_results = []
        for result in results:
            formatted_results.append({
                "title": result.get("title", ""),
                "content": result.get("body", ""),
                "url": result.get("href", result.get("url", "")),
                "source": "web_search",
                "search_query": input_data.query
            })
        logger.debug("Web search completed, found %d results", len(formatted_results))
        return formatted_results
    except Exception as e:
        logger.error("Web search failed: %s", e)
        logger.debug("Web search error details", exc_info=True)
        return []


async def compose_email_tool(input_data: EmailComposeInput) -> Dict[str, Any]:
    """
    Compose and send an email using Gmail.
    Args:
        input_data: Email parameters (to, subject, body)
    Returns:
        Status and message ID
    """
    try:
        result = compose_and_send_email(input_data.to, input_data.subject, input_data.body)
        return result
    except Exception as e:
        return {"status": "error", "error": str(e)}


async def get_document_tool(input_data: DocumentInput) -> Optional[Dict[str, Any]]:
    """
    Retrieve a complete document.
    
    Args:
        input_data: Document retrieval parameters
    
    Returns:
        Document data or None
    """
    try:
        document = await get_document(input_data.document_id)
        
        if document:
            # Also get all chunks for the document
            chunks = await get_document_chunks(input_data.document_id)
            document["chunks"] = chunks
        
        return document
        
    except Exception as e:
        logger.error(f"Document retrieval failed: {e}")
        return None


async def list_documents_tool(input_data: DocumentListInput) -> List[DocumentMetadata]:
    """
    List available documents.
    
    Args:
        input_data: Listing parameters
    
    Returns:
        List of document metadata
    """
    try:
        documents = await list_documents(
            limit=input_data.limit,
            offset=input_data.offset
        )
        
        # Convert to DocumentMetadata models
        return [
            DocumentMetadata(
                id=d["id"],
                title=d["title"],
                source=d["source"],
                metadata=d["metadata"],
                created_at=datetime.fromisoformat(d["created_at"]),
                updated_at=datetime.fromisoformat(d["updated_at"]),
                chunk_count=d.get("chunk_count")
            )
            for d in documents
        ]
        
    except Exception as e:
        logger.error(f"Document listing failed: {e}")
        return []


async def get_entity_relationships_tool(input_data: EntityRelationshipInput) -> Dict[str, Any]:
    """
    Get relationships for an entity.
    
    Args:
        input_data: Entity relationship parameters
    
    Returns:
        Entity relationships
    """
    try:
        return await get_entity_relationships(
            entity=input_data.entity_name,
            depth=input_data.depth
        )
        
    except Exception as e:
        logger.error(f"Entity relationship query failed: {e}")
        return {
            "central_entity": input_data.entity_name,
            "related_entities": [],
            "relationships": [],
            "depth": input_data.depth,
            "error": str(e)
        }


async def get_entity_timeline_tool(input_data: EntityTimelineInput) -> List[Dict[str, Any]]:
    """
    Get timeline of facts for an entity.
    
    Args:
        input_data: Timeline query parameters
    
    Returns:
        Timeline of facts
    """
    try:
        # Parse dates if provided
        start_date = None
        end_date = None
        
        if input_data.start_date:
            start_date = datetime.fromisoformat(input_data.start_date)
        if input_data.end_date:
            end_date = datetime.fromisoformat(input_data.end_date)
        
        # Get timeline from graph
        timeline = await graph_client.get_entity_timeline(
            entity_name=input_data.entity_name,
            start_date=start_date,
            end_date=end_date
        )
        
        return timeline
        
    except Exception as e:
        logger.error(f"Entity timeline query failed: {e}")
        return []


# Combined search function for agent use
async def perform_comprehensive_search(
    query: str,
    use_vector: bool = True,
    use_graph: bool = True,
    limit: int = 10
) -> Dict[str, Any]:
    """
    Perform a comprehensive search using multiple methods.
    
    Args:
        query: Search query
        use_vector: Whether to use vector search
        use_graph: Whether to use graph search
        limit: Maximum results per search type (only applies to vector search)
    
    Returns:
        Combined search results
    """
    results = {
        "query": query,
        "vector_results": [],
        "graph_results": [],
        "total_results": 0
    }
    
    tasks = []
    
    if use_vector:
        tasks.append(vector_search_tool(VectorSearchInput(query=query, limit=limit)))
    
    if use_graph:
        tasks.append(graph_search_tool(GraphSearchInput(query=query)))
    
    if tasks:
        search_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        if use_vector and not isinstance(search_results[0], Exception):
            results["vector_results"] = search_results[0]
        
        if use_graph:
            graph_idx = 1 if use_vector else 0
            if not isinstance(search_results[graph_idx], Exception):
                results["graph_results"] = search_results[graph_idx]
    
    results["total_results"] = len(results["vector_results"]) + len(results["graph_results"])
    
    return results