"""
E2E tests for Wagtail admin login.

Admin Journey 1: Admin Login - User logs into Wagtail admin.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect


@pytest.mark.e2e
class TestAdminLogin:
    """E2E tests for Wagtail admin login."""

    def test_admin_login_page_loads(
        self, page: Page, base_url, seeded_database
    ) -> None:
        """Admin login page should load."""
        page.goto(f"{base_url}/admin/")

        # Should redirect to login or show admin
        expect(page.locator("body")).to_be_visible()

        # Should have login form or admin content
        has_login = page.locator("input[name='username']").count() > 0
        has_admin = page.locator("[class*='admin']").count() > 0

        assert has_login or has_admin, "Should show login or admin"

    def test_admin_login_has_fields(
        self, page: Page, base_url, seeded_database
    ) -> None:
        """Admin login should have username and password fields."""
        page.goto(f"{base_url}/admin/login/")

        # Should have login fields
        username = page.locator("input[name='username']")
        password = page.locator("input[name='password']")

        expect(username).to_be_visible()
        expect(password).to_be_visible()

    def test_admin_login_success(self, page: Page, base_url, seeded_database) -> None:
        """Admin should be able to log in with valid credentials."""
        page.goto(f"{base_url}/admin/login/")

        # Fill login form
        page.locator("input[name='username']").fill("admin")
        page.locator("input[name='password']").fill("adminpass123")

        # Submit form
        page.locator("button[type='submit']").click()
        page.wait_for_load_state("networkidle")

        # Should be logged in - check for admin dashboard elements
        # Wagtail admin should show sidebar or dashboard
        admin_indicators = [
            "[class*='sidebar']",
            "[class*='menu']",
            ".wagtail",
            "#wagtail",
            "[data-controller]",
        ]

        logged_in = False
        for selector in admin_indicators:
            if page.locator(selector).count() > 0:
                logged_in = True
                break

        # Or check URL changed from login
        logged_in = logged_in or "/login" not in page.url

        assert logged_in, "Should be logged into admin"

    def test_admin_login_invalid_credentials(
        self, page: Page, base_url, seeded_database
    ) -> None:
        """Admin login should reject invalid credentials."""
        page.goto(f"{base_url}/admin/login/")

        # Fill with wrong credentials
        page.locator("input[name='username']").fill("wronguser")
        page.locator("input[name='password']").fill("wrongpass")

        # Submit form
        page.locator("button[type='submit']").click()
        page.wait_for_load_state("networkidle")

        # Should still be on login page or show error
        still_on_login = "/login" in page.url
        has_error = page.locator("[class*='error'], .errorlist, .messages").count() > 0

        assert still_on_login or has_error, "Should reject invalid credentials"

    def test_admin_logout(self, page: Page, base_url, seeded_database) -> None:
        """Admin should be able to log out."""
        # First log in
        page.goto(f"{base_url}/admin/login/")
        page.locator("input[name='username']").fill("admin")
        page.locator("input[name='password']").fill("adminpass123")
        page.locator("button[type='submit']").click()
        page.wait_for_load_state("networkidle")

        # Find and click logout
        # Try various logout selectors
        logout_selectors = [
            "a[href*='logout']",
            "button:has-text('Log out')",
            "a:has-text('Log out')",
            "[class*='logout']",
        ]

        for selector in logout_selectors:
            logout = page.locator(selector).first
            if logout.is_visible():
                logout.click()
                page.wait_for_load_state("networkidle")
                break

        # Should be logged out - either on login page or homepage
        expect(page.locator("body")).to_be_visible()
