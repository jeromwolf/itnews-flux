"""API Routers for Tech News Digest."""

from .analytics import router as analytics_router
from .news import router as news_router
from .schedule import router as schedule_router
from .videos import router as videos_router

__all__ = ["news_router", "videos_router", "schedule_router", "analytics_router"]
