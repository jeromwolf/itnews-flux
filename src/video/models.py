"""
Video production data models for Tech News Digest.

Provides Pydantic models for:
- Video segments
- Video projects
- Layout configurations
- Rendering settings
"""

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field

from src.core.ai_services.models import GeneratedAudio, GeneratedImage, GeneratedScript


class VideoResolution(str, Enum):
    """Video resolution presets."""

    HD_720P = "1280x720"  # 16:9 HD
    FULL_HD = "1920x1080"  # 16:9 Full HD
    QHD = "2560x1440"  # 16:9 QHD
    UHD_4K = "3840x2160"  # 16:9 4K


class VideoFormat(str, Enum):
    """Video output format."""

    MP4 = "mp4"  # H.264, most compatible
    MOV = "mov"  # QuickTime
    AVI = "avi"  # Uncompressed


class LayoutStyle(str, Enum):
    """Layout style for video."""

    NEWS_ANCHOR = "news_anchor"  # Professional news style
    SPLIT_SCREEN = "split_screen"  # Side-by-side layout
    FULL_SCREEN = "full_screen"  # Full screen image


class TextPosition(str, Enum):
    """Text position in video."""

    TOP = "top"
    BOTTOM = "bottom"
    LEFT = "left"
    RIGHT = "right"
    CENTER = "center"
    LOWER_THIRD = "lower_third"  # Standard news lower third


class VideoSegment(BaseModel):
    """
    Single video segment (one news story).

    Represents a complete news segment with:
    - Generated content (script, image, audio)
    - Timing information
    - Layout settings
    """

    # Segment identification
    segment_id: str = Field(..., description="Unique segment ID")
    title: str = Field(..., description="News title")
    segment_number: int = Field(..., description="Segment number in video (1-based)")

    # Generated content
    script: GeneratedScript = Field(..., description="Generated script")
    image: GeneratedImage = Field(..., description="Generated image")
    audio: GeneratedAudio = Field(..., description="Generated audio")

    # Timing
    start_time: float = Field(0.0, description="Start time in video (seconds)")
    duration: float = Field(..., description="Duration (seconds)")
    end_time: float = Field(0.0, description="End time in video (seconds)")

    # Layout settings
    layout_style: LayoutStyle = Field(
        LayoutStyle.NEWS_ANCHOR, description="Layout style"
    )
    show_lower_third: bool = Field(True, description="Show lower third subtitle")
    transition_duration: float = Field(0.5, description="Transition duration (seconds)")

    created_at: datetime = Field(default_factory=datetime.utcnow)

    def calculate_end_time(self) -> None:
        """Calculate end time based on start time and duration."""
        self.end_time = self.start_time + self.duration

    @property
    def has_all_content(self) -> bool:
        """Check if all required content exists."""
        return (
            self.script is not None
            and self.image is not None
            and self.image.exists
            and self.audio is not None
            and self.audio.exists
        )


class LowerThirdConfig(BaseModel):
    """Configuration for lower third subtitle bar."""

    # Content
    primary_text: str = Field(..., description="Primary text (English)")
    secondary_text: Optional[str] = Field(None, description="Secondary text (Korean)")

    # Position and size
    position: TextPosition = Field(
        TextPosition.LOWER_THIRD, description="Position in frame"
    )
    height_ratio: float = Field(0.2, ge=0.1, le=0.4, description="Height as ratio of video height")

    # Styling
    background_color: str = Field("#1a1a1a", description="Background color (hex)")
    background_opacity: float = Field(0.85, ge=0.0, le=1.0, description="Background opacity")
    primary_font_size: int = Field(48, description="Primary text font size")
    secondary_font_size: int = Field(32, description="Secondary text font size")
    text_color: str = Field("#ffffff", description="Text color (hex)")
    padding: int = Field(20, description="Padding in pixels")

    # Animation
    fade_in_duration: float = Field(0.3, description="Fade in duration (seconds)")
    fade_out_duration: float = Field(0.3, description="Fade out duration (seconds)")
    display_duration: float = Field(0.0, description="Display duration (0 = full segment)")


class VideoProjectConfig(BaseModel):
    """Configuration for video project."""

    # Video settings
    resolution: VideoResolution = Field(
        VideoResolution.FULL_HD, description="Video resolution"
    )
    fps: int = Field(30, ge=24, le=60, description="Frames per second")
    format: VideoFormat = Field(VideoFormat.MP4, description="Output format")
    codec: str = Field("libx264", description="Video codec")
    audio_codec: str = Field("aac", description="Audio codec")
    bitrate: str = Field("5000k", description="Video bitrate")

    # Project info
    title: str = Field("Tech News Digest", description="Project title")
    date: datetime = Field(default_factory=datetime.utcnow, description="Production date")

    # Layout defaults
    default_layout: LayoutStyle = Field(
        LayoutStyle.NEWS_ANCHOR, description="Default layout style"
    )
    show_intro: bool = Field(True, description="Show intro sequence")
    show_outro: bool = Field(True, description="Show outro sequence")
    intro_duration: float = Field(3.0, description="Intro duration (seconds)")
    outro_duration: float = Field(3.0, description="Outro duration (seconds)")

    # Colors and branding
    primary_color: str = Field("#0066cc", description="Primary brand color")
    secondary_color: str = Field("#003d7a", description="Secondary brand color")
    background_color: str = Field("#ffffff", description="Background color")

    @property
    def width(self) -> int:
        """Get video width in pixels."""
        return int(self.resolution.value.split("x")[0])

    @property
    def height(self) -> int:
        """Get video height in pixels."""
        return int(self.resolution.value.split("x")[1])

    @property
    def aspect_ratio(self) -> float:
        """Get aspect ratio."""
        return self.width / self.height


class VideoProject(BaseModel):
    """
    Complete video project.

    Represents a full video with:
    - Multiple news segments
    - Configuration
    - Rendering state
    """

    # Project identification
    project_id: str = Field(..., description="Unique project ID")
    title: str = Field(..., description="Project title")

    # Configuration
    config: VideoProjectConfig = Field(
        default_factory=VideoProjectConfig, description="Project configuration"
    )

    # Segments
    segments: list[VideoSegment] = Field(
        default_factory=list, description="Video segments"
    )

    # Output
    output_path: Optional[Path] = Field(None, description="Output video file path")

    # Rendering state
    is_rendered: bool = Field(False, description="Whether video has been rendered")
    render_progress: float = Field(0.0, ge=0.0, le=1.0, description="Render progress (0-1)")
    render_time: float = Field(0.0, description="Total render time (seconds)")

    created_at: datetime = Field(default_factory=datetime.utcnow)
    rendered_at: Optional[datetime] = Field(None, description="Render completion time")

    @property
    def total_duration(self) -> float:
        """Calculate total video duration."""
        duration = 0.0

        # Add intro
        if self.config.show_intro:
            duration += self.config.intro_duration

        # Add segments
        for segment in self.segments:
            duration += segment.duration

        # Add outro
        if self.config.show_outro:
            duration += self.config.outro_duration

        return duration

    @property
    def segment_count(self) -> int:
        """Get number of segments."""
        return len(self.segments)

    @property
    def has_all_content(self) -> bool:
        """Check if all segments have required content."""
        return all(segment.has_all_content for segment in self.segments)

    def add_segment(self, segment: VideoSegment) -> None:
        """
        Add a video segment.

        Args:
            segment: Video segment to add
        """
        # Calculate start time based on previous segments
        if self.segments:
            last_segment = self.segments[-1]
            segment.start_time = last_segment.end_time
        else:
            # First segment starts after intro
            segment.start_time = (
                self.config.intro_duration if self.config.show_intro else 0.0
            )

        # Calculate end time
        segment.calculate_end_time()

        # Add to project
        self.segments.append(segment)

    def get_segment(self, segment_number: int) -> Optional[VideoSegment]:
        """
        Get segment by number.

        Args:
            segment_number: Segment number (1-based)

        Returns:
            Video segment or None
        """
        for segment in self.segments:
            if segment.segment_number == segment_number:
                return segment
        return None

    def validate_project(self) -> dict:
        """
        Validate project is ready for rendering.

        Returns:
            Validation result dictionary
        """
        errors = []
        warnings = []

        # Check segments
        if not self.segments:
            errors.append("No segments in project")

        # Check content
        for segment in self.segments:
            if not segment.has_all_content:
                errors.append(
                    f"Segment {segment.segment_number} missing required content"
                )

        # Check total duration
        total_duration = self.total_duration
        if total_duration < 10:
            warnings.append(f"Video very short: {total_duration:.1f}s")
        elif total_duration > 600:
            warnings.append(f"Video very long: {total_duration:.1f}s (10+ minutes)")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "segment_count": self.segment_count,
            "total_duration": total_duration,
            "has_all_content": self.has_all_content,
        }
