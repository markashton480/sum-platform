# THEME-001 Follow-up

## Summary
- Updated `test_project` to resolve Theme A templates and statics from repo-level `themes/theme_a` or `core/sum_core/themes/theme_a`, with fallback to `theme/active`.

## Files changed
- `core/sum_core/test_project/test_project/settings.py`

## Notes
- The template `DIRS` ordering already places theme templates before app templates, so no additional change was needed.

## Testing
- Not run (not requested).
