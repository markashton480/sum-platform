"""
Seed a theme showroom for SUM Platform client projects.

This management command is intended to run inside any generated client project
(`sum init <client> --theme <theme_slug>`), creating a predictable showroom
site tree and navigation settings so theme development can start immediately.

It creates:
- A HomePage (client-owned model) and sets it as the default Wagtail Site root
- A StandardPage showroom + a Contact StandardPage
- A ServiceIndexPage and two ServicePage children
- Example content that showcases *all* blocks available in sum_core.PageStreamBlock,
  spread across multiple pages (not all on one page)
- Branding SiteSettings and Navigation (HeaderNavigation / FooterNavigation)

Usage:
    python manage.py seed_showroom
    python manage.py seed_showroom --clear
    python manage.py seed_showroom --hostname localhost --port 8000
    python manage.py seed_showroom --homepage-model home.HomePage
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from io import BytesIO
from typing import Any

from django.apps import apps
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandParser
from django.db import transaction
from wagtail.models import Page, Site

from sum_core.blocks import PageStreamBlock
from sum_core.branding.models import SiteSettings
from sum_core.navigation.cache import invalidate_nav_cache
from sum_core.navigation.models import FooterNavigation, HeaderNavigation
from sum_core.pages import ServiceIndexPage, ServicePage, StandardPage

try:
    from PIL import Image as PILImage
except Exception:  # pragma: no cover
    PILImage = None


@dataclass(frozen=True)
class _ShowroomSlugs:
    home: str = "showroom-home"
    showroom: str = "showroom"
    contact: str = "contact"
    services: str = "services"
    service_one: str = "solar-installation"
    service_two: str = "roofing"


class Command(BaseCommand):
    help = "Create a theme showroom site tree, blocks, and navigation."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete existing showroom pages (by slug) before re-seeding.",
        )
        parser.add_argument(
            "--hostname",
            default=None,
            help="Set the default Site hostname (defaults to existing or 'localhost').",
        )
        parser.add_argument(
            "--port",
            type=int,
            default=None,
            help="Set the default Site port (defaults to existing or 8000).",
        )
        parser.add_argument(
            "--homepage-model",
            default=None,
            help=(
                "Override HomePage model as 'app_label.ModelName' "
                "(defaults to first installed HomePage)."
            ),
        )

    @transaction.atomic
    def handle(self, *args: Any, **options: dict[str, Any]) -> None:
        slugs = _ShowroomSlugs()

        home_page_model = self._resolve_home_page_model(options.get("homepage_model"))
        if home_page_model is None:
            self.stdout.write(
                self.style.ERROR(
                    "Could not find a HomePage model. Ensure your client 'home' app is in INSTALLED_APPS."
                )
            )
            return

        root = Page.get_first_root_node()
        site = self._get_or_create_default_site(
            options.get("hostname"), options.get("port"), root
        )

        if options.get("clear"):
            self._clear_showroom(
                site=site, slugs=slugs, home_page_model=home_page_model
            )

        # Pages
        home = self._get_or_create_homepage(
            site=site, root=root, home_page_model=home_page_model, slugs=slugs
        )
        showroom = self._get_or_create_standard_page(
            parent=home, title="Showroom", slug=slugs.showroom
        )
        contact = self._get_or_create_standard_page(
            parent=home, title="Contact", slug=slugs.contact
        )
        services_index = self._get_or_create_services_index(
            parent=home, title="Services", slug=slugs.services
        )
        service_one = self._get_or_create_service_page(
            parent=services_index,
            title="Solar Installation",
            slug=slugs.service_one,
            short_description="Premium solar installs with clean, modern finishing.",
        )
        service_two = self._get_or_create_service_page(
            parent=services_index,
            title="Roofing",
            slug=slugs.service_two,
            short_description="Durable, weather-ready roofing from a trusted local team.",
        )

        # Media (placeholder images)
        images = self._get_or_create_showroom_images()

        # Content blocks (show all blocks across pages)
        home.body = self._build_home_stream(images=images, contact_page=contact)
        home.intro = (
            "<p>This is a seeded theme showroom for SUM Platform. "
            "Swap themes with <code>sum init ... --theme</code> and re-run this command.</p>"
        )
        home.save_revision().publish()

        showroom.body = self._build_showroom_stream(
            images=images,
            services_index=services_index,
            service_one=service_one,
            contact_page=contact,
        )
        showroom.save_revision().publish()

        services_index.intro = self._build_services_index_intro_stream(images=images)
        services_index.save_revision().publish()

        service_one.featured_image_id = images.service_featured_one_id
        service_one.body = self._build_service_page_stream(
            images=images, page=service_one, contact_page=contact
        )
        service_one.save_revision().publish()

        service_two.featured_image_id = images.service_featured_two_id
        service_two.body = self._build_service_page_stream(
            images=images, page=service_two, contact_page=contact
        )
        service_two.save_revision().publish()

        contact.body = self._build_contact_stream(images=images)
        contact.save_revision().publish()

        # Site settings (branding + navigation)
        self._seed_branding(site=site, images=images)
        self._seed_navigation(
            site=site,
            home=home,
            showroom=showroom,
            contact=contact,
            services_index=services_index,
            service_one=service_one,
            service_two=service_two,
        )
        invalidate_nav_cache(site.id)

        self.stdout.write(self.style.SUCCESS("✓ Showroom seeded"))
        self.stdout.write(f"  - Home: / (Wagtail site root -> {home.title})")
        self.stdout.write(f"  - Showroom: {showroom.url}")
        self.stdout.write(f"  - Services: {services_index.url}")
        self.stdout.write(f"  - Contact: {contact.url}")

    # -----------------------------------------------------------------------------
    # Model resolution / site helpers
    # -----------------------------------------------------------------------------

    def _resolve_home_page_model(self, dotted: str | None) -> Any | None:
        """
        Resolve the client-owned HomePage model.

        Strategy:
        - If --homepage-model is provided (app_label.ModelName), use it
        - Otherwise, prefer any app labeled 'home' that exposes HomePage
        - Fallback: first installed model named 'HomePage' that is a Page subclass
        """
        from wagtail.models import Page as WagtailPage

        if dotted:
            if "." not in dotted:
                raise ValueError("--homepage-model must be 'app_label.ModelName'")
            app_label, model_name = dotted.split(".", 1)
            return apps.get_model(app_label, model_name)

        # Prefer a 'home' app
        for app_config in apps.get_app_configs():
            if app_config.label == "home" or app_config.label.endswith(".home"):
                try:
                    return apps.get_model(app_config.label, "HomePage")
                except LookupError:
                    continue

        # Fallback: any installed HomePage model
        for model in apps.get_models():
            try:
                if model.__name__ == "HomePage" and issubclass(model, WagtailPage):
                    return model
            except TypeError:
                continue

        return None

    def _get_or_create_default_site(
        self, hostname: str | None, port: int | None, root: Page
    ) -> Site:
        Site.clear_site_root_paths_cache()

        site = Site.objects.filter(is_default_site=True).first()
        if site is None:
            site = Site.objects.create(
                hostname=hostname or "localhost",
                port=port or 8000,
                root_page=root,
                is_default_site=True,
                site_name="Showroom",
            )
        else:
            changed = False
            if hostname and site.hostname != hostname:
                site.hostname = hostname
                changed = True
            if port and site.port != port:
                site.port = port
                changed = True
            if not site.is_default_site:
                site.is_default_site = True
                changed = True
            if changed:
                site.save()

        Site.clear_site_root_paths_cache()
        return site

    def _clear_showroom(
        self, *, site: Site, slugs: _ShowroomSlugs, home_page_model: Any
    ) -> None:
        """
        Remove previously seeded pages without touching unrelated content.
        """
        self.stdout.write("Clearing existing showroom pages...")

        # Delete seeded children first (safe even if missing)
        for slug in [
            slugs.service_one,
            slugs.service_two,
        ]:
            ServicePage.objects.filter(slug=slug).delete()

        ServiceIndexPage.objects.filter(slug=slugs.services).delete()
        StandardPage.objects.filter(slug__in=[slugs.showroom, slugs.contact]).delete()

        # Do not delete HomePage by default (it is a singleton and may be user-edited).
        # If the current default site root *is* our showroom homepage slug, delete it.
        hp = home_page_model.objects.filter(slug=slugs.home).first()
        if hp and site.root_page_id == hp.id:
            site.root_page = Page.get_first_root_node()
            site.save()
            hp.delete()

        Site.clear_site_root_paths_cache()

    # -----------------------------------------------------------------------------
    # Page creation helpers
    # -----------------------------------------------------------------------------

    def _get_or_create_homepage(
        self, *, site: Site, root: Page, home_page_model: Any, slugs: _ShowroomSlugs
    ) -> Any:
        existing = home_page_model.objects.first()
        if existing:
            home = existing
        else:
            slug = slugs.home
            if root.get_children().filter(slug=slug).exists():
                slug = f"{slug}-1"

            home = home_page_model(
                title="Theme Showroom", slug=slug, intro="", body=None
            )
            root.add_child(instance=home)
            home.save_revision().publish()

        # Point default site root at the HomePage (homepage URL becomes "/")
        if site.root_page_id != home.id:
            site.root_page = home
            site.site_name = site.site_name or "Showroom"
            site.save()
            Site.clear_site_root_paths_cache()
        return home

    def _get_or_create_standard_page(
        self, *, parent: Page, title: str, slug: str
    ) -> StandardPage:
        existing = parent.get_children().type(StandardPage).filter(slug=slug).first()
        if existing:
            return existing.specific

        page = StandardPage(title=title, slug=slug, body=None)
        parent.add_child(instance=page)
        return page

    def _get_or_create_services_index(
        self, *, parent: Page, title: str, slug: str
    ) -> ServiceIndexPage:
        existing = (
            parent.get_children().type(ServiceIndexPage).filter(slug=slug).first()
        )
        if existing:
            return existing.specific

        page = ServiceIndexPage(title=title, slug=slug, intro=None)
        parent.add_child(instance=page)
        return page

    def _get_or_create_service_page(
        self,
        *,
        parent: ServiceIndexPage,
        title: str,
        slug: str,
        short_description: str,
    ) -> ServicePage:
        existing = parent.get_children().type(ServicePage).filter(slug=slug).first()
        if existing:
            svc = existing.specific
            svc.short_description = short_description
            svc.save()
            return svc

        page = ServicePage(
            title=title,
            slug=slug,
            short_description=short_description,
            featured_image=None,
            body=None,
        )
        parent.add_child(instance=page)
        return page

    # -----------------------------------------------------------------------------
    # Images
    # -----------------------------------------------------------------------------

    @dataclass(frozen=True)
    class _Images:
        hero_id: int
        legacy_hero_id: int
        comparison_before_id: int
        comparison_after_id: int
        gallery_one_id: int
        gallery_two_id: int
        gallery_three_id: int
        portfolio_one_id: int
        portfolio_two_id: int
        trust_logo_one_id: int
        trust_logo_two_id: int
        image_block_id: int
        service_featured_one_id: int
        service_featured_two_id: int
        brand_logo_id: int
        favicon_id: int

    def _get_or_create_showroom_images(self) -> _Images:
        hero = self._get_or_create_image("Showroom Hero", (1400, 900), "#0ea5e9")
        legacy_hero = self._get_or_create_image("Legacy Hero", (1200, 800), "#14b8a6")
        before = self._get_or_create_image("Comparison Before", (1400, 900), "#334155")
        after = self._get_or_create_image("Comparison After", (1400, 900), "#f97316")
        g1 = self._get_or_create_image("Gallery 1", (1200, 800), "#a855f7")
        g2 = self._get_or_create_image("Gallery 2", (1200, 800), "#22c55e")
        g3 = self._get_or_create_image("Gallery 3", (1200, 800), "#eab308")
        p1 = self._get_or_create_image("Portfolio 1", (1200, 900), "#0f172a")
        p2 = self._get_or_create_image("Portfolio 2", (1200, 900), "#1f2937")
        l1 = self._get_or_create_image("Trust Logo 1", (600, 360), "#111827")
        l2 = self._get_or_create_image("Trust Logo 2", (600, 360), "#0b1220")
        ib = self._get_or_create_image("Content Image", (1600, 900), "#64748b")
        sf1 = self._get_or_create_image("Service Featured 1", (1600, 900), "#2563eb")
        sf2 = self._get_or_create_image("Service Featured 2", (1600, 900), "#dc2626")
        brand = self._get_or_create_image("Brand Logo", (800, 400), "#0f172a")
        favicon = self._get_or_create_image("Favicon", (256, 256), "#0f172a")

        return self._Images(
            hero_id=hero.id,
            legacy_hero_id=legacy_hero.id,
            comparison_before_id=before.id,
            comparison_after_id=after.id,
            gallery_one_id=g1.id,
            gallery_two_id=g2.id,
            gallery_three_id=g3.id,
            portfolio_one_id=p1.id,
            portfolio_two_id=p2.id,
            trust_logo_one_id=l1.id,
            trust_logo_two_id=l2.id,
            image_block_id=ib.id,
            service_featured_one_id=sf1.id,
            service_featured_two_id=sf2.id,
            brand_logo_id=brand.id,
            favicon_id=favicon.id,
        )

    def _get_or_create_image(
        self, title: str, size: tuple[int, int], color_hex: str
    ) -> Any:
        from wagtail.images import get_image_model
        from wagtail.models import Collection

        image_model = get_image_model()
        existing = image_model.objects.filter(title=title).first()
        if existing:
            return existing

        if PILImage is None:  # pragma: no cover
            raise RuntimeError(
                "Pillow is required to generate placeholder images. "
                "Install it (it is usually included with Wagtail)."
            )

        rgb = self._hex_to_rgb(color_hex)
        img = PILImage.new("RGB", size, rgb)
        buf = BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)

        safe = self._slugify(title)
        filename = f"showroom-{safe}.png"
        collection = Collection.get_first_root_node()

        return image_model.objects.create(
            title=title,
            file=ContentFile(buf.read(), name=filename),
            collection=collection,
        )

    def _hex_to_rgb(self, value: str) -> tuple[int, int, int]:
        v = value.strip().lstrip("#")
        if len(v) != 6:
            return (127, 127, 127)
        return (int(v[0:2], 16), int(v[2:4], 16), int(v[4:6], 16))

    # -----------------------------------------------------------------------------
    # Stream builders (PageStreamBlock)
    # -----------------------------------------------------------------------------

    def _build_home_stream(self, *, images: _Images, contact_page: StandardPage) -> Any:
        stream_block = PageStreamBlock()
        return stream_block.to_python(
            [
                {
                    "type": "hero_image",
                    "value": {
                        "headline": "<p>Theme <em>Showroom</em></p>",
                        "subheadline": "A seeded site tree with every block, ready for theme development.",
                        "ctas": [
                            {
                                "label": "View the showroom",
                                "url": "/showroom/",
                                "style": "primary",
                                "open_in_new_tab": False,
                            },
                            {
                                "label": "Contact",
                                # NOTE: Use stable paths rather than page.url because this block uses URLBlock.
                                # page.url may be None for unpublished pages during seeding.
                                "url": "/contact/",
                                "style": "secondary",
                                "open_in_new_tab": False,
                            },
                        ],
                        "status": "SUM Platform",
                        "image": images.hero_id,
                        "image_alt": "A placeholder hero image for theme showcase",
                        "overlay_opacity": "medium",
                        "layout": "full",
                        "floating_card_label": "Avg. response time",
                        "floating_card_value": "< 2 hrs",
                    },
                },
                {
                    "type": "trust_strip_logos",
                    "value": {
                        "eyebrow": "Trusted by",
                        "items": [
                            {
                                "logo": images.trust_logo_one_id,
                                "alt_text": "Trust badge one",
                                "url": "https://example.com/",
                            },
                            {
                                "logo": images.trust_logo_two_id,
                                "alt_text": "Trust badge two",
                                "url": "https://example.com/",
                            },
                        ],
                    },
                },
                {
                    "type": "service_cards",
                    "value": {
                        "eyebrow": "Services",
                        "heading": "<p>Browse our <em>services</em></p>",
                        "intro": "Use this section to test card layouts, hover states, and responsive grids.",
                        "view_all_link": "/services/",
                        "view_all_label": "View all services",
                        "layout_style": "default",
                        "cards": [
                            {
                                "icon": "☀️",
                                "image": None,
                                "title": "Solar Installation",
                                "description": "<p>Modern solar installs with clean finishing.</p>",
                                "link_url": "/services/solar-installation/",
                                "link_label": "Learn more",
                            },
                            {
                                "icon": "🏠",
                                "image": None,
                                "title": "Roofing",
                                "description": "<p>Durable roofing, designed for UK weather.</p>",
                                "link_url": "/services/roofing/",
                                "link_label": "Learn more",
                            },
                            {
                                "icon": "🔋",
                                "image": None,
                                "title": "Battery Storage",
                                "description": "<p>Store energy and improve self-consumption.</p>",
                                "link_url": "/showroom/",
                                "link_label": "See demo",
                            },
                        ],
                    },
                },
                {
                    "type": "testimonials",
                    "value": {
                        "eyebrow": "Client stories",
                        "heading": "<p>People <em>love</em> this</p>",
                        "testimonials": [
                            {
                                "quote": "Everything looked great across mobile and desktop — perfect for our brand.",
                                "author_name": "Alex Taylor",
                                "company": "Taylor & Sons",
                                "photo": None,
                                "rating": 5,
                            },
                            {
                                "quote": "The design tokens made it easy to adjust colours and typography site-wide.",
                                "author_name": "Sam Patel",
                                "company": "Patel Renovations",
                                "photo": None,
                                "rating": 5,
                            },
                            {
                                "quote": "Fast, clean, and consistent. Exactly what we need for client rollouts.",
                                "author_name": "Jamie Kim",
                                "company": "Kim Home Improvements",
                                "photo": None,
                                "rating": 5,
                            },
                        ],
                    },
                },
                {
                    "type": "gallery",
                    "value": {
                        "eyebrow": "Gallery",
                        "heading": "<p>Theme <em>imagery</em></p>",
                        "intro": "Use this gallery to check image ratios, captions, and grid behaviour.",
                        "images": [
                            {
                                "image": images.gallery_one_id,
                                "alt_text": "Gallery image one",
                                "caption": "Clean layout",
                            },
                            {
                                "image": images.gallery_two_id,
                                "alt_text": "Gallery image two",
                                "caption": "Responsive grid",
                            },
                            {
                                "image": images.gallery_three_id,
                                "alt_text": "Gallery image three",
                                "caption": "Typography scale",
                            },
                        ],
                    },
                },
                {
                    "type": "stats",
                    "value": {
                        "eyebrow": "By the numbers",
                        "intro": "Stats are a great place to validate spacing, type rhythm, and colour contrast.",
                        "items": [
                            {
                                "prefix": "",
                                "value": "500",
                                "suffix": "+",
                                "label": "Projects",
                            },
                            {
                                "prefix": "",
                                "value": "15",
                                "suffix": "yrs",
                                "label": "Experience",
                            },
                            {
                                "prefix": "",
                                "value": "98",
                                "suffix": "%",
                                "label": "Satisfaction",
                            },
                        ],
                    },
                },
            ]
        )

    def _build_showroom_stream(
        self,
        *,
        images: _Images,
        services_index: ServiceIndexPage,
        service_one: ServicePage,
        contact_page: StandardPage,
    ) -> Any:
        stream_block = PageStreamBlock()
        return stream_block.to_python(
            [
                {
                    "type": "hero_gradient",
                    "value": {
                        "headline": "<p>Block <em>Showroom</em></p>",
                        "subheadline": "A curated tour: every block type, spread across pages.",
                        "ctas": [
                            {
                                "label": "Services",
                                "url": "/services/",
                                "style": "primary",
                                "open_in_new_tab": False,
                            }
                        ],
                        "status": "Theme QA",
                        "gradient_style": "primary",
                    },
                },
                {
                    "type": "features",
                    "value": {
                        "heading": "Features",
                        "intro": "Check icons, alignment, and spacing across viewports.",
                        "features": [
                            {
                                "icon": "⚡",
                                "title": "Fast",
                                "description": "Token-driven styling and reusable patterns.",
                            },
                            {
                                "icon": "🧱",
                                "title": "Composable",
                                "description": "StreamField blocks let editors build pages without dev.",
                            },
                            {
                                "icon": "🔍",
                                "title": "SEO-ready",
                                "description": "Sitemap, robots.txt, meta tags, and schema helpers.",
                            },
                        ],
                    },
                },
                {
                    "type": "comparison",
                    "value": {
                        "accent_text": "Before / After",
                        "title": "Comparison slider",
                        "description": "Validate handle styling, overlays, and image cropping.",
                        "image_before": images.comparison_before_id,
                        "image_after": images.comparison_after_id,
                    },
                },
                {
                    "type": "manifesto",
                    "value": {
                        "eyebrow": "Manifesto",
                        "heading": "<p>Build with <em>consistency</em></p>",
                        "body": "<p>This section helps validate prose styling, link colours, and list rendering.</p>"
                        "<ul><li>Token-first</li><li>Accessible defaults</li><li>Theme override friendly</li></ul>",
                        "quote": "Good design is what you don’t notice — it just works.",
                        "cta_label": "See services",
                        "cta_url": "/services/",
                    },
                },
                {
                    "type": "portfolio",
                    "value": {
                        "eyebrow": "Portfolio",
                        "heading": "<p>Featured <em>work</em></p>",
                        "intro": "Check alternating layout offsets and typography scale.",
                        "view_all_label": "View all",
                        "view_all_link": "/",
                        "items": [
                            {
                                "image": images.portfolio_one_id,
                                "alt_text": "Portfolio project one",
                                "title": "Solar + battery upgrade",
                                "location": "Kensington, London",
                                "services": "Solar • Battery",
                                "constraint": "Tight access",
                                "material": "Slate roof",
                                "outcome": "Lower bills",
                                "link_url": "/services/solar-installation/",
                            },
                            {
                                "image": images.portfolio_two_id,
                                "alt_text": "Portfolio project two",
                                "title": "Full roof replacement",
                                "location": "Richmond, London",
                                "services": "Roofing",
                                "constraint": "Winter schedule",
                                "material": "Clay tiles",
                                "outcome": "Weatherproof",
                                "link_url": "/services/",
                            },
                        ],
                    },
                },
                {
                    "type": "trust_strip",
                    "value": {
                        "items": [
                            {"text": "Fully insured"},
                            {"text": "5★ reviews"},
                            {"text": "Local team"},
                            {"text": "Transparent pricing"},
                        ]
                    },
                },
                {
                    "type": "editorial_header",
                    "value": {
                        "align": "center",
                        "eyebrow": "Editorial",
                        "heading": "<p>Content <em>blocks</em></p>",
                    },
                },
                {
                    "type": "content",
                    "value": {
                        "align": "left",
                        "body": "<h2>Rich text content</h2><p>This is a general-purpose content block.</p>"
                        "<p>Use it to validate headings, lists, links, and spacing.</p>",
                    },
                },
                {
                    "type": "quote",
                    "value": {
                        "quote": "Design systems are what keep themes consistent as they scale.",
                        "author": "SUM Platform",
                        "role": "Core team",
                    },
                },
                {
                    "type": "image_block",
                    "value": {
                        "image": images.image_block_id,
                        "alt_text": "A cinematic placeholder image",
                        "caption": "Full-bleed image block with caption.",
                        "full_width": False,
                    },
                },
                {
                    "type": "buttons",
                    "value": {
                        "alignment": "left",
                        "buttons": [
                            {
                                "label": "Contact",
                                "url": "/contact/",
                                "style": "primary",
                            },
                            {
                                "label": "Services",
                                "url": "/services/",
                                "style": "secondary",
                            },
                        ],
                    },
                },
                {"type": "spacer", "value": {"size": "medium"}},
                {"type": "divider", "value": {"style": "muted"}},
                {
                    "type": "rich_text",
                    "value": "<h2>Simple RichText</h2><p>This block is the plain RichTextBlock in PageStreamBlock.</p>",
                },
                {
                    "type": "hero",
                    "value": {
                        "status_text": "Legacy block",
                        "title": "Legacy <span class='italic-accent'>Hero</span>",
                        "description": "This is kept for compatibility; themes may still style it.",
                        "primary_cta": {
                            "label": "Explore services",
                            "link": "/services/",
                            "page": None,
                            "style": "btn-primary",
                        },
                        "secondary_cta": {
                            "label": "Contact",
                            "link": "/contact/",
                            "page": None,
                            "style": "btn-outline",
                        },
                        "image": images.legacy_hero_id,
                        "float_card_label": "Demo",
                        "float_card_value": "Legacy",
                    },
                },
            ]
        )

    def _build_services_index_intro_stream(self, *, images: _Images) -> Any:
        stream_block = PageStreamBlock()
        return stream_block.to_python(
            [
                {
                    "type": "content",
                    "value": {
                        "align": "center",
                        "body": "<h2>Services Index</h2><p>This page lists child ServicePage items in a grid.</p>",
                    },
                },
                {
                    "type": "process",
                    "value": {
                        "eyebrow": "Process",
                        "heading": "<p>How we <em>work</em></p>",
                        "intro": "<p>Use this to validate timeline styling and list spacing.</p>",
                        "steps": [
                            {
                                "number": 1,
                                "title": "Assess",
                                "description": "<p>We review your needs.</p>",
                            },
                            {
                                "number": 2,
                                "title": "Plan",
                                "description": "<p>We design the approach.</p>",
                            },
                            {
                                "number": 3,
                                "title": "Deliver",
                                "description": "<p>We build and ship.</p>",
                            },
                        ],
                    },
                },
            ]
        )

    def _build_service_page_stream(
        self, *, images: _Images, page: ServicePage, contact_page: StandardPage
    ) -> Any:
        stream_block = PageStreamBlock()
        return stream_block.to_python(
            [
                {
                    "type": "faq",
                    "value": {
                        "eyebrow": "FAQ",
                        "heading": "<p>Service <em>questions</em></p>",
                        "intro": "<p>Accordion + JSON-LD schema validation.</p>",
                        "allow_multiple_open": False,
                        "items": [
                            {
                                "question": "How long does this take?",
                                "answer": "<p>Most installs complete within 1–2 days.</p>",
                            },
                            {
                                "question": "Is there a warranty?",
                                "answer": "<p>Yes — warranties vary by product and scope.</p>",
                            },
                        ],
                    },
                },
                {
                    "type": "quote_request_form",
                    "value": {
                        "eyebrow": "Quote",
                        "heading": "<p>Request a <em>quote</em></p>",
                        "intro": "<p>Use this to validate form layout and success states.</p>",
                        "success_message": "Thanks — we’ll be in touch with next steps.",
                        "submit_label": "Request quote",
                        "show_compact_meta": False,
                    },
                },
                {
                    "type": "contact_form",
                    "value": {
                        "eyebrow": "Enquiries",
                        "heading": "<p>General <em>enquiry</em></p>",
                        "intro": "<p>Prefer a quick message instead?</p>",
                        "success_message": "Thanks — we’ll reply shortly.",
                        "submit_label": "Send enquiry",
                    },
                },
                {
                    "type": "buttons",
                    "value": {
                        "alignment": "center",
                        "buttons": [
                            {
                                "label": "Contact page",
                                "url": "/contact/",
                                "style": "primary",
                            }
                        ],
                    },
                },
            ]
        )

    def _build_contact_stream(self, *, images: _Images) -> Any:
        stream_block = PageStreamBlock()
        return stream_block.to_python(
            [
                {
                    "type": "editorial_header",
                    "value": {
                        "align": "center",
                        "eyebrow": "Contact",
                        "heading": "<p>Get in <em>touch</em></p>",
                    },
                },
                {
                    "type": "content",
                    "value": {
                        "align": "center",
                        "body": "<p>This page exists so navigation can link cleanly to a contact destination.</p>",
                    },
                },
                {
                    "type": "contact_form",
                    "value": {
                        "eyebrow": "Enquiries",
                        "heading": "<p>Send a <em>message</em></p>",
                        "intro": "<p>We’ll respond as soon as possible.</p>",
                        "success_message": "Thanks — we’ll be in touch shortly.",
                        "submit_label": "Send",
                    },
                },
            ]
        )

    # -----------------------------------------------------------------------------
    # Branding + navigation seeding
    # -----------------------------------------------------------------------------

    def _seed_branding(self, *, site: Site, images: _Images) -> None:
        settings = SiteSettings.for_site(site)
        settings.company_name = settings.company_name or "SUM Theme Showroom"
        settings.tagline = settings.tagline or "A seeded site for theme development."
        settings.phone_number = settings.phone_number or "+44 20 7946 0958"
        settings.email = settings.email or "hello@example.com"
        settings.address = settings.address or "1 Showroom Street\nLondon\nSW1A 1AA"

        # Colours + fonts (safe defaults; themes can override visually)
        settings.primary_color = settings.primary_color or "#0ea5e9"
        settings.secondary_color = settings.secondary_color or "#14b8a6"
        settings.accent_color = settings.accent_color or "#f97316"
        settings.background_color = settings.background_color or "#ffffff"
        settings.surface_color = settings.surface_color or "#f8fafc"
        settings.surface_elevated_color = settings.surface_elevated_color or "#ffffff"
        settings.text_color = settings.text_color or "#0f172a"
        settings.text_light_color = settings.text_light_color or "#475569"
        settings.heading_font = settings.heading_font or "Inter"
        settings.body_font = settings.body_font or "Inter"

        # Logos
        settings.header_logo_id = images.brand_logo_id
        settings.footer_logo_id = images.brand_logo_id
        settings.og_default_image_id = images.brand_logo_id
        settings.favicon_id = images.favicon_id

        # Social links (so footer can render icons)
        settings.facebook_url = settings.facebook_url or "https://facebook.com/"
        settings.instagram_url = settings.instagram_url or "https://instagram.com/"
        settings.linkedin_url = settings.linkedin_url or "https://linkedin.com/"
        settings.twitter_url = settings.twitter_url or "https://x.com/"
        settings.youtube_url = settings.youtube_url or "https://youtube.com/"
        settings.tiktok_url = settings.tiktok_url or "https://tiktok.com/"

        settings.save()

    def _seed_navigation(
        self,
        *,
        site: Site,
        home: Page,
        showroom: StandardPage,
        contact: StandardPage,
        services_index: ServiceIndexPage,
        service_one: ServicePage,
        service_two: ServicePage,
    ) -> None:
        header = HeaderNavigation.for_site(site)
        header.show_phone_in_header = True
        header.header_cta_enabled = True
        header.header_cta_text = "Get a Quote"
        header.mobile_cta_enabled = True
        header.mobile_cta_phone_enabled = True
        header.mobile_cta_button_enabled = True
        header.mobile_cta_button_text = "Enquire"

        menu_stream_block = header._meta.get_field("menu_items").stream_block
        header.menu_items = menu_stream_block.to_python(
            [
                {
                    "type": "item",
                    "value": {
                        "label": "Home",
                        "link": {
                            "link_type": "page",
                            "page": home,
                            "link_text": "Home",
                        },
                        "children": [],
                    },
                },
                {
                    "type": "item",
                    "value": {
                        "label": "Showroom",
                        "link": {
                            "link_type": "page",
                            "page": showroom,
                            "link_text": "Showroom",
                        },
                        "children": [],
                    },
                },
                {
                    "type": "item",
                    "value": {
                        "label": "Services",
                        "link": {
                            "link_type": "page",
                            "page": services_index,
                            "link_text": "Services",
                        },
                        "children": [
                            {
                                "label": "Solar Installation",
                                "link": {
                                    "link_type": "page",
                                    "page": service_one,
                                    "link_text": "Solar Installation",
                                },
                                "children": [
                                    {
                                        "label": "FAQ (anchor demo)",
                                        "link": {
                                            "link_type": "anchor",
                                            "anchor": "faq",
                                            "link_text": "FAQ",
                                        },
                                    }
                                ],
                            },
                            {
                                "label": "Roofing",
                                "link": {
                                    "link_type": "page",
                                    "page": service_two,
                                    "link_text": "Roofing",
                                },
                                "children": [],
                            },
                        ],
                    },
                },
                {
                    "type": "item",
                    "value": {
                        "label": "Contact",
                        "link": {
                            "link_type": "page",
                            "page": contact,
                            "link_text": "Contact",
                        },
                        "children": [],
                    },
                },
            ]
        )

        single_link_block = header._meta.get_field("header_cta_link").stream_block
        header.header_cta_link = single_link_block.to_python(
            [
                {
                    "type": "link",
                    "value": {
                        "link_type": "page",
                        "page": contact,
                        "link_text": "Get a quote",
                    },
                }
            ]
        )

        header.mobile_cta_button_link = single_link_block.to_python(
            [
                {
                    "type": "link",
                    "value": {
                        "link_type": "page",
                        "page": contact,
                        "link_text": "Enquire",
                    },
                }
            ]
        )
        header.save()

        footer = FooterNavigation.for_site(site)
        footer.tagline = ""  # demonstrate branding fallback for tagline
        footer.social_facebook = ""  # demonstrate branding fallback
        footer.social_instagram = ""  # demonstrate branding fallback
        footer.social_linkedin = ""  # demonstrate branding fallback
        footer.social_youtube = ""  # demonstrate branding fallback
        footer.social_x = ""  # demonstrate branding fallback
        footer.copyright_text = "© {year} {company_name}. All rights reserved."

        sections_block = footer._meta.get_field("link_sections").stream_block
        footer.link_sections = sections_block.to_python(
            [
                {
                    "type": "section",
                    "value": {
                        "title": "Company",
                        "links": [
                            {
                                "link_type": "page",
                                "page": showroom,
                                "link_text": "Showroom",
                            },
                            {
                                "link_type": "page",
                                "page": contact,
                                "link_text": "Contact",
                            },
                            {
                                "link_type": "email",
                                "email": "hello@example.com",
                                "link_text": "Email",
                            },
                            {
                                "link_type": "phone",
                                "phone": "+44 20 7946 0958",
                                "link_text": "Call",
                            },
                        ],
                    },
                },
                {
                    "type": "section",
                    "value": {
                        "title": "Services",
                        "links": [
                            {
                                "link_type": "page",
                                "page": services_index,
                                "link_text": "All services",
                            },
                            {
                                "link_type": "page",
                                "page": service_one,
                                "link_text": "Solar installation",
                            },
                            {
                                "link_type": "page",
                                "page": service_two,
                                "link_text": "Roofing",
                            },
                            {
                                "link_type": "url",
                                "url": "https://example.com/",
                                "link_text": "External link",
                                "open_in_new_tab": True,
                            },
                        ],
                    },
                },
            ]
        )
        footer.save()

    # -----------------------------------------------------------------------------
    # Utilities
    # -----------------------------------------------------------------------------

    def _slugify(self, text: str) -> str:
        s = text.strip().lower()
        s = re.sub(r"[^\w\s-]", "", s)
        s = re.sub(r"[-\s]+", "-", s)
        return s.strip("-")
