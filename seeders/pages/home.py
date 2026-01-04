"""Home page seeder."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from django.apps import apps
from wagtail.models import Page

from seeders.base import BaseSeeder, SeederRegistry, publish_page
from seeders.exceptions import SeederContentError, SeederPageError
from seeders.pages.utils import resolve_streamfield_images


@SeederRegistry.register("home")
class HomePageSeeder(BaseSeeder):
    """Seed the HomePage from YAML content."""

    def __init__(self, *, root_page: Page, images: Mapping[str, Any]) -> None:
        self.root_page = root_page
        self.images = images

    def seed(self, content: dict[str, Any], clear: bool = False) -> None:
        if not isinstance(content, dict):
            raise SeederContentError("Home page content must be a mapping")

        slug = content.get("slug", "home")
        if clear:
            self.clear()

        home_model = _get_home_model()
        body = resolve_streamfield_images(content.get("body", []), self.images)
        defaults: dict[str, Any] = {
            "title": content.get("title", "Home"),
            "seo_title": content.get("seo_title", ""),
            "search_description": content.get("search_description", ""),
            "show_in_menus": content.get("show_in_menus", False),
            "body": body,
        }
        intro = content.get("intro")
        if intro is not None:
            defaults["intro"] = intro

        existing = home_model.objects.first()
        if existing is not None:
            conflict = self.root_page.get_children().filter(slug=slug).first()
            if conflict is not None and conflict.pk != existing.pk:
                conflict_page = conflict.specific
                conflict_page.slug = f"{slug}-legacy-{conflict_page.id}"
                conflict_page.title = f"{conflict_page.title} (Legacy)"
                publish_page(conflict_page)
            existing.slug = slug
            for key, value in defaults.items():
                if hasattr(existing, key):
                    setattr(existing, key, value)
            publish_page(existing)
            return

        conflict = self.root_page.get_children().filter(slug=slug).first()
        if conflict is not None and not isinstance(conflict.specific, home_model):
            conflict_page = conflict.specific
            conflict_page.slug = f"{slug}-legacy-{conflict_page.id}"
            conflict_page.title = f"{conflict_page.title} (Legacy)"
            publish_page(conflict_page)

        page = home_model(slug=slug, **defaults)
        self.root_page.add_child(instance=page)
        publish_page(page)

    def clear(self) -> None:
        home_model = _get_home_model()
        existing = home_model.objects.first()
        if existing is None:
            return
        existing.get_descendants(inclusive=True).delete()


def _get_home_model() -> type[Page]:
    try:
        return apps.get_model("home", "HomePage")
    except LookupError as exc:  # pragma: no cover - requires configured apps
        raise SeederPageError("HomePage model could not be resolved") from exc
