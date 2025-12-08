"""
Name: Branding Template Tags
Path: core/sum_core/branding/templatetags/branding_tags.py
Purpose: Exposes branding-related template tags, including access to SiteSettings and branding-driven CSS/font helpers.
Family: Used by Django templates to retrieve branding configuration and inject runtime styles.
Dependencies: Django template system, Wagtail Site and SiteSettings, Django cache.
"""

from __future__ import annotations

from typing import Any, Callable
from urllib.parse import quote_plus

from django import template
from django.conf import settings
from django.core.cache import cache
from django.http import HttpRequest
from django.utils.html import SafeString, format_html
from django.utils.safestring import mark_safe
from wagtail.models import Site

from sum_core.branding.models import SiteSettings

register = template.Library()

FONT_FALLBACK_STACK = (
    'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif'
)


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


def _format_font_value(font_name: str) -> str:
    family = font_name.strip()
    if not family:
        return ""
    return f'"{family}", {FONT_FALLBACK_STACK}'


def _build_css_variables(site_settings: SiteSettings) -> list[str]:
    color_fields = {
        "primary_color": "--color-primary",
        "secondary_color": "--color-secondary",
        "accent_color": "--color-accent",
        "background_color": "--color-background",
        "surface_color": "--color-surface",
        "surface_elevated_color": "--color-surface-elevated",
        "text_color": "--color-text",
        "text_light_color": "--color-text-light",
    }

    variables: list[str] = []

    for field_name, css_var in color_fields.items():
        value = getattr(site_settings, field_name)
        if value:
            variables.append(f"    {css_var}: {value};")

    heading_font = _format_font_value(site_settings.heading_font)
    if heading_font:
        variables.append(f"    --font-heading: {heading_font};")

    body_font = _format_font_value(site_settings.body_font)
    if body_font:
        variables.append(f"    --font-body: {body_font};")

    return variables


def _cacheable_response(cache_key: str, build: Callable[[], SafeString]) -> SafeString:
    if settings.DEBUG:
        return build()

    cached = cache.get(cache_key)
    if cached:
        return cached

    rendered = build()
    cache.set(cache_key, rendered, timeout=None)
    return rendered


@register.simple_tag(takes_context=True)
def branding_css(context: dict[str, Any]) -> SafeString:
    """
    Emit a <style> block with CSS variables sourced from SiteSettings.

    In development, the output is regenerated on every call.
    In production, the output is cached per site and invalidated on settings changes.
    """

    site_settings = get_site_settings(context)
    cache_key = f"branding_css:{site_settings.site_id}"

    def build() -> SafeString:
        variables = _build_css_variables(site_settings)
        css_lines = [":root {", *variables, "}"]
        css = mark_safe("\n".join(css_lines))
        return format_html('<style id="branding-css">\n{}\n</style>', css)

    return _cacheable_response(cache_key, build)


def _unique_fonts(site_settings: SiteSettings) -> list[str]:
    fonts = []
    for font in (site_settings.heading_font, site_settings.body_font):
        cleaned = font.strip() if font else ""
        if cleaned and cleaned not in fonts:
            fonts.append(cleaned)
    return fonts


@register.simple_tag(takes_context=True)
def branding_fonts(context: dict[str, Any]) -> SafeString:
    """
    Emit Google Fonts <link> tags for configured heading/body fonts.

    In development, the output is regenerated on every call.
    In production, the output is cached per site and invalidated on settings changes.
    """

    site_settings = get_site_settings(context)
    cache_key = f"branding_fonts:{site_settings.site_id}"

    def build() -> SafeString:
        fonts = _unique_fonts(site_settings)
        if not fonts:
            return ""

        families = "&".join(
            f"family={quote_plus(font)}:wght@400;500;700" for font in fonts
        )
        href = f"https://fonts.googleapis.com/css2?{families}&display=swap"

        links = [
            '<link rel="preconnect" href="https://fonts.googleapis.com">',
            '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>',
            f'<link rel="stylesheet" href="{href}">',
        ]

        return mark_safe("\n".join(links))

    return _cacheable_response(cache_key, build)
