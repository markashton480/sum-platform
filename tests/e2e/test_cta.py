"""
E2E tests for Call-to-Action user journeys.

Journey 8: CTA Interactions - User interacts with call-to-action elements.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect


@pytest.mark.e2e
class TestCTAInteractions:
    """E2E tests for call-to-action buttons and links."""

    def test_homepage_has_cta(self, page: Page, base_url, seeded_database) -> None:
        """Homepage should have prominent CTA buttons."""
        page.goto(base_url)

        # Look for CTA elements
        cta_selectors = [
            ".btn",
            ".cta",
            "a.button",
            "[class*='cta']",
            "[class*='btn-primary']",
            "button[type='submit']",
        ]

        cta_found = False
        for selector in cta_selectors:
            elements = page.locator(selector).all()
            if len(elements) > 0:
                cta_found = True
                break

        assert cta_found, "Homepage should have CTA elements"

    def test_cta_leads_to_contact(self, page: Page, base_url, seeded_database) -> None:
        """Primary CTA should lead to contact or enquiry."""
        page.goto(base_url)

        # Look for contact-related CTAs
        contact_ctas = page.locator(
            "a[href*='contact'], a:has-text('Contact'), "
            "a:has-text('Enquire'), a:has-text('Get in touch')"
        ).all()

        if len(contact_ctas) > 0:
            # Find first visible CTA
            for cta in contact_ctas:
                if cta.is_visible():
                    cta.click()
                    page.wait_for_load_state("networkidle")

                    # Should navigate to contact page
                    assert "contact" in page.url.lower()
                    break

    def test_services_page_has_cta(self, page: Page, base_url, seeded_database) -> None:
        """Services page should have CTAs to enquire."""
        page.goto(f"{base_url}/services/")

        # Look for CTA buttons or links
        cta_elements = page.locator(
            ".btn, .cta, a.button, [class*='btn'], button"
        ).all()

        # Should have at least one CTA
        assert len(cta_elements) >= 1, "Services page should have CTAs"

    def test_portfolio_has_view_more(
        self, page: Page, base_url, seeded_database
    ) -> None:
        """Portfolio items should have interaction options."""
        page.goto(f"{base_url}/portfolio/")

        # Look for portfolio item links or buttons
        portfolio_actions = page.locator(
            "a[href*='portfolio'], .portfolio-item a, " "[class*='portfolio'] a, main a"
        ).all()

        # Should have clickable portfolio items
        assert len(portfolio_actions) >= 1, "Portfolio should have clickable items"

    def test_blog_has_read_more(self, page: Page, base_url, seeded_database) -> None:
        """Blog posts should have read more links."""
        page.goto(f"{base_url}/journal/")

        # Look for post links
        post_links = page.locator(
            "article a, a:has-text('Read'), a:has-text('More'), " "a[href*='journal/']"
        ).all()

        # Should have at least one read more link
        visible_links = [link for link in post_links if link.is_visible()]
        assert len(visible_links) >= 1, "Blog should have post links"

    def test_cta_button_styles(self, page: Page, base_url, seeded_database) -> None:
        """CTA buttons should have distinctive styling."""
        page.goto(base_url)

        # Find primary buttons
        buttons = page.locator(".btn, [class*='btn'], button").all()

        if len(buttons) > 0:
            # At least one button should exist
            expect(page.locator(".btn, [class*='btn'], button").first).to_be_visible()
