"""
Name: Branding CSS Template Tag Tests
Path: tests/branding/test_branding_css.py
Purpose: Validate branding_css outputs CSS variables sourced from SiteSettings.
Family: Branding test suite.
Dependencies: Django templates, Wagtail Site model, branding template tags.
"""

from __future__ import annotations

import pytest
from django.template import RequestContext, Template
from django.test import RequestFactory
from sum_core.branding.models import SiteSettings  # type: ignore[import-not-found]
from wagtail.models import Site

pytestmark = pytest.mark.django_db


def test_branding_css_outputs_site_colors_and_fonts() -> None:
    """Test that branding CSS outputs HSL variables and font settings."""
    site = Site.objects.get(is_default_site=True)
    settings = SiteSettings.for_site(site)
    settings.primary_color = "#123456"
    settings.secondary_color = "#654321"
    settings.accent_color = "#abcdef"
    settings.heading_font = "Playfair Display"
    settings.body_font = "Open Sans"
    settings.save()

    request = RequestFactory().get("/", HTTP_HOST=site.hostname or "localhost")

    template = Template("{% load branding_tags %}" "{% branding_css %}")
    rendered = template.render(RequestContext(request, {}))

    # The implementation outputs HSL-based variables for theming
    assert "--brand-h:" in rendered
    assert "--brand-s:" in rendered
    assert "--brand-l:" in rendered

    # Secondary and accent colors are output as custom variables
    assert "--color-secondary-custom: #654321;" in rendered
    assert "--color-accent-custom: #abcdef;" in rendered

    # Font variables are output with fallback stack
    assert '--font-heading: "Playfair Display", system-ui' in rendered
    assert '--font-body: "Open Sans", system-ui' in rendered


def test_branding_css_respects_defaults_when_blank() -> None:
    """Test that branding CSS only outputs set values, omitting blank fields."""
    site = Site.objects.get(is_default_site=True)
    settings = SiteSettings.for_site(site)
    settings.primary_color = "#123456"
    settings.secondary_color = ""
    settings.accent_color = ""
    settings.heading_font = ""
    settings.body_font = ""
    settings.save()

    request = RequestFactory().get("/", HTTP_HOST=site.hostname or "localhost")

    template = Template("{% load branding_tags %}" "{% branding_css %}")
    rendered = template.render(RequestContext(request, {}))

    # Primary color generates HSL variables
    assert "--brand-h:" in rendered
    assert "--brand-s:" in rendered
    assert "--brand-l:" in rendered

    # Blank values should not generate custom color variables
    assert "--color-secondary-custom" not in rendered
    assert "--color-accent-custom" not in rendered

    # Blank fonts should not generate font variables
    assert "--font-heading" not in rendered
    assert "--font-body" not in rendered
