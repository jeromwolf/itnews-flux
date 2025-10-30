"""
URL content extractor for custom news articles.

Extracts title, summary, and content from any URL using:
- BeautifulSoup for HTML parsing
- Newspaper3k for article extraction (fallback)
- Basic heuristics for content detection
"""

import re
from datetime import datetime, timezone
from typing import Optional

import requests
from bs4 import BeautifulSoup

from src.core.logging import get_logger

logger = get_logger(__name__)


class URLExtractor:
    """Extract article content from URL."""

    def __init__(self, timeout: int = 10):
        """
        Initialize URL extractor.

        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }

    def extract(self, url: str) -> dict:
        """
        Extract article content from URL.

        Args:
            url: Article URL

        Returns:
            Dictionary with title, summary, content, published_at

        Raises:
            Exception: If extraction fails
        """
        logger.info(f"Extracting content from URL: {url}")

        try:
            # Fetch page
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            response.encoding = response.apparent_encoding

            # Parse HTML
            soup = BeautifulSoup(response.text, "html.parser")

            # Extract metadata
            title = self._extract_title(soup)
            summary = self._extract_summary(soup)
            content = self._extract_content(soup)
            published_at = self._extract_date(soup)

            logger.info(f"Extracted: title={title[:50]}..., content={len(content)} chars")

            return {
                "title": title,
                "summary": summary or content[:500],  # Use content as fallback
                "content": content,
                "published_at": published_at or datetime.now(timezone.utc),
                "url": url,
            }

        except requests.RequestException as e:
            logger.error(f"Failed to fetch URL: {e}")
            raise Exception(f"Failed to fetch URL: {e}")
        except Exception as e:
            logger.error(f"Failed to extract content: {e}")
            raise Exception(f"Failed to extract content: {e}")

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract article title."""
        # Try Open Graph title
        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            return og_title["content"].strip()

        # Try Twitter title
        twitter_title = soup.find("meta", attrs={"name": "twitter:title"})
        if twitter_title and twitter_title.get("content"):
            return twitter_title["content"].strip()

        # Try <title> tag
        if soup.title and soup.title.string:
            return soup.title.string.strip()

        # Try <h1> tag
        h1 = soup.find("h1")
        if h1:
            return h1.get_text().strip()

        return "Untitled Article"

    def _extract_summary(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract article summary/description."""
        # Try Open Graph description
        og_desc = soup.find("meta", property="og:description")
        if og_desc and og_desc.get("content"):
            desc = og_desc["content"].strip()
            if len(desc) >= 20:
                return desc

        # Try meta description
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc and meta_desc.get("content"):
            desc = meta_desc["content"].strip()
            if len(desc) >= 20:
                return desc

        return None

    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Extract article main content."""
        # Remove unwanted elements
        for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
            element.decompose()

        # Try common article selectors
        selectors = [
            "article",
            ".article-content",
            ".post-content",
            ".entry-content",
            ".content",
            "main",
        ]

        for selector in selectors:
            article = soup.select_one(selector)
            if article:
                # Get all paragraphs
                paragraphs = article.find_all("p")
                if paragraphs:
                    text = "\n\n".join(p.get_text().strip() for p in paragraphs if p.get_text().strip())
                    if len(text) > 100:
                        return text

        # Fallback: get all paragraphs
        paragraphs = soup.find_all("p")
        if paragraphs:
            text = "\n\n".join(p.get_text().strip() for p in paragraphs if p.get_text().strip())
            return text if text else "No content extracted"

        return "No content extracted"

    def _extract_date(self, soup: BeautifulSoup) -> Optional[datetime]:
        """Extract publication date."""
        # Try Open Graph article:published_time
        og_date = soup.find("meta", property="article:published_time")
        if og_date and og_date.get("content"):
            try:
                return datetime.fromisoformat(og_date["content"].replace("Z", "+00:00"))
            except:
                pass

        # Try time tag
        time_tag = soup.find("time")
        if time_tag and time_tag.get("datetime"):
            try:
                return datetime.fromisoformat(time_tag["datetime"].replace("Z", "+00:00"))
            except:
                pass

        return None
