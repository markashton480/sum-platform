# Subtask 002: Image Generation

## Overview

Generate placeholder images using PIL/Pillow for all image assets required by the Sage & Stone site.

## Deliverables

1. Image generation utility functions
2. Complete set of placeholder images (~35 total)
3. Wagtail Image model integration
4. Image caching to avoid regeneration

## Image Specifications

Based on wireframe analysis, generate images with brand colors and descriptive text overlays.

### Brand Colors for Placeholders

```python
COLORS = {
    "sage_black": (26, 47, 35),      # #1A2F23
    "sage_moss": (107, 143, 113),    # #6B8F71
    "sage_terra": (160, 86, 59),     # #A0563B
    "sage_oat": (237, 232, 224),     # #EDE8E0
    "sage_linen": (247, 245, 241),   # #F7F5F1
}
```

### Image Categories

| Category | Count | Background | Text Color |
|----------|-------|------------|------------|
| Hero/Feature | 4 | sage_black | sage_oat |
| Team Portraits | 5 | sage_moss | sage_linen |
| Portfolio | 8 | sage_black | sage_oat |
| Services | 8 | sage_moss | sage_linen |
| Detail/Gallery | 6 | sage_terra | sage_linen |
| Logos/Badges | 4 | sage_linen | sage_black |

## Implementation

### 1. Core Image Generator

```python
from PIL import Image as PILImage, ImageDraw, ImageFont
from io import BytesIO
from django.core.files.base import ContentFile
from wagtail.images.models import Image

class PlaceholderImageGenerator:
    """Generate branded placeholder images."""

    COLORS = {
        "sage_black": (26, 47, 35),
        "sage_moss": (107, 143, 113),
        "sage_terra": (160, 86, 59),
        "sage_oat": (237, 232, 224),
        "sage_linen": (247, 245, 241),
    }

    def __init__(self, prefix="SS"):
        self.prefix = prefix

    def generate_image(
        self,
        key: str,
        width: int,
        height: int,
        bg_color: str = "sage_black",
        text_color: str = "sage_oat",
        label: str = None,
    ) -> Image:
        """
        Generate a placeholder image and save to Wagtail.

        Returns existing image if already created.
        """
        title = f"{self.prefix}_{key}"

        # Check for existing
        try:
            return Image.objects.get(title=title)
        except Image.DoesNotExist:
            pass

        # Generate PIL image
        bg = self.COLORS.get(bg_color, self.COLORS["sage_black"])
        text = self.COLORS.get(text_color, self.COLORS["sage_oat"])

        img = PILImage.new("RGB", (width, height), bg)
        draw = ImageDraw.Draw(img)

        # Draw label text
        display_label = label or key.replace("_", " ").title()

        # Try to use a font, fall back to default
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
        except IOError:
            font = ImageFont.load_default()

        # Center text
        bbox = draw.textbbox((0, 0), display_label, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (width - text_width) // 2
        y = (height - text_height) // 2

        draw.text((x, y), display_label, fill=text, font=font)

        # Add dimensions in corner
        dims_text = f"{width}x{height}"
        draw.text((10, height - 30), dims_text, fill=text, font=font)

        # Save to BytesIO
        buffer = BytesIO()
        img.save(buffer, format="JPEG", quality=85)
        buffer.seek(0)

        # Create Wagtail Image
        wagtail_image = Image(title=title)
        wagtail_image.file.save(
            f"{title.lower()}.jpg",
            ContentFile(buffer.getvalue()),
            save=True
        )

        return wagtail_image
```

### 2. Image Manifest

```python
IMAGE_MANIFEST = [
    # Hero/Feature Images
    {"key": "HERO_IMAGE", "width": 1920, "height": 1080, "bg": "sage_black", "label": "Hero Kitchen"},
    {"key": "SURREY_IMAGE", "width": 1000, "height": 700, "bg": "sage_black", "label": "Surrey Commission"},
    {"key": "PROVENANCE_IMAGE", "width": 800, "height": 600, "bg": "sage_terra", "label": "Brass Plate"},
    {"key": "WORKSHOP_IMAGE", "width": 1200, "height": 800, "bg": "sage_black", "label": "Workshop Interior"},

    # Team Portraits
    {"key": "FOUNDER_IMAGE", "width": 800, "height": 1000, "bg": "sage_moss", "label": "Thomas J. Wright"},
    {"key": "TEAM_JAMES", "width": 400, "height": 500, "bg": "sage_moss", "label": "James E."},
    {"key": "TEAM_SARAH", "width": 400, "height": 500, "bg": "sage_moss", "label": "Sarah M."},
    {"key": "TEAM_DAVID", "width": 400, "height": 500, "bg": "sage_moss", "label": "David R."},
    {"key": "TEAM_MARCUS", "width": 400, "height": 500, "bg": "sage_moss", "label": "Marcus T."},

    # Service Images
    {"key": "SERVICE_COMMISSION", "width": 600, "height": 400, "bg": "sage_black", "label": "The Commission"},
    {"key": "SERVICE_RESTORATION", "width": 600, "height": 400, "bg": "sage_black", "label": "The Restoration"},
    {"key": "SERVICE_LARDER", "width": 600, "height": 400, "bg": "sage_black", "label": "The Larder"},
    {"key": "SERVICE_APPLIANCE", "width": 600, "height": 400, "bg": "sage_moss", "label": "Appliance Integration"},
    {"key": "SERVICE_JOINERY", "width": 600, "height": 400, "bg": "sage_moss", "label": "Bespoke Joinery"},
    {"key": "SERVICE_TECHNICAL", "width": 600, "height": 400, "bg": "sage_moss", "label": "Technical Integration"},
    {"key": "SERVICE_STONE", "width": 600, "height": 400, "bg": "sage_moss", "label": "Stone & Surfaces"},

    # Portfolio Images
    {"key": "PORTFOLIO_KENSINGTON", "width": 800, "height": 600, "bg": "sage_black", "label": "Kensington"},
    {"key": "PORTFOLIO_COTSWOLD", "width": 800, "height": 600, "bg": "sage_black", "label": "Cotswold Barn"},
    {"key": "PORTFOLIO_GEORGIAN", "width": 800, "height": 600, "bg": "sage_black", "label": "Georgian Townhouse"},
    {"key": "PORTFOLIO_HIGHLAND", "width": 1200, "height": 600, "bg": "sage_black", "label": "Highland Commission"},
    {"key": "PORTFOLIO_LARDER", "width": 600, "height": 800, "bg": "sage_black", "label": "Pantry Larder"},
    {"key": "PORTFOLIO_GEORGIAN_REST", "width": 600, "height": 800, "bg": "sage_black", "label": "Georgian Restoration"},
    {"key": "PORTFOLIO_BRUTALIST", "width": 800, "height": 500, "bg": "sage_black", "label": "Brutalist Barn"},
    {"key": "PORTFOLIO_UTILITY", "width": 600, "height": 800, "bg": "sage_black", "label": "Utility Room"},

    # Detail/Gallery Images
    {"key": "DETAIL_1", "width": 600, "height": 600, "bg": "sage_terra", "label": "Dovetail Joint"},
    {"key": "DETAIL_2", "width": 600, "height": 600, "bg": "sage_terra", "label": "Hinge Detail"},
    {"key": "DETAIL_3", "width": 600, "height": 600, "bg": "sage_terra", "label": "Surface Finish"},

    # Certification Logos
    {"key": "LOGO_GASSAFE", "width": 200, "height": 80, "bg": "sage_linen", "text": "sage_black", "label": "Gas Safe"},
    {"key": "LOGO_NICEIC", "width": 200, "height": 80, "bg": "sage_linen", "text": "sage_black", "label": "NICEIC"},
    {"key": "LOGO_BIKBBI", "width": 200, "height": 80, "bg": "sage_linen", "text": "sage_black", "label": "BiKBBI"},
    {"key": "LOGO_GUILD", "width": 200, "height": 80, "bg": "sage_linen", "text": "sage_black", "label": "Guild"},

    # Blog Images
    {"key": "BLOG_TIMBER_IMAGE", "width": 1200, "height": 600, "bg": "sage_black", "label": "Seasoning Timber"},
    {"key": "BLOG_TIMBER_STACK", "width": 1000, "height": 600, "bg": "sage_black", "label": "Timber Stacking"},
    {"key": "BLOG_KENSINGTON", "width": 1200, "height": 600, "bg": "sage_black", "label": "Kensington Story"},
    {"key": "BLOG_DOVETAILS", "width": 1200, "height": 600, "bg": "sage_terra", "label": "Dovetails"},
    {"key": "BLOG_WORKSHOP", "width": 1200, "height": 600, "bg": "sage_moss", "label": "Workshop Update"},
    {"key": "BLOG_GEORGIAN", "width": 1200, "height": 600, "bg": "sage_black", "label": "Georgian Journey"},
    {"key": "BLOG_MDF", "width": 1200, "height": 600, "bg": "sage_terra", "label": "Why Not MDF"},
    {"key": "BLOG_MARCUS", "width": 800, "height": 1000, "bg": "sage_moss", "label": "Meet Marcus"},
]
```

### 3. Batch Generation Command

```python
def create_images(self):
    """Generate all placeholder images."""

    generator = PlaceholderImageGenerator(prefix="SS")
    images = {}

    for spec in IMAGE_MANIFEST:
        img = generator.generate_image(
            key=spec["key"],
            width=spec["width"],
            height=spec["height"],
            bg_color=spec.get("bg", "sage_black"),
            text_color=spec.get("text", "sage_oat"),
            label=spec.get("label"),
        )
        images[spec["key"]] = img
        self.stdout.write(f"  Created: {spec['key']}")

    self.images = images
    self.stdout.write(f"Generated {len(images)} images")
```

## Acceptance Criteria

- [ ] All 35+ images generated
- [ ] Images have correct dimensions
- [ ] Images use brand colors
- [ ] Images have readable labels
- [ ] Wagtail Image records created
- [ ] Idempotent: existing images not recreated
- [ ] `--images-only` flag generates only images

## Dependencies

- Pillow installed (`pip install Pillow`)
- MEDIA_ROOT configured
- Write permissions to media directory

## Testing

```python
def test_image_generation():
    generator = PlaceholderImageGenerator()
    img = generator.generate_image("TEST", 800, 600)

    assert img.title == "SS_TEST"
    assert img.width == 800
    assert img.height == 600

def test_image_generation_idempotent():
    generator = PlaceholderImageGenerator()
    img1 = generator.generate_image("TEST", 800, 600)
    img2 = generator.generate_image("TEST", 800, 600)

    assert img1.pk == img2.pk  # Same image returned

def test_all_manifest_images_created():
    call_command("seed_sage_stone", "--images-only")

    for spec in IMAGE_MANIFEST:
        assert Image.objects.filter(title=f"SS_{spec['key']}").exists()
```

## Performance Notes

- PIL operations are fast (~50ms per image)
- Full generation takes ~2-3 seconds
- Consider progress bar for user feedback
- Images cached by title lookup
