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
        image_clip = image_clip.resized(width=config.width, height=config.height)

        # Add audio
        audio_clip = AudioFileClip(str(segment.audio.local_path))

        # IMPORTANT: 이미지 duration을 오디오 길이에 맞춤 (오디오 겹침 방지)
        actual_duration = audio_clip.duration
        image_clip = image_clip.with_duration(actual_duration)
        image_clip = image_clip.with_audio(audio_clip)

        self.logger.debug(f"Segment duration: audio={actual_duration:.2f}s")

        # Add lower third if enabled
        if segment.show_lower_third:
            lower_third_clip = self._create_lower_third_clip(segment, config, actual_duration)

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
        duration: float,
    ) -> VideoClip:
        """
        Create lower third clip for segment.

        Args:
            segment: Video segment
            config: Project configuration
            duration: Actual segment duration (from audio)

        Returns:
            Lower third video clip
        """
        # Create lower third generator
        lt_generator = LowerThirdGenerator(config)

        # Configure lower third
        # Lower Third: 뉴스 제목만 표시 (영어만, 깔끔하게)
        lt_config = LowerThirdConfig(
            primary_text=segment.title,
            secondary_text=None,  # 부제목 없음 (스크립트 내용 표시 방지)
        )

        # Generate lower third image
        temp_path = self.output_dir / f"lower_third_{segment.segment_id}.png"
        lt_image = lt_generator.generate(lt_config, temp_path)

        # Create image clip
        lt_clip = ImageClip(str(temp_path))
        lt_clip = lt_clip.with_duration(duration)  # Use actual audio duration

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
        Create intro clip with Korean font support and custom image.

        Args:
            config: Project configuration

        Returns:
            Intro video clip
        """
        # Background: 1. Custom image, 2. AI ON image, 3. Old default, 4. ColorClip fallback
        if config.use_custom_intro and config.intro_image_path and config.intro_image_path.exists():
            # Use custom image
            intro_bg = ImageClip(str(config.intro_image_path))
            self.logger.info(f"Using custom intro image: {config.intro_image_path}")
        else:
            # Try AI ON intro
            ai_on_intro = Path("resources/ai_on_intro.png")
            if ai_on_intro.exists():
                intro_bg = ImageClip(str(ai_on_intro))
                self.logger.info(f"Using AI ON intro image: {ai_on_intro}")
            else:
                # Try old default
                default_intro = Path("resources/intro_background.png")
                if default_intro.exists():
                    intro_bg = ImageClip(str(default_intro))
                    self.logger.info(f"Using default intro image: {default_intro}")
                else:
                    # Fallback to ColorClip
                    intro_bg = ColorClip(
                        size=(config.width, config.height),
                        color=self._hex_to_rgb(config.primary_color),
                        duration=config.intro_duration,
                    )
                    self.logger.warning("No intro image found, using ColorClip fallback")

        # Set duration and size
        intro_bg = intro_bg.with_duration(config.intro_duration)
        intro_bg = intro_bg.resized(width=config.width, height=config.height)

        # Add title text using PIL for precise control
        try:
            from PIL import Image, ImageDraw, ImageFont
            import numpy as np

            # Create transparent overlay with text
            overlay = Image.new('RGBA', (config.width, config.height), (0, 0, 0, 0))
            draw = ImageDraw.Draw(overlay)

            # Use default font with large size (macOS compatible)
            try:
                # Try macOS fonts first
                font_large = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 140)
                font_medium = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 48)
            except:
                try:
                    # Fallback to Linux fonts
                    font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 140)
                    font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 48)
                except:
                    # Last resort: default font
                    font_large = ImageFont.load_default()
                    font_medium = ImageFont.load_default()

            # Draw "AI ON" in center
            text1 = "AI ON"
            bbox1 = draw.textbbox((0, 0), text1, font=font_large)
            text1_width = bbox1[2] - bbox1[0]
            text1_height = bbox1[3] - bbox1[1]
            x1 = (config.width - text1_width) // 2
            y1 = (config.height - text1_height) // 2 - 60  # Slightly above center

            # Draw stroke (outline)
            stroke_width = 5
            for adj_x in range(-stroke_width, stroke_width+1):
                for adj_y in range(-stroke_width, stroke_width+1):
                    draw.text((x1+adj_x, y1+adj_y), text1, font=font_large, fill=(0, 0, 0, 255))
            # Draw main text
            draw.text((x1, y1), text1, font=font_large, fill=(255, 255, 255, 255))

            # Draw tagline below
            text2 = "Your Daily Tech Intelligence"
            bbox2 = draw.textbbox((0, 0), text2, font=font_medium)
            text2_width = bbox2[2] - bbox2[0]
            text2_height = bbox2[3] - bbox2[1]
            x2 = (config.width - text2_width) // 2
            y2 = y1 + text1_height + 40  # 40px below AI ON

            # Draw stroke
            stroke_width = 3
            for adj_x in range(-stroke_width, stroke_width+1):
                for adj_y in range(-stroke_width, stroke_width+1):
                    draw.text((x2+adj_x, y2+adj_y), text2, font=font_medium, fill=(0, 0, 0, 255))
            # Draw main text
            draw.text((x2, y2), text2, font=font_medium, fill=(255, 255, 255, 255))

            # Convert to numpy array and create clip
            overlay_array = np.array(overlay)
            text_clip = ImageClip(overlay_array).with_duration(config.intro_duration)
            text_clip = text_clip.with_effects([vfx.FadeIn(0.5), vfx.FadeOut(0.5)])

            intro_clip = CompositeVideoClip([intro_bg, text_clip])
            self.logger.info("AI ON intro created with PIL text overlay")

        except Exception as e:
            self.logger.warning(f"Failed to add intro text: {e}")
            intro_clip = intro_bg

        # Add background music if available
        intro_music_path = Path("resources/intro_music.mp3")
        if intro_music_path.exists():
            try:
                from moviepy import AudioFileClip
                import moviepy.audio.fx as afx

                music = AudioFileClip(str(intro_music_path))
                music = music.subclipped(0, min(music.duration, config.intro_duration))
                # Reduce volume to 30%
                music = music.with_effects([afx.MultiplyVolume(0.3)])
                intro_clip = intro_clip.with_audio(music)
                self.logger.info(f"Intro music added: {intro_music_path}")
            except Exception as e:
                self.logger.warning(f"Failed to add intro music: {e}")
        else:
            self.logger.info("No intro music found (resources/intro_music.mp3)")

        return intro_clip

    def _create_outro_clip(self, config: VideoProjectConfig) -> VideoClip:
        """
        Create outro clip with Korean font support and custom image.

        Args:
            config: Project configuration

        Returns:
            Outro video clip
        """
        # Background: Use same image as intro for consistency
        if config.use_custom_outro and config.outro_image_path and config.outro_image_path.exists():
            # Use custom image
            outro_bg = ImageClip(str(config.outro_image_path))
            self.logger.info(f"Using custom outro image: {config.outro_image_path}")
        else:
            # Try AI ON intro (same as intro for consistency)
            ai_on_intro = Path("resources/ai_on_intro.png")
            if ai_on_intro.exists():
                outro_bg = ImageClip(str(ai_on_intro))
                self.logger.info(f"Using AI ON intro image for outro: {ai_on_intro}")
            else:
                # Try old default
                default_outro = Path("resources/outro_background.png")
                if default_outro.exists():
                    outro_bg = ImageClip(str(default_outro))
                    self.logger.info(f"Using default outro image: {default_outro}")
                else:
                    # Fallback to ColorClip
                    outro_bg = ColorClip(
                        size=(config.width, config.height),
                        color=self._hex_to_rgb(config.secondary_color),
                        duration=config.outro_duration,
                    )
                    self.logger.warning("No outro image found, using ColorClip fallback")

        # Set duration and size
        outro_bg = outro_bg.with_duration(config.outro_duration)
        outro_bg = outro_bg.resized(width=config.width, height=config.height)

        # Add outro text using PIL for precise control
        try:
            from PIL import Image, ImageDraw, ImageFont
            import numpy as np

            # Create transparent overlay
            overlay = Image.new('RGBA', (config.width, config.height), (0, 0, 0, 0))
            draw = ImageDraw.Draw(overlay)

            # Load fonts (macOS compatible)
            try:
                # Try macOS fonts first
                font_large = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 120)
                font_medium = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 42)
                font_small = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 36)
            except:
                try:
                    # Fallback to Linux fonts
                    font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 120)
                    font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 42)
                    font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 36)
                except:
                    # Last resort: default font
                    font_large = ImageFont.load_default()
                    font_medium = ImageFont.load_default()
                    font_small = ImageFont.load_default()

            # Draw "AI ON" in center
            text1 = "AI ON"
            bbox1 = draw.textbbox((0, 0), text1, font=font_large)
            text1_width = bbox1[2] - bbox1[0]
            text1_height = bbox1[3] - bbox1[1]
            x1 = (config.width - text1_width) // 2
            y1 = (config.height - text1_height) // 2 - 80  # Above center

            # Draw stroke
            stroke_width = 4
            for adj_x in range(-stroke_width, stroke_width+1):
                for adj_y in range(-stroke_width, stroke_width+1):
                    draw.text((x1+adj_x, y1+adj_y), text1, font=font_large, fill=(0, 0, 0, 255))
            draw.text((x1, y1), text1, font=font_large, fill=(255, 255, 255, 255))

            # Draw "Thank you for watching!"
            text2 = "Thank you for watching!"
            bbox2 = draw.textbbox((0, 0), text2, font=font_medium)
            text2_width = bbox2[2] - bbox2[0]
            text2_height = bbox2[3] - bbox2[1]
            x2 = (config.width - text2_width) // 2
            y2 = y1 + text1_height + 50

            stroke_width = 2
            for adj_x in range(-stroke_width, stroke_width+1):
                for adj_y in range(-stroke_width, stroke_width+1):
                    draw.text((x2+adj_x, y2+adj_y), text2, font=font_medium, fill=(0, 0, 0, 255))
            draw.text((x2, y2), text2, font=font_medium, fill=(255, 255, 255, 255))

            # Draw subscribe message
            text3 = "Like & Subscribe for more AI & Tech news!"
            bbox3 = draw.textbbox((0, 0), text3, font=font_small)
            text3_width = bbox3[2] - bbox3[0]
            x3 = (config.width - text3_width) // 2
            y3 = y2 + text2_height + 30

            stroke_width = 2
            for adj_x in range(-stroke_width, stroke_width+1):
                for adj_y in range(-stroke_width, stroke_width+1):
                    draw.text((x3+adj_x, y3+adj_y), text3, font=font_small, fill=(0, 0, 0, 255))
            draw.text((x3, y3), text3, font=font_small, fill=(255, 255, 255, 255))

            # Convert to clip
            overlay_array = np.array(overlay)
            text_clip = ImageClip(overlay_array).with_duration(config.outro_duration)
            text_clip = text_clip.with_effects([vfx.FadeIn(0.3)])

            outro_clip = CompositeVideoClip([outro_bg, text_clip])
            self.logger.info("AI ON outro created with PIL text overlay")

        except Exception as e:
            self.logger.warning(f"Failed to add outro text: {e}")
            outro_clip = outro_bg

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
