"""
Name: Branding Fonts Template Tag Tests
Path: tests/branding/test_branding_fonts.py
Purpose: Validate branding_fonts outputs Google Fonts links from SiteSettings.
Family: Branding test suite.
Dependencies: Django templates, Wagtail Site model, branding template tags.
"""

from __future__ import annotations

from django.template import RequestContext, Template
from django.test import RequestFactory
from wagtail.models import Site
import pytest

from sum_core.branding.models import SiteSettings  # type: ignore[import-not-found]

pytestmark = pytest.mark.django_db


def test_branding_fonts_outputs_google_fonts_link() -> None:
    site = Site.objects.get(is_default_site=True)
    settings = SiteSettings.for_site(site)
    settings.heading_font = "Playfair Display"
    settings.body_font = "Open Sans"
    settings.save()

    request = RequestFactory().get("/", HTTP_HOST=site.hostname or "localhost")

    template = Template(
        "{% load branding_tags %}"
        "{% branding_fonts %}"
    )
    rendered = template.render(RequestContext(request, {}))

    assert "fonts.googleapis.com/css2" in rendered
    assert "family=Playfair+Display:wght@400;500;700" in rendered
    assert "family=Open+Sans:wght@400;500;700" in rendered
    assert rendered.count("family=") == 2


def test_branding_fonts_deduplicates_same_font() -> None:
    site = Site.objects.get(is_default_site=True)
    settings = SiteSettings.for_site(site)
    settings.heading_font = "Inter"
    settings.body_font = "Inter"
    settings.save()

    request = RequestFactory().get("/", HTTP_HOST=site.hostname or "localhost")

    template = Template(
        "{% load branding_tags %}"
        "{% branding_fonts %}"
    )
    rendered = template.render(RequestContext(request, {}))

    assert rendered.count("family=Inter:wght@400;500;700") == 1


def test_branding_fonts_empty_when_no_fonts() -> None:
    site = Site.objects.get(is_default_site=True)
    settings = SiteSettings.for_site(site)
    settings.heading_font = ""
    settings.body_font = ""
    settings.save()

    request = RequestFactory().get("/", HTTP_HOST=site.hostname or "localhost")

    template = Template(
        "{% load branding_tags %}"
        "{% branding_fonts %}"
    )
    rendered = template.render(RequestContext(request, {}))

    assert rendered.strip() == ""
