# THEME-024 Followup

## Summary
- Rewrote Theme A ImageBlock template with semantic figure/caption markup, full-width layout toggle, and reveal hooks.
- Added Theme A image block rendering tests for template origin, alt text, caption optionality, and width classes.
- Rebuilt Theme A CSS artifacts and fingerprint after template changes.

## Files Modified/Created
- themes/theme_a/templates/sum_core/blocks/content_image.html
- tests/themes/test_theme_a_image_block_rendering.py
- themes/theme_a/static/theme_a/css/main.css
- themes/theme_a/static/theme_a/css/.build_fingerprint
- docs/dev/THEME/tasks/THEME-024_followup.md

## Test Results
- `pytest -q tests/themes/test_theme_a_image_block_rendering.py`
- `make test`
- `make lint`

## Decisions / Blockers
- None

## Doc Updates
- None
