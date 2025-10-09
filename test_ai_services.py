#!/usr/bin/env python3
"""
AI Services Integration Test

Tests all AI services:
- ScriptGenerator (GPT-4o)
- ImageGenerator (DALL-E 3)
- TTSGenerator (OpenAI TTS)

Usage:
    python test_ai_services.py
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.ai_services import (
    create_image_generator,
    create_script_generator,
    create_tts_generator,
)
from src.core.config import get_settings
from src.core.logging import get_logger
from src.news.crawler.sources.techcrunch import create_techcrunch_crawler

logger = get_logger(__name__)


def print_section(title: str):
    """Print section header."""
    print("\n" + "=" * 70)
    print(title.center(70))
    print("=" * 70 + "\n")


def test_script_generation():
    """Test GPT-4o script generation."""
    print_section("Testing GPT-4o Script Generation")

    # Get a news article
    print("Fetching news article...")
    crawler = create_techcrunch_crawler()
    news_collection = crawler.fetch_news(limit=1, max_age_hours=48)

    if news_collection.total == 0:
        print("❌ No news articles found")
        return None

    news = news_collection.articles[0]
    print(f"✓ News: {news.title}\n")

    # Generate script
    print("Generating script...")
    generator = create_script_generator()

    try:
        script = generator.generate(news, target_duration=60)

        print(f"✓ Script generated!")
        print(f"\n[English Script]")
        print("-" * 70)
        print(script.english_script)

        print(f"\n[Korean Translation]")
        print("-" * 70)
        print(script.korean_translation)

        if script.key_vocabulary:
            print(f"\n[Key Vocabulary]")
            print("-" * 70)
            for item in script.key_vocabulary:
                print(
                    f"• {item['word']}: {item['meaning']}"
                )
                if 'example' in item:
                    print(f"  Example: {item['example']}")

        print(f"\n[Statistics]")
        print("-" * 70)
        print(f"Words: {script.word_count}")
        print(f"Est. Duration: {script.estimated_duration:.0f}s")
        print(f"Tokens: {script.prompt_tokens} + {script.completion_tokens}")
        print(f"Cost: ${script.total_cost:.4f}")

        return script

    except Exception as e:
        print(f"❌ Script generation failed: {e}")
        logger.error(f"Script generation failed: {e}", exc_info=True)
        return None


def test_image_generation(news=None):
    """Test DALL-E 3 image generation."""
    print_section("Testing DALL-E 3 Image Generation")

    # Get a news article if not provided
    if not news:
        print("Fetching news article...")
        crawler = create_techcrunch_crawler()
        news_collection = crawler.fetch_news(limit=1, max_age_hours=48)

        if news_collection.total == 0:
            print("❌ No news articles found")
            return None

        news = news_collection.articles[0]

    print(f"✓ News: {news.title}\n")

    # Generate image
    print("Generating image...")
    generator = create_image_generator()

    try:
        image = generator.generate(news, quality="standard")  # Use standard for testing

        print(f"✓ Image generated!")
        print(f"\n[Image Info]")
        print("-" * 70)
        print(f"Size: {image.size}")
        print(f"Path: {image.local_path}")
        print(f"Exists: {image.exists}")
        print(f"Style: {image.style.value}")
        print(f"Quality: {image.quality}")

        print(f"\n[Prompt]")
        print("-" * 70)
        print(image.prompt)

        if image.revised_prompt:
            print(f"\n[Revised Prompt]")
            print("-" * 70)
            print(image.revised_prompt)

        print(f"\n[Cost]")
        print("-" * 70)
        print(f"${image.total_cost:.3f}")

        return image

    except Exception as e:
        print(f"❌ Image generation failed: {e}")
        logger.error(f"Image generation failed: {e}", exc_info=True)
        return None


def test_tts_generation(script=None):
    """Test OpenAI TTS generation."""
    print_section("Testing OpenAI TTS Generation")

    # Use provided script or sample text
    if script:
        text = script.english_script[:500]  # Limit for testing
        print(f"Using generated script (first 500 chars)")
    else:
        text = "Good morning, tech enthusiasts! Today we're looking at the latest developments in artificial intelligence. This is just a test of the text-to-speech system."
        print("Using sample text")

    print(f"\n[Text]")
    print("-" * 70)
    print(f"{text[:200]}..." if len(text) > 200 else text)

    # Generate audio
    print("\nGenerating audio...")
    generator = create_tts_generator()

    try:
        audio = generator.generate(text, speed=1.0)

        print(f"✓ Audio generated!")
        print(f"\n[Audio Info]")
        print("-" * 70)
        print(f"Duration: {audio.duration:.1f}s")
        print(f"Path: {audio.local_path}")
        print(f"Exists: {audio.exists}")
        print(f"Size: {audio.file_size_mb:.2f} MB")
        print(f"Voice: {audio.voice.value}")
        print(f"Speed: {audio.speed}x")
        print(f"Format: {audio.format}")

        print(f"\n[Cost]")
        print("-" * 70)
        print(f"Characters: {audio.character_count}")
        print(f"Cost: ${audio.total_cost:.4f}")

        return audio

    except Exception as e:
        print(f"❌ TTS generation failed: {e}")
        logger.error(f"TTS generation failed: {e}", exc_info=True)
        return None


def main():
    """Run all AI service tests."""
    print_section("Tech News Digest - AI Services Test")

    settings = get_settings()
    print(f"Environment: {settings.app_env.value}")
    print(f"OpenAI Model: {settings.openai.gpt_model}")
    print(f"Image Model: {settings.openai.image_model}")
    print(f"TTS Model: {settings.openai.tts_model}")

    # Test 1: Script Generation
    script = test_script_generation()

    # Test 2: Image Generation (reuse the same news if available)
    if script:
        # Get the news article from crawler again
        crawler = create_techcrunch_crawler()
        news_collection = crawler.fetch_news(limit=1, max_age_hours=48)
        news = news_collection.articles[0] if news_collection.total > 0 else None
        image = test_image_generation(news)
    else:
        image = test_image_generation()

    # Test 3: TTS Generation (use generated script if available)
    audio = test_tts_generation(script)

    # Summary
    print_section("Test Summary")

    results = []
    results.append(("Script Generation", "✓" if script else "✗"))
    results.append(("Image Generation", "✓" if image else "✗"))
    results.append(("TTS Generation", "✓" if audio else "✗"))

    for test_name, result in results:
        print(f"{result} {test_name}")

    # Total cost
    total_cost = 0.0
    if script:
        total_cost += script.total_cost
    if image:
        total_cost += image.total_cost
    if audio:
        total_cost += audio.total_cost

    print(f"\nTotal Cost: ${total_cost:.4f}")

    print_section("✓ TEST COMPLETED")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
