#!/usr/bin/env python3
"""
Test thumbnail generation with AI ON logo and custom config.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.video.thumbnail_generator import ThumbnailGenerator
from src.core.logging import get_logger

logger = get_logger(__name__)


def test_with_logo():
    """Test thumbnail with logo from config file."""
    print("=" * 60)
    print("AI ON Thumbnail Test (with Logo)")
    print("=" * 60)

    # Find sample image
    output_dir = Path("output/images")
    if not output_dir.exists():
        print("\n❌ Error: No images found in output/images")
        print("   Please run test_ai_services.py first")
        return

    images = list(output_dir.glob("*.png"))
    if not images:
        print("\n❌ Error: No PNG images found")
        return

    sample_image = images[0]
    print(f"\n✅ Using sample image: {sample_image.name}")

    # Check if config exists
    config_file = Path("config/thumbnail_config.json")
    if not config_file.exists():
        print(f"\n❌ Error: Config file not found: {config_file}")
        return

    print(f"✅ Using config: {config_file}")

    # Check if logo exists
    logo_path = Path("resources/logo.png")
    if not logo_path.exists():
        print(f"\n⚠️  Logo not found: {logo_path}")
        print("   Run: python create_logo.py")
        return

    print(f"✅ Logo found: {logo_path}")

    # Create generator with config file
    generator = ThumbnailGenerator(config_file=config_file)

    # Test 1: Tech news with logo
    print("\n" + "=" * 60)
    print("Test 1: AI ON Branded Thumbnail")
    print("=" * 60)

    thumbnail = generator.generate(
        title="OpenAI Launches GPT-5 with Revolutionary AI Capabilities",
        background_image_path=sample_image,
        subtitle="Tech News • December 20, 2025",
    )

    print(f"\n✅ Thumbnail generated: {thumbnail}")
    print(f"   Size: {thumbnail.stat().st_size / 1024:.1f} KB")

    # Test 2: Different news
    print("\n" + "=" * 60)
    print("Test 2: Another News Thumbnail")
    print("=" * 60)

    if len(images) >= 2:
        thumbnail2 = generator.generate(
            title="Apple Vision Pro 3 Revolutionizes AR Experience",
            background_image_path=images[1] if len(images) > 1 else images[0],
            subtitle="Hardware • Apple",
            use_cache=False,
        )
        print(f"\n✅ Thumbnail generated: {thumbnail2}")
        print(f"   Size: {thumbnail2.stat().st_size / 1024:.1f} KB")

    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    thumbnails_dir = Path("output/thumbnails")
    all_thumbnails = list(thumbnails_dir.glob("*.jpg"))
    print(f"\n✅ Total thumbnails: {len(all_thumbnails)}")
    print(f"   Location: {thumbnails_dir}")

    print("\n📝 How to customize:")
    print("   1. Edit config: config/thumbnail_config.json")
    print("      - Change brand_text: 'AI ON' → your text")
    print("      - Adjust colors, sizes, positions")
    print("   2. Replace logo: resources/logo.png")
    print("      - Use your actual AI ON logo")
    print("      - Recommended size: 200x200 PNG with transparency")

    print("\n✅ Test completed!")


if __name__ == "__main__":
    try:
        test_with_logo()
    except Exception as e:
        logger.exception("Test failed")
        print(f"\n❌ Error: {e}")
        sys.exit(1)
