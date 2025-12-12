"""
Name: Navigation Template Tags
Path: core/sum_core/navigation/templatetags/navigation_tags.py
Purpose: Provide template tags for rendering header, footer, and sticky CTA navigation.
Family: Navigation System (Phase 1: Foundation)
Dependencies: django.template, django.core.cache, wagtail.models, sum_core.navigation

Tags:
    - header_nav: Returns header menu context with active detection
    - footer_nav: Returns footer links, social, business info, and copyright
    - sticky_cta: Returns mobile sticky CTA bar configuration
"""

from __future__ import annotations

import re
from collections.abc import Callable
from datetime import datetime
from typing import TYPE_CHECKING, Any

from django import template
from django.conf import settings
from django.core.cache import cache
from sum_core.navigation.cache import get_nav_cache_key
from sum_core.navigation.models import FooterNavigation
from sum_core.navigation.services import (
    get_effective_footer_settings,
    get_effective_header_settings,
)
from wagtail.models import Page, Site

if TYPE_CHECKING:
    from django.http import HttpRequest

register = template.Library()

# =============================================================================
# Constants
# =============================================================================

CACHE_TTL_DEFAULT = 3600  # 1 hour in seconds
CACHE_KEY_PREFIX = "nav"

# Phone number cleaning pattern - strips non-digits except leading +
PHONE_CLEAN_PATTERN = re.compile(r"[^\d+]")


# =============================================================================
# Cache Helpers
# =============================================================================


def _get_cache_ttl() -> int:
    """Get cache TTL from settings or use default (1 hour)."""
    return getattr(settings, "NAV_CACHE_TTL", CACHE_TTL_DEFAULT)


def _make_cache_key(tag_name: str, site_id: int) -> str:
    """
    Build a site-specific cache key matching spec format.

    Delegates to shared helper to prevent key format drift.
    """
    return get_nav_cache_key(site_id, tag_name)


def _cache_get_or_build(
    cache_key: str, builder: Callable[[], dict[str, Any]]
) -> dict[str, Any]:
    """
    Read-through cache: return cached dict on hit, or build→store→return on miss.

    Falls back gracefully to builder if cache fails.
    """
    try:
        cached = cache.get(cache_key)
        if cached is not None:
            return cached
    except Exception:
        # Cache backend failed, continue to build
        pass

    result = builder()

    try:
        cache.set(cache_key, result, timeout=_get_cache_ttl())
    except Exception:
        # Cache write failed, just return the result
        pass

    return result


# =============================================================================
# Link Extraction Helpers
# =============================================================================


def _normalize_phone_href(phone_number: str | None) -> str:
    """Clean phone number to tel: href format."""
    if not phone_number:
        return ""
    # Strip non-digits except leading +
    if phone_number.startswith("+"):
        cleaned = "+" + PHONE_CLEAN_PATTERN.sub("", phone_number[1:])
    else:
        cleaned = PHONE_CLEAN_PATTERN.sub("", phone_number)
    return f"tel:{cleaned}" if cleaned else ""


def _extract_link_data(link_value: Any) -> dict[str, Any]:
    """
    Extract link metadata from a UniversalLinkValue or raw dict.

    Returns dict with: href, text, is_external, opens_new_tab, attrs, attrs_str

    Handles both:
    - UniversalLinkValue objects (from proper StreamField loading)
    - Raw dicts (from tests or JSON data)
    """
    if link_value is None:
        return {
            "href": "#",
            "text": "",
            "is_external": False,
            "opens_new_tab": False,
            "attrs": {},
            "attrs_str": "",
        }

    # Check if it has computed properties (UniversalLinkValue)
    # Properties aren't callable, so check for property descriptor on the class
    href_attr = getattr(type(link_value), "href", None)
    if href_attr is not None and isinstance(href_attr, property):
        # This is a proper UniversalLinkValue with computed properties
        return {
            "href": link_value.href,
            "text": link_value.text,
            "is_external": link_value.is_external,
            "opens_new_tab": link_value.opens_new_tab,
            "attrs": link_value.attrs,
            "attrs_str": link_value.attrs_str,
        }

    # Fallback: treat as dict and compute values directly
    # This handles raw dict input from tests or when blocks aren't fully instantiated
    link_type = None
    if hasattr(link_value, "get"):
        link_type = link_value.get("link_type")
    elif hasattr(link_value, "__getitem__"):
        try:
            link_type = link_value["link_type"]
        except (KeyError, TypeError):
            pass

    # Compute href from dict
    href = "#"
    if link_type == "page":
        page = link_value.get("page") if hasattr(link_value, "get") else None
        if page:
            href = getattr(page, "url", "#")
    elif link_type == "url":
        href = link_value.get("url", "#") if hasattr(link_value, "get") else "#"
    elif link_type == "email":
        email = link_value.get("email", "") if hasattr(link_value, "get") else ""
        href = f"mailto:{email}" if email else "#"
    elif link_type == "phone":
        phone = link_value.get("phone", "") if hasattr(link_value, "get") else ""
        if phone:
            if phone.startswith("+"):
                cleaned = "+" + PHONE_CLEAN_PATTERN.sub("", phone[1:])
            else:
                cleaned = PHONE_CLEAN_PATTERN.sub("", phone)
            href = f"tel:{cleaned}" if cleaned else "#"
    elif link_type == "anchor":
        anchor = link_value.get("anchor", "") if hasattr(link_value, "get") else ""
        anchor = anchor.lstrip("#")
        href = f"#{anchor}" if anchor else "#"

    # Compute text from dict
    text = ""
    if hasattr(link_value, "get"):
        text = link_value.get("link_text", "") or link_value.get("text", "")
        if not text:
            # Fallback based on link type
            if link_type == "page":
                page = link_value.get("page")
                text = getattr(page, "title", "Link") if page else "Link"
            elif link_type == "url":
                text = link_value.get("url", "Link") or "Link"
            elif link_type == "email":
                text = link_value.get("email", "Email") or "Email"
            elif link_type == "phone":
                text = link_value.get("phone", "Phone") or "Phone"
            elif link_type == "anchor":
                text = link_value.get("anchor", "Link").lstrip("#") or "Link"
            else:
                text = "Link"

    # Determine if external
    is_external = link_type == "url"

    # Determine if opens in new tab
    open_in_new_tab = None
    if hasattr(link_value, "get"):
        open_in_new_tab = link_value.get("open_in_new_tab")
    if open_in_new_tab is True:
        opens_new_tab = True
    elif open_in_new_tab is False:
        opens_new_tab = False
    else:
        opens_new_tab = is_external  # Default: new tab for external

    # Build attrs
    attrs = {}
    if opens_new_tab:
        attrs["target"] = "_blank"
        attrs["rel"] = "noopener noreferrer"
    if link_type == "phone":
        attrs["data-contact-type"] = "phone"
    elif link_type == "email":
        attrs["data-contact-type"] = "email"

    # Build attrs_str
    attrs_str = " ".join(f'{k}="{v}"' for k, v in attrs.items())

    return {
        "href": href,
        "text": text,
        "is_external": is_external,
        "opens_new_tab": opens_new_tab,
        "attrs": attrs,
        "attrs_str": attrs_str,
    }


def _extract_cta_link(cta_link_stream: Any) -> dict[str, Any] | None:
    """
    Extract CTA link from a SingleLinkStreamBlock (StreamField with max 1).

    Returns link data dict or None if not set.
    """
    if cta_link_stream is None or len(cta_link_stream) == 0:
        return None

    # SingleLinkStreamBlock contains 'link' blocks
    first_block = cta_link_stream[0]
    link_value = first_block.value if hasattr(first_block, "value") else first_block
    return _extract_link_data(link_value)


# =============================================================================
# Active Detection Helpers
# =============================================================================


def _get_current_page(context: dict[str, Any]) -> Page | None:
    """
    Get the current page from template context.

    Checks context['page'] or context['self'] (Wagtail convention).
    """
    page = context.get("page")
    if page is None:
        page = context.get("self")
    if isinstance(page, Page):
        return page
    return None


def _is_current_page(linked_page: Page | None, current_page: Page | None) -> bool:
    """Check if linked page is exactly the current page."""
    if linked_page is None or current_page is None:
        return False
    return linked_page.pk == current_page.pk


def _is_active_section(linked_page: Page | None, current_page: Page | None) -> bool:
    """
    Check if current page is the linked page or a descendant.

    Used for section highlighting (e.g., /services/ link is active on /services/roofing/).
    """
    if linked_page is None or current_page is None:
        return False
    if linked_page.pk == current_page.pk:
        return True
    # Check if current page is a descendant of linked page
    return current_page.is_descendant_of(linked_page)


def _is_current_path(
    href: str, request: HttpRequest | None, link_type: str | None = None
) -> bool:
    """
    Check if href matches current request path (for non-page links).

    Only safe for path-based comparison when link is not a page.
    """
    if request is None or not href or href == "#":
        return False
    if link_type == "page":
        # Page links should use page-based detection
        return False
    return request.path == href


# =============================================================================
# Menu Item Builders
# =============================================================================


def _build_menu_item(
    item_block: Any,
    current_page: Page | None,
    request: HttpRequest | None,
) -> dict[str, Any]:
    """
    Build a menu item dict from a MenuItemBlock value.

    Returns dict with: label, href, is_external, attrs, attrs_str,
                       is_active, is_current, has_children, children
    """
    value = item_block.value if hasattr(item_block, "value") else item_block

    label = value.get("label", "")
    link_value = value.get("link")
    link_data = _extract_link_data(link_value)

    # Get the linked page for active detection
    linked_page = None
    link_type = None
    if link_value:
        link_type = link_value.get("link_type") if hasattr(link_value, "get") else None
        linked_page = link_value.get("page") if hasattr(link_value, "get") else None

    # Determine active states
    is_current = False
    is_active = False

    if link_type == "page" and linked_page:
        is_current = _is_current_page(linked_page, current_page)
        is_active = _is_active_section(linked_page, current_page)
    else:
        # For non-page links, use path comparison
        is_current = _is_current_path(link_data["href"], request, link_type)
        is_active = is_current  # Non-page links: is_active == is_current

    # Build children
    children_blocks = value.get("children", [])
    children = []
    has_children = bool(children_blocks)

    for child_block in children_blocks:
        child_value = (
            child_block.value if hasattr(child_block, "value") else child_block
        )
        child_label = child_value.get("label", "")
        child_link = child_value.get("link")
        child_link_data = _extract_link_data(child_link)

        # Child active detection
        child_linked_page = None
        child_link_type = None
        if child_link and hasattr(child_link, "get"):
            child_link_type = child_link.get("link_type")
            child_linked_page = child_link.get("page")

        child_is_current = False
        child_is_active = False

        if child_link_type == "page" and child_linked_page:
            child_is_current = _is_current_page(child_linked_page, current_page)
            child_is_active = _is_active_section(child_linked_page, current_page)
        else:
            child_is_current = _is_current_path(
                child_link_data["href"], request, child_link_type
            )
            child_is_active = child_is_current

        children.append(
            {
                "label": child_label,
                "href": child_link_data["href"],
                "is_external": child_link_data["is_external"],
                "opens_new_tab": child_link_data["opens_new_tab"],
                "attrs": child_link_data["attrs"],
                "attrs_str": child_link_data["attrs_str"],
                "is_current": child_is_current,
                "is_active": child_is_active,
            }
        )

        # If any child is active, parent should be active too
        if child_is_active:
            is_active = True

    return {
        "label": label,
        "href": link_data["href"],
        "is_external": link_data["is_external"],
        "opens_new_tab": link_data["opens_new_tab"],
        "attrs": link_data["attrs"],
        "attrs_str": link_data["attrs_str"],
        "is_current": is_current,
        "is_active": is_active,
        "has_children": has_children,
        "children": children,
    }


# =============================================================================
# Template Tags
# =============================================================================


@register.simple_tag(takes_context=True)
def header_nav(context: dict[str, Any]) -> dict[str, Any]:
    """
    Return header navigation context dict.

    Context keys:
        - menu_items: list of menu item dicts
        - show_phone: bool
        - phone_number: str (only if show_phone True)
        - phone_href: str (tel: normalized)
        - header_cta: dict with enabled, text, href, attrs
        - current_page: Page object or None

    Usage:
        {% load navigation_tags %}
        {% header_nav as nav %}
        {{ nav.menu_items }}
    """
    request = context.get("request")
    if request is None:
        return {}

    site = Site.find_for_request(request)
    if site is None:
        return {}

    current_page = _get_current_page(context)

    # Build the context (active detection must happen per-request, not cached)
    # The base data can be cached, but we need to compute active states per-request
    header_settings = get_effective_header_settings(site)

    # Build menu items with active detection
    menu_items = []
    if header_settings.menu_items:
        for item in header_settings.menu_items:
            menu_items.append(_build_menu_item(item, current_page, request))

    # Build CTA dict
    cta_link_data = _extract_cta_link(header_settings.header_cta.link)
    header_cta = {
        "enabled": header_settings.header_cta.enabled,
        "text": header_settings.header_cta.text,
        "href": cta_link_data["href"] if cta_link_data else "#",
        "attrs": cta_link_data["attrs"] if cta_link_data else {},
    }

    # Build phone data
    phone_number = header_settings.phone_number or ""
    phone_href = _normalize_phone_href(phone_number)

    return {
        "menu_items": menu_items,
        "show_phone": header_settings.show_phone_in_header,
        "phone_number": phone_number if header_settings.show_phone_in_header else "",
        "phone_href": phone_href if header_settings.show_phone_in_header else "",
        "header_cta": header_cta,
        "current_page": current_page,
    }


@register.simple_tag(takes_context=True)
def sticky_cta(context: dict[str, Any]) -> dict[str, Any]:
    """
    Return sticky CTA (mobile) context dict.

    Context keys:
        - enabled: bool (mobile_cta_enabled)
        - phone_enabled: bool
        - phone_number: str
        - phone_href: str
        - button_enabled: bool
        - button_text: str
        - button_href: str
        - button_attrs: dict

    Usage:
        {% load navigation_tags %}
        {% sticky_cta as cta %}
        {% if cta.enabled %}...{% endif %}
    """
    request = context.get("request")
    if request is None:
        return {}

    site = Site.find_for_request(request)
    if site is None:
        return {}

    cache_key = _make_cache_key("sticky", site.id)

    def build() -> dict[str, Any]:
        header_settings = get_effective_header_settings(site)

        # Phone data
        phone_number = header_settings.phone_number or ""
        phone_href = _normalize_phone_href(phone_number)

        # Button link data
        button_link_data = _extract_cta_link(header_settings.mobile_cta_button.link)

        return {
            "enabled": header_settings.mobile_cta_enabled,
            "phone_enabled": header_settings.mobile_cta_phone_enabled,
            "phone_number": phone_number,
            "phone_href": phone_href,
            "button_enabled": header_settings.mobile_cta_button.enabled,
            "button_text": header_settings.mobile_cta_button.text,
            "button_href": button_link_data["href"] if button_link_data else "#",
            "button_attrs": button_link_data["attrs"] if button_link_data else {},
        }

    return _cache_get_or_build(cache_key, build)


@register.simple_tag(takes_context=True)
def footer_nav(context: dict[str, Any]) -> dict[str, Any]:
    """
    Return footer navigation context dict.

    Context keys:
        - tagline: str
        - link_sections: list of section dicts (title, links)
        - social: dict with facebook/instagram/linkedin/youtube/x/tiktok keys
        - business: dict with company_name, phone_number, email, address
        - copyright: dict with raw and rendered keys

    Copyright placeholders:
        - {year} → current year
        - {company_name} → effective company name

    Usage:
        {% load navigation_tags %}
        {% footer_nav as footer %}
        {{ footer.copyright.rendered }}
    """
    request = context.get("request")
    if request is None:
        return {}

    site = Site.find_for_request(request)
    if site is None:
        return {}

    cache_key = _make_cache_key("footer", site.id)

    def build() -> dict[str, Any]:
        footer_settings = get_effective_footer_settings(site)
        footer_nav_model = FooterNavigation.for_site(site)

        # Build link sections from StreamField
        link_sections = []
        if footer_nav_model.link_sections:
            for section_block in footer_nav_model.link_sections:
                section_value = (
                    section_block.value
                    if hasattr(section_block, "value")
                    else section_block
                )
                title = section_value.get("title", "")
                links_data = []

                for link_item in section_value.get("links", []):
                    link_value = (
                        link_item.value if hasattr(link_item, "value") else link_item
                    )
                    link_data = _extract_link_data(link_value)
                    # Ensure text falls back to the extracted text
                    links_data.append(
                        {
                            "label": link_data["text"],
                            "text": link_data["text"],
                            "href": link_data["href"],
                            "is_external": link_data["is_external"],
                            "opens_new_tab": link_data["opens_new_tab"],
                            "attrs": link_data["attrs"],
                            "attrs_str": link_data["attrs_str"],
                        }
                    )

                link_sections.append(
                    {
                        "title": title,
                        "links": links_data,
                    }
                )

        # Business info
        business = {
            "company_name": footer_settings.company_name,
            "phone_number": footer_settings.phone_number,
            "email": footer_settings.email,
            "address": footer_settings.address,
        }

        # Copyright with placeholder replacement
        copyright_raw = footer_nav_model.copyright_text or ""
        current_year = datetime.now().year
        copyright_rendered = copyright_raw.replace("{year}", str(current_year))
        copyright_rendered = copyright_rendered.replace(
            "{company_name}", footer_settings.company_name
        )

        return {
            "tagline": footer_settings.tagline,
            "link_sections": link_sections,
            "social": footer_settings.social,
            "business": business,
            "copyright": {
                "raw": copyright_raw,
                "rendered": copyright_rendered,
            },
        }

    return _cache_get_or_build(cache_key, build)
