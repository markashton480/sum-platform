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
from sum_core.navigation.models import FooterNavigation, HeaderNavigation
from sum_core.pages.standard import StandardPage
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

        self.images = self.create_images()

        if images_only:
            self.stdout.write("Generated images only (--images-only)")
            return

        site, home_page = self._setup_site(hostname=hostname, port=port)
        self.create_pages(home_page=home_page)
        settings = self._configure_branding(site=site)
        pages = self._get_navigation_pages(site=site, home_page=home_page)
        self._configure_navigation(site=site, pages=pages)
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

    def create_pages(self, *, home_page: HomePage) -> dict[str, Page]:
        """Create core content pages under the home page."""
        pages = {"home": home_page}

        pages["about"] = self._create_about_page(home_page)
        pages["services"] = self._create_services_page(home_page)
        pages["portfolio"] = self._create_portfolio_page(home_page)
        pages["contact"] = self._create_contact_page(home_page)

        self._populate_home_content(home_page)

        self.stdout.write(f"Created {len(pages)} pages")
        return pages

    def _populate_home_content(self, home_page: HomePage) -> None:
        """Add StreamField content to homepage."""
        home_page.body = [
            {
                "type": "hero_image",
                "value": {
                    "headline": "<em>Rooms that remember</em>",
                    "subheadline": (
                        "Heirloom-quality kitchens, handcrafted in Herefordshire. "
                        "12 commissions per year. Lifetime guarantee."
                    ),
                    "ctas": [
                        {
                            "label": "Begin Your Commission",
                            "url": "/contact/",
                            "style": "primary",
                            "open_in_new_tab": False,
                        },
                        {
                            "label": "Our Philosophy",
                            "url": "/about/",
                            "style": "outline",
                            "open_in_new_tab": False,
                        },
                    ],
                    "status": "",
                    "image": self.images["HERO_IMAGE"].pk,
                    "image_alt": "Bespoke kitchen interior with dark wood cabinetry",
                    "overlay_opacity": "medium",
                    "layout": "full",
                    "floating_card_label": "",
                    "floating_card_value": "",
                },
            },
            {
                "type": "stats",
                "value": {
                    "eyebrow": "",
                    "intro": "",
                    "items": [
                        {
                            "value": "12",
                            "label": "Commissions per year",
                            "prefix": "",
                            "suffix": "",
                        },
                        {
                            "value": "12-16",
                            "label": "Week build time",
                            "prefix": "",
                            "suffix": "",
                        },
                        {
                            "value": "Herefordshire",
                            "label": "Workshop location",
                            "prefix": "",
                            "suffix": "",
                        },
                        {
                            "value": "Lifetime",
                            "label": "Joinery guarantee",
                            "prefix": "",
                            "suffix": "",
                        },
                    ],
                },
            },
            {
                "type": "manifesto",
                "value": {
                    "eyebrow": "The Sage & Stone Philosophy",
                    "heading": "Good kitchens don't age. They <em>season</em>.",
                    "body": (
                        "<p>We curate the room your great-grandchildren will fight "
                        "over.</p><p>In a world of disposable design, we build against "
                        "the grain--literally and figuratively. Every joint is cut by "
                        "hand. Every surface is finished to last decades, not seasons.</p>"
                    ),
                    "quote": "Speed is the enemy of legacy",
                },
            },
            {
                "type": "service_cards",
                "value": {
                    "eyebrow": "Our Services",
                    "heading": "What We Create",
                    "intro": "Three ways to begin your Sage & Stone journey.",
                    "view_all_link": "/services/",
                    "view_all_label": "View all services",
                    "cards": [
                        {
                            "icon": "",
                            "image": self.images["SERVICE_COMMISSION"].pk,
                            "title": "The Commission",
                            "description": (
                                "<p>A fully bespoke kitchen, designed and built from "
                                "first principles. Your space, your needs, your legacy.</p>"
                            ),
                            "link_url": "/services/#commission",
                            "link_label": "Learn more",
                        },
                        {
                            "icon": "",
                            "image": self.images["SERVICE_RESTORATION"].pk,
                            "title": "The Restoration",
                            "description": (
                                "<p>Breathing new life into antique furniture and period "
                                "kitchens. Respect for heritage, executed with precision.</p>"
                            ),
                            "link_url": "/services/#restoration",
                            "link_label": "Learn more",
                        },
                        {
                            "icon": "",
                            "image": self.images["SERVICE_LARDER"].pk,
                            "title": "The Larder",
                            "description": (
                                "<p>Standalone pantry units and storage solutions. The "
                                "perfect introduction to Sage & Stone craftsmanship.</p>"
                            ),
                            "link_url": "/services/#larder",
                            "link_label": "Learn more",
                        },
                    ],
                    "layout_style": "default",
                },
            },
            {
                "type": "featured_case_study",
                "value": {
                    "eyebrow": "Provenance Signature",
                    "heading": "Every piece tells a story",
                    "intro": (
                        "<p>Each Sage & Stone kitchen carries a hand-engraved brass plate "
                        "documenting its maker, timber source, and completion date.</p>"
                    ),
                    "points": [
                        "Hand-engraved by our master craftsmen",
                        "GPS coordinates of timber source",
                        "Unique serial number for lifetime support",
                    ],
                    "cta_text": "Learn about our materials",
                    "cta_url": "/about/#materials",
                    "image": self.images["PROVENANCE_IMAGE"].pk,
                    "image_alt": "Brass maker's plate with engraved details",
                    "stats_label": "Kitchens completed",
                    "stats_value": "247",
                },
            },
            {
                "type": "portfolio",
                "value": {
                    "eyebrow": "Case Files",
                    "heading": "Recent Commissions",
                    "intro": "",
                    "view_all_link": "/portfolio/",
                    "view_all_label": "View all projects",
                    "items": [
                        {
                            "title": "The Kensington Commission",
                            "category": "kitchen",
                            "image": self.images["PORTFOLIO_KENSINGTON"].pk,
                            "alt_text": "Kensington commission kitchen interior",
                            "link_url": "/portfolio/#kensington",
                        },
                        {
                            "title": "The Cotswold Barn",
                            "category": "kitchen",
                            "image": self.images["PORTFOLIO_COTSWOLD"].pk,
                            "alt_text": "Cotswold barn kitchen interior",
                            "link_url": "/portfolio/#cotswold",
                        },
                        {
                            "title": "The Georgian Townhouse",
                            "category": "kitchen",
                            "image": self.images["PORTFOLIO_GEORGIAN"].pk,
                            "alt_text": "Georgian townhouse kitchen interior",
                            "link_url": "/portfolio/#georgian",
                        },
                    ],
                },
            },
            {
                "type": "featured_case_study",
                "value": {
                    "eyebrow": "Featured Commission",
                    "heading": "The Surrey Commission",
                    "intro": (
                        "<p>A complete kitchen transformation for a Grade II listed "
                        "property in the Surrey Hills.</p>"
                    ),
                    "points": [
                        "English oak from managed woodland",
                        "Hand-cut dovetail joints throughout",
                        "Integrated appliances from Gaggenau",
                    ],
                    "cta_text": "Read the full case study",
                    "cta_url": "/portfolio/#surrey",
                    "image": self.images["SURREY_IMAGE"].pk,
                    "image_alt": "Surrey kitchen with oak cabinetry",
                    "stats_label": "Project duration",
                    "stats_value": "14 weeks",
                },
            },
            {
                "type": "social_proof_quote",
                "value": {
                    "quote": (
                        "The attention to detail is extraordinary. Every drawer, every "
                        "hinge--it's like working with artisans from another era."
                    ),
                    "author": "Sarah M.",
                    "role": "Homeowner",
                    "company": "Surrey Hills",
                    "logo": None,
                },
            },
            {
                "type": "faq",
                "value": {
                    "eyebrow": "Commission Protocols",
                    "heading": "How It Works",
                    "intro": "",
                    "items": [
                        {
                            "question": "Timeline & Pacing",
                            "answer": (
                                "<p>Every commission begins with a site visit and design "
                                "consultation. From approval to installation typically "
                                "takes 12-16 weeks. We limit ourselves to 12 commissions "
                                "per year to ensure every project receives our full "
                                "attention.</p>"
                            ),
                        },
                        {
                            "question": "Material Provenance",
                            "answer": (
                                "<p>We source timber exclusively from managed British "
                                "woodlands. Each piece is tracked from tree to kitchen, "
                                "with full documentation of origin, seasoning time, and "
                                "milling date.</p>"
                            ),
                        },
                        {
                            "question": "International Works",
                            "answer": (
                                "<p>We undertake select international commissions in "
                                "Europe and North America. International projects require "
                                "a minimum engagement and extended lead times. Contact us "
                                "to discuss feasibility.</p>"
                            ),
                        },
                    ],
                    "allow_multiple_open": False,
                },
            },
            {
                "type": "contact_form",
                "value": {
                    "eyebrow": "Begin the Conversation",
                    "heading": "Request a Consultation",
                    "intro": (
                        "<p>Tell us about your project and we'll be in touch within "
                        "48 hours.</p>"
                    ),
                    "success_message": "Thank you for your enquiry. We'll be in touch shortly.",
                    "submit_label": "Send Enquiry",
                },
            },
        ]

        home_page.save_revision().publish()
        self.stdout.write("  Populated homepage content")

    def _get_or_create_standard_page(
        self,
        *,
        home_page: HomePage,
        slug: str,
        title: str,
        seo_title: str,
        search_description: str,
        show_in_menus: bool,
        body: list[dict[str, Any]],
    ) -> tuple[StandardPage, bool]:
        try:
            page = StandardPage.objects.child_of(home_page).get(slug=slug)
            page.title = title
            page.seo_title = seo_title
            page.search_description = search_description
            page.show_in_menus = show_in_menus
            page.body = body
            page.save_revision().publish()
            return page, False
        except StandardPage.DoesNotExist:
            pass

        conflict = home_page.get_children().filter(slug=slug).first()
        if conflict is not None:
            self.stdout.write(
                self.style.WARNING(
                    f"Existing page with slug '{slug}' is not a StandardPage; renaming it."
                )
            )
            conflict_page = conflict.specific
            conflict_page.slug = f"{slug}-legacy-{conflict_page.id}"
            conflict_page.title = f"{conflict_page.title} (Legacy)"
            conflict_page.save()
            conflict_page.save_revision().publish()

        page = StandardPage(
            title=title,
            slug=slug,
            seo_title=seo_title,
            search_description=search_description,
            show_in_menus=show_in_menus,
            body=body,
        )
        home_page.add_child(instance=page)
        page.save_revision().publish()
        return page, True

    def _create_about_page(self, home_page: HomePage) -> StandardPage:
        """Create About page with full content."""
        body = [
            {
                "type": "hero_gradient",
                "value": {
                    "headline": "Craftsmanship built on <em>obsession</em>",
                    "subheadline": (
                        "Three decades of refining our craft. One mission: kitchens "
                        "that outlast trends."
                    ),
                    "ctas": [],
                    "status": "",
                    "gradient_style": "primary",
                },
            },
            {
                "type": "featured_case_study",
                "value": {
                    "eyebrow": "A Letter from the Founder",
                    "heading": "Thomas J. Wright",
                    "intro": (
                        "<p>I started Sage & Stone because I was tired of watching "
                        "beautiful timber turned into forgettable furniture.</p>"
                        "<p>Every kitchen we build is an argument against "
                        "disposability--a physical reminder that permanence is possible."
                        "</p><p>We don't chase trends. We don't cut corners. We build "
                        "rooms that your grandchildren will cook Sunday lunch in.</p>"
                    ),
                    "points": [],
                    "cta_text": "",
                    "cta_url": "",
                    "image": self.images["FOUNDER_IMAGE"].pk,
                    "image_alt": "Thomas J. Wright, Master Joiner and Founder",
                    "stats_label": "Years of experience",
                    "stats_value": "28",
                },
            },
            {
                "type": "service_cards",
                "value": {
                    "eyebrow": "Our Standards",
                    "heading": "The Sage & Stone Etiquette",
                    "intro": "Three non-negotiable principles that guide every commission.",
                    "view_all_link": "",
                    "view_all_label": "",
                    "cards": [
                        {
                            "icon": "",
                            "image": None,
                            "title": "Invisible Tradesmen",
                            "description": (
                                "<p>You'll never know we were there. Sites are left "
                                "cleaner than we found them. No radio, no mess, no drama.</p>"
                            ),
                            "link_url": "",
                            "link_label": "",
                        },
                        {
                            "icon": "",
                            "image": None,
                            "title": "Obsessive Cleanliness",
                            "description": (
                                "<p>Daily dust extraction, floor protection, and sealed "
                                "work areas. We treat your home like our workshop.</p>"
                            ),
                            "link_url": "",
                            "link_label": "",
                        },
                        {
                            "icon": "",
                            "image": None,
                            "title": "Vetted & Permanent",
                            "description": (
                                "<p>Every team member has been with us for 5+ years. No "
                                "subcontractors, no strangers in your home.</p>"
                            ),
                            "link_url": "",
                            "link_label": "",
                        },
                    ],
                    "layout_style": "tight",
                },
            },
            {
                "type": "team_members",
                "value": {
                    "eyebrow": "Meet the Makers",
                    "heading": "The people behind every commission",
                    "members": [
                        {
                            "name": "James E.",
                            "role": "Head of Installation",
                            "bio": "15 years precision fitting",
                            "photo": self.images["TEAM_JAMES"].pk,
                            "alt_text": "Portrait of James E., Head of Installation",
                        },
                        {
                            "name": "Sarah M.",
                            "role": "Finishing Specialist",
                            "bio": "Traditional hand-finishing techniques",
                            "photo": self.images["TEAM_SARAH"].pk,
                            "alt_text": "Portrait of Sarah M., Finishing Specialist",
                        },
                        {
                            "name": "David R.",
                            "role": "Master Joiner",
                            "bio": "Third-generation craftsman",
                            "photo": self.images["TEAM_DAVID"].pk,
                            "alt_text": "Portrait of David R., Master Joiner",
                        },
                        {
                            "name": "Marcus T.",
                            "role": "Project Director",
                            "bio": "Your single point of contact",
                            "photo": self.images["TEAM_MARCUS"].pk,
                            "alt_text": "Portrait of Marcus T., Project Director",
                        },
                    ],
                },
            },
            {
                "type": "featured_case_study",
                "value": {
                    "eyebrow": "The Workshop",
                    "heading": "Herefordshire, Est. 2005",
                    "intro": (
                        "<p>Our solar-powered facility in the Herefordshire countryside "
                        "is where every Sage & Stone piece comes to life.</p>"
                        "<p>We maintain an open workshop policy--clients are welcome to "
                        "visit and witness their kitchen taking shape.</p>"
                    ),
                    "points": [
                        "4,000 sq ft purpose-built facility",
                        "Solar-powered operations",
                        "Open workshop visits available",
                    ],
                    "cta_text": "Schedule a workshop visit",
                    "cta_url": "/contact/",
                    "image": self.images["WORKSHOP_IMAGE"].pk,
                    "image_alt": "Sage & Stone workshop interior",
                    "stats_label": "Years at this location",
                    "stats_value": "20",
                },
            },
            {
                "type": "buttons",
                "value": {
                    "alignment": "center",
                    "buttons": [
                        {
                            "label": "Request a Site Visit",
                            "url": "/contact/",
                            "style": "primary",
                        }
                    ],
                },
            },
        ]

        page, created = self._get_or_create_standard_page(
            home_page=home_page,
            slug="about",
            title="About Us",
            seo_title="About Sage & Stone | Our Story & Craftsmen",
            search_description=(
                "Meet the makers behind Sage & Stone. 28 years of master joinery "
                "experience. Herefordshire workshop, lifetime guarantee."
            ),
            show_in_menus=True,
            body=body,
        )
        message = "  Created About page" if created else "  Updated About page"
        self.stdout.write(message)
        return page

    def _create_services_page(self, home_page: HomePage) -> StandardPage:
        """Create Services page with full content."""
        body = [
            {
                "type": "hero_gradient",
                "value": {
                    "headline": "Precision <em>Installation</em>",
                    "subheadline": (
                        "Total project management from first measurement to final "
                        "polish."
                    ),
                    "ctas": [],
                    "gradient_style": "primary",
                },
            },
            {
                "type": "manifesto",
                "value": {
                    "eyebrow": "The White Glove Standard",
                    "heading": "Installation is not an afterthought",
                    "body": (
                        "<p>Too many beautiful kitchens are ruined by poor installation. "
                        "At Sage & Stone, installation is where our obsession with detail "
                        "truly shows. Every gap, every alignment, every finish--measured "
                        "to the millimetre.</p>"
                    ),
                    "quote": "Millimetre-perfect is not a goal. It is the baseline.",
                },
            },
            {
                "type": "process",
                "value": {
                    "eyebrow": "The Process",
                    "heading": "Five Phases to Completion",
                    "intro": "Every installation follows our proven methodology.",
                    "steps": [
                        {
                            "number": 1,
                            "title": "Consultation",
                            "description": (
                                "<p>Site survey, design brief, and feasibility assessment."
                                "</p>"
                            ),
                        },
                        {
                            "number": 2,
                            "title": "Strip-Out",
                            "description": (
                                "<p>Careful removal of existing fixtures with full site "
                                "protection.</p>"
                            ),
                        },
                        {
                            "number": 3,
                            "title": "Installation",
                            "description": (
                                "<p>Precision fitting of cabinetry, worktops, and "
                                "integrated appliances.</p>"
                            ),
                        },
                        {
                            "number": 4,
                            "title": "Calibration",
                            "description": (
                                "<p>Fine-tuning of doors, drawers, and hardware for "
                                "perfect operation.</p>"
                            ),
                        },
                        {
                            "number": 5,
                            "title": "Handover",
                            "description": (
                                "<p>Full demonstration, documentation, and aftercare "
                                "guidance.</p>"
                            ),
                        },
                    ],
                },
            },
            {
                "type": "service_cards",
                "value": {
                    "eyebrow": "What We Handle",
                    "heading": "Complete Project Management",
                    "intro": "",
                    "cards": [
                        {
                            "icon": "",
                            "image": self.images["SERVICE_APPLIANCE"].pk,
                            "title": "Appliance Integration",
                            "description": (
                                "<p>Seamless fitting of all integrated appliances, from "
                                "refrigeration to extraction.</p>"
                            ),
                            "link_url": "",
                            "link_label": "",
                        },
                        {
                            "icon": "",
                            "image": self.images["SERVICE_JOINERY"].pk,
                            "title": "Bespoke Joinery",
                            "description": (
                                "<p>On-site adjustments and custom fitting to accommodate "
                                "period properties.</p>"
                            ),
                            "link_url": "",
                            "link_label": "",
                        },
                        {
                            "icon": "",
                            "image": self.images["SERVICE_TECHNICAL"].pk,
                            "title": "Technical Integration",
                            "description": (
                                "<p>Plumbing, electrical, and gas connections by "
                                "certified specialists.</p>"
                            ),
                            "link_url": "",
                            "link_label": "",
                        },
                        {
                            "icon": "",
                            "image": self.images["SERVICE_STONE"].pk,
                            "title": "Stone & Surfaces",
                            "description": (
                                "<p>Precision templating and installation of worktops and "
                                "splashbacks.</p>"
                            ),
                            "link_url": "",
                            "link_label": "",
                        },
                    ],
                    "layout_style": "default",
                },
            },
            {
                "type": "service_cards",
                "value": {
                    "eyebrow": "The Cleanliness Pledge",
                    "heading": "Four Guarantees",
                    "intro": "Your home deserves the same respect as our workshop.",
                    "cards": [
                        {
                            "icon": "",
                            "image": None,
                            "title": "Daily Clean",
                            "description": (
                                "<p>Work areas cleaned and vacuumed at the end of every "
                                "day.</p>"
                            ),
                            "link_url": "",
                            "link_label": "",
                        },
                        {
                            "icon": "",
                            "image": None,
                            "title": "Floor Protection",
                            "description": (
                                "<p>Heavy-duty floor coverings throughout the project "
                                "duration.</p>"
                            ),
                            "link_url": "",
                            "link_label": "",
                        },
                        {
                            "icon": "",
                            "image": None,
                            "title": "Dust Extraction",
                            "description": (
                                "<p>Industrial extraction at source for all cutting and "
                                "sanding.</p>"
                            ),
                            "link_url": "",
                            "link_label": "",
                        },
                        {
                            "icon": "",
                            "image": None,
                            "title": "Sealed Zones",
                            "description": (
                                "<p>Work areas sealed from living spaces with temporary "
                                "partitions.</p>"
                            ),
                            "link_url": "",
                            "link_label": "",
                        },
                    ],
                    "layout_style": "tight",
                },
            },
            {
                "type": "gallery",
                "value": {
                    "eyebrow": "The Details",
                    "heading": "Obsession in every joint",
                    "intro": "",
                    "images": [
                        {
                            "image": self.images["DETAIL_1"].pk,
                            "alt_text": "Hand-cut dovetail joint detail",
                            "caption": "",
                        },
                        {
                            "image": self.images["DETAIL_2"].pk,
                            "alt_text": "Precision hinge alignment",
                            "caption": "",
                        },
                        {
                            "image": self.images["DETAIL_3"].pk,
                            "alt_text": "Hand-finished oak surface",
                            "caption": "",
                        },
                    ],
                },
            },
            {
                "type": "trust_strip_logos",
                "value": {
                    "eyebrow": "Certifications & Memberships",
                    "items": [
                        {
                            "logo": self.images["LOGO_GASSAFE"].pk,
                            "alt_text": "Gas Safe Registered",
                            "url": "",
                        },
                        {
                            "logo": self.images["LOGO_NICEIC"].pk,
                            "alt_text": "NICEIC Approved",
                            "url": "",
                        },
                        {
                            "logo": self.images["LOGO_BIKBBI"].pk,
                            "alt_text": "BiKBBI Member",
                            "url": "",
                        },
                        {
                            "logo": self.images["LOGO_GUILD"].pk,
                            "alt_text": "Guild of Master Craftsmen",
                            "url": "",
                        },
                    ],
                },
            },
            {
                "type": "faq",
                "value": {
                    "eyebrow": "Common Questions",
                    "heading": "Installation FAQs",
                    "intro": "",
                    "items": [
                        {
                            "question": "What is the typical lead time for installation?",
                            "answer": (
                                "<p>Installation typically begins 10-12 weeks after design "
                                "approval, allowing time for material sourcing and "
                                "workshop production. The installation phase itself takes "
                                "2-3 weeks depending on project scope.</p>"
                            ),
                        },
                        {
                            "question": "Do you install flat-pack kitchens?",
                            "answer": (
                                "<p>No. We only install kitchens built in our Herefordshire "
                                "workshop. Every piece is crafted specifically for your "
                                "space--flat-pack has no place in our process.</p>"
                            ),
                        },
                        {
                            "question": "How do you manage other trades?",
                            "answer": (
                                "<p>We coordinate all required trades including plumbing, "
                                "electrical, and plastering. Our project director serves "
                                "as your single point of contact, managing the entire "
                                "installation timeline.</p>"
                            ),
                        },
                    ],
                    "allow_multiple_open": False,
                },
            },
        ]

        page, created = self._get_or_create_standard_page(
            home_page=home_page,
            slug="services",
            title="Services",
            seo_title="Our Services | Bespoke Kitchen Installation | Sage & Stone",
            search_description=(
                "Total project management from first measurement to final polish. "
                "Precision installation, white glove service."
            ),
            show_in_menus=True,
            body=body,
        )
        message = "  Created Services page" if created else "  Updated Services page"
        self.stdout.write(message)
        return page

    def _create_portfolio_page(self, home_page: HomePage) -> StandardPage:
        """Create Portfolio page with full content."""
        body = [
            {
                "type": "editorial_header",
                "value": {
                    "align": "center",
                    "eyebrow": "Our Work",
                    "heading": "The Portfolio",
                },
            },
            {
                "type": "featured_case_study",
                "value": {
                    "eyebrow": "Featured",
                    "heading": "The Highland Commission",
                    "intro": (
                        "<p>A complete kitchen and utility suite for a Scottish estate, "
                        "featuring locally-sourced larch and hand-forged ironmongery.</p>"
                    ),
                    "points": [],
                    "cta_text": "View project",
                    "cta_url": "#highland",
                    "image": self.images["PORTFOLIO_HIGHLAND"].pk,
                    "image_alt": "Highland Commission kitchen interior",
                    "stats_label": "",
                    "stats_value": "",
                },
            },
            {
                "type": "portfolio",
                "value": {
                    "eyebrow": "",
                    "heading": "Selected Works",
                    "intro": "",
                    "view_all_link": "",
                    "view_all_label": "",
                    "items": [
                        {
                            "title": "The Pantry Larder",
                            "category": "furniture",
                            "image": self.images["PORTFOLIO_LARDER"].pk,
                            "alt_text": "Pantry larder in English oak",
                            "services": "Freestanding larder unit in English oak",
                            "link_url": "#pantry-larder",
                        },
                        {
                            "title": "The Georgian Restoration",
                            "category": "restoration",
                            "image": self.images["PORTFOLIO_GEORGIAN_REST"].pk,
                            "alt_text": "Georgian restoration kitchen",
                            "services": "Period-sympathetic kitchen for a 1780s townhouse",
                            "link_url": "#georgian-restoration",
                        },
                        {
                            "title": "The Brutalist Barn",
                            "category": "kitchen",
                            "image": self.images["PORTFOLIO_BRUTALIST"].pk,
                            "alt_text": "Brutalist barn kitchen interior",
                            "services": "Contemporary design meets agricultural character",
                            "link_url": "#brutalist-barn",
                        },
                        {
                            "title": "The Utility Room",
                            "category": "furniture",
                            "image": self.images["PORTFOLIO_UTILITY"].pk,
                            "alt_text": "Utility room storage and boot room",
                            "services": "Boot room and utility suite",
                            "link_url": "#utility-room",
                        },
                    ],
                },
            },
            {
                "type": "quote",
                "value": {
                    "quote": "We don't build against nature. We negotiate with it.",
                    "author": "Thomas J. Wright",
                    "role": "Founder",
                },
            },
            {
                "type": "buttons",
                "value": {
                    "alignment": "center",
                    "buttons": [
                        {
                            "label": "Enquire for 2026",
                            "url": "/contact/",
                            "style": "primary",
                        },
                        {
                            "label": "Read about our process",
                            "url": "/services/",
                            "style": "secondary",
                        },
                    ],
                },
            },
        ]

        page, created = self._get_or_create_standard_page(
            home_page=home_page,
            slug="portfolio",
            title="Portfolio",
            seo_title="Our Portfolio | Bespoke Kitchen Projects | Sage & Stone",
            search_description=(
                "Explore our collection of bespoke kitchen commissions. Heritage, "
                "modernist, and utility designs crafted in Herefordshire."
            ),
            show_in_menus=True,
            body=body,
        )
        message = "  Created Portfolio page" if created else "  Updated Portfolio page"
        self.stdout.write(message)
        return page

    def _create_contact_page(self, home_page: HomePage) -> StandardPage:
        """Create Contact page."""
        body = [
            {
                "type": "hero_gradient",
                "value": {
                    "headline": "Begin Your <em>Commission</em>",
                    "subheadline": (
                        "Tell us about your project and we'll be in touch within 48 "
                        "hours."
                    ),
                    "ctas": [],
                    "gradient_style": "primary",
                },
            },
            {
                "type": "contact_form",
                "value": {
                    "eyebrow": "",
                    "heading": "Request a Consultation",
                    "intro": (
                        "<p>Whether you're ready to begin or simply exploring "
                        "possibilities, we'd love to hear from you.</p>"
                    ),
                    "success_message": (
                        "Thank you for your enquiry. We'll be in touch within 48 hours."
                    ),
                    "submit_label": "Send Enquiry",
                },
            },
        ]

        page, created = self._get_or_create_standard_page(
            home_page=home_page,
            slug="contact",
            title="Contact",
            seo_title="Contact Us | Begin Your Commission | Sage & Stone",
            search_description=(
                "Ready to begin your bespoke kitchen journey? Contact Sage & Stone for "
                "a consultation."
            ),
            show_in_menus=False,
            body=body,
        )
        message = "  Created Contact page" if created else "  Updated Contact page"
        self.stdout.write(message)
        return page

    def _get_navigation_pages(self, *, site: Site, home_page: Page) -> dict[str, Page]:
        """Resolve navigation pages for the header/footer, with home fallbacks."""
        root = site.root_page or home_page
        slug_groups = {
            "about": ["about", "who-we-are"],
            "services": ["services", "what-we-do"],
            "portfolio": ["portfolio", "our-portfolio", "kitchens"],
            "blog_index": ["journal", "blog", "blog-index"],
            "contact": ["contact", "enquire", "enquiry"],
            "terms": ["terms", "terms-of-service", "terms-of-supply"],
        }
        all_slugs = {slug for group in slug_groups.values() for slug in group}
        pages_by_slug = self._build_pages_by_slug(root, all_slugs)

        return {
            "home": home_page,
            "about": self._get_page_by_slugs(
                root, slug_groups["about"], pages_by_slug=pages_by_slug
            )
            or home_page,
            "services": self._get_page_by_slugs(
                root, slug_groups["services"], pages_by_slug=pages_by_slug
            )
            or home_page,
            "portfolio": self._get_page_by_slugs(
                root, slug_groups["portfolio"], pages_by_slug=pages_by_slug
            )
            or home_page,
            "blog_index": self._get_page_by_slugs(
                root, slug_groups["blog_index"], pages_by_slug=pages_by_slug
            )
            or home_page,
            "contact": self._get_page_by_slugs(
                root, slug_groups["contact"], pages_by_slug=pages_by_slug
            )
            or home_page,
            "terms": self._get_page_by_slugs(
                root, slug_groups["terms"], pages_by_slug=pages_by_slug
            )
            or home_page,
        }

    def _build_pages_by_slug(self, root: Page, slugs: set[str]) -> dict[str, Page]:
        """Build a lookup of page.slug -> Page for candidate slugs."""
        if not slugs:
            return {}

        candidates = root.get_descendants(inclusive=True).filter(slug__in=slugs)
        pages_by_slug: dict[str, Page] = {}
        for page in candidates:
            pages_by_slug.setdefault(page.slug, page)
        return pages_by_slug

    def _get_page_by_slugs(
        self,
        root: Page,
        slugs: list[str],
        *,
        pages_by_slug: dict[str, Page] | None = None,
    ) -> Page | None:
        """Return the first matching page for the given slug priority list."""
        if not slugs:
            return None

        pages_by_slug = pages_by_slug or self._build_pages_by_slug(root, set(slugs))

        for slug in slugs:
            page = pages_by_slug.get(slug)
            if page:
                return page
        return None

    def _configure_navigation(
        self, *, site: Site, pages: dict[str, Page]
    ) -> HeaderNavigation:
        """Configure header and footer navigation settings for the site."""
        header = HeaderNavigation.for_site(site)
        contact = pages["contact"]

        header.show_phone_in_header = True

        header.header_cta_enabled = True
        header.header_cta_text = "Enquire"
        header.header_cta_link = self._build_enquire_cta_link(page_id=contact.id)

        header.mobile_cta_enabled = True
        header.mobile_cta_phone_enabled = True
        header.mobile_cta_button_enabled = True
        header.mobile_cta_button_text = "Enquire"
        header.mobile_cta_button_link = self._build_enquire_cta_link(page_id=contact.id)

        header.menu_items = self._build_menu_items(pages)
        header.save()
        self.stdout.write("Configured header navigation")

        self._configure_footer_navigation(site=site, pages=pages)
        return header

    def _build_enquire_cta_link(self, *, page_id: int) -> list[dict[str, Any]]:
        """Build a single link payload for the Enquire CTA."""
        return [
            {
                "type": "link",
                "value": {
                    "link_type": "page",
                    "page": page_id,
                    "link_text": "Enquire",
                },
            }
        ]

    def _build_menu_items(self, pages: dict[str, Page]) -> list[dict[str, Any]]:
        """Build the header menu items, including the Kitchens mega menu."""
        portfolio = pages["portfolio"]
        services = pages["services"]
        about = pages["about"]
        blog_index = pages["blog_index"]

        return [
            {
                "type": "item",
                "value": {
                    "label": "Kitchens",
                    "link": {
                        "link_type": "page",
                        "page": portfolio.id,
                        "link_text": "Kitchens",
                    },
                    "children": [
                        {
                            "label": "Collections",
                            "link": {
                                "link_type": "anchor",
                                "anchor": "collections",
                                "link_text": "Collections",
                            },
                            "children": [
                                {
                                    "label": "The Heritage",
                                    "link": {
                                        "link_type": "url",
                                        "url": "/portfolio/?collection=heritage",
                                        "link_text": "The Heritage",
                                    },
                                },
                                {
                                    "label": "The Modernist",
                                    "link": {
                                        "link_type": "url",
                                        "url": "/portfolio/?collection=modernist",
                                        "link_text": "The Modernist",
                                    },
                                },
                                {
                                    "label": "The Utility",
                                    "link": {
                                        "link_type": "url",
                                        "url": "/portfolio/?collection=utility",
                                        "link_text": "The Utility",
                                    },
                                },
                            ],
                        },
                        {
                            "label": "Fitted Joinery",
                            "link": {
                                "link_type": "anchor",
                                "anchor": "fitted-joinery",
                                "link_text": "Fitted Joinery",
                            },
                            "children": [
                                {
                                    "label": "Larder Cupboards",
                                    "link": {
                                        "link_type": "url",
                                        "url": "/portfolio/?type=larder",
                                        "link_text": "Larder Cupboards",
                                    },
                                },
                                {
                                    "label": "Island Units",
                                    "link": {
                                        "link_type": "url",
                                        "url": "/portfolio/?type=island",
                                        "link_text": "Island Units",
                                    },
                                },
                                {
                                    "label": "Wall Cabinetry",
                                    "link": {
                                        "link_type": "url",
                                        "url": "/portfolio/?type=wall",
                                        "link_text": "Wall Cabinetry",
                                    },
                                },
                                {
                                    "label": "Boot Room Storage",
                                    "link": {
                                        "link_type": "url",
                                        "url": "/portfolio/?type=bootroom",
                                        "link_text": "Boot Room Storage",
                                    },
                                },
                            ],
                        },
                        {
                            "label": "Freestanding",
                            "link": {
                                "link_type": "anchor",
                                "anchor": "freestanding",
                                "link_text": "Freestanding",
                            },
                            "children": [
                                {
                                    "label": "Prep Tables",
                                    "link": {
                                        "link_type": "url",
                                        "url": "/portfolio/?type=prep-table",
                                        "link_text": "Prep Tables",
                                    },
                                },
                                {
                                    "label": "Butcher Blocks",
                                    "link": {
                                        "link_type": "url",
                                        "url": "/portfolio/?type=butcher-block",
                                        "link_text": "Butcher Blocks",
                                    },
                                },
                                {
                                    "label": "Dressers",
                                    "link": {
                                        "link_type": "url",
                                        "url": "/portfolio/?type=dresser",
                                        "link_text": "Dressers",
                                    },
                                },
                            ],
                        },
                    ],
                },
            },
            self._build_simple_menu_item(label="What We Do", page=services),
            self._build_simple_menu_item(label="Who We Are", page=about),
            self._build_simple_menu_item(label="Portfolio", page=portfolio),
            self._build_simple_menu_item(label="Journal", page=blog_index),
        ]

    def _build_simple_menu_item(self, *, label: str, page: Page) -> dict[str, Any]:
        """Build a single-level menu item pointing to a page."""
        return {
            "type": "item",
            "value": {
                "label": label,
                "link": {
                    "link_type": "page",
                    "page": page.id,
                    "link_text": label,
                },
                "children": [],
            },
        }

    def _configure_footer_navigation(
        self, *, site: Site, pages: dict[str, Page]
    ) -> FooterNavigation:
        """Configure footer link sections, tagline, and social overrides."""
        about = pages["about"]
        services = pages["services"]
        portfolio = pages["portfolio"]
        blog_index = pages["blog_index"]
        terms = pages["terms"]

        footer = FooterNavigation.for_site(site)
        footer.tagline = "Rooms that remember."
        footer.auto_service_areas = False
        footer.social_instagram = "https://instagram.com/sageandstone"
        footer.social_facebook = ""
        footer.social_linkedin = ""
        footer.social_youtube = ""
        footer.social_x = ""
        footer.copyright_text = "© {year} Sage & Stone Ltd. All rights reserved."

        explore_links = [
            self._build_footer_link(
                link_type="page", page=about.id, link_text="Who We Are"
            ),
            self._build_footer_link(
                link_type="page", page=services.id, link_text="What We Do"
            ),
            self._build_footer_link(
                link_type="page", page=blog_index.id, link_text="Journal"
            ),
            self._build_footer_link(
                link_type="page", page=portfolio.id, link_text="Our Portfolio"
            ),
        ]
        legal_links = [
            self._build_footer_link(
                link_type="url", url="/privacy/", link_text="Privacy Policy"
            ),
            self._build_footer_link(
                link_type="page", page=terms.id, link_text="Terms of Service"
            ),
            self._build_footer_link(
                link_type="url", url="/accessibility/", link_text="Accessibility"
            ),
        ]
        studio_links = [
            self._build_footer_link(
                link_type="anchor",
                anchor="studio-address",
                link_text="The Old Joinery, Unit 4",
            ),
            self._build_footer_link(
                link_type="anchor",
                anchor="studio-postcode",
                link_text="Herefordshire HR4 9AB",
            ),
            self._build_footer_link(
                link_type="email",
                email="hello@sageandstone.com",
                link_text="hello@sageandstone.com",
            ),
            self._build_footer_link(
                link_type="phone",
                phone="+44 (0) 20 1234 5678",
                link_text="+44 (0) 20 1234 5678",
            ),
        ]

        footer.link_sections = [
            self._build_footer_section(title="Explore", links=explore_links),
            self._build_footer_section(title="Legal", links=legal_links),
            self._build_footer_section(title="Studio", links=studio_links),
        ]

        footer.save()
        self.stdout.write("Configured footer navigation")
        return footer

    def _build_footer_section(
        self, *, title: str, links: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Build a footer section payload for link_sections."""
        return {
            "type": "section",
            "value": {
                "title": title,
                "links": links,
            },
        }

    def _build_footer_link(
        self, *, link_type: str, link_text: str, **kwargs: Any
    ) -> dict[str, Any]:
        """Build a UniversalLink-style payload for footer links."""
        link = {
            "link_type": link_type,
            "link_text": link_text,
        }
        link.update(kwargs)
        return link

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
