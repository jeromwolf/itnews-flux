"""News management API endpoints."""

from datetime import datetime

from fastapi import APIRouter, HTTPException

from ...core.ai_services import create_translation_service
from ...core.logging import get_logger
from ...news.crawler import create_news_crawler
from ...news.models import News, NewsCategory, NewsImportance, NewsSource
from ..schemas.news import ManualNewsRequest, NewsListResponse, NewsResponse, NewsSelectionRequest

logger = get_logger(__name__)
router = APIRouter(prefix="/news", tags=["news"])

# Translation service (lazy initialization)
_translator = None


def get_translator():
    """Get or create translation service instance."""
    global _translator
    if _translator is None:
        _translator = create_translation_service(model="gpt-4o-mini", enable_cache=True)
    return _translator

# In-memory cache for news (in production, use Redis or database)
_news_cache: dict[str, News] = {}
_cache_timestamp: datetime | None = None


@router.get("/", response_model=NewsListResponse)
async def get_news(
    sources: str = "techcrunch,theverge",
    max_age_hours: int = 24,
    limit: int = 10,
    force_refresh: bool = False,
    translate: bool = True,
) -> NewsListResponse:
    """
    Fetch latest tech news from configured sources.

    Args:
        sources: Comma-separated list of sources (e.g., "techcrunch,theverge")
        max_age_hours: Maximum age of news in hours
        limit: Maximum number of news articles to return
        force_refresh: Force refresh cache
        translate: Translate English news to Korean (default: True)

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
            news_id = f"{news.source.value}-{str(news.url).split('/')[-1][:20]}"
            _news_cache[news_id] = news

        _cache_timestamp = datetime.now()

    # Convert to response format
    news_list = list(_news_cache.values())[:limit]

    # Translate if requested
    if translate:
        logger.info("Translating news to Korean...")
        translator = get_translator()

        for news in news_list:
            try:
                # Translate title (generate() returns string directly)
                news.title = translator.generate(
                    text=news.title,
                    source_lang="English",
                    target_lang="Korean"
                )

                # Translate summary
                if news.summary:
                    news.summary = translator.generate(
                        text=news.summary,
                        source_lang="English",
                        target_lang="Korean"
                    )

                logger.debug(f"Translated: {news.title[:50]}...")
            except Exception as e:
                logger.warning(f"Translation failed for {news.title[:30]}: {e}")
                # Keep original English text if translation fails

    news_responses = [
        NewsResponse(
            id=f"{news.source.value}-{str(news.url).split('/')[-1][:20]}",
            title=news.title,
            summary=news.summary,
            url=str(news.url),
            published_at=news.published_at,
            source=news.source.value,
            category=news.category.value,
            score=news.score,
            image_url=None,  # Image URLs not currently extracted
        )
        for news in news_list
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


@router.post("/manual", response_model=NewsResponse)
async def create_manual_news(request: ManualNewsRequest) -> NewsResponse:
    """
    Create a news article manually.

    This endpoint allows users to directly input news content without crawling.
    Perfect for adding custom stories, announcements, or specific topics.

    Args:
        request: Manual news creation request with title, summary, content, etc.

    Returns:
        Created news article with generated ID

    Example:
        POST /api/news/manual
        {
            "title": "OpenAI Releases GPT-5",
            "summary": "Revolutionary AI model with enhanced capabilities...",
            "content": "Full article content...",
            "image_url": "https://example.com/image.jpg",
            "category": "ai_ml"
        }
    """
    logger.info(f"Creating manual news: {request.title[:50]}...")

    # Parse category
    try:
        category = NewsCategory(request.category)
    except ValueError:
        logger.warning(f"Invalid category '{request.category}', using AI_ML")
        category = NewsCategory.AI_ML

    # Generate unique ID
    import hashlib
    news_id = f"manual-{hashlib.md5(request.title.encode()).hexdigest()[:12]}"

    # Check if already exists
    if news_id in _news_cache:
        logger.warning(f"Manual news already exists: {news_id}")
        raise HTTPException(
            status_code=409,
            detail=f"News with this title already exists (ID: {news_id})"
        )

    # Create News object
    news = News(
        title=request.title,
        url=f"manual://{news_id}",  # Special URL for manual news
        source=NewsSource.TECHCRUNCH,  # Use TechCrunch as placeholder
        summary=request.summary,
        content=request.content or request.summary,
        published_at=datetime.now(),
        category=category,
        importance=NewsImportance.MAJOR,  # Manual news is important
        author="Manual Input",
        word_count=len((request.content or request.summary).split()),
        reading_time=len((request.content or request.summary).split()) // 200,
        image_url=request.image_url,
    )

    # Calculate score
    news.calculate_score()

    # Add to cache
    _news_cache[news_id] = news
    logger.info(f"Manual news created: {news_id} (score: {news.score:.2f})")

    # Return response
    return NewsResponse(
        id=news_id,
        title=news.title,
        summary=news.summary,
        url=str(news.url),
        published_at=news.published_at,
        source="manual",
        category=news.category.value,
        score=news.score,
        image_url=request.image_url,
    )
