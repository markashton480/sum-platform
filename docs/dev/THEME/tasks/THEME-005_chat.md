# Wagtail theme showroom seeding command
_Exported on 12/20/2025 at 19:39:19 GMT from Cursor (2.2.20)_

---

**User**

You're a senior Django & Wagtail engineer. We're working in this Wagtail project (@docs/dev/AGENT-ORIENTATION.md / @AGENTS.md ) and I need your help! I need a management command that will: create a homepage and set it as the default, create a homepage, standardpage, and servicespage and populate them with blocks. All of the blocks available need to be shown across the pages (not all on one page, but a demo/showcase sort of situation) and then appropriate navigation in the header, footer etc. 

Context: it's to help me set up a showroom for each theme I make for the "Sum Platform" so I can sum init test-project --theme theme_xx and manage.py seed_showroom.

We have tonnes of documentation: @docs/dev/WIRING-INVENTORY.md , @docs/dev/blocks-reference.md @docs/dev/page-types-reference.md @docs/dev/navigation-tags-reference.md @docs/dev/NAV/navigation.md which should help you identify what/show is available. 

The command should be runnable for every client project, so presumably it'll need to go into the boilerplate dir. 

---

**Cursor**

Got it. I’m going to (a) inspect the existing page models + StreamField block definitions so we seed the **real** shapes, (b) find how navigation/branding settings are stored and expected to be wired, then (c) add a **`seed_showroom` management command** (likely in `core/sum_core` so *every* client that installs SUM Core gets it), which creates a HomePage + StandardPage + ServicesPage and spreads **all available blocks** across them, plus header/footer/sticky CTA settings.

Nice—`HomePage` is clearly **client-owned** (it exists in boilerplate + generated client templates), while `StandardPage` and a core `ServicesPage` live in `core/sum_core/pages/`. Next I’ll read those models + the block definitions so the seeded StreamField data matches the real required fields.

Aha: SUM Core already ships **ServiceIndexPage + ServicePage** (so “ServicesPage” in your request maps cleanly), and the boilerplate `HomePage` uses the same `PageStreamBlock`. Next I’ll inspect the block classes to build valid StreamField JSON (including image/link sub-block shapes) so the seed command never breaks on required fields.

Cool—`PageStreamBlock` is the authoritative list of **every block we must showcase**, including “legacy” blocks like `hero` and simple `rich_text`. Next I’ll inspect the remaining block modules (services/testimonials/gallery/trust/process/faq/forms) so we can generate valid demo values (esp. images + nested list structs) in the management command.

Plan is holding: we now have the full canonical block list + each block’s required fields, including the tricky nested list structures and image requirements. Next I’ll inspect the navigation + branding settings models/services so the command can seed header/footer/sticky CTA in the same way templates expect (including effective override rules + caching keys).

Nice: you already have a `populate_demo_content` command in the boilerplate, but it’s Faker-driven and skips images/nav. Next I’ll add a new deterministic `seed_showroom` command alongside it (in both the repo `boilerplate/` and the packaged `cli/sum_cli/boilerplate/`) so `sum init … && python manage.py seed_showroom` works everywhere.

```python
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
            self._clear_showroom(site=site, slugs=slugs, home_page_model=home_page_model)

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

    def _clear_showroom(self, *, site: Site, slugs: _ShowroomSlugs, home_page_model: Any) -> None:
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

            home = home_page_model(title="Theme Showroom", slug=slug, intro="", body=None)
            root.add_child(instance=home)
            home.save_revision().publish()

        # Point default site root at the HomePage (homepage URL becomes "/")
        if site.root_page_id != home.id:
            site.root_page = home
            site.site_name = site.site_name or "Showroom"
            site.save()
            Site.clear_site_root_paths_cache()
        return home

    def _get_or_create_standard_page(self, *, parent: Page, title: str, slug: str) -> StandardPage:
        existing = parent.get_children().type(StandardPage).filter(slug=slug).first()
        if existing:
            return existing.specific

        page = StandardPage(title=title, slug=slug, body=None)
        parent.add_child(instance=page)
        return page

    def _get_or_create_services_index(self, *, parent: Page, title: str, slug: str) -> ServiceIndexPage:
        existing = parent.get_children().type(ServiceIndexPage).filter(slug=slug).first()
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

    def _get_or_create_image(self, title: str, size: tuple[int, int], color_hex: str) -> Any:
        from wagtail.images import get_image_model
        from wagtail.models import Collection

        ImageModel = get_image_model()
        existing = ImageModel.objects.filter(title=title).first()
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

        return ImageModel.objects.create(
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
                                "url": contact_page.url,
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
                            {"prefix": "", "value": "500", "suffix": "+", "label": "Projects"},
                            {"prefix": "", "value": "15", "suffix": "yrs", "label": "Experience"},
                            {"prefix": "", "value": "98", "suffix": "%", "label": "Satisfaction"},
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
                                "url": services_index.url,
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
                        "cta_url": services_index.url,
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
                                "link_url": service_one.url,
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
                            {"label": "Contact", "url": contact_page.url, "style": "primary"},
                            {"label": "Services", "url": services_index.url, "style": "secondary"},
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
                            "link": services_index.url,
                            "page": None,
                            "style": "btn-primary",
                        },
                        "secondary_cta": {
                            "label": "Contact",
                            "link": contact_page.url,
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
                            {"number": 1, "title": "Assess", "description": "<p>We review your needs.</p>"},
                            {"number": 2, "title": "Plan", "description": "<p>We design the approach.</p>"},
                            {"number": 3, "title": "Deliver", "description": "<p>We build and ship.</p>"},
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
                            {"label": "Contact page", "url": contact_page.url, "style": "primary"}
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
                        "link": {"link_type": "page", "page": home, "link_text": "Home"},
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
                    "value": {"link_type": "page", "page": contact, "link_text": "Get a quote"},
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
                            {"link_type": "page", "page": contact, "link_text": "Contact"},
                            {"link_type": "email", "email": "hello@example.com", "link_text": "Email"},
                            {"link_type": "phone", "phone": "+44 20 7946 0958", "link_text": "Call"},
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
                            {"link_type": "page", "page": service_two, "link_text": "Roofing"},
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


```

```python
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
            self._clear_showroom(site=site, slugs=slugs, home_page_model=home_page_model)

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

    def _clear_showroom(self, *, site: Site, slugs: _ShowroomSlugs, home_page_model: Any) -> None:
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

            home = home_page_model(title="Theme Showroom", slug=slug, intro="", body=None)
            root.add_child(instance=home)
            home.save_revision().publish()

        # Point default site root at the HomePage (homepage URL becomes "/")
        if site.root_page_id != home.id:
            site.root_page = home
            site.site_name = site.site_name or "Showroom"
            site.save()
            Site.clear_site_root_paths_cache()
        return home

    def _get_or_create_standard_page(self, *, parent: Page, title: str, slug: str) -> StandardPage:
        existing = parent.get_children().type(StandardPage).filter(slug=slug).first()
        if existing:
            return existing.specific

        page = StandardPage(title=title, slug=slug, body=None)
        parent.add_child(instance=page)
        return page

    def _get_or_create_services_index(self, *, parent: Page, title: str, slug: str) -> ServiceIndexPage:
        existing = parent.get_children().type(ServiceIndexPage).filter(slug=slug).first()
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

    def _get_or_create_image(self, title: str, size: tuple[int, int], color_hex: str) -> Any:
        from wagtail.images import get_image_model
        from wagtail.models import Collection

        ImageModel = get_image_model()
        existing = ImageModel.objects.filter(title=title).first()
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

        return ImageModel.objects.create(
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
                                "url": contact_page.url,
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
                            {"prefix": "", "value": "500", "suffix": "+", "label": "Projects"},
                            {"prefix": "", "value": "15", "suffix": "yrs", "label": "Experience"},
                            {"prefix": "", "value": "98", "suffix": "%", "label": "Satisfaction"},
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
                                "url": services_index.url,
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
                        "cta_url": services_index.url,
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
                                "link_url": service_one.url,
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
                            {"label": "Contact", "url": contact_page.url, "style": "primary"},
                            {"label": "Services", "url": services_index.url, "style": "secondary"},
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
                            "link": services_index.url,
                            "page": None,
                            "style": "btn-primary",
                        },
                        "secondary_cta": {
                            "label": "Contact",
                            "link": contact_page.url,
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
                            {"number": 1, "title": "Assess", "description": "<p>We review your needs.</p>"},
                            {"number": 2, "title": "Plan", "description": "<p>We design the approach.</p>"},
                            {"number": 3, "title": "Deliver", "description": "<p>We build and ship.</p>"},
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
                            {"label": "Contact page", "url": contact_page.url, "style": "primary"}
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
                        "link": {"link_type": "page", "page": home, "link_text": "Home"},
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
                    "value": {"link_type": "page", "page": contact, "link_text": "Get a quote"},
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
                            {"link_type": "page", "page": contact, "link_text": "Contact"},
                            {"link_type": "email", "email": "hello@example.com", "link_text": "Email"},
                            {"link_type": "phone", "phone": "+44 20 7946 0958", "link_text": "Call"},
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
                            {"link_type": "page", "page": service_two, "link_text": "Roofing"},
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


```

Now that the command exists in both the repo boilerplate and the packaged CLI boilerplate, next I’ll sanity-check for style/type issues (lints) and do a quick smoke run in this repo’s test harness to ensure the command imports cleanly and builds valid StreamField/nav shapes.

```python
"""
Name: CLI Theme Init Tests
Path: cli/tests/test_theme_init.py
Purpose: Integration tests for sum init --theme functionality
Family: sum_cli tests
Dependencies: sum_cli
"""

from __future__ import annotations

import json
import shutil
import time
from pathlib import Path

from sum_cli.commands.init import run_init


def test_init_with_theme_creates_theme_config(monkeypatch) -> None:
    """Test that sum init --theme creates .sum/theme.json provenance file."""
    repo_root = Path(__file__).resolve().parents[2]

    unique_suffix = int(time.time() * 1000) % 100000
    project_name = f"theme-test-{unique_suffix}"

    monkeypatch.chdir(repo_root)
    project_root = repo_root / "clients" / project_name

    try:
        code = run_init(project_name, theme_slug="theme_a")
        assert code == 0

        # Check .sum/theme.json was created
        theme_file = project_root / ".sum" / "theme.json"
        assert theme_file.exists()

        # Validate provenance content
        with theme_file.open("r") as f:
            config = json.load(f)

        assert config["theme"] == "theme_a"
        assert "original_version" in config, "Provenance must include original_version"
        assert config["original_version"] == "1.0.0"
        assert "locked_at" in config
    finally:
        if project_root.exists():
            shutil.rmtree(project_root)


def test_init_copies_theme_to_active_directory(monkeypatch) -> None:
    """Test that sum init --theme copies theme to theme/active/ directory."""
    repo_root = Path(__file__).resolve().parents[2]

    unique_suffix = int(time.time() * 1000) % 100000
    project_name = f"theme-copy-{unique_suffix}"

    monkeypatch.chdir(repo_root)
    project_root = repo_root / "clients" / project_name

    try:
        code = run_init(project_name, theme_slug="theme_a")
        assert code == 0

        # Check theme/active/ directory exists
        theme_active_dir = project_root / "theme" / "active"
        assert theme_active_dir.exists(), "theme/active/ should exist"
        assert theme_active_dir.is_dir(), "theme/active/ should be a directory"

        # Check theme.json was copied
        theme_manifest = theme_active_dir / "theme.json"
        assert theme_manifest.exists(), "theme.json should be copied"

        # Check templates were copied
        templates_dir = theme_active_dir / "templates"
        assert templates_dir.exists(), "templates/ should be copied"
        assert (templates_dir / "theme" / "base.html").exists()

        # Check static files were copied
        static_dir = theme_active_dir / "static"
        assert static_dir.exists(), "static/ should be copied"
        compiled_css = static_dir / "theme_a" / "css" / "main.css"
        assert compiled_css.exists(), "compiled theme CSS must be present"

        # Compiled output should be non-trivial and not reference legacy core CSS
        assert compiled_css.stat().st_size > 5 * 1024
        css_text = compiled_css.read_text(encoding="utf-8", errors="ignore")
        assert "/static/sum_core/css/main.css" not in css_text

        # Toolchain files should be shipped for maintainers (no runtime Node required)
        assert (theme_active_dir / "tailwind" / "tailwind.config.js").exists()
        assert (theme_active_dir / "tailwind" / "postcss.config.js").exists()
        assert (theme_active_dir / "tailwind" / "package.json").exists()
        assert (theme_active_dir / "tailwind" / "npm-shrinkwrap.json").exists()
        assert (static_dir / "theme_a" / "css" / "input.css").exists()

        # init must not copy node_modules into the client project
        assert not (theme_active_dir / "node_modules").exists()
    finally:
        if project_root.exists():
            shutil.rmtree(project_root)


def test_init_with_invalid_theme_fails(monkeypatch, capsys) -> None:
    """Test that sum init --theme fails gracefully with invalid theme."""
    repo_root = Path(__file__).resolve().parents[2]

    unique_suffix = int(time.time() * 1000) % 100000
    project_name = f"invalid-theme-{unique_suffix}"

    monkeypatch.chdir(repo_root)
    project_root = repo_root / "clients" / project_name

    try:
        code = run_init(project_name, theme_slug="nonexistent_theme")
        captured = capsys.readouterr()

        # Should fail
        assert code == 1

        # Should mention the invalid theme
        assert "nonexistent_theme" in captured.out or "does not exist" in captured.out

        # Project should not have been created or should be incomplete
        # (depending on when validation happens)
    finally:
        if project_root.exists():
            shutil.rmtree(project_root)


def test_init_default_theme_is_theme_a(monkeypatch) -> None:
    """Test that sum init without --theme uses theme_a by default."""
    repo_root = Path(__file__).resolve().parents[2]

    unique_suffix = int(time.time() * 1000) % 100000
    project_name = f"default-theme-{unique_suffix}"

    monkeypatch.chdir(repo_root)
    project_root = repo_root / "clients" / project_name

    try:
        # Call without theme_slug - should use default
        code = run_init(project_name)
        assert code == 0

        # Check theme file has theme_a
        theme_file = project_root / ".sum" / "theme.json"
        assert theme_file.exists()

        with theme_file.open("r") as f:
            config = json.load(f)

        assert config["theme"] == "theme_a"

        # Also verify theme was actually copied
        assert (project_root / "theme" / "active" / "theme.json").exists()
    finally:
        if project_root.exists():
            shutil.rmtree(project_root)


def test_init_includes_seed_showroom_command(monkeypatch) -> None:
    """Generated client projects should include the seed_showroom management command."""
    repo_root = Path(__file__).resolve().parents[2]

    unique_suffix = int(time.time() * 1000) % 100000
    project_name = f"seed-showroom-{unique_suffix}"

    monkeypatch.chdir(repo_root)
    project_root = repo_root / "clients" / project_name

    try:
        code = run_init(project_name, theme_slug="theme_a")
        assert code == 0

        cmd = (
            project_root
            / "home"
            / "management"
            / "commands"
            / "seed_showroom.py"
        )
        assert cmd.exists(), "seed_showroom command should be present in the generated project"
    finally:
        if project_root.exists():
            shutil.rmtree(project_root)


def test_init_fails_fast_when_theme_missing_compiled_css(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    """
    Theme exists + manifest is valid, but missing compiled CSS => init should fail
    before scaffolding the client project.
    """
    repo_root = Path(__file__).resolve().parents[2]
    monkeypatch.chdir(repo_root)

    # Create a fake theme registry in a temp directory
    themes_dir = tmp_path / "themes"
    themes_dir.mkdir()

    slug = "theme_b"
    theme_dir = themes_dir / slug
    (theme_dir / "templates" / "theme").mkdir(parents=True)
    (theme_dir / "static" / slug / "css").mkdir(parents=True)

    (theme_dir / "theme.json").write_text(
        json.dumps(
            {
                "slug": slug,
                "name": "Theme B",
                "description": "Test theme for init validation",
                "version": "0.0.1",
            }
        ),
        encoding="utf-8",
    )
    (theme_dir / "templates" / "theme" / "base.html").write_text(
        "<!doctype html><html><body>{% block main %}{% endblock %}</body></html>\n",
        encoding="utf-8",
    )
    # Intentionally omit static/theme_b/css/main.css

    # Override theme discovery for this test to point at our temp registry
    monkeypatch.setenv("SUM_THEME_PATH", str(themes_dir))

    unique_suffix = int(time.time() * 1000) % 100000
    project_name = f"missing-css-{unique_suffix}"
    project_root = repo_root / "clients" / project_name

    try:
        code = run_init(project_name, theme_slug=slug)
        captured = capsys.readouterr()

        assert code == 1
        assert "Missing compiled CSS" in captured.out or "main.css" in captured.out
        assert (
            not project_root.exists()
        ), "init should not scaffold a half-broken client"
    finally:
        if project_root.exists():
            shutil.rmtree(project_root)

```

I’m going to run the CLI test that scaffolds a client and asserts `seed_showroom.py` is included. Then I’ll run a focused pytest subset for navigation/page rendering to ensure the seeded StreamField shapes match what core templates expect.

```python
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
            self._clear_showroom(site=site, slugs=slugs, home_page_model=home_page_model)

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

    def _clear_showroom(self, *, site: Site, slugs: _ShowroomSlugs, home_page_model: Any) -> None:
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

            home = home_page_model(title="Theme Showroom", slug=slug, intro="", body=None)
            root.add_child(instance=home)
            home.save_revision().publish()

        # Point default site root at the HomePage (homepage URL becomes "/")
        if site.root_page_id != home.id:
            site.root_page = home
            site.site_name = site.site_name or "Showroom"
            site.save()
            Site.clear_site_root_paths_cache()
        return home

    def _get_or_create_standard_page(self, *, parent: Page, title: str, slug: str) -> StandardPage:
        existing = parent.get_children().type(StandardPage).filter(slug=slug).first()
        if existing:
            return existing.specific

        page = StandardPage(title=title, slug=slug, body=None)
        parent.add_child(instance=page)
        return page

    def _get_or_create_services_index(self, *, parent: Page, title: str, slug: str) -> ServiceIndexPage:
        existing = parent.get_children().type(ServiceIndexPage).filter(slug=slug).first()
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

    def _get_or_create_image(self, title: str, size: tuple[int, int], color_hex: str) -> Any:
        from wagtail.images import get_image_model
        from wagtail.models import Collection

        ImageModel = get_image_model()
        existing = ImageModel.objects.filter(title=title).first()
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

        return ImageModel.objects.create(
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
                            {"prefix": "", "value": "500", "suffix": "+", "label": "Projects"},
                            {"prefix": "", "value": "15", "suffix": "yrs", "label": "Experience"},
                            {"prefix": "", "value": "98", "suffix": "%", "label": "Satisfaction"},
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
                            {"label": "Contact", "url": "/contact/", "style": "primary"},
                            {"label": "Services", "url": "/services/", "style": "secondary"},
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
                            {"number": 1, "title": "Assess", "description": "<p>We review your needs.</p>"},
                            {"number": 2, "title": "Plan", "description": "<p>We design the approach.</p>"},
                            {"number": 3, "title": "Deliver", "description": "<p>We build and ship.</p>"},
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
                            {"label": "Contact page", "url": "/contact/", "style": "primary"}
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
                        "link": {"link_type": "page", "page": home, "link_text": "Home"},
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
                    "value": {"link_type": "page", "page": contact, "link_text": "Get a quote"},
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
                            {"link_type": "page", "page": contact, "link_text": "Contact"},
                            {"link_type": "email", "email": "hello@example.com", "link_text": "Email"},
                            {"link_type": "phone", "phone": "+44 20 7946 0958", "link_text": "Call"},
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
                            {"link_type": "page", "page": service_two, "link_text": "Roofing"},
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



```

```python
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
            self._clear_showroom(site=site, slugs=slugs, home_page_model=home_page_model)

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

    def _clear_showroom(self, *, site: Site, slugs: _ShowroomSlugs, home_page_model: Any) -> None:
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

            home = home_page_model(title="Theme Showroom", slug=slug, intro="", body=None)
            root.add_child(instance=home)
            home.save_revision().publish()

        # Point default site root at the HomePage (homepage URL becomes "/")
        if site.root_page_id != home.id:
            site.root_page = home
            site.site_name = site.site_name or "Showroom"
            site.save()
            Site.clear_site_root_paths_cache()
        return home

    def _get_or_create_standard_page(self, *, parent: Page, title: str, slug: str) -> StandardPage:
        existing = parent.get_children().type(StandardPage).filter(slug=slug).first()
        if existing:
            return existing.specific

        page = StandardPage(title=title, slug=slug, body=None)
        parent.add_child(instance=page)
        return page

    def _get_or_create_services_index(self, *, parent: Page, title: str, slug: str) -> ServiceIndexPage:
        existing = parent.get_children().type(ServiceIndexPage).filter(slug=slug).first()
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

    def _get_or_create_image(self, title: str, size: tuple[int, int], color_hex: str) -> Any:
        from wagtail.images import get_image_model
        from wagtail.models import Collection

        ImageModel = get_image_model()
        existing = ImageModel.objects.filter(title=title).first()
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

        return ImageModel.objects.create(
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
                            {"prefix": "", "value": "500", "suffix": "+", "label": "Projects"},
                            {"prefix": "", "value": "15", "suffix": "yrs", "label": "Experience"},
                            {"prefix": "", "value": "98", "suffix": "%", "label": "Satisfaction"},
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
                            {"label": "Contact", "url": "/contact/", "style": "primary"},
                            {"label": "Services", "url": "/services/", "style": "secondary"},
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
                            {"number": 1, "title": "Assess", "description": "<p>We review your needs.</p>"},
                            {"number": 2, "title": "Plan", "description": "<p>We design the approach.</p>"},
                            {"number": 3, "title": "Deliver", "description": "<p>We build and ship.</p>"},
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
                            {"label": "Contact page", "url": "/contact/", "style": "primary"}
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
                        "link": {"link_type": "page", "page": home, "link_text": "Home"},
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
                    "value": {"link_type": "page", "page": contact, "link_text": "Get a quote"},
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
                            {"link_type": "page", "page": contact, "link_text": "Contact"},
                            {"link_type": "email", "email": "hello@example.com", "link_text": "Email"},
                            {"link_type": "phone", "phone": "+44 20 7946 0958", "link_text": "Call"},
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
                            {"link_type": "page", "page": service_two, "link_text": "Roofing"},
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



```

### What I built
- **A new management command**: `seed_showroom`
- **Location (so it works for every generated client project)**:
  - `boilerplate/project_name/home/management/commands/seed_showroom.py`
  - `cli/sum_cli/boilerplate/project_name/home/management/commands/seed_showroom.py`

### What the command does
When you run `python manage.py seed_showroom` inside a generated client project, it will:

- **Create or reuse the client-owned `HomePage`** and set it as the **default Wagtail `Site.root_page`** (so `/` is the showroom home).
- Create these pages under the homepage:
  - **`StandardPage`**: `/showroom/`
  - **`StandardPage`**: `/contact/`
  - **`ServiceIndexPage`**: `/services/`
  - **Two `ServicePage` children**: `/services/solar-installation/` and `/services/roofing/`
- **Populate StreamField content** so that **every block in `sum_core.blocks.base.PageStreamBlock` is showcased**, spread across those pages (not all on one page).
- Seed **Branding** (`sum_core.branding.models.SiteSettings`) with reasonable defaults (colors, fonts, company info, social links, logos).
- Seed **Navigation**:
  - `HeaderNavigation` menu items (including a nested submenu + anchor link demo)
  - Header CTA + sticky CTA button
  - `FooterNavigation` link sections
  - Footer social/tagline set blank to demonstrate **branding fallback**
- **Generate placeholder images** in Wagtail’s image library (via Pillow) and wire them into blocks that require images.

### Usage
In a client project (after `sum init …`):

```bash
python manage.py seed_showroom
```

Options:
- `--clear`: remove previously seeded showroom pages by slug and re-seed
- `--hostname`, `--port`: set/update the default `Site`
- `--homepage-model app_label.ModelName`: if your HomePage model isn’t the default autodetected one

### Notes / constraints
- Your “ServicesPage” maps to **`ServiceIndexPage` + `ServicePage`** in core (`core/sum_core/pages/services.py`).
- I used **stable URL paths** (e.g. `"/contact/"`) for blocks that require `URLBlock` values, so it doesn’t depend on `.url` during publishing.

If you want, I can also add a short `docs/dev` note describing the expected showroom page tree + which blocks live on which page, for theme QA consistency.

```shellscript
python manage.py seed_showroom
```

---

**User**

Please can you update @docs/dev/cli.md with a short note about the existance of this, and a more comphrensive "tool documenation" type document in docs/dev/SHOWROOM.md

---

**Cursor**

I’ll keep this tight: add a short mention + link in `docs/dev/cli.md`, then write a new `docs/dev/SHOWROOM.md` that documents `python manage.py seed_showroom` (what it creates, idempotency/--clear, how it picks HomePage model, what pages/blocks/nav/settings it seeds, and how it fits into `sum init` + boilerplate sync).

Got it—next I’ll add a small “Showroom seeding” note under `sum init` (since that’s where people discover it), and then I’ll write `docs/dev/SHOWROOM.md` as the authoritative doc (page tree, what blocks go where, what settings/nav it touches, and safe re-run/clear behaviour).

```markdown
## SUM CLI (v1): `sum init`, `sum check`

This repo ships a minimal **filesystem scaffolding + validation CLI**.
It intentionally does **not** create virtualenvs, install dependencies, initialise git, or touch databases.

### Install (monorepo dev)

From repo root (using the repo virtualenv):

```bash
source .venv/bin/activate
pip install -e ./cli
```

### `sum init <project-name>`

Creates a new client project at `clients/<project-name>/` by copying the boilerplate and applying deterministic renames:

- client directory name uses the provided slug (e.g. `acme-kitchens`)
- Django project package name is normalized for Python imports (hyphens → underscores, e.g. `acme_kitchens`)
- all `project_name` placeholders are replaced
- `.env` is created by copying `.env.example` (no secret generation)

Run from the repo root:

```bash
sum init acme-kitchens
```

### Showroom seeding (`seed_showroom`)

Client projects generated by `sum init` include a Django management command you can run to quickly create a **theme showroom** site tree (pages, blocks, navigation, and branding defaults):

```bash
python manage.py seed_showroom
```

For full documentation, see [`docs/dev/SHOWROOM.md`](./SHOWROOM.md).

### `sum check`

Validates the **current working directory** is a structurally-correct client project.

#### Execution Modes

`sum check` automatically detects its execution context:

**Mode 1: Monorepo dev mode**

When running inside the SUM Platform repository (detected by the presence of `core/` and `boilerplate/` directories with expected markers), the CLI automatically adds the core package to the import path. Output will show:

```
[OK] sum_core import: monorepo mode
```

This allows developers to run `sum check` on scaffolded projects without installing `sum_core` globally.

**Mode 2: Standalone client mode**

When running outside the monorepo (e.g., a client project deployed independently), `sum_core` must be installed via pip. If not installed, the output will show:

```
[FAIL] sum_core import: Install requirements first: pip install -r requirements.txt
```

#### What `sum check` validates

| Check                    | Description                                                  |
| ------------------------ | ------------------------------------------------------------ |
| **Project root**         | `manage.py` exists                                           |
| **Env template**         | `.env.example` exists                                        |
| **Required env vars**    | Keys from `.env.example` are set (via `.env` or environment) |
| **Settings module**      | Inferred from `.env` or `manage.py`, and importable          |
| **Health wiring**        | URLConf includes `sum_core.ops.urls` (string-based check)    |
| **sum_core import**      | `sum_core` package is importable                             |
| **No test_project refs** | No references to `test_project` in project files             |

#### What `sum check` does NOT validate

- Database connectivity or migrations
- Full Django startup / `runserver` success
- Template correctness or static file collection
- Runtime configuration (e.g., email, Celery)
- Whether the health endpoint actually responds

Run from a client project directory:

```bash
cd clients/acme-kitchens
sum check
```

### Boilerplate source resolution

`sum init` uses the canonical repo `/boilerplate/` if present (and valid). If not, it falls back to a boilerplate copy bundled with the CLI package.

You can override the boilerplate path for development:

```bash
SUM_BOILERPLATE_PATH=/path/to/boilerplate sum init acme-kitchens
```

### Boilerplate sync (maintainers)

The CLI bundles a copy of boilerplate for non-monorepo use. To keep it in sync:

```bash
# Sync canonical boilerplate to CLI package
make sync-cli-boilerplate

# Check for drift (CI mode - fails if out of sync)
make check-cli-boilerplate
```

> [!IMPORTANT]
> CI should run `make check-cli-boilerplate` to prevent silent boilerplate drift.

---

## Maintainer Release Notes

When releasing a new version of SUM Platform, follow these steps to keep the CLI and boilerplate in sync.

### When to sync boilerplate

Run `make sync-cli-boilerplate` whenever you modify anything in `/boilerplate/`:

```bash
# After editing boilerplate files
make sync-cli-boilerplate

# Verify sync is clean
make check-cli-boilerplate
```

### Updating `SUM_CORE_GIT_REF`

Before tagging a release, update the boilerplate to pin to the new version:

```bash
make release-set-core-ref REF=v0.1.2
```

This command:

1. Updates `boilerplate/requirements.txt`
2. Syncs CLI boilerplate automatically
3. Verifies drift check passes

### Pre-release checklist

```bash
# Run all release checks
make release-check
```

This runs lint, tests, and drift detection in sequence.

→ See [docs/dev/release-workflow.md](./release-workflow.md) for the full release process.



```

```markdown
# Theme Showroom Seeding (`seed_showroom`)

This repo includes a **client-project management command** that seeds a predictable “showroom” site tree for theme development.

It is designed for this workflow:

- `sum init test-project --theme theme_xx`
- `cd clients/test-project`
- `python manage.py seed_showroom`

The goal is a repeatable content + navigation baseline so you can focus on **theme templates + CSS**, not manual Wagtail setup.

---

## Where it lives

`seed_showroom` is part of **boilerplate** (not `sum_core`), because it depends on the **client-owned `HomePage` model**:

- Canonical boilerplate: `boilerplate/project_name/home/management/commands/seed_showroom.py`
- Packaged CLI boilerplate copy: `cli/sum_cli/boilerplate/project_name/home/management/commands/seed_showroom.py`

Maintainers: after editing canonical boilerplate, sync to the CLI copy:

```bash
make sync-cli-boilerplate
make check-cli-boilerplate
```

---

## Usage

From a generated client project directory:

```bash
python manage.py seed_showroom
```

### Options

- **`--clear`**: delete previously seeded showroom pages (by slug) and recreate them.
- **`--hostname <host>` / `--port <port>`**: update (or set) the default Wagtail `Site` hostname/port.
- **`--homepage-model app_label.ModelName`**: explicitly choose the client `HomePage` model.

Example:

```bash
python manage.py seed_showroom --clear --hostname localhost --port 8000
```

---

## What it creates

### Site root

- **Default Wagtail `Site`**: ensured/updated (`is_default_site=True`)
- **Root page**: set to the client `HomePage` so the showroom home is served at `/`

### Page tree

Under the HomePage, the command creates:

- **`StandardPage`**: `showroom` → `/showroom/`
- **`StandardPage`**: `contact` → `/contact/`
- **`ServiceIndexPage`**: `services` → `/services/`
  - **`ServicePage`**: `solar-installation` → `/services/solar-installation/`
  - **`ServicePage`**: `roofing` → `/services/roofing/`

### Placeholder images

The command generates a set of placeholder images in the Wagtail image library and assigns them to blocks that require images (hero, gallery, portfolio, comparison, trust logos, service featured images, branding logos).

This requires **Pillow** (normally already installed with Wagtail). If Pillow is missing, the command fails fast with an actionable error.

---

## Content strategy: “show all blocks, spread across pages”

The authoritative list of available blocks is `sum_core.blocks.base.PageStreamBlock`. The showroom is designed to include **every block type at least once**, but distributed so no single page is overloaded.

### HomePage (`/`)

HomePage body contains:

- **`hero_image`**
- **`trust_strip_logos`**
- **`service_cards`**
- **`testimonials`**
- **`gallery`**
- **`stats`**

### Showroom page (`/showroom/`)

Showroom body contains:

- **`hero_gradient`**
- **`features`**
- **`comparison`**
- **`manifesto`**
- **`portfolio`**
- **`trust_strip`** (text-only)
- **`editorial_header`**
- **`content`**
- **`quote`**
- **`image_block`**
- **`buttons`**
- **`spacer`**
- **`divider`**
- **`rich_text`** (the plain RichTextBlock)
- **`hero`** (legacy hero block kept for compatibility)

### Services index (`/services/`)

ServiceIndexPage intro contains:

- **`content`**
- **`process`**

### Service pages (`/services/*`)

Each ServicePage body contains:

- **`faq`**
- **`quote_request_form`**
- **`contact_form`**
- **`buttons`**

### Contact page (`/contact/`)

Contact page body contains:

- **`editorial_header`**
- **`content`**
- **`contact_form`**

---

## Navigation + branding seeding

The command seeds the Wagtail settings models used by `sum_core` templates:

### Branding: `sum_core.branding.models.SiteSettings`

Seeds safe defaults for:

- **Business info**: company name, tagline, phone, email, address
- **Theme tokens**: colours + fonts (used by branding CSS tag)
- **Logos**: header/footer/OG + favicon
- **Social URLs**: so footer social icons have data

### Navigation: `sum_core.navigation.models.HeaderNavigation` / `FooterNavigation`

Seeds:

- **Header menu items**: Home, Showroom, Services (with submenu + nested submenu), Contact
- **Header CTA**: enabled + points to Contact
- **Sticky CTA**: enabled, phone enabled, button enabled pointing to Contact
- **Footer sections**: “Company” and “Services”
  - Includes a variety of `UniversalLinkBlock` link types: page, url, email, phone

Note: footer `tagline` and `social_*` are intentionally set blank so the footer demonstrates **effective settings fallback** to Branding (see `sum_core.navigation.services.get_effective_footer_settings`).

---

## Idempotency and safety

### Re-running

Re-running `seed_showroom` is safe:

- It will reuse the first existing HomePage if present (HomePage is a singleton in boilerplate).
- It will create missing pages by slug under the HomePage.
- It will overwrite the seeded pages’ bodies/settings to the showroom baseline.

### Clearing

`--clear` deletes only the showroom pages by slug (and only deletes the showroom HomePage if it’s currently the default site root and has the expected slug).

It does **not** attempt to delete arbitrary user-created content.

---

## Troubleshooting

- **“Could not find a HomePage model”**:
  - Ensure your client `home` app is in `INSTALLED_APPS`
  - Or specify `--homepage-model app_label.HomePage`
- **Pillow missing**:
  - Install `Pillow` (normally included with Wagtail).
  - The command must be able to generate placeholder images because many blocks require images.


```

### Updates made

- **Added a short note + usage snippet for `seed_showroom`** to `docs/dev/cli.md`, with a link to the full doc.
- **Created a new comprehensive documentation page**: `docs/dev/SHOWROOM.md` covering:
  - Where the command lives (boilerplate + CLI boilerplate copy)
  - Usage + options (`--clear`, `--hostname`, `--port`, `--homepage-model`)
  - The exact page tree it creates
  - Which blocks are showcased on which pages (covers all `PageStreamBlock` blocks)
  - Branding + navigation seeding behaviour (including fallback intent)
  - Idempotency/clear safety + troubleshooting

Files:
- `docs/dev/cli.md`
- `docs/dev/SHOWROOM.md`

---

**User**

@bash (201-204) 

---

**Cursor**

I see the Ruff lint: N806 (variable name should be lowercase) for `ImageModel` in both boilerplate copies of `seed_showroom.py`. I’ll rename that local to `image_model` in both files and re-check lints to confirm it’s clean.

```python
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

```

```python
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
from sum_core.blocks import PageStreamBlock
from sum_core.branding.models import SiteSettings
from sum_core.navigation.cache import invalidate_nav_cache
from sum_core.navigation.models import FooterNavigation, HeaderNavigation
from sum_core.pages import ServiceIndexPage, ServicePage, StandardPage
from wagtail.models import Page, Site

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

```

### Fixed the Ruff errors you highlighted

- **Resolved `N806`** (variable should be lowercase) in both boilerplate copies of `seed_showroom.py` by renaming `ImageModel` → `image_model`.

Files fixed:
- `boilerplate/project_name/home/management/commands/seed_showroom.py`
- `cli/sum_cli/boilerplate/project_name/home/management/commands/seed_showroom.py`

Both now lint clean (no remaining lints reported for these files).

