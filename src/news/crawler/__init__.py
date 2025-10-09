"""News crawler factory."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .base_crawler import BaseCrawler


def create_news_crawler(source: str) -> "BaseCrawler":
    """
    Create a news crawler for the specified source.

    Args:
        source: News source name (e.g., "etnews", "zdnet_kr", "techcrunch", "theverge")

    Returns:
        Crawler instance

    Raises:
        ValueError: If source is not supported
    """
    source = source.lower()

    # Korean IT news sources
    if source == "etnews":
        from .sources.etnews import create_etnews_crawler

        return create_etnews_crawler()

    elif source == "zdnet_kr":
        from .sources.zdnet_kr import create_zdnet_kr_crawler

        return create_zdnet_kr_crawler()

    # English IT news sources
    elif source == "techcrunch":
        from .sources.techcrunch import create_techcrunch_crawler

        return create_techcrunch_crawler()

    elif source == "theverge":
        from .sources.theverge import create_theverge_crawler

        return create_theverge_crawler()

    else:
        raise ValueError(
            f"Unknown news source: {source}. "
            f"Supported sources: etnews, zdnet_kr, techcrunch, theverge"
        )


__all__ = ["create_news_crawler"]
