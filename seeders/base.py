"""Base classes and helpers for seeder modules."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable, Iterable
from typing import Any, cast

from django.utils.text import slugify

from .exceptions import (
    SeederNotFoundError,
    SeederPageError,
    SeederRegistrationError,
    SeederSlugError,
)


class BaseSeeder(ABC):
    """Abstract base for all seeders."""

    @abstractmethod
    def seed(self, content: dict[str, Any], clear: bool = False) -> None:
        """Seed content. If clear=True, remove existing first."""

    @abstractmethod
    def clear(self) -> None:
        """Remove seeded content."""


class SeederRegistry:
    """Registry for page seeders."""

    _seeders: dict[str, type[BaseSeeder]] = {}

    @classmethod
    def register(cls, name: str) -> Callable[[type[BaseSeeder]], type[BaseSeeder]]:
        def decorator(seeder_class: type[BaseSeeder]) -> type[BaseSeeder]:
            if name in cls._seeders:
                raise SeederRegistrationError(f"Seeder already registered: {name}")
            cls._seeders[name] = seeder_class
            return seeder_class

        return decorator

    @classmethod
    def get(cls, name: str) -> type[BaseSeeder]:
        try:
            return cls._seeders[name]
        except KeyError as exc:
            raise SeederNotFoundError(f"Seeder not registered: {name}") from exc

    @classmethod
    def all(cls) -> dict[str, type[BaseSeeder]]:
        return dict(cls._seeders)

    @classmethod
    def clear(cls) -> None:
        cls._seeders.clear()


def generate_slug(value: str, fallback: str = "page") -> str:
    """Generate a slug from text, falling back to a default when empty."""

    slug = cast(str, slugify(value))
    if slug:
        return slug
    fallback_slug = cast(str, slugify(fallback))
    if fallback_slug:
        return fallback_slug
    raise SeederSlugError("Unable to generate slug from value or fallback")


def _iter_children(children: Any) -> Iterable[Any]:
    if hasattr(children, "filter"):
        return cast(Iterable[Any], children)
    if isinstance(children, Iterable):
        return children
    raise SeederPageError("Parent children collection is not iterable")


def find_child_by_slug(parent: Any, slug: str) -> Any | None:
    """Return the first child with matching slug, or None."""

    if not hasattr(parent, "get_children"):
        raise SeederPageError("Parent page must provide get_children()")
    children = parent.get_children()
    if hasattr(children, "filter"):
        filtered = children.filter(slug=slug)
        if hasattr(filtered, "first"):
            return filtered.first()
        return next(iter(filtered), None)
    for child in _iter_children(children):
        if getattr(child, "slug", None) == slug:
            return child
    return None


def publish_page(page: Any) -> None:
    """Publish a page if it supports revisions, otherwise save."""

    if hasattr(page, "save_revision"):
        revision = page.save_revision()
        if hasattr(revision, "publish"):
            revision.publish()
            return
    if hasattr(page, "save"):
        page.save()
        return
    raise SeederPageError("Page must implement save or save_revision")


def create_child_page[PageType](parent: Any, page: PageType) -> PageType:
    """Add a child page to a parent and publish it."""

    if not hasattr(parent, "add_child"):
        raise SeederPageError("Parent page must provide add_child(instance=...)")
    parent.add_child(instance=page)
    publish_page(page)
    return page


def get_or_create_page[
    PageType
](
    parent: Any,
    slug: str,
    page_class: Callable[..., PageType],
    **kwargs: Any,
) -> tuple[
    PageType, bool
]:
    """Get or create a child page by slug, updating fields when found."""

    existing = find_child_by_slug(parent, slug=slug)
    if existing is not None:
        for key, value in kwargs.items():
            if hasattr(existing, key):
                setattr(existing, key, value)
        publish_page(existing)
        return existing, False

    page = page_class(slug=slug, **kwargs)
    return create_child_page(parent, page), True
