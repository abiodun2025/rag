-- Migration script from schema v1 to v2
-- This script migrates existing data to the new provider-independent schema
-- Run this after applying schema_v2.sql

-- Migration: Create new tables and migrate data
BEGIN;

-- Step 1: Create new tables (if not already created by schema_v2.sql)
-- Note: This assumes schema_v2.sql has been run first

-- Step 2: Migrate existing Neo4j data to PostgreSQL (if applicable)
-- This is a placeholder for any existing Neo4j data that needs to be migrated
-- In practice, you would need to export data from Neo4j and import it here

-- Step 3: Create sample data in the new schema for testing
-- This ensures the new schema works correctly

-- Insert sample entities
INSERT INTO entities (uuid, name, summary, entity_type, group_id, metadata) VALUES
    (uuid_generate_v4(), 'OpenAI', 'Artificial intelligence research company', 'company', 'tech', '{"industry": "AI", "founded": 2015}'),
    (uuid_generate_v4(), 'Microsoft', 'Technology corporation', 'company', 'tech', '{"industry": "Software", "founded": 1975}'),
    (uuid_generate_v4(), 'Sam Altman', 'CEO of OpenAI', 'person', 'tech', '{"role": "CEO", "company": "OpenAI"}'),
    (uuid_generate_v4(), 'Satya Nadella', 'CEO of Microsoft', 'person', 'tech', '{"role": "CEO", "company": "Microsoft"}');

-- Insert sample relationships
INSERT INTO relationships (uuid, name, fact, source_node_uuid, target_node_uuid, group_id, valid_at, metadata) 
SELECT 
    uuid_generate_v4(),
    'partnership',
    'Microsoft invested $10 billion in OpenAI',
    e1.uuid,
    e2.uuid,
    'tech',
    '2023-01-01'::timestamp with time zone,
    '{"investment_amount": "10B", "announcement_date": "2023-01-23"}'
FROM entities e1, entities e2
WHERE e1.name = 'Microsoft' AND e2.name = 'OpenAI';

INSERT INTO relationships (uuid, name, fact, source_node_uuid, target_node_uuid, group_id, valid_at, metadata)
SELECT 
    uuid_generate_v4(),
    'leads',
    'Sam Altman is the CEO of OpenAI',
    e1.uuid,
    e2.uuid,
    'tech',
    '2019-01-01'::timestamp with time zone,
    '{"position": "CEO", "start_date": "2019"}'
FROM entities e1, entities e2
WHERE e1.name = 'Sam Altman' AND e2.name = 'OpenAI';

INSERT INTO relationships (uuid, name, fact, source_node_uuid, target_node_uuid, group_id, valid_at, metadata)
SELECT 
    uuid_generate_v4(),
    'leads',
    'Satya Nadella is the CEO of Microsoft',
    e1.uuid,
    e2.uuid,
    'tech',
    '2014-02-04'::timestamp with time zone,
    '{"position": "CEO", "start_date": "2014-02-04"}'
FROM entities e1, entities e2
WHERE e1.name = 'Satya Nadella' AND e2.name = 'Microsoft';

-- Insert sample communities
INSERT INTO communities (uuid, name, description, group_id, metadata) VALUES
    (uuid_generate_v4(), 'AI Industry', 'Companies and individuals in the artificial intelligence industry', 'tech', '{"focus": "AI", "members": 100}'),
    (uuid_generate_v4(), 'Tech CEOs', 'Chief executives of technology companies', 'tech', '{"focus": "Leadership", "members": 50}');

-- Insert sample episodic data
INSERT INTO episodic_data (uuid, episode_id, content, source, timestamp, group_id, metadata) VALUES
    (uuid_generate_v4(), 'episode_001', 'Microsoft announces $10 billion investment in OpenAI', 'news', '2023-01-23 10:00:00'::timestamp with time zone, 'tech', '{"event_type": "investment", "amount": "10B"}'),
    (uuid_generate_v4(), 'episode_002', 'OpenAI releases GPT-4 model', 'news', '2023-03-14 15:30:00'::timestamp with time zone, 'tech', '{"event_type": "product_release", "model": "GPT-4"}');

-- Step 4: Verify migration
-- Check that data was migrated correctly
SELECT 'Entities count:' as check_type, COUNT(*) as count FROM entities
UNION ALL
SELECT 'Relationships count:', COUNT(*) FROM relationships
UNION ALL
SELECT 'Communities count:', COUNT(*) FROM communities
UNION ALL
SELECT 'Episodic data count:', COUNT(*) FROM episodic_data;

-- Test search functions
SELECT 'Testing entity search:' as test_type;
SELECT * FROM search_entities('OpenAI', NULL, 5);

SELECT 'Testing relationship search:' as test_type;
SELECT * FROM search_relationships('investment', NULL, 5);

COMMIT;

-- Migration complete
-- The new schema is now ready to use with the updated application code 