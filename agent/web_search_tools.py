"""
Web Search Tools for the Master Agent.
"""

import asyncio
import logging
import requests
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
import json

logger = logging.getLogger(__name__)

@dataclass
class WebSearchResult:
    """Result from web search."""
    title: str
    url: str
    snippet: str
    source: str
    timestamp: str

class WebSearchTools:
    """Web search functionality for the master agent."""
    
    def __init__(self):
        self.search_history = []
        logger.info("Web search tools initialized")
    
    async def search_web(self, query: str, max_results: int = 5) -> List[WebSearchResult]:
        """
        Perform web search using DuckDuckGo API.
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            List of web search results
        """
        try:
            logger.info(f"Performing web search for: {query}")
            
            # Use DuckDuckGo Instant Answer API
            url = "https://api.duckduckgo.com/"
            params = {
                "q": query,
                "format": "json",
                "no_html": "1",
                "skip_disambig": "1"
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            results = []
            
            # Extract instant answer if available
            if data.get("Abstract"):
                results.append(WebSearchResult(
                    title=data.get("Heading", "Instant Answer"),
                    url=data.get("AbstractURL", ""),
                    snippet=data.get("Abstract", ""),
                    source="DuckDuckGo Instant Answer",
                    timestamp=datetime.now().isoformat()
                ))
            
            # Extract related topics
            for topic in data.get("RelatedTopics", [])[:max_results-1]:
                if isinstance(topic, dict) and topic.get("Text"):
                    results.append(WebSearchResult(
                        title=topic.get("FirstURL", "").split("/")[-1] if topic.get("FirstURL") else "Related Topic",
                        url=topic.get("FirstURL", ""),
                        snippet=topic.get("Text", ""),
                        source="DuckDuckGo Related Topics",
                        timestamp=datetime.now().isoformat()
                    ))
            
            # If no results from DuckDuckGo, try a simple web search simulation
            if not results:
                results = self._simulate_web_search(query, max_results)
            
            # Save to search history
            self.search_history.append({
                "query": query,
                "timestamp": datetime.now().isoformat(),
                "results_count": len(results)
            })
            
            logger.info(f"Web search completed. Found {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Web search failed: {e}")
            # Fallback to simulated results
            return self._simulate_web_search(query, max_results)
    
    def _simulate_web_search(self, query: str, max_results: int) -> List[WebSearchResult]:
        """Simulate web search when API is unavailable."""
        logger.info(f"Simulating web search for: {query}")
        
        # Create simulated results based on query
        simulated_results = []
        
        if "AI" in query or "artificial intelligence" in query.lower():
            simulated_results = [
                WebSearchResult(
                    title="Latest AI Developments",
                    url="https://example.com/ai-news",
                    snippet="Recent breakthroughs in artificial intelligence technology and applications.",
                    source="Simulated AI News",
                    timestamp=datetime.now().isoformat()
                ),
                WebSearchResult(
                    title="AI Industry Trends",
                    url="https://example.com/ai-trends",
                    snippet="Current trends in the artificial intelligence industry and market analysis.",
                    source="Simulated AI Trends",
                    timestamp=datetime.now().isoformat()
                )
            ]
        elif "OpenAI" in query:
            simulated_results = [
                WebSearchResult(
                    title="OpenAI Latest News",
                    url="https://example.com/openai-news",
                    snippet="Latest updates from OpenAI including new models and partnerships.",
                    source="Simulated OpenAI News",
                    timestamp=datetime.now().isoformat()
                ),
                WebSearchResult(
                    title="OpenAI Funding and Investments",
                    url="https://example.com/openai-funding",
                    snippet="Recent funding rounds and investment news from OpenAI.",
                    source="Simulated OpenAI Funding",
                    timestamp=datetime.now().isoformat()
                )
            ]
        else:
            simulated_results = [
                WebSearchResult(
                    title=f"Search Results for: {query}",
                    url=f"https://example.com/search?q={query}",
                    snippet=f"Web search results for '{query}' - this is a simulated response.",
                    source="Simulated Web Search",
                    timestamp=datetime.now().isoformat()
                )
            ]
        
        return simulated_results[:max_results]
    
    def get_search_history(self) -> List[Dict[str, Any]]:
        """Get search history."""
        return self.search_history
    
    def clear_search_history(self):
        """Clear search history."""
        self.search_history = []
        logger.info("Web search history cleared")

# Global web search tools instance
web_search_tools = WebSearchTools() 