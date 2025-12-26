# Navigation Template Tags Reference

> **Module:** `sum_core.navigation.templatetags.navigation_tags`  
> **Load with:** `{% load navigation_tags %}`

This document provides a complete reference for the navigation template tags used to render site-wide header, footer, and sticky CTA components.

---

## Overview

The navigation system provides three template tags that return context dictionaries for rendering navigation elements:

| Tag                | Purpose                                        | Cached                         |
| ------------------ | ---------------------------------------------- | ------------------------------ |
| `{% header_nav %}` | Header menu, phone, and CTA                    | No (includes active detection) |
| `{% footer_nav %}` | Footer links, social, business info, copyright | Yes                            |
| `{% sticky_cta %}` | Mobile sticky CTA bar                          | Yes                            |

All tags require `request` in the template context and return an empty dict if unavailable.

---

## `{% header_nav %}`

Returns header navigation context including menu items with active page detection.

### Usage

```django
{% load navigation_tags %}

{% header_nav as nav %}
```

### Context Keys

| Key            | Type         | Description                                  |
| -------------- | ------------ | -------------------------------------------- | ------------------------------- |
| `menu_items`   | `list[dict]` | List of top-level menu items                 |
| `show_phone`   | `bool`       | Whether to display phone number              |
| `phone_number` | `str`        | Phone number (empty if `show_phone=False`)   |
| `phone_href`   | `str`        | Normalized `tel:` link (e.g., `tel:5551234`) |
| `header_cta`   | `dict`       | Header CTA button configuration              |
| `current_page` | `Page        | None`                                        | The current Wagtail page object |

### Menu Item Structure

Each item in `menu_items` contains:

| Key             | Type         | Description                                        |
| --------------- | ------------ | -------------------------------------------------- |
| `label`         | `str`        | Display text for the menu item                     |
| `href`          | `str`        | Link URL                                           |
| `is_external`   | `bool`       | True for external URLs                             |
| `opens_new_tab` | `bool`       | Whether link opens in new tab                      |
| `attrs`         | `dict`       | HTML attributes (e.g., `target`, `rel`)            |
| `attrs_str`     | `str`        | Attributes as string for template interpolation    |
| `is_current`    | `bool`       | True if this is the exact current page             |
| `is_active`     | `bool`       | True if current page is this page or a descendant  |
| `has_children`  | `bool`       | Whether this item has a dropdown                   |
| `children`      | `list[dict]` | Submenu items (same structure, no nested children) |

### Header CTA Structure

| Key       | Type   | Description            |
| --------- | ------ | ---------------------- |
| `enabled` | `bool` | Whether CTA is enabled |
| `text`    | `str`  | Button text            |
| `href`    | `str`  | Link URL               |
| `attrs`   | `dict` | HTML attributes        |

### Active Detection Logic

- **`is_current`**: True only when the menu item links to the exact current page
- **`is_active`**: True when:
  - The menu item links to the current page, OR
  - The current page is a descendant of the linked page (section highlighting), OR
  - Any child menu item is active

This enables section highlighting where, for example, a "Services" link is marked active when viewing `/services/roofing/`.

### Example

```django
{% load navigation_tags %}

{% header_nav as nav %}

<nav class="header-nav">
    <ul>
        {% for item in nav.menu_items %}
        <li class="{% if item.is_active %}is-active{% endif %}">
            <a href="{{ item.href }}" {{ item.attrs_str }}>
                {{ item.label }}
            </a>

            {% if item.has_children %}
            <ul class="dropdown">
                {% for child in item.children %}
                <li class="{% if child.is_current %}is-current{% endif %}">
                    <a href="{{ child.href }}" {{ child.attrs_str }}>
                        {{ child.label }}
                    </a>
                </li>
                {% endfor %}
            </ul>
            {% endif %}
        </li>
        {% endfor %}
    </ul>

    {% if nav.show_phone %}
    <a href="{{ nav.phone_href }}" class="header-phone">
        {{ nav.phone_number }}
    </a>
    {% endif %}

    {% if nav.header_cta.enabled %}
    <a href="{{ nav.header_cta.href }}" class="btn btn-primary">
        {{ nav.header_cta.text }}
    </a>
    {% endif %}
</nav>
```

---

## `{% footer_nav %}`

Returns footer navigation context including link sections, social media, business info, and copyright.

### Usage

```django
{% load navigation_tags %}

{% footer_nav as footer %}
```

### Context Keys

| Key             | Type         | Description                              |
| --------------- | ------------ | ---------------------------------------- |
| `tagline`       | `str`        | Footer tagline (from effective settings) |
| `link_sections` | `list[dict]` | Footer link columns                      |
| `social`        | `dict`       | Social media URLs with canonical keys    |
| `business`      | `dict`       | Business contact information             |
| `copyright`     | `dict`       | Copyright text with placeholders         |

### Link Section Structure

Each item in `link_sections` contains:

| Key     | Type         | Description                                   |
| ------- | ------------ | --------------------------------------------- |
| `title` | `str`        | Section heading (e.g., "Company", "Services") |
| `links` | `list[dict]` | Links in this section                         |

Each link contains:

| Key             | Type   | Description                    |
| --------------- | ------ | ------------------------------ |
| `label`         | `str`  | Display text                   |
| `text`          | `str`  | Display text (alias for label) |
| `href`          | `str`  | Link URL                       |
| `is_external`   | `bool` | True for external URLs         |
| `opens_new_tab` | `bool` | Whether link opens in new tab  |
| `attrs`         | `dict` | HTML attributes                |
| `attrs_str`     | `str`  | Attributes as string           |

### Social Structure

Canonical keys, regardless of underlying field names:

| Key         | Type  | Description              |
| ----------- | ----- | ------------------------ |
| `facebook`  | `str` | Facebook URL             |
| `instagram` | `str` | Instagram URL            |
| `linkedin`  | `str` | LinkedIn URL             |
| `youtube`   | `str` | YouTube URL              |
| `x`         | `str` | X (formerly Twitter) URL |
| `tiktok`    | `str` | TikTok URL               |

### Business Structure

| Key            | Type  | Description      |
| -------------- | ----- | ---------------- |
| `company_name` | `str` | Company name     |
| `phone_number` | `str` | Phone number     |
| `email`        | `str` | Email address    |
| `address`      | `str` | Physical address |

### Copyright Structure

| Key        | Type  | Description                     |
| ---------- | ----- | ------------------------------- |
| `raw`      | `str` | Original text with placeholders |
| `rendered` | `str` | Text with placeholders replaced |

**Supported placeholders:**

- `{year}` → Current year (e.g., `2025`)
- `{company_name}` → Effective company name

Unknown placeholders are left untouched.

### Example

```django
{% load navigation_tags %}

{% footer_nav as footer %}

<footer class="site-footer">
    {% if footer.tagline %}
    <p class="footer-tagline">{{ footer.tagline }}</p>
    {% endif %}

    <div class="footer-links">
        {% for section in footer.link_sections %}
        <div class="footer-column">
            <h4>{{ section.title }}</h4>
            <ul>
                {% for link in section.links %}
                <li>
                    <a href="{{ link.href }}" {{ link.attrs_str }}>
                        {{ link.label }}
                    </a>
                </li>
                {% endfor %}
            </ul>
        </div>
        {% endfor %}
    </div>

    <div class="footer-social">
        {% if footer.social.facebook %}
        <a href="{{ footer.social.facebook }}" aria-label="Facebook">FB</a>
        {% endif %}
        {% if footer.social.instagram %}
        <a href="{{ footer.social.instagram }}" aria-label="Instagram">IG</a>
        {% endif %}
        {% if footer.social.x %}
        <a href="{{ footer.social.x }}" aria-label="X">X</a>
        {% endif %}
    </div>

    <div class="footer-business">
        <p>{{ footer.business.company_name }}</p>
        <p>{{ footer.business.address }}</p>
        <p>
            <a href="mailto:{{ footer.business.email }}">{{ footer.business.email }}</a>
        </p>
    </div>

    <p class="footer-copyright">{{ footer.copyright.rendered }}</p>
</footer>
```

---

## `{% sticky_cta %}`

Returns mobile sticky CTA bar context for phone and action buttons.

### Usage

```django
{% load navigation_tags %}

{% sticky_cta as cta %}
```

### Context Keys

| Key              | Type   | Description                           |
| ---------------- | ------ | ------------------------------------- |
| `enabled`        | `bool` | Whether the sticky CTA bar is enabled |
| `phone_enabled`  | `bool` | Whether to show phone button          |
| `phone_number`   | `str`  | Phone number                          |
| `phone_href`     | `str`  | Normalized `tel:` link                |
| `button_enabled` | `bool` | Whether to show action button         |
| `button_text`    | `str`  | Action button text                    |
| `button_href`    | `str`  | Action button URL                     |
| `button_attrs`   | `dict` | HTML attributes for action button     |

### Example

```django
{% load navigation_tags %}

{% sticky_cta as cta %}

{% if cta.enabled %}
<div class="sticky-cta" aria-label="Quick actions">
    {% if cta.phone_enabled and cta.phone_number %}
    <a href="{{ cta.phone_href }}" class="sticky-cta__phone" aria-label="Call us">
        <svg><!-- phone icon --></svg>
        <span>{{ cta.phone_number }}</span>
    </a>
    {% endif %}

    {% if cta.button_enabled %}
    <a href="{{ cta.button_href }}" class="sticky-cta__button btn btn-primary">
        {{ cta.button_text }}
    </a>
    {% endif %}
</div>
{% endif %}
```

---

## Caching

### Cache Keys

Cache keys follow the format `nav:{tag}:{site_id}`:

| Tag          | Cache Key Format                                   |
| ------------ | -------------------------------------------------- |
| `header_nav` | Not cached (requires per-request active detection) |
| `footer_nav` | `nav:footer:{site_id}`                             |
| `sticky_cta` | `nav:sticky:{site_id}`                             |

### TTL

Default: **3600 seconds (1 hour)**

Configure via Django settings:

```python
# settings.py
NAV_CACHE_TTL = 1800  # 30 minutes
```

### Cache Invalidation

Cache invalidation is handled by navigation signal handlers in `sum_core.navigation`. When navigation or branding settings are saved/published, the relevant cache keys are cleared.

### Cached vs Rendered Fields

`footer_nav` caches only stable data (including the raw copyright template).
Time-dependent rendering (e.g., `{year}`) happens after retrieving the cached payload on each call.

### Graceful Fallback

If the cache backend fails (get or set), the tags gracefully fall back to building the context from the database without raising exceptions.

---

## Data Sources

The template tags pull data from multiple models with override precedence:

| Data           | Primary Source                    | Fallback               |
| -------------- | --------------------------------- | ---------------------- |
| Menu items     | `HeaderNavigation.menu_items`     | —                      |
| Phone number   | `SiteSettings.phone_number`       | —                      |
| Header CTA     | `HeaderNavigation.header_cta_*`   | —                      |
| Mobile CTA     | `HeaderNavigation.mobile_cta_*`   | —                      |
| Footer tagline | `FooterNavigation.tagline`        | `SiteSettings.tagline` |
| Social links   | `FooterNavigation.social_*`       | `SiteSettings.*_url`   |
| Business info  | `SiteSettings.*`                  | —                      |
| Copyright      | `FooterNavigation.copyright_text` | —                      |

See `sum_core.navigation.services` for the effective settings resolver that handles the override/fallback logic.

---

## Related Documentation

- UniversalLinkBlock: `sum_core.blocks.links`
- HeaderNavigation/FooterNavigation models: `sum_core.navigation.models`
- Effective settings resolver: `sum_core.navigation.services`
- Cache invalidation signals: `sum_core.navigation.cache`
- Base templates: `core/sum_core/templates/sum_core/includes/` and `core/sum_core/templates/theme/includes/`
