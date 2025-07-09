#!/usr/bin/env python3
"""Check Neo4j schema for RELATES_TO relationship properties."""

import asyncio
import os
from agent.graph_utils import GraphitiClient

async def check_neo4j_schema():
    """Check Neo4j schema for missing properties."""
    client = GraphitiClient()
    
    try:
        await client.initialize()
        print("✓ Graphiti client initialized")
        
        if not client.graphiti or not client.graphiti.driver:
            print("✗ No Graphiti driver available")
            return
        
        # Check RELATES_TO relationship properties
        async with client.graphiti.driver.session(database="neo4j") as session:
            # Get all RELATES_TO relationships and their properties
            result = await session.run("""
                MATCH ()-[r:RELATES_TO]->()
                RETURN DISTINCT keys(r) as properties
                LIMIT 5
            """)
            
            properties_found = set()
            async for record in result:
                props = record["properties"]
                properties_found.update(props)
                print(f"Found properties: {props}")
            
            print(f"\nAll properties found: {sorted(properties_found)}")
            
            # Check if episodes and fact_embedding exist
            missing_props = []
            if "episodes" not in properties_found:
                missing_props.append("episodes")
            if "fact_embedding" not in properties_found:
                missing_props.append("fact_embedding")
            
            if missing_props:
                print(f"\n❌ Missing properties: {missing_props}")
                print("These properties need to be added to RELATES_TO relationships")
            else:
                print("\n✅ All required properties exist")
            
            # Check if there are any RELATES_TO relationships at all
            count_result = await session.run("MATCH ()-[r:RELATES_TO]->() RETURN count(r) as count")
            count_record = await count_result.single()
            count = count_record["count"]
            print(f"\nTotal RELATES_TO relationships: {count}")
            
            if count == 0:
                print("⚠️  No RELATES_TO relationships found. Need to ingest documents first.")
            
    except Exception as e:
        print(f"Error checking schema: {e}")
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(check_neo4j_schema()) 