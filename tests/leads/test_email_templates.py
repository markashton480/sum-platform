"""
Name: Email template tests
Path: tests/leads/test_email_templates.py
Purpose: Verify lead notification email templates render correctly with all fields.
Family: Leads, notifications, testing.
"""

import pytest
from django.template.loader import render_to_string
from django.utils import timezone
from sum_core.leads.models import Lead, LeadSource
from sum_core.leads.tasks import build_lead_notification_context


@pytest.fixture
def lead_with_attribution(db):
    """Create a lead with full attribution data."""
    return Lead.objects.create(
        name="John Doe",
        email="john@example.com",
        phone="555-0199",
        message="I am interested in your services.\nHere is more info.",
        form_type="contact",
        status=Lead.Status.NEW,
        lead_source=LeadSource.GOOGLE_ADS,
        lead_source_detail="Campaign match",
        utm_source="google",
        utm_medium="cpc",
        utm_campaign="summer_sale",
        utm_term="best_kitchens",
        utm_content="variant_a",
        landing_page_url="https://example.com/landing",
        page_url="https://example.com/contact",
        referrer_url="https://google.com/search",
        submitted_at=timezone.now(),
    )


@pytest.mark.django_db
class TestEmailTemplates:
    def test_subject_template_renders_correctly(self, lead_with_attribution):
        """Subject template should contain form type and lead name."""
        context = build_lead_notification_context(lead_with_attribution)
        subject = render_to_string(
            "sum_core/emails/lead_notification_subject.txt", context
        ).strip()

        assert "Contact" in subject
        assert "John Doe" in subject
        assert subject == "New Contact Lead: John Doe"

    def test_body_template_renders_all_fields(self, lead_with_attribution):
        """Body template should contain all lead details and attribution."""
        context = build_lead_notification_context(lead_with_attribution)
        body = render_to_string("sum_core/emails/lead_notification_body.txt", context)

        # Contact details
        assert "John Doe" in body
        assert "john@example.com" in body
        assert "555-0199" in body

        # Message
        assert "I am interested in your services." in body

        # Submission info
        assert "contact" in body
        assert "https://example.com/contact" in body
        assert "https://google.com/search" in body

        # Attribution
        assert "Google Ads" in body
        assert "Campaign match" in body
        assert "google" in body
        assert "cpc" in body
        assert "summer_sale" in body
        assert "best_kitchens" in body
        assert "variant_a" in body
        assert "https://example.com/landing" in body

        # Footer
        assert f"Lead ID: {lead_with_attribution.id}" in body

    def test_body_template_handles_missing_optional_fields(self):
        """Body template should render gracefully with minimal lead data."""
        lead = Lead.objects.create(
            name="Jane Smith",
            email="jane@example.com",
            message="Simple message",
            form_type="quote",
        )

        context = build_lead_notification_context(lead)
        body = render_to_string("sum_core/emails/lead_notification_body.txt", context)

        assert "Jane Smith" in body
        assert "jane@example.com" in body
        assert "Simple message" in body
        assert "quote" in body

        # Optional sections should be missing
        assert "Phone:" not in body
        assert "Page URL:" not in body
        assert "Referrer:" not in body
        assert "ATTRIBUTION" not in body
