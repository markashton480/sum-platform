# M4-004B Follow-up Report

Date: 2025-12-14

## Summary

The runtime error `TemplateSyntaxError: 'seo_tags' is not a registered tag library` was caused by Django not discovering the `seo_tags` template tag module, even though it existed in `core/sum_core/seo/templatetags/seo_tags.py`.

In parallel, several SEO-related tests were brittle (Treebeard state corruption) and some template integration tests started failing once SEO tags were wired into `base.html`.

All issues below have been addressed and validated with `make lint` + `make test`.

## Findings & fixes

### 1) `seo_tags` not registered (browser traceback)

**Root cause**

- Django only discovers template tag libraries from `templatetags/` packages inside **installed apps**.
- The `seo_tags` module lived under the `sum_core.seo` package, but `sum_core.seo` was not in `INSTALLED_APPS`.

**Fix**

- Added `sum_core.seo` to `INSTALLED_APPS` in `core/sum_core/test_project/test_project/settings.py`.

### 2) SEO tags crashing when `page` context is missing

**Root cause**

- Some template integration tests render `sum_core/base.html` without providing a Wagtail `page` in context.
- In Django templates, an undefined variable resolves to `""` (empty string). Calling `{% render_meta page %}` with `page=""` caused `getattr(page, "title", "")` to resolve to `str.title` (a method), leading to `AttributeError` when `.strip()` was called.

**Fix**

- Guarded calls to `{% render_meta page %}` / `{% render_og page %}` behind `{% if page %}` in `core/sum_core/templates/sum_core/base.html`.

### 3) Tests trying to connect to local Postgres

**Root cause**

- The test project settings load a `.env` and switch to Postgres when `DJANGO_DB_HOST` + `DJANGO_DB_NAME` are present.
- In this environment that pointed at a non-running local Postgres, causing immediate test failure.

**Fix**

- Updated `core/sum_core/test_project/test_project/settings.py` to force SQLite when running under pytest (detect via `sys.argv`), unless explicitly overridden via `SUM_TEST_DB=postgres`.

### 4) Treebeard corruption from bulk deletes (fixture instability)

**Root cause**

- `HomePage.objects.all().delete()` (bulk delete) bypasses Treebeard’s node maintenance, leaving the Wagtail page tree in an inconsistent state (e.g. parent `numchild` incorrect).
- This manifested as Treebeard errors like `AttributeError: 'NoneType' object has no attribute '_inc_path'` when adding new pages in later tests.

**Fix**

- Updated `tests/conftest.py` to delete HomePage instances via `homepage.delete()` in a loop (Treebeard-safe).

### 5) Reinstate/strengthen SEO template-tag test coverage (M4-004B contract)

**Changes**

- Rewrote `tests/seo/test_seo_tags.py` to explicitly encode the SEO contract from `docs/dev/M4/M4-004B.md`:
  - Meta title precedence: `meta_title` → `seo_title` → default `{title} | {company_name}`
  - Meta description precedence: `meta_description` → `search_description` → omitted
  - Robots truth table (4 combinations)
  - Canonical URL is absolute and host/path-correct
  - Open Graph: `og:title`, `og:description`, `og:url`, `og:type`, `og:site_name`, image fallback chain + omission rules

**Note on “missing tests”**

- The transcript mentions a removed `tests/seo/test_imports.py`, but it was not present in git history. Coverage that would have provided has effectively been subsumed by the integration assertions in `tests/seo/test_seo_tags.py` (if `seo_tags` cannot be loaded, these tests fail immediately).

### 6) Small implementation alignment

- Updated `core/sum_core/pages/mixins.py` `SeoFieldsMixin.get_meta_description()` to match platform precedence (`meta_description` → `search_description`).
- Updated `core/sum_core/seo/templatetags/seo_tags.py` to align meta/OG behaviour with the contract (canonical-driven `og:url`, description fallbacks, OG image fallback chain, deterministic robots output).

## Verification

- `make lint` (Ruff passes; mypy output remains as before because it is run as `mypy . || true`)
- `make test` (556 tests passed)

## Files changed

- `core/sum_core/test_project/test_project/settings.py`
- `core/sum_core/templates/sum_core/base.html`
- `core/sum_core/seo/templatetags/seo_tags.py`
- `core/sum_core/pages/mixins.py`
- `tests/seo/test_seo_tags.py`
- `tests/conftest.py`

