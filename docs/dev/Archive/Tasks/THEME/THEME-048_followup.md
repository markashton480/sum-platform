THEME-048 Followup

Summary of changes:
- Added TableOfContentsBlock and LegalSectionBlock with registration on PageStreamBlock plus exports.
- Implemented core + Theme A templates for the legal TOC/sections with anchored IDs and theme styling.
- Updated showroom seeds (canonical, CLI, client copy) and docs to cover the new legal blocks.
- Added Theme A contract/render tests for legal blocks and rebuilt Tailwind CSS + fingerprint.

Files modified/created:
- core/sum_core/blocks/content.py
- core/sum_core/blocks/base.py
- core/sum_core/blocks/__init__.py
- core/sum_core/templates/sum_core/blocks/table_of_contents.html
- core/sum_core/templates/sum_core/blocks/legal_section.html
- themes/theme_a/templates/sum_core/blocks/table_of_contents.html
- themes/theme_a/templates/sum_core/blocks/legal_section.html
- themes/theme_a/static/theme_a/css/main.css
- themes/theme_a/static/theme_a/css/.build_fingerprint
- clients/showroom/showroom/home/management/commands/seed_showroom.py
- boilerplate/project_name/home/management/commands/seed_showroom.py
- cli/sum_cli/boilerplate/project_name/home/management/commands/seed_showroom.py
- docs/dev/blocks-reference.md
- docs/dev/SHOWROOM.md
- tests/blocks/test_page_streamblock.py
- tests/themes/test_theme_a_block_contracts.py
- tests/themes/test_theme_a_legal_rendering.py
- THEME-048_followup.md

Test results:
- `./.venv/bin/python -m pytest tests/themes/ -v`
- `./.venv/bin/python -m pytest tests/ -v`

Decisions made / blockers hit:
- Rebuilt Theme A CSS and fingerprint after adding new templates to keep guardrails passing. No remaining blockers.
