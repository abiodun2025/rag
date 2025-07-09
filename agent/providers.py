"""
Flexible provider configuration for LLM and embedding models.
"""

import os
from typing import Optional, Union
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.models.openai import OpenAIModel
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def get_llm_model(model_choice: Optional[str] = None) -> Union[OpenAIModel, 'CohereLLMModel']:
    """
    Get LLM model configuration based on environment variables.
    
    Args:
        model_choice: Optional override for model choice
    
    Returns:
        Configured model (OpenAI or Cohere)
    """
    provider = get_llm_provider()
    
    if provider.lower() == 'cohere':
        # Use Cohere LLM
        try:
            import cohere
            api_key = os.getenv('LLM_API_KEY')
            if not api_key:
                raise ValueError("LLM_API_KEY environment variable not set for Cohere")
            model_name = model_choice or os.getenv('LLM_CHOICE', 'command-r-plus')
            return CohereLLMModel(api_key, model_name)
        except ImportError:
            raise ImportError("Cohere library not installed. Run: pip install cohere")
    else:
        # Use OpenAI for all other providers
        llm_choice = model_choice or os.getenv('LLM_CHOICE', 'gpt-4-turbo-preview')
        base_url = os.getenv('LLM_BASE_URL', 'https://api.openai.com/v1')
        api_key = os.getenv('LLM_API_KEY', 'ollama')
        
        provider = OpenAIProvider(base_url=base_url, api_key=api_key)
        return OpenAIModel(llm_choice, provider=provider)


class CohereLLMModel:
    """Wrapper for Cohere LLM to maintain compatibility with OpenAI model interface."""
    
    def __init__(self, api_key: str, model: str):
        """Initialize Cohere LLM model."""
        import cohere
        self.client = cohere.AsyncClient(api_key)
        self.model = model
    
    async def generate(self, prompt: str, **kwargs):
        """Generate text using Cohere API."""
        response = await self.client.chat(
            message=prompt,
            model=self.model,
            **kwargs
        )
        
        # Convert to OpenAI-compatible response format
        return CohereLLMResponse(response)


class CohereLLMResponse:
    """Cohere LLM response compatible with OpenAI response format."""
    
    def __init__(self, cohere_response):
        """Initialize response wrapper."""
        self.cohere_response = cohere_response
        self.choices = [CohereLLMChoice(cohere_response)]


class CohereLLMChoice:
    """Cohere LLM choice compatible with OpenAI choice format."""
    
    def __init__(self, cohere_response):
        """Initialize choice wrapper."""
        self.cohere_response = cohere_response
        self.message = CohereLLMMessage(cohere_response)


class CohereLLMMessage:
    """Cohere LLM message compatible with OpenAI message format."""
    
    def __init__(self, cohere_response):
        """Initialize message wrapper."""
        self.cohere_response = cohere_response
        self.content = cohere_response.text


def get_embedding_client() -> Union[openai.AsyncOpenAI, 'CohereClient']:
    """
    Get embedding client configuration based on environment variables.
    
    Returns:
        Configured client for embeddings (OpenAI or Cohere)
    """
    provider = get_embedding_provider()
    
    if provider.lower() == 'cohere':
        # Use Cohere client
        try:
            import cohere
            api_key = os.getenv('EMBEDDING_API_KEY')
            if not api_key:
                raise ValueError("EMBEDDING_API_KEY environment variable not set for Cohere")
            return CohereClient(api_key)
        except ImportError:
            raise ImportError("Cohere library not installed. Run: pip install cohere")
    else:
        # Use OpenAI client for all other providers
        base_url = os.getenv('EMBEDDING_BASE_URL', 'https://api.openai.com/v1')
        api_key = os.getenv('EMBEDDING_API_KEY', 'ollama')
        
        return openai.AsyncOpenAI(
            base_url=base_url,
            api_key=api_key
        )


class CohereClient:
    """Wrapper for Cohere client to maintain compatibility with OpenAI client interface."""
    
    def __init__(self, api_key: str):
        """Initialize Cohere client."""
        import cohere
        self.client = cohere.AsyncClient(api_key)
    
    @property
    def embeddings(self):
        """Return embeddings interface compatible with OpenAI client."""
        return CohereEmbeddings(self.client)


class CohereEmbeddings:
    """Cohere embeddings interface compatible with OpenAI client."""
    
    def __init__(self, client):
        """Initialize Cohere embeddings interface."""
        self.client = client
    
    async def create(self, model: str, input: Union[str, list], **kwargs):
        """Create embeddings using Cohere API."""
        import cohere
        
        # Handle both single text and batch inputs
        if isinstance(input, str):
            texts = [input]
        else:
            texts = input
        
        # Call Cohere API with required input_type
        response = await self.client.embed(
            texts=texts,
            model=model,
            input_type="search_document",
            **kwargs
        )
        
        # Convert to OpenAI-compatible response format
        return CohereEmbeddingResponse(response, len(texts))


class CohereEmbeddingResponse:
    """Cohere embedding response compatible with OpenAI response format."""
    
    def __init__(self, cohere_response, num_texts: int):
        """Initialize response wrapper."""
        self.cohere_response = cohere_response
        self.data = [CohereEmbeddingData(embedding) for embedding in cohere_response.embeddings]


class CohereEmbeddingData:
    """Cohere embedding data compatible with OpenAI data format."""
    
    def __init__(self, embedding):
        """Initialize embedding data wrapper."""
        self.embedding = embedding


def get_llm_model_name() -> str:
    """
    Get LLM model name from environment.
    
    Returns:
        LLM model name
    """
    return os.getenv('LLM_CHOICE', 'gpt-4-turbo-preview')


def get_embedding_model() -> str:
    """
    Get embedding model name from environment.
    
    Returns:
        Embedding model name
    """
    return os.getenv('EMBEDDING_MODEL', 'text-embedding-3-small')


def get_ingestion_model() -> Union[OpenAIModel, 'CohereLLMModel']:
    """
    Get ingestion-specific LLM model (can be faster/cheaper than main model).
    
    Returns:
        Configured model for ingestion tasks
    """
    ingestion_choice = os.getenv('INGESTION_LLM_CHOICE')
    
    # If no specific ingestion model, use the main model
    if not ingestion_choice:
        return get_llm_model()
    
    return get_llm_model(model_choice=ingestion_choice)


# Provider information functions
def get_llm_provider() -> str:
    """Get the LLM provider name."""
    return os.getenv('LLM_PROVIDER', 'openai')


def get_embedding_provider() -> str:
    """Get the embedding provider name."""
    return os.getenv('EMBEDDING_PROVIDER', 'openai')


def validate_configuration() -> bool:
    """
    Validate that required environment variables are set.
    
    Returns:
        True if configuration is valid
    """
    required_vars = [
        'LLM_API_KEY',
        'LLM_CHOICE',
        'EMBEDDING_API_KEY',
        'EMBEDDING_MODEL'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"Missing required environment variables: {', '.join(missing_vars)}")
        return False
    
    return True


def get_model_info() -> dict:
    """
    Get information about current model configuration.
    
    Returns:
        Dictionary with model configuration info
    """
    return {
        "llm_provider": get_llm_provider(),
        "llm_model": os.getenv('LLM_CHOICE'),
        "llm_base_url": os.getenv('LLM_BASE_URL'),
        "embedding_provider": get_embedding_provider(),
        "embedding_model": get_embedding_model(),
        "embedding_base_url": os.getenv('EMBEDDING_BASE_URL'),
        "ingestion_model": os.getenv('INGESTION_LLM_CHOICE', 'same as main'),
    }