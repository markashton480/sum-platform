# TEST-014B Follow-up: Unicode cleanup + dynamic theme discovery

## Summary
- Verified tests/themes contain no hidden non-ASCII control/space characters.
- Updated `theme_dir` fixture to dynamically parametrize over available themes via `themes/` directory.
- All lint and test suites pass on branch `test/TEST-014-theme-conftest`.

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

$ make test-themes
=================================================== 69 passed, 7 warnings in 50.51s ===================================================

$ make test-templates
========================================================================================================== 4 passed, 7 warnings in 47.66s ==========================================================================================================

$ make test
============================================= 752 passed, 45 warnings in 250.79s (0:04:10) =============================================
```

## Notes
- Hidden Unicode scan: no non-ASCII control/space characters detected in `tests/themes/*.py` (checked with Python unicodedata scan).
- Branch clean after commits.
