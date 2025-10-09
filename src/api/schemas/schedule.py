"""Schedule API schemas."""

from pydantic import BaseModel, Field


class ScheduleConfigResponse(BaseModel):
    """Response schema for schedule configuration."""

    enabled: bool = Field(default=True)
    hour: int = Field(default=7, ge=0, le=23)
    minute: int = Field(default=0, ge=0, le=59)
    timezone: str = Field(default="Asia/Seoul")
    news_limit: int = Field(default=3, ge=1, le=10)
    enable_youtube_upload: bool = Field(default=False)
    next_run: str | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "enabled": True,
                "hour": 7,
                "minute": 0,
                "timezone": "Asia/Seoul",
                "news_limit": 3,
                "enable_youtube_upload": True,
                "next_run": "2025-10-10 07:00:00 KST",
            }
        }


class ScheduleConfigUpdate(BaseModel):
    """Request to update schedule configuration."""

    enabled: bool | None = None
    hour: int | None = Field(None, ge=0, le=23)
    minute: int | None = Field(None, ge=0, le=59)
    timezone: str | None = None
    news_limit: int | None = Field(None, ge=1, le=10)
    enable_youtube_upload: bool | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "enabled": True,
                "hour": 9,
                "minute": 30,
                "news_limit": 5,
                "enable_youtube_upload": True,
            }
        }
