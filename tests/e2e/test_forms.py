"""
E2E tests for form submission user journeys.

Journey 3: Contact Form Submission - User submits contact form.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect


@pytest.mark.e2e
class TestContactFormSubmission:
    """E2E tests for contact form submission."""

    def test_contact_page_loads(self, page: Page, base_url, seeded_database) -> None:
        """Contact page should load successfully."""
        page.goto(f"{base_url}/contact/")

        expect(page.locator("body")).to_be_visible()

    def test_contact_form_exists(self, page: Page, base_url, seeded_database) -> None:
        """Contact page should have a form."""
        page.goto(f"{base_url}/contact/")

        # Look for form element
        form = page.locator("form").first
        expect(form).to_be_visible()

    def test_contact_form_has_required_fields(
        self, page: Page, base_url, seeded_database
    ) -> None:
        """Contact form should have name, email, and message fields."""
        page.goto(f"{base_url}/contact/")

        # Check for common form fields
        # Email field
        email_field = page.locator(
            "input[name='email'], input[type='email'], input[id*='email']"
        ).first

        # Message field
        message_field = page.locator(
            "textarea[name='message'], textarea[name='enquiry'], "
            "textarea[id*='message'], textarea"
        ).first

        # At least email and message should exist
        expect(email_field).to_be_visible()
        expect(message_field).to_be_visible()

    def test_contact_form_has_submit_button(
        self, page: Page, base_url, seeded_database
    ) -> None:
        """Contact form should have a submit button."""
        page.goto(f"{base_url}/contact/")

        # Look for submit button
        submit_button = page.locator(
            "button[type='submit'], input[type='submit'], "
            "button:has-text('Send'), button:has-text('Submit')"
        ).first

        expect(submit_button).to_be_visible()

    def test_contact_form_can_be_filled(
        self, page: Page, base_url, seeded_database
    ) -> None:
        """User should be able to fill out the contact form."""
        page.goto(f"{base_url}/contact/")

        # Find and fill form fields
        # Try multiple selectors for each field type

        # Name field
        name_selectors = [
            "input[name='name']",
            "input[name='full_name']",
            "input[name='your_name']",
            "input[id*='name']:not([type='email'])",
        ]
        for selector in name_selectors:
            name_field = page.locator(selector).first
            if name_field.is_visible():
                name_field.fill("Test User")
                break

        # Email field
        email_field = page.locator("input[name='email'], input[type='email']").first
        if email_field.is_visible():
            email_field.fill("test@example.com")

        # Phone field (optional)
        phone_selectors = [
            "input[name='phone']",
            "input[name='telephone']",
            "input[type='tel']",
        ]
        for selector in phone_selectors:
            phone_field = page.locator(selector).first
            if phone_field.is_visible():
                phone_field.fill("+44 1234 567890")
                break

        # Message field
        message_field = page.locator("textarea").first
        if message_field.is_visible():
            message_field.fill("Test inquiry about bespoke kitchens.")

        # Verify fields were filled (at least message)
        message_value = message_field.input_value()
        assert "Test inquiry" in message_value

    def test_contact_form_submission(
        self, page: Page, base_url, seeded_database
    ) -> None:
        """User should be able to submit the contact form."""
        page.goto(f"{base_url}/contact/")

        # Fill required fields
        email_field = page.locator("input[name='email'], input[type='email']").first
        if email_field.is_visible():
            email_field.fill("test@example.com")

        message_field = page.locator("textarea").first
        if message_field.is_visible():
            message_field.fill("Test inquiry from E2E test.")

        # Find and try to fill name field
        name_field = page.locator("input[name='name'], input[name='full_name']").first
        if name_field.is_visible():
            name_field.fill("E2E Test User")

        # Get current URL before submit
        pre_submit_url = page.url

        # Find and click submit
        submit_button = page.locator(
            "button[type='submit'], input[type='submit']"
        ).first

        if submit_button.is_visible():
            submit_button.click()

            # Wait for response
            page.wait_for_timeout(2000)

            # Should see success message OR redirect to thank you page
            # OR stay on page with success message
            page_content = page.content().lower()

            success_indicators = [
                "thank you",
                "success",
                "received",
                "we'll be in touch",
                "message sent",
                "submitted",
            ]

            # Check for success or URL change
            has_success = any(ind in page_content for ind in success_indicators)
            url_changed = page.url != pre_submit_url

            # Either success message or redirect indicates form works
            assert (
                has_success or url_changed
            ), "Form submission should show success or redirect"
