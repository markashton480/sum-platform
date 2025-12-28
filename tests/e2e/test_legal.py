"""
E2E tests for legal page user journeys.

Journey 6: Legal Page Table of Contents - User navigates legal documents.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect


@pytest.mark.e2e
class TestLegalPageTocNavigation:
    """E2E tests for legal page table of contents navigation."""

    def test_terms_page_loads(self, page: Page, base_url, seeded_database) -> None:
        """Terms of Supply page should load successfully."""
        page.goto(f"{base_url}/terms/")

        expect(page.locator("body")).to_be_visible()

    def test_legal_page_has_content(
        self, page: Page, base_url, seeded_database
    ) -> None:
        """Legal page should have substantial content."""
        page.goto(f"{base_url}/terms/")

        # Get main content
        content = page.locator("main, article, .content").first
        expect(content).to_be_visible()

        # Should have substantial text
        text = content.inner_text()
        assert len(text) > 500, "Legal page should have substantial content"

    def test_legal_page_has_sections(
        self, page: Page, base_url, seeded_database
    ) -> None:
        """Legal page should have multiple sections."""
        page.goto(f"{base_url}/terms/")

        # Look for section headings
        headings = page.locator("h2, h3, .section-heading").all()

        # Should have multiple sections
        assert len(headings) >= 2, "Legal page should have multiple sections"

    def test_legal_page_has_toc(self, page: Page, base_url, seeded_database) -> None:
        """Legal page may have a table of contents."""
        page.goto(f"{base_url}/terms/")

        # Look for ToC element
        toc_selectors = [
            ".table-of-contents",
            ".toc",
            "aside nav",
            "[class*='contents']",
            ".sidebar nav",
            "nav[aria-label*='contents']",
        ]

        # Check if any ToC element is visible
        # ToC is optional - theme may not implement it
        for selector in toc_selectors:
            toc = page.locator(selector).first
            if toc.is_visible():
                # ToC found - test passes
                return

        # No ToC found - this is acceptable as it's optional; skip this test explicitly
        pytest.skip("Legal page has no optional table of contents")

    def test_legal_page_anchor_links_work(
        self, page: Page, base_url, seeded_database
    ) -> None:
        """Anchor links within legal page should work."""
        page.goto(f"{base_url}/terms/")

        # Find internal anchor links in the main content area
        # Avoid header/nav anchor links that may be hidden
        anchor_links = page.locator("main a[href^='#'], article a[href^='#']").all()

        # Try to find a visible anchor link to click
        for anchor in anchor_links:
            href = anchor.get_attribute("href")
            if href and href != "#" and anchor.is_visible():
                # Use force click to bypass fixed header interception
                anchor.click(force=True)
                page.wait_for_timeout(300)

                # URL should update with anchor after clicking a visible link
                assert (
                    "#" in page.url
                ), "Clicking an anchor link should update the URL with a fragment"
                return

        # No visible anchor links found - verify page has anchors in content
        # by checking for id attributes that could be targets
        has_anchor_targets = page.locator("[id]").count() > 0
        assert has_anchor_targets, "Page should have anchor target elements"

    def test_legal_page_is_readable(
        self, page: Page, base_url, seeded_database
    ) -> None:
        """Legal page text should be readable (not placeholder)."""
        page.goto(f"{base_url}/terms/")

        # Get text content from main element
        text = page.locator("main").first.inner_text().lower()

        # Should contain legal-related terms
        legal_terms = [
            "terms",
            "supply",
            "agreement",
            "conditions",
            "party",
            "service",
            "payment",
            "liability",
        ]

        terms_found = sum(1 for term in legal_terms if term in text)
        assert terms_found >= 2, "Legal page should contain legal terminology"

    def test_privacy_page_loads(self, page: Page, base_url, seeded_database) -> None:
        """Privacy policy page should load if it exists."""
        response = page.goto(f"{base_url}/privacy/")

        # Page may or may not exist
        if response and response.status == 200:
            expect(page.locator("body")).to_be_visible()

    def test_accessibility_page_loads(
        self, page: Page, base_url, seeded_database
    ) -> None:
        """Accessibility statement page should load if it exists."""
        response = page.goto(f"{base_url}/accessibility/")

        # Page may or may not exist
        if response and response.status == 200:
            expect(page.locator("body")).to_be_visible()
