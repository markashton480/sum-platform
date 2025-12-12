"""
Name: Meta Tags Rendering Tests
Path: tests/templates/test_meta_tags_rendering.py
Purpose: Lightweight integration coverage for SEO/OG/canonical tags in the base template head.
Family: M3-001 test coverage (integration-ish)
Dependencies: Django test client, Wagtail Site/Page, sum_core templates
"""

from __future__ import annotations

import pytest
from django.test import Client
from sum_core.branding.models import SiteSettings
from sum_core.pages import StandardPage
from wagtail.images.models import Image
from wagtail.images.tests.utils import get_test_image_file
from wagtail.models import Site

pytestmark = pytest.mark.django_db


def test_head_contains_basic_meta_og_and_canonical_tags() -> None:
    site = Site.objects.get(is_default_site=True)
    settings = SiteSettings.for_site(site)
    settings.company_name = "Test Co"
    settings.og_default_image = Image.objects.create(
        title="Default OG", file=get_test_image_file()
    )
    settings.save()

    root = site.root_page
    page = StandardPage(
        title="Test Page",
        slug="test-page",
        meta_description="A short description for testing.",
    )
    root.add_child(instance=page)
    page.save_revision().publish()

    client = Client()
    response = client.get(page.url)
    html = response.content.decode()

    assert response.status_code == 200

    # Title default should be "{page.title} | {site name}" when no meta_title/seo_title
    assert "<title>" in html
    assert "Test Page | Test Co" in html

    # Canonical + OG url
    assert '<link rel="canonical"' in html
    assert 'property="og:url"' in html

    # Basic description + OG description
    assert 'name="description"' in html
    assert "A short description for testing." in html
    assert 'property="og:description"' in html

    # OG type + title
    assert 'property="og:type" content="website"' in html
    assert 'property="og:title"' in html

    # OG image should render from the site default
    assert 'property="og:image"' in html
