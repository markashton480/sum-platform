"""
Name: Page Mixins Tests
Path: tests/pages/test_page_mixins.py
Purpose: Unit tests for SEO/OpenGraph/Breadcrumb mixins introduced in Milestone 3.
Family: M3-001 test coverage (unit)
Dependencies: pytest, Wagtail models, sum_core pages mixins, sum_core branding SiteSettings
"""

from __future__ import annotations

import pytest
from django.test import RequestFactory
from sum_core.branding.models import SiteSettings
from sum_core.pages import StandardPage
from wagtail.images.models import Image
from wagtail.images.tests.utils import get_test_image_file
from wagtail.models import Site

pytestmark = pytest.mark.django_db


def test_meta_title_fallback_uses_page_title_and_site_name() -> None:
    site = Site.objects.get(is_default_site=True)
    settings = SiteSettings.for_site(site)
    settings.company_name = "Test Co"
    settings.save()

    page = StandardPage(title="About Us", slug="about-us")
    assert page.meta_title == ""

    assert page.get_meta_title(settings) == "About Us | Test Co"


def test_meta_title_override_wins() -> None:
    site = Site.objects.get(is_default_site=True)
    settings = SiteSettings.for_site(site)
    settings.company_name = "Test Co"
    settings.save()

    page = StandardPage(
        title="About Us", slug="about-us", meta_title="Custom Meta Title"
    )
    assert page.get_meta_title(settings) == "Custom Meta Title"


def test_og_image_fallback_chain_page_then_featured_then_site_default() -> None:
    site = Site.objects.get(is_default_site=True)
    settings = SiteSettings.for_site(site)

    default_img = Image.objects.create(title="Default OG", file=get_test_image_file())
    settings.og_default_image = default_img
    settings.save()

    og_img = Image.objects.create(title="Page OG", file=get_test_image_file())
    featured_img = Image.objects.create(title="Featured", file=get_test_image_file())

    page = StandardPage(title="Page", slug="page")

    # 1) page OG wins
    page.og_image = og_img
    page.featured_image = (
        featured_img  # not a model field; used for fallback logic only
    )
    assert page.get_og_image(settings) == og_img

    # 2) featured wins when no page OG
    page.og_image = None
    assert page.get_og_image(settings) == featured_img

    # 3) site default wins when no page OG and no featured image
    delattr(page, "featured_image")
    assert page.get_og_image(settings) == default_img


def test_breadcrumbs_shape_and_order_for_simple_tree() -> None:
    site = Site.objects.get(is_default_site=True)
    root = site.root_page

    parent = StandardPage(title="Parent", slug="parent")
    root.add_child(instance=parent)
    parent.save_revision().publish()

    child = StandardPage(title="Child", slug="child")
    parent.add_child(instance=child)
    child.save_revision().publish()

    request = RequestFactory().get("/", HTTP_HOST=site.hostname or "testserver")
    crumbs = child.get_breadcrumbs(request=request)

    # Breadcrumbs should end with the parent + current page, in order
    assert [c["title"] for c in crumbs][-2:] == ["Parent", "Child"]
    assert crumbs[-2]["is_current"] is False
    assert crumbs[-1]["is_current"] is True
    assert crumbs[-2]["url"] == parent.get_url(request=request)
    assert crumbs[-1]["url"] == child.get_url(request=request)
