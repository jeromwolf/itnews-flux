#!/usr/bin/env python3
"""
Generate AI ON channel branding assets.

Creates professional intro/outro backgrounds for YouTube channel "AI ON".
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.ai_services import create_image_generator
from src.core.logging import get_logger

logger = get_logger(__name__)


# AI ON 인트로 프롬프트
INTRO_PROMPT = """
Professional YouTube channel intro background for 'AI ON' - an AI and tech news channel.

Design concept:
- Futuristic AI theme with neural network visualization
- Abstract digital data streams and connections flowing
- Modern tech workspace aesthetic with holographic elements
- Color palette: Deep blue (#0047AB) to electric cyan (#00D9FF) gradient
- Subtle geometric patterns representing AI algorithms
- Clean, professional, and sophisticated look
- Background should leave center space clear for text overlay

Technical requirements:
- High contrast for text readability
- 16:9 horizontal format (1792x1024 pixels)
- Professional broadcast quality
- Minimalist but impactful design
- No text or logos in the image (will be added separately)

Style: Modern tech broadcast, similar to WIRED or The Verge intro screens
"""

OUTRO_PROMPT = """
Professional YouTube channel outro background for 'AI ON' tech news channel.

Design concept:
- Clean, minimalist thank you screen
- Soft gradient background from light blue to white
- Abstract tech patterns in the background (very subtle)
- Professional and calming atmosphere
- Space for "AI ON" text and subscribe call-to-action
- Modern corporate tech aesthetic

Technical requirements:
- Welcoming and professional feel
- 16:9 horizontal format (1792x1024 pixels)
- High contrast for text overlay
- Subtle depth with layered elements
- No text or logos in the image (will be added separately)

Style: Clean tech company presentation, Apple keynote aesthetic
"""


def main():
    """Generate AI ON branding assets."""
    logger.info("🎨 Generating AI ON channel branding assets...")

    # Create image generator
    generator = create_image_generator()

    # Output directory
    resources_dir = Path("resources")
    resources_dir.mkdir(exist_ok=True)

    # Create dummy news object for ImageGenerator API
    from src.news.models import News, NewsSource, NewsCategory
    from datetime import datetime
    from pydantic import HttpUrl

    dummy_news = News(
        title="AI ON Intro",
        url=HttpUrl("https://example.com"),
        source=NewsSource.TECHCRUNCH,
        category=NewsCategory.AI_ML,
        published_at=datetime.now(),
    )

    # Generate intro background
    logger.info("\n📺 Generating intro background...")
    logger.info(f"Prompt: {INTRO_PROMPT[:100]}...")

    intro_result = generator.generate(
        news=dummy_news,
        custom_prompt=INTRO_PROMPT,
        quality="hd",
    )

    # Move to resources directory
    import shutil
    intro_path = resources_dir / "ai_on_intro.png"
    shutil.copy(intro_result.local_path, intro_path)

    logger.info(f"✅ Intro generated: {intro_path}")
    logger.info(f"   Cost: ${intro_result.total_cost:.4f}")

    # Generate outro background
    logger.info("\n📺 Generating outro background...")
    logger.info(f"Prompt: {OUTRO_PROMPT[:100]}...")

    dummy_news.title = "AI ON Outro"
    outro_result = generator.generate(
        news=dummy_news,
        custom_prompt=OUTRO_PROMPT,
        quality="hd",
    )

    # Move to resources directory
    outro_path = resources_dir / "ai_on_outro.png"
    shutil.copy(outro_result.local_path, outro_path)

    logger.info(f"✅ Outro generated: {outro_path}")
    logger.info(f"   Cost: ${outro_result.total_cost:.4f}")

    # Summary
    total_cost = intro_result.total_cost + outro_result.total_cost
    logger.info(f"\n🎉 AI ON branding complete!")
    logger.info(f"   Intro: {intro_path}")
    logger.info(f"   Outro: {outro_path}")
    logger.info(f"   Total cost: ${total_cost:.4f}")


if __name__ == "__main__":
    main()
