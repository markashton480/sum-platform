"""
Name: Blog Index Page Tests
Path: tests/pages/test_blog_index_page.py
Purpose: Validate BlogIndexPage listing, filtering, pagination, and constraints.
Family: Blog pages test coverage.
Dependencies: Wagtail Site & Page models, home.HomePage, sum_core.pages.blog.
"""

from __future__ import annotations

from uuid import uuid4

import pytest
from django.core.exceptions import ValidationError
from django.test import RequestFactory
from django.utils import timezone
from home.models import HomePage
from sum_core.blocks import PageStreamBlock
from sum_core.pages import StandardPage
from sum_core.pages.blog import BlogIndexPage, BlogPostPage, Category
from wagtail.models import Site

pytestmark = pytest.mark.django_db


def _create_blog_index(homepage: HomePage, posts_per_page: int = 10) -> BlogIndexPage:
    blog_index = BlogIndexPage(
        title="Blog",
        slug="blog",
        posts_per_page=posts_per_page,
    )
    homepage.add_child(instance=blog_index)
    blog_index.save_revision().publish()
    return blog_index


def _make_body(text: str):
    stream_block = PageStreamBlock()
    return stream_block.to_python([{"type": "rich_text", "value": f"<p>{text}</p>"}])


def _create_post(
    blog_index: BlogIndexPage,
    title: str,
    slug: str,
    published: timezone.datetime | None = None,
    category: Category | None = None,
    publish: bool = True,
) -> BlogPostPage:
    if category is None:
        category = Category.objects.create(
            name=f"Category {uuid4().hex[:6]}",
            slug=f"category-{uuid4().hex[:6]}",
        )
    if published is None:
        published = timezone.now()

    post = BlogPostPage(
        title=title,
        slug=slug,
        published_date=published,
        category=category,
        body=_make_body("Body"),
    )
    blog_index.add_child(instance=post)
    if publish:
        post.save_revision().publish()
    else:
        post.live = False
        post.save(update_fields=["live"])
        post.save_revision()
    return post


def test_blog_index_can_be_created_under_homepage(homepage: HomePage) -> None:
    blog_index = _create_blog_index(homepage)

    assert BlogIndexPage.objects.filter(pk=blog_index.pk).exists()


def test_blog_index_singleton_enforced(homepage: HomePage) -> None:
    _create_blog_index(homepage)

    second_blog = BlogIndexPage(title="Blog 2", slug="blog-2")
    with pytest.raises(ValidationError) as excinfo:
        homepage.add_child(instance=second_blog)

    assert excinfo.value is not None


def test_blog_index_subpage_constraints(homepage: HomePage) -> None:
    blog_index = _create_blog_index(homepage)

    assert BlogPostPage.can_create_at(blog_index) is True
    assert StandardPage.can_create_at(blog_index) is False


def test_get_posts_orders_by_published_date_desc(homepage: HomePage) -> None:
    blog_index = _create_blog_index(homepage)

    base_time = timezone.now()
    older = _create_post(
        blog_index, "Older", "older", base_time - timezone.timedelta(days=2)
    )
    newer = _create_post(blog_index, "Newer", "newer", base_time)

    posts = list(blog_index.get_posts())

    assert posts == [newer, older]


def test_get_posts_by_category_filters(homepage: HomePage) -> None:
    blog_index = _create_blog_index(homepage)

    cats = Category.objects.create(name="Cats", slug="cats")
    dogs = Category.objects.create(name="Dogs", slug="dogs")

    base_time = timezone.now()
    cat_post = _create_post(
        blog_index, "Cats 1", "cats-1", base_time - timezone.timedelta(days=1), cats
    )
    _create_post(blog_index, "Dogs 1", "dogs-1", base_time, dogs)

    posts = list(blog_index.get_posts_by_category(cats))

    assert posts == [cat_post]


def test_get_context_category_filtering_valid_slug(
    homepage: HomePage,
    wagtail_default_site: Site,
) -> None:
    blog_index = _create_blog_index(homepage)

    cats = Category.objects.create(name="Cats", slug="cats")
    base_time = timezone.now()
    cat_post = _create_post(
        blog_index, "Cats 1", "cats-1", base_time - timezone.timedelta(days=1), cats
    )
    _create_post(blog_index, "Dogs 1", "dogs-1", base_time)

    request = RequestFactory().get(
        "/blog/",
        {"category": "cats"},
        HTTP_HOST=wagtail_default_site.hostname or "testserver",
    )
    context = blog_index.get_context(request)

    assert list(context["posts"]) == [cat_post]
    assert context["selected_category"] == cats


def test_get_context_category_filtering_invalid_slug(
    homepage: HomePage,
    wagtail_default_site: Site,
) -> None:
    blog_index = _create_blog_index(homepage)

    post = _create_post(blog_index, "Post 1", "post-1")

    request = RequestFactory().get(
        "/blog/",
        {"category": "missing"},
        HTTP_HOST=wagtail_default_site.hostname or "testserver",
    )
    context = blog_index.get_context(request)

    assert list(context["posts"]) == [post]
    assert context["selected_category"] is None


def test_get_context_pagination_invalid_page_defaults_first(
    homepage: HomePage,
    wagtail_default_site: Site,
) -> None:
    blog_index = _create_blog_index(homepage, posts_per_page=1)

    base_time = timezone.now()
    _create_post(blog_index, "Post 1", "post-1", base_time - timezone.timedelta(days=1))
    newer = _create_post(blog_index, "Post 2", "post-2", base_time)

    request = RequestFactory().get(
        "/blog/",
        {"page": "not-a-number"},
        HTTP_HOST=wagtail_default_site.hostname or "testserver",
    )
    context = blog_index.get_context(request)

    assert list(context["posts"]) == [newer]


def test_get_context_pagination_out_of_range_returns_last_page(
    homepage: HomePage,
    wagtail_default_site: Site,
) -> None:
    blog_index = _create_blog_index(homepage, posts_per_page=1)

    base_time = timezone.now()
    older = _create_post(
        blog_index, "Post 1", "post-1", base_time - timezone.timedelta(days=1)
    )
    _create_post(blog_index, "Post 2", "post-2", base_time)

    request = RequestFactory().get(
        "/blog/",
        {"page": "999"},
        HTTP_HOST=wagtail_default_site.hostname or "testserver",
    )
    context = blog_index.get_context(request)

    assert list(context["posts"]) == [older]


def test_get_context_handles_empty_posts(
    homepage: HomePage,
    wagtail_default_site: Site,
) -> None:
    blog_index = _create_blog_index(homepage)

    request = RequestFactory().get(
        "/blog/",
        HTTP_HOST=wagtail_default_site.hostname or "testserver",
    )
    context = blog_index.get_context(request)

    assert list(context["posts"]) == []


def test_get_context_categories_include_post_counts(
    homepage: HomePage,
    wagtail_default_site: Site,
) -> None:
    blog_index = _create_blog_index(homepage)

    cats = Category.objects.create(name="Cats", slug="cats")
    dogs = Category.objects.create(name="Dogs", slug="dogs")

    base_time = timezone.now()
    _create_post(
        blog_index, "Cats 1", "cats-1", base_time - timezone.timedelta(days=1), cats
    )
    _create_post(blog_index, "Cats 2", "cats-2", base_time, cats)
    _create_post(
        blog_index, "Dogs 1", "dogs-1", base_time - timezone.timedelta(days=2), dogs
    )

    request = RequestFactory().get(
        "/blog/",
        HTTP_HOST=wagtail_default_site.hostname or "testserver",
    )
    context = blog_index.get_context(request)

    counts = {category.slug: category.post_count for category in context["categories"]}

    assert counts["cats"] == 2
    assert counts["dogs"] == 1


def test_posts_per_page_requires_positive_value() -> None:
    blog_index = BlogIndexPage(title="Blog", slug="blog", posts_per_page=0)

    with pytest.raises(ValidationError) as excinfo:
        blog_index.full_clean()

    assert "posts_per_page" in excinfo.value.message_dict


def test_get_posts_excludes_unpublished_posts(homepage: HomePage) -> None:
    blog_index = _create_blog_index(homepage)
    category = Category.objects.create(name="News", slug="news")

    live_post = _create_post(blog_index, "Live", "live", category=category)
    draft = _create_post(
        blog_index,
        "Draft",
        "draft",
        category=category,
        publish=False,
    )

    posts = list(blog_index.get_posts())

    assert live_post in posts
    assert draft not in posts
