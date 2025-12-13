"""
Name: Branding Fonts Template Tag Tests
Path: tests/branding/test_branding_fonts.py
Purpose: Validate branding_fonts outputs Google Fonts links from SiteSettings.
Family: Branding test suite.
Dependencies: Django templates, Wagtail Site model, branding template tags.
"""

from __future__ import annotations

import pytest
from django.template import RequestContext, Template
from django.test import RequestFactory
from sum_core.branding.models import SiteSettings
from wagtail.models import Site

pytestmark = pytest.mark.django_db


def test_branding_fonts_outputs_google_fonts_link() -> None:
    """Test that branding_fonts outputs Google Fonts links with correct weights."""
    site = Site.objects.get(is_default_site=True)
    settings = SiteSettings.for_site(site)
    settings.heading_font = "Playfair Display"
    settings.body_font = "Open Sans"
    settings.save()

    request = RequestFactory().get("/", HTTP_HOST=site.hostname or "localhost")

    template = Template("{% load branding_tags %}" "{% branding_fonts %}")
    rendered = template.render(RequestContext(request, {}))

    assert "fonts.googleapis.com/css2" in rendered
    # Implementation uses full weight range 300-700
    assert "family=Playfair+Display:wght@300;400;500;600;700" in rendered
    assert "family=Open+Sans:wght@300;400;500;600;700" in rendered
    assert rendered.count("family=") == 2


def test_branding_fonts_deduplicates_same_font() -> None:
    """Test that duplicate fonts are only loaded once."""
    site = Site.objects.get(is_default_site=True)
    settings = SiteSettings.for_site(site)
    settings.heading_font = "Inter"
    settings.body_font = "Inter"
    settings.save()

    request = RequestFactory().get("/", HTTP_HOST=site.hostname or "localhost")

    template = Template("{% load branding_tags %}" "{% branding_fonts %}")
    rendered = template.render(RequestContext(request, {}))

    # Should only include Inter once (deduplicated)
    assert rendered.count("family=Inter:wght@300;400;500;600;700") == 1


def test_branding_fonts_uses_defaults_when_no_fonts() -> None:
    """Test that default design system fonts are loaded when none are configured."""
    site = Site.objects.get(is_default_site=True)
    settings = SiteSettings.for_site(site)
    settings.heading_font = ""
    settings.body_font = ""
    settings.save()

    request = RequestFactory().get("/", HTTP_HOST=site.hostname or "localhost")

    template = Template("{% load branding_tags %}" "{% branding_fonts %}")
    rendered = template.render(RequestContext(request, {}))

    # When no fonts are configured, the design system defaults are used
    assert "fonts.googleapis.com/css2" in rendered
    assert "family=Fraunces" in rendered
    assert "family=Manrope" in rendered
