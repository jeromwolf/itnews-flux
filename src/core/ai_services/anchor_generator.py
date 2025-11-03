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

from src.core.ai_services.image_generator import ImageGenerator, GeneratedImage
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
        default="medium-length wavy hair with subtle highlights",
        description="Hairstyle (consistent)",
    )
    face_shape: str = Field(default="oval face", description="Face shape")
    eye_type: str = Field(default="bright expressive eyes", description="Eye type")
    facial_features: str = Field(
        default="friendly smile, professional demeanor, approachable yet authoritative",
        description="Facial characteristics",
    )

    # Personality & vibe
    personality: str = Field(
        default="modern, tech-savvy, energetic yet professional",
        description="Personality traits",
    )
    vibe: str = Field(
        default="MZ generation tech journalist, startup culture, innovation-focused",
        description="Overall vibe",
    )


class DailyOutfit(BaseModel):
    """매일 바뀌는 앵커 의상 및 스타일"""

    outfit: str = Field(..., description="Today's outfit description")
    background: str = Field(..., description="Studio background setting")
    expression: str = Field(..., description="Facial expression")
    accessories: Optional[str] = Field(None, description="Accessories (optional)")
    color_scheme: str = Field(..., description="Overall color scheme")


# 매일 다른 의상 조합 (7일 사이클)
OUTFIT_ROTATION = [
    DailyOutfit(
        outfit="navy blue blazer with white turtleneck, minimalist silver necklace",
        background="modern tech studio with blue LED panels and floating holographic displays",
        expression="confident smile, welcoming gesture",
        accessories="wireless earpiece, smartwatch",
        color_scheme="blue and white, professional tech aesthetic",
    ),
    DailyOutfit(
        outfit="burgundy red suit jacket with black top, gold accent jewelry",
        background="sleek newsroom with multiple screens showing tech headlines",
        expression="focused and engaged, explaining complex tech",
        accessories="tablet in hand, stylus",
        color_scheme="red and black, bold and authoritative",
    ),
    DailyOutfit(
        outfit="emerald green blazer with subtle tech-pattern scarf, modern cut",
        background="futuristic AI lab with glowing servers and digital displays",
        expression="excited about breaking news, animated",
        accessories="AR glasses hanging on collar",
        color_scheme="green and silver, innovation-focused",
    ),
    DailyOutfit(
        outfit="charcoal gray suit with electric blue shirt, contemporary style",
        background="minimalist studio with city skyline and tech company buildings",
        expression="serious professional demeanor, delivering important news",
        accessories="wireless microphone pin",
        color_scheme="gray and blue, corporate tech",
    ),
    DailyOutfit(
        outfit="pastel pink blazer with white blouse, modern feminine power suit",
        background="bright studio with soft lighting and tech-themed decorations",
        expression="warm and approachable smile, friendly energy",
        accessories="pearl earrings, smart ring",
        color_scheme="pink and white, soft yet professional",
    ),
    DailyOutfit(
        outfit="black turtleneck with beige oversized blazer, startup CEO style",
        background="industrial-chic studio with exposed tech, startup vibe",
        expression="casual yet professional, explaining trends",
        accessories="Apple Watch, minimalist jewelry",
        color_scheme="black and beige, modern minimalist",
    ),
    DailyOutfit(
        outfit="bright cobalt blue dress with structured blazer, tech conference ready",
        background="high-tech broadcasting studio with virtual reality displays",
        expression="energetic presentation mode, engaging audience",
        accessories="statement earrings, tech badge lanyard",
        color_scheme="cobalt blue and silver, vibrant tech energy",
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

        # Generate image
        image = self.image_gen.generate(
            prompt=prompt,
            size="1792x1024",  # 16:9 landscape for video
            quality="hd",
            style="natural",  # More realistic for news anchor
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

        image = self.image_gen.generate(
            prompt=prompt,
            size="1024x1024",  # Square for thumbnail (will crop/compose)
            quality="hd",
            style="natural",
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
Professional Korean tech news anchor in modern broadcast studio.

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
- Accessories: {outfit.accessories or 'no special accessories'}
- Color theme: {outfit.color_scheme}

SCENE: {scene_type.upper()}
- Pose: {scene['pose']}
- Camera: {scene['camera']}
- Mood: {scene['mood']}

TECHNICAL SPECIFICATIONS:
- Photo-realistic quality, professional broadcast photography
- Studio lighting: soft key light, subtle fill, rim light for depth
- 4K quality, shallow depth of field
- Modern Korean TV broadcast aesthetic
- Warm professional color grading
- Sharp focus on face, subtle background blur

STYLE REFERENCE:
- Modern Korean tech YouTube anchors (삼프로TV, 슈카월드 style)
- Professional yet approachable
- MZ generation appeal
- Tech startup culture vibe

CRITICAL CONSISTENCY RULES:
1. SAME FACE structure and features every time
2. SAME hairstyle (color, length, style)
3. SAME personality and energy
4. ONLY outfit, background, and accessories vary
5. Always professional news anchor quality

OUTPUT: 16:9 broadcast-quality image, ready for video production.
"""

        return prompt


# Convenience function
def generate_daily_anchor_images(
    date: Optional[datetime] = None,
) -> dict[str, GeneratedImage]:
    """
    Generate all anchor images needed for daily video.

    Args:
        date: Date for outfit selection (uses today if not provided)

    Returns:
        Dictionary with intro, news, outro anchor images
    """
    generator = AnchorImageGenerator()

    images = {
        "intro": generator.generate_anchor_image("intro", date=date),
        "news": generator.generate_anchor_image("news", date=date),
        "outro": generator.generate_anchor_image("outro", date=date),
        "thumbnail": generator.generate_thumbnail_anchor(date=date),
    }

    logger.info(f"Generated {len(images)} anchor images for daily video")

    return images
