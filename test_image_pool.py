"""
Test Image Pool System for Tech News Digest.

Tests:
1. Dry run preview of image pool generation
2. Generate small test pool (2-3 categories)
3. Test ImageSelector with pool
4. Validate cost savings

Usage:
    # Preview prompts (no cost)
    python test_image_pool.py --dry-run

    # Generate test pool (AI_ML + SECURITY categories only)
    python test_image_pool.py --test

    # Test image selection with pool
    python test_image_pool.py --select

    # Full pool generation (all categories)
    python test_image_pool.py --full
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.core.logging import get_logger
from src.news.models import News, NewsCategory, NewsSource
from src.video.image_selector import ImageSelector
from datetime import datetime

logger = get_logger(__name__)


def test_dry_run():
    """Test dry run to preview prompts."""
    from scripts.generate_image_pool import CATEGORY_PROMPTS

    logger.info("=== DRY RUN: Preview Image Pool Prompts ===\n")

    total_images = 0
    for category, prompts in CATEGORY_PROMPTS.items():
        total_images += len(prompts)
        logger.info(f"\n{category.value.upper()} ({len(prompts)} images):")
        for i, prompt in enumerate(prompts, 1):
            logger.info(f"  [{i}] {prompt[:120]}...")

    estimated_cost = total_images * 0.08  # Standard quality
    logger.info(f"\n📊 Summary:")
    logger.info(f"  Total categories: {len(CATEGORY_PROMPTS)}")
    logger.info(f"  Total images: {total_images}")
    logger.info(f"  Estimated cost (standard): ${estimated_cost:.2f}")
    logger.info(f"  Estimated cost (HD): ${total_images * 0.12:.2f}")
    logger.info(f"\n💰 Monthly savings (3 videos/day): ${0.08 * 3 * 30:.2f}")
    logger.info(f"  ROI: {estimated_cost / (0.08 * 3):.1f} days")


def test_small_pool():
    """Generate small test pool (2 categories)."""
    from scripts.generate_image_pool import ImagePoolGenerator
    from src.news.models import NewsCategory

    logger.info("=== TEST: Generate Small Image Pool ===\n")

    # Test with just 2 categories
    test_categories = [NewsCategory.AI_ML, NewsCategory.SECURITY]

    generator = ImagePoolGenerator(resource_pool=True)

    logger.info(f"Generating pool for test categories: {[c.value for c in test_categories]}")
    logger.info("Quality: standard (to save cost)")
    logger.info(f"Expected cost: ${len(test_categories) * 3 * 0.08:.2f}\n")

    results = generator.generate_all_pools(
        quality="standard",
        dry_run=False,
        categories=test_categories,
    )

    # Summary
    total_images = sum(len(imgs) for imgs in results.values())
    logger.info(f"\n✅ Test pool generated!")
    logger.info(f"  Categories: {len(results)}")
    logger.info(f"  Images: {total_images}")
    logger.info(f"  Cost: ${generator.generator.total_cost:.2f}")

    # Check files
    for category, images in results.items():
        logger.info(f"\n{category.value}:")
        for img in images:
            logger.info(f"  ✓ {img.name}")


def test_image_selection():
    """Test ImageSelector with pool."""
    logger.info("=== TEST: Image Selection ===\n")

    # Create test news articles
    test_news = [
        News(
            title="AI breakthrough in language models",
            url="https://example.com/1",
            source=NewsSource.TECHCRUNCH,
            category=NewsCategory.AI_ML,
            published_at=datetime.utcnow(),
        ),
        News(
            title="Security vulnerability discovered",
            url="https://example.com/2",
            source=NewsSource.TECHCRUNCH,
            category=NewsCategory.SECURITY,
            published_at=datetime.utcnow(),
        ),
        News(
            title="New smartphone released",
            url="https://example.com/3",
            source=NewsSource.TECHCRUNCH,
            category=NewsCategory.MOBILE,  # Not in test pool
            published_at=datetime.utcnow(),
        ),
    ]

    # Test with pool enabled
    logger.info("🔵 Testing with pool enabled:")
    selector = ImageSelector(use_pool=True, fallback_to_generation=True)

    pool_status = selector.get_pool_status()
    logger.info(f"\nPool status:")
    logger.info(f"  Pool exists: {pool_status['pool_exists']}")
    logger.info(f"  Categories: {pool_status['categories_in_pool']}")
    logger.info(f"  Total images: {pool_status['total_pool_images']}")
    logger.info(f"  Categories: {', '.join(pool_status['pool_categories'])}\n")

    for i, news in enumerate(test_news, 1):
        logger.info(f"[{i}] Testing: {news.title}")
        logger.info(f"    Category: {news.category.value}")

        has_pool = selector.has_pool_for_category(news.category)
        logger.info(f"    Has pool: {has_pool}")

        if has_pool:
            logger.info(f"    Pool size: {selector.get_category_pool_count(news.category)} images")

        # Note: Not actually selecting images to avoid costs
        # Just checking pool availability

    # Show savings estimate
    logger.info("\n💰 Savings Estimate:")
    estimate = selector.estimate_monthly_savings(daily_videos=3)
    logger.info(f"  Daily videos: {estimate['daily_videos']}")
    logger.info(f"  Monthly without pool: ${estimate['monthly_without_pool']:.2f}")
    logger.info(f"  Monthly with pool: ${estimate['monthly_with_pool']:.2f}")
    logger.info(f"  Monthly savings: ${estimate['monthly_savings']:.2f}")
    logger.info(f"  Annual savings: ${estimate['annual_savings']:.2f}")
    logger.info(f"  Initial investment: ${estimate['initial_investment']:.2f}")
    logger.info(f"  ROI: {estimate['roi_days']:.1f} days")

    # Test without pool
    logger.info("\n🔴 Testing without pool (for comparison):")
    selector_no_pool = ImageSelector(use_pool=False, fallback_to_generation=False)
    logger.info("  Would fall back to generation for all images")
    logger.info(f"  Cost per video (3 images): ${0.08 * 3:.2f}")


def test_full_pool():
    """Generate full image pool (all categories)."""
    from scripts.generate_image_pool import ImagePoolGenerator

    logger.info("=== FULL: Generate Complete Image Pool ===\n")

    generator = ImagePoolGenerator(resource_pool=True)

    logger.info("⚠️  WARNING: This will generate images for ALL categories!")
    logger.info("   Quality: standard")
    logger.info("   Estimated cost: ~$3.60 (45 images × $0.08)")
    logger.info("   Monthly savings: ~$7.20 (3 videos/day)")
    logger.info("   ROI: ~15 days\n")

    response = input("Continue with full pool generation? (yes/no): ").strip().lower()
    if response not in ["yes", "y"]:
        logger.info("❌ Full pool generation cancelled")
        return

    results = generator.generate_all_pools(
        quality="standard",
        dry_run=False,
    )

    # Summary
    total_images = sum(len(imgs) for imgs in results.values())
    logger.info(f"\n✅ Full pool generated!")
    logger.info(f"  Categories: {len(results)}")
    logger.info(f"  Images: {total_images}")
    logger.info(f"  Cost: ${generator.generator.total_cost:.2f}")

    # List all images
    for category, images in results.items():
        logger.info(f"\n{category.value} ({len(images)} images):")
        for img in images:
            logger.info(f"  ✓ {img.name}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Test Image Pool System")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview prompts without generating (FREE)",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Generate small test pool (2 categories, ~$0.48)",
    )
    parser.add_argument(
        "--select",
        action="store_true",
        help="Test image selection with pool (FREE)",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Generate full pool (all categories, ~$3.60)",
    )

    args = parser.parse_args()

    # Default to dry run if no args
    if not any([args.dry_run, args.test, args.select, args.full]):
        logger.info("No test specified. Running dry-run by default.\n")
        logger.info("Usage:")
        logger.info("  --dry-run : Preview prompts (FREE)")
        logger.info("  --test    : Generate small test pool (~$0.48)")
        logger.info("  --select  : Test selection logic (FREE)")
        logger.info("  --full    : Generate full pool (~$3.60)\n")
        args.dry_run = True

    try:
        if args.dry_run:
            test_dry_run()

        if args.test:
            test_small_pool()

        if args.select:
            test_image_selection()

        if args.full:
            test_full_pool()

        logger.info("\n✅ Tests complete!")

    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
