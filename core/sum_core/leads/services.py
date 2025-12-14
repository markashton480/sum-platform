"""
Name: Lead creation service
Path: core/sum_core/leads/services.py
Purpose: Persist inbound leads before any downstream side-effects ("no lost leads" invariant).
Family: Lead management, forms, integrations.
Dependencies: Django ORM, sum_core.leads.models.Lead, Wagtail Page model.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any

from sum_core.leads.attribution import derive_lead_source
from sum_core.leads.models import Lead
from wagtail.models import Page


@dataclass
class AttributionData:
    """
    Container for lead attribution inputs.

    All fields are optional; empty strings are treated as "not provided".
    """

    utm_source: str = ""
    utm_medium: str = ""
    utm_campaign: str = ""
    utm_term: str = ""
    utm_content: str = ""
    landing_page_url: str = ""
    page_url: str = ""
    referrer_url: str = ""


def create_lead_from_submission(
    *,
    name: str,
    email: str,
    message: str,
    form_type: str,
    phone: str | None = None,
    form_data: Mapping[str, Any] | None = None,
    source_page: Page | None = None,
    attribution: AttributionData | None = None,
    post_create_hook: Callable[[Lead], None] | None = None,
) -> Lead:
    """
    Create and persist a Lead as the first durable step.

    The Lead is written to the DB before any optional downstream behaviour
    (represented by `post_create_hook`) is invoked.

    Args:
        name: Contact name (required)
        email: Contact email (required)
        message: Message content (required)
        form_type: Form identifier e.g. 'contact', 'quote' (required)
        phone: Contact phone (optional)
        form_data: Additional form fields as dict (optional)
        source_page: Wagtail page where form was submitted (optional)
        attribution: Attribution data containing UTMs/URLs (optional)
        post_create_hook: Callback invoked after Lead is persisted (optional)

    Returns:
        The created Lead instance

    Raises:
        ValueError: If required fields are empty
    """
    clean_name = name.strip()
    clean_email = email.strip()
    clean_message = message.strip()
    clean_form_type = form_type.strip()

    if not clean_name:
        raise ValueError("name is required")
    if not clean_email:
        raise ValueError("email is required")
    if not clean_message:
        raise ValueError("message is required")
    if not clean_form_type:
        raise ValueError("form_type is required")

    # Prepare attribution fields
    attr = attribution or AttributionData()
    utm_source = attr.utm_source.strip()
    utm_medium = attr.utm_medium.strip()
    utm_campaign = attr.utm_campaign.strip()
    utm_term = attr.utm_term.strip()
    utm_content = attr.utm_content.strip()
    landing_page_url = attr.landing_page_url.strip()
    page_url = attr.page_url.strip()
    referrer_url = attr.referrer_url.strip()

    # Derive lead_source using canonical function
    lead_source, lead_source_detail = derive_lead_source(
        utm_source=utm_source,
        utm_medium=utm_medium,
        utm_campaign=utm_campaign,
        referrer_url=referrer_url,
    )

    # Create Lead record first (durable persistence)
    lead = Lead.objects.create(
        # Core fields
        name=clean_name,
        email=clean_email,
        phone=(phone or "").strip(),
        message=clean_message,
        form_type=clean_form_type,
        form_data=dict(form_data or {}),
        source_page=source_page,
        # Attribution fields
        utm_source=utm_source,
        utm_medium=utm_medium,
        utm_campaign=utm_campaign,
        utm_term=utm_term,
        utm_content=utm_content,
        landing_page_url=landing_page_url,
        page_url=page_url,
        referrer_url=referrer_url,
        # Derived fields
        lead_source=lead_source,
        lead_source_detail=lead_source_detail,
    )

    # Invoke hook after Lead is safely persisted
    if post_create_hook is not None:
        post_create_hook(lead)

    return lead
