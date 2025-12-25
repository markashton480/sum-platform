"""
Name: Form configuration model
Path: core/sum_core/forms/models.py
Purpose: Per-site form settings for spam protection, rate limiting, and notifications.
Family: Forms, Leads, Spam Protection.
Dependencies: Django ORM, Wagtail Site.
"""

from __future__ import annotations

from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.db import models
from sum_core.forms.fields import FormFieldsStreamBlock
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import StreamField
from wagtail.models import Site
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.chooser import SnippetChooserViewSet
from wagtail.snippets.views.snippets import SnippetViewSet


class FormConfiguration(models.Model):
    """
    Per-site form configuration for spam protection and behaviour.

    Each Wagtail Site can have its own FormConfiguration to control:
    - Honeypot field name
    - Rate limiting thresholds
    - Minimum submission time (anti-bot timing check)
    - Notification email address
    """

    site = models.OneToOneField(
        Site,
        on_delete=models.CASCADE,
        related_name="form_configuration",
        help_text="The site this configuration applies to.",
    )

    # Spam protection: Honeypot
    honeypot_field_name = models.CharField(
        max_length=50,
        default="company",
        help_text="Name of the honeypot field. If filled, submission is rejected as spam.",
    )

    # Spam protection: Rate limiting
    rate_limit_per_ip_per_hour = models.PositiveIntegerField(
        default=20,
        help_text="Maximum form submissions allowed per IP address per hour.",
    )

    # Spam protection: Timing
    min_seconds_to_submit = models.PositiveIntegerField(
        default=3,
        help_text="Minimum seconds between form render and submission. Faster submissions are rejected.",
    )

    # Notifications
    lead_notification_email = models.EmailField(
        blank=True,
        help_text="Email address for lead notifications. If blank, falls back to environment variable.",
    )

    # Presentation metadata
    default_form_type = models.CharField(
        max_length=50,
        blank=True,
        help_text="Default form type if not specified in submission.",
    )

    class Meta:
        verbose_name = "Form Configuration"
        verbose_name_plural = "Form Configurations"

    def __str__(self) -> str:
        return f"Form Configuration for {self.site.hostname}"

    @classmethod
    def get_for_site(cls, site: Site) -> FormConfiguration:
        """
        Get or create FormConfiguration for a site.

        Returns the existing configuration or a new instance with defaults.
        The returned instance is always saved to the database.
        """
        from typing import cast

        config, _created = cls.objects.get_or_create(site=site)
        return cast(FormConfiguration, config)

    @classmethod
    def get_defaults(cls) -> dict:
        """Return default configuration values for use when no config exists."""
        return {
            "honeypot_field_name": "company",
            "rate_limit_per_ip_per_hour": 20,
            "min_seconds_to_submit": 3,
        }


def validate_comma_separated_emails(value: str) -> None:
    """Validate comma-separated email addresses."""
    if not value:
        return

    validator = EmailValidator()
    errors: list[str] = []

    for raw_email in value.split(","):
        email = raw_email.strip()
        if not email:
            errors.append("Email addresses must not be empty when separated by commas.")
            continue

        try:
            validator(email)
        except ValidationError:
            errors.append(f"'{email}' is not a valid email address.")

    if errors:
        raise ValidationError(errors)


class FormDefinition(models.Model):
    """
    Reusable form definition for dynamic forms.

    Supports multi-site configuration, notifications, and webhook delivery.
    """

    site = models.ForeignKey(
        Site,
        on_delete=models.CASCADE,
        related_name="form_definitions",
        help_text="Site this form definition belongs to.",
    )
    name = models.CharField(
        max_length=255,
        help_text="Reference name used in the admin.",
    )
    slug = models.SlugField(
        max_length=100,
        help_text="Unique identifier for this form within the site.",
    )
    fields = StreamField(
        FormFieldsStreamBlock(required=False),
        blank=True,
        use_json_field=True,
        help_text="Form field blocks for dynamic forms.",
    )
    success_message = models.TextField(
        default="Thank you for your submission!",
        help_text="Message shown after successful submission.",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Deactivate to hide this form without deleting it.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Notifications
    email_notification_enabled = models.BooleanField(
        default=True,
        help_text="Send notification emails on submission.",
    )
    notification_emails = models.TextField(
        blank=True,
        validators=[validate_comma_separated_emails],
        help_text="Comma-separated list of recipient emails.",
    )
    auto_reply_enabled = models.BooleanField(
        default=False,
        help_text="Send auto-reply to the submitter.",
    )
    auto_reply_subject = models.CharField(
        max_length=255,
        blank=True,
        help_text="Subject for auto-reply emails.",
    )
    auto_reply_body = models.TextField(
        blank=True,
        help_text="Body content for auto-reply emails.",
    )

    # Webhooks
    webhook_enabled = models.BooleanField(
        default=False,
        help_text="Send webhook on submission.",
    )
    webhook_url = models.URLField(
        blank=True,
        help_text="Endpoint to receive submission payloads.",
    )

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("site"),
                FieldPanel("name"),
                FieldPanel("slug"),
            ],
            heading="Basic Settings",
        ),
        MultiFieldPanel(
            [FieldPanel("fields")],
            heading="Form Fields",
        ),
        MultiFieldPanel(
            [FieldPanel("success_message")],
            heading="Submission Settings",
        ),
        MultiFieldPanel(
            [
                FieldPanel("email_notification_enabled"),
                FieldPanel("notification_emails"),
                FieldPanel("auto_reply_enabled"),
                FieldPanel("auto_reply_subject"),
                FieldPanel("auto_reply_body"),
            ],
            heading="Notifications",
        ),
        MultiFieldPanel(
            [
                FieldPanel("webhook_enabled"),
                FieldPanel("webhook_url"),
            ],
            heading="Webhooks",
        ),
        MultiFieldPanel(
            [
                FieldPanel("is_active"),
            ],
            heading="Status",
        ),
    ]

    class Meta:
        verbose_name = "Form Definition"
        verbose_name_plural = "Form Definitions"
        unique_together = [("site", "slug")]
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return str(self.name)

    def clean(self) -> None:
        """Validate notification emails and webhook configuration."""
        errors = {}

        if self.webhook_enabled and not self.webhook_url:
            errors["webhook_url"] = ValidationError(
                "Webhook URL is required when webhooks are enabled."
            )

        if errors:
            raise ValidationError(errors)

        super().clean()


class ActiveFormDefinitionChooserViewSet(SnippetChooserViewSet):
    """Limit chooser options to active form definitions."""

    def get_object_list(self):
        return self.model.objects.filter(is_active=True)


class FormDefinitionViewSet(SnippetViewSet):
    """Wagtail Snippet viewset for managing form definitions."""

    model = FormDefinition
    icon = "form"
    menu_label = "Form Definitions"
    list_display = ["name", "slug", "is_active", "created_at"]
    list_filter = ["is_active", "site"]
    search_fields = ["name", "slug"]
    panels = FormDefinition.panels
    chooser_viewset_class = ActiveFormDefinitionChooserViewSet


register_snippet(FormDefinitionViewSet)
