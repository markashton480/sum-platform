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

| Fixture     | Description                                                  |
| ----------- | ------------------------------------------------------------ |
| `theme_dir` | Parametrized across themes; yields `Path` to theme directory |

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

## Verification Output (close-out)

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

$ make test-themes
=================================================== 69 passed, 7 warnings in 50.61s ===================================================

$ make test-templates
==================================================== 4 passed, 7 warnings in 43.76s ====================================================

$ make test
============================================= 752 passed, 45 warnings in 167.15s (0:02:47) =============================================

$ git status --porcelain
?? docs/dev/Tasks/TEST/TEST-14A.md
?? docs/dev/reports/REDFLAGS.md
```

> Note: working tree shows two pre-existing untracked files (not part of this ticket). No tracked files are modified.

## Success Criteria Met

- ✅ Theme tests collect cleanly without import errors
- ✅ `make test-themes` passes unchanged (69 tests)
- ✅ No repo dirt after runs
- ✅ No autouse leakage outside `tests/themes/`
- ✅ No mutation of protected dirs or theme source
