"""
Video composer for Tech News Digest.

Combines all elements into final video:
- News images
- Audio narration
- Lower third subtitles
- Transitions
- Intro/outro (optional)
"""

from pathlib import Path
from typing import Optional

from moviepy import (
    AudioFileClip,
    ColorClip,
    CompositeVideoClip,
    ImageClip,
    TextClip,
    VideoClip,
    concatenate_videoclips,
    vfx,
)

from src.core.logging import get_logger, log_execution_time
from src.video.layout.lower_third import LowerThirdGenerator
from src.video.models import (
    LowerThirdConfig,
    VideoProject,
    VideoProjectConfig,
    VideoSegment,
)

logger = get_logger(__name__)


class VideoComposer:
    """
    Video composer for news videos.

    Combines generated content into professional news videos with:
    - Image backgrounds
    - Audio narration
    - Lower third subtitles
    - Smooth transitions
    """

    def __init__(
        self,
        output_dir: Optional[Path] = None,
    ):
        """
        Initialize video composer.

        Args:
            output_dir: Output directory for videos
        """
        self.logger = get_logger(__name__)
        self.output_dir = output_dir or Path("output/videos")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.logger.info(f"VideoComposer initialized (output_dir={self.output_dir})")

    @log_execution_time(logger)
    def compose_project(
        self,
        project: VideoProject,
        output_path: Optional[Path] = None,
    ) -> Path:
        """
        Compose complete video project.

        Args:
            project: Video project with segments
            output_path: Output file path (optional)

        Returns:
            Path to generated video

        Raises:
            ValueError: If project validation fails
        """
        self.logger.info(
            f"Composing video project: {project.title} "
            f"({project.segment_count} segments, "
            f"{project.total_duration:.1f}s)"
        )

        # Validate project
        validation = project.validate_project()
        if not validation["valid"]:
            error_msg = f"Project validation failed: {validation['errors']}"
            self.logger.error(error_msg)
            raise ValueError(error_msg)

        if validation["warnings"]:
            for warning in validation["warnings"]:
                self.logger.warning(warning)

        # Generate output path
        if not output_path:
            timestamp = project.created_at.strftime("%Y%m%d_%H%M%S")
            filename = f"tech_news_{timestamp}.{project.config.format.value}"
            output_path = self.output_dir / filename

        # Create video clips
        clips = []

        # Add intro if enabled
        if project.config.show_intro:
            intro_clip = self._create_intro_clip(project.config)
            clips.append(intro_clip)
            self.logger.info("Added intro clip")

        # Add news segments
        for i, segment in enumerate(project.segments, 1):
            self.logger.info(f"Processing segment {i}/{project.segment_count}")
            segment_clip = self._create_segment_clip(segment, project.config)
            clips.append(segment_clip)

        # Add outro if enabled
        if project.config.show_outro:
            outro_clip = self._create_outro_clip(project.config)
            clips.append(outro_clip)
            self.logger.info("Added outro clip")

        # Concatenate all clips
        self.logger.info(f"Concatenating {len(clips)} clips...")
        final_video = concatenate_videoclips(clips, method="compose")

        # Write video file
        self.logger.info(f"Rendering video to: {output_path}")
        final_video.write_videofile(
            str(output_path),
            fps=project.config.fps,
            codec=project.config.codec,
            audio_codec=project.config.audio_codec,
            bitrate=project.config.bitrate,
            logger=None,  # Suppress MoviePy's own logger
        )

        # Update project
        project.output_path = output_path
        project.is_rendered = True

        self.logger.info(f"Video composition complete: {output_path}")
        return output_path

    def _create_segment_clip(
        self,
        segment: VideoSegment,
        config: VideoProjectConfig,
    ) -> VideoClip:
        """
        Create video clip for a single news segment.

        Args:
            segment: Video segment
            config: Project configuration

        Returns:
            Composed video clip
        """
        # Create image clip (background)
        image_clip = ImageClip(str(segment.image.local_path))
        image_clip = image_clip.with_duration(segment.duration)
        image_clip = image_clip.resized(width=config.width, height=config.height)

        # Add audio
        audio_clip = AudioFileClip(str(segment.audio.local_path))
        image_clip = image_clip.with_audio(audio_clip)

        # Add lower third if enabled
        if segment.show_lower_third:
            lower_third_clip = self._create_lower_third_clip(segment, config)

            # Composite image + lower third
            final_clip = CompositeVideoClip(
                [image_clip, lower_third_clip],
                size=(config.width, config.height),
            )
        else:
            final_clip = image_clip

        # Add fade transitions
        if segment.transition_duration > 0:
            final_clip = final_clip.with_effects([
                vfx.FadeIn(segment.transition_duration),
                vfx.FadeOut(segment.transition_duration),
            ])

        return final_clip

    def _create_lower_third_clip(
        self,
        segment: VideoSegment,
        config: VideoProjectConfig,
    ) -> VideoClip:
        """
        Create lower third clip for segment.

        Args:
            segment: Video segment
            config: Project configuration

        Returns:
            Lower third video clip
        """
        # Create lower third generator
        lt_generator = LowerThirdGenerator(config)

        # Configure lower third
        lt_config = LowerThirdConfig(
            primary_text=segment.title,
            secondary_text=segment.script.korean_translation[:100]
            if segment.script
            else None,
        )

        # Generate lower third image
        temp_path = self.output_dir / f"lower_third_{segment.segment_id}.png"
        lt_image = lt_generator.generate(lt_config, temp_path)

        # Create image clip
        lt_clip = ImageClip(str(temp_path))
        lt_clip = lt_clip.with_duration(segment.duration)

        # Position at bottom
        lt_clip = lt_clip.with_position(("center", "bottom"))

        # Add fade in/out
        lt_clip = lt_clip.with_effects([
            vfx.FadeIn(lt_config.fade_in_duration),
            vfx.FadeOut(lt_config.fade_out_duration),
        ])

        return lt_clip

    def _create_intro_clip(self, config: VideoProjectConfig) -> VideoClip:
        """
        Create intro clip.

        Args:
            config: Project configuration

        Returns:
            Intro video clip
        """
        # Create simple colored intro (can be enhanced later)
        # Background
        intro_clip = ColorClip(
            size=(config.width, config.height),
            color=self._hex_to_rgb(config.primary_color),
            duration=config.intro_duration,
        )

        # Add title text
        try:
            title_clip = TextClip(
                text=config.title,
                font_size=80,
                color="white",
                font="Arial-Bold",
                size=(config.width * 0.8, None),
            )
            title_clip = title_clip.with_duration(config.intro_duration)
            title_clip = title_clip.with_position("center")
            title_clip = title_clip.with_effects([vfx.FadeIn(0.5), vfx.FadeOut(0.5)])

            intro_clip = CompositeVideoClip([intro_clip, title_clip])
        except Exception as e:
            self.logger.warning(f"Failed to add title text: {e}")

        return intro_clip

    def _create_outro_clip(self, config: VideoProjectConfig) -> VideoClip:
        """
        Create outro clip.

        Args:
            config: Project configuration

        Returns:
            Outro video clip
        """
        # Background
        outro_clip = ColorClip(
            size=(config.width, config.height),
            color=self._hex_to_rgb(config.secondary_color),
            duration=config.outro_duration,
        )

        # Add text
        try:
            text_clip = TextClip(
                text="Thank you for watching!\n\nSubscribe for more tech news",
                font_size=60,
                color="white",
                font="Arial",
                size=(config.width * 0.8, None),
            )
            text_clip = text_clip.with_duration(config.outro_duration)
            text_clip = text_clip.with_position("center")
            text_clip = text_clip.with_effects([vfx.FadeIn(0.5)])

            outro_clip = CompositeVideoClip([outro_clip, text_clip])
        except Exception as e:
            self.logger.warning(f"Failed to add outro text: {e}")

        return outro_clip

    def _hex_to_rgb(self, hex_color: str) -> tuple[int, int, int]:
        """
        Convert hex color to RGB tuple.

        Args:
            hex_color: Hex color string

        Returns:
            RGB tuple
        """
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))

    def compose_segment(
        self,
        segment: VideoSegment,
        config: Optional[VideoProjectConfig] = None,
        output_path: Optional[Path] = None,
    ) -> Path:
        """
        Compose a single segment into a video.

        Args:
            segment: Video segment
            config: Project configuration (uses defaults if not provided)
            output_path: Output file path (optional)

        Returns:
            Path to generated video
        """
        if not config:
            config = VideoProjectConfig()

        # Create project with single segment
        from datetime import datetime

        project = VideoProject(
            project_id=f"single_{segment.segment_id}",
            title=segment.title,
            config=config,
            segments=[segment],
        )

        # Disable intro/outro for single segment
        project.config.show_intro = False
        project.config.show_outro = False

        return self.compose_project(project, output_path)


def create_video_composer(output_dir: Optional[Path] = None) -> VideoComposer:
    """
    Create video composer instance.

    Args:
        output_dir: Output directory for videos

    Returns:
        VideoComposer instance

    Example:
        >>> composer = create_video_composer()
        >>> video_path = composer.compose_project(project)
    """
    return VideoComposer(output_dir=output_dir)
