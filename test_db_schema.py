#!/usr/bin/env python3
"""Test database schema for embedding dimensions."""

import asyncio
import os
from agent.db_utils import db_pool

async def test_db_schema():
    """Test database schema for embedding dimensions."""
    try:
        await db_pool.initialize()
        
        async with db_pool.acquire() as conn:
            # Check if chunks table exists and has embedding column
            result = await conn.fetchrow("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'chunks' AND column_name = 'embedding'
            """)
            
            if result:
                print(f"✓ Embedding column found: {result['column_name']} ({result['data_type']})")
            else:
                print("✗ Embedding column not found in chunks table")
                return
            
            # Check if there are any chunks with embeddings
            count = await conn.fetchval("SELECT COUNT(*) FROM chunks WHERE embedding IS NOT NULL")
            print(f"✓ Chunks with embeddings: {count}")
            
            if count > 0:
                # Check the dimension of existing embeddings
                sample = await conn.fetchrow("SELECT embedding FROM chunks WHERE embedding IS NOT NULL LIMIT 1")
                if sample and sample['embedding']:
                    dim = len(sample['embedding'])
                    print(f"✓ Sample embedding dimension: {dim}")
                    
                    expected = int(os.getenv('VECTOR_DIMENSION', '1024'))
                    if dim == expected:
                        print(f"✓ Embedding dimension matches expected: {expected}")
                    else:
                        print(f"✗ Embedding dimension mismatch: got {dim}, expected {expected}")
        
        await db_pool.close()
        
    except Exception as e:
        print(f"✗ Database test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_db_schema()) 