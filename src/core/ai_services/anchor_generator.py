"""
News anchor character image generator.

Generates consistent AI anchor character images using DALL-E 3.
Character: 이서연 (Lee Seo-yeon) - Modern tech news anchor
"""

import hashlib
import random
from datetime import datetime
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field

from src.core.ai_services.image_generator import ImageGenerator, GeneratedImage, ImageStyle
from src.core.logging import get_logger

logger = get_logger(__name__)


class AnchorProfile(BaseModel):
    """이서연 앵커 캐릭터 프로필"""

    name: str = Field(default="이서연", description="Anchor name")
    name_en: str = Field(default="Lee Seo-yeon", description="Anchor name (English)")

    # Core identity (NEVER changes - consistency is key)
    gender: str = Field(default="female", description="Gender")
    age: str = Field(default="late 20s", description="Age description")
    ethnicity: str = Field(default="Korean", description="Ethnicity")
    hairstyle: str = Field(
        default="flowing wavy hair with warm orange-peachy highlights, animated style",
        description="Hairstyle (consistent)",
    )
    face_shape: str = Field(default="soft oval face with gentle features", description="Face shape")
    eye_type: str = Field(default="large expressive eyes, anime-inspired", description="Eye type")
    facial_features: str = Field(
        default="warm friendly smile, round glasses (optional), youthful and approachable",
        description="Facial characteristics",
    )
    style_aesthetic: str = Field(
        default="3D character illustration, semi-realistic anime style, soft digital painting",
        description="Art style",
    )

    # Personality & vibe
    personality: str = Field(
        default="futuristic, tech-enthusiast, friendly and relatable",
        description="Personality traits",
    )
    vibe: str = Field(
        default="Gen Z tech creator, digital native, cozy futurism meets cyberpunk lite",
        description="Overall vibe",
    )


class DailyOutfit(BaseModel):
    """매일 바뀌는 앵커 의상 및 스타일"""

    outfit: str = Field(..., description="Today's outfit description")
    background: str = Field(..., description="Studio background setting")
    expression: str = Field(..., description="Facial expression")
    accessories: Optional[str] = Field(None, description="Accessories (optional)")
    color_scheme: str = Field(..., description="Overall color scheme")


# 매일 다른 의상 조합 (7일 사이클) - 미래지향적 스타일
OUTFIT_ROTATION = [
    DailyOutfit(
        outfit="white oversized hoodie with holographic tech patterns, casual comfort",
        background="cozy futuristic room with soft neon lighting, floating digital screens, bokeh effect",
        expression="warm welcoming smile, friendly wave",
        accessories="round wireless earbuds, smart bracelet with glowing display",
        color_scheme="white and soft blue glow, cozy tech aesthetic",
    ),
    DailyOutfit(
        outfit="pastel gradient sweater (pink to purple), relaxed modern style",
        background="dreamy digital workspace with particle effects and soft lights",
        expression="excited and animated, explaining cool tech",
        accessories="AR glasses perched on head, smartwatch",
        color_scheme="pastel gradients, ethereal and friendly",
    ),
    DailyOutfit(
        outfit="mint green tech jacket with subtle circuit patterns, street style",
        background="cyberpunk-lite cafe with neon signs and holographic menus",
        expression="casual smile, pointing at floating UI element",
        accessories="wireless earbuds, digital wristband",
        color_scheme="mint green and warm orange accents, vibrant energy",
    ),
    DailyOutfit(
        outfit="lavender oversized cardigan over white tee, cozy creator",
        background="home studio setup with RGB lighting and floating widgets",
        expression="friendly and approachable, like talking to a friend",
        accessories="headphones around neck, phone with holographic display",
        color_scheme="lavender and warm whites, comfort tech",
    ),
    DailyOutfit(
        outfit="coral pink hoodie with tech brand logo, Gen Z style",
        background="futuristic library with digital books floating, warm lighting",
        expression="excited discovery expression, 'aha!' moment",
        accessories="smart glasses, glowing earrings",
        color_scheme="coral pink and soft gold, playful innovation",
    ),
    DailyOutfit(
        outfit="cream turtleneck with high-tech vest, minimal chic",
        background="sleek minimalist space with floating holographic news feeds",
        expression="calm and focused, explaining clearly",
        accessories="minimal tech jewelry, smart ring glowing softly",
        color_scheme="cream and silver, sophisticated simplicity",
    ),
    DailyOutfit(
        outfit="electric blue bomber jacket over graphic tee, streetwear tech",
        background="urban rooftop with city lights and floating AR displays",
        expression="energetic and dynamic, full of enthusiasm",
        accessories="AR visor pushed up, multiple smart devices",
        color_scheme="electric blue and neon accents, high energy future",
    ),
]


class AnchorImageGenerator:
    """
    Generates consistent news anchor character images.

    Uses DALL-E 3 to create a consistent AI anchor character with
    daily variations in outfit and background while maintaining
    the same face and personality.
    """

    def __init__(
        self,
        profile: Optional[AnchorProfile] = None,
        image_generator: Optional[ImageGenerator] = None,
    ):
        """
        Initialize anchor image generator.

        Args:
            profile: Anchor character profile (uses default 이서연 if not provided)
            image_generator: DALL-E image generator instance
        """
        self.profile = profile or AnchorProfile()
        self.image_gen = image_generator or ImageGenerator()
        self.logger = get_logger(__name__)

        self.logger.info(f"AnchorImageGenerator initialized: {self.profile.name}")

    def get_daily_outfit(self, date: Optional[datetime] = None) -> DailyOutfit:
        """
        Get today's outfit from rotation.

        Args:
            date: Date to get outfit for (uses today if not provided)

        Returns:
            DailyOutfit for the specified date
        """
        if date is None:
            date = datetime.now()

        # Use day of week for consistent rotation (0=Monday, 6=Sunday)
        day_index = date.weekday()
        outfit = OUTFIT_ROTATION[day_index % len(OUTFIT_ROTATION)]

        self.logger.info(
            f"Selected outfit for {date.strftime('%A')}: {outfit.outfit[:50]}..."
        )

        return outfit

    def generate_anchor_image(
        self,
        scene_type: str = "intro",
        custom_outfit: Optional[DailyOutfit] = None,
        date: Optional[datetime] = None,
    ) -> GeneratedImage:
        """
        Generate anchor character image.

        Args:
            scene_type: Type of scene (intro, news, outro, thumbnail)
            custom_outfit: Custom outfit (uses daily rotation if not provided)
            date: Date for outfit selection (uses today if not provided)

        Returns:
            Generated anchor image
        """
        # Get outfit for today
        outfit = custom_outfit or self.get_daily_outfit(date)

        # Build detailed prompt for consistency
        prompt = self._build_prompt(scene_type, outfit)

        self.logger.info(f"Generating {scene_type} anchor image: {self.profile.name}")
        self.logger.debug(f"Outfit: {outfit.outfit}")

        # Create a dummy News object for ImageGenerator compatibility
        from src.news.models import News
        from datetime import datetime, timezone

        dummy_news = News(
            title=f"{self.profile.name} Anchor - {scene_type}",
            summary=f"News anchor image for {scene_type} scene",
            content="",
            url="https://example.com/anchor",
            source="techcrunch",  # Use valid source enum
            published_at=datetime.now(timezone.utc),
        )

        # Generate image using custom_prompt
        image = self.image_gen.generate(
            news=dummy_news,
            style=ImageStyle.NATURAL,  # More realistic for news anchor
            quality="hd",
            custom_prompt=prompt,
        )

        return image

    def generate_thumbnail_anchor(
        self,
        custom_outfit: Optional[DailyOutfit] = None,
        date: Optional[datetime] = None,
    ) -> GeneratedImage:
        """
        Generate anchor image optimized for YouTube thumbnail.

        Args:
            custom_outfit: Custom outfit (uses daily rotation if not provided)
            date: Date for outfit selection

        Returns:
            Generated thumbnail anchor image (portrait orientation)
        """
        outfit = custom_outfit or self.get_daily_outfit(date)

        # Thumbnail-specific prompt (close-up, engaging)
        prompt = f"""
Professional Korean tech news anchor close-up portrait for YouTube thumbnail.

CHARACTER (CRITICAL - MUST BE CONSISTENT):
- {self.profile.name_en}, {self.profile.gender}, {self.profile.age}
- {self.profile.hairstyle}
- {self.profile.face_shape}, {self.profile.eye_type}
- {self.profile.facial_features}
- {self.profile.personality}

TODAY'S STYLE:
- Outfit: {outfit.outfit}
- Expression: {outfit.expression}
- Accessories: {outfit.accessories or 'minimal jewelry'}
- Color scheme: {outfit.color_scheme}

FRAMING & COMPOSITION:
- Close-up portrait (shoulders and head visible)
- Slight angle (3/4 view), engaging eye contact with camera
- Professional studio lighting with soft fill light
- Shallow depth of field, background slightly blurred
- {outfit.background} (subtle, not distracting)

STYLE:
- Photo-realistic, high-end broadcast quality
- 4K resolution, professional color grading
- Modern Korean broadcast aesthetics
- Energetic yet professional vibe
- Perfect for YouTube thumbnail (eye-catching, trustworthy)

CRITICAL: Same person's face every time, only outfit and background vary.
Reference: Modern Korean tech YouTuber/anchor style, MZ generation appeal.
"""

        self.logger.info(f"Generating thumbnail anchor: {self.profile.name}")

        # Create a dummy News object for ImageGenerator compatibility
        from src.news.models import News
        from datetime import datetime, timezone

        dummy_news = News(
            title=f"{self.profile.name} Anchor - Thumbnail",
            summary="News anchor thumbnail portrait",
            content="",
            url="https://example.com/anchor/thumbnail",
            source="techcrunch",  # Use valid source enum
            published_at=datetime.now(timezone.utc),
        )

        # Generate image using custom_prompt
        image = self.image_gen.generate(
            news=dummy_news,
            style=ImageStyle.NATURAL,  # More realistic for news anchor
            quality="hd",
            custom_prompt=prompt,
        )

        return image

    def _build_prompt(self, scene_type: str, outfit: DailyOutfit) -> str:
        """
        Build detailed DALL-E prompt for anchor image.

        Args:
            scene_type: Scene type (intro, news, outro, thumbnail)
            outfit: Today's outfit configuration

        Returns:
            Complete DALL-E prompt
        """
        # Scene-specific settings
        scene_configs = {
            "intro": {
                "pose": "welcoming gesture with open hand, warm greeting posture",
                "camera": "medium shot, slightly low angle for authority",
                "mood": "energetic and inviting, starting the show",
            },
            "news": {
                "pose": "professional anchor posture, hands on desk or gesturing to explain",
                "camera": "medium shot, straight-on professional angle",
                "mood": "focused and informative, delivering news",
            },
            "outro": {
                "pose": "friendly wave or thumbs up, closing gesture",
                "camera": "medium shot, warm and personal",
                "mood": "warm farewell, encouraging viewers to return",
            },
            "thumbnail": {
                "pose": "confident pose with slight lean forward, engaging directly",
                "camera": "close-up portrait, eye-level",
                "mood": "vibrant energy, click-worthy charisma",
            },
        }

        scene = scene_configs.get(scene_type, scene_configs["news"])

        prompt = f"""
Futuristic Korean tech content creator character in cozy digital space.

CHARACTER IDENTITY (CRITICAL - MUST BE EXACTLY THE SAME EVERY TIME):
- Name: {self.profile.name_en} ({self.profile.name})
- Gender: {self.profile.gender}, Age: {self.profile.age}
- Ethnicity: {self.profile.ethnicity}
- Hair: {self.profile.hairstyle}
- Face: {self.profile.face_shape}, {self.profile.eye_type}
- Features: {self.profile.facial_features}
- Personality: {self.profile.personality}
- Vibe: {self.profile.vibe}

TODAY'S VARIATION (ONLY THESE CHANGE):
- Outfit: {outfit.outfit}
- Background: {outfit.background}
- Expression: {outfit.expression}
- Accessories: {outfit.accessories or 'minimal tech accessories'}
- Color theme: {outfit.color_scheme}

SCENE: {scene_type.upper()}
- Pose: {scene['pose']}
- Camera: {scene['camera']}
- Mood: {scene['mood']}

ART STYLE & TECHNICAL SPECIFICATIONS:
- {self.profile.style_aesthetic}
- 3D character illustration with soft lighting and dreamy atmosphere
- Semi-realistic anime/webtoon style, modern digital art
- Warm color palette with soft gradients and bokeh effects
- Cinematic lighting: soft key light, gentle rim light, atmospheric glow
- Sharp focus on character, dreamy blurred background with particles
- Cozy futurism aesthetic - blend of technology and warmth

STYLE REFERENCE:
- Modern Korean digital artists (Loish, Zeronis style influence)
- Genshin Impact / Honkai Star Rail character quality
- Studio Ghibli warmth meets cyberpunk aesthetics
- Artstation trending style, high-quality character design
- Gen Z tech creator vibe, relatable and friendly

CRITICAL CONSISTENCY RULES:
1. SAME FACE structure and features every time - this is crucial!
2. SAME hairstyle (flowing wavy orange-peachy hair, animated style)
3. SAME art style (3D illustration, semi-realistic)
4. SAME character essence and personality
5. ONLY outfit, background, and accessories vary
6. Always maintain illustration/anime quality, NOT photo-realistic

IMPORTANT:
- This is NOT a photograph - it's a character illustration
- Soft, dreamy, and approachable aesthetic
- Tech-forward but warm and friendly
- Perfect for Gen Z audience appeal

OUTPUT: 16:9 high-quality character illustration, ready for video production.
"""

        return prompt


# Convenience function
def generate_daily_anchor_images(
    date: Optional[datetime] = None,
    use_consistent_image: bool = True,
) -> dict[str, GeneratedImage]:
    """
    Generate all anchor images needed for daily video.

    Args:
        date: Date for outfit selection (uses today if not provided)
        use_consistent_image: If True, use same image for all scenes (default: True)

    Returns:
        Dictionary with intro, news, outro, thumbnail anchor images
    """
    from pathlib import Path

    if use_consistent_image:
        # Use the same intro image for all scenes (character consistency)
        logger.info("Using consistent anchor image for all scenes")

        # Find the consistent anchor image
        intro_path = Path("output/images/anchor_consistent_intro.png")

        if not intro_path.exists():
            logger.warning(f"Consistent image not found: {intro_path}")
            logger.info("Generating new intro image...")
            generator = AnchorImageGenerator()
            intro_image = generator.generate_anchor_image("intro", date=date)
        else:
            # Create GeneratedImage object from existing file
            intro_image = GeneratedImage(
                local_path=str(intro_path),
                url="https://localhost/anchor_consistent_intro.png",  # Dummy URL for reused image
                prompt="Consistent anchor character (reused)",
                size="1792x1024",
                cost=0.0,  # No cost for reusing existing image
            )

        # Reuse same image for all scenes
        images = {
            "intro": intro_image,
            "news": intro_image,
            "outro": intro_image,
            "thumbnail": intro_image,
        }

        logger.info(f"Using {intro_path} for all 4 scenes (100% character consistency)")
    else:
        # Generate different images for each scene (original behavior)
        logger.info("Generating unique images for each scene")
        generator = AnchorImageGenerator()

        images = {
            "intro": generator.generate_anchor_image("intro", date=date),
            "news": generator.generate_anchor_image("news", date=date),
            "outro": generator.generate_anchor_image("outro", date=date),
            "thumbnail": generator.generate_thumbnail_anchor(date=date),
        }

        logger.info(f"Generated {len(images)} unique anchor images")

    return images
