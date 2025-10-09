"""
News data models for Tech News Digest.

Provides Pydantic models for:
- News articles
- News categories
- News sources
- News metadata
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl, field_validator


class NewsCategory(str, Enum):
    """News category types."""

    # IT/Tech categories (primary)
    AI_ML = "ai_ml"
    SOFTWARE_CLOUD = "software_cloud"
    STARTUP_FUNDING = "startup_funding"
    SECURITY = "security"
    HARDWARE = "hardware"
    MOBILE = "mobile"
    TECH_GENERAL = "tech_general"

    # Business categories (secondary)
    BUSINESS = "business"
    ECONOMICS = "economics"
    FINANCE = "finance"

    # Other
    BREAKING = "breaking"
    SCIENCE = "science"
    HEALTH = "health"
    WORLD = "world"
    UNKNOWN = "unknown"

    @property
    def weight(self) -> float:
        """Get category weight for news selection."""
        weights = {
            # IT/Tech categories (higher priority)
            self.AI_ML: 1.5,
            self.SOFTWARE_CLOUD: 1.3,
            self.STARTUP_FUNDING: 1.2,
            self.SECURITY: 1.2,
            self.HARDWARE: 1.1,
            self.MOBILE: 1.1,
            self.TECH_GENERAL: 1.0,
            # Business categories
            self.BUSINESS: 1.0,
            self.ECONOMICS: 0.9,
            self.FINANCE: 0.9,
            # Other
            self.BREAKING: 2.0,  # Highest priority
            self.SCIENCE: 0.8,
            self.HEALTH: 0.7,
            self.WORLD: 0.6,
            self.UNKNOWN: 0.5,
        }
        return weights.get(self, 1.0)

    @property
    def is_it_tech(self) -> bool:
        """Check if category is IT/Tech."""
        return self in [
            self.AI_ML,
            self.SOFTWARE_CLOUD,
            self.STARTUP_FUNDING,
            self.SECURITY,
            self.HARDWARE,
            self.MOBILE,
            self.TECH_GENERAL,
        ]

    @property
    def is_business(self) -> bool:
        """Check if category is Business."""
        return self in [self.BUSINESS, self.ECONOMICS, self.FINANCE]


class NewsSource(str, Enum):
    """News source types."""

    # IT/Tech sources (Korean)
    ETNEWS = "etnews"
    ZDNET_KR = "zdnet_kr"

    # IT/Tech sources (English)
    TECHCRUNCH = "techcrunch"
    THE_VERGE = "theverge"
    ARS_TECHNICA = "arstechnica"
    WIRED = "wired"
    MIT_TECH_REVIEW = "mittr"

    # Business sources
    REUTERS = "reuters"
    BLOOMBERG = "bloomberg"

    # General sources
    BBC = "bbc"
    CNN = "cnn"
    NYT = "nyt"
    GUARDIAN = "guardian"

    @property
    def display_name(self) -> str:
        """Get display name for the source."""
        names = {
            self.ETNEWS: "전자신문",
            self.ZDNET_KR: "ZDNet Korea",
            self.TECHCRUNCH: "TechCrunch",
            self.THE_VERGE: "The Verge",
            self.ARS_TECHNICA: "Ars Technica",
            self.WIRED: "Wired",
            self.MIT_TECH_REVIEW: "MIT Technology Review",
            self.REUTERS: "Reuters",
            self.BLOOMBERG: "Bloomberg",
            self.BBC: "BBC News",
            self.CNN: "CNN",
            self.NYT: "The New York Times",
            self.GUARDIAN: "The Guardian",
        }
        return names.get(self, self.value.upper())

    @property
    def rss_url(self) -> Optional[str]:
        """Get RSS feed URL for the source."""
        urls = {
            self.ETNEWS: "https://www.etnews.com/rss/S1N1.xml",
            self.ZDNET_KR: "https://www.zdnet.co.kr/rss/allNews.xml",
            self.TECHCRUNCH: "https://techcrunch.com/feed/",
            self.THE_VERGE: "https://www.theverge.com/rss/index.xml",
            self.ARS_TECHNICA: "https://feeds.arstechnica.com/arstechnica/index",
            self.WIRED: "https://www.wired.com/feed/rss",
            self.MIT_TECH_REVIEW: "https://www.technologyreview.com/feed/",
            self.REUTERS: "https://www.reutersagency.com/feed/?taxonomy=best-topics&post_type=best",
            self.BBC: "http://feeds.bbci.co.uk/news/rss.xml",
            self.CNN: "http://rss.cnn.com/rss/cnn_topstories.rss",
            self.GUARDIAN: "https://www.theguardian.com/world/rss",
        }
        return urls.get(self)

    @property
    def is_it_tech_source(self) -> bool:
        """Check if source is IT/Tech focused."""
        return self in [
            self.ETNEWS,
            self.ZDNET_KR,
            self.TECHCRUNCH,
            self.THE_VERGE,
            self.ARS_TECHNICA,
            self.WIRED,
            self.MIT_TECH_REVIEW,
        ]


class NewsImportance(str, Enum):
    """News importance level."""

    BREAKING = "breaking"  # Breaking news
    MAJOR = "major"  # Major news
    NORMAL = "normal"  # Normal news
    MINOR = "minor"  # Minor news

    @property
    def score(self) -> float:
        """Get importance score."""
        scores = {
            self.BREAKING: 10.0,
            self.MAJOR: 5.0,
            self.NORMAL: 1.0,
            self.MINOR: 0.5,
        }
        return scores.get(self, 1.0)


class News(BaseModel):
    """News article model."""

    # Basic info
    title: str = Field(..., description="Article title", min_length=1, max_length=500)
    url: HttpUrl = Field(..., description="Article URL")
    source: NewsSource = Field(..., description="News source")

    # Content
    summary: Optional[str] = Field(None, description="Article summary", max_length=2000)
    content: Optional[str] = Field(None, description="Full article content")

    # Metadata
    category: NewsCategory = Field(
        NewsCategory.UNKNOWN,
        description="Article category",
    )
    importance: NewsImportance = Field(
        NewsImportance.NORMAL,
        description="Article importance",
    )
    published_at: datetime = Field(..., description="Publication timestamp")
    author: Optional[str] = Field(None, description="Article author")

    # Media
    image_url: Optional[HttpUrl] = Field(None, description="Featured image URL")
    thumbnail_url: Optional[HttpUrl] = Field(None, description="Thumbnail URL")

    # Metrics (for selection algorithm)
    word_count: int = Field(0, ge=0, description="Article word count")
    reading_time: int = Field(0, ge=0, description="Estimated reading time (minutes)")

    # Internal
    crawled_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the article was crawled",
    )
    score: float = Field(0.0, ge=0.0, description="Selection score")

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate and clean title."""
        return v.strip()

    @field_validator("summary", "content")
    @classmethod
    def validate_text(cls, v: Optional[str]) -> Optional[str]:
        """Validate and clean text fields."""
        if v:
            return v.strip()
        return v

    def calculate_score(self) -> float:
        """
        Calculate selection score for this article.

        Score components:
        1. Importance score (0-10)
        2. Category weight (0.5-2.0)
        3. Recency bonus (0-2.0)
        4. Length bonus (0-1.0)

        Returns:
            Final selection score
        """
        # Base score from importance
        score = self.importance.score

        # Category weight
        score *= self.category.weight

        # Recency bonus (newer = better)
        age_hours = (datetime.utcnow() - self.published_at).total_seconds() / 3600
        if age_hours < 6:
            score *= 1.5  # Very recent
        elif age_hours < 24:
            score *= 1.2  # Recent
        elif age_hours > 72:
            score *= 0.5  # Old

        # Length bonus (optimal 300-800 words)
        if 300 <= self.word_count <= 800:
            score *= 1.2
        elif self.word_count < 100:
            score *= 0.7  # Too short

        self.score = score
        return score

    @property
    def is_recent(self) -> bool:
        """Check if article is recent (within 24 hours)."""
        age = datetime.utcnow() - self.published_at
        return age.total_seconds() < 86400  # 24 hours

    @property
    def is_breaking(self) -> bool:
        """Check if article is breaking news."""
        return self.importance == NewsImportance.BREAKING

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return self.model_dump(mode="json")

    class Config:
        """Pydantic config."""

        json_encoders = {
            datetime: lambda v: v.isoformat(),
            HttpUrl: lambda v: str(v),
        }


class NewsCollection(BaseModel):
    """Collection of news articles."""

    articles: list[News] = Field(default_factory=list, description="List of articles")
    total: int = Field(0, description="Total articles")
    source: Optional[NewsSource] = Field(None, description="Source filter")
    category: Optional[NewsCategory] = Field(None, description="Category filter")
    fetched_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When collection was fetched",
    )

    def add(self, article: News) -> None:
        """Add article to collection."""
        self.articles.append(article)
        self.total = len(self.articles)

    def filter_by_category(self, category: NewsCategory) -> "NewsCollection":
        """Filter articles by category."""
        filtered = [a for a in self.articles if a.category == category]
        return NewsCollection(
            articles=filtered,
            total=len(filtered),
            category=category,
            fetched_at=self.fetched_at,
        )

    def filter_by_source(self, source: NewsSource) -> "NewsCollection":
        """Filter articles by source."""
        filtered = [a for a in self.articles if a.source == source]
        return NewsCollection(
            articles=filtered,
            total=len(filtered),
            source=source,
            fetched_at=self.fetched_at,
        )

    def sort_by_score(self, descending: bool = True) -> None:
        """Sort articles by score."""
        self.articles.sort(key=lambda x: x.score, reverse=descending)

    def get_top(self, n: int) -> list[News]:
        """Get top N articles by score."""
        self.sort_by_score()
        return self.articles[:n]
