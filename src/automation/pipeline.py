"""
Content pipeline for Tech News Digest.

Orchestrates the complete workflow:
1. News collection (crawling & selection)
2. AI content generation (script, image, audio)
3. Video production (composition)
4. YouTube upload (optional)
"""

from datetime import datetime
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field

from src.core.ai_services import (
    create_image_generator,
    create_script_generator,
    create_tts_generator,
)
from src.core.logging import get_logger, log_execution_time
from src.news.crawler.sources.techcrunch import create_techcrunch_crawler
from src.news.crawler.sources.theverge import create_theverge_crawler
from src.video import VideoProject, VideoProjectConfig, VideoSegment, create_video_composer

logger = get_logger(__name__)


class PipelineConfig(BaseModel):
    """Pipeline configuration."""

    # News collection
    news_limit: int = Field(default=3, description="Number of news articles to collect")
    max_age_hours: int = Field(default=24, description="Maximum age of news articles")
    sources: list[str] = Field(
        default=["techcrunch", "theverge"], description="News sources to use"
    )

    # AI generation
    script_style: str = Field(default="professional", description="Script style")
    segment_duration: int = Field(default=60, description="Target duration per segment")
    image_quality: str = Field(default="standard", description="Image quality (standard/hd)")
    tts_voice: str = Field(default="alloy", description="TTS voice")

    # Video production
    video_title: str = Field(
        default="Tech News Digest - {date}", description="Video title template"
    )
    show_intro: bool = Field(default=True, description="Show intro")
    show_outro: bool = Field(default=True, description="Show outro")

    # YouTube upload
    enable_youtube_upload: bool = Field(default=False, description="Enable YouTube upload")

    # Output
    output_dir: Path = Field(default=Path("output"), description="Output directory")


class PipelineResult(BaseModel):
    """Pipeline execution result."""

    success: bool
    project_id: str
    video_path: Optional[Path] = None
    youtube_url: Optional[str] = None

    # Metrics
    news_count: int = 0
    total_cost: float = 0.0
    total_duration: float = 0.0
    execution_time: float = 0.0

    # Errors
    errors: list[str] = []

    created_at: datetime = Field(default_factory=datetime.now)


class ContentPipeline:
    """
    Content pipeline for automated news video production.

    Orchestrates the complete workflow from news collection to YouTube upload.
    """

    def __init__(self, config: Optional[PipelineConfig] = None):
        """
        Initialize pipeline.

        Args:
            config: Pipeline configuration
        """
        self.config = config or PipelineConfig()
        self.logger = get_logger(__name__)

        # Initialize services
        self.script_gen = create_script_generator()
        self.image_gen = create_image_generator()
        self.tts_gen = create_tts_generator()
        self.video_composer = create_video_composer(
            output_dir=self.config.output_dir / "videos"
        )

        # YouTube uploader (optional)
        self.youtube_uploader = None
        if self.config.enable_youtube_upload:
            from src.automation.youtube import create_youtube_uploader

            self.youtube_uploader = create_youtube_uploader()
            try:
                self.youtube_uploader.authenticate()
                self.logger.info("YouTube uploader authenticated")
            except Exception as e:
                self.logger.warning(f"YouTube authentication failed: {e}")
                self.youtube_uploader = None

        self.logger.info("ContentPipeline initialized")

    @log_execution_time(logger)
    def fetch_news(self) -> list:
        """
        Fetch news from configured sources.

        Returns:
            List of news articles
        """
        self.logger.info(
            f"Fetching news from {len(self.config.sources)} sources "
            f"(limit={self.config.news_limit}, max_age={self.config.max_age_hours}h)"
        )

        all_news = []

        # Fetch from each source
        for source in self.config.sources:
            try:
                if source == "techcrunch":
                    crawler = create_techcrunch_crawler()
                elif source == "theverge":
                    crawler = create_theverge_crawler()
                else:
                    self.logger.warning(f"Unknown source: {source}")
                    continue

                collection = crawler.fetch_news(
                    limit=self.config.news_limit, max_age_hours=self.config.max_age_hours
                )
                all_news.extend(collection.articles)
                self.logger.info(f"Fetched {collection.total} articles from {source}")

            except Exception as e:
                self.logger.error(f"Failed to fetch from {source}: {e}", exc_info=True)

        # Select top news (deduplicate and rank)
        selected_news = self._select_top_news(all_news, self.config.news_limit)

        self.logger.info(f"Selected {len(selected_news)} news articles")
        return selected_news

    def _select_top_news(self, news_list: list, limit: int) -> list:
        """
        Select top news from list.

        Args:
            news_list: List of news
            limit: Maximum number to select

        Returns:
            Selected news
        """
        # Deduplicate by title
        seen_titles = set()
        unique_news = []
        for news in news_list:
            if news.title not in seen_titles:
                seen_titles.add(news.title)
                unique_news.append(news)

        # Sort by score (already calculated)
        sorted_news = sorted(unique_news, key=lambda n: n.score, reverse=True)

        return sorted_news[:limit]

    @log_execution_time(logger)
    def generate_content(self, news_list: list) -> list[VideoSegment]:
        """
        Generate AI content for news articles.

        Args:
            news_list: List of news articles

        Returns:
            List of video segments
        """
        self.logger.info(f"Generating content for {len(news_list)} articles")

        segments = []
        for i, news in enumerate(news_list, 1):
            try:
                self.logger.info(f"[{i}/{len(news_list)}] Processing: {news.title[:50]}...")

                # Generate script
                script = self.script_gen.generate(
                    news,
                    style=self.config.script_style,
                    target_duration=self.config.segment_duration,
                )
                self.logger.info(f"  Script: {script.word_count} words, ${script.total_cost:.4f}")

                # Generate image
                image = self.image_gen.generate(news, quality=self.config.image_quality)
                self.logger.info(f"  Image: {image.local_path}, ${image.total_cost:.4f}")

                # Generate audio
                audio = self.tts_gen.generate(
                    script.english_script, voice=self.config.tts_voice
                )
                self.logger.info(f"  Audio: {audio.duration:.1f}s, ${audio.total_cost:.4f}")

                # Create segment
                segment = VideoSegment(
                    segment_id=f"seg_{i}",
                    title=news.title,
                    segment_number=i,
                    script=script,
                    image=image,
                    audio=audio,
                    duration=audio.duration,
                )

                segments.append(segment)
                self.logger.info(f"  Segment {i} created successfully")

            except Exception as e:
                self.logger.error(f"Failed to generate content for segment {i}: {e}", exc_info=True)

        return segments

    @log_execution_time(logger)
    def create_video(self, segments: list[VideoSegment], title: Optional[str] = None) -> Path:
        """
        Create video from segments.

        Args:
            segments: List of video segments
            title: Video title (optional)

        Returns:
            Path to created video
        """
        if not title:
            title = self.config.video_title.format(date=datetime.now().strftime("%Y-%m-%d"))

        self.logger.info(f"Creating video: {title} ({len(segments)} segments)")

        # Create project
        project = VideoProject(
            project_id=f"daily_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            title=title,
            config=VideoProjectConfig(
                title=title,
                show_intro=self.config.show_intro,
                show_outro=self.config.show_outro,
            ),
            segments=segments,
        )

        # Compose video
        video_path = self.video_composer.compose_project(project)

        self.logger.info(f"Video created: {video_path}")
        return video_path

    @log_execution_time(logger)
    def run(self) -> PipelineResult:
        """
        Run complete pipeline.

        Returns:
            Pipeline result
        """
        start_time = datetime.now()
        project_id = f"pipeline_{start_time.strftime('%Y%m%d_%H%M%S')}"

        self.logger.info(f"Starting pipeline: {project_id}")

        result = PipelineResult(
            success=False,
            project_id=project_id,
        )

        try:
            # Step 1: Fetch news
            news_list = self.fetch_news()
            if not news_list:
                result.errors.append("No news articles found")
                return result

            result.news_count = len(news_list)

            # Step 2: Generate content
            segments = self.generate_content(news_list)
            if not segments:
                result.errors.append("No segments generated")
                return result

            # Step 3: Create video
            video_path = self.create_video(segments)
            result.video_path = video_path

            # Calculate metrics
            for segment in segments:
                result.total_cost += segment.script.total_cost
                result.total_cost += segment.image.total_cost
                result.total_cost += segment.audio.total_cost
                result.total_duration += segment.duration

            # Step 4: Upload to YouTube (if enabled)
            if self.youtube_uploader:
                try:
                    self.logger.info("Uploading to YouTube...")
                    topics = [segment.title for segment in segments]
                    upload_result = self.youtube_uploader.upload_video(
                        video_path=video_path,
                        topics=topics,
                    )
                    result.youtube_url = upload_result["video_url"]
                    self.logger.info(f"YouTube upload complete: {result.youtube_url}")
                except Exception as e:
                    self.logger.error(f"YouTube upload failed: {e}", exc_info=True)
                    result.errors.append(f"YouTube upload failed: {e}")

            # Success!
            result.success = True
            result.execution_time = (datetime.now() - start_time).total_seconds()

            self.logger.info(
                f"Pipeline completed successfully! "
                f"Video: {video_path}, "
                f"Cost: ${result.total_cost:.4f}, "
                f"Duration: {result.total_duration:.1f}s"
            )
            if result.youtube_url:
                self.logger.info(f"YouTube: {result.youtube_url}")

        except Exception as e:
            self.logger.error(f"Pipeline failed: {e}", exc_info=True)
            result.errors.append(str(e))
            result.execution_time = (datetime.now() - start_time).total_seconds()

        return result


def create_pipeline(config: Optional[PipelineConfig] = None) -> ContentPipeline:
    """
    Create content pipeline.

    Args:
        config: Pipeline configuration

    Returns:
        ContentPipeline instance

    Example:
        >>> pipeline = create_pipeline()
        >>> result = pipeline.run()
        >>> print(result.video_path)
    """
    return ContentPipeline(config=config)
