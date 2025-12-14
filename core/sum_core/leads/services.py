"""
Name: Lead creation service
Path: core/sum_core/leads/services.py
Purpose: Persist inbound leads before any downstream side-effects (“no lost leads” invariant).
Family: Lead management, forms, integrations.
Dependencies: Django ORM, sum_core.leads.models.Lead, Wagtail Page model.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

from sum_core.leads.models import Lead
from wagtail.models import Page


def create_lead_from_submission(
    *,
    name: str,
    email: str,
    message: str,
    form_type: str,
    phone: str | None = None,
    form_data: Mapping[str, Any] | None = None,
    source_page: Page | None = None,
    post_create_hook: Callable[[Lead], None] | None = None,
) -> Lead:
    """
    Create and persist a Lead as the first durable step.

    The Lead is written to the DB before any optional downstream behaviour
    (represented by `post_create_hook`) is invoked.
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

    lead = Lead.objects.create(
        name=clean_name,
        email=clean_email,
        phone=(phone or "").strip(),
        message=clean_message,
        form_type=clean_form_type,
        form_data=dict(form_data or {}),
        source_page=source_page,
    )

    if post_create_hook is not None:
        post_create_hook(lead)

    return lead
