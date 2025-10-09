"""Automation system for Tech News Digest."""

from .pipeline import ContentPipeline, PipelineConfig, PipelineResult, create_pipeline
from .scheduler import DailyScheduler, SchedulerConfig, create_scheduler
from .youtube import YouTubeConfig, YouTubeUploader, create_youtube_uploader

__all__ = [
    # Pipeline
    "ContentPipeline",
    "PipelineConfig",
    "PipelineResult",
    "create_pipeline",
    # Scheduler
    "DailyScheduler",
    "SchedulerConfig",
    "create_scheduler",
    # YouTube
    "YouTubeUploader",
    "YouTubeConfig",
    "create_youtube_uploader",
]
