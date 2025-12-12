"""
Name: Navigation Services Tests
Path: tests/navigation/test_services.py
Purpose: Unit tests for effective settings resolver service (override→fallback precedence).
Family: Navigation System Test Suite
Dependencies: pytest, wagtail.models

Test Coverage:
    - Footer fallback: Empty FooterNavigation fields fall back to Branding
    - Footer override: Non-empty FooterNavigation fields override Branding
    - Field mapping: Branding twitter_url maps to output social["x"]
    - TikTok fallback: social["tiktok"] always from Branding
    - Header phone: phone_number included only when show_phone_in_header=True
"""

import pytest
from sum_core.branding.models import SiteSettings
from sum_core.navigation.models import FooterNavigation, HeaderNavigation
from sum_core.navigation.services import (
    EffectiveCTAConfig,
    EffectiveFooterSettings,
    EffectiveHeaderSettings,
    get_effective_footer_settings,
    get_effective_header_settings,
)

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def default_site(wagtail_default_site):
    """Returns the default Wagtail Site."""
    return wagtail_default_site


@pytest.fixture
def branding_settings(default_site):
    """Create Branding SiteSettings with test values."""
    settings, _ = SiteSettings.objects.get_or_create(
        site=default_site,
        defaults={
            "tagline": "Branding Tagline",
            "company_name": "Branding Company",
            "phone_number": "555-BRANDING",
            "email": "branding@example.com",
            "address": "123 Branding Street",
            "facebook_url": "https://facebook.com/branding",
            "instagram_url": "https://instagram.com/branding",
            "linkedin_url": "https://linkedin.com/branding",
            "youtube_url": "https://youtube.com/branding",
            "twitter_url": "https://twitter.com/branding",
            "tiktok_url": "https://tiktok.com/@branding",
        },
    )
    # Update fields in case the settings already existed
    settings.tagline = "Branding Tagline"
    settings.company_name = "Branding Company"
    settings.phone_number = "555-BRANDING"
    settings.email = "branding@example.com"
    settings.address = "123 Branding Street"
    settings.facebook_url = "https://facebook.com/branding"
    settings.instagram_url = "https://instagram.com/branding"
    settings.linkedin_url = "https://linkedin.com/branding"
    settings.youtube_url = "https://youtube.com/branding"
    settings.twitter_url = "https://twitter.com/branding"
    settings.tiktok_url = "https://tiktok.com/@branding"
    settings.save()
    return settings


@pytest.fixture
def empty_footer_navigation(default_site):
    """Create FooterNavigation with all empty fields."""
    nav, _ = FooterNavigation.objects.get_or_create(
        site=default_site,
        defaults={
            "tagline": "",
            "social_facebook": "",
            "social_instagram": "",
            "social_linkedin": "",
            "social_youtube": "",
            "social_x": "",
        },
    )
    # Ensure fields are empty
    nav.tagline = ""
    nav.social_facebook = ""
    nav.social_instagram = ""
    nav.social_linkedin = ""
    nav.social_youtube = ""
    nav.social_x = ""
    nav.save()
    return nav


@pytest.fixture
def populated_footer_navigation(default_site):
    """Create FooterNavigation with populated override values."""
    nav, _ = FooterNavigation.objects.get_or_create(
        site=default_site,
        defaults={
            "tagline": "Footer Override Tagline",
            "social_facebook": "https://facebook.com/footer",
            "social_instagram": "https://instagram.com/footer",
            "social_linkedin": "https://linkedin.com/footer",
            "social_youtube": "https://youtube.com/footer",
            "social_x": "https://x.com/footer",
        },
    )
    nav.tagline = "Footer Override Tagline"
    nav.social_facebook = "https://facebook.com/footer"
    nav.social_instagram = "https://instagram.com/footer"
    nav.social_linkedin = "https://linkedin.com/footer"
    nav.social_youtube = "https://youtube.com/footer"
    nav.social_x = "https://x.com/footer"
    nav.save()
    return nav


@pytest.fixture
def header_navigation_phone_on(default_site):
    """Create HeaderNavigation with show_phone_in_header=True."""
    nav, _ = HeaderNavigation.objects.get_or_create(
        site=default_site,
        defaults={
            "show_phone_in_header": True,
            "header_cta_enabled": True,
            "header_cta_text": "Get a Quote",
            "mobile_cta_enabled": True,
            "mobile_cta_phone_enabled": True,
            "mobile_cta_button_enabled": True,
            "mobile_cta_button_text": "Call Now",
        },
    )
    nav.show_phone_in_header = True
    nav.header_cta_enabled = True
    nav.header_cta_text = "Get a Quote"
    nav.mobile_cta_enabled = True
    nav.mobile_cta_phone_enabled = True
    nav.mobile_cta_button_enabled = True
    nav.mobile_cta_button_text = "Call Now"
    nav.save()
    return nav


@pytest.fixture
def header_navigation_phone_off(default_site):
    """Create HeaderNavigation with show_phone_in_header=False."""
    nav, _ = HeaderNavigation.objects.get_or_create(
        site=default_site,
        defaults={"show_phone_in_header": False},
    )
    nav.show_phone_in_header = False
    nav.save()
    return nav


# =============================================================================
# Footer Fallback Tests
# =============================================================================


class TestFooterFallback:
    """Tests for footer fallback behaviour (empty Navigation → Branding values)."""

    def test_tagline_falls_back_to_branding(
        self, default_site, branding_settings, empty_footer_navigation
    ):
        """
        When FooterNavigation.tagline is empty, service returns Branding tagline.

        AC: Footer fallback - empty fields return Branding values.
        """
        result = get_effective_footer_settings(default_site)

        assert result.tagline == "Branding Tagline"

    def test_social_facebook_falls_back_to_branding(
        self, default_site, branding_settings, empty_footer_navigation
    ):
        """When FooterNavigation.social_facebook is empty, falls back to Branding."""
        result = get_effective_footer_settings(default_site)

        assert result.social["facebook"] == "https://facebook.com/branding"

    def test_social_instagram_falls_back_to_branding(
        self, default_site, branding_settings, empty_footer_navigation
    ):
        """When FooterNavigation.social_instagram is empty, falls back to Branding."""
        result = get_effective_footer_settings(default_site)

        assert result.social["instagram"] == "https://instagram.com/branding"

    def test_social_linkedin_falls_back_to_branding(
        self, default_site, branding_settings, empty_footer_navigation
    ):
        """When FooterNavigation.social_linkedin is empty, falls back to Branding."""
        result = get_effective_footer_settings(default_site)

        assert result.social["linkedin"] == "https://linkedin.com/branding"

    def test_social_youtube_falls_back_to_branding(
        self, default_site, branding_settings, empty_footer_navigation
    ):
        """When FooterNavigation.social_youtube is empty, falls back to Branding."""
        result = get_effective_footer_settings(default_site)

        assert result.social["youtube"] == "https://youtube.com/branding"

    def test_all_footer_fields_fallback_to_branding(
        self, default_site, branding_settings, empty_footer_navigation
    ):
        """
        When all FooterNavigation fields are empty, all values fall back to Branding.

        AC: Footer fallback - service returns Branding values for all fields.
        """
        result = get_effective_footer_settings(default_site)

        assert result.tagline == "Branding Tagline"
        assert result.company_name == "Branding Company"
        assert result.phone_number == "555-BRANDING"
        assert result.email == "branding@example.com"
        assert result.address == "123 Branding Street"
        assert result.social["facebook"] == "https://facebook.com/branding"
        assert result.social["instagram"] == "https://instagram.com/branding"
        assert result.social["linkedin"] == "https://linkedin.com/branding"
        assert result.social["youtube"] == "https://youtube.com/branding"


# =============================================================================
# Footer Override Tests
# =============================================================================


class TestFooterOverride:
    """Tests for footer override behaviour (non-empty Navigation overrides Branding)."""

    def test_tagline_overrides_branding(
        self, default_site, branding_settings, populated_footer_navigation
    ):
        """
        When FooterNavigation.tagline is set, it overrides Branding tagline.

        AC: Footer override - non-empty fields override Branding.
        """
        result = get_effective_footer_settings(default_site)

        assert result.tagline == "Footer Override Tagline"

    def test_social_facebook_overrides_branding(
        self, default_site, branding_settings, populated_footer_navigation
    ):
        """When FooterNavigation.social_facebook is set, it overrides Branding."""
        result = get_effective_footer_settings(default_site)

        assert result.social["facebook"] == "https://facebook.com/footer"

    def test_social_instagram_overrides_branding(
        self, default_site, branding_settings, populated_footer_navigation
    ):
        """When FooterNavigation.social_instagram is set, it overrides Branding."""
        result = get_effective_footer_settings(default_site)

        assert result.social["instagram"] == "https://instagram.com/footer"

    def test_social_linkedin_overrides_branding(
        self, default_site, branding_settings, populated_footer_navigation
    ):
        """When FooterNavigation.social_linkedin is set, it overrides Branding."""
        result = get_effective_footer_settings(default_site)

        assert result.social["linkedin"] == "https://linkedin.com/footer"

    def test_social_youtube_overrides_branding(
        self, default_site, branding_settings, populated_footer_navigation
    ):
        """When FooterNavigation.social_youtube is set, it overrides Branding."""
        result = get_effective_footer_settings(default_site)

        assert result.social["youtube"] == "https://youtube.com/footer"

    def test_social_x_overrides_branding_twitter(
        self, default_site, branding_settings, populated_footer_navigation
    ):
        """
        When FooterNavigation.social_x is set, it overrides Branding twitter_url.

        AC: Footer override - social_x overrides twitter_url in output.
        """
        result = get_effective_footer_settings(default_site)

        assert result.social["x"] == "https://x.com/footer"

    def test_all_footer_fields_override_branding(
        self, default_site, branding_settings, populated_footer_navigation
    ):
        """
        When all FooterNavigation fields are set, they override all Branding values.

        AC: Footer override - all non-empty fields override Branding.
        """
        result = get_effective_footer_settings(default_site)

        assert result.tagline == "Footer Override Tagline"
        assert result.social["facebook"] == "https://facebook.com/footer"
        assert result.social["instagram"] == "https://instagram.com/footer"
        assert result.social["linkedin"] == "https://linkedin.com/footer"
        assert result.social["youtube"] == "https://youtube.com/footer"
        assert result.social["x"] == "https://x.com/footer"


# =============================================================================
# Field Mapping Tests
# =============================================================================


class TestFieldMapping:
    """Tests for field name mapping between Navigation and Branding."""

    def test_twitter_url_maps_to_social_x(
        self, default_site, branding_settings, empty_footer_navigation
    ):
        """
        Branding twitter_url maps to output social["x"] when FooterNavigation.social_x is blank.

        AC: Field mapping - twitter_url → social["x"].
        """
        result = get_effective_footer_settings(default_site)

        assert result.social["x"] == "https://twitter.com/branding"

    def test_canonical_social_keys(
        self, default_site, branding_settings, empty_footer_navigation
    ):
        """
        Output uses canonical social keys regardless of source field names.

        AC: Canonical social keys are consistent (facebook/instagram/linkedin/youtube/x/tiktok).
        """
        result = get_effective_footer_settings(default_site)

        # Verify canonical keys exist
        assert "facebook" in result.social
        assert "instagram" in result.social
        assert "linkedin" in result.social
        assert "youtube" in result.social
        assert "x" in result.social
        assert "tiktok" in result.social

        # Verify no legacy key names
        assert "twitter" not in result.social
        assert "twitter_url" not in result.social


# =============================================================================
# TikTok Fallback Tests
# =============================================================================


class TestTikTokFallback:
    """Tests for TikTok always falling back to Branding."""

    def test_tiktok_always_from_branding(
        self, default_site, branding_settings, empty_footer_navigation
    ):
        """
        Output includes social["tiktok"] from Branding even though FooterNavigation has no TikTok field.

        AC: TikTok fallback - social["tiktok"] always from Branding.
        """
        result = get_effective_footer_settings(default_site)

        assert result.social["tiktok"] == "https://tiktok.com/@branding"

    def test_tiktok_from_branding_when_footer_populated(
        self, default_site, branding_settings, populated_footer_navigation
    ):
        """
        TikTok comes from Branding even when other footer social fields are populated.

        AC: TikTok fallback - always from Branding regardless of footer field state.
        """
        result = get_effective_footer_settings(default_site)

        # Other fields are overridden by footer
        assert result.social["facebook"] == "https://facebook.com/footer"
        # TikTok always from branding
        assert result.social["tiktok"] == "https://tiktok.com/@branding"


# =============================================================================
# Header Phone Tests
# =============================================================================


class TestHeaderPhone:
    """Tests for header phone number visibility based on toggle."""

    def test_phone_included_when_show_phone_true(
        self, default_site, branding_settings, header_navigation_phone_on
    ):
        """
        When show_phone_in_header=True, effective header includes Branding phone_number.

        AC: Header phone - phone_number included when toggle is True.
        """
        result = get_effective_header_settings(default_site)

        assert result.show_phone_in_header is True
        assert result.phone_number == "555-BRANDING"

    def test_phone_none_when_show_phone_false(
        self, default_site, branding_settings, header_navigation_phone_off
    ):
        """
        When show_phone_in_header=False, effective header phone_number is None.

        AC: Header phone - phone_number is None when toggle is False.
        """
        result = get_effective_header_settings(default_site)

        assert result.show_phone_in_header is False
        assert result.phone_number is None


# =============================================================================
# Header CTA Configuration Tests
# =============================================================================


class TestHeaderCTAConfig:
    """Tests for header CTA configuration pass-through."""

    def test_header_cta_config_passed_through(
        self, default_site, branding_settings, header_navigation_phone_on
    ):
        """Header CTA configuration is passed through from HeaderNavigation."""
        result = get_effective_header_settings(default_site)

        assert isinstance(result.header_cta, EffectiveCTAConfig)
        assert result.header_cta.enabled is True
        assert result.header_cta.text == "Get a Quote"

    def test_mobile_cta_config_passed_through(
        self, default_site, branding_settings, header_navigation_phone_on
    ):
        """Mobile CTA configuration is passed through from HeaderNavigation."""
        result = get_effective_header_settings(default_site)

        assert result.mobile_cta_enabled is True
        assert result.mobile_cta_phone_enabled is True
        assert isinstance(result.mobile_cta_button, EffectiveCTAConfig)
        assert result.mobile_cta_button.enabled is True
        assert result.mobile_cta_button.text == "Call Now"


# =============================================================================
# Return Type Tests
# =============================================================================


class TestReturnTypes:
    """Tests for correct return types from resolver functions."""

    def test_footer_settings_returns_dataclass(
        self, default_site, branding_settings, empty_footer_navigation
    ):
        """get_effective_footer_settings returns EffectiveFooterSettings dataclass."""
        result = get_effective_footer_settings(default_site)

        assert isinstance(result, EffectiveFooterSettings)

    def test_header_settings_returns_dataclass(
        self, default_site, branding_settings, header_navigation_phone_on
    ):
        """get_effective_header_settings returns EffectiveHeaderSettings dataclass."""
        result = get_effective_header_settings(default_site)

        assert isinstance(result, EffectiveHeaderSettings)

    def test_footer_social_is_dict(
        self, default_site, branding_settings, empty_footer_navigation
    ):
        """Footer settings social field is a dictionary."""
        result = get_effective_footer_settings(default_site)

        assert isinstance(result.social, dict)


# =============================================================================
# Whitespace Handling Tests
# =============================================================================


class TestWhitespaceHandling:
    """Tests for proper handling of whitespace-only values."""

    def test_whitespace_tagline_falls_back(self, default_site, branding_settings):
        """Whitespace-only tagline is treated as empty and falls back to Branding."""
        nav, _ = FooterNavigation.objects.get_or_create(site=default_site)
        nav.tagline = "   "  # Whitespace only
        nav.save()

        result = get_effective_footer_settings(default_site)

        assert result.tagline == "Branding Tagline"

    def test_whitespace_social_url_falls_back(self, default_site, branding_settings):
        """Whitespace-only social URL is treated as empty and falls back to Branding."""
        nav, _ = FooterNavigation.objects.get_or_create(site=default_site)
        nav.social_facebook = "   "  # Whitespace only
        nav.save()

        result = get_effective_footer_settings(default_site)

        assert result.social["facebook"] == "https://facebook.com/branding"
