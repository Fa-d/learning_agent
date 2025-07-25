"""
Enhanced web search service using LangChain tools with DuckDuckGo
"""
import logging
from typing import List, Optional
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.tools import Tool

logger = logging.getLogger(__name__)


class LangChainWebSearchService:
    """Enhanced web search service using LangChain with DuckDuckGo and website scraping"""
    
    def __init__(self):
        self.search_tool = DuckDuckGoSearchRun()
        
    def search(self, query: str, max_results: int = 5) -> str:
        """Perform web search and return formatted results"""
        try:
            logger.info(f"Performing enhanced web search for: {query}")
            
            # Perform search using DuckDuckGo tool
            search_results = self.search_tool.run(query)
            
            if not search_results:
                logger.warning(f"No search results found for query: {query}")
                return f"No search results found for '{query}'"
            
            return f"Search results for '{query}':\n{search_results}"
            
        except Exception as e:
            logger.error(f"Web search failed for query '{query}': {e}")
            return f"Web search failed for '{query}': {str(e)}"
    
    def _scrape_website(self, url: str) -> str:
        """Scrape content from a website URL using WebBaseLoader"""
        try:
            logger.info(f"Scraping website: {url}")
            
            # Use WebBaseLoader to scrape the website
            loader = WebBaseLoader(url)
            docs = loader.load()
            
            if docs:
                # Combine content from all documents
                content = "\n".join([doc.page_content for doc in docs])
                # Truncate if too long
                if len(content) > 2000:
                    content = content[:2000] + "...[truncated]"
                return content
            else:
                return f"No content found at {url}"
                
        except Exception as e:
            logger.error(f"Failed to scrape website {url}: {e}")
            return f"Failed to scrape {url}: {str(e)}"
    
    def get_tools(self) -> List[Tool]:
        """Get LangChain tools for agent use"""
        return [
            Tool(
                name="duckduckgo_search",
                description="Search for information using DuckDuckGo. Use this when you need current information about a topic. Input should be a search query string.",
                func=self.search
            ),
            Tool(
                name="scrape_website",
                description="Scrape content from a website URL. Use this to get detailed information from specific web pages. Input should be a valid URL.",
                func=self._scrape_website
            )
        ]


# Global web search service instance
web_search = LangChainWebSearchService()
