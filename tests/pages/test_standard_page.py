"""
Name: Standard Page Tests
Path: tests/pages/test_standard_page.py
Purpose: Validate the StandardPage model and its integration with PageStreamBlock.
Family: Part of the page-level test suite exercising the page types.
Dependencies: Wagtail Site & Page models, sum_core.pages.StandardPage, sum_core.blocks.
"""
from __future__ import annotations

import pytest
from django.template import RequestContext, Template
from django.test import RequestFactory
from sum_core.blocks import PageStreamBlock
from sum_core.pages import StandardPage
from wagtail.fields import StreamField
from wagtail.models import Page, Site

pytestmark = pytest.mark.django_db


def test_standard_page_is_registered_as_page_type() -> None:
    """StandardPage is registered as a Wagtail page type."""
    # Wagtail registers all Page subclasses automatically
    assert issubclass(StandardPage, Page)


def test_standard_page_has_body_stream_field() -> None:
    """StandardPage has a body field that is a StreamField."""
    body_field = StandardPage._meta.get_field("body")
    assert isinstance(body_field, StreamField)


def test_standard_page_body_uses_page_stream_block() -> None:
    """StandardPage body StreamField uses PageStreamBlock."""
    body_field = StandardPage._meta.get_field("body")
    assert isinstance(body_field.stream_block, PageStreamBlock)


def test_standard_page_can_be_created_under_root() -> None:
    """StandardPage can be created under the site root."""
    root = Page.get_first_root_node()
    standard_page = StandardPage(title="Test Standard Page", slug="test-standard-page")
    root.add_child(instance=standard_page)

    assert StandardPage.objects.filter(title="Test Standard Page").exists()


def test_standard_page_can_be_created_with_empty_body() -> None:
    """StandardPage can be created with an empty body StreamField."""
    root = Page.get_first_root_node()
    standard_page = StandardPage(
        title="Empty Standard Page",
        slug="empty-standard-page",
        body=None,
    )
    root.add_child(instance=standard_page)

    retrieved = StandardPage.objects.get(slug="empty-standard-page")
    assert retrieved.title == "Empty Standard Page"


def test_standard_page_can_be_created_with_rich_text_block() -> None:
    """StandardPage can be created with a rich_text block in body."""
    root = Page.get_first_root_node()

    stream_block = PageStreamBlock()
    stream_data = stream_block.to_python(
        [
            {
                "type": "rich_text",
                "value": "<h2>About Us</h2><p>We are a company.</p>",
            }
        ]
    )

    standard_page = StandardPage(
        title="About Page",
        slug="about-page",
        body=stream_data,
    )
    root.add_child(instance=standard_page)

    retrieved = StandardPage.objects.get(slug="about-page")
    assert retrieved.title == "About Page"
    assert len(list(retrieved.body)) == 1


def test_standard_page_can_be_created_with_multiple_blocks() -> None:
    """StandardPage can be created with multiple blocks in body."""
    root = Page.get_first_root_node()

    stream_block = PageStreamBlock()
    stream_data = stream_block.to_python(
        [
            {
                "type": "rich_text",
                "value": "<h2>Section 1</h2><p>Content.</p>",
            },
            {
                "type": "rich_text",
                "value": "<h2>Section 2</h2><p>More content.</p>",
            },
        ]
    )

    standard_page = StandardPage(
        title="Multi Block Page",
        slug="multi-block-page",
        body=stream_data,
    )
    root.add_child(instance=standard_page)

    retrieved = StandardPage.objects.get(slug="multi-block-page")
    assert len(list(retrieved.body)) == 2


def test_standard_page_has_hero_block_returns_false_when_no_body() -> None:
    """has_hero_block returns False when body is empty."""
    root = Page.get_first_root_node()
    standard_page = StandardPage(title="No Hero Page", slug="no-hero-page")
    root.add_child(instance=standard_page)

    assert standard_page.has_hero_block is False


def test_standard_page_has_hero_block_returns_false_for_non_hero_blocks() -> None:
    """has_hero_block returns False when body contains no hero blocks."""
    root = Page.get_first_root_node()

    stream_block = PageStreamBlock()
    stream_data = stream_block.to_python(
        [{"type": "rich_text", "value": "<p>Content.</p>"}]
    )

    standard_page = StandardPage(
        title="Content Only Page",
        slug="content-only-page",
        body=stream_data,
    )
    root.add_child(instance=standard_page)

    assert standard_page.has_hero_block is False


def test_standard_page_has_hero_block_returns_true_for_hero_image() -> None:
    """has_hero_block returns True when body contains hero_image block."""
    from wagtail.images.models import Image
    from wagtail.images.tests.utils import get_test_image_file

    root = Page.get_first_root_node()
    image = Image.objects.create(title="Hero Image", file=get_test_image_file())

    stream_block = PageStreamBlock()
    stream_data = stream_block.to_python(
        [
            {
                "type": "hero_image",
                "value": {
                    "headline": "<p>Welcome</p>",
                    "subheadline": "",
                    "ctas": [],
                    "status": "",
                    "image": image.pk,
                    "image_alt": "Hero background",
                    "overlay_opacity": "medium",
                    "floating_card_label": "",
                    "floating_card_value": "",
                },
            }
        ]
    )

    standard_page = StandardPage(
        title="Hero Page",
        slug="hero-page",
        body=stream_data,
    )
    root.add_child(instance=standard_page)

    assert standard_page.has_hero_block is True


def test_standard_page_has_hero_block_returns_true_for_hero_gradient() -> None:
    """has_hero_block returns True when body contains hero_gradient block."""
    root = Page.get_first_root_node()

    stream_block = PageStreamBlock()
    stream_data = stream_block.to_python(
        [
            {
                "type": "hero_gradient",
                "value": {
                    "headline": "<p>Welcome</p>",
                    "subheadline": "",
                    "ctas": [],
                    "status": "",
                    "gradient_style": "primary",
                },
            }
        ]
    )

    standard_page = StandardPage(
        title="Gradient Hero Page",
        slug="gradient-hero-page",
        body=stream_data,
    )
    root.add_child(instance=standard_page)

    assert standard_page.has_hero_block is True


def test_standard_page_template_path() -> None:
    """StandardPage uses the correct template path."""
    assert StandardPage.template == "theme/standard_page.html"


def test_standard_page_is_leaf_page() -> None:
    """StandardPage has no allowed subpage types (leaf page)."""
    assert StandardPage.subpage_types == []


def test_standard_page_parent_page_types() -> None:
    """StandardPage allows any parent page type via Wagtail default."""
    # parent_page_types is NOT explicitly set in core, inheriting Wagtail's default.
    # Verify it uses Wagtail's default behavior (can be created under root)
    root = Page.get_first_root_node()
    assert StandardPage.can_create_at(root) is True


def test_standard_page_template_uses_sum_core_base() -> None:
    """theme/standard_page.html renders via sum_core fallback base."""
    root = Page.get_first_root_node()
    standard_page = StandardPage(title="Template Test", slug="template-test")
    root.add_child(instance=standard_page)

    site = Site.objects.get(is_default_site=True)
    site.root_page = standard_page
    site.save()

    request = RequestFactory().get("/", HTTP_HOST=site.hostname or "localhost")
    template = Template(
        "{% extends 'theme/standard_page.html' %}"
        "{% block content %}<p>Test Content</p>{% endblock %}"
    )
    rendered = template.render(RequestContext(request, {"page": standard_page}))

    assert "sum_core/css/main.css" in rendered
    assert "<header" in rendered
    assert "<footer" in rendered
