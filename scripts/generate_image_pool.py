"""
Image Pool Generator for Tech News Digest.

Pre-generates category-specific images to reduce DALL-E costs.

Cost Analysis:
- Initial investment: 45 images × $0.08 = $3.60
- Daily savings: 3 videos × $0.08 = $0.24/day = $7.20/month
- ROI: 3.6 days, Annual savings: $84+

Usage:
    python scripts/generate_image_pool.py --categories all
    python scripts/generate_image_pool.py --categories ai_ml,security
    python scripts/generate_image_pool.py --dry-run  # Preview without generating
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.ai_services.image_generator import ImageGenerator
from src.core.ai_services.models import ImageStyle
from src.core.logging import get_logger
from src.news.models import News, NewsCategory, NewsSource

logger = get_logger(__name__)


# Category-specific image prompts (3 variations per category)
CATEGORY_PROMPTS = {
    NewsCategory.AI_ML: [
        "A futuristic AI neural network visualization with glowing blue circuits and data nodes, modern tech aesthetic, 16:9 aspect ratio, photorealistic, professional lighting, no text",
        "Humanoid robot with glowing eyes working at a computer in a high-tech laboratory, artificial intelligence concept, 16:9 aspect ratio, cinematic lighting, no text",
        "Abstract visualization of machine learning algorithms with colorful data flows and geometric patterns, technology background, 16:9 aspect ratio, vibrant colors, no text",
    ],
    NewsCategory.SOFTWARE_CLOUD: [
        "Modern cloud computing data center with rows of servers and blue ambient lighting, professional tech photography, 16:9 aspect ratio, no text",
        "Software developer's workspace with multiple monitors showing code, clean modern office, natural lighting, 16:9 aspect ratio, professional photo, no text",
        "Abstract cloud infrastructure visualization with interconnected nodes and data streams, technology concept, 16:9 aspect ratio, blue theme, no text",
    ],
    NewsCategory.STARTUP_FUNDING: [
        "Modern startup office with enthusiastic team celebrating, bright and energetic atmosphere, 16:9 aspect ratio, professional photography, no text",
        "Business handshake with futuristic holographic charts showing growth, investment concept, 16:9 aspect ratio, professional lighting, no text",
        "Young entrepreneurs brainstorming with post-its and laptops in creative workspace, innovation theme, 16:9 aspect ratio, vibrant colors, no text",
    ],
    NewsCategory.SECURITY: [
        "Cybersecurity concept with glowing shield protecting digital data streams, dark blue theme, 16:9 aspect ratio, professional render, no text",
        "Hacker's hands typing on keyboard with matrix-style code reflections, cybersecurity theme, 16:9 aspect ratio, dramatic lighting, no text",
        "Digital lock and encrypted data visualization with blue security elements, protection concept, 16:9 aspect ratio, high-tech aesthetic, no text",
    ],
    NewsCategory.HARDWARE: [
        "Close-up of cutting-edge microchip with golden circuits on motherboard, macro photography, 16:9 aspect ratio, professional lighting, no text",
        "High-end gaming computer with RGB lighting and transparent case showing components, technology product, 16:9 aspect ratio, studio lighting, no text",
        "Modern smartphone disassembled showing internal components and technology, product photography, 16:9 aspect ratio, clean background, no text",
    ],
    NewsCategory.MOBILE: [
        "Sleek smartphone in hand displaying colorful app interface, modern lifestyle, 16:9 aspect ratio, professional product photography, no text",
        "Multiple mobile devices showing different apps and interfaces on minimalist desk, technology concept, 16:9 aspect ratio, top-down view, no text",
        "Person using mobile payment with smartphone at modern cafe, contactless technology, 16:9 aspect ratio, lifestyle photography, no text",
    ],
    NewsCategory.TECH_GENERAL: [
        "Modern technology workspace with laptop, tablet, and smart devices, minimalist aesthetic, 16:9 aspect ratio, natural lighting, no text",
        "Abstract digital technology background with hexagonal patterns and blue lights, tech concept, 16:9 aspect ratio, futuristic style, no text",
        "Diverse tech products arranged artistically on white background, product photography, 16:9 aspect ratio, studio lighting, no text",
    ],
    NewsCategory.BUSINESS: [
        "Modern corporate office building with glass facade reflecting sky, professional architecture, 16:9 aspect ratio, daytime photography, no text",
        "Business professional analyzing financial charts on large display, modern office, 16:9 aspect ratio, professional lighting, no text",
        "Global business concept with world map hologram and data visualization, technology integration, 16:9 aspect ratio, blue theme, no text",
    ],
    NewsCategory.SCIENCE: [
        "Modern scientific laboratory with advanced equipment and blue ambient lighting, research facility, 16:9 aspect ratio, professional photography, no text",
        "Abstract visualization of scientific data with molecular structures and graphs, science concept, 16:9 aspect ratio, colorful render, no text",
        "Scientist working with futuristic holographic displays showing research data, innovation theme, 16:9 aspect ratio, cinematic lighting, no text",
    ],
    NewsCategory.BREAKING: [
        "Dynamic news breaking concept with red alert elements and motion blur, urgent theme, 16:9 aspect ratio, high energy, no text",
        "Global news network visualization with connecting lines across world map, breaking news concept, 16:9 aspect ratio, dramatic lighting, no text",
        "Live newsroom with multiple screens showing global events, professional broadcast, 16:9 aspect ratio, realistic photography, no text",
    ],
}


# Fallback prompts for categories without specific designs
FALLBACK_PROMPTS = [
    "Modern technology abstract background with blue gradient and geometric shapes, professional aesthetic, 16:9 aspect ratio, no text",
    "High-tech digital interface with glowing elements and data visualization, futuristic concept, 16:9 aspect ratio, no text",
    "Contemporary office workspace with advanced technology devices, professional environment, 16:9 aspect ratio, natural lighting, no text",
]


class ImagePoolGenerator:
    """
    Generator for pre-made category image pools.

    Creates reusable images for each news category to reduce DALL-E API costs.
    """

    def __init__(
        self,
        output_dir: Optional[Path] = None,
        resource_pool: bool = True,
    ):
        """
        Initialize image pool generator.

        Args:
            output_dir: Output directory (uses ContentCreatorResources if resource_pool=True)
            resource_pool: Use shared resource pool directory
        """
        self.logger = get_logger(__name__)

        if resource_pool:
            # Use shared resource pool (~/ContentCreatorResources/library/news_images/)
            home = Path.home()
            self.output_dir = home / "ContentCreatorResources" / "library" / "news_images"
        else:
            self.output_dir = output_dir or Path("output/image_pool")

        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize image generator
        self.generator = ImageGenerator(output_dir=self.output_dir)

        self.logger.info(f"ImagePoolGenerator initialized (output_dir={self.output_dir})")

    def generate_category_pool(
        self,
        category: NewsCategory,
        prompts: Optional[list[str]] = None,
        quality: str = "standard",  # Use standard to save cost
        style: ImageStyle = ImageStyle.VIVID,
        dry_run: bool = False,
    ) -> list[Path]:
        """
        Generate image pool for a specific category.

        Args:
            category: News category
            prompts: Custom prompts (uses defaults if None)
            quality: Image quality (standard/hd)
            style: Image style
            dry_run: Preview without generating

        Returns:
            List of generated image paths
        """
        # Get prompts for category
        prompts = prompts or CATEGORY_PROMPTS.get(category, FALLBACK_PROMPTS)

        # Create category directory
        category_dir = self.output_dir / category.value
        category_dir.mkdir(parents=True, exist_ok=True)

        self.logger.info(
            f"Generating pool for {category.value}: {len(prompts)} images "
            f"(quality={quality}, dry_run={dry_run})"
        )

        if dry_run:
            self.logger.info("DRY RUN - Preview prompts:")
            for i, prompt in enumerate(prompts, 1):
                self.logger.info(f"  [{i}] {prompt[:100]}...")
            return []

        generated_images = []

        for i, prompt in enumerate(prompts, 1):
            try:
                self.logger.info(f"Generating image {i}/{len(prompts)} for {category.value}...")

                # Create dummy news object for generation
                dummy_news = News(
                    title=f"{category.value} news",
                    url="https://example.com",
                    source=NewsSource.TECHCRUNCH,
                    category=category,
                    published_at=datetime.utcnow(),
                )

                # Generate image
                image = self.generator.generate(
                    news=dummy_news,
                    style=style,
                    quality=quality,
                    custom_prompt=prompt,
                )

                # Move to category directory
                category_filename = f"{category.value}_{i:02d}.png"
                category_path = category_dir / category_filename

                # Copy to category directory
                import shutil
                shutil.copy(image.local_path, category_path)

                generated_images.append(category_path)

                self.logger.info(
                    f"✓ Generated: {category_path.name} (${image.total_cost:.3f})"
                )

            except Exception as e:
                self.logger.error(f"Failed to generate image {i}: {e}", exc_info=True)
                continue

        self.logger.info(
            f"Category pool complete: {category.value} - "
            f"{len(generated_images)}/{len(prompts)} images, "
            f"total cost: ${self.generator.total_cost:.3f}"
        )

        return generated_images

    def generate_all_pools(
        self,
        quality: str = "standard",
        style: ImageStyle = ImageStyle.VIVID,
        dry_run: bool = False,
        categories: Optional[list[NewsCategory]] = None,
    ) -> dict[NewsCategory, list[Path]]:
        """
        Generate image pools for all categories.

        Args:
            quality: Image quality
            style: Image style
            dry_run: Preview without generating
            categories: Specific categories (uses all with prompts if None)

        Returns:
            Dictionary mapping categories to image paths
        """
        # Use specified categories or all categories with prompts
        target_categories = categories or list(CATEGORY_PROMPTS.keys())

        total_images = sum(len(CATEGORY_PROMPTS.get(cat, FALLBACK_PROMPTS))
                          for cat in target_categories)
        estimated_cost = total_images * (0.120 if quality == "hd" else 0.080)

        self.logger.info(
            f"Generating pools for {len(target_categories)} categories:\n"
            f"  Total images: {total_images}\n"
            f"  Estimated cost: ${estimated_cost:.2f}\n"
            f"  Quality: {quality}\n"
            f"  Style: {style.value}\n"
            f"  Dry run: {dry_run}"
        )

        if dry_run:
            for cat in target_categories:
                prompts = CATEGORY_PROMPTS.get(cat, FALLBACK_PROMPTS)
                self.logger.info(f"\n{cat.value}: {len(prompts)} images")
            return {}

        # Confirm before proceeding
        if not dry_run and estimated_cost > 1.0:
            print(f"\n⚠️  This will cost approximately ${estimated_cost:.2f}")
            response = input("Continue? (yes/no): ").strip().lower()
            if response not in ["yes", "y"]:
                self.logger.info("Generation cancelled by user")
                return {}

        # Generate pools
        results = {}
        initial_cost = self.generator.total_cost

        for i, category in enumerate(target_categories, 1):
            self.logger.info(f"\n{'='*60}")
            self.logger.info(f"Processing category {i}/{len(target_categories)}: {category.value}")
            self.logger.info(f"{'='*60}")

            images = self.generate_category_pool(
                category=category,
                quality=quality,
                style=style,
                dry_run=False,
            )

            results[category] = images

        # Summary
        total_cost = self.generator.total_cost - initial_cost
        total_generated = sum(len(imgs) for imgs in results.values())

        self.logger.info(f"\n{'='*60}")
        self.logger.info("IMAGE POOL GENERATION COMPLETE")
        self.logger.info(f"{'='*60}")
        self.logger.info(f"Categories: {len(results)}")
        self.logger.info(f"Images generated: {total_generated}/{total_images}")
        self.logger.info(f"Total cost: ${total_cost:.2f}")
        self.logger.info(f"Output directory: {self.output_dir}")
        self.logger.info(f"\n💰 Expected monthly savings: ${0.08 * 3 * 30:.2f}")
        self.logger.info(f"📊 ROI: {total_cost / (0.08 * 3):.1f} days")

        return results


def main():
    """Main entry point."""
    from datetime import datetime

    parser = argparse.ArgumentParser(
        description="Generate category-specific image pools for Tech News Digest"
    )
    parser.add_argument(
        "--categories",
        type=str,
        default="all",
        help="Comma-separated category names or 'all' (default: all)",
    )
    parser.add_argument(
        "--quality",
        type=str,
        choices=["standard", "hd"],
        default="standard",
        help="Image quality (default: standard to save cost)",
    )
    parser.add_argument(
        "--style",
        type=str,
        choices=["natural", "vivid"],
        default="vivid",
        help="Image style (default: vivid)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview prompts without generating images",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Custom output directory (default: ~/ContentCreatorResources/library/news_images/)",
    )
    parser.add_argument(
        "--no-resource-pool",
        action="store_true",
        help="Don't use shared resource pool",
    )

    args = parser.parse_args()

    # Parse categories
    if args.categories.lower() == "all":
        categories = list(CATEGORY_PROMPTS.keys())
    else:
        category_names = [c.strip().upper() for c in args.categories.split(",")]
        categories = []
        for name in category_names:
            try:
                cat = NewsCategory[name]
                categories.append(cat)
            except KeyError:
                logger.error(f"Invalid category: {name}")
                logger.info(f"Valid categories: {', '.join(c.name for c in CATEGORY_PROMPTS.keys())}")
                sys.exit(1)

    # Create generator
    generator = ImagePoolGenerator(
        output_dir=args.output_dir,
        resource_pool=not args.no_resource_pool,
    )

    # Generate pools
    style = ImageStyle.VIVID if args.style == "vivid" else ImageStyle.NATURAL

    results = generator.generate_all_pools(
        quality=args.quality,
        style=style,
        dry_run=args.dry_run,
        categories=categories,
    )

    if results:
        logger.info("\n✅ Image pool generation complete!")
        logger.info(f"Images saved to: {generator.output_dir}")


if __name__ == "__main__":
    main()
