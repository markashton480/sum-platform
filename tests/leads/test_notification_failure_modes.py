"""
Name: Notification failure mode tests
Path: tests/leads/test_notification_failure_modes.py
Purpose: Verify 'no lost leads' invariant when Celery/Broker fails during form submission.
Family: Leads, forms, failures, reliability.
"""

from unittest.mock import patch

import pytest
from django.core.cache import cache
from django.test import Client
from sum_core.forms.models import FormConfiguration
from sum_core.leads.models import EmailStatus, Lead, WebhookStatus
from wagtail.models import Site


def _disable_rate_limit() -> None:
    cache.clear()
    site = Site.objects.get(is_default_site=True)
    config = FormConfiguration.get_for_site(site)
    config.rate_limit_per_ip_per_hour = 0
    config.save(update_fields=["rate_limit_per_ip_per_hour"])


@pytest.mark.django_db
class TestNotificationQueueFailures:
    """
    Test that leads are preserved and status updated even if
    Celery task queueing fails (e.g. Broker down).
    """

    def test_broker_down_during_email_queue(self):
        """
        If queuing the email task raises an exception (e.g. broker down),
        the lead should still exist, and email_status should be FAILED.
        """
        _disable_rate_limit()
        client = Client()
        data = {
            "name": "Queue Fail Test",
            "email": "fail@example.com",
            "message": "Testing broker failure",
            "form_type": "contact",
        }

        # Simulate exception when calling .delay() on the task
        with patch(
            "sum_core.leads.tasks.send_lead_notification.delay",
            side_effect=Exception("Redis connection refused"),
        ):
            response = client.post("/forms/submit/", data)

        assert response.status_code == 200
        assert response.json()["success"] is True

        # Verify lead exists
        lead = Lead.objects.get(email="fail@example.com")

        # Verify status caught the error
        assert lead.email_status == EmailStatus.FAILED
        assert "Redis connection refused" in lead.email_last_error

        # Webhook should still have attempted (unless that also failed, but here we only mocked email failure)
        # Note: In our implementation, we try catch block separately for each task.
        # So webhook task might still be queued successfully if we didn't mock it to fail.
        # But since we use eager mode in tests, it might run. Let's check status.
        # Since we didn't mock send_lead_webhook.delay, and settings might not have URL, check default.
        # If eager, it would run.

    def test_broker_down_during_webhook_queue(self):
        """
        If queuing the webhook task raises an exception,
        the lead should still exist, and webhook_status should be FAILED.
        """
        _disable_rate_limit()
        client = Client()
        data = {
            "name": "Webhook Queue Fail",
            "email": "webhookfail@example.com",
            "message": "Testing webhook broker failure",
            "form_type": "contact",
        }

        with patch(
            "sum_core.leads.tasks.send_lead_webhook.delay",
            side_effect=Exception("Kombu error"),
        ):
            response = client.post("/forms/submit/", data)

        assert response.status_code == 200

        lead = Lead.objects.get(email="webhookfail@example.com")
        assert lead.webhook_status == WebhookStatus.FAILED
        assert "Kombu error" in lead.webhook_last_error

    def test_both_queues_fail_persists_lead(self):
        """
        Even if EVERYTHING fails (both tasks queueing), the lead must persist.
        """
        _disable_rate_limit()
        client = Client()
        data = {
            "name": "Total Failure",
            "email": "totalfail@example.com",
            "message": "Everything is broken",
            "form_type": "contact",
        }

        with (
            patch(
                "sum_core.leads.tasks.send_lead_notification.delay",
                side_effect=Exception("Error 1"),
            ),
            patch(
                "sum_core.leads.tasks.send_lead_webhook.delay",
                side_effect=Exception("Error 2"),
            ),
        ):
            response = client.post("/forms/submit/", data)

        assert response.status_code == 200

        lead = Lead.objects.get(email="totalfail@example.com")
        assert lead.email_status == EmailStatus.FAILED
        assert "Error 1" in lead.email_last_error
        assert lead.webhook_status == WebhookStatus.FAILED
        assert "Error 2" in lead.webhook_last_error
