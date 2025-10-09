"""
DALL-E 3 Image Generator for Tech News Digest.

Generates 16:9 news images with:
- Professional news photo style
- Relevant to article content
- High quality (HD)
- Automatic download and caching
"""

import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional
from urllib.request import urlretrieve

from src.core.ai_services.base import BaseAIService, GenerationError
from src.core.ai_services.models import GeneratedImage, ImageStyle
from src.core.logging import get_logger, log_execution_time
from src.news.models import News

logger = get_logger(__name__)


class ImageGenerator(BaseAIService):
    """
    DALL-E 3 image generator for news content.

    Generates professional news images optimized for:
    - 16:9 aspect ratio (1792x1024)
    - YouTube thumbnails and video content
    - Professional news style
    """

    def __init__(self, output_dir: Optional[Path] = None, **kwargs):
        """
        Initialize image generator.

        Args:
            output_dir: Directory for generated images
        """
        super().__init__(**kwargs)
        self.model = self.settings.openai.image_model
        self.output_dir = output_dir or Path("output/images")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Pricing (DALL-E 3 as of 2025)
        # HD 1792x1024: $0.120 per image
        # Standard 1792x1024: $0.080 per image
        self.price_hd = 0.120
        self.price_standard = 0.080

    @log_execution_time(logger)
    def generate(
        self,
        news: News,
        style: ImageStyle = ImageStyle.VIVID,
        quality: str = "hd",
        custom_prompt: Optional[str] = None,
    ) -> GeneratedImage:
        """
        Generate image for news article.

        Args:
            news: News article
            style: Image style (natural/vivid)
            quality: Image quality (standard/hd)
            custom_prompt: Custom prompt (overrides auto-generated)

        Returns:
            Generated image

        Raises:
            GenerationError: If generation fails
        """
        self.logger.info(
            f"Generating image for: {news.title[:50]}... "
            f"(style={style.value}, quality={quality})"
        )

        # Build prompt
        prompt = custom_prompt or self._build_prompt(news)

        # Check cache
        cache_key = f"{hashlib.md5(prompt.encode()).hexdigest()}_{style.value}_{quality}"
        cached_path = self._get_cache_path(cache_key, "png")

        if cached_path.exists():
            self.logger.info(f"Using cached image: {cached_path.name}")
            return GeneratedImage(
                local_path=cached_path,
                width=1792,
                height=1024,
                prompt=prompt,
                style=style,
                quality=quality,
                model=self.model,
                total_cost=0.0,  # Cached, no cost
            )

        # Generate image
        try:
            response = self._call_api_with_retry(
                self.client.images.generate,
                model=self.model,
                prompt=prompt,
                size="1792x1024",  # 16:9 ratio
                quality=quality,
                style=style.value,
                n=1,
            )

            # Get image URL
            image_data = response.data[0]
            image_url = image_data.url
            revised_prompt = getattr(image_data, "revised_prompt", None)

            # Download image
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_title = self._sanitize_filename(news.title[:30])
            filename = f"{timestamp}_{safe_title}.png"
            local_path = self.output_dir / filename

            self.logger.debug(f"Downloading image from: {image_url}")
            urlretrieve(image_url, local_path)

            # Also save to cache
            if self.enable_cache:
                import shutil
                shutil.copy(local_path, cached_path)

            # Calculate cost
            cost = self.price_hd if quality == "hd" else self.price_standard
            self.total_cost += cost

            # Create image object
            image = GeneratedImage(
                url=image_url,
                local_path=local_path,
                width=1792,
                height=1024,
                prompt=prompt,
                revised_prompt=revised_prompt,
                style=style,
                quality=quality,
                model=self.model,
                total_cost=cost,
            )

            self.logger.info(
                f"Image generated: {local_path.name}, "
                f"size={image.size}, ${cost:.3f}"
            )

            return image

        except Exception as e:
            self.logger.error(f"Image generation failed: {e}", exc_info=True)
            raise GenerationError(f"Image generation failed: {e}") from e

    def _build_prompt(self, news: News) -> str:
        """
        Build image generation prompt from news.

        Args:
            news: News article

        Returns:
            Image prompt
        """
        # Category-specific prompt enhancements
        category_styles = {
            "ai_ml": "with futuristic AI and machine learning elements",
            "software_cloud": "with modern software development and cloud computing visuals",
            "mobile": "with sleek mobile devices and technology",
            "hardware": "with cutting-edge hardware and electronics",
            "startup_funding": "with startup and business growth imagery",
            "security": "with cybersecurity and digital protection themes",
            "crypto_blockchain": "with blockchain and cryptocurrency visuals",
            "gaming": "with gaming technology and esports elements",
            "social_media": "with social media and digital communication themes",
            "ecommerce": "with e-commerce and online shopping visuals",
            "fintech": "with financial technology and digital banking imagery",
            "health_tech": "with health technology and medical innovation visuals",
            "enterprise": "with enterprise and business technology themes",
            "data_science": "with data analytics and visualization elements",
            "business": "with professional business and technology setting",
        }

        category_style = category_styles.get(
            news.category.value, "with modern technology theme"
        )

        prompt = f"""A professional, high-quality news photograph depicting {news.title}.
The image should be in a modern tech news style, {category_style}.
Use a 16:9 aspect ratio suitable for YouTube videos and thumbnails.
The image should be clear, visually engaging, and represent the key concept of the news story.
Photorealistic style, professional lighting, no text or watermarks."""

        # Limit prompt length
        if len(prompt) > 1000:
            prompt = prompt[:997] + "..."

        return prompt

    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename for safe filesystem usage.

        Args:
            filename: Original filename

        Returns:
            Sanitized filename
        """
        import re

        # Remove invalid characters
        filename = re.sub(r'[<>:"/\\|?*]', "", filename)
        # Replace spaces with underscores
        filename = filename.replace(" ", "_")
        # Limit length
        filename = filename[:50]
        return filename

    def generate_batch(
        self,
        news_list: list[News],
        style: ImageStyle = ImageStyle.VIVID,
        quality: str = "hd",
    ) -> list[GeneratedImage]:
        """
        Generate images for multiple news articles.

        Args:
            news_list: List of news articles
            style: Image style
            quality: Image quality

        Returns:
            List of generated images
        """
        self.logger.info(f"Generating {len(news_list)} images in batch")

        images = []
        for i, news in enumerate(news_list, 1):
            try:
                self.logger.info(f"Processing {i}/{len(news_list)}: {news.title[:50]}...")
                image = self.generate(news, style, quality)
                images.append(image)

            except GenerationError as e:
                self.logger.error(f"Failed to generate image for news {i}: {e}")
                # Continue with next article
                continue

        self.logger.info(
            f"Batch generation complete: {len(images)}/{len(news_list)} successful, "
            f"total cost: ${self.total_cost:.3f}"
        )

        return images

    def create_thumbnail(
        self,
        news: News,
        title_text: Optional[str] = None,
    ) -> GeneratedImage:
        """
        Create YouTube thumbnail image.

        Args:
            news: News article
            title_text: Override title text

        Returns:
            Generated thumbnail image
        """
        title = title_text or news.title

        # Custom prompt for thumbnail
        prompt = f"""A bold, eye-catching YouTube thumbnail for a tech news video about: {title}
The image should be vibrant, high-contrast, and visually striking to grab attention.
16:9 aspect ratio, professional photography style, dramatic lighting.
Leave space at the top and bottom for text overlay.
No text or words in the image itself."""

        return self.generate(
            news,
            style=ImageStyle.VIVID,
            quality="hd",
            custom_prompt=prompt,
        )


def create_image_generator(output_dir: Optional[Path] = None, **kwargs) -> ImageGenerator:
    """
    Create image generator instance.

    Args:
        output_dir: Output directory for images

    Returns:
        ImageGenerator instance

    Example:
        >>> generator = create_image_generator()
        >>> image = generator.generate(news_article)
        >>> print(f"Image saved to: {image.local_path}")
    """
    return ImageGenerator(output_dir=output_dir, **kwargs)
