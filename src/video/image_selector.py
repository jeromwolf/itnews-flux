"""
Image Selector for Tech News Digest.

Intelligently selects images from pre-generated pools or generates new ones.

Cost Optimization Strategy:
1. Use pre-generated category images when available (FREE)
2. Fall back to DALL-E generation when pool unavailable ($0.08/image)
3. Track usage and savings metrics

Usage:
    >>> selector = ImageSelector(use_pool=True)
    >>> image = selector.get_image_for_news(news_article)
    >>> print(f"Saved: ${selector.total_savings:.2f}")
"""

import random
from pathlib import Path
from typing import Optional

from src.core.ai_services.image_generator import ImageGenerator
from src.core.ai_services.models import GeneratedImage, ImageStyle
from src.core.logging import get_logger
from src.news.models import News, NewsCategory

logger = get_logger(__name__)


class ImageSelector:
    """
    Smart image selector with pool support.

    Chooses between pre-generated pool images and on-demand DALL-E generation.
    """

    def __init__(
        self,
        pool_dir: Optional[Path] = None,
        use_pool: bool = True,
        fallback_to_generation: bool = True,
        output_dir: Optional[Path] = None,
    ):
        """
        Initialize image selector.

        Args:
            pool_dir: Directory containing image pools (uses ContentCreatorResources if None)
            use_pool: Use pool images when available
            fallback_to_generation: Generate new image if pool unavailable
            output_dir: Output directory for generated images
        """
        self.logger = get_logger(__name__)
        self.use_pool = use_pool
        self.fallback_to_generation = fallback_to_generation

        # Pool directory
        if pool_dir is None:
            home = Path.home()
            self.pool_dir = home / "ContentCreatorResources" / "library" / "news_images"
        else:
            self.pool_dir = pool_dir

        # Image generator (for fallback)
        self.generator = ImageGenerator(output_dir=output_dir) if fallback_to_generation else None

        # Load image pools
        self.image_pools = self._load_image_pools()

        # Metrics
        self.pool_usage_count = 0
        self.generation_count = 0
        self.total_savings = 0.0

        self.logger.info(
            f"ImageSelector initialized:\n"
            f"  Pool directory: {self.pool_dir}\n"
            f"  Use pool: {use_pool}\n"
            f"  Fallback to generation: {fallback_to_generation}\n"
            f"  Categories in pool: {len(self.image_pools)}\n"
            f"  Total pool images: {sum(len(imgs) for imgs in self.image_pools.values())}"
        )

    def _load_image_pools(self) -> dict[NewsCategory, list[Path]]:
        """
        Load pre-generated image pools from directory.

        Returns:
            Dictionary mapping categories to image paths
        """
        pools = {}

        if not self.pool_dir.exists():
            self.logger.warning(f"Pool directory not found: {self.pool_dir}")
            return pools

        # Scan category directories
        for category in NewsCategory:
            category_dir = self.pool_dir / category.value

            if category_dir.exists() and category_dir.is_dir():
                # Find all PNG images in category directory
                images = sorted(category_dir.glob("*.png"))

                if images:
                    pools[category] = images
                    self.logger.debug(
                        f"Loaded pool for {category.value}: {len(images)} images"
                    )

        self.logger.info(f"Loaded {len(pools)} category pools")
        return pools

    def get_image_for_news(
        self,
        news: News,
        style: ImageStyle = ImageStyle.VIVID,
        quality: str = "hd",
        force_generation: bool = False,
    ) -> GeneratedImage:
        """
        Get image for news article.

        Strategy:
        1. If force_generation=True: Always generate new image
        2. If use_pool=True and category in pool: Use random pool image
        3. Else if fallback_to_generation=True: Generate new image
        4. Else: Raise error

        Args:
            news: News article
            style: Image style (for generation)
            quality: Image quality (for generation)
            force_generation: Force new image generation

        Returns:
            Generated or selected image

        Raises:
            ValueError: If no image available and fallback disabled
        """
        # Force generation if requested
        if force_generation:
            return self._generate_image(news, style, quality)

        # Try pool first
        if self.use_pool and news.category in self.image_pools:
            pool_images = self.image_pools[news.category]

            if pool_images:
                # Select random image from pool
                selected_path = random.choice(pool_images)

                self.logger.info(
                    f"Using pool image for {news.category.value}: {selected_path.name}"
                )

                # Track metrics
                self.pool_usage_count += 1
                # Standard quality DALL-E cost
                saved_cost = 0.120 if quality == "hd" else 0.080
                self.total_savings += saved_cost

                # Create GeneratedImage object
                return GeneratedImage(
                    local_path=selected_path,
                    width=1792,
                    height=1024,
                    prompt=f"Pool image for {news.category.value}",
                    style=style,
                    quality=quality,
                    model="pool",
                    total_cost=0.0,  # Free from pool
                    from_pool=True,
                )

        # Fallback to generation
        if self.fallback_to_generation:
            self.logger.info(
                f"No pool image for {news.category.value}, generating new image"
            )
            return self._generate_image(news, style, quality)

        # No image available
        raise ValueError(
            f"No pool image available for category {news.category.value} "
            "and fallback generation is disabled"
        )

    def _generate_image(
        self,
        news: News,
        style: ImageStyle,
        quality: str,
    ) -> GeneratedImage:
        """
        Generate new image using DALL-E.

        Args:
            news: News article
            style: Image style
            quality: Image quality

        Returns:
            Generated image
        """
        if not self.generator:
            raise ValueError("Image generation is disabled (no generator initialized)")

        image = self.generator.generate(news, style, quality)

        # Track metrics
        self.generation_count += 1

        self.logger.info(f"Generated new image: ${image.total_cost:.3f}")
        return image

    def get_pool_status(self) -> dict:
        """
        Get image pool status and metrics.

        Returns:
            Status dictionary with pool info and usage metrics
        """
        total_pool_images = sum(len(imgs) for imgs in self.image_pools.values())

        return {
            "pool_dir": str(self.pool_dir),
            "pool_exists": self.pool_dir.exists(),
            "categories_in_pool": len(self.image_pools),
            "total_pool_images": total_pool_images,
            "pool_categories": [cat.value for cat in self.image_pools.keys()],
            "use_pool": self.use_pool,
            "fallback_to_generation": self.fallback_to_generation,
            # Usage metrics
            "pool_usage_count": self.pool_usage_count,
            "generation_count": self.generation_count,
            "total_requests": self.pool_usage_count + self.generation_count,
            "pool_usage_rate": (
                self.pool_usage_count / (self.pool_usage_count + self.generation_count)
                if (self.pool_usage_count + self.generation_count) > 0
                else 0.0
            ),
            "total_savings": self.total_savings,
            "total_generation_cost": self.generator.total_cost if self.generator else 0.0,
        }

    def reload_pools(self) -> None:
        """Reload image pools from directory."""
        self.logger.info("Reloading image pools...")
        self.image_pools = self._load_image_pools()
        self.logger.info(f"Reloaded {len(self.image_pools)} category pools")

    def get_category_pool_count(self, category: NewsCategory) -> int:
        """
        Get number of images in pool for category.

        Args:
            category: News category

        Returns:
            Number of images in pool (0 if no pool)
        """
        return len(self.image_pools.get(category, []))

    def has_pool_for_category(self, category: NewsCategory) -> bool:
        """
        Check if pool exists for category.

        Args:
            category: News category

        Returns:
            True if pool exists and has images
        """
        return category in self.image_pools and len(self.image_pools[category]) > 0

    def get_missing_categories(self) -> list[NewsCategory]:
        """
        Get list of categories without image pools.

        Returns:
            List of categories missing from pool
        """
        all_categories = set(NewsCategory)
        pooled_categories = set(self.image_pools.keys())
        return list(all_categories - pooled_categories)

    def estimate_monthly_savings(self, daily_videos: int = 3) -> dict:
        """
        Estimate monthly cost savings from using image pool.

        Args:
            daily_videos: Number of videos generated per day

        Returns:
            Dictionary with cost estimates
        """
        # Assume standard quality ($0.08/image) for estimates
        cost_per_image = 0.08

        # Without pool (all generated)
        monthly_without_pool = daily_videos * 30 * cost_per_image

        # With pool (assuming 80% pool usage, 20% generation)
        pool_usage_rate = 0.80
        monthly_with_pool = daily_videos * 30 * cost_per_image * (1 - pool_usage_rate)

        monthly_savings = monthly_without_pool - monthly_with_pool
        annual_savings = monthly_savings * 12

        # Initial pool creation cost (estimate 10 categories × 3 images)
        initial_investment = 10 * 3 * cost_per_image  # $2.40

        # ROI in days
        daily_savings = monthly_savings / 30
        roi_days = initial_investment / daily_savings if daily_savings > 0 else 0

        return {
            "cost_per_image": cost_per_image,
            "daily_videos": daily_videos,
            "monthly_without_pool": monthly_without_pool,
            "monthly_with_pool": monthly_with_pool,
            "monthly_savings": monthly_savings,
            "annual_savings": annual_savings,
            "initial_investment": initial_investment,
            "roi_days": roi_days,
            "pool_usage_rate": pool_usage_rate,
        }


def create_image_selector(
    use_pool: bool = True,
    fallback_to_generation: bool = True,
    **kwargs,
) -> ImageSelector:
    """
    Create image selector instance.

    Args:
        use_pool: Use pool images when available
        fallback_to_generation: Generate new image if pool unavailable

    Returns:
        ImageSelector instance

    Example:
        >>> selector = create_image_selector(use_pool=True)
        >>> image = selector.get_image_for_news(news)
        >>> status = selector.get_pool_status()
        >>> print(f"Pool usage: {status['pool_usage_rate']:.0%}")
        >>> print(f"Savings: ${status['total_savings']:.2f}")
    """
    return ImageSelector(
        use_pool=use_pool,
        fallback_to_generation=fallback_to_generation,
        **kwargs,
    )
