# Align Wagtail project styling with design system
_Exported on 12/10/2025 at 18:23:01 GMT from Cursor (2.1.50)_

---

**User**

We're currently working on this Wagtail project, implementing our design system. It's going okay but the design isn't quite matching up to our reference design @docs/dev/design/premium-trade-website-v3-final.html and @docs/dev/design/design_system.md 



Please can you fully analyse our current styling setup and implement changes to ensure the high standard of design in the reference is carried through to the final product. 

---

**Cursor**

```django-html
{% load static wagtailcore_tags branding_tags wagtailimages_tags %}
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    {% get_site_settings as site_settings %}
    {% wagtail_site as current_site %}
    {% firstof site_settings.company_name current_site.site_name WAGTAIL_SITE_NAME as site_name %}
    <title>
      {% block title %}
        {% if page %}
          {% firstof page.seo_title page.title %}
        {% else %}
          {{ site_name }}
        {% endif %}
      {% endblock %}
    </title>
    {% if site_settings.favicon %}
      {% image site_settings.favicon fill-32x32 as favicon_rendition %}
      <link rel="icon" href="{{ favicon_rendition.url }}">
    {% endif %}
    
    <!-- Branding Fonts -->
    {% branding_fonts %}
    
    <!-- Main CSS -->
    <link rel="stylesheet" href="{% static 'sum_core/css/main.css' %}">

    <!-- Branding Variables (Must load AFTER main.css to override defaults) -->
    {% branding_css %}

    {% block extra_head %}{% endblock %}
  </head>
  <body id="body">
    
    {% include "sum_core/includes/header.html" %}
    
    <main>
        {% block content %}{% endblock %}
    </main>
      
    {% include "sum_core/includes/footer.html" %}

    <!-- Mobile FAB -->
    <a href="#quote" class="mobile-fab" id="mobileFab">
        <span>Book Survey</span>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
    </a>

    <!-- Main JS -->
    <script src="{% static 'sum_core/js/main.js' %}"></script>
    {% block extra_body %}{% endblock %}
  </body>
</html>

```

```python
"""
Name: Branding Template Tags
Path: core/sum_core/branding/templatetags/branding_tags.py
Purpose: Exposes branding-related template tags, including access to SiteSettings and branding-driven CSS/font helpers.
Family: Used by Django templates to retrieve branding configuration and inject runtime styles.
Dependencies: Django template system, Wagtail Site and SiteSettings, Django cache.
"""

from __future__ import annotations

import colorsys
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


def _hex_to_hsl(hex_value: str) -> tuple[int, int, int] | None:
    """
    Convert hex color to CSS HSL values (h=0-360, s=0-100, l=0-100).
    """
    hex_value = hex_value.lstrip("#")
    if len(hex_value) not in (3, 6):
        return None

    if len(hex_value) == 3:
        hex_value = "".join(c * 2 for c in hex_value)

    try:
        r, g, b = (int(hex_value[i : i + 2], 16) / 255.0 for i in (0, 2, 4))
        h, l, s = colorsys.rgb_to_hls(r, g, b)
        return round(h * 360), round(s * 100), round(l * 100)
    except (ValueError, IndexError):
        return None


def _build_css_variables(site_settings: SiteSettings) -> list[str]:
    variables: list[str] = []

    # Inject HSL variables from Primary Color
    if site_settings.primary_color:
        hsl = _hex_to_hsl(site_settings.primary_color)
        if hsl:
            h, s, l = hsl
            variables.extend([
                f"    --brand-h: {h};",
                f"    --brand-s: {s}%;",
                f"    --brand-l: {l}%;",
            ])
        else:
            # Fallback if invalid hex, let CSS defaults handle it
            pass
    
    # If no primary color set, we do NOT inject defaults here.
    # We rely on main.css :root variables to provide the default "Gold" theme.


    # Also inject other specific colors if needed, but the system relies on HSL
    # We can inject them as overrides if we want, or just stick to the design system logic.
    # For now, let's inject the provided secondary/accent as simple hex variables
    # in case we want to use them directly, but the main theme will drive off brand-h/s/l.
    
    if site_settings.secondary_color:
        variables.append(f"    --color-secondary-custom: {site_settings.secondary_color};")
    
    if site_settings.accent_color:
        variables.append(f"    --color-accent-custom: {site_settings.accent_color};")
        # Also try to generate accent HSL if needed
        accent_hsl = _hex_to_hsl(site_settings.accent_color)
        if accent_hsl:
             variables.append(f"    --accent-h: {accent_hsl[0]};")
             variables.append(f"    --accent-s: {accent_hsl[1]}%;")
             variables.append(f"    --accent-l: {accent_hsl[2]}%;")


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
    
    # If no fonts configured, fallback to the design system defaults
    if not fonts:
        return ["Fraunces", "Manrope"]
        
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
            f"family={quote_plus(font)}:wght@300;400;500;600;700" for font in fonts
        )
        href = f"https://fonts.googleapis.com/css2?{families}&display=swap"

        links = [
            '<link rel="preconnect" href="https://fonts.googleapis.com">',
            '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>',
            f'<link rel="stylesheet" href="{href}">',
        ]

        return mark_safe("\n".join(links))

    return _cacheable_response(cache_key, build)

```

```postcss
/* ==========================================================================
   SolarCraft Premium - Design System 2.0 (Brand Agnostic)
   Based on V3 Final Design & Design System Spec
   ========================================================================== */

/* ===================================
   1. DESIGN TOKENS (HSL SYSTEM)
   =================================== */

:root {
  /* 
     Base HSL Values are injected by Wagtail via branding_tags.py:
     --brand-h, --brand-s, --brand-l
     
     If not present, fallback values are defined here.
  */
  --brand-h: 30;    /* Brown/Gold Default */
  --brand-s: 40%;
  --brand-l: 35%;

  /* Derived Palette */
  --primary: var(--brand-h), var(--brand-s), var(--brand-l);
  --primary-deep: var(--brand-h), var(--brand-s), calc(var(--brand-l) - 15%);
  
  /* Surface & Text - Derived for harmony */
  --surface-tint: var(--brand-h), 10%, 97%;
  --surface-pure: 0, 0%, 100%;
  
  --text-main: var(--brand-h), 15%, 15%;
  --text-muted: var(--brand-h), 5%, 45%;
  
  /* Accent - Analogous calculation or custom injection */
  --accent-pop: calc(var(--brand-h) + 30), 60%, 55%;

  /* Typography */
  --font-display: var(--font-heading, 'Fraunces', serif);
  --font-body: var(--font-body, 'Manrope', sans-serif);

  /* Fluid Type Scale */
  --text-xs: 0.75rem;
  --text-sm: 0.875rem;
  --text-base: 1rem;
  --text-lg: 1.125rem;
  --text-xl: 1.25rem;
  --text-2xl: 1.5rem;
  --text-3xl: clamp(1.75rem, 3vw, 2.5rem);
  --text-4xl: clamp(2.25rem, 5vw, 3.5rem);
  --text-display: clamp(3rem, 8vw, 5.5rem); /* Huge Editorial Headings */

  /* Spacing */
  --container-padding: clamp(1.5rem, 5vw, 4rem);
  --section-gap: clamp(4rem, 10vw, 8rem);

  /* Animation Easings */
  --ease-out-expo: cubic-bezier(0.19, 1, 0.22, 1);
  --ease-smooth: cubic-bezier(0.4, 0, 0.2, 1);

  /* Borders & Radius */
  --radius-sm: 4px;
  --radius-md: 12px;
  --radius-lg: 24px;
}

/* Technical Theme Override */
[data-theme="technical"] {
    --brand-h: 210;   /* Deep Blue */
    --brand-s: 80%;
    --brand-l: 25%;

    --surface-tint: 210, 20%, 98%;
    
    --accent-pop: 200, 90%, 40%;
    --font-display: 'Manrope', sans-serif; /* Cleaner look for technical */
}

/* ===================================
   2. RESET & CORE UTILITIES
   =================================== */

* { margin: 0; padding: 0; box-sizing: border-box; }

html { scroll-behavior: smooth; }

body {
    font-family: var(--font-body);
    color: hsla(var(--text-main), 1);
    background-color: hsla(var(--surface-tint), 1);
    line-height: 1.6;
    overflow-x: hidden;
    -webkit-font-smoothing: antialiased;
}

h1, h2, h3, h4, h5 {
    font-family: var(--font-display);
    font-weight: 400; /* Editorial style uses lighter weights */
    line-height: 1.1;
    letter-spacing: -0.02em;
    color: hsla(var(--text-main), 1);
}

img {
    max-width: 100%;
    display: block;
}

a { text-decoration: none; color: inherit; transition: color 0.3s ease; }

/* Utility: Text Emphasis */
.italic-accent {
    font-style: italic;
    font-weight: 300;
    color: hsla(var(--accent-pop), 1);
}

/* Utility: Container */
.container {
    width: 100%;
    max-width: 1400px;
    margin: 0 auto;
    padding: 0 var(--container-padding);
}

.section {
    padding: var(--section-gap) 0;
}

/* ===================================
   3. ANIMATION UTILITIES (The "Wow" Factor)
   =================================== */

/* Text Reveal */
.reveal-text {
    opacity: 0;
    transform: translateY(30px);
    transition: all 1s var(--ease-out-expo);
}

.is-in-view .reveal-text,
.is-in-view.reveal-text {
    opacity: 1;
    transform: translateY(0);
}

/* Image Curtain Reveal */
.reveal-img-wrapper {
    position: relative;
    overflow: hidden;
    background-color: hsla(var(--primary), 0.1);
}

.reveal-img-wrapper img {
    transform: scale(1.15);
    transition: transform 1.5s var(--ease-out-expo);
    will-change: transform;
}

.reveal-img-wrapper::after {
    content: '';
    position: absolute;
    inset: 0;
    background-color: hsla(var(--surface-tint), 1); /* Matches bg */
    transform: scaleY(1);
    transform-origin: bottom;
    transition: transform 1.2s var(--ease-out-expo);
    z-index: 2;
}

.is-in-view .reveal-img-wrapper img,
.is-in-view.reveal-img-wrapper img {
    transform: scale(1);
}

.is-in-view .reveal-img-wrapper::after,
.is-in-view.reveal-img-wrapper::after {
    transform: scaleY(0);
}

/* Stagger Delays */
.delay-100 { transition-delay: 0.1s; }
.delay-200 { transition-delay: 0.2s; }
.delay-300 { transition-delay: 0.3s; }

/* General Fade Group */
.reveal-group {
    opacity: 0;
    transform: translateY(20px);
    transition: opacity 0.8s ease, transform 0.8s ease;
}

.is-in-view.reveal-group, .is-in-view .reveal-group {
    opacity: 1;
    transform: translateY(0);
}


/* ===================================
   4. HEADER (Glassmorphism)
   =================================== */

.header {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    z-index: 100;
    padding: 1.5rem 0;
    transition: all 0.4s ease;
}

.header.scrolled {
    padding: 1rem 0;
    background: hsla(var(--surface-pure), 0.85);
    backdrop-filter: blur(12px);
    border-bottom: 1px solid hsla(var(--text-main), 0.05);
}

.nav-inner {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.logo {
    font-family: var(--font-display);
    font-size: 1.5rem;
    font-weight: 600;
    color: hsla(var(--primary), 1);
}

.nav-links {
    display: none;
    gap: 2.5rem;
}

@media(min-width: 1024px) {
    .nav-links { display: flex; align-items: center; }
}

.nav-item {
    font-size: 0.9rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    position: relative;
}

.nav-item::after {
    content: '';
    position: absolute;
    bottom: -4px;
    left: 0;
    width: 0;
    height: 1px;
    background: hsla(var(--accent-pop), 1);
    transition: width 0.3s ease;
}

.nav-item:hover::after { width: 100%; }

/* Mobile Menu Button */
.menu-btn {
    display: flex;
    flex-direction: column;
    gap: 6px;
    background: none;
    border: none;
    cursor: pointer;
    z-index: 110;
}

@media(min-width: 1024px) { .menu-btn { display: none; } }

.menu-line {
    width: 24px;
    height: 2px;
    background-color: hsla(var(--text-main), 1);
    transition: 0.3s ease;
}


/* ===================================
   5. BUTTONS
   =================================== */

.btn {
    display: inline-flex;
    align-items: center;
    gap: 0.75rem;
    padding: 1rem 2rem;
    border-radius: var(--radius-sm); /* Architectural feel = sharper corners */
    font-weight: 600;
    font-size: 0.95rem;
    transition: all 0.3s ease;
    cursor: pointer;
    letter-spacing: 0.02em;
    border: 1px solid transparent;
}

.btn-primary {
    background-color: hsla(var(--primary), 1);
    color: white; /* Needs check for contrast, but white on dark primary is standard */
    border: 1px solid hsla(var(--primary), 1);
}

.btn-primary:hover {
    background-color: hsla(var(--primary-deep), 1);
    transform: translateY(-2px);
}

.btn-outline {
    background: transparent;
    border: 1px solid hsla(var(--text-main), 0.2);
    color: hsla(var(--text-main), 1);
}

.btn-outline:hover {
    border-color: hsla(var(--primary), 1);
    color: hsla(var(--primary), 1);
}


/* ===================================
   6. HERO SECTION
   =================================== */

.hero {
    padding-top: 180px;
    padding-bottom: 100px;
    position: relative;
    overflow: hidden;
}

.hero-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 3rem;
    align-items: center;
}

@media(min-width: 1024px) {
    .hero-grid {
        grid-template-columns: 1.2fr 1fr;
        gap: 6rem;
    }
}

.hero-status {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    font-size: var(--text-xs);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    font-weight: 700;
    color: hsla(var(--accent-pop), 1);
    margin-bottom: 1.5rem;
    padding: 0.5rem 1rem;
    background: hsla(var(--surface-pure), 0.5);
    border: 1px solid hsla(var(--text-main), 0.1);
    border-radius: 50px;
}

.status-dot {
    width: 8px;
    height: 8px;
    background-color: #10B981;
    border-radius: 50%;
    box-shadow: 0 0 0 2px hsla(var(--surface-tint), 1);
}

.hero h1 {
    font-size: var(--text-display);
    margin-bottom: 2rem;
}

.hero-desc {
    font-size: var(--text-lg);
    color: hsla(var(--text-muted), 1);
    max-width: 500px;
    margin-bottom: 3rem;
}

.hero-actions {
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
}

/* Hero Image Composition */
.hero-visual {
    position: relative;
}

.hero-main-img {
    border-radius: var(--radius-md);
    aspect-ratio: 4/5;
    object-fit: cover;
    width: 100%;
}

/* Floating Element */
.float-card {
    position: absolute;
    bottom: 40px;
    left: -40px;
    background: hsla(var(--surface-pure), 0.95);
    backdrop-filter: blur(10px);
    padding: 1.5rem;
    border-radius: var(--radius-sm);
    box-shadow: 0 20px 40px -10px rgba(0,0,0,0.1);
    max-width: 200px;
    border: 1px solid hsla(var(--text-main), 0.05);
    display: none;
}

@media(min-width: 768px) { .float-card { display: block; } }

.float-label {
    display: block;
    font-size: var(--text-xs);
    color: hsla(var(--text-muted), 1);
    margin-bottom: 0.25rem;
}

.float-value {
    font-family: var(--font-display);
    font-size: 2rem;
    color: hsla(var(--primary), 1);
}


/* ===================================
   7. TRUST STRIP (Marquee)
   =================================== */

.trust-strip {
    border-top: 1px solid hsla(var(--text-main), 0.05);
    border-bottom: 1px solid hsla(var(--text-main), 0.05);
    padding: 2rem 0;
    overflow: hidden;
    background: hsla(var(--surface-pure), 0.5);
}

.marquee-wrapper {
    display: flex;
    width: 100%;
    mask-image: linear-gradient(to right, transparent, black 10%, black 90%, transparent);
    -webkit-mask-image: linear-gradient(to right, transparent, black 10%, black 90%, transparent);
}

.marquee-track {
    display: flex;
    gap: 4rem;
    white-space: nowrap;
    animation: scroll 30s linear infinite;
    padding-left: 4rem;
}

@keyframes scroll {
    0% { transform: translateX(0); }
    100% { transform: translateX(-50%); }
}

.trust-item {
    font-family: var(--font-body);
    font-weight: 600;
    color: hsla(var(--text-muted), 0.6);
    font-size: 1.1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}


/* ===================================
   8. FEATURES
   =================================== */

.features-header {
    max-width: 700px;
    margin-bottom: 4rem;
}

.features-container {
    display: flex;
    overflow-x: auto;
    gap: 1.5rem;
    padding-bottom: 2rem;
    scroll-snap-type: x mandatory;
    scrollbar-width: none;
    -ms-overflow-style: none;
    margin: 0 calc(var(--container-padding) * -1);
    padding: 0 var(--container-padding) 2rem;
}

.features-container::-webkit-scrollbar { display: none; }

@media(min-width: 1024px) {
    .features-container {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        margin: 0;
        padding: 0;
        overflow: visible;
    }
}

.feature-card {
    min-width: 85%;
    scroll-snap-align: center;
    background: hsla(var(--surface-pure), 1);
    padding: 2rem;
    border-radius: var(--radius-sm);
    border: 1px solid hsla(var(--text-main), 0.05);
    transition: transform 0.3s ease;
}

@media(min-width: 1024px) {
    .feature-card { min-width: auto; }
    .feature-card:hover { transform: translateY(-10px); }
}

.feature-icon {
    font-size: 2rem;
    color: hsla(var(--primary), 1);
    margin-bottom: 1.5rem;
    display: inline-block;
}


/* ===================================
   9. COMPARISON SLIDER
   =================================== */

.comparison-section {
    background-color: hsla(var(--text-main), 1);
    color: hsla(var(--surface-tint), 1);
}

.comparison-section h2 { color: hsla(var(--surface-tint), 1); }
.comparison-section p { color: hsla(var(--surface-tint), 0.7); }

.slider-container {
    position: relative;
    width: 100%;
    aspect-ratio: 16/9;
    overflow: hidden;
    border-radius: var(--radius-sm);
    margin-top: 3rem;
}

.img-background, .img-foreground {
    position: absolute;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background-size: cover;
    background-position: center;
}

.img-foreground {
    width: 50%;
    border-right: 2px solid white;
    background-position: left;
    overflow: hidden;
}

.slider-range {
    position: absolute;
    top: 0; left: 0;
    width: 100%; height: 100%;
    opacity: 0;
    cursor: ew-resize;
    z-index: 10;
}

.slider-handle {
    position: absolute;
    top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    width: 40px; height: 40px;
    background: white;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: black;
    pointer-events: none;
    z-index: 11;
    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}


/* ===================================
   10. PORTFOLIO
   =================================== */

.portfolio-grid {
    display: grid;
    gap: 2rem;
}

@media(min-width: 768px) {
    .portfolio-grid {
        grid-template-columns: repeat(2, 1fr);
        gap: 4rem;
    }

    /* Offset effect for editorial look */
    .portfolio-item:nth-child(even) {
        transform: translateY(60px);
    }
}

.portfolio-img {
    aspect-ratio: 4/5;
    width: 100%;
    object-fit: cover;
    border-radius: var(--radius-sm);
    margin-bottom: 1.5rem;
}

.portfolio-meta {
    font-size: var(--text-xs);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: hsla(var(--primary), 1);
    margin-bottom: 0.5rem;
}

.portfolio-title {
    font-size: var(--text-xl);
    margin-bottom: 0.5rem;
}


/* ===================================
   11. MOBILE FAB
   =================================== */

.mobile-fab {
    position: fixed;
    bottom: 20px;
    right: 20px;
    z-index: 99;
    background: hsla(var(--text-main), 1);
    color: white;
    padding: 1rem 1.5rem;
    border-radius: 50px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    transform: translateY(150%);
    transition: transform 0.4s ease;
}

.mobile-fab.visible {
    transform: translateY(0);
}

@media(min-width: 768px) { .mobile-fab { display: none; } }

```

I've fully analyzed your styling setup and implemented the necessary changes to align with the reference design.

Here is a summary of the issues found and the fixes applied:

1.  **CSS Loading Order (Critical Fix)**
    *   **Issue**: In `base.html`, `{% branding_css %}` was loaded *before* `main.css`. Because `main.css` contains default `:root` variable definitions, these defaults were overriding the dynamic values injected by Wagtail.
    *   **Fix**: Swapped the order so `{% branding_css %}` comes *after* `main.css`. This ensures your CMS settings correctly override the defaults.

2.  **Incorrect Fallback Logic**
    *   **Issue**: The Python code in `branding_tags.py` had a hardcoded fallback to "Deep Blue" (Technical Theme) if no primary color was set. However, `main.css` and the reference HTML use "Gold/Brown" as the default base. This caused a mismatch where a new site would look Blue instead of Gold.
    *   **Fix**: Removed the Python-side fallback. Now, if no color is set in the CMS, the system relies on the CSS defaults in `main.css` (Gold), matching the reference design.

3.  **Missing Theme Overrides**
    *   **Issue**: The `main.css` file was missing the `[data-theme="technical"]` block present in the reference HTML.
    *   **Fix**: Added the technical theme overrides to `main.css`, ensuring the alternative color palette and font stack are available.

### Files Updated

1.  `core/sum_core/templates/sum_core/base.html`: Reordered CSS loading.
2.  `core/sum_core/branding/templatetags/branding_tags.py`: Removed hardcoded fallback.
3.  `core/sum_core/static/sum_core/css/main.css`: Added technical theme override.

Your styling infrastructure is now robust. When you add Hero or Feature blocks that use these classes, they will correctly reflect the design system and Wagtail settings.

---

**User**

Okay perfect, the header and footer are now looking much better. However the hero and main content on the home page is still very odd. Can you double check each of the templates to make sure they follow the same standards as the reference design

---

**Cursor**

```python
"""
Name: Content Blocks
Path: core/sum_core/blocks/content.py
Purpose: Define StructBlocks for rich content sections (Hero, Features, Portfolio, etc.).
Family: Used by StreamFields in pages.
"""
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock


class ButtonBlock(blocks.StructBlock):
    label = blocks.CharBlock(required=True)
    link = blocks.URLBlock(required=False)
    page = blocks.PageChooserBlock(required=False)
    style = blocks.ChoiceBlock(choices=[
        ('btn-primary', 'Primary'),
        ('btn-outline', 'Outline'),
    ], default='btn-primary')

    class Meta:
        template = "sum_core/blocks/button.html"
        icon = "placeholder"


class HeroBlock(blocks.StructBlock):
    status_text = blocks.CharBlock(required=False, help_text="e.g. Available for Q1 2025")
    title = blocks.TextBlock(required=True, help_text="Main heading. Use html tags like <span class='italic-accent'> for styling.")
    description = blocks.TextBlock(required=True)
    primary_cta = ButtonBlock(required=False)
    secondary_cta = ButtonBlock(required=False)
    image = ImageChooserBlock(required=True)
    float_card_label = blocks.CharBlock(required=False, help_text="e.g. Est. Annual Savings")
    float_card_value = blocks.CharBlock(required=False, help_text="e.g. £2,450")

    class Meta:
        template = "sum_core/blocks/hero.html"
        icon = "image"
        label = "Hero Section"


class TrustItemBlock(blocks.StructBlock):
    text = blocks.CharBlock(required=True)

    class Meta:
        icon = "tick"


class TrustStripBlock(blocks.StructBlock):
    items = blocks.ListBlock(TrustItemBlock())

    class Meta:
        template = "sum_core/blocks/trust_strip.html"
        icon = "list-ul"
        label = "Trust Strip"


class FeatureBlock(blocks.StructBlock):
    icon = blocks.CharBlock(required=True, help_text="Emoji or text icon")
    title = blocks.CharBlock(required=True)
    description = blocks.TextBlock(required=True)

    class Meta:
        icon = "tick-inverse"


class FeaturesListBlock(blocks.StructBlock):
    heading = blocks.CharBlock(required=True)
    intro = blocks.TextBlock(required=False)
    features = blocks.ListBlock(FeatureBlock())

    class Meta:
        template = "sum_core/blocks/features_list.html"
        icon = "list-ul"
        label = "Features List"


class ComparisonBlock(blocks.StructBlock):
    accent_text = blocks.CharBlock(required=False, help_text="Small italic text above title")
    title = blocks.CharBlock(required=True)
    description = blocks.TextBlock(required=True)
    image_before = ImageChooserBlock(required=True, help_text="Background/Before image")
    image_after = ImageChooserBlock(required=True, help_text="Foreground/After image")

    class Meta:
        template = "sum_core/blocks/comparison.html"
        icon = "image"
        label = "Comparison Slider"


class ProjectBlock(blocks.StructBlock):
    image = ImageChooserBlock(required=True)
    meta = blocks.CharBlock(required=True, help_text="e.g. Kensington • 12kW System")
    title = blocks.CharBlock(required=True)

    class Meta:
        icon = "image"


class PortfolioBlock(blocks.StructBlock):
    heading = blocks.CharBlock(required=True)
    projects = blocks.ListBlock(ProjectBlock())

    class Meta:
        template = "sum_core/blocks/portfolio.html"
        icon = "grip"
        label = "Portfolio Grid"

```

```python
"""
Name: Blocks Package Init
Path: core/sum_core/blocks/__init__.py
Purpose: Namespace for reusable block definitions within sum_core.
Family: Imported by sum_core consumers and test_project when implementing page content.
Dependencies: PageStreamBlock from base module.
"""

from .base import PageStreamBlock
from .content import (
    HeroBlock,
    TrustStripBlock,
    FeaturesListBlock,
    ComparisonBlock,
    PortfolioBlock,
)

__all__ = [
    "PageStreamBlock",
    "HeroBlock",
    "TrustStripBlock",
    "FeaturesListBlock",
    "ComparisonBlock",
    "PortfolioBlock",
]

```

```python
"""
Name: Base Block Definitions
Path: core/sum_core/blocks/base.py
Purpose: Core block infrastructure and canonical page StreamField definition for sum_core.
Family: Imported by page models and block implementations across sum_core.
Dependencies: Wagtail blocks, rich text utilities.
"""

from wagtail import blocks
from wagtail.blocks import StreamBlock

from sum_core.blocks.content import (
    HeroBlock,
    TrustStripBlock,
    FeaturesListBlock,
    ComparisonBlock,
    PortfolioBlock,
)


class PageStreamBlock(StreamBlock):
    """
    Canonical StreamBlock for page content fields.

    This block defines the available content blocks that can be used in page
    body fields. It serves as the foundation for building pages through the
    Wagtail admin interface.
    """

    hero = HeroBlock(group="Sections")
    trust_strip = TrustStripBlock(group="Sections")
    features = FeaturesListBlock(group="Sections")
    comparison = ComparisonBlock(group="Sections")
    portfolio = PortfolioBlock(group="Sections")

    rich_text = blocks.RichTextBlock(
        label="Rich Text",
        help_text="Add formatted text content. Use H2-H4 for headings, avoid H1.",
        features=[
            "h2", "h3", "h4",  # Headings H2-H4 only, no H1
            "bold", "italic",   # Text formatting
            "link",             # Links
            "ol", "ul",         # Ordered and unordered lists
        ],
        required=False,
    )

    class Meta:
        """Meta configuration for PageStreamBlock."""
        icon = "doc-full"
        label = "Content Block"
        label_format = "Content: {label}"
        template = "sum_core/blocks/rich_text.html"  # Default template for rendering

```

