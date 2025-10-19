"""
Lower Third component for Tech News Digest.

Generates professional news-style lower third subtitle bars with:
- Primary text (English)
- Secondary text (Korean)
- Customizable styling
- Animation support
"""

from pathlib import Path
from typing import Optional, Tuple

from PIL import Image, ImageDraw, ImageFont

from src.core.logging import get_logger
from src.video.models import LowerThirdConfig, VideoProjectConfig

logger = get_logger(__name__)


class LowerThirdGenerator:
    """
    Generator for lower third subtitle bars.

    Creates professional news-style subtitle graphics with:
    - Dual language support (English + Korean)
    - Customizable colors and fonts
    - Transparent background support
    """

    def __init__(
        self,
        video_config: VideoProjectConfig,
        fonts_dir: Optional[Path] = None,
    ):
        """
        Initialize lower third generator.

        Args:
            video_config: Video project configuration
            fonts_dir: Directory containing fonts (optional)
        """
        self.logger = get_logger(__name__)
        self.config = video_config
        self.fonts_dir = fonts_dir or Path("resources/fonts")

        self.logger.info(
            f"LowerThirdGenerator initialized "
            f"(resolution={video_config.resolution.value})"
        )

    def generate(
        self,
        lower_third_config: LowerThirdConfig,
        output_path: Optional[Path] = None,
    ) -> Image.Image:
        """
        Generate lower third image.

        Args:
            lower_third_config: Lower third configuration
            output_path: Optional path to save image

        Returns:
            PIL Image with transparency
        """
        self.logger.info(
            f"Generating lower third: '{lower_third_config.primary_text[:30]}...'"
        )

        # Calculate dimensions
        video_width = self.config.width
        video_height = self.config.height
        bar_height = int(video_height * lower_third_config.height_ratio)

        # Create image with transparency
        image = Image.new("RGBA", (video_width, bar_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        # Draw background bar
        background_color = self._hex_to_rgba(
            lower_third_config.background_color,
            lower_third_config.background_opacity,
        )
        draw.rectangle([(0, 0), (video_width, bar_height)], fill=background_color)

        # Load fonts
        try:
            primary_font = self._load_font(lower_third_config.primary_font_size)
            secondary_font = self._load_font(lower_third_config.secondary_font_size)
        except Exception as e:
            self.logger.warning(f"Failed to load custom font: {e}, using default")
            primary_font = ImageFont.load_default()
            secondary_font = ImageFont.load_default()

        # Calculate text positions
        padding = lower_third_config.padding
        text_color = lower_third_config.text_color
        max_width = video_width - (padding * 2)  # Available width for text

        # Primary text (English) - top with auto wrap
        primary_text_wrapped = self._wrap_text(
            lower_third_config.primary_text,
            primary_font,
            max_width,
            draw
        )
        primary_y = padding
        draw.text(
            (padding, primary_y),
            primary_text_wrapped,
            fill=text_color,
            font=primary_font,
        )

        # Secondary text (Korean) - bottom with auto wrap
        if lower_third_config.secondary_text:
            # Calculate position below primary text
            try:
                _, _, _, primary_height = draw.textbbox(
                    (0, 0), primary_text_wrapped, font=primary_font
                )
            except:
                primary_height = lower_third_config.primary_font_size * 1.5  # Estimate for wrapped text

            secondary_text_wrapped = self._wrap_text(
                lower_third_config.secondary_text,
                secondary_font,
                max_width,
                draw
            )

            secondary_y = primary_y + primary_height + 10  # 10px spacing
            draw.text(
                (padding, secondary_y),
                secondary_text_wrapped,
                fill=text_color,
                font=secondary_font,
            )

        # Save if output path provided
        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            image.save(output_path, "PNG")
            self.logger.info(f"Lower third saved to: {output_path}")

        return image

    def generate_simple(
        self,
        primary_text: str,
        secondary_text: Optional[str] = None,
        output_path: Optional[Path] = None,
    ) -> Image.Image:
        """
        Generate simple lower third with default settings.

        Args:
            primary_text: Primary text (English)
            secondary_text: Secondary text (Korean, optional)
            output_path: Optional path to save image

        Returns:
            PIL Image with transparency
        """
        config = LowerThirdConfig(
            primary_text=primary_text,
            secondary_text=secondary_text,
        )
        return self.generate(config, output_path)

    def _load_font(self, size: int) -> ImageFont.FreeTypeFont:
        """
        Load font with Korean support and fallback.

        Args:
            size: Font size

        Returns:
            Font object with Korean glyph support
        """
        # Try to load fonts with Korean support (in order of preference)
        font_paths = [
            # macOS - Korean fonts
            "/System/Library/Fonts/AppleSDGothicNeo.ttc",  # Best Korean font
            "/System/Library/AssetsV2/com_apple_MobileAsset_Font7/bad9b4bf17cf1669dde54184ba4431c22dcad27b.asset/AssetData/NanumGothic.ttc",
            "/Library/Fonts/NanumGothic.ttf",

            # Linux - Korean fonts
            "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",

            # Windows - Korean fonts
            "C:\\Windows\\Fonts\\malgun.ttf",  # Malgun Gothic
            "C:\\Windows\\Fonts\\gulim.ttc",   # Gulim

            # Fallback to English fonts (no Korean support)
            "/System/Library/Fonts/Helvetica.ttc",  # macOS
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  # Linux
            "C:\\Windows\\Fonts\\arial.ttf",  # Windows
        ]

        for font_path in font_paths:
            try:
                if Path(font_path).exists():
                    font = ImageFont.truetype(font_path, size)
                    self.logger.info(f"Loaded font: {Path(font_path).name} (size={size})")
                    return font
            except Exception as e:
                self.logger.debug(f"Failed to load {font_path}: {e}")
                continue

        # Fallback to default (warning: no Korean support)
        self.logger.warning(f"Using default font (size={size}) - Korean characters may not display correctly")
        return ImageFont.load_default()

    def _wrap_text(self, text: str, font: ImageFont.FreeTypeFont, max_width: int, draw: ImageDraw.ImageDraw) -> str:
        """
        Wrap text to fit within max width.

        Args:
            text: Text to wrap
            font: Font to use
            max_width: Maximum width in pixels
            draw: ImageDraw instance for measuring text

        Returns:
            Wrapped text with newlines
        """
        words = text.split()
        lines = []
        current_line = []

        for word in words:
            # Try adding word to current line
            test_line = ' '.join(current_line + [word])

            # Measure text width
            try:
                bbox = draw.textbbox((0, 0), test_line, font=font)
                text_width = bbox[2] - bbox[0]
            except:
                # Fallback: estimate width
                text_width = len(test_line) * (font.size if hasattr(font, 'size') else 12) * 0.6

            if text_width <= max_width:
                current_line.append(word)
            else:
                # Line is too long, start new line
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]

        # Add last line
        if current_line:
            lines.append(' '.join(current_line))

        return '\n'.join(lines)

    def _hex_to_rgba(self, hex_color: str, opacity: float = 1.0) -> Tuple[int, int, int, int]:
        """
        Convert hex color to RGBA tuple.

        Args:
            hex_color: Hex color string (e.g., "#1a1a1a")
            opacity: Opacity (0.0-1.0)

        Returns:
            RGBA tuple
        """
        # Remove '#' if present
        hex_color = hex_color.lstrip("#")

        # Convert to RGB
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)

        # Add alpha channel
        a = int(opacity * 255)

        return (r, g, b, a)

    def create_animated_sequence(
        self,
        config: LowerThirdConfig,
        output_dir: Path,
        fps: int = 30,
    ) -> list[Path]:
        """
        Create sequence of images for animation.

        Args:
            config: Lower third configuration
            output_dir: Output directory for frames
            fps: Frames per second

        Returns:
            List of frame image paths
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        fade_in_frames = int(config.fade_in_duration * fps)
        fade_out_frames = int(config.fade_out_duration * fps)

        frames = []

        # Fade in
        for i in range(fade_in_frames):
            opacity = (i + 1) / fade_in_frames * config.background_opacity
            frame_config = config.model_copy()
            frame_config.background_opacity = opacity

            frame_path = output_dir / f"frame_{len(frames):04d}.png"
            self.generate(frame_config, frame_path)
            frames.append(frame_path)

        # Display (full opacity)
        display_frames = int(config.display_duration * fps) if config.display_duration > 0 else 0
        for i in range(display_frames):
            frame_path = output_dir / f"frame_{len(frames):04d}.png"
            self.generate(config, frame_path)
            frames.append(frame_path)

        # Fade out
        for i in range(fade_out_frames):
            opacity = (1 - (i + 1) / fade_out_frames) * config.background_opacity
            frame_config = config.model_copy()
            frame_config.background_opacity = opacity

            frame_path = output_dir / f"frame_{len(frames):04d}.png"
            self.generate(frame_config, frame_path)
            frames.append(frame_path)

        self.logger.info(f"Generated {len(frames)} frames for animation")
        return frames


def create_lower_third_generator(
    video_config: VideoProjectConfig,
    **kwargs,
) -> LowerThirdGenerator:
    """
    Create lower third generator instance.

    Args:
        video_config: Video project configuration

    Returns:
        LowerThirdGenerator instance

    Example:
        >>> from src.video.models import VideoProjectConfig
        >>> config = VideoProjectConfig()
        >>> generator = create_lower_third_generator(config)
        >>> image = generator.generate_simple("Breaking News", "속보")
    """
    return LowerThirdGenerator(video_config, **kwargs)
