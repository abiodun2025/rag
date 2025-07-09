#!/usr/bin/env python3
"""
Debug logging setup for the Agentic RAG system.

This script shows how to enable comprehensive debug logging for troubleshooting.
"""

import logging
import os
import sys
from datetime import datetime

def setup_debug_logging():
    """
    Setup comprehensive debug logging for the entire system.
    
    This function configures logging to capture detailed information about:
    - API requests and responses
    - Agent execution
    - Tool calls and their results
    - Database operations
    - Graph operations
    - Embedding generation
    - Error details with full stack traces
    """
    
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Generate timestamp for log file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"logs/rag_debug_{timestamp}.log"
    
    # Configure root logger
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            # Console handler with INFO level (less verbose)
            logging.StreamHandler(sys.stdout),
            # File handler with DEBUG level (very verbose)
            logging.FileHandler(log_filename, mode='w')
        ]
    )
    
    # Set specific loggers to DEBUG level
    debug_loggers = [
        'agent',
        'agent.api',
        'agent.agent',
        'agent.tools',
        'agent.db_utils',
        'agent.graph_utils',
        'agent.providers',
        'ingestion',
        'ingestion.chunker',
        'ingestion.embedder',
        'ingestion.graph_builder',
        'ingestion.ingest',
        'anthropic',
        'httpx',
        'asyncio',
        'uvicorn',
        'fastapi'
    ]
    
    for logger_name in debug_loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)
    
    # Set environment variable for log level
    os.environ['LOG_LEVEL'] = 'DEBUG'
    
    # Log startup information
    root_logger = logging.getLogger()
    root_logger.info("=" * 80)
    root_logger.info("DEBUG LOGGING ENABLED")
    root_logger.info("=" * 80)
    root_logger.info(f"Log file: {log_filename}")
    root_logger.info(f"Python version: {sys.version}")
    root_logger.info(f"Current working directory: {os.getcwd()}")
    root_logger.info("=" * 80)
    
    return log_filename

def setup_console_debug_logging():
    """
    Setup debug logging for console output only (no file logging).
    
    Useful for development and quick debugging.
    """
    
    # Configure root logger for console only
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Set specific loggers to DEBUG level
    debug_loggers = [
        'agent',
        'agent.api',
        'agent.agent',
        'agent.tools',
        'agent.db_utils',
        'agent.graph_utils',
        'agent.providers',
        'ingestion',
        'ingestion.chunker',
        'ingestion.embedder',
        'ingestion.graph_builder',
        'ingestion.ingest',
        'anthropic',
        'httpx',
        'asyncio',
        'uvicorn',
        'fastapi'
    ]
    
    for logger_name in debug_loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)
    
    # Set environment variable for log level
    os.environ['LOG_LEVEL'] = 'DEBUG'
    
    # Log startup information
    root_logger = logging.getLogger()
    root_logger.info("=" * 80)
    root_logger.info("CONSOLE DEBUG LOGGING ENABLED")
    root_logger.info("=" * 80)
    root_logger.info(f"Python version: {sys.version}")
    root_logger.info(f"Current working directory: {os.getcwd()}")
    root_logger.info("=" * 80)

def get_debug_logger(name: str) -> logging.Logger:
    """
    Get a logger configured for debug output.
    
    Args:
        name: Logger name (usually __name__)
    
    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    return logger

def log_system_info():
    """
    Log system information for debugging purposes.
    """
    logger = logging.getLogger(__name__)
    
    logger.info("System Information:")
    logger.info(f"  Python version: {sys.version}")
    logger.info(f"  Platform: {sys.platform}")
    logger.info(f"  Working directory: {os.getcwd()}")
    logger.info(f"  Environment variables:")
    
    # Log relevant environment variables
    relevant_vars = [
        'LOG_LEVEL', 'LLM_CHOICE', 'LLM_API_KEY', 'LLM_BASE_URL',
        'EMBEDDING_MODEL', 'EMBEDDING_API_KEY', 'EMBEDDING_BASE_URL',
        'DATABASE_URL', 'NEO4J_URI', 'NEO4J_USERNAME', 'NEO4J_PASSWORD',
        'APP_ENV', 'APP_HOST', 'APP_PORT'
    ]
    
    for var in relevant_vars:
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            if 'PASSWORD' in var or 'API_KEY' in var:
                masked_value = value[:4] + '*' * (len(value) - 8) + value[-4:] if len(value) > 8 else '***'
                logger.info(f"    {var}: {masked_value}")
            else:
                logger.info(f"    {var}: {value}")
        else:
            logger.info(f"    {var}: <not set>")

if __name__ == "__main__":
    # Example usage
    print("Debug Logging Setup")
    print("==================")
    print()
    print("1. Setup file and console logging:")
    print("   from debug_setup import setup_debug_logging")
    print("   log_file = setup_debug_logging()")
    print()
    print("2. Setup console-only logging:")
    print("   from debug_setup import setup_console_debug_logging")
    print("   setup_console_debug_logging()")
    print()
    print("3. Get a debug logger:")
    print("   from debug_setup import get_debug_logger")
    print("   logger = get_debug_logger(__name__)")
    print()
    print("4. Log system information:")
    print("   from debug_setup import log_system_info")
    print("   log_system_info()")
    print()
    
    # Demonstrate the setup
    print("Setting up debug logging...")
    log_file = setup_debug_logging()
    print(f"Debug logging enabled. Log file: {log_file}")
    
    # Log some example information
    logger = get_debug_logger(__name__)
    logger.info("Debug logging setup completed successfully")
    log_system_info() 