"""
Name: Zapier webhook tests
Path: tests/leads/test_zapier.py
Purpose: Verify Zapier webhook delivery (payload, success, failure, retry, idempotency).
Family: Leads, integrations, async processing, testing.
"""

from unittest.mock import patch

import pytest
import requests
from sum_core.branding.models import SiteSettings
from sum_core.integrations.zapier import (
    ZapierResult,
    build_zapier_payload,
    send_zapier_request,
)
from sum_core.leads.models import Lead, ZapierStatus
from sum_core.leads.tasks import send_zapier_webhook
from wagtail.models import Site


@pytest.fixture
def site(db):
    """Get or create the default test site."""
    return Site.objects.get(is_default_site=True)


@pytest.fixture
def site_settings(site):
    """Create SiteSettings with Zapier enabled."""
    settings, _ = SiteSettings.objects.get_or_create(site=site)
    settings.zapier_enabled = True
    settings.zapier_webhook_url = "https://hooks.zapier.com/test"
    settings.save()
    return settings


@pytest.fixture
def lead(db):
    """Create a test lead."""
    return Lead.objects.create(
        name="Test Lead",
        email="test@example.com",
        phone="07123456789",
        message="Test message",
        form_type="contact",
        page_url="https://example.com/contact",
        utm_source="google",
        utm_medium="cpc",
        utm_campaign="test_campaign",
    )


@pytest.mark.django_db
class TestBuildZapierPayload:
    """Unit tests for payload builder."""

    def test_payload_contains_required_fields(self, lead, site):
        """Payload includes all required fields from SSOT."""
        payload = build_zapier_payload(lead, site)

        # Lead identification
        assert payload["lead_id"] == lead.id
        assert payload["submitted_at"] is not None

        # Site context
        assert payload["site_hostname"] == site.hostname
        assert payload["site_name"] == site.site_name

        # Contact fields
        assert payload["name"] == "Test Lead"
        assert payload["email"] == "test@example.com"
        assert payload["phone"] == "07123456789"
        assert payload["message"] == "Test message"
        assert payload["form_type"] == "contact"

        # Attribution
        assert payload["utm_source"] == "google"
        assert payload["utm_medium"] == "cpc"
        assert payload["utm_campaign"] == "test_campaign"

    def test_payload_handles_empty_optional_fields(self, site, db):
        """Payload gracefully handles empty optional fields."""
        lead = Lead.objects.create(
            name="Minimal Lead",
            email="minimal@example.com",
            message="Minimal",
            form_type="contact",
        )
        payload = build_zapier_payload(lead, site)

        assert payload["phone"] == ""
        assert payload["utm_source"] == ""
        assert payload["page_url"] == ""


@pytest.mark.django_db
class TestSendZapierRequest:
    """Unit tests for HTTP request helper."""

    def test_success_returns_result_with_status_code(self):
        """Successful request returns ZapierResult with success=True."""
        with patch("requests.post") as mock_post:
            mock_post.return_value.ok = True
            mock_post.return_value.status_code = 200

            result = send_zapier_request(
                "https://hooks.zapier.com/test", {"test": "data"}
            )

            assert result.success is True
            assert result.status_code == 200
            assert result.error_message == ""

    def test_failure_returns_error_message(self):
        """Failed request returns ZapierResult with error message."""
        with patch("requests.post") as mock_post:
            mock_post.return_value.ok = False
            mock_post.return_value.status_code = 500
            mock_post.return_value.text = "Internal Server Error"

            result = send_zapier_request(
                "https://hooks.zapier.com/test", {"test": "data"}
            )

            assert result.success is False
            assert result.status_code == 500
            assert "500" in result.error_message

    def test_timeout_returns_error(self):
        """Timeout returns ZapierResult with timeout error."""
        with patch(
            "requests.post", side_effect=requests.Timeout("Connection timed out")
        ):
            result = send_zapier_request(
                "https://hooks.zapier.com/test", {"test": "data"}
            )

            assert result.success is False
            assert result.status_code is None
            assert "timeout" in result.error_message.lower()

    def test_connection_error_returns_error(self):
        """Connection error returns ZapierResult with connection error."""
        with patch(
            "requests.post", side_effect=requests.ConnectionError("Connection refused")
        ):
            result = send_zapier_request(
                "https://hooks.zapier.com/test", {"test": "data"}
            )

            assert result.success is False
            assert "Connection" in result.error_message


@pytest.mark.django_db
class TestSendZapierWebhookTask:
    """Integration tests for Zapier webhook task."""

    def test_webhook_sent_successfully(self, lead, site, site_settings):
        """Task sends webhook and updates status to SENT."""
        with patch("sum_core.integrations.zapier.send_zapier_request") as mock_request:
            mock_request.return_value = ZapierResult(success=True, status_code=200)

            send_zapier_webhook(lead.id, site.id)

            lead.refresh_from_db()
            assert lead.zapier_status == ZapierStatus.SENT
            assert lead.zapier_last_attempt_at is not None
            assert lead.zapier_attempt_count == 1
            assert lead.zapier_last_error == ""

            mock_request.assert_called_once()

    def test_webhook_disabled_if_no_url(self, lead, site):
        """Task marks DISABLED if no URL configured."""
        # Create settings without Zapier URL
        settings, _ = SiteSettings.objects.get_or_create(site=site)
        settings.zapier_enabled = True
        settings.zapier_webhook_url = ""
        settings.save()

        send_zapier_webhook(lead.id, site.id)

        lead.refresh_from_db()
        assert lead.zapier_status == ZapierStatus.DISABLED
        assert lead.zapier_attempt_count == 0

    def test_webhook_disabled_if_not_enabled(self, lead, site):
        """Task marks DISABLED if Zapier is not enabled."""
        settings, _ = SiteSettings.objects.get_or_create(site=site)
        settings.zapier_enabled = False
        settings.zapier_webhook_url = "https://hooks.zapier.com/test"
        settings.save()

        send_zapier_webhook(lead.id, site.id)

        lead.refresh_from_db()
        assert lead.zapier_status == ZapierStatus.DISABLED

    def test_webhook_retry_on_failure(self, lead, site, site_settings):
        """Task retries on failure and eventually marks FAILED."""
        with (
            patch("sum_core.integrations.zapier.send_zapier_request") as mock_request,
            patch("sum_core.leads.tasks.ZAPIER_MAX_RETRIES", 0),
        ):
            mock_request.return_value = ZapierResult(
                success=False, status_code=500, error_message="Server Error"
            )

            send_zapier_webhook(lead.id, site.id)

            lead.refresh_from_db()
            assert lead.zapier_status == ZapierStatus.FAILED
            assert lead.zapier_attempt_count >= 1
            assert "Server Error" in lead.zapier_last_error

    def test_webhook_idempotency(self, lead, site, site_settings):
        """Task does not resend if already marked SENT."""
        lead.zapier_status = ZapierStatus.SENT
        lead.save()

        with patch("sum_core.integrations.zapier.send_zapier_request") as mock_request:
            send_zapier_webhook(lead.id, site.id)

            # Should not make any HTTP request
            mock_request.assert_not_called()


@pytest.mark.django_db
class TestConcurrencyIdempotency:
    """Tests for concurrency safety in Zapier tasks (CM-001 requirement)."""

    def test_duplicate_tasks_only_send_once(self, lead, site, site_settings):
        """
        Simulates the 'double-run' scenario where two tasks run for the same lead.

        With select_for_update() the second task should see SENT status and skip.
        """
        call_count = 0

        def counting_request(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            return ZapierResult(success=True, status_code=200)

        with patch(
            "sum_core.integrations.zapier.send_zapier_request",
            side_effect=counting_request,
        ):
            # First task sends the webhook
            send_zapier_webhook(lead.id, site.id)

            lead.refresh_from_db()
            assert lead.zapier_status == ZapierStatus.SENT
            assert lead.zapier_attempt_count == 1
            assert call_count == 1

            first_attempt_at = lead.zapier_last_attempt_at

            # Second task should detect SENT and skip
            send_zapier_webhook(lead.id, site.id)

            lead.refresh_from_db()
            # Should still be SENT with same timestamp (not re-sent)
            assert lead.zapier_status == ZapierStatus.SENT
            assert lead.zapier_attempt_count == 1
            assert lead.zapier_last_attempt_at == first_attempt_at

            # Only one HTTP call should have been made
            assert call_count == 1


@pytest.mark.django_db
class TestLeadExistsRegardlessOfWebhookOutcome:
    """Tests proving 'no lost leads' invariant."""

    def test_lead_exists_after_webhook_success(self, lead, site, site_settings):
        """Lead persists after successful webhook."""
        with patch("sum_core.integrations.zapier.send_zapier_request") as mock_request:
            mock_request.return_value = ZapierResult(success=True, status_code=200)

            send_zapier_webhook(lead.id, site.id)

            # Lead still exists
            assert Lead.objects.filter(id=lead.id).exists()

    def test_lead_exists_after_webhook_failure(self, lead, site, site_settings):
        """Lead persists even when webhook fails permanently."""
        with (
            patch("sum_core.integrations.zapier.send_zapier_request") as mock_request,
            patch("sum_core.leads.tasks.ZAPIER_MAX_RETRIES", 0),
        ):
            mock_request.return_value = ZapierResult(
                success=False, status_code=500, error_message="Permanent failure"
            )

            send_zapier_webhook(lead.id, site.id)

            # Lead still exists
            assert Lead.objects.filter(id=lead.id).exists()
            lead.refresh_from_db()
            assert lead.zapier_status == ZapierStatus.FAILED

    def test_lead_exists_when_site_not_found(self, lead, db):
        """Lead persists even when site lookup fails."""
        # Use non-existent site ID
        send_zapier_webhook(lead.id, site_id=99999)

        # Lead still exists
        assert Lead.objects.filter(id=lead.id).exists()
        lead.refresh_from_db()
        assert lead.zapier_status == ZapierStatus.FAILED
