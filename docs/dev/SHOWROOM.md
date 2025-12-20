# Theme Showroom Seeding (`seed_showroom`)

This repo includes a **client-project management command** that seeds a predictable “showroom” site tree for theme development.

It is designed for this workflow:

- `sum init test-project --theme theme_xx`
- `cd clients/test-project`
- `python manage.py seed_showroom`

The goal is a repeatable content + navigation baseline so you can focus on **theme templates + CSS**, not manual Wagtail setup.

---

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

### Options

- **`--clear`**: delete previously seeded showroom pages (by slug) and recreate them.
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

- **`StandardPage`**: `showroom` → `/showroom/`
- **`StandardPage`**: `kitchen-sink` → `/kitchen-sink/`
- **`StandardPage`**: `contact` → `/contact/`
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

HomePage body contains:

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
- **`quote`**
- **`image_block`**
- **`buttons`**
- **`spacer`**
- **`divider`**
- **`rich_text`** (the plain RichTextBlock)
- **`hero`** (legacy hero block kept for compatibility)

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
- **Footer sections**: “Company” and “Services”
  - Includes a variety of `UniversalLinkBlock` link types: page, url, email, phone
  - Explicitly adds a "Kitchen Sink" link to the footer for easy access.

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
  - Fix pattern: merge *raw* stream data (e.g. via `stream_value.get_prep_value()`) and only call `to_python()` once, or assign raw stream data directly to the StreamField.
