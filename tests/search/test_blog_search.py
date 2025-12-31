"""
Name: Blog Search Tests
Path: tests/search/test_blog_search.py
Purpose: Validate blog search view, URL resolution, and search functionality.
Family: Search tests.
Dependencies: Django test client, Wagtail search, sum_core.search module.

Note: Tests that require Wagtail search functionality are marked with
`wagtail_search_required` as they may need special database configuration
(e.g., PostgreSQL with full-text search) to pass reliably.
"""

from __future__ import annotations

from uuid import uuid4

import pytest
from django.test import Client
from django.urls import reverse
from django.utils import timezone
from home.models import HomePage
from sum_core.blocks import PageStreamBlock
from sum_core.pages.blog import BlogIndexPage, BlogPostPage, Category

pytestmark = pytest.mark.django_db

# Mark for tests that depend on Wagtail search functionality
# These may fail with SQLite's limited search capabilities
wagtail_search_required = pytest.mark.skipif(
    True,  # Skip in standard test runs; remove to enable with PostgreSQL
    reason="Wagtail search requires PostgreSQL full-text search for reliable results",
)


def _make_body(text: str):
    """Create a minimal StreamField body with text content."""
    stream_block = PageStreamBlock()
    return stream_block.to_python([{"type": "rich_text", "value": f"<p>{text}</p>"}])


def _create_blog_index(homepage: HomePage, posts_per_page: int = 10) -> BlogIndexPage:
    """Create and publish a BlogIndexPage under the homepage."""
    blog_index = BlogIndexPage(
        title="Blog",
        slug="blog",
        posts_per_page=posts_per_page,
    )
    homepage.add_child(instance=blog_index)
    blog_index.save_revision().publish()
    return blog_index


def _create_post(
    blog_index: BlogIndexPage,
    title: str,
    slug: str,
    body_text: str = "Default body text",
    published: timezone.datetime | None = None,
    category: Category | None = None,
    publish: bool = True,
) -> BlogPostPage:
    """Create a blog post with specified content."""
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
        body=_make_body(body_text),
    )
    blog_index.add_child(instance=post)
    if publish:
        post.save_revision().publish()
    else:
        post.live = False
        post.save(update_fields=["live"])
        post.save_revision()
    return post


class TestBlogSearchURL:
    """Tests for blog search URL configuration."""

    def test_blog_search_url_resolves(self) -> None:
        """blog_search URL name resolves correctly."""
        url = reverse("blog_search")
        assert url == "/blog/search/"

    def test_blog_search_url_returns_200(
        self,
        client: Client,
        homepage: HomePage,
    ) -> None:
        """blog_search URL returns 200 OK."""
        _create_blog_index(homepage)
        response = client.get("/blog/search/")
        assert response.status_code == 200

    def test_blog_search_url_with_query(
        self,
        client: Client,
        homepage: HomePage,
    ) -> None:
        """blog_search URL accepts query parameter."""
        _create_blog_index(homepage)
        response = client.get("/blog/search/", {"q": "test"})
        assert response.status_code == 200


class TestBlogSearchView:
    """Tests for blog search view behavior."""

    def test_empty_query_returns_no_results(
        self,
        client: Client,
        homepage: HomePage,
    ) -> None:
        """Empty search query returns empty results."""
        blog_index = _create_blog_index(homepage)
        _create_post(blog_index, "Test Post", "test-post")

        response = client.get("/blog/search/")

        assert response.context["query"] == ""
        assert response.context["result_count"] == 0
        assert len(response.context["results"]) == 0

    def test_whitespace_query_treated_as_empty(
        self,
        client: Client,
        homepage: HomePage,
    ) -> None:
        """Whitespace-only query is treated as empty."""
        blog_index = _create_blog_index(homepage)
        _create_post(blog_index, "Test Post", "test-post")

        response = client.get("/blog/search/", {"q": "   "})

        assert response.context["query"] == ""
        assert response.context["result_count"] == 0

    @wagtail_search_required
    def test_search_finds_post_by_title(
        self,
        client: Client,
        homepage: HomePage,
    ) -> None:
        """Search returns posts matching title."""
        blog_index = _create_blog_index(homepage)
        matching_post = _create_post(
            blog_index,
            "Kitchen Design Guide",
            "kitchen-design",
            body_text="Tips for designing your kitchen.",
        )
        _create_post(
            blog_index,
            "Bathroom Renovation",
            "bathroom-reno",
            body_text="How to renovate your bathroom.",
        )

        response = client.get("/blog/search/", {"q": "kitchen"})

        results = list(response.context["results"])
        assert len(results) == 1
        assert results[0].pk == matching_post.pk

    @wagtail_search_required
    def test_search_finds_post_by_body_content(
        self,
        client: Client,
        homepage: HomePage,
    ) -> None:
        """Search returns posts matching body content."""
        blog_index = _create_blog_index(homepage)
        matching_post = _create_post(
            blog_index,
            "Generic Title",
            "generic-post",
            body_text="This post discusses sustainable architecture principles.",
        )
        _create_post(
            blog_index,
            "Another Post",
            "another-post",
            body_text="This is about something else entirely.",
        )

        response = client.get("/blog/search/", {"q": "sustainable"})

        results = list(response.context["results"])
        assert len(results) == 1
        assert results[0].pk == matching_post.pk

    @wagtail_search_required
    def test_search_is_case_insensitive(
        self,
        client: Client,
        homepage: HomePage,
    ) -> None:
        """Search is case-insensitive."""
        blog_index = _create_blog_index(homepage)
        post = _create_post(
            blog_index,
            "UPPERCASE TITLE",
            "upper-post",
            body_text="Body text here.",
        )

        response = client.get("/blog/search/", {"q": "uppercase"})

        results = list(response.context["results"])
        assert len(results) == 1
        assert results[0].pk == post.pk

    @wagtail_search_required
    def test_search_excludes_draft_posts(
        self,
        client: Client,
        homepage: HomePage,
    ) -> None:
        """Search excludes unpublished/draft posts."""
        blog_index = _create_blog_index(homepage)
        _create_post(
            blog_index,
            "Draft Kitchen Post",
            "draft-kitchen",
            body_text="Draft content about kitchens.",
            publish=False,
        )
        live_post = _create_post(
            blog_index,
            "Live Kitchen Post",
            "live-kitchen",
            body_text="Published content about kitchens.",
        )

        response = client.get("/blog/search/", {"q": "kitchen"})

        results = list(response.context["results"])
        assert len(results) == 1
        assert results[0].pk == live_post.pk

    @wagtail_search_required
    def test_search_excludes_future_posts(
        self,
        client: Client,
        homepage: HomePage,
    ) -> None:
        """Search excludes posts with future published_date."""
        blog_index = _create_blog_index(homepage)

        future_time = timezone.now() + timezone.timedelta(days=7)
        _create_post(
            blog_index,
            "Future Kitchen Post",
            "future-kitchen",
            body_text="Scheduled content about kitchens.",
            published=future_time,
        )

        past_time = timezone.now() - timezone.timedelta(days=1)
        past_post = _create_post(
            blog_index,
            "Past Kitchen Post",
            "past-kitchen",
            body_text="Published content about kitchens.",
            published=past_time,
        )

        response = client.get("/blog/search/", {"q": "kitchen"})

        results = list(response.context["results"])
        assert len(results) == 1
        assert results[0].pk == past_post.pk

    def test_search_with_no_matches_returns_empty(
        self,
        client: Client,
        homepage: HomePage,
    ) -> None:
        """Search query with no matches returns empty results."""
        blog_index = _create_blog_index(homepage)
        _create_post(
            blog_index,
            "Kitchen Design",
            "kitchen-design",
            body_text="Content about kitchens.",
        )

        response = client.get("/blog/search/", {"q": "xyznonexistent"})

        assert response.context["result_count"] == 0
        assert len(list(response.context["results"])) == 0

    @wagtail_search_required
    def test_search_returns_multiple_matches(
        self,
        client: Client,
        homepage: HomePage,
    ) -> None:
        """Search returns all matching posts."""
        blog_index = _create_blog_index(homepage)
        post1 = _create_post(
            blog_index,
            "Kitchen Design Tips",
            "kitchen-tips",
            body_text="Tips for kitchens.",
        )
        post2 = _create_post(
            blog_index,
            "Kitchen Renovation Guide",
            "kitchen-reno",
            body_text="Renovation guide for kitchens.",
        )
        _create_post(
            blog_index,
            "Bathroom Ideas",
            "bathroom-ideas",
            body_text="Ideas for bathrooms.",
        )

        response = client.get("/blog/search/", {"q": "kitchen"})

        results = list(response.context["results"])
        result_pks = [r.pk for r in results]
        assert len(results) == 2
        assert post1.pk in result_pks
        assert post2.pk in result_pks


class TestBlogSearchPagination:
    """Tests for blog search pagination."""

    @wagtail_search_required
    def test_search_paginates_results(
        self,
        client: Client,
        homepage: HomePage,
    ) -> None:
        """Search results are paginated at 10 per page."""
        blog_index = _create_blog_index(homepage)

        # Create 15 posts with "kitchen" in the title
        for i in range(15):
            _create_post(
                blog_index,
                f"Kitchen Post {i}",
                f"kitchen-post-{i}",
                body_text=f"Kitchen content {i}.",
            )

        response = client.get("/blog/search/", {"q": "kitchen"})

        assert len(list(response.context["results"])) == 10
        assert response.context["results"].has_next is True

    @wagtail_search_required
    def test_search_page_parameter_works(
        self,
        client: Client,
        homepage: HomePage,
    ) -> None:
        """Page parameter returns correct page of results."""
        blog_index = _create_blog_index(homepage)

        # Create 15 posts with "kitchen" in the title
        for i in range(15):
            _create_post(
                blog_index,
                f"Kitchen Post {i}",
                f"kitchen-post-{i}",
                body_text=f"Kitchen content {i}.",
            )

        response = client.get("/blog/search/", {"q": "kitchen", "page": "2"})

        assert len(list(response.context["results"])) == 5
        assert response.context["results"].has_previous is True
        assert response.context["results"].has_next is False

    def test_search_invalid_page_defaults_to_first(
        self,
        client: Client,
        homepage: HomePage,
    ) -> None:
        """Invalid page parameter returns first page."""
        blog_index = _create_blog_index(homepage)

        for i in range(15):
            _create_post(
                blog_index,
                f"Kitchen Post {i}",
                f"kitchen-post-{i}",
                body_text=f"Kitchen content {i}.",
            )

        response = client.get("/blog/search/", {"q": "kitchen", "page": "invalid"})

        assert response.context["results"].number == 1


class TestBlogSearchContext:
    """Tests for blog search context data."""

    def test_context_includes_query(
        self,
        client: Client,
        homepage: HomePage,
    ) -> None:
        """Search context includes the query string."""
        _create_blog_index(homepage)

        response = client.get("/blog/search/", {"q": "test query"})

        assert response.context["query"] == "test query"

    @wagtail_search_required
    def test_context_includes_result_count(
        self,
        client: Client,
        homepage: HomePage,
    ) -> None:
        """Search context includes total result count."""
        blog_index = _create_blog_index(homepage)

        for i in range(5):
            _create_post(
                blog_index,
                f"Kitchen Post {i}",
                f"kitchen-post-{i}",
                body_text=f"Kitchen content {i}.",
            )

        response = client.get("/blog/search/", {"q": "kitchen"})

        assert response.context["result_count"] == 5

    def test_context_uses_correct_template(
        self,
        client: Client,
        homepage: HomePage,
    ) -> None:
        """Search view renders the correct template."""
        _create_blog_index(homepage)

        response = client.get("/blog/search/", {"q": "test"})

        assert "sum_core/search/blog_search_results.html" in [
            t.name for t in response.templates
        ]
