"""
Application settings management using Pydantic.

Provides type-safe configuration management with:
- Environment variable loading
- Validation
- Default values
- Nested configuration
"""

from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(str, Enum):
    """Application environment types."""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class LogFormat(str, Enum):
    """Log format types."""

    JSON = "json"
    TEXT = "text"


class OpenAISettings(BaseSettings):
    """OpenAI API settings."""

    model_config = SettingsConfigDict(env_prefix="OPENAI_", extra="ignore")

    api_key: str = Field(..., description="OpenAI API key")
    org_id: str | None = Field(None, description="OpenAI Organization ID")

    # Model settings
    gpt_model: str = Field("gpt-4o", description="GPT model to use")
    image_model: str = Field("dall-e-3", description="Image generation model")
    tts_model: str = Field("tts-1", description="Text-to-speech model")
    tts_voice: str = Field("alloy", description="TTS voice name")

    @field_validator("tts_voice")
    @classmethod
    def validate_tts_voice(cls, v: str) -> str:
        """Validate TTS voice name."""
        valid_voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
        if v not in valid_voices:
            raise ValueError(f"Invalid TTS voice. Must be one of: {valid_voices}")
        return v


class YouTubeSettings(BaseSettings):
    """YouTube API settings."""

    model_config = SettingsConfigDict(env_prefix="YOUTUBE_", extra="ignore")

    api_key: str = Field(..., description="YouTube Data API key")
    channel_id: str | None = Field(None, description="YouTube channel ID")
    category_id: str = Field("28", description="Video category (28 = Science & Technology)")
    privacy_status: str = Field("public", description="Upload privacy status")
    upload_time: str = Field("07:00", description="Daily upload time")

    @field_validator("privacy_status")
    @classmethod
    def validate_privacy(cls, v: str) -> str:
        """Validate privacy status."""
        if v not in ["public", "private", "unlisted"]:
            raise ValueError("Privacy status must be: public, private, or unlisted")
        return v


class DatabaseSettings(BaseSettings):
    """Database configuration."""

    model_config = SettingsConfigDict(env_prefix="DATABASE_", extra="ignore")

    url: str = Field(
        "postgresql://user:password@localhost:5432/technews",
        description="Database connection URL",
    )
    pool_size: int = Field(5, description="Connection pool size")
    max_overflow: int = Field(10, description="Max overflow connections")


class RedisSettings(BaseSettings):
    """Redis cache configuration."""

    model_config = SettingsConfigDict(env_prefix="REDIS_", extra="ignore")

    url: str = Field("redis://localhost:6379/0", description="Redis connection URL")
    password: str | None = Field(None, description="Redis password")
    max_connections: int = Field(10, description="Max connections")


class AWSSettings(BaseSettings):
    """AWS configuration."""

    model_config = SettingsConfigDict(env_prefix="AWS_", extra="ignore")

    access_key_id: str | None = Field(None, description="AWS access key ID")
    secret_access_key: str | None = Field(None, description="AWS secret access key")
    region: str = Field("ap-northeast-2", description="AWS region")
    s3_bucket: str | None = Field(None, description="S3 bucket name")
    s3_video_prefix: str = Field("videos/", description="S3 video prefix")
    s3_thumbnail_prefix: str = Field("thumbnails/", description="S3 thumbnail prefix")


class CrawlerSettings(BaseSettings):
    """News crawler settings."""

    model_config = SettingsConfigDict(env_prefix="CRAWLER_", extra="ignore")

    user_agent: str = Field(
        "TechNewsDigest/1.0 (+https://technewsdigest.com)",
        description="User agent string",
    )
    timeout: int = Field(30, description="Request timeout in seconds")
    max_retries: int = Field(3, description="Max retry attempts")
    retry_delay: int = Field(5, description="Retry delay in seconds")


class NewsSourcesSettings(BaseSettings):
    """News sources configuration."""

    model_config = SettingsConfigDict(env_prefix="NEWS_SOURCES_", extra="ignore")

    it: str = Field(
        "techcrunch,theverge,arstechnica,wired,mittr",
        description="IT news sources (comma-separated)",
    )
    business: str = Field(
        "reuters,bloomberg",
        description="Business news sources (comma-separated)",
    )

    @property
    def it_sources(self) -> list[str]:
        """Get IT news sources as list."""
        return [s.strip() for s in self.it.split(",") if s.strip()]

    @property
    def business_sources(self) -> list[str]:
        """Get business news sources as list."""
        return [s.strip() for s in self.business.split(",") if s.strip()]


class VideoSettings(BaseSettings):
    """Video generation settings."""

    model_config = SettingsConfigDict(env_prefix="VIDEO_", extra="ignore")

    width: int = Field(1920, description="Video width")
    height: int = Field(1080, description="Video height")
    fps: int = Field(30, description="Frames per second")
    duration: int = Field(300, description="Video duration in seconds")
    bitrate: str = Field("5000k", description="Video bitrate")


class ImageSettings(BaseSettings):
    """Image generation settings."""

    model_config = SettingsConfigDict(env_prefix="IMAGE_", extra="ignore")

    width: int = Field(1792, description="Image width")
    height: int = Field(1024, description="Image height")
    quality: str = Field("hd", description="Image quality")

    @field_validator("quality")
    @classmethod
    def validate_quality(cls, v: str) -> str:
        """Validate image quality."""
        if v not in ["standard", "hd"]:
            raise ValueError("Image quality must be 'standard' or 'hd'")
        return v


class TTSSettings(BaseSettings):
    """Text-to-speech settings."""

    model_config = SettingsConfigDict(env_prefix="TTS_", extra="ignore")

    speed: float = Field(1.0, ge=0.25, le=4.0, description="Speech speed")
    format: str = Field("mp3", description="Audio format")


class SchedulerSettings(BaseSettings):
    """Scheduler settings."""

    model_config = SettingsConfigDict(env_prefix="SCHEDULER_", extra="ignore")

    enabled: bool = Field(True, description="Enable scheduler")
    run_time: str = Field("06:00", description="Daily run time")
    timezone: str = Field("Asia/Seoul", description="Timezone")


class MonitoringSettings(BaseSettings):
    """Monitoring and alerting settings."""

    model_config = SettingsConfigDict(env_prefix="", extra="ignore")

    # Slack
    slack_webhook_url: str | None = Field(None, description="Slack webhook URL")
    slack_channel: str = Field("#tech-news-alerts", description="Slack channel")

    # Email
    smtp_host: str = Field("smtp.gmail.com", description="SMTP host")
    smtp_port: int = Field(587, description="SMTP port")
    smtp_user: str | None = Field(None, description="SMTP username")
    smtp_password: str | None = Field(None, description="SMTP password")
    alert_email: str | None = Field(None, description="Alert email address")

    # Sentry
    sentry_dsn: str | None = Field(None, description="Sentry DSN")


class ContentSettings(BaseSettings):
    """Content generation settings."""

    model_config = SettingsConfigDict(env_prefix="", extra="ignore")

    # News selection
    news_count_total: int = Field(5, description="Total news count")
    news_count_it: int = Field(4, description="IT news count")
    news_count_business: int = Field(1, description="Business news count")

    # Category weights
    weight_ai_ml: float = Field(1.5, description="AI/ML category weight")
    weight_software_cloud: float = Field(1.3, description="Software/Cloud weight")
    weight_startup_funding: float = Field(1.2, description="Startup/Funding weight")
    weight_security: float = Field(1.2, description="Security weight")
    weight_business: float = Field(1.0, description="Business weight")


class Settings(BaseSettings):
    """Main application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_env: Environment = Field(Environment.DEVELOPMENT, description="Environment")
    app_debug: bool = Field(True, description="Debug mode")
    app_log_level: str = Field("INFO", description="Log level")
    app_port: int = Field(8000, description="Application port")

    # Logging
    log_file_path: Path = Field(Path("logs/app.log"), description="Log file path")
    log_max_bytes: int = Field(10485760, description="Max log file size (10MB)")
    log_backup_count: int = Field(5, description="Log backup count")
    log_format: LogFormat = Field(LogFormat.TEXT, description="Log format")

    # Security
    secret_key: str = Field(..., description="Secret key")
    jwt_secret: str = Field(..., description="JWT secret")
    jwt_algorithm: str = Field("HS256", description="JWT algorithm")
    jwt_expiration: int = Field(3600, description="JWT expiration (seconds)")

    # Feature flags
    feature_auto_upload: bool = Field(True, description="Auto upload to YouTube")
    feature_generate_subtitles: bool = Field(False, description="Generate subtitles")
    feature_multilingual: bool = Field(False, description="Multilingual support")
    feature_analytics: bool = Field(True, description="Enable analytics")

    # Rate limiting
    rate_limit_openai_rpm: int = Field(60, description="OpenAI requests per minute")
    rate_limit_openai_rpd: int = Field(1000, description="OpenAI requests per day")
    rate_limit_crawler_rps: int = Field(5, description="Crawler requests per second")

    # Cache settings
    cache_enabled: bool = Field(True, description="Enable caching")
    cache_ttl_news: int = Field(3600, description="News cache TTL (seconds)")
    cache_ttl_image: int = Field(86400, description="Image cache TTL (seconds)")
    cache_ttl_tts: int = Field(86400, description="TTS cache TTL (seconds)")

    # Nested settings
    openai: OpenAISettings = Field(default_factory=OpenAISettings)
    youtube: YouTubeSettings = Field(default_factory=YouTubeSettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    aws: AWSSettings = Field(default_factory=AWSSettings)
    crawler: CrawlerSettings = Field(default_factory=CrawlerSettings)
    news_sources: NewsSourcesSettings = Field(default_factory=NewsSourcesSettings)
    video: VideoSettings = Field(default_factory=VideoSettings)
    image: ImageSettings = Field(default_factory=ImageSettings)
    tts: TTSSettings = Field(default_factory=TTSSettings)
    scheduler: SchedulerSettings = Field(default_factory=SchedulerSettings)
    monitoring: MonitoringSettings = Field(default_factory=MonitoringSettings)
    content: ContentSettings = Field(default_factory=ContentSettings)

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.app_env == Environment.DEVELOPMENT

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.app_env == Environment.PRODUCTION

    @property
    def is_testing(self) -> bool:
        """Check if running in testing mode."""
        return self.app_env == Environment.TESTING

    def model_dump_safe(self) -> dict[str, Any]:
        """
        Dump settings with sensitive data redacted.

        Returns:
            Settings dictionary with API keys and secrets redacted
        """
        data = self.model_dump()

        # Redact sensitive fields
        sensitive_fields = [
            "api_key",
            "secret",
            "password",
            "access_key",
            "webhook_url",
            "dsn",
        ]

        def redact_dict(d: dict) -> dict:
            for key, value in d.items():
                if isinstance(value, dict):
                    d[key] = redact_dict(value)
                elif any(sensitive in key.lower() for sensitive in sensitive_fields):
                    d[key] = "***REDACTED***"
            return d

        return redact_dict(data)


# Global settings instance
_settings: Settings | None = None


def get_settings() -> Settings:
    """
    Get global settings instance.

    Returns:
        Application settings

    Example:
        >>> from src.core.config import get_settings
        >>> settings = get_settings()
        >>> print(settings.openai.api_key)
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reload_settings() -> Settings:
    """
    Reload settings from environment.

    Returns:
        Reloaded settings instance
    """
    global _settings
    _settings = Settings()
    return _settings
