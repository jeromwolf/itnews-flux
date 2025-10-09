"""
Base crawler class for news sources.

Provides abstract base class for all news crawlers with:
- RSS feed parsing
- Rate limiting
- Error handling
- Caching
- Logging
"""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Optional
from urllib.parse import urlparse

import feedparser
import requests
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential

from src.core.config import get_settings
from src.core.logging import get_logger, log_execution_time
from src.news.models import News, NewsCategory, NewsCollection, NewsImportance, NewsSource

# Get settings and logger
settings = get_settings()
logger = get_logger(__name__)


class CrawlerError(Exception):
    """Base exception for crawler errors."""

    pass


class FetchError(CrawlerError):
    """Error fetching data from source."""

    pass


class ParseError(CrawlerError):
    """Error parsing data."""

    pass


class BaseCrawler(ABC):
    """
    Abstract base class for news crawlers.

    All crawlers must implement:
    - parse_article(): Parse individual article from feed entry
    - _get_category(): Determine article category
    """

    def __init__(
        self,
        source: NewsSource,
        rss_url: Optional[str] = None,
    ):
        """
        Initialize crawler.

        Args:
            source: News source type
            rss_url: RSS feed URL (uses default if not provided)
        """
        self.source = source
        self.rss_url = rss_url or source.rss_url
        self.logger = get_logger(f"{__name__}.{source.value}")

        if not self.rss_url:
            raise ValueError(f"No RSS URL available for {source.value}")

        self.session = self._create_session()
        self._cache: dict[str, News] = {}

    def _create_session(self) -> requests.Session:
        """Create HTTP session with timeout and user agent."""
        session = requests.Session()
        session.headers.update(
            {
                "User-Agent": settings.crawler.user_agent,
                "Accept": "application/rss+xml, application/xml, text/xml",
            }
        )
        return session

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True,
    )
    def _fetch_rss_feed(self) -> feedparser.FeedParserDict:
        """
        Fetch RSS feed with retry logic.

        Returns:
            Parsed RSS feed

        Raises:
            FetchError: If fetching fails
        """
        try:
            self.logger.debug(f"Fetching RSS feed: {self.rss_url}")

            response = self.session.get(
                self.rss_url,
                timeout=settings.crawler.timeout,
            )
            response.raise_for_status()

            feed = feedparser.parse(response.content)

            if feed.bozo:
                self.logger.warning(
                    f"RSS feed parsing warning: {feed.bozo_exception}",
                )

            self.logger.info(
                f"Fetched {len(feed.entries)} entries from {self.source.display_name}"
            )

            return feed

        except requests.RequestException as e:
            self.logger.error(f"Failed to fetch RSS feed: {e}", exc_info=True)
            raise FetchError(f"Failed to fetch from {self.source.value}") from e

    @abstractmethod
    def parse_article(self, entry: feedparser.FeedParserDict) -> Optional[News]:
        """
        Parse article from feed entry.

        Must be implemented by subclasses.

        Args:
            entry: RSS feed entry

        Returns:
            Parsed News article or None if parsing fails
        """
        pass

    @abstractmethod
    def _get_category(
        self,
        entry: feedparser.FeedParserDict,
        title: str,
        summary: str,
    ) -> NewsCategory:
        """
        Determine article category.

        Must be implemented by subclasses based on source-specific logic.

        Args:
            entry: RSS feed entry
            title: Article title
            summary: Article summary

        Returns:
            Article category
        """
        pass

    def _get_importance(
        self,
        entry: feedparser.FeedParserDict,
        title: str,
    ) -> NewsImportance:
        """
        Determine article importance.

        Can be overridden by subclasses.

        Args:
            entry: RSS feed entry
            title: Article title

        Returns:
            Article importance level
        """
        # Check for breaking news keywords
        breaking_keywords = ["breaking", "urgent", "alert", "live"]
        title_lower = title.lower()

        if any(keyword in title_lower for keyword in breaking_keywords):
            return NewsImportance.BREAKING

        # Check for major news indicators
        major_keywords = ["announces", "launches", "reveals", "reports"]
        if any(keyword in title_lower for keyword in major_keywords):
            return NewsImportance.MAJOR

        return NewsImportance.NORMAL

    def _parse_publish_date(self, entry: feedparser.FeedParserDict) -> datetime:
        """
        Parse publication date from entry.

        Args:
            entry: RSS feed entry

        Returns:
            Publication datetime (UTC)
        """
        # Try different date fields
        date_fields = ["published_parsed", "updated_parsed", "created_parsed"]

        for field in date_fields:
            if hasattr(entry, field) and getattr(entry, field):
                time_struct = getattr(entry, field)
                return datetime(*time_struct[:6])

        # Fallback to current time
        self.logger.warning(f"No date found for entry: {entry.get('title', 'Unknown')}")
        return datetime.utcnow()

    def _extract_text(self, html: str, max_length: int = 2000) -> str:
        """
        Extract clean text from HTML.

        Args:
            html: HTML content
            max_length: Maximum text length

        Returns:
            Clean text
        """
        soup = BeautifulSoup(html, "lxml")

        # Remove script and style tags
        for tag in soup(["script", "style", "nav", "footer", "aside"]):
            tag.decompose()

        # Get text
        text = soup.get_text(separator=" ", strip=True)

        # Clean whitespace
        text = " ".join(text.split())

        return text[:max_length]

    def _estimate_reading_time(self, word_count: int) -> int:
        """
        Estimate reading time in minutes.

        Assumes average reading speed of 200 words per minute.

        Args:
            word_count: Number of words

        Returns:
            Reading time in minutes
        """
        return max(1, word_count // 200)

    @log_execution_time(logger)
    def fetch_news(
        self,
        limit: Optional[int] = None,
        min_age_hours: int = 0,
        max_age_hours: int = 24,
    ) -> NewsCollection:
        """
        Fetch news articles from source.

        Args:
            limit: Maximum number of articles to fetch (None = all)
            min_age_hours: Minimum article age in hours
            max_age_hours: Maximum article age in hours

        Returns:
            Collection of news articles

        Raises:
            CrawlerError: If fetching or parsing fails
        """
        self.logger.info(
            f"Starting news fetch from {self.source.display_name}",
            extra={"source": self.source.value, "limit": limit},
        )

        try:
            # Fetch RSS feed
            feed = self._fetch_rss_feed()

            # Parse articles
            collection = NewsCollection(source=self.source)
            now = datetime.utcnow()
            min_age = timedelta(hours=min_age_hours)
            max_age = timedelta(hours=max_age_hours)

            for entry in feed.entries:
                # Check limit
                if limit and collection.total >= limit:
                    break

                try:
                    # Parse article
                    article = self.parse_article(entry)

                    if not article:
                        continue

                    # Check age
                    age = now - article.published_at
                    if age < min_age or age > max_age:
                        self.logger.debug(
                            f"Skipping article (age {age.total_seconds() / 3600:.1f}h): {article.title}"
                        )
                        continue

                    # Calculate score
                    article.calculate_score()

                    # Add to collection
                    collection.add(article)

                    # Cache
                    self._cache[str(article.url)] = article

                except ParseError as e:
                    self.logger.warning(f"Failed to parse entry: {e}")
                    continue

                except Exception as e:
                    self.logger.error(f"Unexpected error parsing entry: {e}", exc_info=True)
                    continue

            self.logger.info(
                f"Fetched {collection.total} articles from {self.source.display_name}",
                extra={"source": self.source.value, "count": collection.total},
            )

            return collection

        except FetchError as e:
            self.logger.error(f"Failed to fetch news: {e}")
            raise

        except Exception as e:
            self.logger.critical(f"Unexpected error in fetch_news: {e}", exc_info=True)
            raise CrawlerError(f"Failed to fetch news from {self.source.value}") from e

    def get_cached_article(self, url: str) -> Optional[News]:
        """Get cached article by URL."""
        return self._cache.get(url)

    def clear_cache(self) -> None:
        """Clear article cache."""
        self._cache.clear()
        self.logger.debug("Article cache cleared")

    def __repr__(self) -> str:
        """String representation."""
        return f"{self.__class__.__name__}(source={self.source.value})"
