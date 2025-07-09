-- Database Schema v2: Provider-independent schema
-- This schema is designed to be independent of specific LLM provider requirements
-- and uses a flexible metadata system for storing provider-specific data

CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Drop existing tables if they exist
DROP TABLE IF EXISTS messages CASCADE;
DROP TABLE IF EXISTS sessions CASCADE;
DROP TABLE IF EXISTS chunks CASCADE;
DROP TABLE IF EXISTS documents CASCADE;
DROP TABLE IF EXISTS entities CASCADE;
DROP TABLE IF EXISTS relationships CASCADE;
DROP TABLE IF EXISTS communities CASCADE;
DROP TABLE IF EXISTS episodic_data CASCADE;

-- Drop existing indexes
DROP INDEX IF EXISTS idx_chunks_embedding;
DROP INDEX IF EXISTS idx_chunks_document_id;
DROP INDEX IF EXISTS idx_documents_metadata;
DROP INDEX IF EXISTS idx_chunks_content_trgm;
DROP INDEX IF EXISTS idx_entities_uuid;
DROP INDEX IF EXISTS idx_relationships_uuid;
DROP INDEX IF EXISTS idx_communities_uuid;
DROP INDEX IF EXISTS idx_episodic_uuid;

-- Core document storage (unchanged from v1)
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    source TEXT NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_documents_metadata ON documents USING GIN (metadata);
CREATE INDEX idx_documents_created_at ON documents (created_at DESC);

-- Document chunks (unchanged from v1)
CREATE TABLE chunks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    embedding vector(1024),
    chunk_index INTEGER NOT NULL,
    metadata JSONB DEFAULT '{}',
    token_count INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_chunks_embedding ON chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 1);
CREATE INDEX idx_chunks_document_id ON chunks (document_id);
CREATE INDEX idx_chunks_chunk_index ON chunks (document_id, chunk_index);
CREATE INDEX idx_chunks_content_trgm ON chunks USING GIN (content gin_trgm_ops);

-- Session management (unchanged from v1)
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_sessions_user_id ON sessions (user_id);
CREATE INDEX idx_sessions_expires_at ON sessions (expires_at);

-- Messages (unchanged from v1)
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_messages_session_id ON messages (session_id, created_at);

-- New: Provider-independent entity table
CREATE TABLE entities (
    uuid UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    summary TEXT DEFAULT '',
    entity_type TEXT DEFAULT '',
    group_id TEXT DEFAULT '',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_entities_uuid ON entities (uuid);
CREATE INDEX idx_entities_name ON entities (name);
CREATE INDEX idx_entities_group_id ON entities (group_id);
CREATE INDEX idx_entities_metadata ON entities USING GIN (metadata);

-- New: Provider-independent relationship table
CREATE TABLE relationships (
    uuid UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    fact TEXT DEFAULT '',
    source_node_uuid UUID NOT NULL REFERENCES entities(uuid) ON DELETE CASCADE,
    target_node_uuid UUID NOT NULL REFERENCES entities(uuid) ON DELETE CASCADE,
    group_id TEXT DEFAULT '',
    valid_at TIMESTAMP WITH TIME ZONE,
    invalid_at TIMESTAMP WITH TIME ZONE,
    expired_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_relationships_uuid ON relationships (uuid);
CREATE INDEX idx_relationships_name ON relationships (name);
CREATE INDEX idx_relationships_group_id ON relationships (group_id);
CREATE INDEX idx_relationships_source ON relationships (source_node_uuid);
CREATE INDEX idx_relationships_target ON relationships (target_node_uuid);
CREATE INDEX idx_relationships_valid_at ON relationships (valid_at);
CREATE INDEX idx_relationships_invalid_at ON relationships (invalid_at);
CREATE INDEX idx_relationships_metadata ON relationships USING GIN (metadata);

-- New: Provider-independent community table
CREATE TABLE communities (
    uuid UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    description TEXT DEFAULT '',
    group_id TEXT DEFAULT '',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_communities_uuid ON communities (uuid);
CREATE INDEX idx_communities_name ON communities (name);
CREATE INDEX idx_communities_group_id ON communities (group_id);
CREATE INDEX idx_communities_metadata ON communities USING GIN (metadata);

-- New: Provider-independent episodic data table
CREATE TABLE episodic_data (
    uuid UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    episode_id TEXT DEFAULT '',
    content TEXT DEFAULT '',
    source TEXT DEFAULT '',
    timestamp TIMESTAMP WITH TIME ZONE,
    group_id TEXT DEFAULT '',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_episodic_uuid ON episodic_data (uuid);
CREATE INDEX idx_episodic_episode_id ON episodic_data (episode_id);
CREATE INDEX idx_episodic_group_id ON episodic_data (group_id);
CREATE INDEX idx_episodic_timestamp ON episodic_data (timestamp);
CREATE INDEX idx_episodic_metadata ON episodic_data USING GIN (metadata);

-- Full-text search indexes for the new tables
CREATE INDEX idx_entities_name_summary ON entities USING GIN (to_tsvector('english', name || ' ' || summary));
CREATE INDEX idx_relationships_name_fact ON relationships USING GIN (to_tsvector('english', name || ' ' || fact));
CREATE INDEX idx_communities_name_description ON communities USING GIN (to_tsvector('english', name || ' ' || description));
CREATE INDEX idx_episodic_content ON episodic_data USING GIN (to_tsvector('english', content));

-- Vector search functions (unchanged from v1)
CREATE OR REPLACE FUNCTION match_chunks(
    query_embedding vector(1024),
    match_count INT DEFAULT 10
)
RETURNS TABLE (
    chunk_id UUID,
    document_id UUID,
    content TEXT,
    similarity FLOAT,
    metadata JSONB,
    document_title TEXT,
    document_source TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c.id AS chunk_id,
        c.document_id,
        c.content,
        1 - (c.embedding <=> query_embedding) AS similarity,
        c.metadata,
        d.title AS document_title,
        d.source AS document_source
    FROM chunks c
    JOIN documents d ON c.document_id = d.id
    WHERE c.embedding IS NOT NULL
    ORDER BY c.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

CREATE OR REPLACE FUNCTION hybrid_search(
    query_embedding vector(1024),
    query_text TEXT,
    match_count INT DEFAULT 10,
    text_weight FLOAT DEFAULT 0.3
)
RETURNS TABLE (
    chunk_id UUID,
    document_id UUID,
    content TEXT,
    combined_score FLOAT,
    vector_similarity FLOAT,
    text_similarity FLOAT,
    metadata JSONB,
    document_title TEXT,
    document_source TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    WITH vector_results AS (
        SELECT 
            c.id AS chunk_id,
            c.document_id,
            c.content,
            1 - (c.embedding <=> query_embedding) AS vector_sim,
            c.metadata,
            d.title AS doc_title,
            d.source AS doc_source
        FROM chunks c
        JOIN documents d ON c.document_id = d.id
        WHERE c.embedding IS NOT NULL
    ),
    text_results AS (
        SELECT 
            c.id AS chunk_id,
            c.document_id,
            c.content,
            ts_rank_cd(to_tsvector('english', c.content), plainto_tsquery('english', query_text)) AS text_sim,
            c.metadata,
            d.title AS doc_title,
            d.source AS doc_source
        FROM chunks c
        JOIN documents d ON c.document_id = d.id
        WHERE to_tsvector('english', c.content) @@ plainto_tsquery('english', query_text)
    )
    SELECT 
        COALESCE(v.chunk_id, t.chunk_id) AS chunk_id,
        COALESCE(v.document_id, t.document_id) AS document_id,
        COALESCE(v.content, t.content) AS content,
        (COALESCE(v.vector_sim, 0) * (1 - text_weight) + COALESCE(t.text_sim, 0) * text_weight) AS combined_score,
        COALESCE(v.vector_sim, 0) AS vector_similarity,
        COALESCE(t.text_sim, 0) AS text_similarity,
        COALESCE(v.metadata, t.metadata) AS metadata,
        COALESCE(v.doc_title, t.doc_title) AS document_title,
        COALESCE(t.doc_source, t.doc_source) AS document_source
    FROM vector_results v
    FULL OUTER JOIN text_results t ON v.chunk_id = t.chunk_id
    ORDER BY combined_score DESC
    LIMIT match_count;
END;
$$;

-- New: Knowledge graph search functions
CREATE OR REPLACE FUNCTION search_entities(
    search_query TEXT,
    group_ids TEXT[] DEFAULT NULL,
    limit_count INT DEFAULT 10
)
RETURNS TABLE (
    uuid UUID,
    name TEXT,
    summary TEXT,
    entity_type TEXT,
    group_id TEXT,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        e.uuid,
        e.name,
        e.summary,
        e.entity_type,
        e.group_id,
        e.metadata,
        e.created_at
    FROM entities e
    WHERE (group_ids IS NULL OR e.group_id = ANY(group_ids))
    AND (
        e.name ILIKE '%' || search_query || '%'
        OR e.summary ILIKE '%' || search_query || '%'
        OR to_tsvector('english', e.name || ' ' || e.summary) @@ plainto_tsquery('english', search_query)
    )
    ORDER BY 
        CASE 
            WHEN e.name ILIKE search_query THEN 1
            WHEN e.name ILIKE '%' || search_query || '%' THEN 2
            ELSE 3
        END,
        e.created_at DESC
    LIMIT limit_count;
END;
$$;

CREATE OR REPLACE FUNCTION search_relationships(
    search_query TEXT,
    group_ids TEXT[] DEFAULT NULL,
    limit_count INT DEFAULT 10
)
RETURNS TABLE (
    uuid UUID,
    name TEXT,
    fact TEXT,
    source_node_uuid UUID,
    target_node_uuid UUID,
    group_id TEXT,
    valid_at TIMESTAMP WITH TIME ZONE,
    invalid_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        r.uuid,
        r.name,
        r.fact,
        r.source_node_uuid,
        r.target_node_uuid,
        r.group_id,
        r.valid_at,
        r.invalid_at,
        r.metadata,
        r.created_at
    FROM relationships r
    WHERE (group_ids IS NULL OR r.group_id = ANY(group_ids))
    AND (
        r.name ILIKE '%' || search_query || '%'
        OR r.fact ILIKE '%' || search_query || '%'
        OR to_tsvector('english', r.name || ' ' || r.fact) @@ plainto_tsquery('english', search_query)
    )
    ORDER BY 
        CASE 
            WHEN r.name ILIKE search_query THEN 1
            WHEN r.name ILIKE '%' || search_query || '%' THEN 2
            ELSE 3
        END,
        r.created_at DESC
    LIMIT limit_count;
END;
$$;

-- Utility functions
CREATE OR REPLACE FUNCTION get_document_chunks(doc_id UUID)
RETURNS TABLE (
    chunk_id UUID,
    content TEXT,
    chunk_index INTEGER,
    metadata JSONB
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        id AS chunk_id,
        chunks.content,
        chunks.chunk_index,
        chunks.metadata
    FROM chunks
    WHERE document_id = doc_id
    ORDER BY chunk_index;
END;
$$;

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers for updated_at columns
CREATE TRIGGER update_documents_updated_at BEFORE UPDATE ON documents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_sessions_updated_at BEFORE UPDATE ON sessions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_entities_updated_at BEFORE UPDATE ON entities
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_relationships_updated_at BEFORE UPDATE ON relationships
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_communities_updated_at BEFORE UPDATE ON communities
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_episodic_data_updated_at BEFORE UPDATE ON episodic_data
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Views for easier querying
CREATE OR REPLACE VIEW document_summaries AS
SELECT 
    d.id,
    d.title,
    d.source,
    d.created_at,
    d.updated_at,
    COUNT(c.id) AS chunk_count,
    d.metadata
FROM documents d
LEFT JOIN chunks c ON d.id = c.document_id
GROUP BY d.id, d.title, d.source, d.created_at, d.updated_at, d.metadata;

CREATE OR REPLACE VIEW entity_relationship_summary AS
SELECT 
    r.uuid,
    r.name,
    r.fact,
    r.valid_at,
    r.invalid_at,
    source.name AS source_entity_name,
    target.name AS target_entity_name,
    r.group_id,
    r.metadata
FROM relationships r
JOIN entities source ON r.source_node_uuid = source.uuid
JOIN entities target ON r.target_node_uuid = target.uuid; 