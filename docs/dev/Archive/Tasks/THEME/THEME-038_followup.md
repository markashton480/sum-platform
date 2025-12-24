THEME-038 Followup

Summary of changes:
- Added TeamMemberBlock + TeamMemberItemBlock, registered in the page stream.
- Added Theme A and core templates for a responsive team grid with Wagtail renditions.
- Added alt text + help text guidance and documented the new block in the reference.

Files modified/created:
- core/sum_core/blocks/content.py
- core/sum_core/blocks/base.py
- core/sum_core/templates/sum_core/blocks/team_members.html
- themes/theme_a/templates/sum_core/blocks/team_members.html
- themes/theme_a/static/theme_a/css/.build_fingerprint
- tests/themes/test_theme_a_block_contracts.py
- tests/themes/test_theme_a_team_members_rendering.py
- docs/dev/blocks-reference.md
- THEME-038.md
- THEME-038_followup.md

Test results:
- `./.venv/bin/python -m pytest tests/themes/test_theme_a_team_members_rendering.py`
- `./.venv/bin/python -m pytest tests/themes/test_theme_a_block_contracts.py`
- `./.venv/bin/python themes/theme_a/build_fingerprint.py`

Decisions made / blockers hit:
- Regenerated Theme A build fingerprint after template updates to satisfy guardrail checks.
- No blockers.

Doc updates made:
- docs/dev/blocks-reference.md
