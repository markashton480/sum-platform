"""
Name: Lead persistence
Path: core/sum_core/leads/models.py
Purpose: Store all inbound leads reliably (“no lost leads” invariant).
Family: Lead management, forms, integrations, admin visibility.
Dependencies: Django ORM, Wagtail Page model.
"""

from __future__ import annotations

from django.db import models
from wagtail.models import Page


class Lead(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "New"
        CONTACTED = "contacted", "Contacted"
        QUOTED = "quoted", "Quoted"
        WON = "won", "Won"
        LOST = "lost", "Lost"

    name: models.CharField = models.CharField(max_length=100)
    email: models.EmailField = models.EmailField()
    phone: models.CharField = models.CharField(
        max_length=20,
        blank=True,
    )
    message: models.TextField = models.TextField()

    form_type: models.CharField = models.CharField(
        max_length=50,
        help_text="Form identifier (e.g. 'contact', 'quote').",
    )
    form_data: models.JSONField = models.JSONField(default=dict)

    source_page: models.ForeignKey = models.ForeignKey(
        Page,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="leads",
    )

    submitted_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    status: models.CharField = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
    )
    is_archived: models.BooleanField = models.BooleanField(default=False)

    class Meta:
        ordering = ["-submitted_at"]

    def __str__(self) -> str:
        return f"{self.name} <{self.email}> ({self.form_type})"
