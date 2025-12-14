"""
Name: seo_tags
Path: core/sum_core/seo/templatetags/seo_tags.py
Purpose: Render SEO meta + Open Graph tags with platform-standard defaults/fallbacks.
Family: base template head rendering; SEO verification tests
Dependencies: Wagtail Page, SiteSettings, SeoFieldsMixin/OpenGraphMixin
"""

from django import template
from sum_core.branding.models import SiteSettings
from wagtail.models import Page, Site

register = template.Library()


@register.inclusion_tag("sum_core/includes/seo/meta.html", takes_context=True)
def render_meta(context, page):
    """
    Renders standard SEO meta tags: title, description, robots, canonical.
    """
    request = context.get("request")

    # Resolve Site Settings/Site Name
    site = None
    if request:
        site = Site.find_for_request(request)

    # Fallback to page.get_site() if request resolution fails
    if not site and isinstance(page, Page):
        site = page.get_site()

    site_settings = SiteSettings.for_site(site) if site else None
    site_name = (site.site_name if site else "") or ""

    # 1. Title
    # Use helper if available (SeoFieldsMixin), else manual fallback
    if hasattr(page, "get_meta_title") and site_settings:
        meta_title = page.get_meta_title(site_settings)
    else:
        # Fallback for pages not using SeoFieldsMixin or missing settings
        p_title = getattr(page, "title", "")
        # Try to read meta_title directly if mixin present but no settings
        if hasattr(page, "meta_title") and page.meta_title:
            meta_title = page.meta_title
        elif hasattr(page, "seo_title") and page.seo_title:  # Wagtail default
            meta_title = page.seo_title
        else:
            meta_title = f"{p_title} | {site_name}" if site_name else p_title

    # 2. Description
    if hasattr(page, "get_meta_description"):
        meta_description = page.get_meta_description()
    else:
        meta_description = getattr(page, "search_description", "")

    # 3. Robots
    # Check for seo_noindex/seo_nofollow
    noindex = getattr(page, "seo_noindex", False)
    nofollow = getattr(page, "seo_nofollow", False)

    robots_content = []
    if noindex:
        robots_content.append("noindex")
    else:
        robots_content.append(
            "index"
        )  # Explicit index is fine, or omit. keeping implicit usually better but requirement says "variants as needed".
        # Actually usually 'noindex' or nothing (which implies index).
        # But if noindex is False, we typically don't output "index".
        # Let's clean this up.

    if nofollow:
        robots_content.append("nofollow")
    else:
        robots_content.append("follow")

    # Simplify: default is index, follow. Only output if deviating or explicit 'noindex'.
    # Actually, standard is: if noindex or nofollow is set, output meta robots.
    # If both false, we can omit or output "index, follow".
    # Requirement: "Use seo_noindex / seo_nofollow flags to build content='noindex,nofollow' variants as needed."

    robots_val = ""
    parts = []
    if noindex:
        parts.append("noindex")
    else:
        parts.append("index")

    if nofollow:
        parts.append("nofollow")
    else:
        parts.append("follow")

    robots_val = ", ".join(parts)

    # 4. Canonical
    canonical_url = ""
    if hasattr(page, "get_canonical_url"):
        canonical_url = page.get_canonical_url(request)
    elif isinstance(page, Page):
        canonical_url = page.get_full_url(request)

    return {
        "meta_title": meta_title,
        "meta_description": meta_description,
        "robots_content": robots_val,
        "canonical_url": canonical_url,
        "request": request,
    }


@register.inclusion_tag("sum_core/includes/seo/og.html", takes_context=True)
def render_og(context, page):
    """
    Renders Open Graph tags.
    """
    request = context.get("request")

    site = None
    if request:
        site = Site.find_for_request(request)
    if not site and isinstance(page, Page):
        site = page.get_site()

    site_settings = SiteSettings.for_site(site) if site else None

    # OG Title
    og_title = ""
    if hasattr(page, "get_og_title") and site_settings:
        og_title = page.get_og_title(site_settings)
    else:
        og_title = getattr(page, "title", "")

    # OG Description
    og_description = ""
    if hasattr(page, "get_og_description"):
        og_description = page.get_og_description()

    # OG Type
    og_type = "website"

    # OG URL
    og_url = ""
    if isinstance(page, Page):
        og_url = page.get_full_url(request)

    # OG Image
    og_image = None
    if hasattr(page, "get_og_image") and site_settings:
        og_image = page.get_og_image(site_settings)
    else:
        # Manual fallback chain if mixin helper missing
        # 1. page.og_image
        if hasattr(page, "og_image") and page.og_image:
            og_image = page.og_image
        # 2. page.featured_image
        elif hasattr(page, "featured_image") and page.featured_image:
            og_image = page.featured_image
        # 3. site defaults
        elif site_settings and site_settings.og_default_image:
            og_image = site_settings.og_default_image

    return {
        "og_title": og_title,
        "og_description": og_description,
        "og_type": og_type,
        "og_url": og_url,
        "og_image": og_image,
        "site_name": site.site_name if site else "",
        "request": request,
    }


@register.simple_tag(takes_context=True)
def absolute_url(context, url):
    """
    Returns the absolute URL for a given relative URL.
    Uses request from context if available.
    """
    request = context.get("request")
    if request:
        return request.build_absolute_uri(url)
    return url
