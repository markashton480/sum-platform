"""
Name: Lead Model Tests
Path: tests/leads/test_lead_model.py
Purpose: Validate Lead model defaults, field persistence, and LeadSource choices.
Family: Lead management test coverage.
Dependencies: Django ORM, sum_core.leads.models.Lead, sum_core.leads.models.LeadSource.
"""

from __future__ import annotations

import pytest
from sum_core.leads.models import Lead, LeadSource

pytestmark = pytest.mark.django_db


class TestLeadDefaults:
    """Tests for Lead model default values."""

    def test_lead_defaults(self) -> None:
        lead = Lead.objects.create(
            name="Jane Doe",
            email="jane@example.com",
            phone="",
            message="Hello",
            form_type="contact",
            form_data={"topic": "General enquiry"},
        )

        assert lead.status == Lead.Status.NEW
        assert lead.is_archived is False
        assert lead.submitted_at is not None

    def test_attribution_fields_default_to_empty(self) -> None:
        lead = Lead.objects.create(
            name="Test User",
            email="test@example.com",
            message="Test message",
            form_type="contact",
        )

        assert lead.utm_source == ""
        assert lead.utm_medium == ""
        assert lead.utm_campaign == ""
        assert lead.utm_term == ""
        assert lead.utm_content == ""
        assert lead.landing_page_url == ""
        assert lead.page_url == ""
        assert lead.referrer_url == ""
        assert lead.lead_source == ""
        assert lead.lead_source_detail == ""


class TestLeadFieldPersistence:
    """Tests for Lead field persistence."""

    def test_lead_form_data_persists_exactly(self) -> None:
        payload = {
            "postcode": "SW1A 1AA",
            "budget": "20-40k",
            "details": "Kitchen + bath",
        }
        lead = Lead.objects.create(
            name="Sam Smith",
            email="sam@example.com",
            message="Please quote",
            phone="07123456789",
            form_type="quote",
            form_data=payload,
        )

        lead.refresh_from_db()
        assert lead.form_data == payload

    def test_attribution_fields_persist(self) -> None:
        lead = Lead.objects.create(
            name="Attribution Test",
            email="attr@example.com",
            message="Test",
            form_type="contact",
            utm_source="google",
            utm_medium="cpc",
            utm_campaign="test-campaign",
            utm_term="test term",
            utm_content="ad-a",
            landing_page_url="https://example.com/landing",
            page_url="https://example.com/form",
            referrer_url="https://google.com/",
            lead_source="google_ads",
            lead_source_detail="campaign=test-campaign",
        )

        lead.refresh_from_db()
        assert lead.utm_source == "google"
        assert lead.utm_medium == "cpc"
        assert lead.utm_campaign == "test-campaign"
        assert lead.utm_term == "test term"
        assert lead.utm_content == "ad-a"
        assert lead.landing_page_url == "https://example.com/landing"
        assert lead.page_url == "https://example.com/form"
        assert lead.referrer_url == "https://google.com/"
        assert lead.lead_source == "google_ads"
        assert lead.lead_source_detail == "campaign=test-campaign"


class TestLeadSourceChoices:
    """Tests for LeadSource TextChoices."""

    def test_lead_source_choices_exist(self) -> None:
        # Verify all expected choices are defined
        assert LeadSource.GOOGLE_ADS == "google_ads"
        assert LeadSource.META_ADS == "meta_ads"
        assert LeadSource.BING_ADS == "bing_ads"
        assert LeadSource.SEO == "seo"
        assert LeadSource.DIRECT == "direct"
        assert LeadSource.REFERRAL == "referral"
        assert LeadSource.OFFLINE == "offline"
        assert LeadSource.UNKNOWN == "unknown"

    def test_lead_source_labels(self) -> None:
        # Verify human-readable labels
        assert LeadSource.GOOGLE_ADS.label == "Google Ads"
        assert LeadSource.META_ADS.label == "Meta Ads"
        assert LeadSource.SEO.label == "SEO"
        assert LeadSource.DIRECT.label == "Direct"

    def test_lead_accepts_valid_source_choice(self) -> None:
        lead = Lead.objects.create(
            name="Choice Test",
            email="choice@example.com",
            message="Test",
            form_type="contact",
            lead_source=LeadSource.GOOGLE_ADS,
        )

        lead.refresh_from_db()
        assert lead.lead_source == "google_ads"


class TestLeadModelMeta:
    """Tests for Lead model Meta configuration."""

    def test_ordering_by_submitted_at_descending(self) -> None:
        lead1 = Lead.objects.create(
            name="First",
            email="first@example.com",
            message="First lead",
            form_type="contact",
        )
        lead2 = Lead.objects.create(
            name="Second",
            email="second@example.com",
            message="Second lead",
            form_type="contact",
        )

        leads = list(Lead.objects.all())
        # Most recent first
        assert leads[0] == lead2
        assert leads[1] == lead1

    def test_str_representation(self) -> None:
        lead = Lead(
            name="John Doe",
            email="john@example.com",
            form_type="quote",
        )
        assert str(lead) == "John Doe <john@example.com> (quote)"
