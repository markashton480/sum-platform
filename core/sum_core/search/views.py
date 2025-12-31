"""
Name: Blog Search Views
Path: core/sum_core/search/views.py
Purpose: View functions for blog search functionality.
Family: Search.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from django.core.paginator import Paginator
from django.shortcuts import render
from django.utils import timezone
from sum_core.pages.blog import BlogPostPage

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse


def blog_search(request: HttpRequest) -> HttpResponse:
    """
    Search blog posts by title and body content.

    Query parameters:
        q: Search query string
        page: Page number for pagination (default: 1)

    Returns:
        Rendered search results page with paginated results.
    """
    query = request.GET.get("q", "").strip()
    page_number = request.GET.get("page", 1)

    if query:
        # Search only live, published blog posts
        # Note: Apply search first, then filter results to handle
        # Wagtail search backend limitations with complex filters
        search_results = BlogPostPage.objects.live().public().search(query)

        # Convert to list and filter by published_date
        # This is acceptable for blog search with reasonable result sets
        now = timezone.now()
        results = [post for post in search_results if post.published_date <= now]
    else:
        results = []

    # Paginate results
    paginator = Paginator(results, 10)
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "sum_core/search/blog_search_results.html",
        {
            "query": query,
            "results": page_obj,
            "result_count": paginator.count if query else 0,
        },
    )
