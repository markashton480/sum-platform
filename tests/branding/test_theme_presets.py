"""
Name: Theme Presets Tests
Path: tests/branding/test_theme_presets.py
Purpose: Verify theme preset definitions and SiteSettings admin form behaviour.
Family: Branding test suite.
Dependencies: SiteSettings, SiteSettingsAdminForm, THEME_PRESETS.
"""

from __future__ import annotations

import pytest
from wagtail.models import Site

from sum_core.branding.forms import SiteSettingsAdminForm  # type: ignore[import-not-found]
from sum_core.branding.models import SiteSettings  # type: ignore[import-not-found]
from sum_core.branding.theme_presets import THEME_PRESETS  # type: ignore[import-not-found]

pytestmark = pytest.mark.django_db


# PRD Table C.5 – canonical values
PRD_PRESETS = {
    "premium-trade": {
        "label": "Premium Trade",
        "primary_color": "#1e3a5f",
        "secondary_color": "#0f172a",
        "accent_color": "#f59e0b",
        "heading_font": "Montserrat",
        "body_font": "Open Sans",
    },
    "professional-blue": {
        "label": "Professional Blue",
        "primary_color": "#2563eb",
        "secondary_color": "#1e40af",
        "accent_color": "#f97316",
        "heading_font": "Poppins",
        "body_font": "Inter",
    },
    "modern-green": {
        "label": "Modern Green",
        "primary_color": "#059669",
        "secondary_color": "#064e3b",
        "accent_color": "#fbbf24",
        "heading_font": "DM Sans",
        "body_font": "Source Sans 3",
    },
    "warm-earth": {
        "label": "Warm Earth",
        "primary_color": "#92400e",
        "secondary_color": "#78350f",
        "accent_color": "#dc2626",
        "heading_font": "Playfair Display",
        "body_font": "Lato",
    },
    "clean-slate": {
        "label": "Clean Slate",
        "primary_color": "#374151",
        "secondary_color": "#1f2937",
        "accent_color": "#6366f1",
        "heading_font": "Work Sans",
        "body_font": "Roboto",
    },
}


def test_theme_presets_match_prd_definitions() -> None:
    """Assert THEME_PRESETS has 5 entries with expected slugs and values from PRD table C.5."""
    assert len(THEME_PRESETS) == 5
    expected_keys = {
        "premium-trade",
        "professional-blue",
        "modern-green",
        "warm-earth",
        "clean-slate",
    }
    assert set(THEME_PRESETS.keys()) == expected_keys

    for key, expected in PRD_PRESETS.items():
        preset = THEME_PRESETS[key]
        assert preset.label == expected["label"], f"{key}: label mismatch"
        assert preset.primary_color == expected["primary_color"], f"{key}: primary_color mismatch"
        assert (
            preset.secondary_color == expected["secondary_color"]
        ), f"{key}: secondary_color mismatch"
        assert preset.accent_color == expected["accent_color"], f"{key}: accent_color mismatch"
        assert preset.heading_font == expected["heading_font"], f"{key}: heading_font mismatch"
        assert preset.body_font == expected["body_font"], f"{key}: body_font mismatch"


def test_site_settings_admin_form_has_theme_preset_field() -> None:
    """Instantiate SiteSettingsAdminForm and verify theme_preset field exists with correct choices."""
    site = Site.objects.get(is_default_site=True)
    settings = SiteSettings.for_site(site)
    form = SiteSettingsAdminForm(instance=settings)

    assert "theme_preset" in form.fields
    choices = form.fields["theme_preset"].choices
    # 1 blank + 5 presets = 6 choices
    assert len(choices) == 6
    # First choice should be blank
    assert choices[0] == ("", "---------")
    # All preset keys should be in choices
    preset_keys = {choice[0] for choice in choices[1:]}
    assert preset_keys == set(THEME_PRESETS.keys())


def test_applying_theme_preset_updates_site_settings_fields() -> None:
    """Applying 'premium-trade' preset should update colour and font fields."""
    site = Site.objects.get(is_default_site=True)
    settings = SiteSettings.for_site(site)

    # Set initial different values
    settings.primary_color = "#000000"
    settings.secondary_color = "#111111"
    settings.accent_color = "#222222"
    settings.heading_font = "Arial"
    settings.body_font = "Helvetica"
    settings.save()

    # Build form data with all required fields + theme_preset
    form_data = {
        "site": site.pk,
        "theme_preset": "premium-trade",
        # Include other required fields with current/blank values
        "primary_color": settings.primary_color,
        "secondary_color": settings.secondary_color,
        "accent_color": settings.accent_color,
        "background_color": settings.background_color,
        "surface_color": settings.surface_color,
        "surface_elevated_color": settings.surface_elevated_color,
        "text_color": settings.text_color,
        "text_light_color": settings.text_light_color,
        "heading_font": settings.heading_font,
        "body_font": settings.body_font,
        "company_name": settings.company_name,
        "tagline": settings.tagline,
        "phone_number": settings.phone_number,
        "email": settings.email,
        "address": settings.address,
        "business_hours": settings.business_hours,
        "facebook_url": settings.facebook_url,
        "instagram_url": settings.instagram_url,
        "linkedin_url": settings.linkedin_url,
        "twitter_url": settings.twitter_url,
        "youtube_url": settings.youtube_url,
        "tiktok_url": settings.tiktok_url,
    }

    form = SiteSettingsAdminForm(data=form_data, instance=settings)
    assert form.is_valid(), f"Form errors: {form.errors}"
    saved_instance = form.save()

    # Verify the preset values were applied
    expected = PRD_PRESETS["premium-trade"]
    assert saved_instance.primary_color == expected["primary_color"]
    assert saved_instance.secondary_color == expected["secondary_color"]
    assert saved_instance.accent_color == expected["accent_color"]
    assert saved_instance.heading_font == expected["heading_font"]
    assert saved_instance.body_font == expected["body_font"]


def test_manual_edits_after_preset_are_respected() -> None:
    """After applying a preset, manual edits with no preset selected should persist."""
    site = Site.objects.get(is_default_site=True)
    settings = SiteSettings.for_site(site)

    # First, apply a preset
    form_data = {
        "site": site.pk,
        "theme_preset": "clean-slate",
        "primary_color": "",
        "secondary_color": "",
        "accent_color": "",
        "background_color": "",
        "surface_color": "",
        "surface_elevated_color": "",
        "text_color": "",
        "text_light_color": "",
        "heading_font": "",
        "body_font": "",
        "company_name": "",
        "tagline": "",
        "phone_number": "",
        "email": "",
        "address": "",
        "business_hours": "",
        "facebook_url": "",
        "instagram_url": "",
        "linkedin_url": "",
        "twitter_url": "",
        "youtube_url": "",
        "tiktok_url": "",
    }

    form = SiteSettingsAdminForm(data=form_data, instance=settings)
    assert form.is_valid(), f"Form errors: {form.errors}"
    form.save()

    # Refresh from database to get the saved state
    settings.refresh_from_db()

    # Confirm preset values applied
    assert settings.primary_color == PRD_PRESETS["clean-slate"]["primary_color"]

    # Now make manual edits with no preset selected
    custom_primary = "#abcdef"
    custom_heading_font = "Custom Font"

    form_data_manual = {
        "site": site.pk,
        "theme_preset": "",  # No preset selected
        "primary_color": custom_primary,
        "secondary_color": settings.secondary_color,
        "accent_color": settings.accent_color,
        "background_color": settings.background_color,
        "surface_color": settings.surface_color,
        "surface_elevated_color": settings.surface_elevated_color,
        "text_color": settings.text_color,
        "text_light_color": settings.text_light_color,
        "heading_font": custom_heading_font,
        "body_font": settings.body_font,
        "company_name": settings.company_name,
        "tagline": settings.tagline,
        "phone_number": settings.phone_number,
        "email": settings.email,
        "address": settings.address,
        "business_hours": settings.business_hours,
        "facebook_url": settings.facebook_url,
        "instagram_url": settings.instagram_url,
        "linkedin_url": settings.linkedin_url,
        "twitter_url": settings.twitter_url,
        "youtube_url": settings.youtube_url,
        "tiktok_url": settings.tiktok_url,
    }

    form2 = SiteSettingsAdminForm(data=form_data_manual, instance=settings)
    assert form2.is_valid(), f"Form errors: {form2.errors}"
    form2.save()

    # Refresh from database to verify saved values
    settings.refresh_from_db()

    # Verify manual edits persisted and were not overwritten
    assert settings.primary_color == custom_primary
    assert settings.heading_font == custom_heading_font
    # Other preset values should still be from clean-slate (unchanged)
    assert settings.secondary_color == PRD_PRESETS["clean-slate"]["secondary_color"]

