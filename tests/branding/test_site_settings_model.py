"""
Name: SiteSettings Model Tests
Path: tests/branding/test_site_settings_model.py
Purpose: Validate the SiteSettings model stores and retrieves branding data.
Family: Branding test suite.
Dependencies: Django, Wagtail, sum_core.branding.models.SiteSettings.
"""

from __future__ import annotations

import pytest
from sum_core.branding.models import SiteSettings
from wagtail.models import Site

pytestmark = pytest.mark.django_db


def test_site_settings_fields_persist() -> None:
    site = Site.objects.get(is_default_site=True)
    settings = SiteSettings.for_site(site)

    settings.primary_color = "#123456"
    settings.secondary_color = "#abcdef"
    settings.accent_color = "#fedcba"
    settings.background_color = "#ffffff"
    settings.text_color = "#000000"
    settings.surface_color = "#f8fafc"
    settings.surface_elevated_color = "#e2e8f0"
    settings.text_light_color = "#94a3b8"
    settings.heading_font = "Roboto"
    settings.body_font = "Open Sans"
    settings.company_name = "Acme Corp"
    settings.tagline = "Quality You Can Trust"
    settings.phone_number = "+44 1234 567890"
    settings.email = "info@example.com"
    settings.address = "1 High Street\nLondon"
    settings.business_hours = "Mon–Fri 9-5"
    settings.facebook_url = "https://facebook.com/acme"
    settings.instagram_url = "https://instagram.com/acme"
    settings.linkedin_url = "https://linkedin.com/company/acme"
    settings.twitter_url = "https://x.com/acme"
    settings.youtube_url = "https://youtube.com/@acme"
    settings.tiktok_url = "https://tiktok.com/@acme"
    settings.save()

    retrieved = SiteSettings.for_site(site)

    assert retrieved.company_name == "Acme Corp"
    assert retrieved.primary_color == "#123456"
    assert retrieved.text_color == "#000000"
    assert retrieved.body_font == "Open Sans"
    assert retrieved.tagline == "Quality You Can Trust"
    assert retrieved.address.startswith("1 High Street")
    assert retrieved.facebook_url.endswith("/acme")
    assert retrieved.instagram_url.endswith("/acme")
    assert retrieved.business_hours.startswith("Mon–Fri")


def test_site_settings_established_year_field() -> None:
    field = SiteSettings._meta.get_field("established_year")
    assert field.null is True
    assert field.blank is True
