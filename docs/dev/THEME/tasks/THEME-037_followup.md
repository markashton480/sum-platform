# THEME-037 Followup

Summary of changes:
- Added PageHeaderBlock to sum_core and registered it in PageStreamBlock.
- Added core fallback and Theme A page header templates with accessible breadcrumbs.
- Added Theme A rendering coverage and updated block reference docs.

Files modified/created:
- core/sum_core/blocks/content.py
- core/sum_core/blocks/base.py
- core/sum_core/blocks/__init__.py
- core/sum_core/templates/sum_core/blocks/page_header.html
- themes/theme_a/templates/sum_core/blocks/page_header.html
- tests/themes/test_theme_a_block_contracts.py
- tests/themes/test_theme_a_page_header_rendering.py
- docs/dev/blocks-reference.md
- docs/dev/THEME/tasks/THEME-037.md
- docs/dev/THEME/tasks/THEME-037_followup.md

Test results:
- `./.venv/bin/python -m pytest tests/themes/test_theme_a_block_contracts.py -k page_header`
- `./.venv/bin/python -m pytest tests/themes/test_theme_a_page_header_rendering.py -vv`
- `./.venv/bin/python -m pytest tests/themes/`

Decisions made / blockers hit:
- Rebuilt Theme A CSS and regenerated the fingerprint to keep guardrails in sync with the new template.

Doc updates made:
- `docs/dev/blocks-reference.md`
