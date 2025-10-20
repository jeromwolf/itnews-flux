#!/usr/bin/env python3
"""
Test script for YouTube Thumbnail Generator.

Tests thumbnail generation with different configurations.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.video.thumbnail_generator import ThumbnailConfig, ThumbnailGenerator
from src.core.logging import get_logger

logger = get_logger(__name__)


def test_thumbnail_generation():
    """Test thumbnail generation with sample news."""
    print("=" * 60)
    print("YouTube Thumbnail Generator Test")
    print("=" * 60)

    # Find a sample AI-generated image from output
    output_dir = Path("output/images")
    if not output_dir.exists():
        print("\n❌ Error: No images found in output/images")
        print("   Please run test_ai_services.py first to generate images")
        return

    # Get first image
    images = list(output_dir.glob("*.png"))
    if not images:
        print("\n❌ Error: No PNG images found in output/images")
        return

    sample_image = images[0]
    print(f"\n✅ Using sample image: {sample_image.name}")

    # Test 1: Default configuration
    print("\n" + "=" * 60)
    print("Test 1: Default Configuration")
    print("=" * 60)

    generator = ThumbnailGenerator()

    thumbnail_path = generator.generate(
        title="OpenAI Launches GPT-5 with Revolutionary Multimodal Capabilities",
        background_image_path=sample_image,
        subtitle="Breaking Tech News • Today",
    )

    print(f"\n✅ Thumbnail generated: {thumbnail_path}")
    print(f"   Size: {thumbnail_path.stat().st_size / 1024:.1f} KB")

    # Test 2: Custom branding
    print("\n" + "=" * 60)
    print("Test 2: Custom Branding")
    print("=" * 60)

    custom_config = ThumbnailConfig(
        brand_text="TECH DIGEST",  # Custom brand text
        brand_font_size=42,
        text_box_color="#0066FF",  # Brighter blue
        background_opacity=0.4,  # Darker background
    )

    generator2 = ThumbnailGenerator(config=custom_config)

    thumbnail_path2 = generator2.generate(
        title="Apple Vision Pro 2 Release Date Confirmed for 2025",
        background_image_path=sample_image,
        subtitle="Hardware • Apple",
        use_cache=False,  # Don't use cache for testing
    )

    print(f"\n✅ Thumbnail generated: {thumbnail_path2}")
    print(f"   Size: {thumbnail_path2.stat().st_size / 1024:.1f} KB")

    # Test 3: Long title (text wrapping)
    print("\n" + "=" * 60)
    print("Test 3: Long Title (Text Wrapping)")
    print("=" * 60)

    thumbnail_path3 = generator.generate(
        title="Artificial Intelligence Research Team at Stanford University Develops New Algorithm That Can Predict Stock Market Trends with 95% Accuracy",
        background_image_path=sample_image,
        subtitle="AI & ML • Research",
        use_cache=False,
    )

    print(f"\n✅ Thumbnail generated: {thumbnail_path3}")
    print(f"   Size: {thumbnail_path3.stat().st_size / 1024:.1f} KB")

    # Test 4: Multiple images (if available)
    if len(images) >= 3:
        print("\n" + "=" * 60)
        print("Test 4: Multiple Thumbnails (Batch Generation)")
        print("=" * 60)

        titles = [
            "Meta Unveils Llama 3 with 405 Billion Parameters",
            "Tesla Bot Achieves Human-Level Dexterity in Factory Tests",
            "Quantum Computing Breakthrough Solves Previously Impossible Problem",
        ]

        for i, title in enumerate(titles):
            img = images[min(i, len(images) - 1)]
            thumb = generator.generate(
                title=title,
                background_image_path=img,
                subtitle=f"News #{i+1}",
                use_cache=False,
            )
            print(f"   ✅ Generated: {thumb.name}")

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    thumbnails_dir = Path("output/thumbnails")
    all_thumbnails = list(thumbnails_dir.glob("*.jpg"))

    print(f"\n✅ Total thumbnails generated: {len(all_thumbnails)}")
    print(f"   Location: {thumbnails_dir}")
    print(f"\n   Total size: {sum(t.stat().st_size for t in all_thumbnails) / 1024:.1f} KB")

    print("\n💡 Next steps:")
    print("   1. Open output/thumbnails/ to view generated thumbnails")
    print("   2. Customize ThumbnailConfig in src/video/thumbnail_generator.py")
    print("   3. Add your logo: config.logo_path = Path('path/to/logo.png')")
    print("   4. Change brand text: config.brand_text = 'Your Channel Name'")

    print("\n✅ Test completed successfully!")


if __name__ == "__main__":
    try:
        test_thumbnail_generation()
    except Exception as e:
        logger.exception("Test failed")
        print(f"\n❌ Error: {e}")
        sys.exit(1)
