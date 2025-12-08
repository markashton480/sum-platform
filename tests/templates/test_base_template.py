"""
Name: Base Template Tests
Path: tests/templates/test_base_template.py
Purpose: Validate base layout and shared header/footer render SiteSettings data and branding hooks.
Family: Template/layout test suite.
Dependencies: Django templates, Wagtail Site and SiteSettings helpers.
"""

from __future__ import annotations

from types import SimpleNamespace

from django.template import RequestContext, Template
from django.test import RequestFactory
from wagtail.models import Site
import pytest

from sum_core.branding.models import SiteSettings  # type: ignore[import-not-found]

pytestmark = pytest.mark.django_db


def test_base_template_renders_with_branding_and_content() -> None:
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
    assert "sum_core/css/main.css" in rendered
    assert '<style id="branding-css">' in rendered
    assert "Hello" in rendered


def test_header_and_footer_render_site_settings() -> None:
    site = Site.objects.get(is_default_site=True)
    settings = SiteSettings.for_site(site)
    settings.company_name = "Header Footer Co"
    settings.tagline = "Quality you can trust"
    settings.phone_number = "01234 567890"
    settings.email = "hello@example.com"
    settings.address = "123 Test St\nTestville"
    settings.save()

    request = RequestFactory().get("/", HTTP_HOST=site.hostname or "localhost")
    context = RequestContext(request, {})

    header_html = Template(
        "{% load branding_tags %}"
        "{% include 'sum_core/includes/header.html' %}"
    ).render(context)
    footer_html = Template(
        "{% load branding_tags %}"
        "{% include 'sum_core/includes/footer.html' %}"
    ).render(context)

    assert "Header Footer Co" in header_html
    assert "Header Footer Co" in footer_html
    assert "Quality you can trust" in footer_html
    assert "01234 567890" in footer_html
    assert "hello@example.com" in footer_html
    assert "123 Test St" in footer_html
