"""
Name: Blog Page Tests
Path: tests/pages/test_blog_pages.py
Purpose: Validate BlogIndexPage and BlogPostPage models, hierarchy enforcement, and pagination.
Family: Part of the page-level test suite exercising the page types.
Dependencies: Wagtail Site & Page models, sum_core.pages.blog, home.HomePage.
"""

from __future__ import annotations

from datetime import date

import pytest
from django.test import RequestFactory
from home.models import HomePage
from sum_core.blocks import PageStreamBlock
from sum_core.pages.blog import BlogIndexPage, BlogPostPage
from wagtail.fields import StreamField
from wagtail.models import Page, Site

pytestmark = pytest.mark.django_db


def publish(page: Page) -> None:
    page.save_revision().publish()
    page.refresh_from_db()


# =============================================================================
# BlogIndexPage Model Tests
# =============================================================================


def test_blog_index_page_is_registered_as_page_type() -> None:
    """BlogIndexPage is registered as a Wagtail page type."""
    assert issubclass(BlogIndexPage, Page)


def test_blog_index_page_has_intro_stream_field() -> None:
    """BlogIndexPage has an intro field that is a StreamField."""
    intro_field = BlogIndexPage._meta.get_field("intro")
    assert isinstance(intro_field, StreamField)


def test_blog_index_page_intro_uses_page_stream_block() -> None:
    """BlogIndexPage intro StreamField uses PageStreamBlock."""
    intro_field = BlogIndexPage._meta.get_field("intro")
    assert isinstance(intro_field.stream_block, PageStreamBlock)


def test_blog_index_page_has_paginate_by_field() -> None:
    """BlogIndexPage has a paginate_by field with a default."""
    paginate_field = BlogIndexPage._meta.get_field("paginate_by")
    assert paginate_field.default == 6


def test_blog_index_page_template_path() -> None:
    """BlogIndexPage uses the correct template path."""
    assert BlogIndexPage.template == "theme/blog_index_page.html"


def test_blog_index_page_subpage_types() -> None:
    """BlogIndexPage only allows BlogPostPage children."""
    assert "sum_core_pages.BlogPostPage" in BlogIndexPage.subpage_types


def test_blog_index_page_parent_page_types() -> None:
    """BlogIndexPage allows any parent page type via Wagtail default."""
    root = Page.get_first_root_node()
    assert BlogIndexPage.can_create_at(root) is True


def test_blog_index_page_get_context_includes_paginated_posts() -> None:
    """BlogIndexPage.get_context() includes paginated BlogPostPage children."""
    root = Page.get_first_root_node()

    homepage = HomePage(title="Home", slug="home-blog-context")
    root.add_child(instance=homepage)

    blog_index = BlogIndexPage(title="Blog", slug="blog", paginate_by=2)
    homepage.add_child(instance=blog_index)

    post_one = BlogPostPage(title="Post One", slug="post-one", date=date(2024, 1, 1))
    blog_index.add_child(instance=post_one)
    publish(post_one)

    post_two = BlogPostPage(title="Post Two", slug="post-two", date=date(2024, 2, 1))
    blog_index.add_child(instance=post_two)
    publish(post_two)

    post_three = BlogPostPage(
        title="Post Three", slug="post-three", date=date(2024, 3, 1)
    )
    blog_index.add_child(instance=post_three)
    publish(post_three)

    request = RequestFactory().get("/blog/")
    context = blog_index.get_context(request)

    posts = list(context["posts"])
    assert context["is_paginated"] is True
    assert len(posts) == 2
    assert posts[0].title == "Post Three"
    assert posts[1].title == "Post Two"


def test_blog_index_page_pagination_second_page() -> None:
    """BlogIndexPage pagination returns remaining posts on later pages."""
    root = Page.get_first_root_node()

    homepage = HomePage(title="Home", slug="home-blog-page-2")
    root.add_child(instance=homepage)

    blog_index = BlogIndexPage(title="Blog", slug="blog-page-2", paginate_by=2)
    homepage.add_child(instance=blog_index)

    post_one = BlogPostPage(title="Post One", slug="post-one-2", date=date(2024, 1, 1))
    blog_index.add_child(instance=post_one)
    publish(post_one)

    post_two = BlogPostPage(title="Post Two", slug="post-two-2", date=date(2024, 2, 1))
    blog_index.add_child(instance=post_two)
    publish(post_two)

    post_three = BlogPostPage(
        title="Post Three", slug="post-three-2", date=date(2024, 3, 1)
    )
    blog_index.add_child(instance=post_three)
    publish(post_three)

    request = RequestFactory().get("/blog/?page=2")
    context = blog_index.get_context(request)

    posts = list(context["posts"])
    assert len(posts) == 1
    assert posts[0].title == "Post One"


def test_blog_index_page_returns_200_and_contains_titles(client) -> None:
    """BlogIndexPage response includes expected post titles."""
    root = Page.get_first_root_node()

    homepage = HomePage(title="Home", slug="home-blog-response")
    root.add_child(instance=homepage)
    publish(homepage)

    blog_index = BlogIndexPage(title="Blog", slug="blog-response")
    homepage.add_child(instance=blog_index)
    publish(blog_index)

    post = BlogPostPage(
        title="Featured Post", slug="featured-post", date=date(2024, 4, 1)
    )
    blog_index.add_child(instance=post)
    publish(post)

    site = Site.objects.get(is_default_site=True)
    site.root_page = homepage
    site.save()
    Site.clear_site_root_paths_cache()

    response = client.get(blog_index.url)
    content = response.content.decode()

    assert response.status_code == 200
    assert "Featured Post" in content


# =============================================================================
# BlogPostPage Model Tests
# =============================================================================


def test_blog_post_page_parent_page_types() -> None:
    """BlogPostPage can only be created under BlogIndexPage."""
    assert BlogPostPage.parent_page_types == ["sum_core_pages.BlogIndexPage"]


def test_blog_post_page_can_be_created_under_blog_index() -> None:
    """BlogPostPage can be created under BlogIndexPage."""
    root = Page.get_first_root_node()

    homepage = HomePage(title="Home", slug="home-blog-create")
    root.add_child(instance=homepage)

    blog_index = BlogIndexPage(title="Blog", slug="blog-create")
    homepage.add_child(instance=blog_index)

    post = BlogPostPage(title="Hello Blog", slug="hello-blog")
    blog_index.add_child(instance=post)

    assert BlogPostPage.objects.filter(title="Hello Blog").exists()
