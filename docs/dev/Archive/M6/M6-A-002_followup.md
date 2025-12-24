## M6-A-002 Follow-up — `sum init` theme copy + theme-aware `sum check`

### What shipped

- `sum init --theme <slug>` now validates the selected theme’s on-disk contract **before** scaffolding a client project, and copies the theme into `clients/<client>/theme/active/` **without** copying `node_modules/`.
- `sum check` now validates the **client-installed** theme contract structurally (manifest, base template, compiled CSS, provenance).
- Packaged CLI boilerplate settings now resolve templates/statics from `theme/active/` (matching the monorepo boilerplate + THEME-ARCHITECTURE-SPECv1).

### Key behaviours (Acceptance Criteria mapping)

- AC1: `sum init --theme theme_a foo` creates `clients/foo/theme/active/` with `theme.json`, templates, and `static/theme_a/css/main.css` (compiled).
- AC3/5: `sum init` fails non-zero with clear errors for:
  - unknown theme slugs
  - themes missing critical contract files (e.g. compiled CSS, base template)
  - themes whose compiled CSS is trivial or references `/static/sum_core/css/main.css`
- AC2/4: `sum check` fails non-zero with a short list of missing/invalid theme items, and passes for a valid scaffold.

### Implementation notes

- Transactional-ish theme copy: `sum init` copies into a temp dir under `theme/`, validates, then renames to `theme/active/`. On failure it cleans up.
- `node_modules/` is explicitly excluded during theme copy (even if it exists inside `sum_core/themes/<slug>/`).
- Theme selection is recorded in `.sum/theme.json` and `sum check` enforces that it matches `theme/active/theme.json`.

### Files changed

- `cli/sum_cli/commands/init.py`
- `cli/sum_cli/commands/check.py`
- `cli/sum_cli/boilerplate/project_name/settings/base.py`
- `cli/tests/test_theme_init.py`
- `cli/tests/test_cli_init_and_check.py`

### Verification

- Ran `source .venv/bin/activate && make lint`
  - Ruff/Black/isort passed; mypy currently reports a known duplicate-module issue and is already non-blocking (`mypy . || true`).
- Ran `source .venv/bin/activate && make test`

### Manual checklist

- `sum init --theme theme_a foo`
- `cd clients/foo && sum check` (should pass)
- Start the site and confirm Theme A styles apply without running Node tooling.

