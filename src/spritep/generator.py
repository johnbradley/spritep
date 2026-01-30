"""Sprite generation logic."""

from pathlib import Path
from typing import Any

import click
import yaml
from PIL import Image, ImageColor, ImageDraw, ImageFont
from PIL.Image import Resampling


def load_config(config_path: Path) -> dict[str, Any]:
    """Load and parse YAML configuration file."""
    with open(config_path) as f:
        return yaml.safe_load(f)


def parse_color(color: str | list | None, default: tuple[int, ...] | str = (0, 0, 0, 0)) -> tuple[int, ...]:
    """Parse a color value into an RGB/RGBA tuple.

    Supports:
    - Named colors: "red", "blue", "forestgreen", etc.
    - Hex RGB: "#FF0000"
    - Hex RGBA: "#FF000080"
    - RGB list: [255, 0, 0]
    - RGBA list: [255, 0, 0, 128]
    """
    if color is None:
        if isinstance(default, tuple):
            return default
        color = default

    if isinstance(color, list):
        return tuple(color)

    if isinstance(color, str):
        # Handle hex colors (with or without #)
        stripped = color.lstrip("#")
        if len(stripped) in (6, 8) and all(c in "0123456789abcdefABCDEF" for c in stripped):
            if len(stripped) == 8:
                return tuple(int(stripped[i:i+2], 16) for i in (0, 2, 4, 6))
            color = f"#{stripped}"

        # Use PIL's ImageColor for named colors and standard hex
        try:
            return ImageColor.getrgb(color)
        except ValueError:
            pass

    return (0, 0, 0, 0)


def create_rounded_mask(width: int, height: int, radius: int) -> Image.Image:
    """Create a mask with rounded corners."""
    mask = Image.new("L", (width, height), 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([0, 0, width - 1, height - 1], radius=radius, fill=255)
    return mask


# Font paths to try, in order of preference (emoji-capable fonts first)
FONT_PATHS = [
    # macOS fonts with emoji/symbol support
    "/System/Library/Fonts/Apple Color Emoji.ttc",
    "/System/Library/Fonts/Supplemental/Apple Symbols.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
    "/System/Library/Fonts/SFNS.ttf",
    # Linux fonts
    "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf",
    "/usr/share/fonts/truetype/noto/NotoSansSymbols-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    # Windows fonts
    "C:/Windows/Fonts/seguiemj.ttf",
    "C:/Windows/Fonts/segoeui.ttf",
]


def _load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Load a font that supports emojis and symbols."""
    for font_path in FONT_PATHS:
        try:
            return ImageFont.truetype(font_path, size)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()


def generate_sprite(
    name: str,
    width: int,
    height: int,
    background: str | list | None = None,
    text: str | None = None,
    text_color: str | list | None = None,
    border: dict | None = None,
    corner_radius: int | None = None,
    folder: str | None = None,
    output_dir: Path = Path("output"),
    scale: int = 4,
) -> Path:
    """Generate a single placeholder sprite.

    Uses supersampling for better quality: renders at higher resolution
    then scales down with LANCZOS resampling.
    """
    # Render at higher resolution for better quality
    render_width = width * scale
    render_height = height * scale

    bg_color = parse_color(background, (0, 0, 0, 0))
    img = Image.new("RGBA", (render_width, render_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Scale pixel-based values
    radius = (corner_radius or 0) * scale
    scaled_border_width = (border.get("width", 1) * scale) if border else 0

    # Draw background (with optional rounded corners)
    if radius > 0:
        draw.rounded_rectangle(
            [0, 0, render_width - 1, render_height - 1],
            radius=radius,
            fill=bg_color,
        )
    else:
        draw.rectangle([0, 0, render_width - 1, render_height - 1], fill=bg_color)

    # Draw border if specified
    if border:
        border_color = parse_color(border.get("color"), "#999999")
        for i in range(scaled_border_width):
            if radius > 0:
                draw.rounded_rectangle(
                    [i, i, render_width - 1 - i, render_height - 1 - i],
                    radius=max(0, radius - i),
                    outline=border_color,
                )
            else:
                draw.rectangle(
                    [i, i, render_width - 1 - i, render_height - 1 - i],
                    outline=border_color,
                )

    # Draw text label if specified
    if text is not None:
        txt_color = parse_color(text_color, "#666666")

        # Scale font size
        font_size = min(width, height) // 4
        font_size = max(10, min(font_size, 72))
        scaled_font_size = font_size * scale

        font = _load_font(scaled_font_size)

        # Center the text
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (render_width - text_width) // 2
        y = (render_height - text_height) // 2

        draw.text((x, y), text, fill=txt_color, font=font, embedded_color=True)

    # Scale down to final size with high-quality resampling
    img = img.resize((width, height), Resampling.LANCZOS)

    # Determine output path with optional folder
    sprite_dir = output_dir / folder if folder else output_dir
    sprite_dir.mkdir(parents=True, exist_ok=True)
    output_path = sprite_dir / f"{name}.png"

    # Save the sprite
    img.save(output_path, "PNG")

    return output_path


def generate_sprites(
    config_path: Path,
    output_dir: Path,
    verbose: bool = False,
) -> list[Path]:
    """Generate all sprites defined in the configuration file."""
    config = load_config(config_path)
    sprites_config = config.get("sprites", [])

    if not sprites_config:
        click.echo("Warning: No sprites defined in configuration.", err=True)
        return []

    generated = []
    defaults = config.get("defaults", {})

    for sprite in sprites_config:
        name = sprite.get("name", f"sprite_{len(generated)}")
        width = sprite.get("width", defaults.get("width", 100))
        height = sprite.get("height", defaults.get("height", 100))
        background = sprite.get("background", defaults.get("background"))
        text = sprite.get("text")
        text_color = sprite.get("text_color", defaults.get("text_color"))
        border = sprite.get("border", defaults.get("border"))
        corner_radius = sprite.get("corner_radius", defaults.get("corner_radius"))
        folder = sprite.get("folder", defaults.get("folder"))

        if verbose:
            folder_display = f"{folder}/" if folder else ""
            click.echo(f"Generating: {folder_display}{name} ({width}x{height})")

        output_path = generate_sprite(
            name=name,
            width=width,
            height=height,
            background=background,
            text=text,
            text_color=text_color,
            border=border,
            corner_radius=corner_radius,
            folder=folder,
            output_dir=output_dir,
        )
        generated.append(output_path)

    return generated
