"""
Name: Branding Template Tags
Path: core/sum_core/branding/templatetags/branding_tags.py
Purpose: Exposes branding-related template tags, including access to SiteSettings.
Family: Used by Django templates to retrieve branding configuration.
Dependencies: Django template system, Wagtail Site and SiteSettings.
"""

from __future__ import annotations

from typing import Any

from django import template
from django.http import HttpRequest
from wagtail.models import Site

from sum_core.branding.models import SiteSettings

register = template.Library()


@register.simple_tag(takes_context=True)
def get_site_settings(context: dict[str, Any]) -> SiteSettings:
    """
    Return the SiteSettings for the current request/site.

    Caches per-request to avoid repeated DB hits.
    """

    request = context.get("request")
    if request is None or not isinstance(request, HttpRequest):
        raise ValueError("get_site_settings requires 'request' in the template context.")

    cached_settings = getattr(request, "_site_settings_cache", None)
    if cached_settings is not None:
        return cached_settings

    site = Site.find_for_request(request)
    if site is None:
        site = Site.objects.get(is_default_site=True)

    site_settings = SiteSettings.for_site(site)
    request._site_settings_cache = site_settings
    return site_settings
