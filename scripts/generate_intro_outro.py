"""
Generate Intro/Outro Background Images for Tech News Digest.

Creates professional background images for video intro and outro sequences.

Usage:
    python scripts/generate_intro_outro.py --type intro
    python scripts/generate_intro_outro.py --type outro
    python scripts/generate_intro_outro.py --type both
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
from datetime import datetime

logger = get_logger(__name__)


# 프롬프트 정의
INTRO_PROMPT = """
Modern tech news studio background for 'Tech News Digest' YouTube channel.
Professional blue gradient from dark blue (#003d7a) to lighter blue (#0066cc).
Subtle geometric patterns and circuit board motifs in the background.
Clean, minimalist, high-tech aesthetic suitable for a news channel intro.
16:9 horizontal format (1792x1024).
No text or logos - leave space for title overlay in the center.
Photorealistic, professional studio lighting.
Depth of field with slight blur in background elements.
Modern, sleek, and trustworthy appearance.
"""

OUTRO_PROMPT = """
Minimalist thank you background for 'Tech News Digest' tech news channel.
Simple gradient background from light blue to white.
Clean and friendly aesthetic suitable for video outro.
16:9 horizontal format (1792x1024).
Space for 'Subscribe' call-to-action text overlay.
Professional but approachable design.
Subtle tech-themed decorative elements (optional).
Bright, positive, and welcoming atmosphere.
No text - leave center area clear for message.
"""


class IntroOutroGenerator:
    """Generate intro/outro background images."""

    def __init__(self, output_dir: Optional[Path] = None):
        """
        Initialize generator.

        Args:
            output_dir: Output directory (defaults to resources/)
        """
        self.logger = get_logger(__name__)
        self.output_dir = output_dir or (project_root / "resources")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Create image generator
        self.generator = ImageGenerator(output_dir=self.output_dir)

        self.logger.info(f"IntroOutroGenerator initialized (output_dir={self.output_dir})")

    def generate_intro(self, quality: str = "hd") -> Path:
        """
        Generate intro background image.

        Args:
            quality: Image quality (standard/hd)

        Returns:
            Path to generated image
        """
        self.logger.info("Generating intro background image...")
        self.logger.info(f"Prompt: {INTRO_PROMPT[:100]}...")

        # Create dummy news for generation
        dummy_news = News(
            title="Tech News Digest Intro",
            url="https://example.com",
            source=NewsSource.TECHCRUNCH,
            category=NewsCategory.TECH_GENERAL,
            published_at=datetime.utcnow(),
        )

        # Generate image
        image = self.generator.generate(
            news=dummy_news,
            style=ImageStyle.VIVID,
            quality=quality,
            custom_prompt=INTRO_PROMPT,
        )

        # Move to final location
        final_path = self.output_dir / "intro_background.png"

        import shutil
        shutil.copy(image.local_path, final_path)

        self.logger.info(f"✅ Intro image generated: {final_path}")
        self.logger.info(f"   Cost: ${image.total_cost:.2f}")
        self.logger.info(f"   Size: {image.size}")

        return final_path

    def generate_outro(self, quality: str = "hd") -> Path:
        """
        Generate outro background image.

        Args:
            quality: Image quality (standard/hd)

        Returns:
            Path to generated image
        """
        self.logger.info("Generating outro background image...")
        self.logger.info(f"Prompt: {OUTRO_PROMPT[:100]}...")

        # Create dummy news for generation
        dummy_news = News(
            title="Tech News Digest Outro",
            url="https://example.com",
            source=NewsSource.TECHCRUNCH,
            category=NewsCategory.TECH_GENERAL,
            published_at=datetime.utcnow(),
        )

        # Generate image
        image = self.generator.generate(
            news=dummy_news,
            style=ImageStyle.NATURAL,  # Outro는 Natural 스타일
            quality=quality,
            custom_prompt=OUTRO_PROMPT,
        )

        # Move to final location
        final_path = self.output_dir / "outro_background.png"

        import shutil
        shutil.copy(image.local_path, final_path)

        self.logger.info(f"✅ Outro image generated: {final_path}")
        self.logger.info(f"   Cost: ${image.total_cost:.2f}")
        self.logger.info(f"   Size: {image.size}")

        return final_path

    def generate_both(self, quality: str = "hd") -> tuple[Path, Path]:
        """
        Generate both intro and outro images.

        Args:
            quality: Image quality (standard/hd)

        Returns:
            Tuple of (intro_path, outro_path)
        """
        self.logger.info("=" * 60)
        self.logger.info("Generating Intro & Outro Background Images")
        self.logger.info("=" * 60)

        cost_estimate = 0.12 if quality == "hd" else 0.08
        total_estimate = cost_estimate * 2

        self.logger.info(f"Quality: {quality}")
        self.logger.info(f"Estimated cost: ${total_estimate:.2f} (2 images)")
        self.logger.info("")

        # Generate intro
        intro_path = self.generate_intro(quality)

        self.logger.info("")

        # Generate outro
        outro_path = self.generate_outro(quality)

        # Summary
        total_cost = self.generator.total_cost
        self.logger.info("")
        self.logger.info("=" * 60)
        self.logger.info("✅ Generation Complete!")
        self.logger.info("=" * 60)
        self.logger.info(f"Intro: {intro_path}")
        self.logger.info(f"Outro: {outro_path}")
        self.logger.info(f"Total cost: ${total_cost:.2f}")
        self.logger.info("")

        return intro_path, outro_path


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate intro/outro background images for Tech News Digest"
    )
    parser.add_argument(
        "--type",
        type=str,
        choices=["intro", "outro", "both"],
        default="both",
        help="Which image(s) to generate (default: both)",
    )
    parser.add_argument(
        "--quality",
        type=str,
        choices=["standard", "hd"],
        default="hd",
        help="Image quality (default: hd)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Custom output directory (default: resources/)",
    )

    args = parser.parse_args()

    try:
        # Create generator
        generator = IntroOutroGenerator(output_dir=args.output_dir)

        # Generate based on type
        if args.type == "intro":
            intro_path = generator.generate_intro(quality=args.quality)
            logger.info(f"\n✅ Intro image saved to: {intro_path}")

        elif args.type == "outro":
            outro_path = generator.generate_outro(quality=args.quality)
            logger.info(f"\n✅ Outro image saved to: {outro_path}")

        elif args.type == "both":
            intro_path, outro_path = generator.generate_both(quality=args.quality)
            logger.info(f"\n✅ Images saved to: {generator.output_dir}")

    except Exception as e:
        logger.error(f"Generation failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
