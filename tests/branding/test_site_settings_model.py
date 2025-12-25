"""
Name: SiteSettings Model Tests
Path: tests/branding/test_site_settings_model.py
Purpose: Validate the SiteSettings model stores and retrieves branding data.
Family: Branding test suite.
Dependencies: Django, Wagtail, sum_core.branding.models.SiteSettings.
"""

from __future__ import annotations

import uuid

import pytest
from sum_core.branding.models import SiteSettings
from sum_core.pages import StandardPage
from wagtail.models import Site

pytestmark = pytest.mark.django_db


def test_site_settings_fields_persist() -> None:
    site = Site.objects.get(is_default_site=True)
    settings = SiteSettings.for_site(site)
    root = site.root_page

    privacy_page = StandardPage(
        title="Privacy Policy", slug=f"privacy-{uuid.uuid4().hex[:8]}"
    )
    root.add_child(instance=privacy_page)
    privacy_page.save_revision().publish()

    cookie_page = StandardPage(
        title="Cookie Policy", slug=f"cookies-{uuid.uuid4().hex[:8]}"
    )
    root.add_child(instance=cookie_page)
    cookie_page.save_revision().publish()

    terms_page = StandardPage(title="Terms", slug=f"terms-{uuid.uuid4().hex[:8]}")
    root.add_child(instance=terms_page)
    terms_page.save_revision().publish()

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
    settings.cookie_banner_enabled = True
    settings.cookie_consent_version = "2024-01"
    settings.privacy_policy_page = privacy_page
    settings.cookie_policy_page = cookie_page
    settings.terms_page = terms_page
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
    assert retrieved.cookie_banner_enabled is True
    assert retrieved.cookie_consent_version == "2024-01"
    assert retrieved.privacy_policy_page.specific == privacy_page
    assert retrieved.cookie_policy_page.specific == cookie_page
    assert retrieved.terms_page.specific == terms_page


def test_site_settings_established_year_field() -> None:
    field = SiteSettings._meta.get_field("established_year")
    assert field.null is True
    assert field.blank is True


def test_cookie_consent_fields_are_per_site() -> None:
    default_site = Site.objects.get(is_default_site=True)
    alt_site = Site.objects.create(
        hostname="consent-alt.test",
        port=80,
        site_name="Consent Alt",
        root_page=default_site.root_page,
        is_default_site=False,
    )

    default_settings = SiteSettings.for_site(default_site)
    default_settings.cookie_banner_enabled = True
    default_settings.cookie_consent_version = "v2"
    default_settings.save()

    alt_settings = SiteSettings.for_site(alt_site)

    assert alt_settings.cookie_banner_enabled is False
    assert alt_settings.cookie_consent_version == "1"
