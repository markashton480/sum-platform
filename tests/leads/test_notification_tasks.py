"""
Name: Notification tasks tests
Path: tests/leads/test_notification_tasks.py
Purpose: Verify Celery tasks for email and webhook notifications (success, failure, idempotency).
Family: Leads, notifications, async processing, testing.
"""

from unittest.mock import patch

import pytest
import requests
from django.core import mail
from django.test import override_settings
from sum_core.leads.models import EmailStatus, Lead, WebhookStatus
from sum_core.leads.tasks import send_lead_notification, send_lead_webhook


# Mock retry to avoid actual delays/retries during tests
@pytest.fixture
def lead(db):
    return Lead.objects.create(
        name="Test Lead",
        email="test@example.com",
        message="Test message",
        form_type="contact",
    )


@pytest.mark.django_db
class TestEmailNotificationTask:
    @override_settings(LEAD_NOTIFICATION_EMAIL="notify@example.com")
    def test_email_sent_successfully(self, lead):
        """Task sends email and updates status to SENT."""
        send_lead_notification(lead.id)

        lead.refresh_from_db()
        assert lead.email_status == EmailStatus.SENT
        assert lead.email_sent_at is not None
        assert lead.email_attempts == 1
        assert lead.email_last_error == ""

        assert len(mail.outbox) == 1
        assert mail.outbox[0].to == ["notify@example.com"]
        assert "Test Lead" in mail.outbox[0].subject

    def test_email_skipped_if_no_config(self, lead):
        """Task marks FAILED if no notification email configured."""
        with override_settings(LEAD_NOTIFICATION_EMAIL=""):
            send_lead_notification(lead.id)

        lead.refresh_from_db()
        assert lead.email_status == EmailStatus.FAILED
        assert "No notification email" in lead.email_last_error
        assert len(mail.outbox) == 0

    @override_settings(LEAD_NOTIFICATION_EMAIL="notify@example.com")
    def test_email_idempotency(self, lead):
        """Task does not resend if already marked SENT."""
        lead.email_status = EmailStatus.SENT
        lead.save()

        send_lead_notification(lead.id)

        assert len(mail.outbox) == 0

    @override_settings(LEAD_NOTIFICATION_EMAIL="notify@example.com")
    def test_email_retry_on_failure(self, lead):
        """Task retries on SMTP failure and eventually marks FAILED."""
        # Patch local import in tasks module and MAX_RETRIES to force failure path
        with patch(
            "sum_core.leads.tasks.send_mail", side_effect=Exception("SMTP Down")
        ), patch("sum_core.leads.tasks.MAX_RETRIES", 0):
            # With MAX_RETRIES=0, it should fail immediately, update DB, and NOT raise exception (caught in task)
            send_lead_notification(lead.id)

            lead.refresh_from_db()
            assert lead.email_status == EmailStatus.FAILED
            # attempts=1 because we simulate exhaustion on first try
            assert lead.email_attempts >= 1
            assert "SMTP Down" in lead.email_last_error


@pytest.mark.django_db
class TestWebhookNotificationTask:
    @override_settings(ZAPIER_WEBHOOK_URL="https://hooks.zapier.com/test")
    def test_webhook_sent_successfully(self, lead):
        """Task posts payload and updates status to SENT."""
        with patch("requests.post") as mock_post:
            mock_post.return_value.ok = True
            mock_post.return_value.status_code = 200

            send_lead_webhook(lead.id)

            lead.refresh_from_db()
            assert lead.webhook_status == WebhookStatus.SENT
            assert lead.webhook_sent_at is not None
            assert lead.webhook_attempts == 1
            assert lead.webhook_last_status_code == 200

            assert mock_post.called
            assert mock_post.call_args[1]["json"]["name"] == "Test Lead"

    def test_webhook_disabled_if_no_url(self, lead):
        """Task marks DISABLED if no URL configured."""
        with override_settings(ZAPIER_WEBHOOK_URL=""):
            send_lead_webhook(lead.id)

        lead.refresh_from_db()
        assert lead.webhook_status == WebhookStatus.DISABLED
        assert lead.webhook_attempts == 0

    @override_settings(ZAPIER_WEBHOOK_URL="https://hooks.zapier.com/test")
    def test_webhook_retry_on_failure(self, lead):
        """Task retries on 500 response and eventually marks FAILED."""
        with patch("requests.post") as mock_post, patch(
            "sum_core.leads.tasks.MAX_RETRIES", 0
        ):
            mock_post.return_value.ok = False
            mock_post.return_value.status_code = 500
            mock_post.return_value.text = "Internal Server Error"

            send_lead_webhook(lead.id)

            lead.refresh_from_db()
            assert lead.webhook_status == WebhookStatus.FAILED
            # attempts incremented before checking retries
            assert lead.webhook_attempts >= 1
            assert lead.webhook_last_status_code == 500

    @override_settings(ZAPIER_WEBHOOK_URL="https://hooks.zapier.com/test")
    def test_webhook_retry_on_timeout(self, lead):
        """Task retries on timeout and eventually marks FAILED."""
        with patch(
            "requests.post", side_effect=requests.Timeout("Connection timed out")
        ), patch("sum_core.leads.tasks.MAX_RETRIES", 0):
            send_lead_webhook(lead.id)

            lead.refresh_from_db()
            assert lead.webhook_status == WebhookStatus.FAILED
            assert lead.webhook_attempts >= 1
            assert "timeout" in lead.webhook_last_error
