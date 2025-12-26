# Theme Showroom Seeding (`seed_showroom`)

This repo includes a **client-project management command** that seeds a predictable “showroom” site tree for theme development.

It is designed for this workflow:

- `sum init test-project --theme theme_xx`
- `cd clients/test-project`
- `python manage.py seed_showroom`

The goal is a repeatable content + navigation baseline so you can focus on **theme templates + CSS**, not manual Wagtail setup.

---

## Related

Tasks: SQ-002, SQ-003, SQ-004

## Where it lives

`seed_showroom` is part of **boilerplate** (not `sum_core`), because it depends on the **client-owned `HomePage` model**:

- Canonical boilerplate: `boilerplate/project_name/home/management/commands/seed_showroom.py`
- Packaged CLI boilerplate copy: `cli/sum_cli/boilerplate/project_name/home/management/commands/seed_showroom.py`

Maintainers: after editing canonical boilerplate, sync to the CLI copy:

```bash
make sync-cli-boilerplate
make check-cli-boilerplate
```

---

## Usage

From a generated client project directory:

```bash
python manage.py seed_showroom
```

To seed the full block showroom instead of the starter baseline:

```bash
python manage.py seed_showroom --profile showroom
```

## Canonical theme dev override (SQ-003)

For fast showroom iteration, you can point Django at the **canonical theme source** instead of the copied `theme/active` assets.

1. Set the canonical root (must contain `templates/`, `static/` optional):

```bash
export SUM_CANONICAL_THEME_ROOT=/home/mark/workspaces/sum-platform/themes/theme_a
```

2. Run the showroom as normal (e.g. `python manage.py runserver`).
3. Verify templates resolve from the canonical path:

```bash
python manage.py shell -c "from django.template.loader import get_template; t=get_template('theme/base.html'); print(t.origin.name)"
```

If the path is invalid, Django raises `ImproperlyConfigured` with guidance; unset `SUM_CANONICAL_THEME_ROOT` to return to the default `theme/active` copy.

### Options

- **`--clear`**: delete previously seeded showroom pages (by slug) and recreate them.
- **`--profile starter|showroom`**: choose the starter baseline (default) or full showroom profile.
- **`--hostname <host>` / `--port <port>`**: update (or set) the default Wagtail `Site` hostname/port.
- **`--homepage-model app_label.ModelName`**: explicitly choose the client `HomePage` model.

Example:

```bash
python manage.py seed_showroom --clear --hostname localhost --port 8000
```

---

## What it creates

### Site root

- **Default Wagtail `Site`**: ensured/updated (`is_default_site=True`)
- **Root page**: set to the client `HomePage` so the showroom home is served at `/`

### Page tree

Under the HomePage, the command creates:

- **`StandardPage`**: `showroom` → `/showroom/` (showroom profile only)
- **`StandardPage`**: `kitchen-sink` → `/kitchen-sink/` (showroom profile only)
- **`StandardPage`**: `contact` → `/contact/`
- **`StandardPage`**: `terms` → `/terms/`
- **`StandardPage`**: `privacy` → `/privacy/`
- **`StandardPage`**: `cookies` → `/cookies/`
- **`ServiceIndexPage`**: `services` → `/services/`
  - **`ServicePage`**: `solar-installation` → `/services/solar-installation/`
  - **`ServicePage`**: `roofing` → `/services/roofing/`

### Placeholder images

The command generates a set of placeholder images in the **"Showroom" Wagtail Collection** and assigns them to blocks that require images (hero, gallery, portfolio, comparison, trust logos, service featured images, branding logos).

This requires **Pillow** (normally already installed with Wagtail). If Pillow is missing, the command fails fast with an actionable error.

---

## Content strategy: “show all blocks, spread across pages”

The authoritative list of available blocks is `sum_core.blocks.base.PageStreamBlock`. The showroom is designed to include **every block type at least once**.

### HomePage (`/`)

Starter profile HomePage body contains:

- **`hero_image`**
- **`content`**
- **`testimonials`**

Showroom profile HomePage body contains:

- **`hero_image`**
- **`trust_strip_logos`**
- **`service_cards`**
- **`testimonials`**
- **`gallery`**
- **`stats`**

### Showroom page (`/showroom/`)

Showroom body contains:

- **`hero_gradient`**
- **`features`**
- **`comparison`**
- **`manifesto`**
- **`portfolio`**
- **`trust_strip`** (text-only)
- **`editorial_header`**
- **`content`**
- **`table_of_contents`**
- **`legal_section`** (multiple)
- **`quote`**
- **`image_block`**
- **`buttons`**
- **`spacer`**
- **`divider`**
- **`rich_text`** (the plain RichTextBlock)
- **`hero`** (legacy hero block kept for compatibility)

Note: showroom portfolio items include categories so the filter navigation renders.

### Kitchen Sink page (`/kitchen-sink/`)

Kitchen Sink body contains **every block type** available in the showroom, aggregated into a single stream. This is intended for rapid template iteration and visual regression testing without clicking through multiple pages.

### Services index (`/services/`)

ServiceIndexPage intro contains:

- **`content`**
- **`process`**

### Service pages (`/services/*`)

Each ServicePage body contains:

- **`faq`**
- **`quote_request_form`**
- **`contact_form`**
- **`buttons`**

### Contact page (`/contact/`)

Contact page body contains:

- **`editorial_header`**
- **`content`**
- **`contact_form`**

### Legal pages (`/terms/`, `/privacy/`, `/cookies/`)

Legal pages provide anchored sections to validate legal-page layout and typography:

- **`editorial_header`** (center aligned, "Legal" eyebrow)
- **`content`** intro block
- **`table_of_contents`** with anchors
- **`legal_section`** blocks for each section

---

## Navigation + branding seeding

The command seeds the Wagtail settings models used by `sum_core` templates:

### Branding: `sum_core.branding.models.SiteSettings`

Seeds safe defaults for:

- **Business info**: company name, tagline, phone, email, address
- **Theme tokens**: colours + fonts (used by branding CSS tag)
- **Logos**: header/footer/OG + favicon
- **Social URLs**: so footer social icons have data

### Navigation: `sum_core.navigation.models.HeaderNavigation` / `FooterNavigation`

Seeds:

- **Header menu items**: Home, Services (with submenu), Showroom, Contact
- **Header CTA**: enabled + points to Contact
- **Sticky CTA**: enabled, phone enabled, button enabled pointing to Contact
- **Footer sections**: Explore, Services, Company, Legal
  - Explore: Home, Showroom, Kitchen Sink
  - Services: index + both example service pages
  - Company: Contact
  - Legal: Terms + Privacy + Cookies pages, ensuring footer legal links resolve to real pages

Cookie consent wiring:

- `SiteSettings.cookie_banner_enabled` is seeded `True` so the footer renders the **Manage cookies** link.
- `SiteSettings.terms_page`, `privacy_policy_page`, and `cookie_policy_page` point to the seeded legal pages.

Note: footer `tagline` and `social_*` are intentionally set blank so the footer demonstrates **effective settings fallback** to Branding (see `sum_core.navigation.services.get_effective_footer_settings`).

Implementation detail: both Header and Footer navigation are seeded via **StreamField raw data** (`menu_items`, `header_cta_link`, `mobile_cta_button_link`, `link_sections`) rather than a relational `.items.create(...)` API.

---

## Idempotency and safety

### Re-running

Re-running `seed_showroom` is safe:

- It will reuse the existing HomePage (if found by slug) or create a new one if missing.
- It will create missing pages by slug under the HomePage.
- It will overwrite the seeded pages’ bodies/settings to the showroom baseline.

### Clearing

`--clear` removes seeded content safely:

- It identifies the specific seeded HomePage by slug (`showroom-home`).
- It deletes all **descendants** of that page recursively.
- It deletes the home page itself.
- It does **not** rely on global slug deletions (safeguarding user content with similar slugs, like "contact").

---

## Troubleshooting

- **“Could not find a HomePage model”**:
  - Ensure your client `home` app is in `INSTALLED_APPS`
  - Or specify `--homepage-model app_label.HomePage`
- **Pillow missing**:

  - Install `Pillow` (normally included with Wagtail).
  - The command must be able to generate placeholder images because many blocks require images.

- **Kitchen Sink StreamField `TypeError: cannot unpack non-iterable StreamChild object`**:
  - This usually means you combined already-converted StreamField values (iterating a StreamValue yields `StreamChild` objects) and then called `StreamBlock.to_python()` again.
  - Fix pattern: merge _raw_ stream data (e.g. via `stream_value.get_prep_value()`) and only call `to_python()` once, or assign raw stream data directly to the StreamField.
