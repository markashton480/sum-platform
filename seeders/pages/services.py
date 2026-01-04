"""Services page seeder."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from sum_core.pages.standard import StandardPage

from seeders.base import BaseSeeder, SeederRegistry
from seeders.exceptions import SeederContentError
from seeders.pages.utils import get_or_create_child_page, resolve_streamfield_images


@SeederRegistry.register("services")
class ServicesPageSeeder(BaseSeeder):
    """Seed the Services page from YAML content."""

    def __init__(self, *, home_page: Any, images: Mapping[str, Any]) -> None:
        self.home_page = home_page
        self.images = images
        self.page_slug = "services"

    def seed(self, content: dict[str, Any], clear: bool = False) -> None:
        if not isinstance(content, dict):
            raise SeederContentError("Services page content must be a mapping")

        self.page_slug = content.get("slug", self.page_slug)
        if clear:
            self.clear()

        body = resolve_streamfield_images(content.get("body", []), self.images)
        defaults: dict[str, Any] = {
            "title": content.get("title", "Services"),
            "seo_title": content.get("seo_title", ""),
            "search_description": content.get("search_description", ""),
            "show_in_menus": content.get("show_in_menus", False),
            "body": body,
        }

        get_or_create_child_page(
            self.home_page,
            page_class=StandardPage,
            slug=self.page_slug,
            defaults=defaults,
        )

    def clear(self) -> None:
        page = (
            StandardPage.objects.child_of(self.home_page)
            .filter(slug=self.page_slug)
            .first()
        )
        if page is not None:
            page.delete()
