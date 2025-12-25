"""
Name: Dynamic form async tasks
Path: core/sum_core/forms/tasks.py
Purpose: Send dynamic form notifications, auto-replies, and webhooks asynchronously.
Family: Forms, Leads, Integrations.
Dependencies: Celery, Django email backend, HTTP client, Lead model.
"""

from __future__ import annotations

import logging

import requests
from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
RETRY_BACKOFF = 60  # seconds; exponential backoff uses 60, 120, 240
WEBHOOK_TIMEOUT = 10  # seconds


def _parse_recipients(emails: str) -> list[str]:
    return [email.strip() for email in emails.split(",") if email.strip()]


def _build_webhook_payload(lead, form_definition) -> dict:
    return {
        "event": "form.submitted",
        "timestamp": timezone.now().isoformat(),
        "form": {
            "id": form_definition.id,
            "name": form_definition.name,
            "slug": form_definition.slug,
        },
        "submission": {
            "id": lead.id,
            "data": lead.form_data,
            "created_at": lead.submitted_at.isoformat() if lead.submitted_at else None,
        },
        "attribution": {
            "source_url": lead.page_url,
            "landing_page": lead.landing_page_url,
            "utm_source": lead.utm_source,
            "utm_medium": lead.utm_medium,
            "utm_campaign": lead.utm_campaign,
            "utm_term": lead.utm_term,
            "utm_content": lead.utm_content,
        },
    }


@shared_task(bind=True, max_retries=MAX_RETRIES)
def send_form_notification(self, lead_id: int, form_definition_id: int) -> None:
    """
    Send email notification to admin recipients when a dynamic form is submitted.
    """
    from sum_core.forms.models import FormDefinition
    from sum_core.leads.models import Lead

    try:
        lead = Lead.objects.get(id=lead_id)
        form_definition = FormDefinition.objects.get(id=form_definition_id)
    except (Lead.DoesNotExist, FormDefinition.DoesNotExist):
        logger.warning(
            "Skipping form notification: lead or form definition missing",
            extra={"lead_id": lead_id, "form_definition_id": form_definition_id},
        )
        return

    if not form_definition.email_notification_enabled:
        return

    recipients = _parse_recipients(form_definition.notification_emails)
    if not recipients:
        return

    context = {"lead": lead, "form_definition": form_definition}
    subject = f"New {form_definition.name} Submission"

    try:
        html_message = render_to_string(
            "sum_core/emails/form_notification.html", context
        )
        plain_message = render_to_string(
            "sum_core/emails/form_notification.txt", context
        )
        send_mail(
            subject=subject,
            message=plain_message,
            html_message=html_message,
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@example.com"),
            recipient_list=recipients,
            fail_silently=False,
        )
    except Exception as exc:
        raise self.retry(exc=exc, countdown=RETRY_BACKOFF * (2**self.request.retries))


@shared_task(bind=True, max_retries=MAX_RETRIES)
def send_auto_reply(self, lead_id: int, form_definition_id: int) -> None:
    """Send auto-reply email to the submitter."""
    from sum_core.forms.models import FormDefinition
    from sum_core.leads.models import Lead

    try:
        lead = Lead.objects.get(id=lead_id)
        form_definition = FormDefinition.objects.get(id=form_definition_id)
    except (Lead.DoesNotExist, FormDefinition.DoesNotExist):
        logger.warning(
            "Skipping auto reply: lead or form definition missing",
            extra={"lead_id": lead_id, "form_definition_id": form_definition_id},
        )
        return

    if not form_definition.auto_reply_enabled:
        return

    submitter_email = lead.email or lead.form_data.get("email")
    if not submitter_email:
        return

    subject = form_definition.auto_reply_subject or "Thank you for contacting us"
    body = form_definition.auto_reply_body or form_definition.success_message

    name = lead.name or lead.form_data.get("name", "there")
    subject = subject.replace("{{name}}", name)
    body = body.replace("{{name}}", name)

    try:
        send_mail(
            subject=subject,
            message=body,
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@example.com"),
            recipient_list=[submitter_email],
            fail_silently=False,
        )
    except Exception as exc:
        raise self.retry(exc=exc, countdown=RETRY_BACKOFF * (2**self.request.retries))


@shared_task(bind=True, max_retries=MAX_RETRIES)
def send_webhook(self, lead_id: int, form_definition_id: int) -> None:
    """Send webhook with form submission data."""
    from sum_core.forms.models import FormDefinition
    from sum_core.leads.models import Lead

    try:
        lead = Lead.objects.get(id=lead_id)
        form_definition = FormDefinition.objects.get(id=form_definition_id)
    except (Lead.DoesNotExist, FormDefinition.DoesNotExist):
        logger.warning(
            "Skipping webhook: lead or form definition missing",
            extra={"lead_id": lead_id, "form_definition_id": form_definition_id},
        )
        return

    if not form_definition.webhook_enabled or not form_definition.webhook_url:
        return

    payload = _build_webhook_payload(lead, form_definition)

    try:
        response = requests.post(
            form_definition.webhook_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=WEBHOOK_TIMEOUT,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise self.retry(exc=exc, countdown=RETRY_BACKOFF * (2**self.request.retries))
