# TEST-012: Follow-Up Report

**Date:** 2025-12-22  
**Branch:** `test/TEST-012-template-resolution`  
**Status:** ✅ Complete

## Summary

Implemented Phase 2 of the test strategy (Root Cause Fixes) by:

1. Documenting deterministic template resolution in `settings.py`
2. Adding core-only fallback test (`trust_strip.html`)
3. Creating `make test-templates` Makefile target
4. Adding `test-templates` CI gate

## Audit Findings

### `RUNNING_TESTS` Usage in settings.py

| Lines   | Usage              | Affects Templates? |
| ------- | ------------------ | ------------------ |
| 29      | Detection flag     | No                 |
| 182-183 | Skip DB validation | No                 |
| 185-203 | SQLite vs Postgres | No                 |

**Result:** Template resolution was already deterministic. No code changes required beyond documentation.

### Template Resolution Order (unchanged)

```
1. theme/active/templates     (client-owned, from sum init)
2. themes/theme_a/templates   (repo-root, local dev)
3. sum_core/templates         (APP_DIRS fallback)
```

## Test Template Selection

| Test Case        | Template                           | Location                      |
| ---------------- | ---------------------------------- | ----------------------------- |
| Theme precedence | `sum_core/blocks/stats.html`       | Theme A (overrides core)      |
| Consistency      | `sum_core/blocks/hero_image.html`  | Theme A                       |
| Core fallback    | `sum_core/blocks/trust_strip.html` | Core only (no theme override) |

## Files Modified/Added

- `core/sum_core/test_project/test_project/settings.py` — Added inline documentation
- `tests/templates/test_template_loading_order.py` — Added `test_core_only_template_resolves_from_core`
- `Makefile` — Added `test-templates` target
- `.github/workflows/ci.yml` — Added `test-templates` job

## Verification Output

```
make lint                   ✅ All checks passed
pytest tests/templates/...  ✅ 4 passed
make test-cli               ✅ 16 passed
make test-themes            ✅ 69 passed
make test                   ✅ 752 passed
```

## CI Gate Design

The new `test-templates` job:

- Runs after `lint` gate
- 5-minute timeout (fast fail)
- Includes protected-assets guard
- Independent of other test jobs (parallel execution)
