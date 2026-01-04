"""Legal page seeder."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from sum_core.pages.legal import LegalPage
from sum_core.pages.standard import StandardPage

from seeders.base import BaseSeeder, SeederRegistry
from seeders.exceptions import SeederContentError
from seeders.pages.utils import (
    get_or_create_child_page,
    parse_date,
    resolve_streamfield_images,
)


@SeederRegistry.register("legal")
class LegalPageSeeder(BaseSeeder):
    """Seed legal pages (terms, privacy, accessibility) from YAML content."""

    def __init__(self, *, home_page: Any, images: Mapping[str, Any]) -> None:
        self.home_page = home_page
        self.images = images
        self.terms_slug = "terms"
        self.privacy_slug = "privacy"
        self.accessibility_slug = "accessibility"

    def seed(self, content: dict[str, Any], clear: bool = False) -> None:
        if not isinstance(content, dict):
            raise SeederContentError("Legal page content must be a mapping")

        self.terms_slug = content.get("slug", self.terms_slug)
        privacy_content = content.get("privacy") or {}
        accessibility_content = content.get("accessibility") or {}

        if isinstance(privacy_content, dict):
            self.privacy_slug = privacy_content.get("slug", self.privacy_slug)
        if isinstance(accessibility_content, dict):
            self.accessibility_slug = accessibility_content.get(
                "slug", self.accessibility_slug
            )

        if clear:
            self.clear()

        sections = resolve_streamfield_images(content.get("sections", []), self.images)
        defaults: dict[str, Any] = {
            "title": content.get("title", "Terms"),
            "seo_title": content.get("seo_title", ""),
            "search_description": content.get("search_description", ""),
            "show_in_menus": content.get("show_in_menus", False),
            "last_updated": parse_date(
                content.get("last_updated"), field="last_updated"
            ),
            "sections": sections,
        }

        get_or_create_child_page(
            self.home_page,
            page_class=LegalPage,
            slug=self.terms_slug,
            defaults=defaults,
        )

        if isinstance(privacy_content, dict) and privacy_content:
            privacy_body = resolve_streamfield_images(
                privacy_content.get("body", []), self.images
            )
            privacy_defaults: dict[str, Any] = {
                "title": privacy_content.get("title", "Privacy Policy"),
                "seo_title": privacy_content.get("seo_title", ""),
                "search_description": privacy_content.get("search_description", ""),
                "show_in_menus": privacy_content.get("show_in_menus", False),
                "body": privacy_body,
            }
            get_or_create_child_page(
                self.home_page,
                page_class=StandardPage,
                slug=self.privacy_slug,
                defaults=privacy_defaults,
            )

        if isinstance(accessibility_content, dict) and accessibility_content:
            accessibility_body = resolve_streamfield_images(
                accessibility_content.get("body", []), self.images
            )
            accessibility_defaults: dict[str, Any] = {
                "title": accessibility_content.get("title", "Accessibility"),
                "seo_title": accessibility_content.get("seo_title", ""),
                "search_description": accessibility_content.get(
                    "search_description", ""
                ),
                "show_in_menus": accessibility_content.get("show_in_menus", False),
                "body": accessibility_body,
            }
            get_or_create_child_page(
                self.home_page,
                page_class=StandardPage,
                slug=self.accessibility_slug,
                defaults=accessibility_defaults,
            )

    def clear(self) -> None:
        terms_page = (
            LegalPage.objects.child_of(self.home_page)
            .filter(slug=self.terms_slug)
            .first()
        )
        if terms_page is not None:
            terms_page.delete()

        for slug in (self.privacy_slug, self.accessibility_slug):
            page = (
                StandardPage.objects.child_of(self.home_page).filter(slug=slug).first()
            )
            if page is not None:
                page.delete()
