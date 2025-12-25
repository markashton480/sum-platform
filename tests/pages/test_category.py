"""
Name: Category Snippet Tests
Path: tests/pages/test_category.py
Purpose: Ensure the Category model behaves as the blog snippet.
Family: Pages.
"""

from __future__ import annotations

import pytest
from django.db import IntegrityError
from sum_core.pages.blog import Category
from wagtail.snippets.models import get_snippet_models

pytestmark = pytest.mark.django_db


def test_category_can_be_created() -> None:
    """Category instances can be persisted with descriptive text."""
    category = Category.objects.create(
        name="News",
        slug="news",
        description="Updates straight from the field.",
    )

    assert Category.objects.filter(slug="news").exists()
    assert str(category) == "News"


def test_category_slug_is_unique() -> None:
    """Attempting to reuse a slug violates constraints."""
    Category.objects.create(name="News", slug="news")

    with pytest.raises(IntegrityError):
        Category.objects.create(name="Also News", slug="news")


def test_category_description_is_optional() -> None:
    """Description field may be left blank."""
    category = Category.objects.create(name="Updates", slug="updates")

    assert category.description == ""


def test_categories_are_ordered_by_name() -> None:
    """Categories are guaranteed to appear alphabetically."""
    names = ["Zulu", "Alpha", "Beta"]

    for name in names:
        slug = f"{name.lower()}-category"
        Category.objects.create(name=name, slug=slug)

    ordered_names = [category.name for category in Category.objects.all()]

    assert ordered_names == sorted(names)


def test_category_is_registered_as_snippet() -> None:
    """Category is exposed in the Wagtail Snippet registry with the right options."""
    models = get_snippet_models()

    assert Category in models
    viewset = Category.snippet_viewset
    assert viewset is not None
    assert viewset.list_display == ["name", "slug"]
    assert viewset.search_fields == ["name", "description"]
