"""
Web search tools.

This module provides functionality to perform web searches using various search APIs:
- DuckDuckGo (free, no API key needed)
- Brave Search API (requires API key)
- Tavily API (requires API key)
"""

import logging
import os
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


def search_web(query: str, max_results: int = 5, search_engine: str = "duckduckgo") -> Dict[str, Any]:
    """
    Perform a web search.

    Args:
        query: Search query
        max_results: Maximum number of results to return
        search_engine: Search engine to use ('duckduckgo', 'brave', 'tavily')

    Returns:
        Dictionary with keys:
        - success: bool
        - query: str
        - results: List[Dict] with 'title', 'url', 'snippet'
        - error: str (if failed)
    """
    try:
        if search_engine.lower() == "duckduckgo":
            return _search_duckduckgo(query, max_results)
        elif search_engine.lower() == "brave":
            return _search_brave(query, max_results)
        elif search_engine.lower() == "tavily":
            return _search_tavily(query, max_results)
        else:
            return {
                "success": False,
                "error": f"Unsupported search engine: {search_engine}"
            }
    except Exception as e:
        logger.error(f"Search error: {e}")
        return {
            "success": False,
            "query": query,
            "error": str(e)
        }


def _search_duckduckgo(query: str, max_results: int) -> Dict[str, Any]:
    """Search using DuckDuckGo (free, no API key needed)."""
    try:
        from duckduckgo_search import DDGS
    except ImportError:
        raise ImportError(
            "Please install duckduckgo-search: pip install duckduckgo-search"
        )

    try:
        with DDGS() as ddgs:
            results = []
            for result in ddgs.text(query, max_results=max_results):
                results.append({
                    "title": result.get("title", ""),
                    "url": result.get("href", ""),
                    "snippet": result.get("body", ""),
                })

            return {
                "success": True,
                "query": query,
                "results": results,
                "search_engine": "duckduckgo"
            }
    except Exception as e:
        logger.error(f"DuckDuckGo search error: {e}")
        return {
            "success": False,
            "query": query,
            "error": str(e)
        }


def _search_brave(query: str, max_results: int) -> Dict[str, Any]:
    """Search using Brave Search API (requires API key)."""
    try:
        import requests
    except ImportError:
        raise ImportError("Please install requests: pip install requests")

    api_key = os.getenv("BRAVE_API_KEY")
    if not api_key:
        return {
            "success": False,
            "query": query,
            "error": "BRAVE_API_KEY not set in environment variables"
        }

    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": api_key
    }

    params = {
        "q": query,
        "count": max_results
    }

    try:
        response = requests.get(
            "https://api.search.brave.com/res/v1/web/search",
            headers=headers,
            params=params,
            timeout=10
        )
        response.raise_for_status()

        data = response.json()
        results = []

        for item in data.get("web", {}).get("results", []):
            results.append({
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "snippet": item.get("description", ""),
            })

        return {
            "success": True,
            "query": query,
            "results": results,
            "search_engine": "brave"
        }

    except Exception as e:
        logger.error(f"Brave search error: {e}")
        return {
            "success": False,
            "query": query,
            "error": str(e)
        }


def _search_tavily(query: str, max_results: int) -> Dict[str, Any]:
    """Search using Tavily API (requires API key)."""
    try:
        from tavily import TavilyClient
    except ImportError:
        raise ImportError("Please install tavily-python: pip install tavily-python")

    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return {
            "success": False,
            "query": query,
            "error": "TAVILY_API_KEY not set in environment variables"
        }

    try:
        client = TavilyClient(api_key=api_key)
        response = client.search(query, max_results=max_results)

        results = []
        for item in response.get("results", []):
            results.append({
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "snippet": item.get("content", ""),
            })

        return {
            "success": True,
            "query": query,
            "results": results,
            "search_engine": "tavily"
        }

    except Exception as e:
        logger.error(f"Tavily search error: {e}")
        return {
            "success": False,
            "query": query,
            "error": str(e)
        }


def format_search_results(search_result: Dict[str, Any]) -> str:
    """
    Format search results into a readable string.

    Args:
        search_result: Search result dictionary

    Returns:
        Formatted string
    """
    if not search_result.get("success"):
        return f"Search failed: {search_result.get('error', 'Unknown error')}"

    query = search_result["query"]
    results = search_result["results"]
    engine = search_result.get("search_engine", "unknown")

    if not results:
        return f"No results found for: {query}"

    lines = [f"**Search results for: {query}** (via {engine})\n"]

    for i, result in enumerate(results, 1):
        lines.append(f"{i}. **{result['title']}**")
        lines.append(f"   {result['url']}")
        if result['snippet']:
            snippet = result['snippet']
            if len(snippet) > 200:
                snippet = snippet[:200] + "..."
            lines.append(f"   {snippet}")
        lines.append("")

    return '\n'.join(lines)
