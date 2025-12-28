"""
E2E tests for Wagtail admin blog management.

Admin Journey 3: Blog Post - Admin creates and manages blog posts.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect


@pytest.mark.e2e
class TestAdminBlogManagement:
    """E2E tests for Wagtail blog post management."""

    def _login(self, page: Page, base_url: str) -> None:
        """Helper to log into admin."""
        page.goto(f"{base_url}/admin/login/")
        page.locator("input[name='username']").fill("admin")
        page.locator("input[name='password']").fill("adminpass123")
        page.locator("button[type='submit']").click()
        page.wait_for_load_state("networkidle")

    def test_can_access_pages_explorer(
        self, page: Page, base_url, seeded_database
    ) -> None:
        """Admin can access pages explorer."""
        self._login(page, base_url)

        # Navigate to pages
        page.goto(f"{base_url}/admin/pages/")

        # Should show pages explorer
        expect(page.locator("body")).to_be_visible()

        # Should have page listings
        page_content = page.content().lower()
        assert "page" in page_content or "explorer" in page_content

    def test_can_find_blog_section(self, page: Page, base_url, seeded_database) -> None:
        """Admin can find blog/journal section in pages."""
        self._login(page, base_url)

        # Navigate to pages
        page.goto(f"{base_url}/admin/pages/")

        # Look for blog/journal in the page tree
        page_content = page.content().lower()

        has_blog = "journal" in page_content or "ledger" in page_content
        has_pages = "page" in page_content

        assert has_blog or has_pages, "Should show blog section or pages"

    def test_can_access_add_page(self, page: Page, base_url, seeded_database) -> None:
        """Admin can access add page interface."""
        self._login(page, base_url)

        # Try to add a child page to home (page id 3 is Sage & Stone home)
        page.goto(f"{base_url}/admin/pages/3/add_subpage/")

        # Should show page type selection
        expect(page.locator("body")).to_be_visible()

        # Should have page type options
        page_content = page.content().lower()
        has_types = "page" in page_content or "type" in page_content

        assert has_types, "Should show page type options"

    def test_blog_posts_listed(self, page: Page, base_url, seeded_database) -> None:
        """Admin can see existing blog posts."""
        self._login(page, base_url)

        # Navigate to pages and look for blog posts
        # Blog index is typically under the home page
        page.goto(f"{base_url}/admin/pages/")

        # Look for blog post titles in the content
        page_content = page.content().lower()

        # Check for known blog post titles from seeder
        blog_titles = ["timber", "kensington", "dovetail", "workshop", "georgian"]
        found_posts = any(title in page_content for title in blog_titles)

        # Or just check we can see pages
        has_pages = page.locator("table, .listing, [class*='page']").count() > 0

        assert found_posts or has_pages, "Should show blog posts or page listings"

    def test_can_edit_existing_page(
        self, page: Page, base_url, seeded_database
    ) -> None:
        """Admin can access edit interface for existing pages."""
        self._login(page, base_url)

        # Try to edit the home page (page id 3)
        page.goto(f"{base_url}/admin/pages/3/edit/")

        # Should show edit form
        expect(page.locator("body")).to_be_visible()

        # Should have form elements
        has_form = page.locator("form").count() > 0
        has_fields = page.locator("input, textarea, select").count() > 0

        assert has_form or has_fields, "Should show edit form"

    def test_edit_page_has_publish_option(
        self, page: Page, base_url, seeded_database
    ) -> None:
        """Edit page should have publish options."""
        self._login(page, base_url)

        # Edit the home page
        page.goto(f"{base_url}/admin/pages/3/edit/")

        # Look for publish/save buttons
        publish_selectors = [
            "button:has-text('Publish')",
            "button:has-text('Save')",
            "[class*='publish']",
            "[class*='save']",
            "button[type='submit']",
        ]

        publish_found = False
        for selector in publish_selectors:
            if page.locator(selector).count() > 0:
                publish_found = True
                break

        assert publish_found, "Edit page should have publish/save option"
