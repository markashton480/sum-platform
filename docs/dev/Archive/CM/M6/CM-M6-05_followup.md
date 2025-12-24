# **[CM-M6-05]: Adopt v0.6 Theme-Owned Rendering Contract (Forward Cut) — Follow‑Up**

## Outcome

Implemented the **v0.6 theme-owned rendering contract**:

- v0.6 page models now reference `theme/...` template paths (not `sum_core/...`).
- Theme A is reshaped to provide canonical templates at `templates/theme/…` (no `templates/sum_core/` shadowing).
- `sum_core` now ships **fallback** templates under `sum_core/templates/theme/…` so `theme/...` always resolves even without a client theme.
- The test harness is **neutral**: no theme apps in `INSTALLED_APPS`, no precedence tricks.
- Tests validate rendering via the new contract and assert Theme A DOM hooks.

This is a **forward cut** (legacy v0.5 behaviour not targeted for preservation).

---

## Rendering Contract Implementation

### 1) v0.6 model template paths

Updated these v0.6 page models to use `theme/<page>.html` (with a short inline comment noting the contract):

- `HomePage` → `theme/home_page.html`
- `StandardPage` → `theme/standard_page.html`
- `ServiceIndexPage` → `theme/service_index_page.html`
- `ServicePage` → `theme/service_page.html`

### 2) Theme A canonical templates

Theme A templates are now located at:

`core/sum_core/themes/theme_a/templates/theme/`

Required structure is present:

```
theme/
├── base.html
├── home_page.html
├── standard_page.html
├── service_index_page.html
├── service_page.html
└── includes/
    ├── header.html
    ├── footer.html
    └── sticky_cta.html
```

Theme A templates now reference `theme/...` includes/extends internally (no `theme_a/...` template namespace, and no `sum_core/...` shadowing directory).

### 3) Core fallback templates

Added SUM Core fallback templates under:

`core/sum_core/templates/theme/`

These are safe/minimal fallbacks for when `theme/active/templates/` is missing.

Legacy v0.5 `sum_core/...` page templates were retained but converted into **thin wrappers** that extend the new `theme/...` fallbacks (and include comments marking them legacy).

### 4) Neutral test harness (no hacks)

`core/sum_core/test_project/test_project/settings.py` now:

- Removes `sum_core.themes.theme_a` from `INSTALLED_APPS`
- Adds `theme/active/templates` + `templates/overrides` to `TEMPLATES[0]["DIRS"]`
- Adds `theme/active/static` to `STATICFILES_DIRS`

No new template loaders were introduced; this is purely configuration + template path updates.

---

## Test Updates

- Updated tests to assert v0.6 template paths (`theme/...`).
- Updated template-wiring tests to extend/include `theme/...` paths.
- Updated Theme A rendering tests to validate the contract by copying Theme A templates into `theme/active/templates/` during the test run and asserting Theme A DOM hooks (e.g. `id="main-header"`).
- Updated CLI init test to expect Theme A templates under `theme/active/templates/theme/…` (not `theme_a/…`).

---

## Files Changed (High Signal)

### Page models
- `core/sum_core/pages/standard.py`
- `core/sum_core/pages/services.py`
- `core/sum_core/test_project/home/models.py`

### Theme A templates
- `core/sum_core/themes/theme_a/templates/theme/…` (moved/updated)
- Removed template-shadowing directory: `core/sum_core/themes/theme_a/templates/sum_core/…`

### Core fallback templates
- Added: `core/sum_core/templates/theme/…`
- Updated legacy wrappers: `core/sum_core/templates/sum_core/base.html`, `core/sum_core/templates/sum_core/home_page.html`, `core/sum_core/templates/sum_core/standard_page.html`, `core/sum_core/templates/sum_core/service_index_page.html`, `core/sum_core/templates/sum_core/service_page.html`

### Test harness + tests
- `core/sum_core/test_project/test_project/settings.py`
- `tests/themes/test_theme_a_rendering.py`
- `tests/pages/test_home_page.py`
- `tests/pages/test_standard_page.py`
- `tests/pages/test_service_pages.py`
- `tests/templates/test_navigation_template.py`
- `cli/tests/test_theme_init.py`

---

## Verification

Run commands (from repo root):

- Tests: `.venv/bin/python -m pytest`
- Lint: `PATH=\"$PWD/.venv/bin:$PATH\" make lint`

Result:

- All tests passed locally.
- Lint passed locally.

Note: pytest-cov emitted warnings about an existing corrupted `.coverage` file in this workspace (`no such table: tracer`). Deleting `.coverage` resolves that, but it’s not caused by the changes in this CM.

