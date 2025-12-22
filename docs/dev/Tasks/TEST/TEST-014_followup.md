# TEST-014 Follow-up: Theme Test Conftest + Standard Fixtures

## Summary

Upgraded `tests/themes/conftest.py` with standard fixtures and refactored 4 theme test files to use centralized `tests.utils.REPO_ROOT` instead of bespoke path resolution.

## Fixtures Added/Changed

### New Session-Scoped Fixtures

| Fixture                 | Description                                                  |
| ----------------------- | ------------------------------------------------------------ |
| `themes_root_dir`       | Returns `REPO_ROOT / "themes"` — single source of truth      |
| `available_theme_slugs` | Dynamically discovers theme slugs from `themes/*/theme.json` |
| `theme_a_dir`           | Convenience shortcut for Theme A path                        |

### Parametrized Fixtures

| Fixture     | Description                                             |
| ----------- | ------------------------------------------------------- |
| `theme_dir` | Parametrized across themes; yields `(slug, Path)` tuple |

### Helper Functions

| Function                         | Description                                     |
| -------------------------------- | ----------------------------------------------- |
| `theme_templates_dir(path)`      | Returns `path / "templates"`                    |
| `theme_static_dir(path, slug)`   | Returns `path / "static" / slug`                |
| `assert_theme_template_origin()` | Verifies template origin matches expected theme |

### Autouse Decisions

- `theme_filesystem_sandbox` remains `autouse=True` — scoped to `tests/themes/` by file location
- All other fixtures are **not** autouse to avoid unexpected side effects outside theme tests

## Files Refactored

Replaced bespoke `repo_root = Path(__file__).resolve().parents[2]` with centralized import:

1. `tests/themes/conftest.py` — upgraded with standard fixtures
2. `tests/themes/test_theme_a_contract.py`
3. `tests/themes/test_theme_a_guardrails.py`
4. `tests/themes/test_theme_a_tailwind.py`
5. `tests/themes/test_theme_discovery.py`

## Verification Output

```
$ make lint
ruff check . --config pyproject.toml
All checks passed!
mypy core cli tests
Success: no issues found in 250 source files
black --check core cli tests
All done! ✨ 🍰 ✨
231 files would be left unchanged.
isort --check-only core cli tests
Skipped 44 files

$ pytest tests/themes/ --collect-only
========================= 69 tests collected in 3.06s ==========================

$ make test-themes
================== 69 passed, 7 warnings in 66.38s (0:01:06) ===================

$ make test-templates
======================== 4 passed, 7 warnings in 52.55s ========================

$ make test
================= 752 passed, 45 warnings in 184.14s (0:03:04) =================

$ git status --porcelain
# Only expected modified files (5 theme test files)
```

## Success Criteria Met

- ✅ Theme tests collect cleanly without import errors
- ✅ `make test-themes` passes unchanged (69 tests)
- ✅ No repo dirt after runs
- ✅ No autouse leakage outside `tests/themes/`
- ✅ No mutation of protected dirs or theme source
