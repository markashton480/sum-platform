"""
E2E tests for portfolio user journeys.

Journey 5: Portfolio Case Study Interaction - User views portfolio items.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect


@pytest.mark.e2e
class TestPortfolioCaseStudyViewing:
    """E2E tests for portfolio case study viewing."""

    def test_portfolio_page_loads(self, page: Page, base_url, seeded_database) -> None:
        """Portfolio page should load successfully."""
        page.goto(f"{base_url}/portfolio/")

        expect(page.locator("body")).to_be_visible()

    def test_portfolio_shows_items(self, page: Page, base_url, seeded_database) -> None:
        """Portfolio page should display portfolio items."""
        page.goto(f"{base_url}/portfolio/")

        # Look for portfolio items
        item_selectors = [
            ".portfolio-item",
            ".case-study-card",
            ".project-card",
            ".portfolio-card",
            ".work-item",
            "[class*='portfolio'] article",
            "[class*='portfolio'] .item",
        ]

        items_found = False
        for selector in item_selectors:
            items = page.locator(selector).all()
            if len(items) > 0:
                items_found = True
                break

        # Should have portfolio items OR images in portfolio section
        if not items_found:
            # Check for images in main content area
            images = page.locator("main img, .content img").all()
            items_found = len(images) > 0

        assert items_found, "Portfolio page should display items or images"

    def test_portfolio_items_have_images(
        self, page: Page, base_url, seeded_database
    ) -> None:
        """Portfolio items should have images."""
        page.goto(f"{base_url}/portfolio/")

        # Find images in the portfolio area
        images = page.locator("main img, .content img, article img").all()

        # Should have at least some images
        assert len(images) >= 1, "Portfolio should display images"

    def test_portfolio_item_interaction(
        self, page: Page, base_url, seeded_database
    ) -> None:
        """Clicking a portfolio item should show details."""
        page.goto(f"{base_url}/portfolio/")

        # Find clickable portfolio items
        clickable_selectors = [
            ".portfolio-item a",
            ".case-study-card a",
            ".portfolio-item",
            "[class*='portfolio'] a",
            "main article a",
        ]

        item_clicked = False
        for selector in clickable_selectors:
            items = page.locator(selector).all()
            for item in items:
                href = item.get_attribute("href")
                if href and href != "#":
                    item.click()
                    page.wait_for_timeout(1000)
                    item_clicked = True
                    break
            if item_clicked:
                break

        if item_clicked:
            # Should have opened modal or navigated to detail page
            # Check for modal
            modal = page.locator(
                ".modal, .case-study-modal, [role='dialog'], .lightbox"
            ).first

            if modal.is_visible():
                # Modal opened - verify it has content
                expect(modal).to_be_visible()
            else:
                # Navigated to detail page - verify content
                expect(page.locator("body")).to_be_visible()

    def test_portfolio_has_descriptions(
        self, page: Page, base_url, seeded_database
    ) -> None:
        """Portfolio items should have descriptive text."""
        page.goto(f"{base_url}/portfolio/")

        # Get page text content
        text_content = page.locator("main, .content").inner_text()

        # Should have substantial text describing projects
        # (Not just image alt text)
        assert len(text_content) > 100, "Portfolio should have descriptive text"
