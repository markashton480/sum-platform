# Navigation System

This document explains how navigation works in SUM Core (header, footer, sticky CTA), including:

- Where editors manage navigation in Wagtail
- How developer wiring, caching, and invalidation work
- Common pitfalls (especially tests + nested block data shapes)

For the template tag API reference, see:

- [`docs/dev/navigation-tags-reference.md`](../navigation-tags-reference.md)

## Overview

The navigation system provides:

- **Header navigation** (primary menu, nested dropdowns up to 3 levels, optional phone/CTA)
- **Footer navigation** (link sections, optional tagline/social overrides, business info, copyright)
- **Sticky CTA** (mobile-only quick actions)

Intentionally out of scope:

- Per-page bespoke nav logic in templates
- Heavy client-side routing/SPA behaviour

## Editor guide (Wagtail)

Navigation is managed per-site under Wagtail **Settings**:

- **Header Navigation**
  - Controls primary menu structure, dropdowns, header CTA, and “show phone” toggle.
- **Footer Navigation**
  - Controls footer link sections and optional footer overrides (tagline/social/copyright).

### Adding menu items (Header)

1. Wagtail Admin → Settings → **Header Navigation**
2. Add/edit **Menu Items**
3. For each item choose a link type and fill the required field (page/url/email/phone/anchor).
4. To create a dropdown, add **Children** to a menu item.
5. **Nested Menus:** You can add **Children** to a submenu item to create a 3rd level (Top -> Submenu -> Nested). Max 8 items per level.

### Adding footer sections

1. Wagtail Admin → Settings → **Footer Navigation**
2. Add a **Link Section**
3. Add **Links** within that section.

### Override behaviour (FooterNavigation vs Branding SiteSettings)

Some fields exist both in Branding `SiteSettings` and `FooterNavigation`.

Rule: `FooterNavigation` values **override** Branding **only if non-empty** (not just non-null).
If empty/blank, the system falls back to Branding.

Notes:

- X/Twitter: Branding uses `twitter_url`; output is normalized to `social["x"]`.
- TikTok: always from Branding `SiteSettings.tiktok_url` (no FooterNavigation override field by design).

## Developer architecture

End-to-end flow:

1. **Wagtail settings models**
   - `HeaderNavigation` / `FooterNavigation` (`core/sum_core/navigation/models.py`)
   - Branding `SiteSettings` (`core/sum_core/branding/models.py`)
2. **Resolver layer (effective settings)**
   - `get_effective_header_settings(site_or_request)`
   - `get_effective_footer_settings(site_or_request)`
   - Implemented in `core/sum_core/navigation/services.py`
3. **Template tags (cached, stable output)**
   - `header_nav`, `footer_nav`, `sticky_cta`
   - Implemented in `core/sum_core/navigation/templatetags/navigation_tags.py`
4. **Templates (wired to tags)**
   - `core/sum_core/templates/sum_core/base.html`
   - `core/sum_core/templates/sum_core/includes/header.html`
   - `core/sum_core/templates/sum_core/includes/footer.html`
   - `core/sum_core/templates/sum_core/includes/sticky_cta.html`
5. **JavaScript (minimal behaviour)**
   - `core/sum_core/static/sum_core/js/navigation.js`

Key convention:

- Templates should not read settings models directly; they should consume the tag context dicts.

## Template tags

See:

- [`docs/dev/navigation-tags-reference.md`](../navigation-tags-reference.md)

## Caching + invalidation

Navigation template tags use read-through caching keyed by site:

- `nav:header:{site_id}` — header base data (active states applied per-request)
- `nav:footer:{site_id}` — footer context
- `nav:sticky:{site_id}` — sticky CTA context

TTL:

- Defaults to **1 hour**.
- Can be overridden with `NAV_CACHE_TTL` (seconds) in Django settings.

### Invalidation triggers

Navigation cache is invalidated by signal handlers in `core/sum_core/navigation/cache.py`:

- Saving `HeaderNavigation` → invalidates `header` + `sticky`
- Saving `FooterNavigation` → invalidates `footer`
- Saving Branding `SiteSettings` → invalidates all nav keys
- Publishing/unpublishing/deleting Wagtail pages → invalidates nav keys (site-scoped when possible, safe fallback is all sites)

## Template wiring

### Base

File: `core/sum_core/templates/sum_core/base.html`

- Includes header/footer/sticky CTA templates.
- Loads `sum_core/js/navigation.js`.

### Header

File: `core/sum_core/templates/sum_core/includes/header.html`

- `{% header_nav as nav %}`
- Renders `nav.menu_items` with dropdown buttons and ARIA attributes (supporting 2-level nesting).
- Uses `aria-current="page"` when `is_current` is true.
- Classes: `.nav-dropdown` (level 2) and `.nav-nested-dropdown` (level 3).
- Uses `is-active` CSS class when `is_active` is true (propagates up from child to parent).

### Footer

File: `core/sum_core/templates/sum_core/includes/footer.html`

- `{% footer_nav as footer %}`
- Renders `footer.link_sections`, `footer.social`, `footer.business`, `footer.tagline`, `footer.copyright`.

### Sticky CTA

File: `core/sum_core/templates/sum_core/includes/sticky_cta.html`

- `{% sticky_cta as cta %}`
- If enabled, renders phone and/or button CTAs for mobile.

## JavaScript behaviour

File: `core/sum_core/static/sum_core/js/navigation.js`

Intentionally minimal:

- Toggles mobile menu open/close (adds/removes `is-open`, updates `aria-expanded`/`aria-hidden`)
- Toggles dropdown open/close via `aria-expanded`
- Handles nested dropdowns: opening a child keeps ancestors open; opening a non-related item closes others.
- Escape closes open states; clicking outside closes dropdowns
- Resizes to desktop close the mobile menu

Designed to fail gracefully if elements aren’t present.

## Testing & gotchas

### 1) ListBlock data shape (footer links)

Footer link sections contain a StreamField block that includes a **ListBlock** of `UniversalLinkBlock` items.

When setting up test data (or assigning StreamField values directly), **ListBlock items must be raw value dicts** (no `{type, value}` wrapper inside the list).

Correct (inside `links: [...]`):

```python
{
    "link_type": "url",
    "url": "https://example.com/about/",
    "link_text": "About Us",
}
```

Incorrect:

```python
{
    "type": "link",
    "value": {"link_type": "url", "url": "https://example.com/about/"},
}
```

### 2) Cache-related test isolation

Navigation tags cache results; tests that depend on settings changes must isolate cache.

Patterns used in this repo:

- Add an autouse `clear_cache` fixture that calls `django.core.cache.cache.clear()` before/after tests (see `tests/navigation/` and `tests/templates/`).
- When asserting Branding fallback behaviour, explicitly ensure the relevant FooterNavigation override field is blank (override wins when non-empty).

## Extending safely

### Adding a new social platform

1. Add fields and editor UI in Branding `SiteSettings` and (optionally) in `FooterNavigation` if you want an override.
2. Extend `get_effective_footer_settings()` to implement override → fallback mapping.
3. Update `footer_nav` output and `core/sum_core/templates/sum_core/includes/footer.html`.
4. Add/adjust tests in `tests/navigation/` and template wiring smoke tests.

### Adding a new `link_type`

1. Update `UniversalLinkBlock` value logic and validation rules.
2. Update link extraction fallback in `core/sum_core/navigation/templatetags/navigation_tags.py` (`_extract_link_data`).
3. Add tests that cover the new type and any edge cases (missing data, defaults).
