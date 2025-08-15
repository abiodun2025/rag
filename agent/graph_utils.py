"""
Graph utilities for Neo4j/Graphiti integration.
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional, Tuple, Union
from datetime import datetime, timezone
from contextlib import asynccontextmanager
import asyncio

from graphiti_core import Graphiti
from graphiti_core.utils.maintenance.graph_data_operations import clear_data
from graphiti_core.llm_client.config import LLMConfig
from graphiti_core.llm_client.openai_client import OpenAIClient
from graphiti_core.embedder.openai import OpenAIEmbedder, OpenAIEmbedderConfig
from graphiti_core.embedder.client import EmbedderClient
from graphiti_core.cross_encoder.openai_reranker_client import OpenAIRerankerClient
from dotenv import load_dotenv
from .schemas import ProviderType, convert_to_provider_format, convert_from_provider_format

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class CohereEmbedder(EmbedderClient):
    """Custom embedder for Cohere that's compatible with Graphiti."""
    
    def __init__(self, api_key: str, embedding_model: str, embedding_dim: int):
        """Initialize Cohere embedder."""
        super().__init__()
        self.api_key = api_key
        self.embedding_model = embedding_model
        self.embedding_dim = embedding_dim
        self._client = None
        self._detected_dimension = None
    
    @property
    def client(self):
        """Get Cohere client."""
        if self._client is None:
            try:
                import cohere
                self._client = cohere.AsyncClient(self.api_key)
            except ImportError:
                raise ImportError("Cohere library not installed. Run: pip install cohere")
        return self._client
    
    async def create(self, input_data: Union[str, List[str]]) -> List[float]:
        """Create embedding for single input (required by EmbedderClient)."""
        if isinstance(input_data, str):
            response = await self.client.embed(
                texts=[input_data],
                model=self.embedding_model,
                input_type="search_document"
            )
            embedding = response.embeddings[0]
            
            # Detect embedding dimension dynamically
            if self._detected_dimension is None:
                self._detected_dimension = len(embedding)
                logger.info(f"Detected Cohere embedding dimension: {self._detected_dimension} for model {self.embedding_model}")
            
            return embedding
        else:
            # Handle list input
            response = await self.client.embed(
                texts=input_data,
                model=self.embedding_model,
                input_type="search_document"
            )
            embedding = response.embeddings[0]  # Return first embedding for single input
            
            # Detect embedding dimension dynamically
            if self._detected_dimension is None:
                self._detected_dimension = len(embedding)
                logger.info(f"Detected Cohere embedding dimension: {self._detected_dimension} for model {self.embedding_model}")
            
            return embedding
    
    async def create_batch(self, input_data_list: List[str]) -> List[List[float]]:
        """Create embeddings for batch input (required by EmbedderClient)."""
        response = await self.client.embed(
            texts=input_data_list,
            model=self.embedding_model,
            input_type="search_document"
        )
        embeddings = response.embeddings
        
        # Detect embedding dimension dynamically from first embedding
        if self._detected_dimension is None and embeddings:
            self._detected_dimension = len(embeddings[0])
            logger.info(f"Detected Cohere embedding dimension: {self._detected_dimension} for model {self.embedding_model}")
        
        return embeddings


def get_embedding_provider() -> str:
    """Get the embedding provider name."""
    return os.getenv('EMBEDDING_PROVIDER', 'openai')


# Help from this PR for setting up the custom clients: https://github.com/getzep/graphiti/pull/601/files
class GraphitiClient:
    """Manages Graphiti knowledge graph operations."""
    
    def __init__(
        self,
        neo4j_uri: Optional[str] = None,
        neo4j_user: Optional[str] = None,
        neo4j_password: Optional[str] = None
    ):
        """
        Initialize Graphiti client.
        
        Args:
            neo4j_uri: Neo4j connection URI
            neo4j_user: Neo4j username
            neo4j_password: Neo4j password
        """
        # Neo4j configuration
        self.neo4j_uri = neo4j_uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.neo4j_user = neo4j_user or os.getenv("NEO4J_USER", "neo4j")
        self.neo4j_password = neo4j_password or os.getenv("NEO4J_PASSWORD")
        
        if not self.neo4j_password:
            raise ValueError("NEO4J_PASSWORD environment variable not set")
        
        # LLM configuration
        self.llm_base_url = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
        self.llm_api_key = os.getenv("LLM_API_KEY")
        self.llm_choice = os.getenv("LLM_CHOICE", "gpt-4.1-mini")
        
        if not self.llm_api_key:
            raise ValueError("LLM_API_KEY environment variable not set")
        
        # Embedding configuration
        self.embedding_base_url = os.getenv("EMBEDDING_BASE_URL", "https://api.openai.com/v1")
        self.embedding_api_key = os.getenv("EMBEDDING_API_KEY")
        self.embedding_model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
        self.embedding_provider = get_embedding_provider()
        
        if not self.embedding_api_key:
            raise ValueError("EMBEDDING_API_KEY environment variable not set")
        
        self.graphiti: Optional[Graphiti] = None
        self._initialized = False
    
    async def initialize(self):
        """Initialize Graphiti client."""
        if self._initialized:
            return
        
        try:
            # Create LLMConfig
            llm_config = LLMConfig(
                api_key=self.llm_api_key,
                model=self.llm_choice,
                small_model=self.llm_choice,  # Can be the same as main model
                base_url=self.llm_base_url
            )
            
            # Create OpenAI LLM client
            llm_client = OpenAIClient(config=llm_config)
            
            # Create embedder based on provider
            if self.embedding_provider.lower() == 'cohere':
                # Use custom Cohere embedder - dimension will be detected dynamically
                embedder = CohereEmbedder(
                    api_key=self.embedding_api_key,
                    embedding_model=self.embedding_model,
                    embedding_dim=1024  # Will be overridden by actual model response
                )
            else:
                # Use OpenAI embedder for all other providers - dimension will be detected dynamically
                embedder = OpenAIEmbedder(
                    config=OpenAIEmbedderConfig(
                        api_key=self.embedding_api_key,
                        embedding_model=self.embedding_model,
                        embedding_dim=1536,  # Will be overridden by actual model response
                        base_url=self.embedding_base_url
                    )
                )
            
            # Initialize Graphiti with custom clients
            self.graphiti = Graphiti(
                self.neo4j_uri,
                self.neo4j_user,
                self.neo4j_password,
                llm_client=llm_client,
                embedder=embedder,
                cross_encoder=OpenAIRerankerClient(client=llm_client, config=llm_config)
            )
            
            # Build indices and constraints
            await self.graphiti.build_indices_and_constraints()
            
            self._initialized = True
            logger.info(f"Graphiti client initialized successfully with LLM: {self.llm_choice} and embedder: {self.embedding_model} (provider: {self.embedding_provider})")
            
        except Exception as e:
            logger.error(f"Failed to initialize Graphiti: {e}")
            raise
    
    async def close(self):
        """Close Graphiti connection."""
        if self.graphiti:
            await self.graphiti.close()
            self.graphiti = None
            self._initialized = False
            logger.info("Graphiti client closed")
    
    async def add_episode(
        self,
        episode_id: str,
        content: str,
        source: str,
        timestamp: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Add an episode to the knowledge graph.
        
        Args:
            episode_id: Unique episode identifier
            content: Episode content
            source: Source of the content
            timestamp: Episode timestamp
            metadata: Additional metadata
        """
        if not self._initialized:
            await self.initialize()
        
        episode_timestamp = timestamp or datetime.now(timezone.utc)
        
        # Import EpisodeType for proper source handling
        from graphiti_core.nodes import EpisodeType
        
        await self.graphiti.add_episode(
            name=episode_id,
            episode_body=content,
            source=EpisodeType.text,  # Always use text type for our content
            source_description=source,
            reference_time=episode_timestamp
        )
        
        logger.info(f"Added episode {episode_id} to knowledge graph")
    
    async def search(
        self,
        query: str,
        center_node_distance: int = 2,
        use_hybrid_search: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Search the knowledge graph using custom Cypher queries.
        
        Args:
            query: Search query
            center_node_distance: Distance from center nodes
            use_hybrid_search: Whether to use hybrid search
        
        Returns:
            Search results
        """
        if not self._initialized:
            await self.initialize()
        
        try:
            # Use direct Neo4j queries instead of Graphiti's problematic search
            results = await self._custom_search(query)
            converted_results = []
            provider = ProviderType.COHERE
            
            for result in results:
                # Convert to provider format to ensure compatibility
                provider_data = convert_to_provider_format(result, provider)
                db_data = convert_from_provider_format(provider_data, provider, "relationship")
                converted_results.append(db_data)
            
            return converted_results
        except Exception as e:
            logger.error(f"Graph search failed: {e}")
            return []
    
    async def _custom_search(self, query: str) -> List[Dict[str, Any]]:
        """
        Custom search implementation using direct Neo4j queries.
        
        Args:
            query: Search query
        
        Returns:
            Search results
        """
        if not self.graphiti or not self.graphiti.driver:
            return []
        
        results = []
        
        # Use text search only (semantic search requires fact_embedding which doesn't exist)
        try:
            text_results = await self._text_search(query)
            results.extend(text_results)
        except Exception as e:
            logger.warning(f"Text search failed: {e}")
        
        # Remove duplicates and limit results
        seen_uuids = set()
        unique_results = []
        for result in results:
            if result.get("uuid") not in seen_uuids:
                seen_uuids.add(result.get("uuid"))
                unique_results.append(result)
        
        return unique_results[:10]  # Limit to 10 results
    
    async def _text_search(self, query: str) -> List[Dict[str, Any]]:
        """Perform text-based search."""
        if not self.graphiti or not self.graphiti.driver:
            return []
        
        # Simple text search that works with our data structure
        cypher_query = """
        MATCH (a:Entity)-[r:RELATES_TO]->(b:Entity)
        WHERE toLower(a.name) CONTAINS toLower($query) 
           OR toLower(b.name) CONTAINS toLower($query)
           OR toLower(r.fact) CONTAINS toLower($query)
        RETURN
            r.uuid AS uuid,
            r.group_id AS group_id,
            a.uuid AS source_node_uuid,
            b.uuid AS target_node_uuid,
            r.created_at AS created_at,
            r.name AS name,
            r.fact AS fact,
            r.expired_at AS expired_at,
            r.valid_at AS valid_at,
            r.invalid_at AS invalid_at,
            properties(r) AS attributes,
            1.0 AS score
        ORDER BY score DESC LIMIT $limit
        """
        
        try:
            async with self.graphiti.driver.session(database="neo4j") as session:
                result = await session.run(
                    cypher_query,
                    parameters={
                        "query": query,
                        "limit": 5
                    }
                )
                
                results = []
                async for record in result:
                    results.append({
                        "uuid": str(record["uuid"]),
                        "fact": record["fact"] or "",
                        "valid_at": str(record["valid_at"]) if record["valid_at"] else None,
                        "invalid_at": str(record["invalid_at"]) if record["invalid_at"] else None,
                        "source_node_uuid": str(record["source_node_uuid"]) if record["source_node_uuid"] else None,
                        "score": record["score"]
                    })
                
                return results
        except Exception as e:
            logger.warning(f"Text search query failed: {e}")
            return []
    
    async def get_related_entities(
        self,
        entity_name: str,
        relationship_types: Optional[List[str]] = None,
        depth: int = 1
    ) -> Dict[str, Any]:
        """
        Get entities related to a given entity using custom Neo4j queries.
        
        Args:
            entity_name: Name of the entity
            relationship_types: Types of relationships to follow (not used)
            depth: Maximum depth to traverse (not used)
        
        Returns:
            Related entities and relationships
        """
        if not self._initialized:
            await self.initialize()
        
        if not self.graphiti or not self.graphiti.driver:
            return {
                "central_entity": entity_name,
                "related_facts": [],
                "search_method": "custom_neo4j_search"
            }
        
        # Use custom Cypher query to find relationships involving the entity
        cypher_query = """
        MATCH (n:Entity)-[r:RELATES_TO]->(m:Entity)
        WHERE (n.name CONTAINS $entity_name OR m.name CONTAINS $entity_name OR r.fact CONTAINS $entity_name)
        AND r.group_id IS NOT NULL
        RETURN
            r.uuid AS uuid,
            r.group_id AS group_id,
            n.uuid AS source_node_uuid,
            m.uuid AS target_node_uuid,
            n.name AS source_name,
            m.name AS target_name,
            r.created_at AS created_at,
            r.name AS name,
            r.fact AS fact,
            r.expired_at AS expired_at,
            r.valid_at AS valid_at,
            r.invalid_at AS invalid_at,
            properties(r) AS attributes
        ORDER BY r.created_at DESC
        LIMIT 10
        """
        
        try:
            async with self.graphiti.driver.session(database="neo4j") as session:
                result = await session.run(
                    cypher_query,
                    parameters={
                        "entity_name": entity_name
                    }
                )
                facts = []
                related_entities = set()
                async for record in result:
                    fact_data = {
                        "fact": record["fact"] or "",
                        "uuid": str(record["uuid"]),
                        "valid_at": str(record["valid_at"]) if record["valid_at"] else None,
                        "source_entity": record["source_name"],
                        "target_entity": record["target_name"]
                    }
                    facts.append(fact_data)
                    if record["source_name"]:
                        related_entities.add(record["source_name"])
                    if record["target_name"]:
                        related_entities.add(record["target_name"])
                return {
                    "central_entity": entity_name,
                    "related_facts": facts,
                    "related_entities": list(related_entities),
                    "search_method": "custom_neo4j_search"
                }
        except Exception as e:
            logger.warning(f"Custom entity search failed: {e}")
            return {
                "central_entity": entity_name,
                "related_facts": [],
                "search_method": "custom_neo4j_search"
            }
    
    async def get_entity_timeline(
        self,
        entity_name: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Get timeline of facts for an entity using custom search.
        
        Args:
            entity_name: Name of the entity
            start_date: Start of time range (not currently used)
            end_date: End of time range (not currently used)
        
        Returns:
            Timeline of facts
        """
        if not self._initialized:
            await self.initialize()
        
        # Use custom search instead of Graphiti's problematic search
        results = await self._custom_search(f"timeline history of {entity_name}")
        
        timeline = []
        for result in results:
            timeline.append({
                "fact": result.get("fact", ""),
                "uuid": result.get("uuid", ""),
                "valid_at": result.get("valid_at"),
                "invalid_at": result.get("invalid_at")
            })
        
        # Sort by valid_at if available
        timeline.sort(key=lambda x: x.get('valid_at') or '', reverse=True)
        
        return timeline
    
    async def get_graph_statistics(self) -> Dict[str, Any]:
        """
        Get basic statistics about the knowledge graph.
        
        Returns:
            Graph statistics
        """
        if not self._initialized:
            await self.initialize()
        
        # Use custom search instead of Graphiti's problematic search
        try:
            test_results = await self._custom_search("test")
            return {
                "graphiti_initialized": True,
                "sample_search_results": len(test_results),
                "note": "Detailed statistics require direct Neo4j access"
            }
        except Exception as e:
            return {
                "graphiti_initialized": False,
                "error": str(e)
            }
    
    async def clear_graph(self):
        """Clear all data from the graph (USE WITH CAUTION)."""
        if not self._initialized:
            await self.initialize()
        
        try:
            # Use Graphiti's proper clear_data function with the driver
            await clear_data(self.graphiti.driver)
            logger.warning("Cleared all data from knowledge graph")
        except Exception as e:
            logger.error(f"Failed to clear graph using clear_data: {e}")
            # Fallback: Close and reinitialize (this will create fresh indices)
            if self.graphiti:
                await self.graphiti.close()
            
            # Create clients for reinitialization based on provider
            llm_config = LLMConfig(
                api_key=self.llm_api_key,
                model=self.llm_choice,
                small_model=self.llm_choice,
                base_url=self.llm_base_url
            )
            
            llm_client = OpenAIClient(config=llm_config)
            
            # Create embedder based on provider
            if self.embedding_provider.lower() == 'cohere':
                embedder = CohereEmbedder(
                    api_key=self.embedding_api_key,
                    embedding_model=self.embedding_model,
                    embedding_dim=1024  # Cohere embed-english-v3.0 default
                )
            else:
                embedder = OpenAIEmbedder(
                    config=OpenAIEmbedderConfig(
                        api_key=self.embedding_api_key,
                        embedding_model=self.embedding_model,
                        embedding_dim=1536,  # OpenAI text-embedding-3-small default
                        base_url=self.embedding_base_url
                    )
                )
            
            self.graphiti = Graphiti(
                self.neo4j_uri,
                self.neo4j_user,
                self.neo4j_password,
                llm_client=llm_client,
                embedder=embedder,
                cross_encoder=OpenAIRerankerClient(client=llm_client, config=llm_config)
            )
            await self.graphiti.build_indices_and_constraints()
            
            logger.warning("Reinitialized Graphiti client (fresh indices created)")


# Global Graphiti client instance - only create if environment is properly configured
try:
    # Check if required environment variables are set
    if os.getenv("EMBEDDING_API_KEY") and os.getenv("LLM_API_KEY"):
        graph_client = GraphitiClient()
    else:
        graph_client = None
        logger.warning("Graphiti client not initialized - missing environment variables")
except Exception as e:
    graph_client = None
    logger.warning(f"Graphiti client not initialized - error: {e}")


async def initialize_graph():
    """Initialize graph client."""
    if graph_client is None:
        logger.warning("Graphiti client not initialized - cannot initialize")
        return
    await graph_client.initialize()


async def close_graph():
    """Close graph client."""
    if graph_client is None:
        logger.warning("Graphiti client not initialized - cannot close")
        return
    await graph_client.close()


# Convenience functions for common operations
async def add_to_knowledge_graph(
    content: str,
    source: str,
    episode_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    """
    Add content to the knowledge graph.
    
    Args:
        content: Content to add
        source: Source of the content
        episode_id: Optional episode ID
        metadata: Optional metadata
    
    Returns:
        Episode ID
    """
    if graph_client is None:
        raise RuntimeError("Graphiti client not initialized - check environment variables")
    
    if not episode_id:
        episode_id = f"episode_{datetime.now(timezone.utc).isoformat()}"
    
    await graph_client.add_episode(
        episode_id=episode_id,
        content=content,
        source=source,
        metadata=metadata
    )
    
    return episode_id


async def search_knowledge_graph(
    query: str
) -> List[Dict[str, Any]]:
    """
    Search the knowledge graph.
    
    Args:
        query: Search query
    
    Returns:
        Search results
    """
    if graph_client is None:
        raise RuntimeError("Graphiti client not initialized - check environment variables")
    
    # Ensure the global client is initialized
    if not graph_client._initialized:
        await graph_client.initialize()
    
    return await graph_client._custom_search(query)


async def get_entity_relationships(
    entity: str,
    depth: int = 2
) -> Dict[str, Any]:
    """
    Get relationships for an entity.
    
    Args:
        entity: Entity name
        depth: Maximum traversal depth
    
    Returns:
        Entity relationships
    """
    if graph_client is None:
        raise RuntimeError("Graphiti client not initialized - check environment variables")
    
    return await graph_client.get_related_entities(entity, depth=depth)


async def test_graph_connection() -> bool:
    """
    Test graph database connection.
    
    Returns:
        True if connection successful
    """
    if graph_client is None:
        logger.warning("Graphiti client not initialized - cannot test connection")
        return False
    
    try:
        await graph_client.initialize()
        stats = await graph_client.get_graph_statistics()
        logger.info(f"Graph connection successful. Stats: {stats}")
        return True
    except Exception as e:
        logger.error(f"Graph connection test failed: {e}")
        return False