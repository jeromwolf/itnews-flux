"""News management API endpoints."""

from datetime import datetime

from fastapi import APIRouter, HTTPException

from ...core.logging import get_logger
from ...news.crawler import create_news_crawler
from ...news.models import News
from ..schemas.news import NewsListResponse, NewsResponse, NewsSelectionRequest

logger = get_logger(__name__)
router = APIRouter(prefix="/news", tags=["news"])

# In-memory cache for news (in production, use Redis or database)
_news_cache: dict[str, News] = {}
_cache_timestamp: datetime | None = None


@router.get("/", response_model=NewsListResponse)
async def get_news(
    sources: str = "techcrunch,theverge",
    max_age_hours: int = 24,
    limit: int = 10,
    force_refresh: bool = False,
) -> NewsListResponse:
    """
    Fetch latest tech news from configured sources.

    Args:
        sources: Comma-separated list of sources (e.g., "techcrunch,theverge")
        max_age_hours: Maximum age of news in hours
        limit: Maximum number of news articles to return
        force_refresh: Force refresh cache

    Returns:
        List of news articles with metadata
    """
    global _news_cache, _cache_timestamp

    # Check cache validity (5 minutes)
    cache_valid = (
        _cache_timestamp is not None
        and (datetime.now() - _cache_timestamp).total_seconds() < 300
        and not force_refresh
    )

    if not cache_valid:
        logger.info(f"Fetching news from sources: {sources}")
        _news_cache.clear()

        source_list = [s.strip() for s in sources.split(",")]
        all_news: list[News] = []

        for source in source_list:
            try:
                crawler = create_news_crawler(source)
                news_collection = crawler.fetch_news(limit=limit, max_age_hours=max_age_hours)
                all_news.extend(news_collection.articles)
                logger.info(f"Fetched {news_collection.total} articles from {source}")
            except ValueError as e:
                logger.warning(f"Unknown source '{source}': {e}")
                continue
            except Exception as e:
                logger.error(f"Error crawling {source}: {e}")
                continue

        # Sort by score (descending)
        all_news.sort(key=lambda x: x.score, reverse=True)

        # Update cache
        for news in all_news[:limit]:
            # Generate unique ID
            news_id = f"{news.source.value}-{news.url.split('/')[-1][:20]}"
            _news_cache[news_id] = news

        _cache_timestamp = datetime.now()

    # Convert to response format
    news_responses = [
        NewsResponse(
            id=f"{news.source.value}-{news.url.split('/')[-1][:20]}",
            title=news.title,
            summary=news.summary,
            url=str(news.url),
            published_at=news.published_at,
            source=news.source.value,
            category=news.category.value,
            score=news.score,
            image_url=None,  # Image URLs not currently extracted
        )
        for news in list(_news_cache.values())[:limit]
    ]

    return NewsListResponse(
        total=len(news_responses), news=news_responses, fetched_at=_cache_timestamp or datetime.now()
    )


@router.get("/{news_id}", response_model=NewsResponse)
async def get_news_by_id(news_id: str) -> NewsResponse:
    """
    Get a specific news article by ID.

    Args:
        news_id: Unique news article ID

    Returns:
        News article details
    """
    if news_id not in _news_cache:
        raise HTTPException(status_code=404, detail=f"News article '{news_id}' not found")

    news = _news_cache[news_id]
    return NewsResponse(
        id=news_id,
        title=news.title,
        summary=news.summary,
        url=str(news.url),
        published_at=news.published_at,
        source=news.source.value,
        category=news.category.value,
        score=news.score,
        image_url=None,
    )


@router.post("/select")
async def select_news(request: NewsSelectionRequest) -> dict:
    """
    Select specific news articles for video generation.

    Args:
        request: List of news IDs to select

    Returns:
        Confirmation with selected news
    """
    selected: list[News] = []
    missing: list[str] = []

    for news_id in request.news_ids:
        if news_id in _news_cache:
            selected.append(_news_cache[news_id])
        else:
            missing.append(news_id)

    if missing:
        raise HTTPException(
            status_code=404, detail=f"News articles not found: {', '.join(missing)}"
        )

    logger.info(f"Selected {len(selected)} news articles for video generation")

    return {
        "status": "success",
        "selected_count": len(selected),
        "news_ids": request.news_ids,
        "titles": [news.title for news in selected],
    }


def get_cached_news(news_id: str) -> News | None:
    """Get news from cache (for internal use)."""
    return _news_cache.get(news_id)
