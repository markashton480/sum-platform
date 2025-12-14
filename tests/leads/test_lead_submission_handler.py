"""
Name: Lead Submission Handler Tests
Path: tests/leads/test_lead_submission_handler.py
Purpose: Validate "submission → Lead persisted" and "no lost leads" invariant on downstream failures.
Family: Lead management test coverage.
Dependencies: sum_core.leads.services.create_lead_from_submission.
"""

from __future__ import annotations

import pytest
from sum_core.leads.models import Lead, LeadSourceRule
from sum_core.leads.services import AttributionData, create_lead_from_submission

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def clear_lead_source_rules() -> None:
    """Clear all LeadSourceRule objects before each test to ensure isolation."""
    LeadSourceRule.objects.all().delete()


class TestBasicLeadCreation:
    """Tests for basic lead creation functionality."""

    def test_create_lead_from_submission_creates_lead(self) -> None:
        payload = {"preferred_time": "morning", "notes": "Call first"}
        lead = create_lead_from_submission(
            name="Alex Example",
            email="alex@example.com",
            phone="07000000000",
            message="Hi",
            form_type="contact",
            form_data=payload,
        )

        assert Lead.objects.filter(pk=lead.pk).exists()
        assert lead.status == Lead.Status.NEW
        assert lead.form_type == "contact"
        assert lead.form_data == payload

    def test_downstream_failure_does_not_delete_persisted_lead(self) -> None:
        def _raise_after_create(_: Lead) -> None:
            raise RuntimeError("simulated downstream failure")

        with pytest.raises(RuntimeError):
            create_lead_from_submission(
                name="Failure Case",
                email="failure@example.com",
                message="Test",
                form_type="contact",
                form_data={"a": 1},
                post_create_hook=_raise_after_create,
            )

        assert Lead.objects.filter(
            email="failure@example.com", form_type="contact"
        ).exists()


class TestAttributionDataIntegration:
    """Tests for attribution data storage and derivation."""

    def test_lead_with_attribution_stores_utm_fields(self) -> None:
        attribution = AttributionData(
            utm_source="google",
            utm_medium="cpc",
            utm_campaign="kitchens-2025",
            utm_term="kitchen renovation",
            utm_content="ad-variant-a",
        )

        lead = create_lead_from_submission(
            name="UTM Test",
            email="utm@example.com",
            message="Test attribution",
            form_type="quote",
            attribution=attribution,
        )

        lead.refresh_from_db()
        assert lead.utm_source == "google"
        assert lead.utm_medium == "cpc"
        assert lead.utm_campaign == "kitchens-2025"
        assert lead.utm_term == "kitchen renovation"
        assert lead.utm_content == "ad-variant-a"

    def test_lead_with_attribution_stores_url_fields(self) -> None:
        attribution = AttributionData(
            landing_page_url="https://example.com/services/kitchens",
            page_url="https://example.com/quote",
            referrer_url="https://www.google.com/",
        )

        lead = create_lead_from_submission(
            name="URL Test",
            email="url@example.com",
            message="Test URLs",
            form_type="contact",
            attribution=attribution,
        )

        lead.refresh_from_db()
        assert lead.landing_page_url == "https://example.com/services/kitchens"
        assert lead.page_url == "https://example.com/quote"
        assert lead.referrer_url == "https://www.google.com/"

    def test_lead_derives_google_ads_source(self) -> None:
        attribution = AttributionData(
            utm_source="google",
            utm_medium="cpc",
            utm_campaign="winter-sale",
        )

        lead = create_lead_from_submission(
            name="Google Ads Test",
            email="gads@example.com",
            message="From Google Ads",
            form_type="contact",
            attribution=attribution,
        )

        lead.refresh_from_db()
        assert lead.lead_source == "google_ads"
        assert "campaign=winter-sale" in lead.lead_source_detail

    def test_lead_derives_seo_source_from_google_referrer(self) -> None:
        attribution = AttributionData(
            referrer_url="https://www.google.com/search?q=kitchen+renovation",
        )

        lead = create_lead_from_submission(
            name="SEO Test",
            email="seo@example.com",
            message="From organic search",
            form_type="contact",
            attribution=attribution,
        )

        lead.refresh_from_db()
        assert lead.lead_source == "seo"

    def test_lead_derives_direct_source_with_no_attribution(self) -> None:
        lead = create_lead_from_submission(
            name="Direct Test",
            email="direct@example.com",
            message="Direct visitor",
            form_type="contact",
            # No attribution provided
        )

        lead.refresh_from_db()
        assert lead.lead_source == "direct"

    def test_lead_derives_referral_source_from_external_referrer(self) -> None:
        attribution = AttributionData(
            referrer_url="https://www.checkatrade.com/trades/example",
        )

        lead = create_lead_from_submission(
            name="Referral Test",
            email="referral@example.com",
            message="From Checkatrade",
            form_type="quote",
            attribution=attribution,
        )

        lead.refresh_from_db()
        assert lead.lead_source == "referral"
        assert "checkatrade.com" in lead.lead_source_detail

    def test_lead_derives_meta_ads_source(self) -> None:
        attribution = AttributionData(
            utm_source="facebook",
            utm_medium="cpc",
        )

        lead = create_lead_from_submission(
            name="Meta Ads Test",
            email="meta@example.com",
            message="From Facebook Ads",
            form_type="contact",
            attribution=attribution,
        )

        lead.refresh_from_db()
        assert lead.lead_source == "meta_ads"

    def test_lead_with_empty_attribution_defaults_to_direct(self) -> None:
        attribution = AttributionData()  # All empty strings

        lead = create_lead_from_submission(
            name="Empty Attribution",
            email="empty@example.com",
            message="Empty attribution data",
            form_type="contact",
            attribution=attribution,
        )

        lead.refresh_from_db()
        assert lead.lead_source == "direct"

    def test_attribution_values_are_trimmed(self) -> None:
        attribution = AttributionData(
            utm_source="  google  ",
            utm_medium="  cpc  ",
            utm_campaign="  campaign  ",
        )

        lead = create_lead_from_submission(
            name="Trim Test",
            email="trim@example.com",
            message="Test trimming",
            form_type="contact",
            attribution=attribution,
        )

        lead.refresh_from_db()
        assert lead.utm_source == "google"
        assert lead.utm_medium == "cpc"
        assert lead.utm_campaign == "campaign"


class TestNoLostLeadsInvariant:
    """Tests to verify the "no lost leads" invariant is maintained."""

    def test_lead_persisted_before_hook_called(self) -> None:
        """Verify Lead exists in DB before post_create_hook runs."""
        captured_lead_id = None

        def _capture_and_verify(lead: Lead) -> None:
            nonlocal captured_lead_id
            captured_lead_id = lead.pk
            # Verify lead exists in DB at this point
            assert Lead.objects.filter(pk=lead.pk).exists()

        create_lead_from_submission(
            name="Hook Order Test",
            email="hook@example.com",
            message="Test hook order",
            form_type="contact",
            post_create_hook=_capture_and_verify,
        )

        assert captured_lead_id is not None

    def test_attribution_derivation_failure_does_not_prevent_persistence(self) -> None:
        """Even if attribution is unusual, lead should still be created."""
        attribution = AttributionData(
            utm_source="weird-source-with-special-chars!@#",
            utm_medium="also-unusual",
        )

        lead = create_lead_from_submission(
            name="Weird Attribution",
            email="weird@example.com",
            message="Unusual attribution",
            form_type="contact",
            attribution=attribution,
        )

        lead.refresh_from_db()
        assert lead.pk is not None
        # Should derive to unknown but still persist
        assert lead.lead_source == "unknown"
