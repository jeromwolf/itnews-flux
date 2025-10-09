"""
AI Services module for Tech News Digest.

Provides AI-powered content generation services:
- GPT-4o: News script generation
- DALL-E 3: Image generation
- TTS: Voice narration generation
"""

from .base import AIServiceError, BaseAIService, GenerationError, RateLimitError
from .image_generator import ImageGenerator, create_image_generator
from .models import (
    GeneratedAudio,
    GeneratedImage,
    GeneratedScript,
    ImageStyle,
    NewsSegment,
    ScriptStyle,
    TTSVoice,
)
from .script_generator import ScriptGenerator, create_script_generator
from .tts_generator import TTSGenerator, create_tts_generator

__all__ = [
    # Base classes
    "BaseAIService",
    "AIServiceError",
    "GenerationError",
    "RateLimitError",
    # Generators
    "ScriptGenerator",
    "ImageGenerator",
    "TTSGenerator",
    # Factory functions
    "create_script_generator",
    "create_image_generator",
    "create_tts_generator",
    # Models
    "GeneratedScript",
    "GeneratedImage",
    "GeneratedAudio",
    "NewsSegment",
    # Enums
    "ScriptStyle",
    "ImageStyle",
    "TTSVoice",
]
