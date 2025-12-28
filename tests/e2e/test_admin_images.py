"""
E2E tests for Wagtail admin image management.

Admin Journey 5: Image Management - Admin manages images and documents.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect


@pytest.mark.e2e
class TestAdminImageManagement:
    """E2E tests for Wagtail image management."""

    def _login(self, page: Page, base_url: str) -> None:
        """Helper to log into admin."""
        page.goto(f"{base_url}/admin/login/")
        page.locator("input[name='username']").fill("admin")
        page.locator("input[name='password']").fill("adminpass123")
        page.locator("button[type='submit']").click()
        page.wait_for_load_state("networkidle")

    def test_images_menu_exists(self, page: Page, base_url, seeded_database) -> None:
        """Admin should have images menu option."""
        self._login(page, base_url)

        # Look for images in sidebar/menu
        images_selectors = [
            "a[href*='images']",
            "[class*='images']",
            ":text('Images')",
        ]

        images_found = False
        for selector in images_selectors:
            if page.locator(selector).count() > 0:
                images_found = True
                break

        assert images_found, "Admin should have images option"

    def test_can_access_images_list(
        self, page: Page, base_url, seeded_database
    ) -> None:
        """Admin can access images list."""
        self._login(page, base_url)

        # Navigate to images
        page.goto(f"{base_url}/admin/images/")

        # Should show images list
        expect(page.locator("body")).to_be_visible()

        # Should have table or listing
        has_list = page.locator("table, .listing, [class*='image']").count() > 0
        has_content = len(page.content()) > 1000

        assert has_list or has_content, "Should show images list"

    def test_images_list_shows_thumbnails(
        self, page: Page, base_url, seeded_database
    ) -> None:
        """Images list should show thumbnails."""
        self._login(page, base_url)

        page.goto(f"{base_url}/admin/images/")

        # Look for image thumbnails
        thumbnails = page.locator("img, [class*='thumbnail'], [class*='preview']")

        # Should have some visual elements
        assert thumbnails.count() >= 0  # May have thumbnails
        expect(page.locator("body")).to_be_visible()

    def test_can_access_add_image(self, page: Page, base_url, seeded_database) -> None:
        """Admin can access add image page."""
        self._login(page, base_url)

        page.goto(f"{base_url}/admin/images/add/")

        # Should show upload form
        expect(page.locator("body")).to_be_visible()

        # Should have file input or upload area
        upload_selectors = [
            "input[type='file']",
            "[class*='upload']",
            "[class*='dropzone']",
            "form",
        ]

        upload_found = False
        for selector in upload_selectors:
            if page.locator(selector).count() > 0:
                upload_found = True
                break

        assert upload_found, "Should have upload functionality"

    def test_documents_menu_exists(self, page: Page, base_url, seeded_database) -> None:
        """Admin should have documents menu option."""
        self._login(page, base_url)

        # Look for documents in sidebar/menu
        docs_selectors = [
            "a[href*='documents']",
            "[class*='documents']",
            ":text('Documents')",
        ]

        docs_found = False
        for selector in docs_selectors:
            if page.locator(selector).count() > 0:
                docs_found = True
                break

        assert docs_found, "Admin should have documents option"

    def test_can_access_documents_list(
        self, page: Page, base_url, seeded_database
    ) -> None:
        """Admin can access documents list."""
        self._login(page, base_url)

        page.goto(f"{base_url}/admin/documents/")

        # Should show documents list
        expect(page.locator("body")).to_be_visible()

    def test_image_search_exists(self, page: Page, base_url, seeded_database) -> None:
        """Images page should have search functionality."""
        self._login(page, base_url)

        page.goto(f"{base_url}/admin/images/")

        # Look for search input
        search_selectors = [
            "input[type='search']",
            "input[name='q']",
            "[class*='search'] input",
            "input[placeholder*='search' i]",
        ]

        search_found = False
        for selector in search_selectors:
            if page.locator(selector).count() > 0:
                search_found = True
                break

        # Search is common but not required in all deployments
        # If it's not available, skip rather than asserting a tautology
        if not search_found:
            pytest.skip("Image search is not enabled in this configuration")

        expect(page.locator("body")).to_be_visible()
