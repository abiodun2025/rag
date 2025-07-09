"""
Schema management system for provider-specific schemas and database mapping.
"""

from typing import Dict, Any, Optional, List, Union, Type
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


# Base class for all database schemas
class DatabaseSchema(BaseModel):
    """Base class for all database schemas."""
    pass


class ProviderType(str, Enum):
    """Supported provider types."""
    COHERE = "cohere"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


# Original database schemas (the contract) - these match the actual database structure
class Document(DatabaseSchema):
    """Original document schema from database."""
    id: Optional[str] = None
    title: str = Field(..., description="Document title")
    source: str = Field(..., description="Document source")
    content: str = Field(..., description="Document content")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Document metadata")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class Chunk(DatabaseSchema):
    """Original chunk schema from database."""
    id: Optional[str] = None
    document_id: str = Field(..., description="Document ID")
    content: str = Field(..., description="Chunk content")
    embedding: Optional[List[float]] = None
    chunk_index: int = Field(..., description="Chunk index")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Chunk metadata")
    token_count: Optional[int] = None
    created_at: Optional[datetime] = None


class Session(DatabaseSchema):
    """Original session schema from database."""
    id: Optional[str] = None
    user_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Session metadata")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None


class Message(DatabaseSchema):
    """Original message schema from database."""
    id: Optional[str] = None
    session_id: str = Field(..., description="Session ID")
    role: str = Field(..., description="Message role")
    content: str = Field(..., description="Message content")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Message metadata")
    created_at: Optional[datetime] = None


# Neo4j/Graphiti schemas (the contract) - these match the actual Neo4j structure
class Neo4jEntity(DatabaseSchema):
    """Neo4j entity schema (the contract)."""
    uuid: str = Field(..., description="Entity UUID")
    name: str = Field(..., description="Entity name")
    summary: str = Field("", description="Entity summary")
    entity_type: str = Field("", description="Entity type")
    group_id: str = Field("", description="Group ID")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Entity metadata")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class Neo4jRelationship(DatabaseSchema):
    """Neo4j relationship schema (the contract)."""
    uuid: str = Field(..., description="Relationship UUID")
    name: str = Field(..., description="Relationship name")
    fact: str = Field("", description="Factual information")
    source_node_uuid: str = Field("", description="Source entity UUID")
    target_node_uuid: str = Field("", description="Target entity UUID")
    group_id: str = Field("", description="Group ID")
    valid_at: Optional[datetime] = None
    invalid_at: Optional[datetime] = None
    expired_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Relationship metadata")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ProviderSchema(BaseModel):
    """Provider-specific schema that handles Cohere and other provider requirements."""
    
    # Required fields for all providers
    uuid: str = Field(..., description="Unique identifier")
    name: str = Field(..., description="Name or title")
    
    # Cohere-specific fields (all strings to avoid Union[str, None] issues)
    episodes: str = Field("", description="Episodes information")
    fact_embedding: List[float] = Field(default_factory=list, description="Fact embedding vector")
    start_date: str = Field("", description="Start date")
    end_date: str = Field("", description="End date")
    description: str = Field("", description="Description")
    type: str = Field("", description="Type information")
    
    # Additional flexible fields
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    model_config = ConfigDict(extra="allow")


class SchemaMapper:
    """Maps between database schemas and provider-specific schemas."""
    
    def __init__(self, provider: ProviderType):
        """Initialize schema mapper for specific provider."""
        self.provider = provider
    
    def database_to_provider(self, db_data: Dict[str, Any]) -> ProviderSchema:
        """Convert database data to provider-specific schema."""
        # Handle Neo4j relationship data (from Graphiti)
        if "fact" in db_data and "uuid" in db_data:
            # This is a Neo4j relationship
            return ProviderSchema(
                uuid=db_data.get("uuid", ""),
                name=db_data.get("name", ""),
                description=db_data.get("fact", ""),
                start_date=db_data.get("valid_at", ""),
                end_date=db_data.get("invalid_at", ""),
                episodes="",  # Cohere-compatible default
                fact_embedding=[],  # Cohere-compatible default
                type="relationship",
                metadata=db_data.get("metadata", {})
            )
        elif "summary" in db_data and "uuid" in db_data:
            # This is a Neo4j entity
            return ProviderSchema(
                uuid=db_data.get("uuid", ""),
                name=db_data.get("name", ""),
                description=db_data.get("summary", ""),
                start_date="",
                end_date="",
                episodes="",  # Cohere-compatible default
                fact_embedding=[],  # Cohere-compatible default
                type=db_data.get("entity_type", ""),
                metadata=db_data.get("metadata", {})
            )
        else:
            # Generic conversion for other data
            return ProviderSchema(
                uuid=db_data.get("uuid", ""),
                name=db_data.get("name", ""),
                description=db_data.get("description", ""),
                start_date=db_data.get("start_date", ""),
                end_date=db_data.get("end_date", ""),
                episodes="",  # Cohere-compatible default
                fact_embedding=[],  # Cohere-compatible default
                type=db_data.get("type", ""),
                metadata=db_data.get("metadata", {})
            )
    
    def provider_to_database(self, provider_schema: ProviderSchema, schema_type: str) -> Dict[str, Any]:
        """Convert provider-specific schema back to database format."""
        if schema_type == "relationship":
            return {
                "uuid": provider_schema.uuid,
                "name": provider_schema.name,
                "fact": provider_schema.description,
                "source_node_uuid": provider_schema.metadata.get("source_node_uuid", ""),
                "target_node_uuid": provider_schema.metadata.get("target_node_uuid", ""),
                "valid_at": provider_schema.start_date if provider_schema.start_date else None,
                "invalid_at": provider_schema.end_date if provider_schema.end_date else None,
                "metadata": provider_schema.metadata
            }
        elif schema_type == "entity":
            return {
                "uuid": provider_schema.uuid,
                "name": provider_schema.name,
                "summary": provider_schema.description,
                "entity_type": provider_schema.type,
                "metadata": provider_schema.metadata
            }
        else:
            # Generic conversion
            return {
                "uuid": provider_schema.uuid,
                "name": provider_schema.name,
                "description": provider_schema.description,
                "metadata": provider_schema.metadata
            }


class SchemaRegistry:
    """Registry for managing schemas across different providers."""
    
    def __init__(self):
        """Initialize schema registry."""
        self._mappers: Dict[ProviderType, SchemaMapper] = {}
        self._schemas: Dict[str, Type[DatabaseSchema]] = {}
    
    def register_mapper(self, provider: ProviderType, mapper: SchemaMapper):
        """Register a schema mapper for a provider."""
        self._mappers[provider] = mapper
    
    def register_schema(self, name: str, schema_class: Type[DatabaseSchema]):
        """Register a database schema class."""
        self._schemas[name] = schema_class
    
    def get_mapper(self, provider: ProviderType) -> SchemaMapper:
        """Get schema mapper for provider."""
        if provider not in self._mappers:
            self._mappers[provider] = SchemaMapper(provider)
        return self._mappers[provider]
    
    def get_schema(self, name: str) -> Type[DatabaseSchema]:
        """Get database schema class by name."""
        return self._schemas.get(name, DatabaseSchema)
    
    def convert_for_provider(self, db_data: Dict[str, Any], provider: ProviderType) -> ProviderSchema:
        """Convert database data to provider-specific schema."""
        mapper = self.get_mapper(provider)
        return mapper.database_to_provider(db_data)
    
    def convert_from_provider(self, provider_schema: ProviderSchema, provider: ProviderType, schema_type: str) -> Dict[str, Any]:
        """Convert provider-specific schema to database format."""
        mapper = self.get_mapper(provider)
        return mapper.provider_to_database(provider_schema, schema_type)


# Global schema registry
schema_registry = SchemaRegistry()

# Register default schemas (original database schemas)
schema_registry.register_schema("document", Document)
schema_registry.register_schema("chunk", Chunk)
schema_registry.register_schema("session", Session)
schema_registry.register_schema("message", Message)
schema_registry.register_schema("neo4j_entity", Neo4jEntity)
schema_registry.register_schema("neo4j_relationship", Neo4jRelationship)


def get_provider_schema(provider: ProviderType) -> Type[ProviderSchema]:
    """Get provider-specific schema class."""
    return ProviderSchema


def create_database_schema(schema_type: str, **kwargs) -> BaseModel:
    """Create a database schema instance."""
    schema_class = schema_registry.get_schema(schema_type)
    return schema_class(**kwargs)


def convert_to_provider_format(data: Dict[str, Any], provider: ProviderType) -> Dict[str, Any]:
    """Convert data to provider-specific format."""
    # Convert to provider schema
    provider_schema = schema_registry.convert_for_provider(data, provider)
    
    # Return as dict
    return provider_schema.model_dump()


def convert_from_provider_format(data: Dict[str, Any], provider: ProviderType, schema_type: str) -> Dict[str, Any]:
    """Convert data from provider-specific format to database format."""
    # Create a temporary provider schema
    temp_provider_schema = ProviderSchema(**data)
    
    # Convert to database format
    db_data = schema_registry.convert_from_provider(temp_provider_schema, provider, schema_type)
    
    # Return as dict
    return db_data 