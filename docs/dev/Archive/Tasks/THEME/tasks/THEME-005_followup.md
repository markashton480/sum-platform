## THEME-005 Follow-up Report

### Mission Recap

Align theme source-of-truth to `docs/dev/master-docs/THEME-ARCHITECTURE-SPECv1.md` by establishing repo-root `themes/` as canonical, migrating Theme A, updating wiring/tooling, and updating documentation so future work doesn’t drift.

### High-Level Outcome

- **Canonical theme source is now repo-root `themes/`** (Theme A lives at `themes/theme_a/`).
- **`core/sum_core/themes/theme_a/` was removed** so there’s no “two sources” ambiguity.
- **CLI theme discovery now follows Spec v1** (supports `SUM_THEME_PATH`, then `./themes`, no longer depends on `sum_core.themes`).
- **Docs updated** to reflect the new canonical layout + template/static wiring contract.
- **Guardrails/tests updated** to reference repo-root themes and the new Tailwind toolchain layout.

---

### What Changed (Implementation)

#### 1) Canonical repo-root `themes/` added + Theme A migrated

- **Added**: `themes/theme_a/` with spec-aligned structure:
  - `theme.json`
  - `templates/` (includes `templates/theme/*` and `templates/sum_core/*` overrides)
  - `static/theme_a/...` (compiled CSS + optional JS)
  - `tailwind/` (maintainer toolchain)
- **Moved toolchain into `tailwind/`**:
  - `themes/theme_a/tailwind/package.json` scripts updated to build into `../static/theme_a/css/main.css`
  - `themes/theme_a/tailwind/tailwind.config.js` content globs updated for the new directory depth
  - `themes/theme_a/build_fingerprint.py` updated to hash `tailwind/tailwind.config.js` + `tailwind/postcss.config.js` and all templates under `templates/`
- **Removed**: `core/sum_core/themes/theme_a/` (old location).

#### 2) Demoted `sum_core.themes` as canonical

- Updated `core/sum_core/themes/__init__.py` to explicitly mark it **deprecated** and to stop claiming “themes shipped with sum_core are canonical sources”.

#### 3) CLI now resolves themes via Spec v1 (repo-root `themes/`)

- **Added**: `cli/sum_cli/themes_registry.py`
  - Search order:
    1. `SUM_THEME_PATH` (can point to a single theme dir or a themes-root dir)
    2. `./themes/<slug>` (repo-local canonical)
    3. (Bundled CLI themes: intentionally not implemented yet)
- Updated:
  - `cli/sum_cli/commands/init.py` to use `sum_cli.themes_registry` (no `sum_core.themes` dependency)
  - `cli/sum_cli/commands/themes.py` to list themes via `sum_cli.themes_registry`
  - CLI tests to use `SUM_THEME_PATH` override for fake theme registries and to reflect the new `tailwind/` folder layout.

---

### What Changed (Tests / Guardrails)

- Updated Theme A guardrail/toolchain tests to use **repo-root `themes/theme_a`**:
  - `tests/themes/test_theme_a_guardrails.py`
  - `tests/themes/test_theme_a_tailwind.py`
  - `tests/themes/test_theme_a_rendering.py`
- Updated theme discovery tests to validate **CLI theme discovery** (not `sum_core.themes`):
  - `tests/themes/test_theme_discovery.py`
- Added a small harness wiring guardrail:
  - `tests/themes/test_test_project_theme_wiring.py` asserts:
    - `themes/theme_a/` exists (theme.json + templates + static)
    - `core/sum_core/test_project/test_project/settings.py` includes repo-root `REPO_ROOT / "themes" / "theme_a"` as candidates

---

### Documentation Updates

Updated “pointer docs” to align to Theme Architecture Spec v1:

- `docs/dev/CODEBASE-STRUCTURE.md`
  - Added repo-root `themes/`
  - Updated the “Client Projects” section to reflect the **theme → overrides → core** template resolution order
- `docs/dev/WIRING-INVENTORY.md`
  - Added **Theme Wiring (v0.6+)** section: where themes live, resolution order, and static expectations
- `docs/dev/master-docs/POST-MVP_BIG-PLAN.md`
  - Updated example theme file structure to `themes/theme_a/...`
  - Updated the “Theme Distribution Method” decision block to match the canonical repo-root `themes/` model
- Note: historical task/chat/prompt artifacts were intentionally left as-is (audit trail preserved).

---

### Verification Notes / How To Test Locally

#### Harness (manual)

- Confirm Theme A templates + statics are discoverable from repo-root themes:
  - `python core/sum_core/test_project/manage.py runserver`
  - Edit a file under `themes/theme_a/templates/...` and refresh to verify it’s picked up.

#### CLI (manual)

- From repo root:
  - `python -m sum_cli init <project-name> --theme theme_a` (or equivalent CLI entrypoint you use)
  - Confirm `clients/<project>/theme/active/` contains:
    - `templates/`, `static/`, `tailwind/`, `theme.json`

#### Tailwind rebuild (maintainers only)

```bash
cd themes/theme_a/tailwind
npm install
npm run build
python ../build_fingerprint.py
git add ../static/theme_a/css/main.css ../static/theme_a/css/.build_fingerprint
```

#### Automated tests

- Ran full suite in repo venv:
  - `./venv/bin/python -m pytest`
  - Result: **717 passed**

Note: `source venv/bin/activate` in this workspace did not update PATH correctly, so using `./venv/bin/python` is the reliable invocation here.

---

### Observations / Red Flags / Potential Follow-ups

- **Audit trail integrity**: I initially (incorrectly) edited historical audit artifacts while doing doc updates. Those changes have been reverted so only the final pointer docs are updated.
- **`sum_core.themes` still exists** (deprecated). If you want strict separation of “presentation assets live outside sum_core,” we can consider removing it entirely later (once no tooling/tests depend on it).
- **Bundled CLI themes not implemented**: `sum_cli.themes_registry` currently supports the spec’s first two resolution steps (env override and repo-local `./themes`). The “bundled themes inside CLI package” step is intentionally left as a future addition.

---

### Files Touched (High Signal)

- **Canonical themes**: `themes/theme_a/...` (new)
- **Removed old location**: `core/sum_core/themes/theme_a/...` (deleted)
- **CLI**:
  - `cli/sum_cli/themes_registry.py` (new)
  - `cli/sum_cli/commands/init.py` (updated)
  - `cli/sum_cli/commands/themes.py` (updated)
- **Tests**: `tests/themes/*` (updated + new harness wiring test)
- **Docs**: `docs/dev/CODEBASE-STRUCTURE.md`, `docs/dev/WIRING-INVENTORY.md`, `docs/dev/master-docs/POST-MVP_BIG-PLAN.md` (+ supporting theme docs)


