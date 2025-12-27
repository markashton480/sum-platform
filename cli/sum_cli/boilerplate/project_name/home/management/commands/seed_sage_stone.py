"""
Seed the Sage & Stone site root and HomePage.

Creates a HomePage under the Wagtail root and configures a default Site
pointing at it. Supports idempotent re-runs and a scoped --clear reset.
"""

from __future__ import annotations

from io import BytesIO
from typing import Any, TypedDict

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandParser
from home.models import HomePage
from PIL import Image as PILImage
from PIL import ImageDraw, ImageFont
from sum_core.branding.models import SiteSettings
from wagtail.images.models import Image
from wagtail.models import Page, Site

IMAGE_PREFIX = "SS"

BRAND_CONFIG = {
    # Company Info
    "company_name": "Sage & Stone",
    "established_year": 2025,
    "tagline": "Rooms that remember",
    # Contact
    "phone_number": "+44 (0) 20 1234 5678",
    "email": "hello@sageandstone.com",
    "address": "The Old Joinery\nUnit 4\nHerefordshire HR4 9AB",
    "business_hours": (
        "Monday - Friday: 9am - 5pm\nSaturday: By appointment\nSunday: Closed"
    ),
    # Colors (from Tailwind config)
    "primary_color": "#1A2F23",  # sage-black
    "secondary_color": "#4A6350",  # sage-darkmoss
    "accent_color": "#A0563B",  # sage-terra
    "background_color": "#F7F5F1",  # sage-linen
    "text_color": "#1A2F23",  # sage-black
    "surface_color": "#EDE8E0",  # sage-oat
    "surface_elevated_color": "#FFFFFF",
    "text_light_color": "#5A6E5F",  # meta color
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


class RequiredImageSpec(TypedDict):
    key: str
    width: int
    height: int


class ImageSpec(RequiredImageSpec, total=False):
    bg: str
    text: str
    label: str


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


class PlaceholderImageGenerator:
    """Generate branded placeholder images."""

    COLORS = {
        "sage_black": (26, 47, 35),
        "sage_moss": (107, 143, 113),
        "sage_terra": (160, 86, 59),
        "sage_oat": (237, 232, 224),
        "sage_linen": (247, 245, 241),
    }

    def __init__(self, prefix: str = IMAGE_PREFIX) -> None:
        """Namespace generated image titles for easy lookup/cleanup."""
        self.prefix = prefix

    def generate_image(
        self,
        key: str,
        width: int,
        height: int,
        *,
        bg_color: str = "sage_black",
        text_color: str = "sage_oat",
        label: str | None = None,
    ) -> Image:
        """
        Generate a placeholder image and save to Wagtail.

        Returns an existing image if already present.
        """
        title = f"{self.prefix}_{key}"

        existing = Image.objects.filter(title=title).first()
        if existing is not None:
            return existing

        bg = self.COLORS.get(bg_color, self.COLORS["sage_black"])
        text = self.COLORS.get(text_color, self.COLORS["sage_oat"])

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
        wagtail_image = Image(title=title)
        wagtail_image.file.save(file_name, ContentFile(buffer.getvalue()), save=False)
        wagtail_image.width = img.width
        wagtail_image.height = img.height
        wagtail_image.save()
        return wagtail_image

    def _get_placeholder_font(
        self, size: int
    ) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
        """
        Choose a legible font from common locations, fallback to default.
        """
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


class Command(BaseCommand):
    help = "Create the Sage & Stone site root and HomePage."
    image_prefix = IMAGE_PREFIX

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete existing Sage & Stone content before re-seeding.",
        )
        parser.add_argument(
            "--images-only",
            action="store_true",
            help="Generate Sage & Stone placeholder images only.",
        )
        parser.add_argument(
            "--hostname",
            default="localhost",
            help="Hostname for the Wagtail Site (defaults to localhost).",
        )
        parser.add_argument(
            "--port",
            type=int,
            default=8000,
            help="Port for the Wagtail Site (defaults to 8000).",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        hostname = options.get("hostname") or "localhost"
        port = options.get("port") or 8000
        images_only = options.get("images_only", False)

        if options.get("clear"):
            self._clear_existing_content(hostname=hostname, port=port)

        self.create_images()

        if images_only:
            self.stdout.write("Generated images only (--images-only)")
            return

        site, home_page = self._setup_site(hostname=hostname, port=port)
        settings = self._configure_branding(site=site)
        self.stdout.write(f"Site configured: {site.site_name} (root={home_page.slug})")
        self.stdout.write(f"Configured branding for {settings.company_name}")

    def create_images(self) -> dict[str, Image]:
        """
        Generate or retrieve placeholder images for each manifest entry.

        Idempotent: existing images are reused based on title matching.
        """
        generator = PlaceholderImageGenerator(prefix=self.image_prefix)
        images: dict[str, Image] = {}

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

        self.stdout.write(f"Created {len(images)} placeholder images")
        return images

    def _setup_site(self, *, hostname: str, port: int) -> tuple[Site, HomePage]:
        root = Page.get_first_root_node()
        home_page, _ = self._get_or_create_home_page(root)

        site, created = Site.objects.get_or_create(
            hostname=hostname,
            port=port,
            defaults={
                "site_name": "Sage & Stone",
                "root_page": home_page,
                "is_default_site": True,
            },
        )

        if not created:
            site.site_name = "Sage & Stone"
            site.root_page = home_page
            site.is_default_site = True
            site.save()

        Site.clear_site_root_paths_cache()
        return site, home_page

    def _get_or_create_home_page(self, root: Page) -> tuple[HomePage, bool]:
        try:
            home_page = root.get_children().type(HomePage).get(slug="home").specific
            home_page.title = "Sage & Stone"
            home_page.seo_title = "Sage & Stone | Bespoke Kitchens, Herefordshire"
            home_page.search_description = (
                "Heirloom-quality kitchens, handcrafted in Herefordshire. "
                "12 commissions per year. Lifetime guarantee."
            )
            home_page.show_in_menus = False
            home_page.save_revision().publish()
            return home_page, False
        except Page.DoesNotExist:
            pass

        conflict = root.get_children().filter(slug="home").first()
        if conflict is not None:
            self.stdout.write(
                self.style.WARNING(
                    "Existing page with slug 'home' is not a HomePage; renaming it."
                )
            )
            conflict_page = conflict.specific
            conflict_page.slug = f"home-legacy-{conflict_page.id}"
            conflict_page.title = f"{conflict_page.title} (Legacy)"
            conflict_page.save()
            conflict_page.save_revision().publish()

        home_page = HomePage(
            title="Sage & Stone",
            slug="home",
            seo_title="Sage & Stone | Bespoke Kitchens, Herefordshire",
            search_description=(
                "Heirloom-quality kitchens, handcrafted in Herefordshire. "
                "12 commissions per year. Lifetime guarantee."
            ),
            show_in_menus=False,
        )
        root.add_child(instance=home_page)
        home_page.save_revision().publish()
        return home_page, True

    def _configure_branding(self, *, site: Site) -> SiteSettings:
        settings, _ = SiteSettings.objects.get_or_create(site=site)

        brand_fields = [
            # Company info
            "company_name",
            "established_year",
            "tagline",
            # Contact
            "phone_number",
            "email",
            "address",
            "business_hours",
            # Colors
            "primary_color",
            "secondary_color",
            "accent_color",
            "background_color",
            "text_color",
            "surface_color",
            "surface_elevated_color",
            "text_light_color",
            # Typography
            "heading_font",
            "body_font",
            # Social Links
            "instagram_url",
            "facebook_url",
            "linkedin_url",
            "twitter_url",
            "youtube_url",
            "tiktok_url",
            # Analytics
            "gtm_container_id",
            "ga_measurement_id",
            # Cookie Banner
            "cookie_banner_enabled",
        ]

        for field_name in brand_fields:
            setattr(settings, field_name, BRAND_CONFIG[field_name])

        # Images (logo, favicon, OG)
        settings.header_logo = self._create_logo_image()
        settings.footer_logo = settings.header_logo
        settings.favicon = self._create_favicon_image()

        og_image = self._get_og_default_image()
        if og_image:
            settings.og_default_image = og_image

        settings.save()
        return settings

    def _load_font(
        self, path: str, *, size: int
    ) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            return ImageFont.load_default()

    def _create_logo_image(self) -> Image:
        title = f"{self.image_prefix}_LOGO"

        try:
            return Image.objects.get(title=title)
        except Image.DoesNotExist:
            pass

        width, height = 300, 80
        img = PILImage.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        font = self._load_font(
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", size=28
        )
        text = "SAGE & STONE"
        text_color = (26, 47, 35)  # sage-black

        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) // 2
        y = 20
        draw.text((x, y), text, fill=text_color, font=font)

        small_font = self._load_font(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size=12
        )
        est_text = "Est. 2025"
        est_bbox = draw.textbbox((0, 0), est_text, font=small_font)
        est_width = est_bbox[2] - est_bbox[0]
        draw.text(
            ((width - est_width) // 2, 55),
            est_text,
            fill=text_color,
            font=small_font,
        )

        return self._save_image(image=img, title=title, filename="sage_stone_logo.png")

    def _create_favicon_image(self) -> Image:
        title = f"{self.image_prefix}_FAVICON"

        try:
            return Image.objects.get(title=title)
        except Image.DoesNotExist:
            pass

        size = 64  # Generate larger, browser will scale
        img = PILImage.new("RGB", (size, size), (26, 47, 35))  # sage-black
        draw = ImageDraw.Draw(img)

        font = self._load_font(
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", size=48
        )
        text = "S"
        text_color = (237, 232, 224)  # sage-oat

        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (size - text_width) // 2
        y = (size - text_height) // 2 - 5
        draw.text((x, y), text, fill=text_color, font=font)

        return self._save_image(image=img, title=title, filename="favicon.png")

    def _get_og_default_image(self) -> Image | None:
        images = getattr(self, "images", None)
        if isinstance(images, dict):
            hero_image = images.get("HERO_IMAGE")
            if hero_image:
                return hero_image

        try:
            return Image.objects.get(title=f"{self.image_prefix}_HERO_IMAGE")
        except Image.DoesNotExist:
            pass

        width, height = 1920, 1080
        img = PILImage.new("RGB", (width, height), (26, 47, 35))  # sage-black
        draw = ImageDraw.Draw(img)

        font = self._load_font(
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", size=48
        )
        text = "Sage & Stone"
        text_color = (237, 232, 224)  # sage-oat

        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        draw.text((x, y), text, fill=text_color, font=font)

        return self._save_image(
            image=img, title=f"{self.image_prefix}_HERO_IMAGE", filename="hero.png"
        )

    def _save_image(self, *, image: PILImage.Image, title: str, filename: str) -> Image:
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)

        wagtail_image = Image(title=title)
        wagtail_image.file.save(filename, ContentFile(buffer.getvalue()), save=False)
        wagtail_image.width, wagtail_image.height = image.size
        wagtail_image.save()
        return wagtail_image

    def _clear_existing_content(self, *, hostname: str, port: int) -> None:
        """
        Remove Sage & Stone content for a fresh seed.

        Scoped to the specific site to avoid data loss in multi-site setups.
        """
        # Find the Sage & Stone site
        site = Site.objects.filter(hostname=hostname, port=port).first()
        if site is None:
            self.stdout.write("No existing Sage & Stone site found, nothing to clear")
            return

        root_page = site.root_page
        if root_page and root_page.specific_class == HomePage:
            root_page.get_descendants(inclusive=True).delete()
            self.stdout.write(f"Deleted {root_page.title} and all descendant pages")
        else:
            self.stdout.write(
                self.style.WARNING(
                    "Site root is not a HomePage. Skipping clear to avoid data loss."
                )
            )
            return

        # Clear site-specific settings and navigation
        from sum_core.navigation.models import FooterNavigation, HeaderNavigation

        SiteSettings.objects.filter(site=site).delete()
        HeaderNavigation.objects.filter(site=site).delete()
        FooterNavigation.objects.filter(site=site).delete()

        # Clear seeded categories and images
        from sum_core.pages.blog import Category

        Category.objects.filter(
            name__in=[
                "Commission Stories",
                "Material Science",
                "The Workshop",
                "Sage & Stone Updates",
            ]
        ).delete()
        Image.objects.filter(title__startswith=f"{self.image_prefix}_").delete()

        self.stdout.write("Cleared existing Sage & Stone content (scoped to site)")
