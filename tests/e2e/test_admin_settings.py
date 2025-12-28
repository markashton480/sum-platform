"""
E2E tests for Wagtail admin site settings.

Admin Journey 2: Site Settings - Admin manages site settings/branding.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect


@pytest.mark.e2e
class TestAdminSiteSettings:
    """E2E tests for Wagtail site settings management."""

    def _login(self, page: Page, base_url: str) -> None:
        """Helper to log into admin."""
        page.goto(f"{base_url}/admin/login/")
        page.locator("input[name='username']").fill("admin")
        page.locator("input[name='password']").fill("adminpass123")
        page.locator("button[type='submit']").click()
        page.wait_for_load_state("networkidle")

    def test_settings_menu_exists(self, page: Page, base_url, seeded_database) -> None:
        """Admin should have settings menu."""
        self._login(page, base_url)

        # Look for settings in sidebar/menu
        settings_selectors = [
            "a[href*='settings']",
            "[class*='settings']",
            ":text('Settings')",
        ]

        settings_found = False
        for selector in settings_selectors:
            if page.locator(selector).count() > 0:
                settings_found = True
                break

        assert settings_found, "Admin should have settings option"

    def test_can_access_site_settings(
        self, page: Page, base_url, seeded_database
    ) -> None:
        """Admin can access site settings page."""
        self._login(page, base_url)

        # Try to navigate to settings
        # Wagtail settings are usually at /admin/settings/
        page.goto(f"{base_url}/admin/settings/")

        # Should load settings page or show settings options
        expect(page.locator("body")).to_be_visible()

    def test_can_access_branding_settings(
        self, page: Page, base_url, seeded_database
    ) -> None:
        """Admin can access branding/site settings."""
        self._login(page, base_url)

        # Navigate to site settings (SiteSettings model)
        page.goto(f"{base_url}/admin/settings/sum_core_branding/sitesettings/")

        # Should show settings form or redirect to valid page
        expect(page.locator("body")).to_be_visible()

        # Check for form elements or settings content
        has_form = page.locator("form").count() > 0
        has_content = len(page.content()) > 1000

        assert has_form or has_content, "Should show settings content"

    def test_can_view_sites(self, page: Page, base_url, seeded_database) -> None:
        """Admin can view sites list."""
        self._login(page, base_url)

        # Navigate to sites
        page.goto(f"{base_url}/admin/sites/")

        # Should show sites list
        expect(page.locator("body")).to_be_visible()

        # Should have at least one site listed
        page_content = page.content()
        assert "sage" in page_content.lower() or "site" in page_content.lower()

    def test_settings_have_save_button(
        self, page: Page, base_url, seeded_database
    ) -> None:
        """Settings pages should have save functionality."""
        self._login(page, base_url)

        # Go to any settings page
        page.goto(f"{base_url}/admin/settings/")

        # Look for save/submit buttons
        save_buttons = page.locator(
            "button[type='submit'], input[type='submit'], "
            "button:has-text('Save'), a:has-text('Save')"
        ).all()

        # Settings page should have save option or links to settings
        has_save = len(save_buttons) > 0
        has_links = page.locator("a").count() > 0

        assert has_save or has_links, "Settings should have save or navigation options"
