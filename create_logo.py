#!/usr/bin/env python3
"""
Create a simple AI ON logo for thumbnails.

This creates a placeholder logo. Replace with your actual logo later.
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

def create_logo():
    """Create a simple AI ON logo."""
    # Logo size
    size = 200

    # Create image with transparency
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Background circle (blue)
    margin = 10
    draw.ellipse(
        [margin, margin, size - margin, size - margin],
        fill=(30, 64, 175, 255),  # #1E40AF
        outline=(255, 255, 255, 255),
        width=5
    )

    # Text
    try:
        # Try to use Arial
        font = ImageFont.truetype("Arial", 60)
    except OSError:
        # Fallback to default
        font = ImageFont.load_default()

    # Draw "AI ON" text
    text = "AI\nON"

    # Get text bounding box for centering
    bbox = draw.multiline_textbbox((0, 0), text, font=font, align="center")
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # Center position
    x = (size - text_width) // 2
    y = (size - text_height) // 2 - 10

    # Draw text with stroke
    # Stroke (black)
    for offset_x in range(-2, 3):
        for offset_y in range(-2, 3):
            if offset_x != 0 or offset_y != 0:
                draw.multiline_text(
                    (x + offset_x, y + offset_y),
                    text,
                    font=font,
                    fill=(0, 0, 0, 255),
                    align="center"
                )

    # Main text (white)
    draw.multiline_text(
        (x, y),
        text,
        font=font,
        fill=(255, 255, 255, 255),
        align="center"
    )

    # Save
    output_path = Path("resources/logo.png")
    img.save(output_path, "PNG")
    print(f"✅ Logo created: {output_path}")
    print(f"   Size: {size}x{size}")
    print(f"   File size: {output_path.stat().st_size / 1024:.1f} KB")
    print(f"\n💡 You can replace this with your actual AI ON logo")
    print(f"   Just save it as: resources/logo.png")

if __name__ == "__main__":
    create_logo()
