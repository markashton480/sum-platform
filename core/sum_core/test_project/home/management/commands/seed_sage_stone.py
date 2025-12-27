"""
Seed the Sage & Stone site root and HomePage.

Creates a HomePage under the Wagtail root and configures a default Site
pointing at it. Supports idempotent re-runs and a scoped --clear reset.
"""

from __future__ import annotations

from io import BytesIO
from typing import Any

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandParser
from home.models import HomePage
from PIL import Image as PILImage
from PIL import ImageDraw, ImageFont
from sum_core.branding.models import SiteSettings
from wagtail.images.models import Image
from wagtail.models import Page, Site

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


class Command(BaseCommand):
    help = "Create the Sage & Stone site root and HomePage."
    image_prefix = "SS_"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete existing Sage & Stone content before re-seeding.",
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

        if options.get("clear"):
            self._clear_existing_content(hostname=hostname, port=port)

        site, home_page = self._setup_site(hostname=hostname, port=port)
        settings = self._configure_branding(site=site)
        self.stdout.write(f"Site configured: {site.site_name} (root={home_page.slug})")
        self.stdout.write(f"Configured branding for {settings.company_name}")

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
        title = f"{self.image_prefix}LOGO"

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
        title = f"{self.image_prefix}FAVICON"

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
            return Image.objects.get(title=f"{self.image_prefix}HERO_IMAGE")
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
            image=img, title=f"{self.image_prefix}HERO_IMAGE", filename="hero.png"
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
        Image.objects.filter(title__startswith=self.image_prefix).delete()

        self.stdout.write("Cleared existing Sage & Stone content (scoped to site)")
