"""
Name: Navigation Site Settings Models Tests
Path: tests/navigation/test_models.py
Purpose: Unit tests for HeaderNavigation and FooterNavigation site settings.
Family: Navigation System Test Suite
Dependencies: pytest, wagtail.models

Test Coverage:
    - Model field and type verification
    - StreamField constraints (max 8 menu items, min 2/max 4 footer sections)
    - CTA link StreamField constraints (max 1)
    - Site isolation/uniqueness (BaseSiteSetting behavior)
"""

import pytest
from sum_core.navigation.models import (
    FooterNavigation,
    FooterSectionsStreamBlock,
    HeaderNavigation,
    MenuItemsStreamBlock,
    SingleLinkStreamBlock,
)
from wagtail.models import Site

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def default_site(wagtail_default_site):
    """Returns the default Wagtail Site."""
    return wagtail_default_site


@pytest.fixture
def second_site(wagtail_default_site):
    """Creates and returns a second Wagtail Site for isolation tests."""
    from wagtail.models import Page

    root = Page.get_first_root_node()
    # Create a second site with a different hostname
    site, created = Site.objects.get_or_create(
        hostname="second-site.example.com",
        defaults={
            "port": 80,
            "root_page": root,
            "is_default_site": False,
        },
    )
    return site


# =============================================================================
# HeaderNavigation Model Tests
# =============================================================================


class TestHeaderNavigationModel:
    """Tests for HeaderNavigation site settings model."""

    def test_model_has_required_fields(self):
        """Verify HeaderNavigation has all required fields."""
        # Get field names from model
        field_names = [f.name for f in HeaderNavigation._meta.get_fields()]

        # Main navigation fields
        assert "menu_items" in field_names
        assert "show_phone_in_header" in field_names

        # Header CTA fields
        assert "header_cta_enabled" in field_names
        assert "header_cta_text" in field_names
        assert "header_cta_link" in field_names

        # Mobile CTA fields
        assert "mobile_cta_enabled" in field_names
        assert "mobile_cta_phone_enabled" in field_names
        assert "mobile_cta_button_enabled" in field_names
        assert "mobile_cta_button_text" in field_names
        assert "mobile_cta_button_link" in field_names

    def test_header_cta_text_max_length(self):
        """Verify header_cta_text has max_length of 50."""
        field = HeaderNavigation._meta.get_field("header_cta_text")
        assert field.max_length == 50

    def test_mobile_cta_button_text_max_length(self):
        """Verify mobile_cta_button_text has max_length of 50."""
        field = HeaderNavigation._meta.get_field("mobile_cta_button_text")
        assert field.max_length == 50

    def test_boolean_fields_have_defaults(self):
        """Verify boolean fields have appropriate defaults."""
        assert HeaderNavigation._meta.get_field("show_phone_in_header").default is True
        assert HeaderNavigation._meta.get_field("header_cta_enabled").default is True
        assert HeaderNavigation._meta.get_field("mobile_cta_enabled").default is True
        assert (
            HeaderNavigation._meta.get_field("mobile_cta_phone_enabled").default is True
        )
        assert (
            HeaderNavigation._meta.get_field("mobile_cta_button_enabled").default
            is True
        )

    def test_is_registered_setting(self):
        """Verify HeaderNavigation is a BaseSiteSetting subclass."""
        from wagtail.contrib.settings.models import BaseSiteSetting

        assert issubclass(HeaderNavigation, BaseSiteSetting)


# =============================================================================
# FooterNavigation Model Tests
# =============================================================================


class TestFooterNavigationModel:
    """Tests for FooterNavigation site settings model."""

    def test_model_has_required_fields(self):
        """Verify FooterNavigation has all required fields."""
        field_names = [f.name for f in FooterNavigation._meta.get_fields()]

        # Footer content fields
        assert "tagline" in field_names
        assert "link_sections" in field_names
        assert "auto_service_areas" in field_names

        # Social link fields
        assert "social_facebook" in field_names
        assert "social_instagram" in field_names
        assert "social_linkedin" in field_names
        assert "social_youtube" in field_names
        assert "social_x" in field_names

        # Copyright
        assert "copyright_text" in field_names

    def test_tagline_max_length(self):
        """Verify tagline has max_length of 255."""
        field = FooterNavigation._meta.get_field("tagline")
        assert field.max_length == 255

    def test_copyright_text_max_length(self):
        """Verify copyright_text has max_length of 255."""
        field = FooterNavigation._meta.get_field("copyright_text")
        assert field.max_length == 255

    def test_copyright_text_default(self):
        """Verify copyright_text has a sensible default with placeholders."""
        field = FooterNavigation._meta.get_field("copyright_text")
        assert "{year}" in field.default
        assert "{company_name}" in field.default

    def test_is_registered_setting(self):
        """Verify FooterNavigation is a BaseSiteSetting subclass."""
        from wagtail.contrib.settings.models import BaseSiteSetting

        assert issubclass(FooterNavigation, BaseSiteSetting)


# =============================================================================
# Menu Items StreamField Constraint Tests
# =============================================================================


class TestMenuItemsStreamBlock:
    """Tests for MenuItemsStreamBlock constraints (max 8)."""

    def test_max_num_is_8(self):
        """
        Verify MenuItemsStreamBlock has max_num of 8.

        AC: menu_items enforces max 8 top-level items.
        The constraint is enforced in the Wagtail editor UI and via the
        StreamBlock.clean() method when processing form submissions.
        """
        block = MenuItemsStreamBlock()
        assert block.meta.max_num == 8

    def test_has_item_child_block(self):
        """Verify MenuItemsStreamBlock has 'item' as the only child block type."""
        block = MenuItemsStreamBlock()
        child_block_names = list(block.child_blocks.keys())
        assert "item" in child_block_names


# =============================================================================
# Footer Sections StreamField Constraint Tests
# =============================================================================


class TestFooterSectionsStreamBlock:
    """Tests for FooterSectionsStreamBlock constraints (min 2, max 4)."""

    def test_min_num_is_2(self):
        """
        Verify FooterSectionsStreamBlock has min_num of 2.

        AC: link_sections rejects < 2 sections.
        """
        block = FooterSectionsStreamBlock()
        assert block.meta.min_num == 2

    def test_max_num_is_4(self):
        """
        Verify FooterSectionsStreamBlock has max_num of 4.

        AC: link_sections rejects > 4 sections.
        """
        block = FooterSectionsStreamBlock()
        assert block.meta.max_num == 4

    def test_has_section_child_block(self):
        """Verify FooterSectionsStreamBlock has 'section' as the only child block type."""
        block = FooterSectionsStreamBlock()
        child_block_names = list(block.child_blocks.keys())
        assert "section" in child_block_names


# =============================================================================
# Single Link StreamField Constraint Tests
# =============================================================================


class TestSingleLinkStreamBlock:
    """Tests for SingleLinkStreamBlock constraints (0-1 items)."""

    def test_max_num_is_1(self):
        """
        Verify SingleLinkStreamBlock has max_num of 1.

        AC: CTA link StreamFields reject > 1 item.
        """
        block = SingleLinkStreamBlock()
        assert block.meta.max_num == 1

    def test_min_num_is_0(self):
        """Verify SingleLinkStreamBlock has min_num of 0 (optional)."""
        block = SingleLinkStreamBlock()
        assert block.meta.min_num == 0

    def test_has_link_child_block(self):
        """Verify SingleLinkStreamBlock has 'link' as the only child block type."""
        block = SingleLinkStreamBlock()
        child_block_names = list(block.child_blocks.keys())
        assert "link" in child_block_names


# =============================================================================
# Site Uniqueness / Isolation Tests
# =============================================================================


class TestSiteUniqueness:
    """Tests for site-level uniqueness and isolation."""

    def test_header_navigation_per_site(self, default_site, second_site):
        """
        Verify HeaderNavigation maintains one instance per Site.

        AC: One settings instance per Site (BaseSiteSetting behavior).
        """
        # Clean up any existing settings for these sites
        HeaderNavigation.objects.filter(site=default_site).delete()
        HeaderNavigation.objects.filter(site=second_site).delete()

        # Get or create settings for default site
        settings1 = HeaderNavigation.objects.create(
            site=default_site,
            header_cta_text="Default Site CTA",
        )

        # Get or create settings for second site
        settings2 = HeaderNavigation.objects.create(
            site=second_site,
            header_cta_text="Second Site CTA",
        )

        # Verify they are different instances
        assert settings1.pk != settings2.pk
        assert settings1.header_cta_text == "Default Site CTA"
        assert settings2.header_cta_text == "Second Site CTA"

        # Verify site association
        assert settings1.site == default_site
        assert settings2.site == second_site

    def test_footer_navigation_per_site(self, default_site, second_site):
        """
        Verify FooterNavigation maintains one instance per Site.

        AC: One settings instance per Site (BaseSiteSetting behavior).
        """
        # Clean up any existing settings for these sites
        FooterNavigation.objects.filter(site=default_site).delete()
        FooterNavigation.objects.filter(site=second_site).delete()

        # Get or create settings for default site
        settings1 = FooterNavigation.objects.create(
            site=default_site,
            tagline="Default Site Tagline",
        )

        # Get or create settings for second site
        settings2 = FooterNavigation.objects.create(
            site=second_site,
            tagline="Second Site Tagline",
        )

        # Verify they are different instances
        assert settings1.pk != settings2.pk
        assert settings1.tagline == "Default Site Tagline"
        assert settings2.tagline == "Second Site Tagline"

    def test_different_sites_can_store_different_menu_counts(
        self, default_site, second_site
    ):
        """
        Verify different sites can store different header CTA text values.

        AC: Different Sites can store different configurations without overlap.
        """
        # Clean up any existing settings
        HeaderNavigation.objects.filter(site=default_site).delete()
        HeaderNavigation.objects.filter(site=second_site).delete()

        settings1 = HeaderNavigation.objects.create(
            site=default_site,
            header_cta_text="Site One CTA",
            mobile_cta_button_text="Call Site One",
        )

        settings2 = HeaderNavigation.objects.create(
            site=second_site,
            header_cta_text="Site Two CTA",
            mobile_cta_button_text="Call Site Two",
        )

        # Refresh from database
        settings1.refresh_from_db()
        settings2.refresh_from_db()

        # Verify different values
        assert settings1.header_cta_text == "Site One CTA"
        assert settings2.header_cta_text == "Site Two CTA"
        assert settings1.mobile_cta_button_text == "Call Site One"
        assert settings2.mobile_cta_button_text == "Call Site Two"


# =============================================================================
# Verbose Name Tests
# =============================================================================


class TestVerboseNames:
    """Tests for model verbose names (used in Wagtail admin)."""

    def test_header_navigation_verbose_name(self):
        """Verify HeaderNavigation has correct verbose_name."""
        assert HeaderNavigation._meta.verbose_name == "Header Navigation"

    def test_footer_navigation_verbose_name(self):
        """Verify FooterNavigation has correct verbose_name."""
        assert FooterNavigation._meta.verbose_name == "Footer Navigation"
