"""
The Verge news crawler.

The Verge is a technology news and media network covering the intersection
of technology, science, art, and culture.

RSS Feed: https://www.theverge.com/rss/index.xml
"""

from typing import Optional

import feedparser

from src.news.crawler.base_crawler import BaseCrawler, ParseError
from src.news.models import News, NewsCategory, NewsImportance, NewsSource


class TheVergeCrawler(BaseCrawler):
    """
    The Verge news crawler.

    Fetches and parses news from The Verge RSS feed.
    """

    def __init__(self):
        """Initialize The Verge crawler."""
        super().__init__(
            source=NewsSource.THE_VERGE,
            rss_url="https://www.theverge.com/rss/index.xml",
        )

    def parse_article(self, entry: feedparser.FeedParserDict) -> Optional[News]:
        """
        Parse article from The Verge RSS entry.

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
            raise ParseError(f"Failed to parse The Verge entry: {e}") from e

    def _get_category(
        self,
        entry: feedparser.FeedParserDict,
        title: str,
        summary: str,
    ) -> NewsCategory:
        """
        Determine article category based on The Verge-specific logic.

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
            if any(tag in ["ai", "artificial intelligence", "machine learning"] for tag in tags):
                return NewsCategory.AI_ML

            # Mobile
            if any(tag in ["mobile", "smartphone", "iphone", "android"] for tag in tags):
                return NewsCategory.MOBILE

            # Hardware
            if any(tag in ["hardware", "gadgets", "devices"] for tag in tags):
                return NewsCategory.HARDWARE

            # Software/Cloud
            if any(tag in ["software", "apps", "cloud", "internet"] for tag in tags):
                return NewsCategory.SOFTWARE_CLOUD

            # Security
            if any(tag in ["security", "privacy", "cybersecurity"] for tag in tags):
                return NewsCategory.SECURITY

        # Keyword-based detection
        # AI/ML keywords
        ai_keywords = [
            "artificial intelligence",
            "machine learning",
            "ai",
            "chatgpt",
            "openai",
            "claude",
            "llm",
            "neural network",
            "generative ai",
        ]
        if any(keyword in text for keyword in ai_keywords):
            return NewsCategory.AI_ML

        # Mobile keywords
        mobile_keywords = [
            "iphone",
            "android",
            "ios",
            "smartphone",
            "mobile",
            "pixel",
            "galaxy",
            "phone",
        ]
        if any(keyword in text for keyword in mobile_keywords):
            return NewsCategory.MOBILE

        # Hardware keywords
        hardware_keywords = [
            "laptop",
            "tablet",
            "gadget",
            "device",
            "hardware",
            "computer",
            "chip",
            "processor",
            "gaming pc",
            "console",
        ]
        if any(keyword in text for keyword in hardware_keywords):
            return NewsCategory.HARDWARE

        # Security keywords
        security_keywords = [
            "security",
            "privacy",
            "hack",
            "breach",
            "vulnerability",
            "encryption",
            "cybersecurity",
        ]
        if any(keyword in text for keyword in security_keywords):
            return NewsCategory.SECURITY

        # Cloud/Software keywords
        cloud_keywords = [
            "cloud",
            "app",
            "software",
            "platform",
            "service",
            "google",
            "microsoft",
            "amazon web services",
        ]
        if any(keyword in text for keyword in cloud_keywords):
            return NewsCategory.SOFTWARE_CLOUD

        # Default to tech general
        return NewsCategory.TECH_GENERAL

    def _get_importance(
        self,
        entry: feedparser.FeedParserDict,
        title: str,
    ) -> NewsImportance:
        """
        Determine article importance for The Verge.

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
            "just announced",
            "live",
        ]
        if any(keyword in title_lower for keyword in breaking_keywords):
            return NewsImportance.BREAKING

        # Major news indicators (big companies, major product launches)
        major_keywords = [
            "apple",
            "google",
            "microsoft",
            "amazon",
            "meta",
            "samsung",
            "announced",
            "unveils",
            "launches",
            "released",
            "confirms",
        ]
        if any(keyword in title_lower for keyword in major_keywords):
            return NewsImportance.MAJOR

        # Reviews and analysis are typically normal
        if any(word in title_lower for word in ["review", "hands-on", "opinion"]):
            return NewsImportance.NORMAL

        return NewsImportance.NORMAL


# Convenience function
def create_theverge_crawler() -> TheVergeCrawler:
    """
    Create The Verge crawler instance.

    Returns:
        The Verge crawler

    Example:
        >>> crawler = create_theverge_crawler()
        >>> news = crawler.fetch_news(limit=10)
        >>> print(f"Fetched {news.total} articles")
    """
    return TheVergeCrawler()
