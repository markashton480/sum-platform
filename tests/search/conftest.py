"""
Name: Search Test Fixtures
Path: tests/search/conftest.py
Purpose: Shared fixtures for search tests.
Family: Tests.
"""

from __future__ import annotations

from uuid import uuid4

import pytest
from home.models import HomePage
from wagtail.models import Page, Site


@pytest.fixture
def homepage(wagtail_default_site: Site) -> HomePage:
    """Create a HomePage as root page for the default Wagtail site."""
    root = Page.get_first_root_node()
    slug = f"home-{uuid4().hex[:8]}"
    page = HomePage(title="Home", slug=slug)
    root.add_child(instance=page)

    wagtail_default_site.root_page = page
    wagtail_default_site.save()

    return page
