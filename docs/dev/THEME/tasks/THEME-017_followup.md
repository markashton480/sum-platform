# THEME-017 Followup

## Summary
- Implemented Theme A FAQ block markup aligned with the Sage & Stone wireframe while preserving FAQPage JSON-LD.
- Added Theme A FAQ accordion JS behavior honoring allow-multiple and a no-JS first item open state.
- Added Theme A FAQ rendering tests for structure, content, JSON-LD, and allow-multiple flag.

## Files Modified/Created
- Modified: themes/theme_a/templates/sum_core/blocks/faq.html
- Modified: themes/theme_a/static/theme_a/js/main.js
- Created: tests/themes/test_theme_a_faq_rendering.py
- Created: docs/dev/THEME/tasks/THEME-017_followup.md

## Test Results
- `source .venv/bin/activate && pytest -q tests/themes -k faq` (passed)
- `source .venv/bin/activate && make test` (timed out after 120s; in progress around 51% complete)

## Decisions / Blockers
- Defaulted the first FAQ item to open in markup to ensure content is reachable without JS.
- No blockers.

## Doc Updates
- None.
