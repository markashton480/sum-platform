"""
Name: Branding Site Settings
Path: core/sum_core/branding/models.py
Purpose: Provides Wagtail SiteSettings for branding and business configuration shared across client sites.
Family: Used by template tags and frontend templates (branding_css, branding_fonts, base layouts).
Dependencies: Django models, Wagtail settings framework, wagtailimages, Django cache.
"""

from __future__ import annotations

from typing import Any

from django.core.cache import cache
from django.db import models
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting


@register_setting
class SiteSettings(BaseSiteSetting):
    primary_color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Primary brand colour in hex format (e.g. #0055ff).",
    )
    secondary_color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Secondary brand colour in hex format (e.g. #f97316).",
    )
    accent_color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Accent brand colour in hex format (e.g. #10b981).",
    )
    background_color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Background colour for pages (e.g. #ffffff).",
    )
    text_color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Default text colour (e.g. #0f172a).",
    )
    surface_color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Surface colour for cards and panels (e.g. #f8fafc).",
    )
    surface_elevated_color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Elevated surface colour for layered elements.",
    )
    text_light_color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Subtle text colour for muted labels.",
    )
    header_logo = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    footer_logo = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    favicon = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    heading_font = models.CharField(
        max_length=100,
        blank=True,
        help_text="Google Fonts family name for headings.",
    )
    body_font = models.CharField(
        max_length=100,
        blank=True,
        help_text="Google Fonts family name for body text.",
    )
    company_name = models.CharField(
        max_length=255,
        blank=True,
        help_text="Company or brand name displayed across the site.",
    )
    tagline = models.CharField(
        max_length=255,
        blank=True,
        help_text="Short tagline or strapline.",
    )
    phone_number = models.CharField(
        max_length=50,
        blank=True,
        help_text="Primary contact phone number.",
    )
    email = models.EmailField(
        blank=True,
        help_text="Primary contact email address.",
    )
    address = models.TextField(
        blank=True,
        help_text="Postal address displayed in footers or contact sections.",
    )
    business_hours = models.TextField(
        blank=True,
        help_text="Business hours text (free-form).",
    )
    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    tiktok_url = models.URLField(blank=True)

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("primary_color"),
                FieldPanel("secondary_color"),
                FieldPanel("accent_color"),
                FieldPanel("background_color"),
                FieldPanel("surface_color"),
                FieldPanel("surface_elevated_color"),
                FieldPanel("text_color"),
                FieldPanel("text_light_color"),
            ],
            heading="Brand Colours",
        ),
        MultiFieldPanel(
            [
                FieldPanel("header_logo"),
                FieldPanel("footer_logo"),
                FieldPanel("favicon"),
            ],
            heading="Logos & Favicon",
        ),
        MultiFieldPanel(
            [
                FieldPanel("heading_font"),
                FieldPanel("body_font"),
            ],
            heading="Typography",
        ),
        MultiFieldPanel(
            [
                FieldPanel("company_name"),
                FieldPanel("tagline"),
                FieldPanel("phone_number"),
                FieldPanel("email"),
                FieldPanel("address"),
                FieldPanel("business_hours"),
            ],
            heading="Business Info",
        ),
        MultiFieldPanel(
            [
                FieldPanel("facebook_url"),
                FieldPanel("instagram_url"),
                FieldPanel("linkedin_url"),
                FieldPanel("twitter_url"),
                FieldPanel("youtube_url"),
                FieldPanel("tiktok_url"),
            ],
            heading="Social Links",
        ),
    ]

    class Meta:
        verbose_name = "Site settings"
        verbose_name_plural = "Site settings"

    def __str__(self) -> str:  # pragma: no cover - admin display helper
        return self.company_name or "Site settings"

    def _invalidate_branding_cache(self) -> None:
        cache.delete(f"branding_css:{self.site_id}")
        cache.delete(f"branding_fonts:{self.site_id}")

    def save(self, *args: Any, **kwargs: Any) -> None:
        super().save(*args, **kwargs)
        self._invalidate_branding_cache()

    def delete(self, *args: Any, **kwargs: Any) -> None:
        site_id = self.site_id
        super().delete(*args, **kwargs)
        cache.delete(f"branding_css:{site_id}")
        cache.delete(f"branding_fonts:{site_id}")
