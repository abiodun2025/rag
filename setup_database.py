#!/usr/bin/env python3
"""
Dynamic database setup script that detects embedding dimensions and creates the appropriate schema.
"""

import asyncio
import os
import subprocess
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

from ingestion.embedder import EmbeddingGenerator

load_dotenv()

async def detect_embedding_dimension():
    """Detect the embedding dimension from the configured model."""
    try:
        # Create embedder to detect dimension
        embedder = EmbeddingGenerator()
        
        # Generate a test embedding to detect dimension
        test_text = "This is a test embedding to detect the dimension."
        embedding = await embedder.generate_embedding(test_text)
        
        dimension = len(embedding)
        print(f"✓ Detected embedding dimension: {dimension}")
        return dimension
        
    except Exception as e:
        print(f"✗ Failed to detect embedding dimension: {e}")
        # Fallback to default
        default_dim = int(os.getenv('VECTOR_DIMENSION', '1024'))
        print(f"⚠ Using default dimension: {default_dim}")
        return default_dim

def setup_database(dimension: int):
    """Set up the database with the correct embedding dimension."""
    try:
        # Get database URL from environment
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            print("✗ DATABASE_URL environment variable not set")
            return False
        
        # Extract database name from URL
        if database_url.startswith('postgresql://'):
            db_name = database_url.split('/')[-1].split('?')[0]
        else:
            print("✗ Invalid DATABASE_URL format")
            return False
        
        print(f"✓ Setting up database: {db_name}")
        
        # Generate schema with correct dimension
        schema_path = Path(__file__).parent / "sql" / "schema_dynamic.sql"
        if not schema_path.exists():
            print(f"✗ Schema file not found: {schema_path}")
            return False
        
        # Read schema template
        with open(schema_path, 'r') as f:
            schema_content = f.read()
        
        # Replace placeholder with actual dimension
        schema_content = schema_content.replace('__EMBEDDING_DIMENSION__', str(dimension))
        
        # Write temporary schema file
        temp_schema_path = Path(__file__).parent / "sql" / "schema_temp.sql"
        with open(temp_schema_path, 'w') as f:
            f.write(schema_content)
        
        # Execute schema
        print(f"✓ Applying schema with {dimension}-dimensional embeddings...")
        
        # Use psql to execute the schema
        cmd = [
            'psql',
            '-d', database_url,
            '-f', str(temp_schema_path),
            '-q'  # Quiet mode
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Clean up temp file
        temp_schema_path.unlink()
        
        if result.returncode == 0:
            print("✓ Database schema applied successfully")
            return True
        else:
            print(f"✗ Failed to apply schema: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"✗ Database setup failed: {e}")
        return False

async def main():
    """Main function to set up the database."""
    print("🔧 Setting up database with dynamic embedding dimensions...")
    
    # Detect embedding dimension
    dimension = await detect_embedding_dimension()
    
    # Set up database
    success = setup_database(dimension)
    
    if success:
        print(f"✅ Database setup complete with {dimension}-dimensional embeddings")
        print(f"💡 You can now run: python -m ingestion.ingest --clean")
    else:
        print("❌ Database setup failed")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 