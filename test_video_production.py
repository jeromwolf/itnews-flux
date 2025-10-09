#!/usr/bin/env python3
"""
Video Production Integration Test

Tests complete video production pipeline:
1. Load AI-generated content (from Phase 2)
2. Create video project
3. Add video segments
4. Compose video
5. Validate output

Usage:
    python test_video_production.py
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.ai_services import (
    GeneratedAudio,
    GeneratedImage,
    GeneratedScript,
    create_image_generator,
    create_script_generator,
    create_tts_generator,
)
from src.core.config import get_settings
from src.core.logging import get_logger
from src.news.crawler.sources.techcrunch import create_techcrunch_crawler
from src.video import (
    VideoProject,
    VideoProjectConfig,
    VideoSegment,
    create_video_composer,
)

logger = get_logger(__name__)


def print_section(title: str):
    """Print section header."""
    print("\n" + "=" * 70)
    print(title.center(70))
    print("=" * 70 + "\n")


def generate_content_for_news(news):
    """
    Generate all required content for a news article.

    Args:
        news: News article

    Returns:
        Tuple of (script, image, audio)
    """
    print(f"Generating content for: {news.title[:50]}...")

    # Generate script
    script_gen = create_script_generator()
    script = script_gen.generate(news, target_duration=30)  # 30s per segment for testing
    print(f"✓ Script: {script.word_count} words")

    # Generate image
    image_gen = create_image_generator()
    image = image_gen.generate(news, quality="standard")
    print(f"✓ Image: {image.local_path}")

    # Generate audio
    tts_gen = create_tts_generator()
    audio = tts_gen.generate(script.english_script[:500])  # Limit for testing
    print(f"✓ Audio: {audio.duration:.1f}s, {audio.local_path}")

    return script, image, audio


def test_video_production():
    """Test complete video production pipeline."""
    print_section("Tech News Digest - Video Production Test")

    settings = get_settings()
    print(f"Environment: {settings.app_env.value}")

    # Step 1: Get news articles
    print_section("Step 1: Fetching News Articles")
    crawler = create_techcrunch_crawler()
    news_collection = crawler.fetch_news(limit=2, max_age_hours=48)  # 2 articles for testing

    if news_collection.total == 0:
        print("❌ No news articles found")
        return False

    print(f"✓ Fetched {news_collection.total} articles")

    # Step 2: Generate content for each article
    print_section("Step 2: Generating AI Content")

    segments = []
    for i, news in enumerate(news_collection.articles, 1):
        print(f"\n[{i}/{news_collection.total}] {news.title[:60]}...")

        script, image, audio = generate_content_for_news(news)

        # Create video segment
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
        print(f"✓ Segment {i} created")

    # Step 3: Create video project
    print_section("Step 3: Creating Video Project")

    config = VideoProjectConfig(
        title="Tech News Digest - Test Edition",
        show_intro=True,
        show_outro=True,
        intro_duration=2.0,  # Short intro for testing
        outro_duration=2.0,  # Short outro for testing
    )

    project = VideoProject(
        project_id="test_project_001",
        title=config.title,
        config=config,
    )

    # Add segments
    for segment in segments:
        project.add_segment(segment)

    print(f"✓ Project created: {project.title}")
    print(f"  Segments: {project.segment_count}")
    print(f"  Total duration: {project.total_duration:.1f}s")

    # Validate project
    validation = project.validate_project()
    print(f"\n[Validation]")
    print(f"  Valid: {validation['valid']}")
    if validation['errors']:
        print(f"  Errors: {validation['errors']}")
    if validation['warnings']:
        print(f"  Warnings: {validation['warnings']}")

    if not validation['valid']:
        print("\n❌ Project validation failed")
        return False

    # Step 4: Compose video
    print_section("Step 4: Composing Video")

    composer = create_video_composer()

    print("This may take several minutes...")
    print("Rendering video with MoviePy...")

    try:
        video_path = composer.compose_project(project)

        print(f"\n✓ Video created successfully!")
        print(f"\n[Video Info]")
        print(f"  Path: {video_path}")
        print(f"  Size: {video_path.stat().st_size / 1024 / 1024:.2f} MB")
        print(f"  Duration: {project.total_duration:.1f}s")
        print(f"  Segments: {project.segment_count}")

        # Calculate total cost
        total_cost = 0.0
        for segment in project.segments:
            total_cost += segment.script.total_cost
            total_cost += segment.image.total_cost
            total_cost += segment.audio.total_cost

        print(f"\n[Cost]")
        print(f"  Total: ${total_cost:.4f}")
        print(f"  Per segment: ${total_cost / project.segment_count:.4f}")

        return True

    except Exception as e:
        logger.error(f"Video composition failed: {e}", exc_info=True)
        print(f"\n❌ Video composition failed: {e}")
        return False


def test_lower_third_only():
    """Test only lower third generation (quick test)."""
    print_section("Lower Third Component Test")

    from src.video import VideoProjectConfig, create_lower_third_generator

    config = VideoProjectConfig()
    generator = create_lower_third_generator(config)

    # Generate lower third
    image = generator.generate_simple(
        primary_text="Breaking: OpenAI Announces GPT-5",
        secondary_text="속보: OpenAI, GPT-5 발표",
        output_path=Path("output/test_lower_third.png"),
    )

    print(f"✓ Lower third generated")
    print(f"  Size: {image.size}")
    print(f"  Path: output/test_lower_third.png")

    return True


def main():
    """Run video production tests."""
    import argparse

    parser = argparse.ArgumentParser(description="Video Production Test")
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Run quick test (lower third only)",
    )
    args = parser.parse_args()

    try:
        if args.quick:
            success = test_lower_third_only()
        else:
            print("\n⚠️  WARNING: Full video production test will take several minutes")
            print("and will consume OpenAI API credits (~$0.03)")
            response = input("\nContinue? (y/n): ")

            if response.lower() != 'y':
                print("Test cancelled")
                return

            success = test_video_production()

        if success:
            print_section("✓ TEST COMPLETED SUCCESSFULLY")
        else:
            print_section("✗ TEST FAILED")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
