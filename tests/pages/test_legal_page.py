"""
Name: Legal Page Tests
Path: tests/pages/test_legal_page.py
Purpose: Validate the LegalPage model and section-based TOC structure.
Family: Part of the page-level test suite exercising the page types.
Dependencies: Wagtail Page models, sum_core.pages.LegalPage, sum_core.blocks.
"""

from __future__ import annotations

import datetime as dt

import pytest
from django.db import models
from sum_core.blocks import LegalSectionBlock
from sum_core.pages import LegalPage
from wagtail.fields import StreamField
from wagtail.models import Page

pytestmark = pytest.mark.django_db


def test_legal_page_is_registered_as_page_type() -> None:
    """LegalPage is registered as a Wagtail page type."""
    assert issubclass(LegalPage, Page)


def test_legal_page_has_last_updated_field() -> None:
    """LegalPage has a last_updated date field."""
    last_updated_field = LegalPage._meta.get_field("last_updated")
    assert isinstance(last_updated_field, models.DateField)


def test_legal_page_has_sections_stream_field() -> None:
    """LegalPage has a sections StreamField with LegalSectionBlock."""
    sections_field = LegalPage._meta.get_field("sections")
    assert isinstance(sections_field, StreamField)
    assert "section" in sections_field.stream_block.child_blocks
    assert isinstance(
        sections_field.stream_block.child_blocks["section"], LegalSectionBlock
    )


def test_legal_page_can_be_created_with_sections() -> None:
    """LegalPage can be created with section data."""
    root = Page.get_first_root_node()
    page = LegalPage(
        title="Terms",
        slug="terms",
        last_updated=dt.date(2025, 10, 1),
        sections=[
            (
                "section",
                {
                    "anchor": "scope",
                    "heading": "Scope of Works",
                    "body": "<p>Scope details.</p>",
                },
            )
        ],
    )
    root.add_child(instance=page)

    retrieved = LegalPage.objects.get(slug="terms")
    assert retrieved.last_updated == dt.date(2025, 10, 1)
    assert len(list(retrieved.sections)) == 1


def test_legal_page_template_path() -> None:
    """LegalPage uses the theme template path."""
    assert LegalPage.template == "theme/legal_page.html"


def test_legal_page_has_hero_block() -> None:
    """LegalPage should render with hero-compatible layout."""
    page = LegalPage(title="Legal", slug="legal")
    assert page.has_hero_block is True


def test_legal_page_has_no_subpages() -> None:
    """LegalPage has no allowed subpage types."""
    assert LegalPage.subpage_types == []


def test_legal_section_block_anchor_validation() -> None:
    """LegalSectionBlock anchor field validates URL-safe format."""
    from django.core.exceptions import ValidationError

    # Get the anchor field directly from the block
    block = LegalSectionBlock()
    anchor_field = block.child_blocks["anchor"]

    # Valid anchors - should clean without error
    valid_anchors = ["scope", "data-collection", "section1", "a"]
    for anchor in valid_anchors:
        cleaned = anchor_field.clean(anchor)
        assert cleaned == anchor

    # Invalid anchors should raise validation error
    invalid_anchors = [
        "123-starts-with-number",
        "Capital",
        "has spaces",
        "special!chars",
        "-starts-with-hyphen",
    ]
    for anchor in invalid_anchors:
        with pytest.raises(ValidationError):
            anchor_field.clean(anchor)
