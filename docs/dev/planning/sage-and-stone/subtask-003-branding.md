# Subtask 003: Branding Configuration

## Overview

Configure SiteSettings with Sage & Stone brand identity including colors, typography, company information, and contact details.

## Deliverables

1. SiteSettings configuration
2. Logo and favicon assignment (from generated images)
3. Company information
4. Social links

## Implementation

### 1. Brand Configuration Data

```python
BRAND_CONFIG = {
    # Company Info
    "company_name": "Sage & Stone",
    "established_year": 2025,
    "tagline": "Rooms that remember",

    # Contact
    "phone_number": "+44 (0) 20 1234 5678",
    "email": "hello@sageandstone.com",
    "address": "The Old Joinery\nUnit 4\nHerefordshire HR4 9AB",
    "business_hours": "Monday - Friday: 9am - 5pm\nSaturday: By appointment\nSunday: Closed",

    # Colors (from Tailwind config)
    "primary_color": "#1A2F23",       # sage-black
    "secondary_color": "#4A6350",     # sage-darkmoss
    "accent_color": "#A0563B",        # sage-terra
    "background_color": "#F7F5F1",    # sage-linen
    "text_color": "#1A2F23",          # sage-black
    "surface_color": "#EDE8E0",       # sage-oat
    "surface_elevated_color": "#FFFFFF",
    "text_light_color": "#5A6E5F",    # meta color

    # Typography (Google Fonts)
    "heading_font": "Playfair Display",
    "body_font": "Lato",

    # Social Media
    "instagram_url": "https://instagram.com/sageandstone",
    "facebook_url": "",
    "linkedin_url": "",
    "twitter_url": "",
    "youtube_url": "",
    "tiktok_url": "",

    # Analytics (empty for demo)
    "gtm_container_id": "",
    "ga_measurement_id": "",

    # Cookie/Consent
    "cookie_banner_enabled": False,
}
```

### 2. SiteSettings Creation

```python
from sum_core.branding.models import SiteSettings

def create_branding(self, site):
    """Configure SiteSettings with Sage & Stone branding."""

    # Get or create SiteSettings
    settings, created = SiteSettings.objects.get_or_create(site=site)

    # Company Info
    settings.company_name = BRAND_CONFIG["company_name"]
    settings.established_year = BRAND_CONFIG["established_year"]
    settings.tagline = BRAND_CONFIG["tagline"]

    # Contact
    settings.phone_number = BRAND_CONFIG["phone_number"]
    settings.email = BRAND_CONFIG["email"]
    settings.address = BRAND_CONFIG["address"]
    settings.business_hours = BRAND_CONFIG["business_hours"]

    # Colors
    settings.primary_color = BRAND_CONFIG["primary_color"]
    settings.secondary_color = BRAND_CONFIG["secondary_color"]
    settings.accent_color = BRAND_CONFIG["accent_color"]
    settings.background_color = BRAND_CONFIG["background_color"]
    settings.text_color = BRAND_CONFIG["text_color"]
    settings.surface_color = BRAND_CONFIG["surface_color"]
    settings.surface_elevated_color = BRAND_CONFIG["surface_elevated_color"]
    settings.text_light_color = BRAND_CONFIG["text_light_color"]

    # Typography
    settings.heading_font = BRAND_CONFIG["heading_font"]
    settings.body_font = BRAND_CONFIG["body_font"]

    # Social Links
    settings.instagram_url = BRAND_CONFIG["instagram_url"]
    settings.facebook_url = BRAND_CONFIG["facebook_url"]
    settings.linkedin_url = BRAND_CONFIG["linkedin_url"]
    settings.twitter_url = BRAND_CONFIG["twitter_url"]
    settings.youtube_url = BRAND_CONFIG["youtube_url"]
    settings.tiktok_url = BRAND_CONFIG["tiktok_url"]

    # Analytics
    settings.gtm_container_id = BRAND_CONFIG["gtm_container_id"]
    settings.ga_measurement_id = BRAND_CONFIG["ga_measurement_id"]

    # Cookie Banner
    settings.cookie_banner_enabled = BRAND_CONFIG["cookie_banner_enabled"]

    # Images (from generated placeholders)
    if hasattr(self, 'images'):
        # Create dedicated logo images
        logo = self._create_logo_image()
        settings.header_logo = logo
        settings.footer_logo = logo

        favicon = self._create_favicon_image()
        settings.favicon = favicon

        # Default OG image
        settings.og_default_image = self.images.get("HERO_IMAGE")

    settings.save()
    self.stdout.write(f"Configured branding for {settings.company_name}")

    return settings
```

### 3. Logo Generation

```python
def _create_logo_image(self):
    """Generate a text-based logo placeholder."""

    from PIL import Image as PILImage, ImageDraw, ImageFont
    from io import BytesIO
    from django.core.files.base import ContentFile
    from wagtail.images.models import Image

    title = "SS_LOGO"

    try:
        return Image.objects.get(title=title)
    except Image.DoesNotExist:
        pass

    # Create transparent PNG with text logo
    width, height = 300, 80
    img = PILImage.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Draw "SAGE & STONE" text
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", 28)
    except IOError:
        font = ImageFont.load_default()

    text = "SAGE & STONE"
    text_color = (26, 47, 35)  # sage-black

    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    x = (width - text_width) // 2
    y = 20

    draw.text((x, y), text, fill=text_color, font=font)

    # Add "Est. 2025" below
    try:
        small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
    except IOError:
        small_font = ImageFont.load_default()

    est_text = "Est. 2025"
    est_bbox = draw.textbbox((0, 0), est_text, font=small_font)
    est_width = est_bbox[2] - est_bbox[0]
    draw.text(((width - est_width) // 2, 55), est_text, fill=text_color, font=small_font)

    # Save to BytesIO
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    # Create Wagtail Image
    wagtail_image = Image(title=title)
    wagtail_image.file.save(
        "sage_stone_logo.png",
        ContentFile(buffer.getvalue()),
        save=True
    )

    return wagtail_image


def _create_favicon_image(self):
    """Generate a simple favicon."""

    from PIL import Image as PILImage, ImageDraw
    from io import BytesIO
    from django.core.files.base import ContentFile
    from wagtail.images.models import Image

    title = "SS_FAVICON"

    try:
        return Image.objects.get(title=title)
    except Image.DoesNotExist:
        pass

    # 32x32 favicon with "S" letter
    size = 64  # Generate larger, browser will scale
    img = PILImage.new("RGB", (size, size), (26, 47, 35))  # sage-black
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", 48)
    except IOError:
        font = ImageFont.load_default()

    text = "S"
    text_color = (237, 232, 224)  # sage-oat

    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (size - text_width) // 2
    y = (size - text_height) // 2 - 5

    draw.text((x, y), text, fill=text_color, font=font)

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    wagtail_image = Image(title=title)
    wagtail_image.file.save(
        "favicon.png",
        ContentFile(buffer.getvalue()),
        save=True
    )

    return wagtail_image
```

## Acceptance Criteria

- [ ] SiteSettings created with all brand colors
- [ ] Typography fonts configured
- [ ] Company information populated
- [ ] Contact details set
- [ ] Logo images created and assigned
- [ ] Favicon created and assigned
- [ ] OG default image set
- [ ] Instagram link configured
- [ ] Idempotent: can update existing settings

## Dependencies

- Subtask 001 (Site exists)
- Subtask 002 (Images generated)
- SiteSettings model available

## Testing

```python
def test_branding_creates_settings():
    call_command("seed_sage_stone")

    site = Site.objects.get(hostname="localhost")
    settings = SiteSettings.for_site(site)

    assert settings.company_name == "Sage & Stone"
    assert settings.primary_color == "#1A2F23"
    assert settings.heading_font == "Playfair Display"
    assert settings.phone_number == "+44 (0) 20 1234 5678"

def test_branding_has_logo():
    call_command("seed_sage_stone")

    site = Site.objects.get(hostname="localhost")
    settings = SiteSettings.for_site(site)

    assert settings.header_logo is not None
    assert settings.favicon is not None
```

## Notes

- Colors match wireframe Tailwind config exactly
- Typography uses Google Fonts (theme must load them)
- Social links minimal for demo (only Instagram)
- Cookie banner disabled for cleaner demo
