"""
Name: Task Correlation Tests
Path: tests/leads/test_task_correlation.py
Purpose: Unit tests for request_id propagation in Celery tasks.
Family: Leads/Ops Tests (Milestone 4)
Dependencies: pytest, pytest-django
"""

from __future__ import annotations

import logging
from unittest.mock import patch

import pytest


class TestTaskCorrelation:
    """Tests for request_id propagation in lead tasks."""

    @pytest.mark.django_db
    def test_send_lead_notification_logs_request_id(self, caplog):
        """Test send_lead_notification includes request_id in logs."""
        from sum_core.leads.models import Lead

        # Create a lead
        lead = Lead.objects.create(
            name="Test User",
            email="test@example.com",
            message="Test message",
            form_type="contact",
        )

        # Force propagation to capture logs since strict config disables it
        logger = logging.getLogger("sum_core.leads.tasks")
        old_propagate = logger.propagate
        logger.propagate = True

        # Also enable propagation on parent logger so caplog can capture
        parent_logger = logging.getLogger("sum_core")
        old_parent_propagate = parent_logger.propagate
        parent_logger.propagate = True

        try:
            with caplog.at_level(logging.INFO):
                with patch("sum_core.leads.tasks.EmailMultiAlternatives"):
                    with patch("django.conf.settings.LEAD_NOTIFICATION_EMAIL", ""):
                        from sum_core.leads.tasks import send_lead_notification

                        # Call task directly
                        send_lead_notification(
                            lead.id, request_id="test-correlation-123"
                        )
        finally:
            logger.propagate = old_propagate
            parent_logger.propagate = old_parent_propagate

        # Check that request_id appears in log records
        # Check all records, and handle potential UUID vs str mismatch
        assert any(
            str(getattr(r, "request_id", "")) == "test-correlation-123"
            for r in caplog.records
        )

    @pytest.mark.django_db
    def test_send_lead_notification_works_without_request_id(self):
        """Test send_lead_notification works when request_id is None."""
        from sum_core.leads.models import Lead

        # Create a lead
        lead = Lead.objects.create(
            name="Test User",
            email="test@example.com",
            message="Test message",
            form_type="contact",
        )

        with patch("sum_core.leads.tasks.EmailMultiAlternatives"):
            with patch("django.conf.settings.LEAD_NOTIFICATION_EMAIL", ""):
                from sum_core.leads.tasks import send_lead_notification

                # Should not raise when request_id is None (backward compat)
                send_lead_notification(lead.id, request_id=None)

    @pytest.mark.django_db
    def test_send_lead_webhook_includes_request_id(self, caplog):
        """Test send_lead_webhook includes request_id in logs."""
        from sum_core.leads.models import Lead

        # Create a lead
        lead = Lead.objects.create(
            name="Test User",
            email="test@example.com",
            message="Test message",
            form_type="contact",
        )

        # Force propagation
        logger = logging.getLogger("sum_core.leads.tasks")
        old_propagate = logger.propagate
        logger.propagate = True

        # Also enable propagation on parent logger so caplog can capture
        parent_logger = logging.getLogger("sum_core")
        old_parent_propagate = parent_logger.propagate
        parent_logger.propagate = True

        try:
            with caplog.at_level(logging.INFO):
                with patch("django.conf.settings.ZAPIER_WEBHOOK_URL", ""):
                    from sum_core.leads.tasks import send_lead_webhook

                    send_lead_webhook(lead.id, request_id="webhook-correlation-456")
        finally:
            logger.propagate = old_propagate
            parent_logger.propagate = old_parent_propagate

        # Check that request_id appears in log extra
        assert any(
            str(getattr(r, "request_id", "")) == "webhook-correlation-456"
            for r in caplog.records
        )

    @pytest.mark.django_db
    def test_send_zapier_webhook_includes_request_id(
        self, caplog, wagtail_default_site
    ):
        """Test send_zapier_webhook includes request_id in logs."""
        from sum_core.leads.models import Lead

        # Create a lead
        lead = Lead.objects.create(
            name="Test User",
            email="test@example.com",
            message="Test message",
            form_type="contact",
        )

        # Force propagation
        logger = logging.getLogger("sum_core.leads.tasks")
        old_propagate = logger.propagate
        logger.propagate = True

        # Also enable propagation on parent logger so caplog can capture
        parent_logger = logging.getLogger("sum_core")
        old_parent_propagate = parent_logger.propagate
        parent_logger.propagate = True

        try:
            with caplog.at_level(logging.INFO):
                from sum_core.leads.tasks import send_zapier_webhook

                send_zapier_webhook(
                    lead.id,
                    wagtail_default_site.id,
                    request_id="zapier-correlation-789",
                )
        finally:
            logger.propagate = old_propagate
            parent_logger.propagate = old_parent_propagate

        # Check that request_id appears in log extra
        # Use str() comparison to handle potential UUID vs str mismatch
        assert any(
            str(getattr(r, "request_id", "")) == "zapier-correlation-789"
            for r in caplog.records
        )

    @pytest.mark.django_db
    def test_sentry_context_set_with_request_id(self):
        """Test that Sentry context is set when request_id is provided."""
        from sum_core.leads.models import Lead

        lead = Lead.objects.create(
            name="Test User",
            email="test@example.com",
            message="Test message",
            form_type="contact",
        )

        # Patch where it is used (in tasks.py), not where it is defined
        with patch("sum_core.leads.tasks.set_sentry_context") as mock_set_context:
            with patch("django.conf.settings.LEAD_NOTIFICATION_EMAIL", ""):
                from sum_core.leads.tasks import send_lead_notification

                send_lead_notification(lead.id, request_id="sentry-test-id")

        mock_set_context.assert_called_once()
        call_kwargs = mock_set_context.call_args[1]
        assert call_kwargs["request_id"] == "sentry-test-id"
        assert call_kwargs["lead_id"] == lead.id
