#!/usr/bin/env python3
"""
Pipeline Integration Test

Tests complete automated pipeline:
1. News collection from multiple sources
2. AI content generation
3. Video production
4. Result reporting

Usage:
    python test_pipeline.py
    python test_pipeline.py --limit 2  # Limit to 2 news articles
"""

import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.automation import PipelineConfig, create_pipeline
from src.core.logging import get_logger

logger = get_logger(__name__)


def print_section(title: str):
    """Print section header."""
    print("\n" + "=" * 70)
    print(title.center(70))
    print("=" * 70 + "\n")


def test_pipeline(news_limit: int = 2):
    """
    Test complete pipeline.

    Args:
        news_limit: Number of news articles to process
    """
    print_section("Tech News Digest - Pipeline Test")

    # Create pipeline config
    config = PipelineConfig(
        news_limit=news_limit,
        max_age_hours=48,
        sources=["techcrunch", "theverge"],
        segment_duration=30,  # Short segments for testing
        image_quality="standard",
        tts_voice="alloy",
        show_intro=True,
        show_outro=True,
    )

    print(f"Configuration:")
    print(f"  News limit: {config.news_limit}")
    print(f"  Max age: {config.max_age_hours}h")
    print(f"  Sources: {', '.join(config.sources)}")
    print(f"  Segment duration: {config.segment_duration}s")

    # Create and run pipeline
    print_section("Running Pipeline")
    print("This may take several minutes...")
    print("Fetching news → Generating AI content → Creating video\n")

    pipeline = create_pipeline(config)
    result = pipeline.run()

    # Display results
    print_section("Pipeline Results")

    if result.success:
        print("✓ Pipeline completed successfully!\n")

        print("[Video Info]")
        print(f"  Project ID: {result.project_id}")
        print(f"  Video Path: {result.video_path}")
        if result.video_path and result.video_path.exists():
            print(f"  File Size: {result.video_path.stat().st_size / 1024 / 1024:.2f} MB")
        print(f"  Duration: {result.total_duration:.1f}s")
        print(f"  News Count: {result.news_count}")

        print(f"\n[Cost]")
        print(f"  Total: ${result.total_cost:.4f}")
        print(f"  Per segment: ${result.total_cost / max(result.news_count, 1):.4f}")

        print(f"\n[Performance]")
        print(f"  Execution time: {result.execution_time:.1f}s ({result.execution_time / 60:.1f}m)")

        return True

    else:
        print("✗ Pipeline failed!\n")

        print("[Errors]")
        for error in result.errors:
            print(f"  - {error}")

        print(f"\n[Partial Results]")
        print(f"  News Count: {result.news_count}")
        print(f"  Execution time: {result.execution_time:.1f}s")

        return False


def main():
    """Run pipeline test."""
    parser = argparse.ArgumentParser(description="Pipeline Integration Test")
    parser.add_argument(
        "--limit",
        type=int,
        default=2,
        help="Number of news articles to process (default: 2)",
    )
    args = parser.parse_args()

    try:
        print("\n⚠️  WARNING: This test will:")
        print(f"- Fetch {args.limit} news articles from TechCrunch and The Verge")
        print("- Generate AI content (Script + Image + Audio)")
        print("- Create a complete video")
        print("- Consume OpenAI API credits (~$0.05-0.10)")
        print("- Take several minutes to complete")

        response = input("\nContinue? (y/n): ")
        if response.lower() != 'y':
            print("Test cancelled")
            return

        success = test_pipeline(news_limit=args.limit)

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
