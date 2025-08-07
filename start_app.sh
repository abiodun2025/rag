#!/bin/bash

# Set environment variables
export DATABASE_URL="sqlite:///rag.db"
export NEO4J_PASSWORD="agenticrag"
export LLM_API_KEY="test_key_for_development"
export EMBEDDING_API_KEY="test_embedding_key_for_development"
export OPENAI_API_KEY="test_openai_key_for_development"

echo "🚀 Starting Agentic RAG API..."
echo "📊 Database: SQLite"
echo "🧠 Graph Database: Neo4j"
echo "🔗 API: http://localhost:8000"
echo ""

# Start the API server
python3 -m agent.api 