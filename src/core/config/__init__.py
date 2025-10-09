"""
Configuration management for Tech News Digest.

Provides type-safe settings using Pydantic with:
- Environment variable loading
- Validation
- Default values
- Nested configuration

Usage:
    >>> from src.core.config import get_settings
    >>>
    >>> settings = get_settings()
    >>> print(settings.openai.api_key)
    >>> print(settings.is_production)
"""

from .settings import (
    AWSSettings,
    ContentSettings,
    CrawlerSettings,
    DatabaseSettings,
    Environment,
    ImageSettings,
    LogFormat,
    MonitoringSettings,
    NewsSourcesSettings,
    OpenAISettings,
    RedisSettings,
    SchedulerSettings,
    Settings,
    TTSSettings,
    VideoSettings,
    YouTubeSettings,
    get_settings,
    reload_settings,
)

__all__ = [
    # Main functions
    "get_settings",
    "reload_settings",
    # Enums
    "Environment",
    "LogFormat",
    # Settings classes
    "Settings",
    "OpenAISettings",
    "YouTubeSettings",
    "DatabaseSettings",
    "RedisSettings",
    "AWSSettings",
    "CrawlerSettings",
    "NewsSourcesSettings",
    "VideoSettings",
    "ImageSettings",
    "TTSSettings",
    "SchedulerSettings",
    "MonitoringSettings",
    "ContentSettings",
]
