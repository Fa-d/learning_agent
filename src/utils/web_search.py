"""
Web search utilities for content enrichment
"""
import logging
from typing import Optional
import requests
from bs4 import BeautifulSoup

from ..core.config import settings

logger = logging.getLogger(__name__)


class WebSearchService:
    """Service for web searching to enrich content generation"""
    
    def __init__(self):
        self.enabled = settings.enable_web_search
        self.max_results = settings.search_max_results
        self.timeout = settings.search_timeout
    
    def search(self, query: str) -> str:
        """
        Search the web for additional context
        
        Args:
            query: Search query string
            
        Returns:
            String containing search results or fallback message
        """
        if not self.enabled:
            return self._get_fallback_message(query)
            
        try:
            return self._search_duckduckgo(query)
        except Exception as e:
            logger.warning(f"Web search failed for query '{query}': {e}")
            return self._get_fallback_message(query)
    
    def _search_duckduckgo(self, query: str) -> str:
        """Search using DuckDuckGo lite interface"""
        search_url = "https://duckduckgo.com/lite/"
        
        params = {
            'q': query,
            'kl': 'us-en'
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(
            search_url, 
            params=params, 
            headers=headers, 
            timeout=self.timeout
        )
        
        if response.status_code != 200:
            raise Exception(f"Search request failed with status {response.status_code}")
        
        soup = BeautifulSoup(response.content, 'html.parser')
        text_content = soup.get_text()
        
        # Clean and limit the content
        lines = [line.strip() for line in text_content.split('\n') if line.strip()]
        relevant_lines = [line for line in lines if query.lower() in line.lower()][:self.max_results]
        
        if relevant_lines:
            return f"Web search context for '{query}':\n" + "\n".join(relevant_lines)
        else:
            return self._get_fallback_message(query)
    
    def _get_fallback_message(self, query: str) -> str:
        """Get fallback message when search is unavailable"""
        return f"Limited search results found for '{query}'. Generating content based on internal knowledge."


# Global instance
web_search = WebSearchService()
