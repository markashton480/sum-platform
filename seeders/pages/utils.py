"""Shared helpers for page seeders."""

from __future__ import annotations

from collections.abc import Mapping, MutableMapping
from datetime import date, datetime
from typing import Any

from django.utils import timezone
from wagtail.models import Page

from seeders.base import create_child_page, publish_page
from seeders.exceptions import SeederContentError, SeederPageError

IMAGE_FIELD_NAMES = {"image", "photo", "logo"}


def resolve_streamfield_images(data: Any, images: Mapping[str, Any]) -> Any:
    """Recursively resolve image key references in StreamField payloads."""

    if isinstance(data, list):
        return [resolve_streamfield_images(item, images) for item in data]
    if isinstance(data, dict):
        resolved: dict[str, Any] = {}
        for key, value in data.items():
            if key in IMAGE_FIELD_NAMES:
                resolved[key] = _resolve_image_value(value, images, field=key)
            else:
                resolved[key] = resolve_streamfield_images(value, images)
        return resolved
    return data


def parse_date(value: Any, *, field: str) -> date | None:
    """Parse an ISO date string into a date object."""

    if value in (None, ""):
        return None
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return date.fromisoformat(value)
        except ValueError as exc:
            raise SeederContentError(f"Invalid date for {field}: {value}") from exc
    raise SeederContentError(f"Invalid date for {field}: {value!r}")


def parse_datetime(value: Any, *, field: str) -> datetime:
    """Parse an ISO date string into a datetime object."""

    if isinstance(value, datetime):
        return _ensure_aware(value)
    if isinstance(value, str):
        try:
            parsed = datetime.strptime(value, "%Y-%m-%d")
            return _ensure_aware(parsed)
        except ValueError as exc:
            raise SeederContentError(f"Invalid datetime for {field}: {value}") from exc
    raise SeederContentError(f"Invalid datetime for {field}: {value!r}")


def get_or_create_child_page[
    PageType
](
    parent: Page,
    *,
    page_class: type[PageType],
    slug: str,
    defaults: MutableMapping[str, Any],
) -> tuple[PageType, bool]:
    """Get or create a child page, resolving slug conflicts."""

    if not hasattr(parent, "get_children"):
        raise SeederPageError("Parent page must provide get_children()")

    existing = page_class.objects.child_of(parent).filter(slug=slug).first()
    if existing is not None:
        for key, value in defaults.items():
            if hasattr(existing, key):
                setattr(existing, key, value)
        publish_page(existing)
        return existing, False

    conflict = parent.get_children().filter(slug=slug).first()
    if conflict is not None and not isinstance(conflict.specific, page_class):
        conflict_page = conflict.specific
        conflict_page.slug = f"{slug}-legacy-{conflict_page.id}"
        conflict_page.title = f"{conflict_page.title} (Legacy)"
        publish_page(conflict_page)

    page = page_class(slug=slug, **defaults)
    return create_child_page(parent, page), True


def _resolve_image_value(value: Any, images: Mapping[str, Any], *, field: str) -> Any:
    if value is None:
        return None
    if isinstance(value, str):
        image = images.get(value)
        if image is None:
            raise SeederContentError(f"Unknown image key for {field}: {value}")
        return getattr(image, "pk", image)
    if hasattr(value, "pk"):
        return getattr(value, "pk")
    return value


def _ensure_aware(value: datetime) -> datetime:
    if timezone.is_naive(value):
        return timezone.make_aware(value, timezone.get_current_timezone())
    return value
