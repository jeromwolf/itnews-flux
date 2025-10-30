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
from src.video.image_selector import create_image_selector
from src.video.thumbnail_generator import ThumbnailConfig, ThumbnailGenerator

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
    use_image_pool: bool = Field(default=True, description="Use pre-generated image pool")
    tts_voice: str = Field(default="alloy", description="TTS voice")

    # Video production
    video_title: str = Field(
        default="Tech News Digest - {date}", description="Video title template"
    )
    show_intro: bool = Field(default=True, description="Show intro")
    show_outro: bool = Field(default=True, description="Show outro")

    # YouTube upload
    enable_youtube_upload: bool = Field(default=False, description="Enable YouTube upload")
    generate_thumbnail: bool = Field(default=True, description="Generate YouTube thumbnail")
    thumbnail_brand_text: str = Field(default="AI ON", description="Thumbnail brand text")

    # Output
    output_dir: Path = Field(default=Path("output"), description="Output directory")


class PipelineResult(BaseModel):
    """Pipeline execution result."""

    success: bool
    project_id: str
    video_path: Optional[Path] = None
    thumbnail_path: Optional[Path] = None
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

        # Use ImageSelector instead of direct ImageGenerator
        # This allows cost savings through image pool
        self.image_selector = create_image_selector(
            use_pool=self.config.use_image_pool,
            fallback_to_generation=True,
        )

        self.tts_gen = create_tts_generator()
        self.video_composer = create_video_composer(
            output_dir=self.config.output_dir / "videos"
        )

        # Thumbnail generator
        self.thumbnail_generator = None
        if self.config.generate_thumbnail:
            thumbnail_config = ThumbnailConfig(
                brand_text=self.config.thumbnail_brand_text
            )
            self.thumbnail_generator = ThumbnailGenerator(config=thumbnail_config)
            self.logger.info("Thumbnail generator initialized")

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
                # 첫 번째 뉴스에만 오프닝 멘트, 마지막 뉴스에만 클로징 멘트 포함
                script = self.script_gen.generate(
                    news,
                    style=self.config.script_style,
                    target_duration=self.config.segment_duration,
                    is_first_segment=(i == 1),  # 첫 번째 세그먼트 (오프닝)
                    is_last_segment=(i == len(news_list)),  # 마지막 세그먼트 (클로징)
                )
                self.logger.info(f"  Script: {script.word_count} words, ${script.total_cost:.4f}")

                # Get image (from pool or generate)
                image = self.image_selector.get_image_for_news(
                    news,
                    quality=self.config.image_quality,
                )
                source = "pool" if image.from_pool else "generated"
                self.logger.info(f"  Image: {image.local_path} ({source}), ${image.total_cost:.4f}")

                # Generate audio with voice rotation
                # 한글 번역이 있으면 한글로, 없으면 영어로 TTS 생성
                # Option 1: 세그먼트별 목소리 교체 (다양성 증가)
                voice_rotation = ["nova", "onyx", "shimmer", "fable", "echo"]
                selected_voice = voice_rotation[(i - 1) % len(voice_rotation)]

                tts_text = script.korean_translation if script.korean_translation else script.english_script
                audio = self.tts_gen.generate(
                    tts_text, voice=selected_voice
                )
                self.logger.info(f"  Audio: {audio.duration:.1f}s, voice={selected_voice}, ${audio.total_cost:.4f} (language: {'Korean' if script.korean_translation else 'English'})")

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

        # Log image pool statistics
        pool_status = self.image_selector.get_pool_status()
        self.logger.info(
            f"\n📊 Image Pool Statistics:\n"
            f"  Pool usage: {pool_status['pool_usage_count']}/{pool_status['total_requests']} "
            f"({pool_status['pool_usage_rate']:.0%})\n"
            f"  Savings: ${pool_status['total_savings']:.4f}\n"
            f"  Generation cost: ${pool_status['total_generation_cost']:.4f}\n"
            f"  Categories in pool: {pool_status['categories_in_pool']}\n"
            f"  Total pool images: {pool_status['total_pool_images']}"
        )

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

            # Step 4: Generate thumbnail (if enabled)
            thumbnail_path = None
            if self.thumbnail_generator and segments:
                try:
                    self.logger.info("Generating YouTube thumbnail...")
                    # Use first segment's title and image for thumbnail
                    first_segment = segments[0]
                    thumbnail_path = self.thumbnail_generator.generate(
                        title=first_segment.title,
                        background_image_path=Path(first_segment.image.image_path),
                        subtitle=f"Tech News • {datetime.now().strftime('%B %d, %Y')}",
                    )
                    result.thumbnail_path = thumbnail_path
                    self.logger.info(f"Thumbnail generated: {thumbnail_path}")
                except Exception as e:
                    self.logger.warning(f"Thumbnail generation failed: {e}", exc_info=True)
                    result.errors.append(f"Thumbnail generation failed: {e}")

            # Step 5: Upload to YouTube (if enabled)
            if self.youtube_uploader:
                try:
                    self.logger.info("Uploading to YouTube...")
                    topics = [segment.title for segment in segments]
                    upload_result = self.youtube_uploader.upload_video(
                        video_path=video_path,
                        topics=topics,
                    )
                    video_id = upload_result["video_id"]
                    result.youtube_url = upload_result["video_url"]
                    self.logger.info(f"YouTube upload complete: {result.youtube_url}")

                    # Upload thumbnail (if generated)
                    if thumbnail_path and thumbnail_path.exists():
                        try:
                            self.logger.info("Uploading thumbnail to YouTube...")
                            self.youtube_uploader.set_thumbnail(video_id, thumbnail_path)
                            self.logger.info("Thumbnail uploaded successfully")
                        except Exception as e:
                            self.logger.warning(f"Thumbnail upload failed: {e}", exc_info=True)
                            result.errors.append(f"Thumbnail upload failed: {e}")

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
