"""Video API schemas."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class VideoStatus(str, Enum):
    """Video creation status."""

    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"
    UPLOADING = "uploading"
    UPLOADED = "uploaded"


class VideoCreateRequest(BaseModel):
    """Request to create a new video."""

    news_ids: list[str] = Field(..., min_length=1, max_length=5)
    upload_to_youtube: bool = Field(default=False)
    style: str = Field(default="professional")
    voice: str = Field(default="alloy")

    class Config:
        json_schema_extra = {
            "example": {
                "news_ids": ["techcrunch-123", "theverge-456"],
                "upload_to_youtube": True,
                "style": "professional",
                "voice": "alloy",
            }
        }


class VideoSegmentInfo(BaseModel):
    """Information about a video segment."""

    title: str
    duration: float
    cost: float


class VideoResponse(BaseModel):
    """Response schema for a video."""

    id: str
    status: VideoStatus
    title: str
    created_at: datetime
    video_path: str | None = None
    youtube_url: str | None = None
    duration: float | None = None
    segments: list[VideoSegmentInfo] = []
    total_cost: float = Field(default=0.0)
    error: str | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "id": "video-20251009-001",
                "status": "completed",
                "title": "Tech News Digest - 2025-10-09",
                "created_at": "2025-10-09T10:30:00Z",
                "video_path": "/output/videos/tech_news_20251009.mp4",
                "youtube_url": "https://youtube.com/watch?v=...",
                "duration": 120.5,
                "segments": [
                    {"title": "OpenAI GPT-5", "duration": 60.0, "cost": 0.012},
                    {"title": "Tesla AI", "duration": 60.5, "cost": 0.011},
                ],
                "total_cost": 0.023,
                "error": None,
            }
        }
