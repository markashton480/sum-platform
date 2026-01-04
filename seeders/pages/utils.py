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
        if timezone.is_aware(value):
            return value
        return _ensure_aware(value)
    if isinstance(value, str):
        try:
            parsed = datetime.fromisoformat(value)
        except ValueError:
            parsed = datetime.strptime(value, "%Y-%m-%d")
        try:
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
        page_defaults = dict(defaults)
        for key, value in page_defaults.items():
            if hasattr(existing, key):
                setattr(existing, key, value)
        publish_page(existing)
        return existing, False

    page_defaults = dict(defaults)
    rename_conflicting_page(parent, slug=slug, expected_class=page_class)

    page = page_class(slug=slug, **page_defaults)
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
        return getattr(value, "pk", value)
    return value


def _ensure_aware(value: datetime) -> datetime:
    if timezone.is_naive(value):
        return timezone.make_aware(value, timezone.get_current_timezone())
    return value


def rename_conflicting_page(
    parent: Page,
    *,
    slug: str,
    expected_class: type[Any],
    ignore_page_id: int | None = None,
) -> None:
    """Rename a conflicting child page to a unique legacy slug."""

    if not hasattr(parent, "get_children"):
        raise SeederPageError("Parent page must provide get_children()")

    conflict = parent.get_children().filter(slug=slug).first()
    if conflict is None:
        return
    if ignore_page_id is not None and conflict.pk == ignore_page_id:
        return

    conflict_page = conflict.specific
    if isinstance(conflict_page, expected_class):
        return

    legacy_slug = _build_legacy_slug(parent, slug, conflict_page.id)
    conflict_page.slug = legacy_slug
    if not str(conflict_page.title).endswith(" (Legacy)"):
        conflict_page.title = f"{conflict_page.title} (Legacy)"
    publish_page(conflict_page)


def _build_legacy_slug(parent: Page, slug: str, page_id: int) -> str:
    base_slug = f"{slug}-legacy-{page_id}"
    if not parent.get_children().filter(slug=base_slug).exists():
        return base_slug
    counter = 1
    candidate = f"{base_slug}-conflict-{counter}"
    while parent.get_children().filter(slug=candidate).exists():
        counter += 1
        candidate = f"{base_slug}-conflict-{counter}"
    return candidate
