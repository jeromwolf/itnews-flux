"""
Test script for anchor image generation.

Generates sample anchor images to verify consistency and quality.
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.ai_services.anchor_generator import (
    AnchorImageGenerator,
    generate_daily_anchor_images,
)
from src.core.logging import get_logger

logger = get_logger(__name__)


def test_single_anchor_image():
    """Test generating a single anchor image."""
    logger.info("=" * 70)
    logger.info("Test 1: Generate single intro anchor image")
    logger.info("=" * 70)

    generator = AnchorImageGenerator()

    # Generate intro image for today
    image = generator.generate_anchor_image(scene_type="intro")

    logger.info(f"✅ Generated intro image: {image.local_path}")
    logger.info(f"   Size: {image.size}")
    logger.info(f"   URL: {image.url}")

    return image


def test_daily_outfit_rotation():
    """Test outfit rotation across 7 days."""
    logger.info("\n" + "=" * 70)
    logger.info("Test 2: Generate anchor images for 7 days (outfit rotation)")
    logger.info("=" * 70)

    generator = AnchorImageGenerator()

    for i in range(7):
        date = datetime.now() + timedelta(days=i)
        day_name = date.strftime("%A")

        outfit = generator.get_daily_outfit(date)

        logger.info(f"\n📅 {day_name} ({date.strftime('%Y-%m-%d')})")
        logger.info(f"   Outfit: {outfit.outfit[:60]}...")
        logger.info(f"   Color: {outfit.color_scheme}")
        logger.info(f"   Expression: {outfit.expression[:50]}...")


def test_all_scene_types():
    """Test generating all scene types (intro, news, outro, thumbnail)."""
    logger.info("\n" + "=" * 70)
    logger.info("Test 3: Generate all scene types for today")
    logger.info("=" * 70)

    generator = AnchorImageGenerator()

    scenes = ["intro", "news", "outro"]

    images = {}
    for scene in scenes:
        logger.info(f"\n🎬 Generating {scene} scene...")
        image = generator.generate_anchor_image(scene_type=scene)
        images[scene] = image

        logger.info(f"   ✅ {scene}: {image.local_path}")

    # Thumbnail (different size)
    logger.info(f"\n🖼️  Generating thumbnail...")
    thumbnail = generator.generate_thumbnail_anchor()
    images["thumbnail"] = thumbnail

    logger.info(f"   ✅ thumbnail: {thumbnail.local_path}")

    return images


def test_complete_daily_set():
    """Test complete daily anchor image generation."""
    logger.info("\n" + "=" * 70)
    logger.info("Test 4: Generate complete daily image set (using convenience function)")
    logger.info("=" * 70)

    images = generate_daily_anchor_images()

    logger.info(f"\n✅ Generated {len(images)} images:")
    for scene_type, image in images.items():
        logger.info(f"   - {scene_type}: {image.local_path}")

    return images


def main():
    """Run all tests."""
    logger.info("\n" + "=" * 70)
    logger.info("🎬 이서연 Anchor Image Generator - Test Suite")
    logger.info("=" * 70)

    try:
        # Test 1: Single image
        test_single_anchor_image()

        # Test 2: Outfit rotation
        test_daily_outfit_rotation()

        # Test 3: All scene types
        logger.info("\n⚠️  WARNING: Test 3 will generate 4 images (costs ~$0.16)")
        response = input("Continue with image generation? (y/n): ")
        if response.lower() == "y":
            test_all_scene_types()
        else:
            logger.info("Skipped Test 3")

        # Test 4: Complete daily set
        logger.info("\n⚠️  WARNING: Test 4 will generate 4 images (costs ~$0.16)")
        response = input("Generate complete daily image set? (y/n): ")
        if response.lower() == "y":
            images = test_complete_daily_set()

            logger.info("\n" + "=" * 70)
            logger.info("✅ All tests completed successfully!")
            logger.info("=" * 70)
            logger.info("\n📸 Generated images:")
            for scene_type, image in images.items():
                logger.info(f"   {scene_type:12s} → {image.local_path}")
        else:
            logger.info("Skipped Test 4")

        logger.info("\n💡 Next steps:")
        logger.info("   1. Review generated images for consistency")
        logger.info("   2. Check if 이서연 looks the same across different outfits")
        logger.info("   3. Verify outfit variations are working properly")
        logger.info("   4. If satisfied, integrate into video pipeline")

    except KeyboardInterrupt:
        logger.info("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        logger.error(f"\n❌ Test failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
