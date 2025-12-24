# CM-M6-03 Follow-up Report

**Task**: Align Theme System Implementation with THEME-ARCHITECTURE-SPECv1  
**Completed**: 2025-12-17  
**Status**: ✅ Complete

---

## Summary

Corrected the M6-002 theme system implementation to conform to **THEME-ARCHITECTURE-SPECv1**. The key change was moving from a **pointer-based model** (loading themes directly from `sum_core` at runtime) to a **copy-into-client model** (copying theme files into `theme/active/` at init-time).

---

## Changes Made

### 1. `core/sum_core/themes/__init__.py`

**Added**: `get_theme_dir()` helper function

```python
def get_theme_dir(slug: str) -> Path:
    """Get the root directory path for a theme."""
```

This function returns the absolute path to a theme's source directory in `sum_core`, enabling the CLI to copy it during `sum init`.

---

### 2. `cli/sum_cli/commands/init.py`

**Added**: `_copy_theme_to_active()` function

- Copies selected theme from `sum_core/themes/<slug>/` into `<client>/theme/active/`
- Preserves full structure: `theme.json`, `templates/`, `static/`, `tailwind/` (if present)

**Updated**: `_write_theme_config()` function

- Now accepts `theme_version` parameter
- Records provenance with `original_version` field (not used for runtime loading)

**Updated**: `run_init()` function

- Stores theme manifest to capture version
- Calls `_copy_theme_to_active()` before writing provenance
- Passes theme version to `_write_theme_config()`

---

### 3. `boilerplate/project_name/settings/base.py`

**Complete rewrite of theme configuration section**:

| Before (M6-002)                                                | After (CM-M6-03)                              |
| -------------------------------------------------------------- | --------------------------------------------- |
| Read theme slug from `.sum/theme.json`                         | Read theme slug for logging only (provenance) |
| Load templates from `sum_core.themes.get_theme_template_dir()` | Load templates from `theme/active/templates/` |
| No theme static file handling                                  | Added `_get_theme_static_dirs()` helper       |

**Template resolution order now**:

1. `theme/active/templates/` (client-owned theme)
2. `templates/overrides/` (client-specific overrides)
3. APP_DIRS fallback (`sum_core` templates)

**Static file resolution order now**:

1. `theme/active/static/` (client-owned theme)
2. `static/` (client-specific statics)

---

### 4. `cli/tests/test_theme_init.py`

**Updated existing tests**:

- `test_init_with_theme_creates_theme_config` now verifies `original_version` field

**Added new test**:

- `test_init_copies_theme_to_active_directory` - comprehensive test verifying:
  - `theme/active/` directory exists
  - `theme.json` manifest is copied
  - `templates/` directory is copied with expected files
  - `static/` directory is copied with expected files

**Updated**:

- `test_init_default_theme_is_theme_a` now also verifies theme copy

---

## Verification Results

### Automated Tests

```
672 passed, 45 warnings in 174.64s
```

All tests pass, including 4 theme-specific tests:

- `test_init_with_theme_creates_theme_config`
- `test_init_copies_theme_to_active_directory`
- `test_init_with_invalid_theme_fails`
- `test_init_default_theme_is_theme_a`

### Linting

```
ruff check . → All checks passed!
mypy . → Pre-existing duplicate module warning (unrelated)
black --check . → No changes needed
isort --check-only . → No changes needed
```

### Manual Verification

Created test project with `sum init test-project --theme theme_a`:

**✅ theme/active/ structure created**:

```
theme/active/
├── static/
│   └── theme_a/
│       └── css/
│           └── main.css
├── templates/
│   └── theme_a/
│       ├── base.html
│       ├── home_page.html
│       ├── includes/
│       │   ├── footer.html
│       │   ├── header.html
│       │   └── sticky_cta.html
│       ├── service_index_page.html
│       ├── service_page.html
│       └── standard_page.html
└── theme.json
```

**✅ .sum/theme.json provenance**:

```json
{
  "theme": "theme_a",
  "original_version": "1.0.0",
  "locked_at": "2025-12-17T18:25:28.113792+00:00"
}
```

**✅ Settings correctly configured**:

- Templates resolve from `theme/active/templates/` first
- Static files resolve from `theme/active/static/` first
- No runtime dependency on `sum_core.themes` for template/static loading

---

## Acceptance Criteria

| Criteria                                                              | Status |
| --------------------------------------------------------------------- | ------ |
| `sum init --theme <slug>` copies theme into `theme/active/`           | ✅     |
| Client project runs without referencing theme templates in `sum_core` | ✅     |
| Template resolution prioritises `theme/active/`                       | ✅     |
| Static assets are served from client-owned theme directory            | ✅     |
| `.sum/theme.json` records provenance only                             | ✅     |
| No regressions to M5 or other M6-002 functionality                    | ✅     |
| Existing tests pass; new tests added only where required              | ✅     |

---

## Technical Notes

### Why This Matters

The copy-into-client model provides:

1. **Theme ownership clarity** - Client owns their theme files, modifications are local
2. **Predictable upgrades** - Updating `sum_core` doesn't change client theme
3. **Offline capability** - Client site works without access to `sum_core` themes
4. **Easier debugging** - Theme files visible in client repo

### Immutability Rules (Unchanged)

- Theme selection remains **init-time only**
- No CLI support for switching themes post-init
- Manual migration required for theme changes

---

## Files Changed

| File                                        | Change Type                                     |
| ------------------------------------------- | ----------------------------------------------- |
| `core/sum_core/themes/__init__.py`          | Modified (added `get_theme_dir()`)              |
| `cli/sum_cli/commands/init.py`              | Modified (added copy logic, updated provenance) |
| `boilerplate/project_name/settings/base.py` | Modified (rewrote theme resolution)             |
| `cli/tests/test_theme_init.py`              | Modified (updated + added tests)                |
| `docs/dev/CM/M6/CM-M6-03.md`                | Modified (marked criteria complete)             |

---

## Remaining Work

None. Task complete.

---

## Related Tasks

- **M6-002**: Original theme system implementation (superseded by this CM)
- **M6-003** (Theme A – Sage & Stone): Can now proceed without hidden coupling to platform internals
