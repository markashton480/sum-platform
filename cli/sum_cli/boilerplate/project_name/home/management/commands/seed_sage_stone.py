"""
Seed the Sage & Stone site root and HomePage.

Creates a HomePage under the Wagtail root and configures a default Site
pointing at it. Supports idempotent re-runs and a scoped --clear reset.
"""

from __future__ import annotations

from typing import Any

from django.core.management.base import BaseCommand, CommandParser
from home.models import HomePage
from wagtail.models import Page, Site


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
        self.stdout.write(f"Site configured: {site.site_name} (root={home_page.slug})")

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

    def _clear_existing_content(self, *, hostname: str, port: int) -> None:
        """
        Remove Sage & Stone content for a fresh seed.

        Scoped to the specific site to avoid data loss in multi-site setups.
        """
        from wagtail.images.models import Image

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
        from sum_core.branding.models import SiteSettings
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
