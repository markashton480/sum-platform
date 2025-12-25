"""
Name: BlogPostPage Tests
Path: tests/pages/test_blog_post_page.py
Purpose: Validate BlogPostPage model fields, constraints, and helpers.
"""

from __future__ import annotations

import pytest
from django.db.models.deletion import ProtectedError
from sum_core.blocks import DynamicFormBlock, PageStreamBlock
from sum_core.pages.blog import BlogIndexPage, BlogPostPage, Category
from wagtail.models import Page

pytestmark = pytest.mark.django_db


def _make_blog_index(slug: str = "blog") -> BlogIndexPage:
    """Create a BlogIndexPage under the root node."""
    root = Page.get_first_root_node()
    blog_index = BlogIndexPage(title="Blog", slug=slug)
    root.add_child(instance=blog_index)
    return blog_index


def _make_body(text: str):
    """Return StreamField data for a simple rich text block."""
    stream_block = PageStreamBlock()
    return stream_block.to_python([{"type": "rich_text", "value": f"<p>{text}</p>"}])


def test_blog_post_page_can_be_created_under_blog_index_page() -> None:
    """BlogPostPage can be added as a child of BlogIndexPage."""
    category = Category.objects.create(name="News", slug="news")
    blog_index = _make_blog_index()

    body = _make_body("Welcome to the blog.")
    post = BlogPostPage(
        title="First Post",
        slug="first-post",
        category=category,
        body=body,
    )
    blog_index.add_child(instance=post)

    assert BlogPostPage.objects.filter(slug="first-post").exists()


def test_blog_post_page_parent_constraints() -> None:
    """BlogPostPage is restricted to BlogIndexPage as its parent."""
    blog_index = _make_blog_index(slug="blog-parent-test")
    root = Page.get_first_root_node()

    assert BlogPostPage.can_create_at(blog_index) is True
    assert BlogPostPage.can_create_at(root) is False


def test_blog_post_body_includes_dynamic_form_block() -> None:
    """StreamField block set exposes DynamicFormBlock for CTAs."""
    body_field = BlogPostPage._meta.get_field("body")
    stream_block = body_field.stream_block

    assert "dynamic_form" in stream_block.child_blocks
    assert isinstance(stream_block.child_blocks["dynamic_form"], DynamicFormBlock)


def test_reading_time_calculates_from_body_text() -> None:
    """Reading time estimates minutes using 200 WPM with a minimum of one minute."""
    category = Category.objects.create(name="Guides", slug="guides")
    blog_index = _make_blog_index(slug="blog-reading-time")

    text = " ".join(["word"] * 450)  # ~2.25 minutes at 200 WPM
    post = BlogPostPage(
        title="Reading Time Test",
        slug="reading-time-test",
        category=category,
        body=_make_body(text),
        reading_time=0,
    )
    blog_index.add_child(instance=post)
    post.refresh_from_db()

    assert post.reading_time == 2


def test_reading_time_respects_minimum_one_minute() -> None:
    """Reading time bottoms out at one minute for short content."""
    category = Category.objects.create(name="Updates", slug="updates")
    blog_index = _make_blog_index(slug="blog-reading-min")

    post = BlogPostPage(
        title="Short Post",
        slug="short-post",
        category=category,
        body=_make_body("Short text."),
        reading_time=0,
    )
    blog_index.add_child(instance=post)
    post.refresh_from_db()

    assert post.reading_time == 1


def test_get_excerpt_prefers_manual_excerpt() -> None:
    """Manual excerpt is returned when provided."""
    category = Category.objects.create(name="Insights", slug="insights")
    blog_index = _make_blog_index(slug="blog-excerpt-manual")

    post = BlogPostPage(
        title="Manual Excerpt",
        slug="manual-excerpt",
        category=category,
        body=_make_body("This body should not be used."),
        excerpt="Use this excerpt instead.",
    )
    blog_index.add_child(instance=post)

    assert post.get_excerpt() == "Use this excerpt instead."


def test_get_excerpt_falls_back_to_body_text() -> None:
    """Excerpt is generated from body text when field is blank."""
    category = Category.objects.create(name="Cases", slug="cases")
    blog_index = _make_blog_index(slug="blog-excerpt-fallback")

    text = " ".join(["content"] * 50)  # long enough to trigger truncation
    post = BlogPostPage(
        title="Fallback Excerpt",
        slug="fallback-excerpt",
        category=category,
        body=_make_body(text),
        excerpt="",
    )
    blog_index.add_child(instance=post)

    excerpt = post.get_excerpt()
    assert excerpt.startswith("content content")
    assert excerpt.endswith("...")
    assert len(excerpt) == 150


def test_featured_image_is_optional() -> None:
    """Featured image field is nullable and optional."""
    category = Category.objects.create(name="Announcements", slug="announcements")
    blog_index = _make_blog_index(slug="blog-featured-image")

    post = BlogPostPage(
        title="Optional Featured Image",
        slug="optional-featured-image",
        category=category,
        body=_make_body("Body content."),
        featured_image=None,
    )
    blog_index.add_child(instance=post)

    saved_post = BlogPostPage.objects.get(slug="optional-featured-image")
    assert saved_post.featured_image is None


def test_category_is_protected_from_deletion() -> None:
    """Category uses PROTECT to prevent deletion when posts reference it."""
    category = Category.objects.create(name="How-Tos", slug="how-tos")
    blog_index = _make_blog_index(slug="blog-protect-category")

    post = BlogPostPage(
        title="Category Protected",
        slug="category-protected",
        category=category,
        body=_make_body("Body content."),
    )
    blog_index.add_child(instance=post)

    with pytest.raises(ProtectedError):
        category.delete()
