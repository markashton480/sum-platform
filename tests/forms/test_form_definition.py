"""
Name: FormDefinition model tests
Path: tests/forms/test_form_definition.py
Purpose: Validate FormDefinition snippet creation, constraints, and validations.
Family: Forms, Dynamic Forms foundation.
Dependencies: pytest, Django ORM, Wagtail Site fixtures.
"""

from __future__ import annotations

import pytest
from django.core.exceptions import ValidationError
from sum_core.forms.models import FormDefinition


@pytest.mark.django_db
def test_can_create_form_definition(wagtail_default_site):
    """Model should save with defaults and __str__ should match name."""
    form_def = FormDefinition.objects.create(
        site=wagtail_default_site,
        name="Contact Form",
        slug="contact",
    )

    assert form_def.pk is not None
    assert form_def.success_message == "Thank you for your submission!"
    assert form_def.is_active is True
    assert str(form_def) == "Contact Form"


@pytest.mark.django_db
def test_slug_unique_per_site(wagtail_default_site):
    """Slug must be unique per site."""
    FormDefinition.objects.create(
        site=wagtail_default_site,
        name="Contact Form",
        slug="contact",
    )

    duplicate = FormDefinition(
        site=wagtail_default_site,
        name="Contact Form Duplicate",
        slug="contact",
    )

    with pytest.raises(ValidationError):
        duplicate.full_clean()


@pytest.mark.django_db
def test_is_active_toggle(wagtail_default_site):
    """is_active flag should toggle on/off."""
    form_def = FormDefinition.objects.create(
        site=wagtail_default_site,
        name="Quote Form",
        slug="quote",
        is_active=False,
    )

    assert form_def.is_active is False
    form_def.is_active = True
    form_def.save(update_fields=["is_active"])
    form_def.refresh_from_db()
    assert form_def.is_active is True


@pytest.mark.django_db
def test_notification_emails_validation(wagtail_default_site):
    """Invalid email addresses should raise validation errors."""
    form_def = FormDefinition(
        site=wagtail_default_site,
        name="Support Form",
        slug="support",
        notification_emails="invalid-email, support@example.com",
    )

    with pytest.raises(ValidationError):
        form_def.full_clean()


@pytest.mark.django_db
def test_notification_emails_accepts_valid_list(wagtail_default_site):
    """Valid comma-separated emails should pass validation."""
    form_def = FormDefinition(
        site=wagtail_default_site,
        name="Newsletter Form",
        slug="newsletter",
        notification_emails="admin@example.com, support@example.com",
    )

    form_def.full_clean()
    assert form_def.notification_emails == "admin@example.com, support@example.com"


@pytest.mark.django_db
def test_webhook_requires_url_when_enabled(wagtail_default_site):
    """Webhook URL is required when webhook delivery is enabled."""
    form_def = FormDefinition(
        site=wagtail_default_site,
        name="Feedback Form",
        slug="feedback",
        webhook_enabled=True,
        webhook_url="",
    )

    with pytest.raises(ValidationError):
        form_def.full_clean()


@pytest.mark.django_db
def test_webhook_accepts_valid_url_when_enabled(wagtail_default_site):
    """Valid webhook URL should pass validation when enabled."""
    form_def = FormDefinition(
        site=wagtail_default_site,
        name="API Form",
        slug="api-form",
        webhook_enabled=True,
        webhook_url="https://api.example.com/webhook",
    )

    form_def.full_clean()
    assert form_def.webhook_url == "https://api.example.com/webhook"


@pytest.mark.django_db
def test_auto_reply_fields_persist(wagtail_default_site):
    """Auto-reply fields should store provided values."""
    form_def = FormDefinition.objects.create(
        site=wagtail_default_site,
        name="Auto Reply Form",
        slug="auto-reply",
        auto_reply_enabled=True,
        auto_reply_subject="Thanks for reaching out",
        auto_reply_body="We'll get back to you shortly.",
    )

    form_def.refresh_from_db()
    assert form_def.auto_reply_enabled is True
    assert form_def.auto_reply_subject == "Thanks for reaching out"
    assert form_def.auto_reply_body == "We'll get back to you shortly."
