#!/usr/bin/env python3
"""
Test the knowledge graph data.
"""

import asyncio
import os
from dotenv import load_dotenv
from neo4j import AsyncGraphDatabase

# Load environment variables
load_dotenv()

async def test_knowledge_graph():
    """Test the knowledge graph data."""
    # Create Neo4j driver
    driver = AsyncGraphDatabase.driver(
        os.getenv("NEO4J_URI", "bolt://localhost:7687"),
        auth=(os.getenv("NEO4J_USER", "neo4j"), os.getenv("NEO4J_PASSWORD", "agenticrag"))
    )
    
    try:
        async with driver.session() as session:
            # Test entities
            print("=== Testing Entities ===")
            result = await session.run("MATCH (e:Entity) RETURN e.name as name, e.entity_type as type LIMIT 5")
            records = await result.data()
            for record in records:
                print(f"Entity: {record['name']} ({record['type']})")
            
            # Test episodes
            print("\n=== Testing Episodes ===")
            result = await session.run("MATCH (ep:Episodic) RETURN ep.source as source, ep.content as content LIMIT 3")
            records = await result.data()
            for record in records:
                print(f"Episode: {record['source']}")
                print(f"Content: {record['content'][:100]}...")
                print()
            
            # Test relationships
            print("=== Testing Relationships ===")
            result = await session.run("MATCH (a:Entity)-[r:RELATES_TO]->(b:Entity) RETURN a.name as source, r.name as rel, b.name as target LIMIT 5")
            records = await result.data()
            for record in records:
                print(f"Relationship: {record['source']} --[{record['rel']}]--> {record['target']}")
            
            # Test search
            print("\n=== Testing Search ===")
            result = await session.run("""
                MATCH (e:Entity)
                WHERE toLower(e.name) CONTAINS toLower('OpenAI') OR toLower(e.summary) CONTAINS toLower('OpenAI')
                RETURN e.name as name, e.summary as summary
            """)
            records = await result.data()
            for record in records:
                print(f"Search result: {record['name']} - {record['summary']}")
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await driver.close()

if __name__ == "__main__":
    asyncio.run(test_knowledge_graph()) 