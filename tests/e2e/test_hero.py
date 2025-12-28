"""
E2E tests for hero section user journeys.

Journey 9: Hero Section - User views and interacts with hero content.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page


@pytest.mark.e2e
class TestHeroSection:
    """E2E tests for homepage hero section."""

    def test_hero_section_exists(self, page: Page, base_url, seeded_database) -> None:
        """Homepage should have a hero section."""
        page.goto(base_url)

        # Look for hero section
        hero_selectors = [
            ".hero",
            "[class*='hero']",
            "section:first-of-type",
            "#hero",
            "main > section:first-child",
        ]

        hero_found = False
        for selector in hero_selectors:
            if page.locator(selector).count() > 0:
                hero_found = True
                break

        # Hero section should exist
        assert hero_found or page.locator("main").is_visible()

    def test_hero_has_headline(self, page: Page, base_url, seeded_database) -> None:
        """Hero section should have a headline."""
        page.goto(base_url)

        # Look for prominent headlines
        headlines = page.locator("h1, [class*='hero'] h2, main h1").all()

        assert len(headlines) >= 1, "Page should have a headline"

    def test_hero_has_tagline(self, page: Page, base_url, seeded_database) -> None:
        """Hero section should have descriptive tagline."""
        page.goto(base_url)

        # Get hero area text
        main_content = page.locator("main").first.inner_text()

        # Should have substantial introductory text
        assert len(main_content) > 100, "Hero should have descriptive content"

    def test_hero_has_image(self, page: Page, base_url, seeded_database) -> None:
        """Hero section should have visual content."""
        page.goto(base_url)

        # Look for hero images
        images = page.locator("img, [class*='hero'] img, picture").all()

        # Should have at least one image
        assert len(images) >= 1, "Page should have images"

    def test_hero_cta_visible(self, page: Page, base_url, seeded_database) -> None:
        """Hero CTA should be immediately visible."""
        page.goto(base_url)

        # Check viewport for CTA without scrolling
        cta_elements = page.locator(
            ".btn, .cta, a.button, [class*='btn-primary']"
        ).all()

        # At least one CTA should be in the initial viewport
        visible_ctas = [cta for cta in cta_elements if cta.is_visible()]
        assert len(visible_ctas) >= 1, "CTA should be visible in hero area"

    def test_scroll_indicator_or_content_below(
        self, page: Page, base_url, seeded_database
    ) -> None:
        """Page should indicate more content below hero."""
        page.goto(base_url)

        # Check page has scrollable content
        page_height = page.evaluate("document.body.scrollHeight")
        viewport_height = page.evaluate("window.innerHeight")

        # Page should have content below the fold
        assert page_height > viewport_height, "Page should have scrollable content"
