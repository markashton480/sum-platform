"""
E2E tests for footer navigation user journeys.

Journey 7: Footer Navigation - User navigates via footer links.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect


@pytest.mark.e2e
class TestFooterNavigation:
    """E2E tests for footer navigation."""

    def test_footer_exists(self, page: Page, base_url, seeded_database) -> None:
        """Footer should be present on all pages."""
        page.goto(base_url)

        footer = page.locator("footer").first
        expect(footer).to_be_visible()

    def test_footer_has_brand_info(self, page: Page, base_url, seeded_database) -> None:
        """Footer should contain brand information."""
        page.goto(base_url)

        footer = page.locator("footer").first
        footer_text = footer.inner_text().lower()

        # Should have brand name or tagline
        assert "sage" in footer_text or "stone" in footer_text

    def test_footer_has_navigation_links(
        self, page: Page, base_url, seeded_database
    ) -> None:
        """Footer should have navigation links."""
        page.goto(base_url)

        footer_links = page.locator("footer a[href]").all()

        # Should have multiple footer links
        assert len(footer_links) >= 3, "Footer should have at least 3 links"

    def test_footer_links_work(self, page: Page, base_url, seeded_database) -> None:
        """Footer links should navigate to valid pages."""
        page.goto(base_url)

        # Find footer links
        footer_links = page.locator("footer a[href]").all()

        # Try clicking a visible internal link
        for link in footer_links:
            href = link.get_attribute("href")
            if (
                href
                and not href.startswith("mailto:")
                and not href.startswith("tel:")
                and not href.startswith("#")
                and link.is_visible()
            ):
                # Navigate to the link
                link.click()
                page.wait_for_load_state("networkidle")

                # Should load a valid page
                expect(page.locator("body")).to_be_visible()
                break

    def test_footer_has_contact_info(
        self, page: Page, base_url, seeded_database
    ) -> None:
        """Footer should have contact information."""
        page.goto(base_url)

        footer = page.locator("footer").first
        footer_text = footer.inner_text().lower()

        # Should have some contact indicator
        contact_indicators = ["contact", "email", "phone", "address", "@", "tel"]
        has_contact = any(ind in footer_text for ind in contact_indicators)

        # Footer may have contact info or link to contact page
        footer_links = page.locator("footer a[href*='contact']").count()
        assert has_contact or footer_links > 0, "Footer should have contact info"

    def test_footer_has_legal_links(
        self, page: Page, base_url, seeded_database
    ) -> None:
        """Footer should have legal page links."""
        page.goto(base_url)

        # Look for legal links in footer
        legal_patterns = ["terms", "privacy", "cookie", "legal", "accessibility"]

        footer_links = page.locator("footer a[href]").all()
        legal_links_found = 0

        for link in footer_links:
            href = (link.get_attribute("href") or "").lower()
            text = link.inner_text().lower()
            if any(pattern in href or pattern in text for pattern in legal_patterns):
                legal_links_found += 1

        # Should have at least one legal link
        assert legal_links_found >= 1, "Footer should have at least one legal link"

    def test_footer_social_links(self, page: Page, base_url, seeded_database) -> None:
        """Footer may have social media links."""
        page.goto(base_url)

        # Social links are optional; this test only ensures the footer is visible
        expect(page.locator("footer")).to_be_visible()
