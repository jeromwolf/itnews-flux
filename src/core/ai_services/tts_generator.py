"""
OpenAI TTS Generator for Tech News Digest.

Generates natural-sounding speech with:
- Multiple voice options
- Adjustable speed
- High quality audio
- Automatic caching
"""

import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional

from src.core.ai_services.base import BaseAIService, GenerationError
from src.core.ai_services.models import GeneratedAudio, TTSVoice
from src.core.logging import get_logger, log_execution_time

logger = get_logger(__name__)


class TTSGenerator(BaseAIService):
    """
    OpenAI TTS generator for news narration.

    Generates professional voice narration optimized for:
    - Clear pronunciation
    - Natural pacing
    - Professional tone
    """

    def __init__(self, output_dir: Optional[Path] = None, **kwargs):
        """
        Initialize TTS generator.

        Args:
            output_dir: Directory for generated audio files
        """
        super().__init__(**kwargs)
        self.model = self.settings.openai.tts_model
        self.output_dir = output_dir or Path("output/audio")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Pricing (OpenAI TTS as of 2025)
        # TTS-1: $15.00 per 1M characters
        # TTS-1-HD: $30.00 per 1M characters
        self.price_standard = 15.00 / 1_000_000
        self.price_hd = 30.00 / 1_000_000

    @log_execution_time(logger)
    def generate(
        self,
        text: str,
        voice: TTSVoice = TTSVoice.ALLOY,
        speed: float = 1.0,
        use_hd: bool = False,
    ) -> GeneratedAudio:
        """
        Generate speech from text.

        Args:
            text: Text to convert to speech
            voice: Voice to use
            speed: Speech speed (0.25-4.0)
            use_hd: Use HD model (better quality, 2x cost)

        Returns:
            Generated audio

        Raises:
            GenerationError: If generation fails
        """
        if not text or not text.strip():
            raise GenerationError("Text cannot be empty")

        if not (0.25 <= speed <= 4.0):
            raise ValueError("Speed must be between 0.25 and 4.0")

        self.logger.info(
            f"Generating audio: {len(text)} chars, "
            f"voice={voice.value}, speed={speed}, hd={use_hd}"
        )

        # Check cache
        cache_key = f"{hashlib.md5(text.encode()).hexdigest()}_{voice.value}_{speed}_{use_hd}"
        cached_path = self._get_cache_path(cache_key, "mp3")

        if cached_path.exists():
            self.logger.info(f"Using cached audio: {cached_path.name}")
            duration = self._estimate_duration(text, speed)
            return GeneratedAudio(
                local_path=cached_path,
                duration=duration,
                format="mp3",
                text=text,
                voice=voice,
                speed=speed,
                model="tts-1-hd" if use_hd else "tts-1",
                character_count=len(text),
                total_cost=0.0,  # Cached, no cost
            )

        # Generate audio
        try:
            model = "tts-1-hd" if use_hd else "tts-1"

            response = self._call_api_with_retry(
                self.client.audio.speech.create,
                model=model,
                voice=voice.value,
                input=text,
                speed=speed,
            )

            # Save audio file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{voice.value}.mp3"
            local_path = self.output_dir / filename

            # Write audio data
            with open(local_path, "wb") as f:
                for chunk in response.iter_bytes():
                    f.write(chunk)

            # Also save to cache
            if self.enable_cache:
                import shutil
                shutil.copy(local_path, cached_path)

            # Calculate duration and cost
            duration = self._estimate_duration(text, speed)
            character_count = len(text)
            price_per_char = self.price_hd if use_hd else self.price_standard
            cost = character_count * price_per_char
            self.total_cost += cost

            # Create audio object
            audio = GeneratedAudio(
                local_path=local_path,
                duration=duration,
                format="mp3",
                text=text,
                voice=voice,
                speed=speed,
                model=model,
                character_count=character_count,
                total_cost=cost,
            )

            self.logger.info(
                f"Audio generated: {local_path.name}, "
                f"{duration:.1f}s, ${cost:.4f}"
            )

            return audio

        except Exception as e:
            self.logger.error(f"TTS generation failed: {e}", exc_info=True)
            raise GenerationError(f"TTS generation failed: {e}") from e

    def _estimate_duration(self, text: str, speed: float) -> float:
        """
        Estimate audio duration based on text length and speed.

        Args:
            text: Input text
            speed: Speech speed

        Returns:
            Estimated duration in seconds
        """
        # Average speaking rate: ~150 words per minute (2.5 words per second)
        # Adjusted by speed factor
        word_count = len(text.split())
        base_duration = word_count / 2.5  # seconds
        adjusted_duration = base_duration / speed
        return adjusted_duration

    def generate_batch(
        self,
        texts: list[str],
        voice: TTSVoice = TTSVoice.ALLOY,
        speed: float = 1.0,
        use_hd: bool = False,
    ) -> list[GeneratedAudio]:
        """
        Generate audio for multiple texts.

        Args:
            texts: List of texts
            voice: Voice to use
            speed: Speech speed
            use_hd: Use HD model

        Returns:
            List of generated audio files
        """
        self.logger.info(f"Generating {len(texts)} audio files in batch")

        audio_files = []
        for i, text in enumerate(texts, 1):
            try:
                self.logger.info(
                    f"Processing {i}/{len(texts)}: {len(text)} chars..."
                )
                audio = self.generate(text, voice, speed, use_hd)
                audio_files.append(audio)

            except GenerationError as e:
                self.logger.error(f"Failed to generate audio {i}: {e}")
                # Continue with next text
                continue

        self.logger.info(
            f"Batch generation complete: {len(audio_files)}/{len(texts)} successful, "
            f"total cost: ${self.total_cost:.4f}"
        )

        return audio_files

    def get_available_voices(self) -> dict[str, str]:
        """
        Get available voice options with descriptions.

        Returns:
            Dictionary of voice names and descriptions
        """
        return {
            TTSVoice.ALLOY.value: "Neutral, balanced voice (recommended for news)",
            TTSVoice.ECHO.value: "Male voice, clear pronunciation",
            TTSVoice.FABLE.value: "British accent, professional",
            TTSVoice.ONYX.value: "Deep male voice, authoritative",
            TTSVoice.NOVA.value: "Female voice, warm and engaging",
            TTSVoice.SHIMMER.value: "Female voice, soft and friendly",
        }

    def test_voices(
        self,
        text: str = "Good morning! This is a test of the text-to-speech system.",
    ) -> list[GeneratedAudio]:
        """
        Generate test audio for all available voices.

        Args:
            text: Test text

        Returns:
            List of generated audio files, one per voice
        """
        self.logger.info("Generating voice samples for all voices")

        samples = []
        for voice in TTSVoice:
            try:
                audio = self.generate(text, voice=voice, speed=1.0)
                samples.append(audio)
                self.logger.info(f"Generated sample for {voice.value}")

            except Exception as e:
                self.logger.error(f"Failed to generate sample for {voice.value}: {e}")

        return samples


def create_tts_generator(output_dir: Optional[Path] = None, **kwargs) -> TTSGenerator:
    """
    Create TTS generator instance.

    Args:
        output_dir: Output directory for audio files

    Returns:
        TTSGenerator instance

    Example:
        >>> generator = create_tts_generator()
        >>> audio = generator.generate("Hello, world!")
        >>> print(f"Audio saved to: {audio.local_path}")
    """
    return TTSGenerator(output_dir=output_dir, **kwargs)
