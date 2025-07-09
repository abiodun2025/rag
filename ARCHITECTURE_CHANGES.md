# Architectural Changes: Provider-Independent Schema System

## Overview

This document outlines the major architectural changes implemented to fix Cohere API compatibility issues and future-proof the system for new LLM providers.

## Problem Statement

### Original Issues
1. **Cohere API 400 Error**: The system was generating schemas with `anyOf` containing `string` and `null` for optional fields, which Cohere v1 doesn't accept
2. **Database Schema Coupling**: Database schemas were tightly coupled to specific LLM provider requirements
3. **Future Scalability**: Adding new LLM providers required database schema changes
4. **Neo4j Warnings**: Database queries were referencing missing properties (`episodes`, `fact_embedding`)

### Root Cause
The Pydantic models used `Union[str, None]` for optional fields, which generated incompatible schemas for Cohere. The database schema was also directly tied to provider-specific requirements.

## Solution: Provider-Independent Schema Architecture

### 1. New Schema System (`agent/schemas.py`)

#### Core Components

**Original Database Schemas**: Keep the original database schemas as the contract
```python
class Document(BaseModel):
    id: Optional[str] = None
    title: str
    source: str
    content: str
    metadata: Dict[str, Any] = {}
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class Neo4jRelationship(BaseModel):
    uuid: str
    name: str
    fact: str
    source_node_uuid: str
    target_node_uuid: str
    valid_at: Optional[datetime] = None
    invalid_at: Optional[datetime] = None
    metadata: Dict[str, Any] = {}
```

**ProviderSchema**: Provider-specific schema for LLM compatibility
```python
class ProviderSchema(BaseModel):
    uuid: str
    name: str
    episodes: str = ""  # Cohere-compatible (no Union[str, None])
    fact_embedding: List[float] = []
    start_date: str = ""  # Cohere-compatible (no Union[str, None])
    end_date: str = ""  # Cohere-compatible (no Union[str, None])
    description: str = ""
    type: str = ""
    metadata: Dict[str, Any] = {}
```

**SchemaMapper**: Converts between database and provider formats
```python
class SchemaMapper:
    def database_to_provider(self, db_schema: DatabaseSchema) -> ProviderSchema
    def provider_to_database(self, provider_schema: ProviderSchema, schema_type: str) -> DatabaseSchema
```

**SchemaRegistry**: Manages schemas across different providers
```python
class SchemaRegistry:
    def convert_for_provider(self, db_schema: DatabaseSchema, provider: ProviderType) -> ProviderSchema
    def convert_from_provider(self, provider_schema: ProviderSchema, provider: ProviderType, schema_type: str) -> DatabaseSchema
```

### 2. Original Database Schema (`sql/schema.sql`)

#### Database Contract
- **Documents**: Original document storage with metadata
- **Chunks**: Original chunk storage with embeddings
- **Sessions**: Original session management
- **Messages**: Original message storage

#### Key Features
- **Unchanged Contract**: Original database schema remains the contract
- **Provider-Agnostic**: Database schema is independent of LLM providers
- **Vector Search**: Original PostgreSQL functions for vector search
- **Indexes**: Original optimized indexes for search

### 3. Updated Application Code

#### Tools Layer (`agent/tools.py`)
- Added schema conversion in `graph_search_tool`
- Converts database results to provider format for Cohere compatibility
- Converts back to database format for consistent API responses

#### Agent Layer (`agent/agent.py`)
- Added schema conversion in `graph_search` tool
- Ensures all data passed to LLM providers is compatible
- Maintains consistent data flow

#### Graph Utils (`agent/graph_utils.py`)
- Updated search functions to use schema conversion
- Ensures Neo4j results are compatible with all providers

#### Database Utils (`agent/db_utils.py`)
- Added schema system imports
- Ready for future provider-specific database operations

## Migration Guide

### For New Installations
1. Use `sql/schema.sql` for database setup (original schema)
2. The new schema system is automatically used for provider compatibility

### For Existing Installations
1. No database migration needed - original schema remains unchanged
2. The schema mapping layer handles provider compatibility automatically
3. Application code updates are already implemented

## Benefits

### 1. Cohere Compatibility
- ✅ Fixed "property start_date must have a type" error
- ✅ Eliminated `anyOf` schema issues
- ✅ All optional fields now use simple string types with defaults

### 2. Future-Proofing
- ✅ Easy to add new LLM providers
- ✅ No database schema changes required for new providers
- ✅ Clean separation between data storage and provider requirements

### 3. Database Consistency
- ✅ Eliminated Neo4j warnings about missing properties
- ✅ Consistent data structure across all providers
- ✅ Flexible metadata storage for provider-specific data

### 4. Maintainability
- ✅ Centralized schema management
- ✅ Clear conversion paths between formats
- ✅ Type-safe schema definitions

## Usage Examples

### Converting Database Data for Cohere
```python
from agent.schemas import ProviderType, convert_to_provider_format

# Database data
db_data = {
    "uuid": "123e4567-e89b-12d3-a456-426614174000",
    "name": "OpenAI",
    "fact": "AI research company",
    "valid_at": "2023-01-01T00:00:00Z"
}

# Convert for Cohere
cohere_data = convert_to_provider_format(db_data, ProviderType.COHERE)
# Result: All optional fields have string defaults, no Union types
```

### Adding New Provider Support
```python
# 1. Add new provider type
class ProviderType(str, Enum):
    COHERE = "cohere"
    OPENAI = "openai"
    NEW_PROVIDER = "new_provider"  # Add here

# 2. Create provider-specific mapper (if needed)
class NewProviderMapper(SchemaMapper):
    def database_to_provider(self, db_schema: DatabaseSchema) -> ProviderSchema:
        # Custom conversion logic for new provider
        pass

# 3. Register mapper
schema_registry.register_mapper(ProviderType.NEW_PROVIDER, NewProviderMapper())
```

## Testing

The schema system has been tested with:
- ✅ Schema conversion between database and provider formats
- ✅ Schema registry functionality
- ✅ Provider-specific schema creation
- ✅ Cohere compatibility verification

## Backward Compatibility

- ✅ Existing API endpoints remain unchanged
- ✅ Database queries continue to work
- ✅ Migration script preserves existing data
- ✅ Gradual migration path available

## Conclusion

The new provider-independent schema architecture successfully:
1. **Fixed the immediate Cohere compatibility issues**
2. **Created a scalable foundation for future LLM providers**
3. **Eliminated database schema coupling**
4. **Improved system maintainability**

This architectural change positions the system for long-term success with multiple LLM providers while maintaining clean separation of concerns between data storage and provider requirements. 