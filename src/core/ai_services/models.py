"""
AI Services data models for Tech News Digest.

Provides Pydantic models for:
- Generated scripts (GPT-4o)
- Generated images (DALL-E 3)
- Generated audio (TTS)
"""

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl


class ScriptStyle(str, Enum):
    """Script style for news anchor."""

    PROFESSIONAL = "professional"  # Professional news anchor
    CASUAL = "casual"  # Casual conversational
    EDUCATIONAL = "educational"  # Educational focus


class ImageStyle(str, Enum):
    """Image generation style."""

    NATURAL = "natural"  # Natural photo style
    VIVID = "vivid"  # Vivid and dramatic


class TTSVoice(str, Enum):
    """Available TTS voices."""

    ALLOY = "alloy"  # Neutral, balanced
    ECHO = "echo"  # Male voice
    FABLE = "fable"  # British accent
    ONYX = "onyx"  # Deep male voice
    NOVA = "nova"  # Female voice
    SHIMMER = "shimmer"  # Female, soft


class GeneratedScript(BaseModel):
    """Generated news script from GPT-4o."""

    # Content
    english_script: str = Field(..., description="English news script")
    korean_translation: str = Field(..., description="Korean translation")

    # Vocabulary
    key_vocabulary: list[dict[str, str]] = Field(
        default_factory=list,
        description="Key vocabulary with translations",
    )

    # Metadata
    word_count: int = Field(..., description="Word count")
    estimated_duration: float = Field(..., description="Estimated duration (seconds)")
    style: ScriptStyle = Field(
        ScriptStyle.PROFESSIONAL, description="Script style"
    )

    # Generation info
    model: str = Field("gpt-4o", description="Model used")
    prompt_tokens: int = Field(0, description="Prompt tokens used")
    completion_tokens: int = Field(0, description="Completion tokens used")
    total_cost: float = Field(0.0, description="Total cost (USD)")

    created_at: datetime = Field(default_factory=datetime.utcnow)

    @property
    def formatted_vocabulary(self) -> str:
        """
        Format vocabulary for display.

        Returns:
            Formatted vocabulary string
        """
        if not self.key_vocabulary:
            return ""

        lines = []
        for item in self.key_vocabulary:
            word = item.get("word", "")
            meaning = item.get("meaning", "")
            example = item.get("example", "")

            lines.append(f"• {word}: {meaning}")
            if example:
                lines.append(f"  Example: {example}")

        return "\n".join(lines)


class GeneratedImage(BaseModel):
    """Generated image from DALL-E 3."""

    # Image info
    url: Optional[HttpUrl] = Field(None, description="Image URL (temporary)")
    local_path: Optional[Path] = Field(None, description="Local file path")
    width: int = Field(1792, description="Image width")
    height: int = Field(1024, description="Image height")

    # Generation info
    prompt: str = Field(..., description="Image generation prompt")
    revised_prompt: Optional[str] = Field(
        None, description="Revised prompt by DALL-E"
    )
    style: ImageStyle = Field(ImageStyle.VIVID, description="Image style")
    quality: str = Field("hd", description="Image quality (standard/hd)")

    model: str = Field("dall-e-3", description="Model used")
    total_cost: float = Field(0.0, description="Total cost (USD)")

    created_at: datetime = Field(default_factory=datetime.utcnow)

    @property
    def size(self) -> str:
        """Get image size string."""
        return f"{self.width}x{self.height}"

    @property
    def exists(self) -> bool:
        """Check if local file exists."""
        if not self.local_path:
            return False
        return self.local_path.exists()


class GeneratedAudio(BaseModel):
    """Generated audio from OpenAI TTS."""

    # Audio info
    local_path: Path = Field(..., description="Local audio file path")
    duration: float = Field(..., description="Audio duration (seconds)")
    format: str = Field("mp3", description="Audio format")
    sample_rate: int = Field(24000, description="Sample rate (Hz)")

    # Generation info
    text: str = Field(..., description="Input text")
    voice: TTSVoice = Field(TTSVoice.ALLOY, description="Voice used")
    speed: float = Field(1.0, ge=0.25, le=4.0, description="Speech speed")

    model: str = Field("tts-1", description="Model used (tts-1/tts-1-hd)")
    character_count: int = Field(..., description="Character count")
    total_cost: float = Field(0.0, description="Total cost (USD)")

    created_at: datetime = Field(default_factory=datetime.utcnow)

    @property
    def exists(self) -> bool:
        """Check if local file exists."""
        return self.local_path.exists()

    @property
    def file_size_mb(self) -> float:
        """Get file size in MB."""
        if not self.exists:
            return 0.0
        return self.local_path.stat().st_size / (1024 * 1024)


class NewsSegment(BaseModel):
    """Complete news segment with all generated content."""

    # Source news
    news_id: str = Field(..., description="News article ID")
    news_title: str = Field(..., description="News title")
    news_url: HttpUrl = Field(..., description="News URL")

    # Generated content
    script: Optional[GeneratedScript] = Field(None, description="Generated script")
    image: Optional[GeneratedImage] = Field(None, description="Generated image")
    audio: Optional[GeneratedAudio] = Field(None, description="Generated audio")

    # Metadata
    segment_number: int = Field(..., description="Segment number in video")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @property
    def is_complete(self) -> bool:
        """Check if all content is generated."""
        return (
            self.script is not None
            and self.image is not None
            and self.audio is not None
        )

    @property
    def total_cost(self) -> float:
        """Calculate total cost for this segment."""
        cost = 0.0
        if self.script:
            cost += self.script.total_cost
        if self.image:
            cost += self.image.total_cost
        if self.audio:
            cost += self.audio.total_cost
        return cost

    def validate_files(self) -> bool:
        """
        Validate all generated files exist.

        Returns:
            True if all files exist
        """
        if self.image and not self.image.exists:
            return False
        if self.audio and not self.audio.exists:
            return False
        return True
