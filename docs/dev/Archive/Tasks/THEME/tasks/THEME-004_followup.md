# THEME-004 Follow-up — ManifestoBlock (end-to-end)

## Summary

Implemented **`ManifestoBlock`** end-to-end:

- Added canonical **Wagtail block definition** in `sum_core`
- Registered the block in the canonical **`PageStreamBlock`** so editors can add it on pages that use `PageStreamBlock` (StandardPage + client-owned HomePage patterns)
- Added a **Theme A template override** for the block (and a safe core fallback template)
- Added **minimal tests** and updated the **blocks reference docs**
- Verified **migrations + tests using Postgres**

## What changed

### 1) Block definition

- **File**: `core/sum_core/blocks/content.py`
- **New block**: `ManifestoBlock`
- **Fields**:
  - `eyebrow` (optional)
  - `heading` (optional, RichText; italic/bold)
  - `body` (optional, RichText; bold/italic/link/ol/ul)
  - `quote` (optional)
  - `cta_label` + `cta_url` (both optional; only rendered when both provided)

Design intent is a single semantic “manifesto” section matching the Theme A wireframe structure (eyebrow → heading → prose → optional quote + CTA).

### 2) Registration in the correct StreamField

- **File**: `core/sum_core/blocks/base.py`
- **Change**: Registered `manifesto = ManifestoBlock(group="Sections")` inside `PageStreamBlock`.

This is the canonical StreamBlock used by:

- `core/sum_core/pages/standard.py` (`StandardPage.body`)
- `core/sum_core/pages/services.py` (`ServiceIndexPage.intro`, `ServicePage.body`)
- client-owned HomePage implementations that use `PageStreamBlock` (including the harness `core/sum_core/test_project/home/HomePage`)

### 3) Theme A template + fallback template

- **Theme A override**:
  - `core/sum_core/themes/theme_a/templates/sum_core/blocks/manifesto.html`
  - Tailwind-styled, centered layout aligned to the wireframe’s manifesto section.

- **Core fallback** (non-theme-owned rendering):
  - `core/sum_core/templates/sum_core/blocks/manifesto.html`
  - Minimal, safe markup so the block renders even when no theme override is installed.

### 4) Migrations

- **Migration**: `core/sum_core/pages/migrations/0007_alter_serviceindexpage_intro_alter_servicepage_body_and_more.py`
- **Why**: Adding a new child block to `PageStreamBlock` changes the StreamField definitions on page models in `sum_core_pages`.

Non-negotiable checks:

- No unrelated migrations were generated.
- `makemigrations --check` is clean after generating `0007`.

### 5) Tests added/updated

Minimal coverage added to assert the block exists, is registered, and renders:

- `tests/blocks/test_content_blocks.py`
  - New `test_manifesto_block_definition`
- `tests/blocks/test_page_streamblock.py`
  - Assert `manifesto` is present in `PageStreamBlock`
- `tests/pages/test_home_page.py`
  - New `test_home_page_renders_manifesto_block` smoke test

### 6) Docs updated

- **File**: `docs/dev/blocks-reference.md`
- Added:
  - Quick reference entry for `manifesto`
  - Full ManifestoBlock section with field table + notes

## Postgres verification

### Database vendor

Used the repo’s Postgres container from `docker-compose.yml` and ran Django management commands/tests with Postgres env vars set:

- `DJANGO_DB_NAME=sum_db`
- `DJANGO_DB_USER=sum_user`
- `DJANGO_DB_PASSWORD=sum_password`
- `DJANGO_DB_HOST=localhost`
- `SUM_TEST_DB=postgres` (forces Postgres for pytest via harness settings)

### Commands executed (high level)

- `docker compose up -d db`
- `python manage.py makemigrations --check --dry-run` (Postgres env set)
- `python manage.py makemigrations sum_core_pages` → produced `0007`
- `python manage.py migrate` (Postgres)
- `pytest` (Postgres)

Result: **test suite passes under Postgres**.

## Files touched (git-level)

- `core/sum_core/blocks/content.py`
- `core/sum_core/blocks/base.py`
- `core/sum_core/blocks/__init__.py`
- `core/sum_core/pages/migrations/0007_alter_serviceindexpage_intro_alter_servicepage_body_and_more.py`
- `core/sum_core/themes/theme_a/templates/sum_core/blocks/manifesto.html`
- `core/sum_core/templates/sum_core/blocks/manifesto.html`
- `docs/dev/blocks-reference.md`
- `tests/blocks/test_content_blocks.py`
- `tests/blocks/test_page_streamblock.py`
- `tests/pages/test_home_page.py`

## Notes / gotchas

- The harness settings now force theme templates to resolve from `theme/active/templates` **during pytest**, to keep tests deterministic and to ensure the Theme A rendering tests explicitly install the theme into `theme/active/` (matching the v0.6 theme contract).

## How to manually verify in Wagtail

1. Run the harness with Postgres configured (same env vars as above).
2. In Wagtail admin, edit the HomePage/StandardPage `body` StreamField.
3. Add **Manifesto** (group: **Sections**).
4. Fill eyebrow/heading/body/quote and publish.
5. Confirm it renders via Theme A with the centered manifesto layout.



