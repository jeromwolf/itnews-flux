"""
YouTube Thumbnail Generator for Tech News Digest.

Generates eye-catching thumbnails with:
- Background image (AI-generated, darkened)
- News title with text box overlay
- Branding elements (logo, channel name)
- Professional design optimized for CTR
"""

import hashlib
import json
from pathlib import Path
from typing import Optional

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
from pydantic import BaseModel, Field

from ..core.logging import get_logger

logger = get_logger(__name__)


class ThumbnailConfig(BaseModel):
    """Configuration for thumbnail generation."""

    # Size
    width: int = Field(1280, description="Thumbnail width (YouTube recommended)")
    height: int = Field(720, description="Thumbnail height (YouTube recommended)")

    # Background
    background_opacity: float = Field(
        0.5, ge=0.0, le=1.0, description="Background image opacity (0=black, 1=full)"
    )
    blur_radius: int = Field(
        0, ge=0, le=10, description="Background blur radius (0=no blur)"
    )

    # Text box
    text_box_color: str = Field("#1E40AF", description="Text box background color (hex)")
    text_box_opacity: float = Field(
        0.85, ge=0.0, le=1.0, description="Text box opacity"
    )
    text_box_padding: int = Field(40, description="Text box padding (pixels)")
    text_box_margin: int = Field(60, description="Text box margin from edges (pixels)")

    # Title text
    title_font_size: int = Field(72, description="Title font size")
    title_color: str = Field("#FFFFFF", description="Title text color (hex)")
    title_max_lines: int = Field(3, description="Maximum lines for title")
    title_line_spacing: int = Field(10, description="Line spacing for title")

    # Subtitle text (optional)
    show_subtitle: bool = Field(True, description="Show subtitle (category/date)")
    subtitle_text: Optional[str] = Field(None, description="Subtitle text")
    subtitle_font_size: int = Field(36, description="Subtitle font size")
    subtitle_color: str = Field("#E0E0E0", description="Subtitle text color (hex)")

    # Branding
    brand_text: str = Field("AI ON", description="Brand text (customizable)")
    brand_font_size: int = Field(48, description="Brand text font size")
    brand_color: str = Field("#FFFFFF", description="Brand text color (hex)")
    brand_position: str = Field(
        "bottom-left", description="Brand position (bottom-left, bottom-right, top-left, top-right)"
    )
    brand_margin: int = Field(30, description="Brand margin from edges (pixels)")

    # Logo (optional)
    logo_path: Optional[Path] = Field(None, description="Path to logo image")
    logo_position: str = Field(
        "bottom-right", description="Logo position (bottom-left, bottom-right, top-left, top-right)"
    )
    logo_size: int = Field(80, description="Logo size (max width/height)")
    logo_margin: int = Field(30, description="Logo margin from edges (pixels)")

    # Effects
    text_shadow: bool = Field(True, description="Add shadow to text")
    text_stroke: bool = Field(True, description="Add stroke to text")
    text_stroke_width: int = Field(3, description="Text stroke width")


class ThumbnailGenerator:
    """
    Generates YouTube thumbnails for news videos.

    Features:
    - Background image with darkening/blur
    - Centered text box with news title
    - Branding elements (customizable text + logo)
    - Optimized for YouTube CTR
    """

    def __init__(self, config: Optional[ThumbnailConfig] = None, config_file: Optional[Path] = None):
        """
        Initialize thumbnail generator.

        Args:
            config: Thumbnail configuration (optional, uses defaults if not provided)
            config_file: Path to JSON config file (optional, e.g., config/thumbnail_config.json)
        """
        # Load from config file if provided
        if config_file and config_file.exists():
            logger.info(f"Loading thumbnail config from {config_file}")
            self.config = self._load_config_from_file(config_file)
        elif config:
            self.config = config
        else:
            # Try default config file
            default_config = Path("config/thumbnail_config.json")
            if default_config.exists():
                logger.info(f"Loading default thumbnail config from {default_config}")
                self.config = self._load_config_from_file(default_config)
            else:
                self.config = ThumbnailConfig()

        self.cache_dir = Path("output/thumbnails")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        logger.info(
            f"ThumbnailGenerator initialized: {self.config.width}x{self.config.height}, "
            f"brand='{self.config.brand_text}', logo={self.config.logo_path is not None}"
        )

    def _load_config_from_file(self, config_file: Path) -> ThumbnailConfig:
        """
        Load configuration from JSON file.

        Args:
            config_file: Path to JSON config file

        Returns:
            ThumbnailConfig instance
        """
        with open(config_file, "r", encoding="utf-8") as f:
            config_data = json.load(f)

        # Convert logo_path string to Path if present
        if "logo_path" in config_data and config_data["logo_path"]:
            config_data["logo_path"] = Path(config_data["logo_path"])

        return ThumbnailConfig(**config_data)

    def generate(
        self,
        title: str,
        background_image_path: Path,
        output_path: Optional[Path] = None,
        subtitle: Optional[str] = None,
        use_cache: bool = True,
    ) -> Path:
        """
        Generate YouTube thumbnail.

        Args:
            title: News title (will be wrapped to fit)
            background_image_path: Path to background image (AI-generated)
            output_path: Output file path (optional, auto-generated if not provided)
            subtitle: Subtitle text (optional, e.g., category or date)
            use_cache: Use cached thumbnail if available

        Returns:
            Path to generated thumbnail
        """
        logger.info(f"Generating thumbnail: {title[:50]}...")

        # Generate cache key
        cache_key = self._generate_cache_key(title, background_image_path, subtitle)
        cached_path = self.cache_dir / f"{cache_key}.jpg"

        # Check cache
        if use_cache and cached_path.exists():
            logger.info(f"Using cached thumbnail: {cached_path}")
            return cached_path

        # Determine output path
        if output_path is None:
            output_path = cached_path

        # Load and prepare background
        background = self._prepare_background(background_image_path)

        # Create drawing context
        draw = ImageDraw.Draw(background, "RGBA")

        # Draw text box and title
        self._draw_text_box_and_title(draw, background, title, subtitle)

        # Draw branding
        self._draw_branding(background, draw)

        # Draw logo (if configured)
        if self.config.logo_path and self.config.logo_path.exists():
            self._draw_logo(background)

        # Convert to RGB and save
        background = background.convert("RGB")
        background.save(output_path, "JPEG", quality=95, optimize=True)

        logger.info(f"Thumbnail generated: {output_path}")
        return output_path

    def _generate_cache_key(
        self, title: str, background_image_path: Path, subtitle: Optional[str]
    ) -> str:
        """Generate cache key for thumbnail."""
        content = f"{title}_{background_image_path.name}_{subtitle or ''}"
        return hashlib.md5(content.encode()).hexdigest()

    def _prepare_background(self, image_path: Path) -> Image.Image:
        """
        Prepare background image.

        - Resize to thumbnail size
        - Apply darkening
        - Apply blur (optional)

        Args:
            image_path: Path to background image

        Returns:
            Prepared background image
        """
        # Load image
        img = Image.open(image_path).convert("RGBA")

        # Resize to thumbnail size (crop to fit)
        img = self._resize_and_crop(img, self.config.width, self.config.height)

        # Apply blur (if configured)
        if self.config.blur_radius > 0:
            img = img.filter(ImageFilter.GaussianBlur(radius=self.config.blur_radius))

        # Apply darkening overlay
        if self.config.background_opacity < 1.0:
            # Create dark overlay
            overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
            dark_alpha = int(255 * (1.0 - self.config.background_opacity))
            overlay.paste((0, 0, 0, dark_alpha), (0, 0, img.size[0], img.size[1]))

            # Composite
            img = Image.alpha_composite(img, overlay)

        return img

    def _resize_and_crop(self, img: Image.Image, target_w: int, target_h: int) -> Image.Image:
        """
        Resize image to target size, cropping to fit (center crop).

        Args:
            img: Input image
            target_w: Target width
            target_h: Target height

        Returns:
            Resized and cropped image
        """
        img_ratio = img.width / img.height
        target_ratio = target_w / target_h

        if img_ratio > target_ratio:
            # Image is wider, scale by height and crop width
            new_h = target_h
            new_w = int(img.width * (target_h / img.height))
        else:
            # Image is taller, scale by width and crop height
            new_w = target_w
            new_h = int(img.height * (target_w / img.width))

        # Resize
        img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

        # Center crop
        left = (new_w - target_w) // 2
        top = (new_h - target_h) // 2
        right = left + target_w
        bottom = top + target_h

        return img.crop((left, top, right, bottom))

    def _draw_text_box_and_title(
        self,
        draw: ImageDraw.ImageDraw,
        img: Image.Image,
        title: str,
        subtitle: Optional[str],
    ) -> None:
        """
        Draw text box and title in center of thumbnail.

        Args:
            draw: ImageDraw context
            img: Image to draw on
            title: News title
            subtitle: Subtitle text (optional)
        """
        # Load fonts
        try:
            title_font = ImageFont.truetype("Arial", self.config.title_font_size)
            subtitle_font = ImageFont.truetype("Arial", self.config.subtitle_font_size)
        except OSError:
            # Fallback to default font
            logger.warning("Arial font not found, using default font")
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()

        # Wrap title text
        max_width = self.config.width - 2 * (
            self.config.text_box_margin + self.config.text_box_padding
        )
        wrapped_lines = self._wrap_text(title, title_font, max_width)

        # Limit lines
        if len(wrapped_lines) > self.config.title_max_lines:
            wrapped_lines = wrapped_lines[: self.config.title_max_lines]
            wrapped_lines[-1] = wrapped_lines[-1][:-3] + "..."

        # Calculate text dimensions
        line_heights = [
            draw.textbbox((0, 0), line, font=title_font)[3] for line in wrapped_lines
        ]
        total_text_height = sum(line_heights) + self.config.title_line_spacing * (
            len(wrapped_lines) - 1
        )

        # Add subtitle height if present
        if subtitle and self.config.show_subtitle:
            subtitle_bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
            subtitle_height = subtitle_bbox[3] - subtitle_bbox[1]
            total_text_height += subtitle_height + 20  # 20px gap

        # Calculate text box dimensions
        text_box_height = total_text_height + 2 * self.config.text_box_padding
        text_box_width = self.config.width - 2 * self.config.text_box_margin

        # Center position
        text_box_x = self.config.text_box_margin
        text_box_y = (self.config.height - text_box_height) // 2

        # Draw text box (rounded rectangle with transparency)
        self._draw_rounded_rectangle(
            draw,
            [(text_box_x, text_box_y), (text_box_x + text_box_width, text_box_y + text_box_height)],
            radius=20,
            fill=self._hex_to_rgba(
                self.config.text_box_color, self.config.text_box_opacity
            ),
        )

        # Draw title text
        current_y = text_box_y + self.config.text_box_padding
        for line in wrapped_lines:
            # Get text bbox for centering
            bbox = draw.textbbox((0, 0), line, font=title_font)
            text_width = bbox[2] - bbox[0]
            text_x = (self.config.width - text_width) // 2

            # Draw text with stroke/shadow
            if self.config.text_stroke:
                # Draw stroke
                for offset_x in range(-self.config.text_stroke_width, self.config.text_stroke_width + 1):
                    for offset_y in range(-self.config.text_stroke_width, self.config.text_stroke_width + 1):
                        if offset_x != 0 or offset_y != 0:
                            draw.text(
                                (text_x + offset_x, current_y + offset_y),
                                line,
                                font=title_font,
                                fill=(0, 0, 0, 255),
                            )

            # Draw main text
            draw.text(
                (text_x, current_y),
                line,
                font=title_font,
                fill=self._hex_to_rgba(self.config.title_color, 1.0),
            )

            # Move to next line
            line_height = draw.textbbox((0, 0), line, font=title_font)[3]
            current_y += line_height + self.config.title_line_spacing

        # Draw subtitle
        if subtitle and self.config.show_subtitle:
            current_y += 20  # Gap
            bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
            text_width = bbox[2] - bbox[0]
            text_x = (self.config.width - text_width) // 2

            draw.text(
                (text_x, current_y),
                subtitle,
                font=subtitle_font,
                fill=self._hex_to_rgba(self.config.subtitle_color, 1.0),
            )

    def _draw_branding(self, img: Image.Image, draw: ImageDraw.ImageDraw) -> None:
        """
        Draw branding text (e.g., 'AI ON').

        Args:
            img: Image to draw on
            draw: ImageDraw context
        """
        try:
            brand_font = ImageFont.truetype("Arial", self.config.brand_font_size)
        except OSError:
            brand_font = ImageFont.load_default()

        # Calculate position
        bbox = draw.textbbox((0, 0), self.config.brand_text, font=brand_font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        if self.config.brand_position == "bottom-left":
            x = self.config.brand_margin
            y = self.config.height - text_height - self.config.brand_margin
        elif self.config.brand_position == "bottom-right":
            x = self.config.width - text_width - self.config.brand_margin
            y = self.config.height - text_height - self.config.brand_margin
        elif self.config.brand_position == "top-left":
            x = self.config.brand_margin
            y = self.config.brand_margin
        else:  # top-right
            x = self.config.width - text_width - self.config.brand_margin
            y = self.config.brand_margin

        # Draw text with stroke
        if self.config.text_stroke:
            for offset_x in range(-2, 3):
                for offset_y in range(-2, 3):
                    if offset_x != 0 or offset_y != 0:
                        draw.text(
                            (x + offset_x, y + offset_y),
                            self.config.brand_text,
                            font=brand_font,
                            fill=(0, 0, 0, 255),
                        )

        draw.text(
            (x, y),
            self.config.brand_text,
            font=brand_font,
            fill=self._hex_to_rgba(self.config.brand_color, 1.0),
        )

    def _draw_logo(self, img: Image.Image) -> None:
        """
        Draw logo image.

        Args:
            img: Image to draw on
        """
        try:
            logo = Image.open(self.config.logo_path).convert("RGBA")

            # Resize logo to fit
            logo.thumbnail((self.config.logo_size, self.config.logo_size), Image.Resampling.LANCZOS)

            # Calculate position
            if self.config.logo_position == "bottom-left":
                x = self.config.logo_margin
                y = self.config.height - logo.height - self.config.logo_margin
            elif self.config.logo_position == "bottom-right":
                x = self.config.width - logo.width - self.config.logo_margin
                y = self.config.height - logo.height - self.config.logo_margin
            elif self.config.logo_position == "top-left":
                x = self.config.logo_margin
                y = self.config.logo_margin
            else:  # top-right
                x = self.config.width - logo.width - self.config.logo_margin
                y = self.config.logo_margin

            # Paste logo
            img.paste(logo, (x, y), logo)

        except Exception as e:
            logger.warning(f"Failed to draw logo: {e}")

    def _wrap_text(
        self, text: str, font: ImageFont.FreeTypeFont, max_width: int
    ) -> list[str]:
        """
        Wrap text to fit within max width.

        Args:
            text: Text to wrap
            font: Font to use
            max_width: Maximum width in pixels

        Returns:
            List of wrapped lines
        """
        words = text.split()
        lines = []
        current_line = []

        for word in words:
            # Try adding word to current line
            test_line = " ".join(current_line + [word])
            bbox = ImageDraw.Draw(Image.new("RGBA", (1, 1))).textbbox(
                (0, 0), test_line, font=font
            )
            width = bbox[2] - bbox[0]

            if width <= max_width:
                current_line.append(word)
            else:
                # Line is full, start new line
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]

        # Add last line
        if current_line:
            lines.append(" ".join(current_line))

        return lines

    def _draw_rounded_rectangle(
        self,
        draw: ImageDraw.ImageDraw,
        xy: list,
        radius: int,
        fill: tuple,
    ) -> None:
        """
        Draw rounded rectangle.

        Args:
            draw: ImageDraw context
            xy: Coordinates [(x1, y1), (x2, y2)]
            radius: Corner radius
            fill: Fill color (RGBA tuple)
        """
        x1, y1 = xy[0]
        x2, y2 = xy[1]

        # Draw rounded rectangle using PIL's built-in method
        draw.rounded_rectangle(xy, radius=radius, fill=fill)

    def _hex_to_rgba(self, hex_color: str, alpha: float) -> tuple:
        """
        Convert hex color to RGBA tuple.

        Args:
            hex_color: Hex color string (e.g., '#1E40AF')
            alpha: Alpha value (0.0-1.0)

        Returns:
            RGBA tuple
        """
        hex_color = hex_color.lstrip("#")
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        a = int(alpha * 255)
        return (r, g, b, a)
