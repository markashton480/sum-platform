"""
Name: Lead async tasks
Path: core/sum_core/leads/tasks.py
Purpose: Send lead notifications and webhooks asynchronously with retries and status tracking.
Family: Leads, forms, integrations, ops visibility.
Dependencies: Celery, Django email backend, HTTP client, Lead model.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import requests
from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone

if TYPE_CHECKING:
    from sum_core.leads.models import Lead

logger = logging.getLogger(__name__)

# Retry configuration
MAX_RETRIES = 3
RETRY_BACKOFF = 60  # Base backoff in seconds (60, 120, 240)
WEBHOOK_TIMEOUT = 10  # seconds


def build_lead_notification_context(lead: Lead) -> dict:
    """
    Build template context for lead notification email.

    Args:
        lead: The Lead instance to build context for.

    Returns:
        Dictionary with all context variables for email templates.
    """
    return {
        "lead_id": lead.id,
        "name": lead.name,
        "email": lead.email,
        "phone": lead.phone,
        "message": lead.message,
        "form_type": lead.form_type,
        "submitted_at": lead.submitted_at,
        "page_url": lead.page_url,
        "referrer_url": lead.referrer_url,
        "lead_source": lead.lead_source,
        "lead_source_display": lead.get_lead_source_display()
        if lead.lead_source
        else "",
        "lead_source_detail": lead.lead_source_detail,
        "utm_source": lead.utm_source,
        "utm_medium": lead.utm_medium,
        "utm_campaign": lead.utm_campaign,
        "utm_term": lead.utm_term,
        "utm_content": lead.utm_content,
        "landing_page_url": lead.landing_page_url,
        "site_name": getattr(settings, "WAGTAIL_SITE_NAME", ""),
    }


def build_webhook_payload(lead: Lead) -> dict:
    """
    Build JSON payload for webhook POST matching SSOT schema.

    Args:
        lead: The Lead instance to build payload for.

    Returns:
        Dictionary matching the SSOT webhook payload schema.
    """
    return {
        "lead_id": lead.id,
        "name": lead.name,
        "email": lead.email,
        "phone": lead.phone,
        "message": lead.message,
        "form_type": lead.form_type,
        "form_data": lead.form_data,
        "lead_source": lead.lead_source,
        "utm_source": lead.utm_source,
        "utm_medium": lead.utm_medium,
        "utm_campaign": lead.utm_campaign,
        "page_url": lead.page_url,
        "submitted_at": lead.submitted_at.isoformat() if lead.submitted_at else None,
    }


@shared_task(
    bind=True,
    max_retries=MAX_RETRIES,
    default_retry_delay=RETRY_BACKOFF,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=300,
)
def send_lead_notification(self, lead_id: int) -> None:
    """
    Send email notification for a new lead.

    This task is idempotent and concurrency-safe - uses select_for_update()
    to prevent duplicate sends under concurrent execution.

    Args:
        lead_id: The ID of the Lead to send notification for.
    """
    from django.db import transaction
    from sum_core.leads.models import EmailStatus, Lead

    # Use select_for_update within a transaction for concurrency safety
    with transaction.atomic():
        try:
            lead = Lead.objects.select_for_update(nowait=False).get(id=lead_id)
        except Lead.DoesNotExist:
            logger.error(f"Lead {lead_id} not found for email notification")
            return

        # Idempotency check - don't resend if already sent (with lock held)
        if lead.email_status == EmailStatus.SENT:
            logger.info(f"Lead {lead_id} email already sent, skipping")
            return

        # Get notification email address
        notification_email = getattr(settings, "LEAD_NOTIFICATION_EMAIL", "")
        if not notification_email:
            logger.warning(
                f"No LEAD_NOTIFICATION_EMAIL configured, skipping lead {lead_id}"
            )
            lead.email_status = EmailStatus.FAILED
            lead.email_last_error = "No notification email address configured"
            lead.email_attempts += 1
            lead.save(
                update_fields=["email_status", "email_last_error", "email_attempts"]
            )
            return

        # Build email context and render templates
        context = build_lead_notification_context(lead)

        try:
            subject = render_to_string(
                "sum_core/emails/lead_notification_subject.txt", context
            ).strip()
            body = render_to_string(
                "sum_core/emails/lead_notification_body.txt", context
            )

            # Send the email
            send_mail(
                subject=subject,
                message=body,
                from_email=getattr(
                    settings, "DEFAULT_FROM_EMAIL", "noreply@example.com"
                ),
                recipient_list=[notification_email],
                fail_silently=False,
            )

            # Update status on success (within transaction - lock still held)
            lead.email_status = EmailStatus.SENT
            lead.email_sent_at = timezone.now()
            lead.email_attempts += 1
            lead.email_last_error = ""
            lead.save(
                update_fields=[
                    "email_status",
                    "email_sent_at",
                    "email_attempts",
                    "email_last_error",
                ]
            )
            logger.info(f"Lead {lead_id} email notification sent successfully")

        except Exception as e:
            # Update status on failure
            lead.email_attempts += 1
            lead.email_last_error = str(e)[:500]

            # Check if we should retry
            if self.request.retries < MAX_RETRIES:
                lead.save(update_fields=["email_attempts", "email_last_error"])
                logger.warning(
                    f"Lead {lead_id} email failed (attempt {lead.email_attempts}): {e}"
                )
                raise  # Trigger retry
            else:
                # Max retries reached, mark as failed
                lead.email_status = EmailStatus.FAILED
                lead.save(
                    update_fields=[
                        "email_status",
                        "email_attempts",
                        "email_last_error",
                    ]
                )
                logger.error(
                    f"Lead {lead_id} email failed permanently after "
                    f"{lead.email_attempts} attempts: {e}"
                )


@shared_task(
    bind=True,
    max_retries=MAX_RETRIES,
    default_retry_delay=RETRY_BACKOFF,
    autoretry_for=(requests.RequestException,),
    retry_backoff=True,
    retry_backoff_max=300,
)
def send_lead_webhook(self, lead_id: int) -> None:
    """
    Send webhook notification for a new lead.

    This task is idempotent and concurrency-safe - uses select_for_update()
    to prevent duplicate sends under concurrent execution.

    If no webhook URL is configured, the status is set to 'disabled'.

    Args:
        lead_id: The ID of the Lead to send webhook for.
    """
    from django.db import transaction
    from sum_core.leads.models import Lead, WebhookStatus

    # Use select_for_update within a transaction for concurrency safety
    with transaction.atomic():
        try:
            lead = Lead.objects.select_for_update(nowait=False).get(id=lead_id)
        except Lead.DoesNotExist:
            logger.error(f"Lead {lead_id} not found for webhook notification")
            return

        # Idempotency check - don't resend if already sent (with lock held)
        if lead.webhook_status == WebhookStatus.SENT:
            logger.info(f"Lead {lead_id} webhook already sent, skipping")
            return

        # Check if webhook URL is configured
        webhook_url = getattr(settings, "ZAPIER_WEBHOOK_URL", "")
        if not webhook_url:
            lead.webhook_status = WebhookStatus.DISABLED
            lead.save(update_fields=["webhook_status"])
            logger.info(f"Lead {lead_id} webhook disabled (no URL configured)")
            return

        # Build JSON payload
        payload = build_webhook_payload(lead)

        try:
            response = requests.post(
                webhook_url,
                json=payload,
                timeout=WEBHOOK_TIMEOUT,
                headers={"Content-Type": "application/json"},
            )
            lead.webhook_last_status_code = response.status_code
            lead.webhook_attempts += 1

            if response.ok:
                # Success (2xx status) - mark sent within transaction
                lead.webhook_status = WebhookStatus.SENT
                lead.webhook_sent_at = timezone.now()
                lead.webhook_last_error = ""
                lead.save(
                    update_fields=[
                        "webhook_status",
                        "webhook_sent_at",
                        "webhook_attempts",
                        "webhook_last_status_code",
                        "webhook_last_error",
                    ]
                )
                logger.info(f"Lead {lead_id} webhook sent successfully")
            else:
                # Non-2xx response - treat as failure
                lead.webhook_last_error = (
                    f"HTTP {response.status_code}: {response.text[:200]}"
                )

                if self.request.retries < MAX_RETRIES:
                    lead.save(
                        update_fields=[
                            "webhook_attempts",
                            "webhook_last_status_code",
                            "webhook_last_error",
                        ]
                    )
                    logger.warning(
                        f"Lead {lead_id} webhook failed "
                        f"(attempt {lead.webhook_attempts}): "
                        f"HTTP {response.status_code}"
                    )
                    raise requests.RequestException(lead.webhook_last_error)
                else:
                    lead.webhook_status = WebhookStatus.FAILED
                    lead.save(
                        update_fields=[
                            "webhook_status",
                            "webhook_attempts",
                            "webhook_last_status_code",
                            "webhook_last_error",
                        ]
                    )
                    logger.error(
                        f"Lead {lead_id} webhook failed permanently: "
                        f"HTTP {response.status_code}"
                    )

        except requests.Timeout as e:
            lead.webhook_attempts += 1
            lead.webhook_last_error = f"Request timeout: {str(e)[:200]}"

            if self.request.retries < MAX_RETRIES:
                lead.save(update_fields=["webhook_attempts", "webhook_last_error"])
                logger.warning(
                    f"Lead {lead_id} webhook timeout "
                    f"(attempt {lead.webhook_attempts})"
                )
                raise
            else:
                lead.webhook_status = WebhookStatus.FAILED
                lead.save(
                    update_fields=[
                        "webhook_status",
                        "webhook_attempts",
                        "webhook_last_error",
                    ]
                )
                logger.error(f"Lead {lead_id} webhook failed permanently: timeout")

        except requests.RequestException as e:
            lead.webhook_attempts += 1
            lead.webhook_last_error = str(e)[:500]

            if self.request.retries < MAX_RETRIES:
                lead.save(update_fields=["webhook_attempts", "webhook_last_error"])
                logger.warning(
                    f"Lead {lead_id} webhook failed "
                    f"(attempt {lead.webhook_attempts}): {e}"
                )
                raise
            else:
                lead.webhook_status = WebhookStatus.FAILED
                lead.save(
                    update_fields=[
                        "webhook_status",
                        "webhook_attempts",
                        "webhook_last_error",
                    ]
                )
                logger.error(f"Lead {lead_id} webhook failed permanently: {e}")


# Zapier-specific retry configuration (M4-007)
ZAPIER_MAX_RETRIES = 5
ZAPIER_RETRY_BACKOFF = 60  # Base backoff in seconds


@shared_task(
    bind=True,
    max_retries=ZAPIER_MAX_RETRIES,
    default_retry_delay=ZAPIER_RETRY_BACKOFF,
    autoretry_for=(requests.RequestException,),
    retry_backoff=True,
    retry_backoff_max=600,
)
def send_zapier_webhook(self, lead_id: int, site_id: int) -> None:
    """
    Send Zapier webhook for a new lead using per-site configuration.

    This task is idempotent and concurrency-safe - uses select_for_update()
    to prevent duplicate sends under concurrent execution (CM-001 pattern).

    If Zapier is not configured for the site, the status is set to 'disabled'.

    Args:
        lead_id: The ID of the Lead to send webhook for.
        site_id: The ID of the Wagtail Site to fetch Zapier config from.
    """
    from django.db import transaction
    from sum_core.branding.models import SiteSettings
    from sum_core.integrations.zapier import build_zapier_payload, send_zapier_request
    from sum_core.leads.models import Lead, ZapierStatus
    from wagtail.models import Site

    # Use select_for_update within a transaction for concurrency safety
    with transaction.atomic():
        try:
            lead = Lead.objects.select_for_update(nowait=False).get(id=lead_id)
        except Lead.DoesNotExist:
            logger.error(f"Lead {lead_id} not found for Zapier webhook")
            return

        # Idempotency check - don't resend if already sent (with lock held)
        if lead.zapier_status == ZapierStatus.SENT:
            logger.info(f"Lead {lead_id} Zapier webhook already sent, skipping")
            return

        # Get site and settings
        try:
            site = Site.objects.get(id=site_id)
        except Site.DoesNotExist:
            logger.error(f"Site {site_id} not found for Zapier webhook, lead {lead_id}")
            lead.zapier_status = ZapierStatus.FAILED
            lead.zapier_last_error = f"Site {site_id} not found"
            lead.save(update_fields=["zapier_status", "zapier_last_error"])
            return

        # Get SiteSettings for Zapier configuration
        try:
            site_settings = SiteSettings.for_site(site)
        except SiteSettings.DoesNotExist:
            logger.info(f"Lead {lead_id} Zapier disabled (no SiteSettings)")
            lead.zapier_status = ZapierStatus.DISABLED
            lead.save(update_fields=["zapier_status"])
            return

        # Check if Zapier is enabled and URL is configured
        if not site_settings.zapier_enabled or not site_settings.zapier_webhook_url:
            logger.info(
                f"Lead {lead_id} Zapier disabled (enabled={site_settings.zapier_enabled}, "
                f"url_set={bool(site_settings.zapier_webhook_url)})"
            )
            lead.zapier_status = ZapierStatus.DISABLED
            lead.save(update_fields=["zapier_status"])
            return

        # Build payload and send request
        payload = build_zapier_payload(lead, site)
        result = send_zapier_request(site_settings.zapier_webhook_url, payload)

        # Update attempt tracking
        lead.zapier_attempt_count += 1
        lead.zapier_last_attempt_at = timezone.now()

        if result.success:
            # Success - mark sent within transaction
            lead.zapier_status = ZapierStatus.SENT
            lead.zapier_last_error = ""
            lead.save(
                update_fields=[
                    "zapier_status",
                    "zapier_attempt_count",
                    "zapier_last_attempt_at",
                    "zapier_last_error",
                ]
            )
            logger.info(f"Lead {lead_id} Zapier webhook sent successfully")
        else:
            # Failure - record error and potentially retry
            lead.zapier_last_error = result.error_message[:500]

            if self.request.retries < ZAPIER_MAX_RETRIES:
                lead.save(
                    update_fields=[
                        "zapier_attempt_count",
                        "zapier_last_attempt_at",
                        "zapier_last_error",
                    ]
                )
                logger.warning(
                    f"Lead {lead_id} Zapier webhook failed "
                    f"(attempt {lead.zapier_attempt_count}): {result.error_message}"
                )
                # Raise to trigger Celery retry
                raise requests.RequestException(result.error_message)
            else:
                # Max retries reached, mark as failed
                lead.zapier_status = ZapierStatus.FAILED
                lead.save(
                    update_fields=[
                        "zapier_status",
                        "zapier_attempt_count",
                        "zapier_last_attempt_at",
                        "zapier_last_error",
                    ]
                )
                logger.error(
                    f"Lead {lead_id} Zapier webhook failed permanently after "
                    f"{lead.zapier_attempt_count} attempts: {result.error_message}"
                )
