#!/usr/bin/env python3
"""
Check Documents in PostgreSQL Database
"""

import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import asyncpg
import json

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

load_dotenv()

async def check_database_documents():
    """Check what documents and files are stored in the PostgreSQL database."""
    
    try:
        # Get database URL from environment
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            print("❌ DATABASE_URL environment variable not set")
            return
        
        print("🔍 Checking PostgreSQL Database Documents")
        print("=" * 60)
        
        # Connect to database
        conn = await asyncpg.connect(database_url)
        
        # Check documents table
        print("\n📄 DOCUMENTS TABLE:")
        print("-" * 30)
        
        documents = await conn.fetch("""
            SELECT 
                id,
                title,
                source,
                LENGTH(content) as content_length,
                metadata,
                created_at,
                updated_at
            FROM documents 
            ORDER BY created_at DESC
        """)
        
        if documents:
            print(f"✅ Found {len(documents)} documents in database:")
            print()
            
            for i, doc in enumerate(documents, 1):
                print(f"{i}. 📄 {doc['title']}")
                print(f"   📍 Source: {doc['source']}")
                print(f"   📏 Content Length: {doc['content_length']:,} characters")
                print(f"   📅 Created: {doc['created_at']}")
                print(f"   🔄 Updated: {doc['updated_at']}")
                
                # Show metadata if available
                if doc['metadata'] and doc['metadata'] != {}:
                    print(f"   📋 Metadata: {json.dumps(doc['metadata'], indent=2)}")
                
                print()
        else:
            print("❌ No documents found in database")
        
        # Check chunks table
        print("\n🧩 CHUNKS TABLE:")
        print("-" * 30)
        
        chunks = await conn.fetch("""
            SELECT 
                COUNT(*) as total_chunks,
                COUNT(DISTINCT document_id) as unique_documents,
                AVG(LENGTH(content)) as avg_chunk_length,
                MIN(LENGTH(content)) as min_chunk_length,
                MAX(LENGTH(content)) as max_chunk_length
            FROM chunks
        """)
        
        if chunks and chunks[0]['total_chunks'] > 0:
            chunk_info = chunks[0]
            print(f"✅ Found {chunk_info['total_chunks']} chunks from {chunk_info['unique_documents']} documents")
            print(f"   📊 Average chunk length: {chunk_info['avg_chunk_length']:.0f} characters")
            print(f"   📏 Chunk size range: {chunk_info['min_chunk_length']} - {chunk_info['max_chunk_length']} characters")
        else:
            print("❌ No chunks found in database")
        
        # Check embeddings
        print("\n🧠 EMBEDDINGS:")
        print("-" * 30)
        
        embeddings = await conn.fetch("""
            SELECT 
                COUNT(*) as total_embeddings,
                COUNT(*) FILTER (WHERE embedding IS NOT NULL) as with_embeddings,
                COUNT(*) FILTER (WHERE embedding IS NULL) as without_embeddings
            FROM chunks
        """)
        
        if embeddings:
            emb_info = embeddings[0]
            print(f"✅ Total chunks: {emb_info['total_embeddings']}")
            print(f"   🧠 With embeddings: {emb_info['with_embeddings']}")
            print(f"   ⚠️  Without embeddings: {emb_info['without_embeddings']}")
            
            if emb_info['with_embeddings'] > 0:
                # Get embedding dimension
                sample_embedding = await conn.fetchval("""
                    SELECT embedding FROM chunks 
                    WHERE embedding IS NOT NULL 
                    LIMIT 1
                """)
                if sample_embedding:
                    dimension = len(sample_embedding)
                    print(f"   📐 Embedding dimension: {dimension}")
        
        # Check messages table
        print("\n💬 MESSAGES TABLE:")
        print("-" * 30)
        
        messages = await conn.fetch("""
            SELECT 
                COUNT(*) as total_messages,
                COUNT(DISTINCT session_id) as unique_sessions,
                COUNT(*) FILTER (WHERE role = 'user') as user_messages,
                COUNT(*) FILTER (WHERE role = 'assistant') as assistant_messages,
                COUNT(*) FILTER (WHERE role = 'system') as system_messages
            FROM messages
        """)
        
        if messages:
            msg_info = messages[0]
            print(f"✅ Found {msg_info['total_messages']} messages in {msg_info['unique_sessions']} sessions")
            print(f"   👤 User messages: {msg_info['user_messages']}")
            print(f"   🤖 Assistant messages: {msg_info['assistant_messages']}")
            print(f"   ⚙️  System messages: {msg_info['system_messages']}")
        
        # Show recent documents with sample content
        print("\n📋 RECENT DOCUMENTS (Sample Content):")
        print("-" * 50)
        
        recent_docs = await conn.fetch("""
            SELECT 
                title,
                source,
                LEFT(content, 200) as content_preview,
                created_at
            FROM documents 
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        
        for i, doc in enumerate(recent_docs, 1):
            print(f"{i}. 📄 {doc['title']}")
            print(f"   📍 Source: {doc['source']}")
            print(f"   📅 Created: {doc['created_at']}")
            print(f"   📝 Preview: {doc['content_preview']}...")
            print()
        
        # Check database size
        print("\n💾 DATABASE SIZE:")
        print("-" * 30)
        
        try:
            db_size = await conn.fetchval("""
                SELECT pg_size_pretty(pg_database_size(current_database()))
            """)
            print(f"✅ Database size: {db_size}")
        except Exception as e:
            print(f"⚠️  Could not get database size: {e}")
        
        await conn.close()
        
        print("\n" + "=" * 60)
        print("✅ Database check complete!")
        
    except Exception as e:
        print(f"❌ Error checking database: {e}")
        import traceback
        traceback.print_exc()

async def search_documents(query: str):
    """Search for documents containing specific text."""
    
    try:
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            print("❌ DATABASE_URL environment variable not set")
            return
        
        print(f"\n🔍 SEARCHING FOR: '{query}'")
        print("=" * 50)
        
        conn = await asyncpg.connect(database_url)
        
        # Search in documents
        docs = await conn.fetch("""
            SELECT 
                title,
                source,
                created_at,
                LENGTH(content) as content_length
            FROM documents 
            WHERE 
                title ILIKE $1 OR 
                content ILIKE $1 OR
                source ILIKE $1
            ORDER BY created_at DESC
        """, f'%{query}%')
        
        if docs:
            print(f"✅ Found {len(docs)} documents matching '{query}':")
            print()
            
            for i, doc in enumerate(docs, 1):
                print(f"{i}. 📄 {doc['title']}")
                print(f"   📍 Source: {doc['source']}")
                print(f"   📏 Size: {doc['content_length']:,} characters")
                print(f"   📅 Created: {doc['created_at']}")
                print()
        else:
            print(f"❌ No documents found matching '{query}'")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ Error searching documents: {e}")

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Check PostgreSQL database documents")
    parser.add_argument("--search", "-s", help="Search for documents containing this text")
    
    args = parser.parse_args()
    
    if args.search:
        asyncio.run(search_documents(args.search))
    else:
        asyncio.run(check_database_documents())

if __name__ == "__main__":
    main() 