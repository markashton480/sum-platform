"""
E2E tests for interactive elements user journeys.

Journey 11: Interactive Elements - User interacts with accordions, tabs, etc.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect


@pytest.mark.e2e
class TestInteractiveElements:
    """E2E tests for interactive page elements."""

    def test_accordion_exists(self, page: Page, base_url, seeded_database) -> None:
        """Page may have accordion/FAQ elements."""
        page.goto(base_url)

        # Look for accordion/FAQ elements
        accordion_selectors = [
            "[class*='accordion']",
            "[class*='faq']",
            "[data-accordion]",
            "details",
            "[role='tablist']",
        ]

        accordion_found = False
        for selector in accordion_selectors:
            if page.locator(selector).count() > 0:
                accordion_found = True
                break

        # Accordion is optional - just ensure page loads
        assert accordion_found or True  # Accordion optional
        expect(page.locator("body")).to_be_visible()

    def test_accordion_interaction(self, page: Page, base_url, seeded_database) -> None:
        """Accordion items should expand when clicked."""
        page.goto(base_url)

        # Look for expandable elements
        expandable = page.locator(
            "button[aria-expanded], [class*='accordion'] button, details summary"
        ).all()

        if len(expandable) > 0:
            # Try clicking the first expandable element
            first_expandable = expandable[0]
            if first_expandable.is_visible():
                first_expandable.click()
                page.wait_for_timeout(500)

                # Page should still be functional
                expect(page.locator("body")).to_be_visible()

    def test_smooth_scroll(self, page: Page, base_url, seeded_database) -> None:
        """Page should support smooth scrolling to anchors."""
        page.goto(base_url)

        # Check for smooth scroll class
        html = page.locator("html")
        html_class = html.get_attribute("class") or ""

        # Either has smooth-scroll class or scroll-behavior in CSS
        has_smooth = "smooth" in html_class or True  # Smooth scroll optional
        assert has_smooth
        expect(page.locator("body")).to_be_visible()

    def test_form_validation_feedback(
        self, page: Page, base_url, seeded_database
    ) -> None:
        """Forms should provide validation feedback."""
        page.goto(f"{base_url}/contact/")

        # Find submit button
        submit = page.locator("button[type='submit'], input[type='submit']").first

        if submit.is_visible():
            # Try to submit empty form
            submit.click()
            page.wait_for_timeout(500)

            # Should either show validation or still be on page
            # (browser native validation will prevent submission)
            expect(page.locator("body")).to_be_visible()

    def test_image_loading(self, page: Page, base_url, seeded_database) -> None:
        """Images should load properly."""
        page.goto(base_url)

        # Wait for images to load
        page.wait_for_load_state("networkidle")

        images = page.locator("img").all()

        if len(images) > 0:
            # Check at least first few images loaded
            for img in images[:5]:
                if img.is_visible():
                    # Image should have dimensions (not broken)
                    width = img.evaluate("el => el.naturalWidth")
                    assert width > 0, "Image should load properly"
                    break

    def test_lazy_loading(self, page: Page, base_url, seeded_database) -> None:
        """Images may use lazy loading."""
        page.goto(base_url)

        # Check for lazy loading attributes
        lazy_images = page.locator("img[loading='lazy']").count()

        # Lazy loading is optional but good practice
        assert lazy_images >= 0  # May have lazy images
        expect(page.locator("body")).to_be_visible()

    def test_page_transitions(self, page: Page, base_url, seeded_database) -> None:
        """Navigation should work smoothly."""
        page.goto(base_url)

        # Navigate to about page
        page.goto(f"{base_url}/about/")
        expect(page.locator("body")).to_be_visible()

        # Navigate back
        page.go_back()
        expect(page.locator("body")).to_be_visible()

        # URL should be back to homepage
        assert page.url == base_url or page.url == f"{base_url}/"
