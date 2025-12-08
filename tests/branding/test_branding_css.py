"""
Name: Branding CSS Template Tag Tests
Path: tests/branding/test_branding_css.py
Purpose: Validate branding_css outputs CSS variables sourced from SiteSettings.
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


def test_branding_css_outputs_site_colors_and_fonts() -> None:
    site = Site.objects.get(is_default_site=True)
    settings = SiteSettings.for_site(site)
    settings.primary_color = "#123456"
    settings.secondary_color = "#654321"
    settings.accent_color = "#abcdef"
    settings.background_color = "#ffffff"
    settings.surface_color = "#eeeeee"
    settings.surface_elevated_color = "#dddddd"
    settings.text_color = "#111111"
    settings.text_light_color = "#999999"
    settings.heading_font = "Playfair Display"
    settings.body_font = "Open Sans"
    settings.save()

    request = RequestFactory().get("/", HTTP_HOST=site.hostname or "localhost")

    template = Template(
        "{% load branding_tags %}"
        "{% branding_css %}"
    )
    rendered = template.render(RequestContext(request, {}))

    assert "--color-primary: #123456;" in rendered
    assert "--color-secondary: #654321;" in rendered
    assert "--color-accent: #abcdef;" in rendered
    assert "--color-background: #ffffff;" in rendered
    assert "--color-surface: #eeeeee;" in rendered
    assert "--color-surface-elevated: #dddddd;" in rendered
    assert "--color-text: #111111;" in rendered
    assert "--color-text-light: #999999;" in rendered
    assert '--font-heading: "Playfair Display", system-ui' in rendered
    assert '--font-body: "Open Sans", system-ui' in rendered


def test_branding_css_respects_defaults_when_blank() -> None:
    site = Site.objects.get(is_default_site=True)
    settings = SiteSettings.for_site(site)
    settings.primary_color = "#123456"
    settings.secondary_color = ""
    settings.accent_color = ""
    settings.background_color = "#ffffff"
    settings.surface_color = ""
    settings.surface_elevated_color = ""
    settings.text_color = ""
    settings.text_light_color = ""
    settings.heading_font = ""
    settings.body_font = ""
    settings.save()

    request = RequestFactory().get("/", HTTP_HOST=site.hostname or "localhost")

    template = Template(
        "{% load branding_tags %}"
        "{% branding_css %}"
    )
    rendered = template.render(RequestContext(request, {}))

    assert "--color-primary: #123456;" in rendered
    assert "--color-background: #ffffff;" in rendered
    assert "--color-secondary" not in rendered
    assert "--color-accent" not in rendered
    assert "--color-surface:" not in rendered
    assert "--color-surface-elevated:" not in rendered
    assert "--color-text:" not in rendered
    assert "--color-text-light:" not in rendered
    assert "--font-heading" not in rendered
    assert "--font-body" not in rendered
