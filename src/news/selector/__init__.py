"""
News selection module.

Provides algorithms for selecting optimal news articles based on:
- Importance and relevance
- Category diversity
- IT/Tech focus
- Recency
"""

from .news_selector import NewsSelector, select_news

__all__ = [
    "NewsSelector",
    "select_news",
]
