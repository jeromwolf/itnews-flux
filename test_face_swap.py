"""
Test face swapping with anchor images.
"""

from pathlib import Path
from src.core.ai_services.face_swapper import FaceSwapper
from src.core.logging import get_logger

logger = get_logger(__name__)


def main():
    logger.info("=" * 70)
    logger.info("🎭 Face Swap Test - Anchor Character Consistency")
    logger.info("=" * 70)

    # Paths
    intro_image = "output/images/20251104_071749_이서연_Anchor_-_intro.png"

    target_images = [
        "output/images/20251104_072822_이서연_Anchor_-_news.png",
        "output/images/20251104_072855_이서연_Anchor_-_outro.png",
        "output/images/20251104_072930_이서연_Anchor_-_Thumbnail.png",
    ]

    # Check if files exist
    if not Path(intro_image).exists():
        logger.error(f"Reference image not found: {intro_image}")
        return

    for target in target_images:
        if not Path(target).exists():
            logger.error(f"Target image not found: {target}")
            return

    logger.info(f"\n📸 Reference image: {intro_image}")
    logger.info(f"🎯 Target images: {len(target_images)}")
    for target in target_images:
        logger.info(f"   - {Path(target).name}")

    # Initialize face swapper
    logger.info("\n🔧 Initializing FaceSwapper...")
    swapper = FaceSwapper()

    # Swap faces
    logger.info("\n🎭 Swapping faces...")
    output_dir = Path("output/images")
    output_dir.mkdir(parents=True, exist_ok=True)

    results = []
    for i, target in enumerate(target_images, 1):
        logger.info(f"\n[{i}/{len(target_images)}] Processing: {Path(target).name}")

        try:
            # Generate output filename
            target_path = Path(target)
            output_path = str(output_dir / f"{target_path.stem}_consistent{target_path.suffix}")

            result = swapper.swap_face(
                source_image_path=intro_image,
                target_image_path=target,
                output_path=output_path
            )

            results.append(result)
            logger.info(f"   ✅ Saved: {result}")

        except Exception as e:
            logger.error(f"   ❌ Failed: {e}", exc_info=True)

    # Summary
    logger.info("\n" + "=" * 70)
    logger.info(f"✨ Face swap complete!")
    logger.info(f"📊 Success: {len(results)}/{len(target_images)}")
    logger.info("\n📁 Output files:")
    for result in results:
        logger.info(f"   - {result}")
    logger.info("=" * 70)


if __name__ == "__main__":
    main()
