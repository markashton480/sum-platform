# SUM Platform – Page Types Reference

This document describes the available page types in the SUM Platform core package (`sum_core`).

---

## StandardPage

**Module:** `sum_core.pages.standard`  
**Import:** `from sum_core.pages import StandardPage`

### Purpose

A general-purpose content page for About, FAQ, Terms, Privacy Policy, Service Overview, and other generic content pages. Editors can compose pages using the full set of available blocks without developer involvement.

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `body` | StreamField (PageStreamBlock) | Main content area using the standard block set |

### Available Blocks

StandardPage uses `PageStreamBlock`, which includes:

**Hero Blocks:**
- `hero_image` – Hero with background image
- `hero_gradient` – Hero with gradient background

**Section Blocks:**
- `service_cards` – Grid of service cards
- `testimonials` – Customer testimonial cards
- `gallery` – Image gallery grid
- `trust_strip` – Trust badges/text strip
- `trust_strip_logos` – Logo trust strip
- `stats` – Statistics display
- `process` – Process steps
- `faq` – Accordion FAQ section
- `features` – Features list
- `comparison` – Before/after comparison
- `portfolio` – Portfolio items grid

**Page Content Blocks:**
- `editorial_header` – Section header with eyebrow
- `content` – Rich text content block
- `quote` – Pull quote
- `image_block` – Single image with caption
- `buttons` – Button group
- `spacer` – Vertical spacing
- `divider` – Horizontal divider
- `rich_text` – Simple rich text

### Template

**Path:** `sum_core/templates/sum_core/standard_page.html`

The template:
- Extends `sum_core/base.html`
- Shows a page title header when no hero block is present
- Renders all body blocks via `{% include_block %}`
- Uses design system tokens and classes (no hardcoded values)

### Page Hierarchy

| Setting | Value | Notes |
|---------|-------|-------|
| `parent_page_types` | `["wagtailcore.Page", "home.HomePage"]` | Can be created under site root or HomePage |
| `subpage_types` | `[]` | Leaf page – no children allowed |

### Usage Example

```python
from sum_core.pages import StandardPage

# Create a StandardPage programmatically
page = StandardPage(
    title="About Us",
    slug="about",
    body=[
        ("hero_gradient", {
            "headline": "<p>About <em>Our Company</em></p>",
            "subheadline": "Quality solutions since 2020",
            "ctas": [],
            "status": "",
            "gradient_style": "primary",
        }),
        ("rich_text", "<h2>Our Mission</h2><p>We deliver excellence.</p>"),
    ]
)
parent_page.add_child(instance=page)
```

### Admin Usage

1. In Wagtail admin, navigate to Pages
2. Select a parent page (site root or HomePage)
3. Click "Add child page" → "Standard Page"
4. Add a title and compose content using available blocks
5. Publish when ready

---

## HomePage

**Module:** `home.models` (test project)  
**Note:** HomePage is **client-owned** (it is intentionally not shipped as a core page type in `sum_core`).
The repo includes a harness-only HomePage in `core/sum_core/test_project/home/` for local dev + CI validation, and the canonical consumer example lives in `clients/sum_client/sum_client/home/models.py`.

### Purpose

Site homepage with intro text and StreamField body using `PageStreamBlock`.

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `intro` | RichTextField | Optional intro text (shown when no hero) |
| `body` | StreamField (PageStreamBlock) | Main content area |

### Template

**Path:** `sum_core/templates/sum_core/home_page.html`

---

## Adding to Client Projects

To use `StandardPage` in a client project:

1. Add `sum_core.pages` to `INSTALLED_APPS`:
   ```python
   INSTALLED_APPS = [
       # ...
       "sum_core",
       "sum_core.pages",
       # ...
   ]
   ```

2. Run migrations:
   ```bash
   python manage.py migrate
   ```

3. StandardPage will appear as a creatable page type in Wagtail admin.

