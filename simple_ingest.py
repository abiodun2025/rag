#!/usr/bin/env python3
"""
Simplified document ingestion script for PostgreSQL only (no Neo4j)
"""

import asyncio
import os
import logging
import json
import glob
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import argparse

import asyncpg
from dotenv import load_dotenv

# Add the project root to the path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from ingestion.chunker import ChunkingConfig, create_chunker, DocumentChunk
from ingestion.embedder import create_embedder

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class SimpleDocumentIngestionPipeline:
    """Simplified pipeline for ingesting documents into PostgreSQL only."""
    
    def __init__(
        self,
        documents_folder: str = "big_tech_docs",
        clean_before_ingest: bool = False,
        chunk_size: int = 800,
        chunk_overlap: int = 150
    ):
        """
        Initialize ingestion pipeline.
        
        Args:
            documents_folder: Folder containing markdown documents
            clean_before_ingest: Whether to clean existing data before ingestion
            chunk_size: Size of document chunks
            chunk_overlap: Overlap between chunks
        """
        self.documents_folder = documents_folder
        self.clean_before_ingest = clean_before_ingest
        
        # Initialize components
        self.chunker_config = ChunkingConfig(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_chunk_size=chunk_size * 2,
            use_semantic_splitting=True
        )
        
        self.chunker = create_chunker(self.chunker_config)
        self.embedder = create_embedder()
        
        # Database connection
        self.db_pool = None
        self._initialized = False
    
    async def initialize(self):
        """Initialize database connection."""
        if self._initialized:
            return
        
        logger.info("Initializing ingestion pipeline...")
        
        # Get database URL from environment
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            raise ValueError("DATABASE_URL environment variable not set")
        
        # Create database connection pool
        self.db_pool = await asyncpg.create_pool(database_url)
        
        self._initialized = True
        logger.info("Ingestion pipeline initialized")
    
    async def close(self):
        """Close database connection."""
        if self._initialized and self.db_pool:
            await self.db_pool.close()
            self._initialized = False
    
    async def ingest_documents(self, progress_callback: Optional[callable] = None) -> List[Dict[str, Any]]:
        """
        Ingest all documents from the documents folder.
        
        Args:
            progress_callback: Optional callback for progress updates
            
        Returns:
            List of ingestion results
        """
        await self.initialize()
        
        if self.clean_before_ingest:
            await self._clean_database()
        
        # Find all markdown files
        markdown_files = self._find_markdown_files()
        
        if not markdown_files:
            logger.warning(f"No markdown files found in {self.documents_folder}")
            return []
        
        logger.info(f"Found {len(markdown_files)} markdown files to process")
        
        results = []
        for i, file_path in enumerate(markdown_files):
            try:
                logger.info(f"Processing {file_path} ({i+1}/{len(markdown_files)})")
                
                result = await self._ingest_single_document(file_path)
                results.append(result)
                
                if progress_callback:
                    progress_callback(i + 1, len(markdown_files))
                    
            except Exception as e:
                logger.error(f"Failed to process {file_path}: {e}")
                results.append({
                    "title": Path(file_path).name,
                    "source": file_path,
                    "success": False,
                    "error": str(e),
                    "chunks_created": 0
                })
        
        return results
    
    async def _ingest_single_document(self, file_path: str) -> Dict[str, Any]:
        """Ingest a single document."""
        try:
            # Read document content
            content = self._read_document(file_path)
            title = self._extract_title(content, file_path)
            metadata = self._extract_document_metadata(content, file_path)
            
            # Chunk the document
            chunks = await self.chunker.chunk_document(content, file_path, metadata)
            
            # Generate embeddings for chunks
            for chunk in chunks:
                if chunk.content.strip():
                    chunk.embedding = await self.embedder.generate_embedding(chunk.content)
            
            # Save to PostgreSQL
            document_id = await self._save_to_postgres(title, file_path, content, chunks, metadata)
            
            return {
                "title": title,
                "source": file_path,
                "success": True,
                "document_id": document_id,
                "chunks_created": len(chunks),
                "content_length": len(content)
            }
            
        except Exception as e:
            logger.error(f"Error ingesting {file_path}: {e}")
            return {
                "title": Path(file_path).name,
                "source": file_path,
                "success": False,
                "error": str(e),
                "chunks_created": 0
            }
    
    def _find_markdown_files(self) -> List[str]:
        """Find all markdown files in the documents folder."""
        pattern = os.path.join(self.documents_folder, "*.md")
        return glob.glob(pattern)
    
    def _read_document(self, file_path: str) -> str:
        """Read document content from file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _extract_title(self, content: str, file_path: str) -> str:
        """Extract title from document content or filename."""
        # Try to extract title from first heading
        lines = content.split('\n')
        for line in lines:
            if line.startswith('# '):
                return line[2:].strip()
        
        # Fallback to filename
        return Path(file_path).stem.replace('_', ' ').title()
    
    def _extract_document_metadata(self, content: str, file_path: str) -> Dict[str, Any]:
        """Extract metadata from document."""
        return {
            "source_file": file_path,
            "file_size": len(content),
            "word_count": len(content.split()),
            "ingested_at": datetime.now().isoformat()
        }
    
    async def _save_to_postgres(
        self,
        title: str,
        source: str,
        content: str,
        chunks: List[DocumentChunk],
        metadata: Dict[str, Any]
    ) -> str:
        """Save document and chunks to PostgreSQL."""
        async with self.db_pool.acquire() as conn:
            async with conn.transaction():
                # Insert document
                document_id = await conn.fetchval("""
                    INSERT INTO documents (title, source, content, metadata)
                    VALUES ($1, $2, $3, $4)
                    RETURNING id
                """, title, source, content, json.dumps(metadata))
                
                # Insert chunks
                for chunk in chunks:
                    if chunk.embedding is not None:
                        await conn.execute("""
                            INSERT INTO chunks (document_id, content, embedding, chunk_index, metadata, token_count)
                            VALUES ($1, $2, $3, $4, $5, $6)
                        """, document_id, chunk.content, chunk.embedding, chunk.index, json.dumps(chunk.metadata), chunk.token_count)
                
                return str(document_id)
    
    async def _clean_database(self):
        """Clean existing data from database."""
        logger.warning("Cleaning existing data from database...")
        
        async with self.db_pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute("DELETE FROM chunks")
                await conn.execute("DELETE FROM documents")
        
        logger.info("Cleaned database")


async def main():
    """Main function for running ingestion."""
    parser = argparse.ArgumentParser(description="Ingest documents into PostgreSQL")
    parser.add_argument("--documents", "-d", default="big_tech_docs", help="Documents folder path")
    parser.add_argument("--clean", "-c", action="store_true", help="Clean existing data before ingestion")
    parser.add_argument("--chunk-size", type=int, default=800, help="Chunk size for splitting documents")
    parser.add_argument("--chunk-overlap", type=int, default=150, help="Chunk overlap size")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Create and run pipeline
    pipeline = SimpleDocumentIngestionPipeline(
        documents_folder=args.documents,
        clean_before_ingest=args.clean,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap
    )
    
    def progress_callback(current: int, total: int):
        print(f"Progress: {current}/{total} documents processed")
    
    try:
        start_time = datetime.now()
        
        results = await pipeline.ingest_documents(progress_callback)
        
        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds()
        
        # Print summary
        print("\n" + "="*50)
        print("INGESTION SUMMARY")
        print("="*50)
        print(f"Documents processed: {len(results)}")
        print(f"Successful: {sum(1 for r in results if r['success'])}")
        print(f"Failed: {sum(1 for r in results if not r['success'])}")
        print(f"Total chunks created: {sum(r.get('chunks_created', 0) for r in results if r['success'])}")
        print(f"Total processing time: {total_time:.2f} seconds")
        print()
        
        # Print individual results
        for result in results:
            status = "✓" if result['success'] else "✗"
            print(f"{status} {result['title']}: {result.get('chunks_created', 0)} chunks")
            
            if not result['success']:
                print(f"  Error: {result.get('error', 'Unknown error')}")
        
    except KeyboardInterrupt:
        print("\nIngestion interrupted by user")
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        raise
    finally:
        await pipeline.close()


if __name__ == "__main__":
    asyncio.run(main()) 