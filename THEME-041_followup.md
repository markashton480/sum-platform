THEME-041 Followup

Summary of changes:
- Added TimelineBlock and TimelineItemBlock to core, registered in PageStreamBlock, and provided core rendering template.
- Implemented Theme A override for timeline section with accessible layout and image support.
- Extended theme contract tests, added timeline rendering coverage, and documented the new block contract.
- Rebuilt Theme A CSS and fingerprint after template addition.

Files modified/created:
- core/sum_core/blocks/content.py
- core/sum_core/blocks/base.py
- core/sum_core/blocks/__init__.py
- core/sum_core/templates/sum_core/blocks/timeline.html
- themes/theme_a/templates/sum_core/blocks/timeline.html
- themes/theme_a/static/theme_a/css/main.css
- themes/theme_a/static/theme_a/css/.build_fingerprint
- tests/themes/test_theme_block_contracts.py
- tests/themes/test_theme_a_block_contracts.py
- tests/themes/test_theme_a_timeline_rendering.py
- docs/dev/blocks-reference.md
- THEME-041.md
- THEME-041_followup.md

Test results:
- ./.venv/bin/python -m pytest tests/themes/ -v
- make test

Decisions made / blockers hit:
- Added wagtailimages_tags to timeline templates to support the image tag.
- Regenerated Theme A CSS/fingerprint to satisfy guardrail tests after introducing the new template.

Doc updates made:
- Added TimelineBlock contract details to docs/dev/blocks-reference.md.
