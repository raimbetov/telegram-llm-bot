"""
Web scraping and URL fetching tools.

This module provides functionality to:
- Fetch web page content
- Extract text and metadata from HTML
- Handle JavaScript-heavy sites with Playwright (optional)
"""

import logging
import requests
from typing import Dict, Any, Optional
from urllib.parse import urlparse
import re

logger = logging.getLogger(__name__)


def fetch_url(url: str, use_playwright: bool = False, timeout: int = 10) -> Dict[str, Any]:
    """
    Fetch content from a URL.

    Args:
        url: URL to fetch
        use_playwright: Whether to use Playwright for JavaScript-heavy sites
        timeout: Request timeout in seconds

    Returns:
        Dictionary with keys:
        - success: bool
        - url: str (original URL)
        - title: str (page title)
        - content: str (extracted text content)
        - error: str (error message if failed)
    """
    try:
        # Validate URL
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return {
                "success": False,
                "url": url,
                "error": "Invalid URL format"
            }

        if use_playwright:
            return _fetch_with_playwright(url, timeout)
        else:
            return _fetch_with_requests(url, timeout)

    except Exception as e:
        logger.error(f"Error fetching URL {url}: {e}")
        return {
            "success": False,
            "url": url,
            "error": str(e)
        }


def _fetch_with_requests(url: str, timeout: int) -> Dict[str, Any]:
    """Fetch URL using requests + BeautifulSoup."""
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        raise ImportError("Please install beautifulsoup4: pip install beautifulsoup4")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    response = requests.get(url, headers=headers, timeout=timeout)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, 'html.parser')

    # Remove script and style elements
    for script in soup(['script', 'style', 'nav', 'footer', 'header']):
        script.decompose()

    # Extract title
    title = soup.title.string if soup.title else "No title"

    # Extract main content
    # Try to find main content area
    main_content = (
        soup.find('main') or
        soup.find('article') or
        soup.find('div', {'class': re.compile(r'content|article|post', re.I)}) or
        soup.body
    )

    if main_content:
        text = main_content.get_text(separator='\n', strip=True)
    else:
        text = soup.get_text(separator='\n', strip=True)

    # Clean up excessive whitespace
    text = re.sub(r'\n\s*\n', '\n\n', text)
    text = '\n'.join(line.strip() for line in text.split('\n'))

    # Limit content length (approximately 8000 chars to avoid token limits)
    if len(text) > 8000:
        text = text[:8000] + "\n\n[Content truncated...]"

    return {
        "success": True,
        "url": url,
        "title": title.strip(),
        "content": text,
    }


def _fetch_with_playwright(url: str, timeout: int) -> Dict[str, Any]:
    """Fetch URL using Playwright for JavaScript-heavy sites."""
    try:
        from playwright.sync_api import sync_playwright
        from bs4 import BeautifulSoup
    except ImportError:
        raise ImportError(
            "Please install playwright: pip install playwright && playwright install"
        )

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            page.goto(url, timeout=timeout * 1000, wait_until='networkidle')

            # Get page content
            html = page.content()
            title = page.title()

            soup = BeautifulSoup(html, 'html.parser')

            # Remove script and style elements
            for script in soup(['script', 'style', 'nav', 'footer', 'header']):
                script.decompose()

            # Extract main content
            main_content = (
                soup.find('main') or
                soup.find('article') or
                soup.find('div', {'class': re.compile(r'content|article|post', re.I)}) or
                soup.body
            )

            if main_content:
                text = main_content.get_text(separator='\n', strip=True)
            else:
                text = soup.get_text(separator='\n', strip=True)

            # Clean up
            text = re.sub(r'\n\s*\n', '\n\n', text)
            text = '\n'.join(line.strip() for line in text.split('\n'))

            if len(text) > 8000:
                text = text[:8000] + "\n\n[Content truncated...]"

            return {
                "success": True,
                "url": url,
                "title": title,
                "content": text,
            }

        finally:
            browser.close()


def extract_urls(text: str) -> list:
    """
    Extract URLs from text.

    Args:
        text: Text to search for URLs

    Returns:
        List of URLs found in the text
    """
    url_pattern = re.compile(
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    )
    return url_pattern.findall(text)
