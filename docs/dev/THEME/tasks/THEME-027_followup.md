# THEME-027 Follow-up

## Summary
- Added SocialProofQuoteBlock wiring in core with a semantic fallback template.
- Implemented Theme A override with logo + attribution handling and reveal hooks.
- Added Theme A rendering tests covering template origin and optional fields.

## Files Modified/Created
- core/sum_core/blocks/content.py
- core/sum_core/blocks/base.py
- core/sum_core/blocks/__init__.py
- core/sum_core/templates/sum_core/blocks/content_social_proof_quote.html
- themes/theme_a/templates/sum_core/blocks/content_social_proof_quote.html
- tests/themes/test_theme_a_social_proof_quote_rendering.py
- docs/dev/THEME/tasks/THEME-027_followup.md

## Tests
- `./.venv/bin/python -m pytest -q tests/themes/test_theme_a_social_proof_quote_rendering.py` (pass; warnings about Django URLField scheme)

## Decisions / Blockers
- Preflight fetch failed due to restricted network (unable to reach github.com).
- Stashed untracked `docs/dev/THEME/tasks/THEME-027.md` to allow preflight; stash preserved.

## Documentation Updates
- None.
