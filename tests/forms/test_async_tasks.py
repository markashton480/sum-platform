"""
Name: Dynamic form async tasks tests
Path: tests/forms/test_async_tasks.py
Purpose: Verify dynamic form Celery tasks for notifications and webhooks.
Family: Forms, Leads, Notifications, Async processing.
"""

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest
import requests
from django.core import mail
from sum_core.forms.models import FormDefinition
from sum_core.forms.tasks import send_auto_reply, send_form_notification, send_webhook
from sum_core.leads.models import Lead


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

        assert len(mail.outbox) == 1
        email = mail.outbox[0]
        assert email.to == ["admin@example.com"]
        assert "Dynamic Contact" in email.subject
        assert "Roofing" in email.body
        assert email.alternatives

    def test_form_notification_skips_when_disabled(self, lead, form_definition):
        form_definition.email_notification_enabled = False
        form_definition.save(update_fields=["email_notification_enabled"])

        send_form_notification(lead.id, form_definition.id)

        assert len(mail.outbox) == 0

    def test_auto_reply_sends_email(self, lead, form_definition):
        send_auto_reply(lead.id, form_definition.id)

        assert len(mail.outbox) == 1
        email = mail.outbox[0]
        assert email.to == [lead.email]
        assert "Jane Doe" in email.subject
        assert "Jane Doe" in email.body

    def test_auto_reply_skips_without_email(self, lead, form_definition):
        lead.email = ""
        lead.save(update_fields=["email"])

        send_auto_reply(lead.id, form_definition.id)

        assert len(mail.outbox) == 0

    def test_webhook_payload(self, lead, form_definition):
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None

        with patch("requests.post", return_value=mock_response) as mock_post:
            send_webhook(lead.id, form_definition.id)

        assert mock_post.called
        payload = mock_post.call_args[1]["json"]
        assert payload["event"] == "form.submitted"
        assert payload["form"]["id"] == form_definition.id
        assert payload["submission"]["id"] == lead.id
        assert payload["submission"]["data"]["service"] == "Roofing"
        assert payload["attribution"]["utm_source"] == "google"

    def test_webhook_skips_when_disabled(self, lead, form_definition):
        form_definition.webhook_enabled = False
        form_definition.save(update_fields=["webhook_enabled"])

        with patch("requests.post") as mock_post:
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

    def test_webhook_retries_on_failure(self, lead, form_definition):
        with patch("requests.post", side_effect=requests.RequestException("Boom")):
            with pytest.raises(requests.RequestException):
                send_webhook(lead.id, form_definition.id)
