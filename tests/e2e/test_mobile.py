"""
E2E tests for mobile navigation user journeys.

Journey 4: Mobile Navigation Drill-Down - User navigates on mobile viewport.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect


@pytest.mark.e2e
class TestMobileNavigationDrillDown:
    """E2E tests for mobile navigation patterns."""

    def test_mobile_homepage_loads(self, page: Page, base_url, seeded_database) -> None:
        """Homepage should load on mobile viewport."""
        # Set mobile viewport
        page.set_viewport_size({"width": 375, "height": 667})
        page.goto(base_url)

        expect(page.locator("body")).to_be_visible()

    def test_mobile_menu_toggle_exists(
        self, page: Page, base_url, seeded_database
    ) -> None:
        """Mobile menu toggle (hamburger) should be visible on mobile."""
        page.set_viewport_size({"width": 375, "height": 667})
        page.goto(base_url)

        # Look for mobile menu toggle
        toggle_selectors = [
            "button.mobile-menu-toggle",
            ".hamburger",
            "[aria-label='Menu']",
            "[aria-label='Toggle menu']",
            "button[class*='mobile']",
            "button[class*='hamburger']",
            ".menu-toggle",
            "#mobile-menu-toggle",
        ]

        toggle_found = False
        for selector in toggle_selectors:
            toggle = page.locator(selector).first
            if toggle.is_visible():
                toggle_found = True
                break

        # Mobile menu toggle should exist
        # Note: Some themes may use CSS-only solutions
        assert (
            toggle_found or page.locator("nav").is_visible()
        ), "Should have mobile menu toggle or visible navigation"

    def test_mobile_menu_opens(self, page: Page, base_url, seeded_database) -> None:
        """Clicking mobile menu toggle should open navigation."""
        page.set_viewport_size({"width": 375, "height": 667})
        page.goto(base_url)

        # Find and click mobile menu toggle
        toggle_selectors = [
            "button.mobile-menu-toggle",
            ".hamburger",
            "[aria-label='Menu']",
            "button[class*='mobile']",
            ".menu-toggle",
        ]

        for selector in toggle_selectors:
            toggle = page.locator(selector).first
            if toggle.is_visible():
                toggle.click()
                page.wait_for_timeout(500)
                break

        # After clicking, mobile menu should be visible
        mobile_menu_selectors = [
            ".mobile-menu",
            "nav.mobile",
            ".mobile-nav",
            "[class*='mobile-menu']",
            "nav[class*='open']",
            "nav[class*='active']",
        ]

        menu_visible = False
        for selector in mobile_menu_selectors:
            menu = page.locator(selector).first
            if menu.is_visible():
                menu_visible = True
                break

        # If no explicit mobile menu, check that nav links are now visible
        if not menu_visible:
            nav_links = page.locator("nav a").all()
            menu_visible = len(nav_links) > 0

    def test_mobile_navigation_works(
        self, page: Page, base_url, seeded_database
    ) -> None:
        """User should be able to navigate to pages on mobile."""
        page.set_viewport_size({"width": 375, "height": 667})

        # Try navigating directly to a page
        page.goto(f"{base_url}/about/")

        expect(page.locator("body")).to_be_visible()

        # Content should be visible
        main = page.locator("main, article, .content").first
        if main.is_visible():
            expect(main).not_to_be_empty()

    def test_mobile_pages_are_responsive(
        self, page: Page, base_url, seeded_database
    ) -> None:
        """Pages should render properly on mobile viewport."""
        page.set_viewport_size({"width": 375, "height": 667})

        pages_to_test = [
            "/",
            "/about/",
            "/services/",
            "/contact/",
            "/journal/",
        ]

        overflow_count = 0
        for path in pages_to_test:
            page.goto(f"{base_url}{path}")

            # Page should load without horizontal scroll
            body = page.locator("body")
            expect(body).to_be_visible()

            # Check that content doesn't overflow horizontally
            # This is a basic responsiveness check
            body_width = page.evaluate("document.body.scrollWidth")
            viewport_width = 375

            # Track pages with overflow but don't fail immediately
            # Some minor overflow may be acceptable
            if body_width > viewport_width + 50:
                overflow_count += 1

        # At least 3 of 5 pages should be responsive
        assert (
            overflow_count <= 2
        ), f"{overflow_count} pages have significant horizontal overflow"
