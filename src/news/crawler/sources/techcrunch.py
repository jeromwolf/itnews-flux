"""
TechCrunch news crawler.

TechCrunch is a leading technology media property, dedicated to obsessively
profiling startups, reviewing new Internet products, and breaking tech news.

RSS Feed: https://techcrunch.com/feed/
"""

import re
from typing import Optional

import feedparser

from src.news.crawler.base_crawler import BaseCrawler, ParseError
from src.news.models import News, NewsCategory, NewsImportance, NewsSource


class TechCrunchCrawler(BaseCrawler):
    """
    TechCrunch news crawler.

    Fetches and parses news from TechCrunch RSS feed.
    """

    def __init__(self):
        """Initialize TechCrunch crawler."""
        super().__init__(
            source=NewsSource.TECHCRUNCH,
            rss_url="https://techcrunch.com/feed/",
        )

    def parse_article(self, entry: feedparser.FeedParserDict) -> Optional[News]:
        """
        Parse article from TechCrunch RSS entry.

        Args:
            entry: RSS feed entry

        Returns:
            Parsed News article or None if parsing fails

        Raises:
            ParseError: If required fields are missing
        """
        try:
            # Extract basic fields
            title = entry.get("title", "").strip()
            url = entry.get("link", "").strip()

            if not title or not url:
                raise ParseError("Missing title or URL")

            # Extract summary
            summary = entry.get("summary", "")
            if summary:
                summary = self._extract_text(summary, max_length=500)

            # Extract content (if available)
            content = None
            if "content" in entry and entry.content:
                content = self._extract_text(entry.content[0].value, max_length=2000)

            # Extract author
            author = entry.get("author", None)
            if not author and "authors" in entry and entry.authors:
                author = entry.authors[0].get("name")

            # Extract image
            image_url = None
            thumbnail_url = None

            # Try media:content
            if "media_content" in entry and entry.media_content:
                image_url = entry.media_content[0].get("url")

            # Try media:thumbnail
            if "media_thumbnail" in entry and entry.media_thumbnail:
                thumbnail_url = entry.media_thumbnail[0].get("url")

            # Parse publish date
            published_at = self._parse_publish_date(entry)

            # Determine category
            category = self._get_category(entry, title, summary)

            # Determine importance
            importance = self._get_importance(entry, title)

            # Calculate word count
            text_for_count = content or summary or ""
            word_count = len(text_for_count.split())
            reading_time = self._estimate_reading_time(word_count)

            # Create News object
            news = News(
                title=title,
                url=url,
                source=self.source,
                summary=summary,
                content=content,
                category=category,
                importance=importance,
                published_at=published_at,
                author=author,
                image_url=image_url,
                thumbnail_url=thumbnail_url,
                word_count=word_count,
                reading_time=reading_time,
            )

            self.logger.debug(
                f"Parsed article: {title[:50]}...",
                extra={
                    "category": category.value,
                    "importance": importance.value,
                },
            )

            return news

        except ParseError:
            raise

        except Exception as e:
            raise ParseError(f"Failed to parse TechCrunch entry: {e}") from e

    def _get_category(
        self,
        entry: feedparser.FeedParserDict,
        title: str,
        summary: str,
    ) -> NewsCategory:
        """
        Determine article category based on TechCrunch-specific logic.

        Args:
            entry: RSS feed entry
            title: Article title
            summary: Article summary

        Returns:
            Article category
        """
        # Combine title and summary for analysis
        text = f"{title} {summary}".lower()

        # Check RSS categories/tags first
        if "tags" in entry:
            tags = [tag.get("term", "").lower() for tag in entry.tags]

            # AI/ML
            if any(tag in ["ai", "artificial-intelligence", "machine-learning", "ml"] for tag in tags):
                return NewsCategory.AI_ML

            # Startup/Funding
            if any(
                tag in ["startups", "venture-capital", "funding", "vc"] for tag in tags
            ):
                return NewsCategory.STARTUP_FUNDING

            # Security
            if any(tag in ["security", "privacy", "cybersecurity"] for tag in tags):
                return NewsCategory.SECURITY

            # Cloud/Software
            if any(tag in ["cloud", "saas", "software", "enterprise"] for tag in tags):
                return NewsCategory.SOFTWARE_CLOUD

        # Keyword-based detection
        # AI/ML keywords
        ai_keywords = [
            "artificial intelligence",
            "machine learning",
            "deep learning",
            "neural network",
            "chatgpt",
            "openai",
            "anthropic",
            "claude",
            "gpt",
            "llm",
            "ai model",
            "generative ai",
        ]
        if any(keyword in text for keyword in ai_keywords):
            return NewsCategory.AI_ML

        # Startup/Funding keywords
        startup_keywords = [
            "raises $",
            "raises funds",
            "series a",
            "series b",
            "series c",
            "seed round",
            "venture capital",
            "vc funding",
            "startup",
            "valuation",
            "unicorn",
        ]
        if any(keyword in text for keyword in startup_keywords):
            return NewsCategory.STARTUP_FUNDING

        # Security keywords
        security_keywords = [
            "security",
            "hack",
            "breach",
            "cybersecurity",
            "privacy",
            "encryption",
            "vulnerability",
            "malware",
            "ransomware",
        ]
        if any(keyword in text for keyword in security_keywords):
            return NewsCategory.SECURITY

        # Cloud/Software keywords
        cloud_keywords = [
            "cloud",
            "aws",
            "azure",
            "google cloud",
            "saas",
            "platform",
            "api",
            "software",
            "enterprise",
        ]
        if any(keyword in text for keyword in cloud_keywords):
            return NewsCategory.SOFTWARE_CLOUD

        # Mobile keywords
        mobile_keywords = [
            "iphone",
            "android",
            "ios",
            "mobile app",
            "smartphone",
            "tablet",
        ]
        if any(keyword in text for keyword in mobile_keywords):
            return NewsCategory.MOBILE

        # Hardware keywords
        hardware_keywords = [
            "chip",
            "processor",
            "hardware",
            "device",
            "gadget",
            "semiconductor",
        ]
        if any(keyword in text for keyword in hardware_keywords):
            return NewsCategory.HARDWARE

        # Default to tech general
        return NewsCategory.TECH_GENERAL

    def _get_importance(
        self,
        entry: feedparser.FeedParserDict,
        title: str,
    ) -> NewsImportance:
        """
        Determine article importance for TechCrunch.

        Args:
            entry: RSS feed entry
            title: Article title

        Returns:
            Article importance level
        """
        title_lower = title.lower()

        # Breaking news indicators
        breaking_keywords = [
            "breaking",
            "exclusive",
            "just in",
            "alert",
        ]
        if any(keyword in title_lower for keyword in breaking_keywords):
            return NewsImportance.BREAKING

        # Major news indicators (big companies, big funding)
        major_keywords = [
            "google",
            "apple",
            "microsoft",
            "amazon",
            "meta",
            "openai",
            "raises $100",
            "raises $500",
            "billion",
            "announces",
            "launches",
            "acquires",
            "acquisition",
        ]
        if any(keyword in title_lower for keyword in major_keywords):
            return NewsImportance.MAJOR

        # Check for large funding amounts
        funding_pattern = r"raises \$(\d+)([mb])"
        match = re.search(funding_pattern, title_lower)
        if match:
            amount = int(match.group(1))
            unit = match.group(2)

            # $50M+ or any billion
            if unit == "b" or (unit == "m" and amount >= 50):
                return NewsImportance.MAJOR

        return NewsImportance.NORMAL


# Convenience function
def create_techcrunch_crawler() -> TechCrunchCrawler:
    """
    Create TechCrunch crawler instance.

    Returns:
        TechCrunch crawler

    Example:
        >>> crawler = create_techcrunch_crawler()
        >>> news = crawler.fetch_news(limit=10)
        >>> print(f"Fetched {news.total} articles")
    """
    return TechCrunchCrawler()
