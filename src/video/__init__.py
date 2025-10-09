"""
Video production module for Tech News Digest.

Provides video composition and layout tools:
- Video models and configurations
- Layout components (Lower Third)
- Video composition (MoviePy)
"""

from .composition.video_composer import VideoComposer, create_video_composer
from .layout.lower_third import LowerThirdGenerator, create_lower_third_generator
from .models import (
    LayoutStyle,
    LowerThirdConfig,
    TextPosition,
    VideoFormat,
    VideoProject,
    VideoProjectConfig,
    VideoResolution,
    VideoSegment,
)

__all__ = [
    # Models
    "VideoSegment",
    "VideoProject",
    "VideoProjectConfig",
    "LowerThirdConfig",
    # Enums
    "VideoResolution",
    "VideoFormat",
    "LayoutStyle",
    "TextPosition",
    # Components
    "LowerThirdGenerator",
    "create_lower_third_generator",
    # Composer
    "VideoComposer",
    "create_video_composer",
]
