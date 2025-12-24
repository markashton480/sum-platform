THEME-036 Followup

Summary of changes:
- Aligned Theme A editorial block templates to the shared section rhythm and container widths.
- Confirmed semantic markup and alignment behaviors with updated theme tests.
- Added a Theme A editorial block contract test for required overrides.
- Regenerated the Theme A build fingerprint after template updates.

Files modified/created:
- themes/theme_a/templates/sum_core/blocks/content_editorial_header.html
- themes/theme_a/templates/sum_core/blocks/content_richtext.html
- themes/theme_a/templates/sum_core/blocks/content_quote.html
- themes/theme_a/templates/sum_core/blocks/content_image.html
- themes/theme_a/templates/sum_core/blocks/content_buttons.html
- tests/themes/test_theme_a_editorial_header_rendering.py
- tests/themes/test_theme_a_richtext_content_rendering.py
- tests/themes/test_theme_a_quote_rendering.py
- tests/themes/test_theme_a_image_block_rendering.py
- tests/themes/test_theme_a_buttons_social_proof_rendering.py
- tests/themes/test_theme_a_block_contracts.py
- themes/theme_a/static/theme_a/css/.build_fingerprint
- THEME-036.md
- THEME-036_followup.md

Test results:
- `./.venv/bin/python -m pytest tests/themes/ -v`
- `make test`

Decisions made / blockers hit:
- Standardized editorial blocks on the Theme A `.section` layout primitive for consistent rhythm.
- No blockers.

Doc updates made:
- None.
