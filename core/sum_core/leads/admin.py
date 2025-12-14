"""
Name: Lead admin
Path: core/sum_core/leads/admin.py
Purpose: Provide minimum viable admin visibility into persisted Lead records.
Family: Lead management, admin visibility.
Dependencies: Django admin, sum_core.leads.models.Lead.
"""

from __future__ import annotations

import json

from django.contrib import admin
from django.utils.html import format_html
from django.utils.text import Truncator
from sum_core.leads.models import Lead


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    date_hierarchy = "submitted_at"
    list_display = (
        "submitted_at",
        "name",
        "email",
        "form_type",
        "source_page",
        "status",
        "is_archived",
    )
    list_filter = ("form_type", "status", "is_archived", "submitted_at")
    search_fields = ("name", "email", "phone", "message")

    readonly_fields = (
        "submitted_at",
        "name",
        "email",
        "phone",
        "message",
        "form_type",
        "source_page",
        "formatted_form_data",
    )

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "submitted_at",
                    "status",
                    "is_archived",
                )
            },
        ),
        (
            "Contact",
            {"fields": ("name", "email", "phone", "message")},
        ),
        (
            "Form",
            {"fields": ("form_type", "source_page", "formatted_form_data")},
        ),
    )

    @admin.display(description="Form data")
    def formatted_form_data(self, obj: Lead) -> str:
        pretty = json.dumps(obj.form_data or {}, indent=2, sort_keys=True)
        return format_html("<pre style='white-space: pre-wrap'>{}</pre>", pretty)

    @admin.display(description="Message")
    def short_message(self, obj: Lead) -> str:
        return Truncator(obj.message).chars(60)
