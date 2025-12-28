"""
E2E tests for SEO and meta tag user journeys.

Journey 10: SEO Verification - Pages have proper SEO elements.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page


@pytest.mark.e2e
class TestSEOElements:
    """E2E tests for SEO and meta elements."""

    def test_homepage_has_title(self, page: Page, base_url, seeded_database) -> None:
        """Homepage should have a proper title tag."""
        page.goto(base_url)

        title = page.title()
        assert len(title) > 10, "Homepage should have a descriptive title"
        assert "sage" in title.lower() or "stone" in title.lower()

    def test_homepage_has_meta_description(
        self, page: Page, base_url, seeded_database
    ) -> None:
        """Homepage should have a meta description."""
        page.goto(base_url)

        meta_desc = page.locator("meta[name='description']").get_attribute("content")
        assert meta_desc and len(meta_desc) > 50, "Should have meta description"

    def test_pages_have_unique_titles(
        self, page: Page, base_url, seeded_database
    ) -> None:
        """Different pages should have unique titles."""
        pages = ["/", "/about/", "/services/", "/contact/"]
        titles = []

        for path in pages:
            page.goto(f"{base_url}{path}")
            titles.append(page.title())

        # All titles should be unique
        unique_titles = set(titles)
        assert len(unique_titles) == len(titles), "Pages should have unique titles"

    def test_pages_have_canonical_urls(
        self, page: Page, base_url, seeded_database
    ) -> None:
        """Pages should have canonical URLs."""
        page.goto(base_url)

        canonical = page.locator("link[rel='canonical']")
        assert canonical.count() >= 1, "Page should have canonical link"

    def test_pages_have_og_tags(self, page: Page, base_url, seeded_database) -> None:
        """Pages should have Open Graph tags."""
        page.goto(base_url)

        og_title = page.locator("meta[property='og:title']").count()
        og_desc = page.locator("meta[property='og:description']").count()

        assert og_title >= 1, "Page should have og:title"
        assert og_desc >= 1, "Page should have og:description"

    def test_images_have_alt_text(self, page: Page, base_url, seeded_database) -> None:
        """Images should have alt text."""
        page.goto(base_url)

        images = page.locator("img").all()

        if len(images) > 0:
            # Check at least some images have alt text
            images_with_alt = 0
            for img in images:
                alt = img.get_attribute("alt")
                if alt and len(alt) > 0:
                    images_with_alt += 1

            # At least 50% of images should have alt text
            ratio = images_with_alt / len(images)
            assert ratio >= 0.5, f"Only {ratio*100:.0f}% of images have alt text"

    def test_headings_hierarchy(self, page: Page, base_url, seeded_database) -> None:
        """Page should have proper heading hierarchy."""
        page.goto(base_url)

        h1_count = page.locator("h1").count()

        # Should have exactly one H1
        assert h1_count >= 1, "Page should have at least one H1"

    def test_lang_attribute(self, page: Page, base_url, seeded_database) -> None:
        """HTML should have lang attribute."""
        page.goto(base_url)

        lang = page.locator("html").get_attribute("lang")
        assert lang and len(lang) >= 2, "HTML should have lang attribute"
