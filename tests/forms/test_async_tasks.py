"""
Name: Dynamic form async tasks tests
Path: tests/forms/test_async_tasks.py
Purpose: Verify dynamic form Celery tasks for notifications and webhooks.
Family: Forms, Leads, Notifications, Async processing.
"""

from __future__ import annotations

import json
from unittest.mock import Mock, patch

import pytest
import requests
from django.core import mail
from sum_core.forms.models import FormDefinition
from sum_core.forms.tasks import send_auto_reply, send_form_notification, send_webhook
from sum_core.leads.models import EmailStatus, Lead, WebhookStatus


@pytest.fixture(autouse=True)
def clear_outbox(settings):
    settings.DEFAULT_FROM_EMAIL = "noreply@example.com"
    mail.outbox.clear()
    yield
    mail.outbox.clear()


@pytest.fixture
def form_definition(wagtail_default_site):
    return FormDefinition.objects.create(
        site=wagtail_default_site,
        name="Dynamic Contact",
        slug="dynamic-contact",
        fields=[],
        email_notification_enabled=True,
        notification_emails="admin@example.com",
        auto_reply_enabled=True,
        auto_reply_subject="Thanks, {{name}}",
        auto_reply_body="Hi {{name}}, we received your request.",
        webhook_enabled=True,
        webhook_url="https://example.com/webhook",
    )


@pytest.fixture
def lead(form_definition):
    return Lead.objects.create(
        name="Jane Doe",
        email="jane@example.com",
        message="Need a quote",
        form_type=form_definition.slug,
        form_notification_status=EmailStatus.PENDING,
        auto_reply_status=EmailStatus.PENDING,
        form_webhook_status=WebhookStatus.PENDING,
        form_data={"service": "Roofing"},
        landing_page_url="https://example.com/landing",
        page_url="https://example.com/contact",
        utm_source="google",
        utm_medium="cpc",
        utm_campaign="spring",
        utm_term="roofing",
        utm_content="ad-1",
    )


@pytest.mark.django_db
class TestDynamicFormTasks:
    def test_form_notification_sends_email(self, lead, form_definition):
        send_form_notification(lead.id, form_definition.id)

        lead.refresh_from_db()
        assert len(mail.outbox) == 1
        email = mail.outbox[0]
        assert email.to == ["admin@example.com"]
        assert "Dynamic Contact" in email.subject
        assert "Roofing" in email.body
        assert email.alternatives
        assert lead.form_notification_status == EmailStatus.SENT
        assert lead.form_notification_sent_at is not None

    def test_form_notification_skips_when_disabled(self, lead, form_definition):
        form_definition.email_notification_enabled = False
        form_definition.save(update_fields=["email_notification_enabled"])

        send_form_notification(lead.id, form_definition.id)

        lead.refresh_from_db()
        assert len(mail.outbox) == 0
        assert lead.form_notification_status == EmailStatus.DISABLED

    def test_form_notification_idempotent(self, lead, form_definition):
        lead.form_notification_status = EmailStatus.SENT
        lead.save(update_fields=["form_notification_status"])

        send_form_notification(lead.id, form_definition.id)

        assert len(mail.outbox) == 0

    def test_auto_reply_sends_email(self, lead, form_definition):
        send_auto_reply(lead.id, form_definition.id)

        lead.refresh_from_db()
        assert len(mail.outbox) == 1
        email = mail.outbox[0]
        assert email.to == [lead.email]
        assert "Jane Doe" in email.subject
        assert "Jane Doe" in email.body
        assert lead.auto_reply_status == EmailStatus.SENT
        assert lead.auto_reply_sent_at is not None

    def test_auto_reply_skips_when_disabled(self, lead, form_definition):
        form_definition.auto_reply_enabled = False
        form_definition.save(update_fields=["auto_reply_enabled"])

        send_auto_reply(lead.id, form_definition.id)

        lead.refresh_from_db()
        assert len(mail.outbox) == 0
        assert lead.auto_reply_status == EmailStatus.DISABLED

    def test_auto_reply_idempotent(self, lead, form_definition):
        lead.auto_reply_status = EmailStatus.SENT
        lead.save(update_fields=["auto_reply_status"])

        send_auto_reply(lead.id, form_definition.id)

        assert len(mail.outbox) == 0

    def test_auto_reply_skips_without_email(self, lead, form_definition):
        lead.email = ""
        lead.save(update_fields=["email"])

        send_auto_reply(lead.id, form_definition.id)

        lead.refresh_from_db()
        assert len(mail.outbox) == 0
        assert lead.auto_reply_status == EmailStatus.FAILED
        assert "Submitter email" in lead.auto_reply_last_error

    def test_auto_reply_strips_header_newlines(self, lead, form_definition):
        lead.name = "Eve\r\nBcc:evil@example.com"
        lead.save(update_fields=["name"])

        send_auto_reply(lead.id, form_definition.id)

        lead.refresh_from_db()
        assert len(mail.outbox) == 1
        subject = mail.outbox[0].subject
        assert "\n" not in subject
        assert "\r" not in subject

    def test_auto_reply_preserves_plain_text_name(self, lead, form_definition):
        lead.name = "<script>alert('xss')</script>"
        lead.save(update_fields=["name"])

        send_auto_reply(lead.id, form_definition.id)

        lead.refresh_from_db()
        assert len(mail.outbox) == 1
        subject = mail.outbox[0].subject
        body = mail.outbox[0].body
        assert "<script>" in subject
        assert "<script>" in body
        assert "&lt;script&gt;" not in subject

    def test_webhook_payload(self, lead, form_definition):
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.status_code = 200

        with patch(
            "sum_core.forms.tasks.requests.post", return_value=mock_response
        ) as mock_post:
            send_webhook(lead.id, form_definition.id)

        assert mock_post.called
        payload = json.loads(mock_post.call_args[1]["data"])
        assert payload["event"] == "form.submitted"
        assert payload["form"]["id"] == form_definition.id
        assert payload["submission"]["id"] == lead.id
        assert payload["submission"]["contact"]["email"] == lead.email
        assert payload["submission"]["contact"]["name"] == lead.name
        assert payload["submission"]["data"]["service"] == "Roofing"
        assert payload["attribution"]["utm_source"] == "google"

        lead.refresh_from_db()
        assert lead.form_webhook_status == WebhookStatus.SENT
        assert lead.form_webhook_sent_at is not None
        assert lead.form_webhook_last_status_code == 200

    def test_webhook_payload_includes_request_id(self, lead, form_definition):
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.status_code = 200

        with patch(
            "sum_core.forms.tasks.requests.post", return_value=mock_response
        ) as mock_post:
            send_webhook(lead.id, form_definition.id, request_id="req-123")

        payload = json.loads(mock_post.call_args[1]["data"])
        assert payload["request_id"] == "req-123"

    def test_webhook_skips_when_disabled(self, lead, form_definition):
        form_definition.webhook_enabled = False
        form_definition.save(update_fields=["webhook_enabled"])

        with patch("sum_core.forms.tasks.requests.post") as mock_post:
            send_webhook(lead.id, form_definition.id)

        lead.refresh_from_db()
        assert not mock_post.called
        assert lead.form_webhook_status == WebhookStatus.DISABLED

    def test_webhook_blocks_private_url(self, lead, form_definition):
        form_definition.webhook_url = "http://127.0.0.1/secret"
        form_definition.save(update_fields=["webhook_url"])

        with patch("sum_core.forms.tasks.requests.post") as mock_post:
            send_webhook(lead.id, form_definition.id)

        lead.refresh_from_db()
        assert not mock_post.called
        assert lead.form_webhook_status == WebhookStatus.FAILED
        assert "Webhook URL" in lead.form_webhook_last_error

    def test_webhook_idempotent(self, lead, form_definition):
        lead.form_webhook_status = WebhookStatus.SENT
        lead.save(update_fields=["form_webhook_status"])

        with patch("sum_core.forms.tasks.requests.post") as mock_post:
            send_webhook(lead.id, form_definition.id)

        assert not mock_post.called

    def test_tasks_handle_missing_records(self):
        send_form_notification(9999, 9999)
        send_auto_reply(9999, 9999)
        send_webhook(9999, 9999)
        assert len(mail.outbox) == 0

    def test_form_notification_retries_on_failure(self, lead, form_definition):
        with patch("sum_core.forms.tasks.send_mail", side_effect=Exception("SMTP")):
            with pytest.raises(Exception):
                send_form_notification(lead.id, form_definition.id)

        lead.refresh_from_db()
        assert lead.form_notification_status == EmailStatus.IN_PROGRESS
        assert "SMTP" in lead.form_notification_last_error

    def test_webhook_retries_on_failure(self, lead, form_definition):
        with patch(
            "sum_core.forms.tasks.requests.post",
            side_effect=requests.RequestException("Boom"),
        ):
            with pytest.raises(requests.RequestException):
                send_webhook(lead.id, form_definition.id)

        lead.refresh_from_db()
        assert lead.form_webhook_status == WebhookStatus.IN_PROGRESS
        assert "Boom" in lead.form_webhook_last_error


class TestWebhookSSRFProtection:
    """
    Test SSRF (Server-Side Request Forgery) protection in webhook delivery.

    Phase 2: Security-critical tests for webhook URL validation.
    Ensures webhooks cannot be used to probe internal networks or cloud metadata services.
    """

    @pytest.mark.parametrize(
        "webhook_url",
        [
            "http://127.0.0.1/admin",
            "http://127.0.0.1:8000/secret",
            "http://localhost/internal",
            "http://0.0.0.0/test",
            "http://[::1]/ipv6-localhost",
            "http://10.0.0.1/private",
            "http://10.255.255.255/private",
            "http://172.16.0.1/private",
            "http://172.31.255.255/private",
            "http://192.168.0.1/private",
            "http://192.168.255.255/private",
            "http://169.254.169.254/latest/meta-data/",  # AWS metadata
            "http://metadata.google.internal/",  # GCP metadata
        ],
    )
    def test_webhook_blocks_private_ip_addresses(
        self, lead, form_definition, webhook_url
    ):
        """Test webhook delivery rejects private/internal IP addresses."""
        form_definition.webhook_url = webhook_url
        form_definition.save(update_fields=["webhook_url"])

        with patch("sum_core.forms.tasks.requests.post") as mock_post:
            send_webhook(lead.id, form_definition.id)

        lead.refresh_from_db()
        assert not mock_post.called
        assert lead.form_webhook_status == WebhookStatus.FAILED
        # Error message should indicate the webhook was blocked for security
        error_msg = lead.form_webhook_last_error.lower()
        assert any(
            phrase in error_msg
            for phrase in ["non-public", "private", "not be resolved", "not allowed"]
        )

    def test_webhook_rejects_file_scheme(self, lead, form_definition):
        """Test webhook delivery rejects file:// URLs."""
        form_definition.webhook_url = "file:///etc/passwd"
        form_definition.save(update_fields=["webhook_url"])

        with patch("sum_core.forms.tasks.requests.post") as mock_post:
            send_webhook(lead.id, form_definition.id)

        lead.refresh_from_db()
        assert not mock_post.called
        assert lead.form_webhook_status == WebhookStatus.FAILED


class TestEmailRetryBehavior:
    """
    Test email retry and error persistence.

    Phase 2: Tests for retry logic and error tracking in email notifications.
    """

    def test_email_notification_persists_error_message(self, lead, form_definition):
        """Test email errors are persisted to lead for debugging."""
        error_msg = "Connection refused to SMTP server"
        with patch("sum_core.forms.tasks.send_mail", side_effect=Exception(error_msg)):
            with pytest.raises(Exception):
                send_form_notification(lead.id, form_definition.id)

        lead.refresh_from_db()
        assert lead.form_notification_status == EmailStatus.IN_PROGRESS
        assert error_msg in lead.form_notification_last_error

    def test_auto_reply_persists_error_message(self, lead, form_definition):
        """Test auto-reply errors are persisted to lead for debugging."""
        error_msg = "SMTP timeout after 30s"
        with patch("sum_core.forms.tasks.send_mail", side_effect=Exception(error_msg)):
            with pytest.raises(Exception):
                send_auto_reply(lead.id, form_definition.id)

        lead.refresh_from_db()
        assert lead.auto_reply_status == EmailStatus.IN_PROGRESS
        assert error_msg in lead.auto_reply_last_error
