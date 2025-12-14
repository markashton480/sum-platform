"""
Name: Base Template Tests
Path: tests/templates/test_base_template.py
Purpose: Validate base layout and shared header/footer render SiteSettings data
         and branding hooks, with navigation template tags integration.
Family: Template/layout test suite.
Dependencies: Django templates, Wagtail Site and SiteSettings helpers,
              navigation models and template tags.
"""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from django.core.cache import cache
from django.template import RequestContext, Template
from django.test import RequestFactory
from sum_core.branding.models import SiteSettings
from sum_core.navigation.models import FooterNavigation
from wagtail.models import Site

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def clear_cache():
    """Clear cache before and after each test."""
    cache.clear()
    yield
    cache.clear()


def test_base_template_renders_with_branding_and_content() -> None:
    """Test that base template renders with branding CSS and content blocks."""
    site = Site.objects.get(is_default_site=True)
    settings = SiteSettings.for_site(site)
    settings.company_name = "Test Co"
    settings.save()

    request = RequestFactory().get("/", HTTP_HOST=site.hostname or "localhost")
    page = SimpleNamespace(title="Sample Page", seo_title="Custom SEO Title")

    template = Template(
        "{% extends 'sum_core/base.html' %}"
        "{% load branding_tags %}"
        "{% block content %}Hello{% endblock %}"
    )
    rendered = template.render(RequestContext(request, {"page": page}))

    assert "<title>" in rendered
    assert "Custom SEO Title" in rendered
    assert "Test Co" in rendered
    assert "Hello" in rendered
    assert "sum_core/css/main.css" in rendered
    assert '<style id="branding-css">' in rendered


def test_header_and_footer_render_site_settings() -> None:
    """Test that header shows company name and footer shows business info."""
    site = Site.objects.get(is_default_site=True)
    settings = SiteSettings.for_site(site)
    settings.company_name = "Header Footer Co"
    settings.tagline = "Quality you can trust"
    settings.phone_number = "01234 567890"
    settings.email = "hello@example.com"
    settings.address = "123 Test St\nTestville"
    settings.save()

    # Ensure navigation has no overrides
    nav = FooterNavigation.for_site(site)
    nav.tagline = ""
    nav.save()

    request = RequestFactory().get("/", HTTP_HOST=site.hostname or "localhost")
    context = RequestContext(request, {})

    header_html = Template(
        "{% load branding_tags navigation_tags %}"
        "{% include 'sum_core/includes/header.html' %}"
    ).render(context)
    footer_html = Template(
        "{% load branding_tags navigation_tags %}"
        "{% include 'sum_core/includes/footer.html' %}"
    ).render(context)

    # Header should show company name in logo
    assert "Header Footer Co" in header_html

    # Footer should show company name and tagline
    assert "Header Footer Co" in footer_html
    assert "Quality you can trust" in footer_html

    # Business info should appear in footer (via fallback contact section or business section)
    assert "hello@example.com" in footer_html


def test_footer_business_info_in_contact_section() -> None:
    """Test that footer shows business info when no link sections configured."""
    site = Site.objects.get(is_default_site=True)
    settings = SiteSettings.for_site(site)
    settings.company_name = "Business Info Co"
    settings.phone_number = "01onal234 567890"
    settings.email = "info@business.com"
    settings.address = "456 Business Ave\nCommerceville"
    settings.save()

    # Ensure no link sections - should trigger fallback contact section
    nav = FooterNavigation.for_site(site)
    nav.link_sections = []
    nav.save()

    request = RequestFactory().get("/", HTTP_HOST=site.hostname or "localhost")
    context = RequestContext(request, {})

    footer_html = Template(
        "{% load branding_tags navigation_tags %}"
        "{% include 'sum_core/includes/footer.html' %}"
    ).render(context)

    assert "Business Info Co" in footer_html
    assert "info@business.com" in footer_html


def test_event_tracking_script_included() -> None:
    """Validate that event tracking JS is included in base template with defer."""
    site = Site.objects.get(is_default_site=True)
    request = RequestFactory().get("/", HTTP_HOST=site.hostname or "localhost")
    page = SimpleNamespace(title="Event Tracking Test")

    template = Template(
        "{% extends 'sum_core/base.html' %}" "{% block content %}{% endblock %}"
    )
    rendered = template.render(RequestContext(request, {"page": page}))

    # Check for script tag
    assert 'src="/static/sum_core/js/event_tracking.js"' in rendered
    # Check that defer attribute is present (simple string check)
    assert "defer" in rendered
