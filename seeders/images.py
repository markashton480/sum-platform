"""
Image utilities for seeder placeholder generation.
"""

from __future__ import annotations

from collections.abc import Iterable
from io import BytesIO
from typing import TypedDict

from django.core.files.base import ContentFile
from PIL import Image as PILImage
from PIL import ImageDraw, ImageFont
from wagtail.images.models import Image as WagtailImage


class RequiredImageSpec(TypedDict):
    key: str
    width: int
    height: int


class ImageSpec(RequiredImageSpec, total=False):
    bg: str
    text: str
    label: str


DEFAULT_PALETTE: dict[str, str] = {
    "sage_black": "#1A2F23",
    "sage_moss": "#6B8F71",
    "sage_terra": "#A0563B",
    "sage_oat": "#EDE8E0",
    "sage_linen": "#F7F5F1",
}

DEFAULT_BG = "sage_black"
DEFAULT_TEXT = "sage_oat"

IMAGE_MANIFEST: list[ImageSpec] = [
    # Hero/Feature Images
    {
        "key": "HERO_IMAGE",
        "width": 1920,
        "height": 1080,
        "bg": "sage_black",
        "label": "Hero Kitchen",
    },
    {
        "key": "SURREY_IMAGE",
        "width": 1000,
        "height": 700,
        "bg": "sage_black",
        "label": "Surrey Commission",
    },
    {
        "key": "PROVENANCE_IMAGE",
        "width": 800,
        "height": 600,
        "bg": "sage_terra",
        "label": "Brass Plate",
    },
    {
        "key": "WORKSHOP_IMAGE",
        "width": 1200,
        "height": 800,
        "bg": "sage_black",
        "label": "Workshop Interior",
    },
    # Team Portraits
    {
        "key": "FOUNDER_IMAGE",
        "width": 800,
        "height": 1000,
        "bg": "sage_moss",
        "label": "Thomas J. Wright",
    },
    {
        "key": "TEAM_JAMES",
        "width": 400,
        "height": 500,
        "bg": "sage_moss",
        "label": "James E.",
    },
    {
        "key": "TEAM_SARAH",
        "width": 400,
        "height": 500,
        "bg": "sage_moss",
        "label": "Sarah M.",
    },
    {
        "key": "TEAM_DAVID",
        "width": 400,
        "height": 500,
        "bg": "sage_moss",
        "label": "David R.",
    },
    {
        "key": "TEAM_MARCUS",
        "width": 400,
        "height": 500,
        "bg": "sage_moss",
        "label": "Marcus T.",
    },
    # Service Images
    {
        "key": "SERVICE_COMMISSION",
        "width": 600,
        "height": 400,
        "bg": "sage_black",
        "label": "The Commission",
    },
    {
        "key": "SERVICE_RESTORATION",
        "width": 600,
        "height": 400,
        "bg": "sage_black",
        "label": "The Restoration",
    },
    {
        "key": "SERVICE_LARDER",
        "width": 600,
        "height": 400,
        "bg": "sage_black",
        "label": "The Larder",
    },
    {
        "key": "SERVICE_APPLIANCE",
        "width": 600,
        "height": 400,
        "bg": "sage_moss",
        "label": "Appliance Integration",
    },
    {
        "key": "SERVICE_JOINERY",
        "width": 600,
        "height": 400,
        "bg": "sage_moss",
        "label": "Bespoke Joinery",
    },
    {
        "key": "SERVICE_TECHNICAL",
        "width": 600,
        "height": 400,
        "bg": "sage_moss",
        "label": "Technical Integration",
    },
    {
        "key": "SERVICE_STONE",
        "width": 600,
        "height": 400,
        "bg": "sage_moss",
        "label": "Stone & Surfaces",
    },
    # Portfolio Images
    {
        "key": "PORTFOLIO_KENSINGTON",
        "width": 800,
        "height": 600,
        "bg": "sage_black",
        "label": "Kensington",
    },
    {
        "key": "PORTFOLIO_COTSWOLD",
        "width": 800,
        "height": 600,
        "bg": "sage_black",
        "label": "Cotswold Barn",
    },
    {
        "key": "PORTFOLIO_GEORGIAN",
        "width": 800,
        "height": 600,
        "bg": "sage_black",
        "label": "Georgian Townhouse",
    },
    {
        "key": "PORTFOLIO_HIGHLAND",
        "width": 1200,
        "height": 600,
        "bg": "sage_black",
        "label": "Highland Commission",
    },
    {
        "key": "PORTFOLIO_LARDER",
        "width": 600,
        "height": 800,
        "bg": "sage_black",
        "label": "Pantry Larder",
    },
    {
        "key": "PORTFOLIO_GEORGIAN_REST",
        "width": 600,
        "height": 800,
        "bg": "sage_black",
        "label": "Georgian Restoration",
    },
    {
        "key": "PORTFOLIO_BRUTALIST",
        "width": 800,
        "height": 500,
        "bg": "sage_black",
        "label": "Brutalist Barn",
    },
    {
        "key": "PORTFOLIO_UTILITY",
        "width": 600,
        "height": 800,
        "bg": "sage_black",
        "label": "Utility Room",
    },
    # Detail/Gallery Images
    {
        "key": "DETAIL_1",
        "width": 600,
        "height": 600,
        "bg": "sage_terra",
        "label": "Dovetail Joint",
    },
    {
        "key": "DETAIL_2",
        "width": 600,
        "height": 600,
        "bg": "sage_terra",
        "label": "Hinge Detail",
    },
    {
        "key": "DETAIL_3",
        "width": 600,
        "height": 600,
        "bg": "sage_terra",
        "label": "Surface Finish",
    },
    # Certification Logos
    {
        "key": "LOGO_GASSAFE",
        "width": 200,
        "height": 80,
        "bg": "sage_linen",
        "text": "sage_black",
        "label": "Gas Safe",
    },
    {
        "key": "LOGO_NICEIC",
        "width": 200,
        "height": 80,
        "bg": "sage_linen",
        "text": "sage_black",
        "label": "NICEIC",
    },
    {
        "key": "LOGO_BIKBBI",
        "width": 200,
        "height": 80,
        "bg": "sage_linen",
        "text": "sage_black",
        "label": "BiKBBI",
    },
    {
        "key": "LOGO_GUILD",
        "width": 200,
        "height": 80,
        "bg": "sage_linen",
        "text": "sage_black",
        "label": "Guild",
    },
    # Blog Images
    {
        "key": "BLOG_TIMBER_IMAGE",
        "width": 1200,
        "height": 600,
        "bg": "sage_black",
        "label": "Seasoning Timber",
    },
    {
        "key": "BLOG_TIMBER_STACK",
        "width": 1000,
        "height": 600,
        "bg": "sage_black",
        "label": "Timber Stacking",
    },
    {
        "key": "BLOG_KENSINGTON",
        "width": 1200,
        "height": 600,
        "bg": "sage_black",
        "label": "Kensington Story",
    },
    {
        "key": "BLOG_DOVETAILS",
        "width": 1200,
        "height": 600,
        "bg": "sage_terra",
        "label": "Dovetails",
    },
    {
        "key": "BLOG_WORKSHOP",
        "width": 1200,
        "height": 600,
        "bg": "sage_moss",
        "label": "Workshop Update",
    },
    {
        "key": "BLOG_GEORGIAN",
        "width": 1200,
        "height": 600,
        "bg": "sage_black",
        "label": "Georgian Journey",
    },
    {
        "key": "BLOG_MDF",
        "width": 1200,
        "height": 600,
        "bg": "sage_terra",
        "label": "Why Not MDF",
    },
    {
        "key": "BLOG_MARCUS",
        "width": 800,
        "height": 1000,
        "bg": "sage_moss",
        "label": "Meet Marcus",
    },
]


class ImageManager:
    """Generate and manage placeholder images."""

    def __init__(
        self, prefix: str = "SEED", palette: dict[str, str] | None = None
    ) -> None:
        """Namespace generated image titles for easy lookup/cleanup."""
        self.prefix = prefix
        self.palette = dict(palette or DEFAULT_PALETTE)
        self._generated: dict[str, WagtailImage] = {}

    def generate(
        self,
        key: str,
        width: int,
        height: int,
        *,
        bg_color: str = DEFAULT_BG,
        text_color: str = DEFAULT_TEXT,
        label: str | None = None,
    ) -> WagtailImage:
        """Generate a placeholder image and save to Wagtail."""
        title = f"{self.prefix}_{key}"

        existing = WagtailImage.objects.filter(title=title).first()
        if existing is not None:
            self._generated[key] = existing
            return existing

        bg = self._resolve_color(bg_color, DEFAULT_BG)
        text = self._resolve_color(text_color, DEFAULT_TEXT)

        img = PILImage.new("RGB", (width, height), bg)
        draw = ImageDraw.Draw(img)

        display_label = label or key.replace("_", " ").title()
        font = self._get_placeholder_font(24)

        bbox = draw.textbbox((0, 0), display_label, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (width - text_width) // 2
        y = (height - text_height) // 2

        draw.text((x, y), display_label, fill=text, font=font)

        dims_text = f"{width}x{height}"
        dims_bbox = draw.textbbox((0, 0), dims_text, font=font)
        dims_height = dims_bbox[3] - dims_bbox[1]
        padding = 10
        dims_x = padding
        space_below_label = height - (y + text_height) - padding
        if space_below_label >= dims_height:
            dims_y = height - dims_height - padding
            draw.text((dims_x, dims_y), dims_text, fill=text, font=font)

        buffer = BytesIO()
        img.save(buffer, format="JPEG", quality=85)
        buffer.seek(0)

        file_name = f"{title.lower()}.jpg"
        wagtail_image = WagtailImage(title=title)
        wagtail_image.file.save(file_name, ContentFile(buffer.getvalue()), save=False)
        wagtail_image.width = img.width
        wagtail_image.height = img.height
        wagtail_image.save()

        self._generated[key] = wagtail_image
        return wagtail_image

    def generate_manifest(
        self, manifest: Iterable[ImageSpec]
    ) -> dict[str, WagtailImage]:
        """Generate images for a manifest and store them in the registry."""
        images: dict[str, WagtailImage] = {}
        for spec in manifest:
            image = self.generate(
                key=spec["key"],
                width=spec["width"],
                height=spec["height"],
                bg_color=spec.get("bg", DEFAULT_BG),
                text_color=spec.get("text", DEFAULT_TEXT),
                label=spec.get("label"),
            )
            images[spec["key"]] = image
        self._generated.update(images)
        return images

    def get(self, key: str) -> WagtailImage | None:
        """Retrieve a previously generated image."""
        return self._generated.get(key)

    def _resolve_color(self, value: str, fallback: str) -> tuple[int, int, int]:
        resolved = self._resolve_hex(value)
        if resolved is None:
            resolved = self._resolve_hex(fallback)
        if resolved is None:
            resolved = "#000000"
        return self._hex_to_rgb(resolved)

    def _resolve_hex(self, value: str) -> str | None:
        if value in self.palette:
            return self.palette[value]
        trimmed = value.lstrip("#")
        if len(trimmed) in {3, 6} and all(
            c in "0123456789abcdefABCDEF" for c in trimmed
        ):
            return f"#{trimmed}"
        return None

    def _hex_to_rgb(self, value: str) -> tuple[int, int, int]:
        trimmed = value.lstrip("#")
        if len(trimmed) == 3:
            trimmed = "".join(ch * 2 for ch in trimmed)
        return tuple(int(trimmed[i : i + 2], 16) for i in (0, 2, 4))

    def _get_placeholder_font(
        self, size: int
    ) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
        candidates = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/Library/Fonts/Arial.ttf",
            "C:\\Windows\\Fonts\\arial.ttf",
        ]
        for path in candidates:
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                continue
        return ImageFont.load_default()
