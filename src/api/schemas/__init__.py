"""API Schemas for Tech News Digest."""

from .news import NewsListResponse, NewsResponse, NewsSelectionRequest
from .schedule import ScheduleConfigResponse, ScheduleConfigUpdate
from .video import VideoCreateRequest, VideoResponse, VideoStatus

__all__ = [
    # News
    "NewsResponse",
    "NewsListResponse",
    "NewsSelectionRequest",
    # Video
    "VideoCreateRequest",
    "VideoResponse",
    "VideoStatus",
    # Schedule
    "ScheduleConfigResponse",
    "ScheduleConfigUpdate",
]
