THEME-042 Followup

Summary of changes:
- Added ServiceDetailBlock with highlights, CTA, and layout controls, registered on PageStreamBlock.
- Implemented core and Theme A templates for the service detail section with image/no-image variants.
- Updated theme contract/doc references and added Theme A render coverage; regenerated the Theme A CSS build fingerprint.

Files modified/created:
- core/sum_core/blocks/services.py
- core/sum_core/blocks/base.py
- core/sum_core/blocks/__init__.py
- core/sum_core/templates/sum_core/blocks/service_detail.html
- themes/theme_a/templates/sum_core/blocks/service_detail.html
- tests/themes/test_theme_a_service_detail_rendering.py
- tests/themes/test_theme_block_contracts.py
- docs/dev/blocks-reference.md
- themes/theme_a/static/theme_a/css/main.css
- themes/theme_a/static/theme_a/css/.build_fingerprint
- THEME-042.md
- THEME-042_followup.md

Test results:
- `./.venv/bin/python -m pytest tests/themes/ -v`
- `PATH="/home/codex_b/workspaces/sum-platform/.venv/bin:$PATH" make test`

Decisions made / blockers hit:
- Regenerated Theme A CSS and fingerprint after adding the new block template override; no outstanding blockers.

Doc updates made:
- Added ServiceDetailBlock entry to docs/dev/blocks-reference.md.
