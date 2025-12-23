THEME-038 Followup

Summary of changes:
- Added TeamMemberBlock + TeamMemberItemBlock, registered in the page stream.
- Added Theme A and core templates for a responsive team grid with Wagtail renditions.
- Added Theme A contract coverage and documented the new block in the reference.

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
- `./.venv/bin/python -m pytest tests/themes/test_theme_a_block_contracts.py -k team` (failed: 0 tests selected)
- `./.venv/bin/python -m pytest tests/themes/test_theme_a_team_members_rendering.py -k team`
- `./.venv/bin/python -m pytest tests/themes/` (failed: Theme A build fingerprint stale)
- `./.venv/bin/python themes/theme_a/build_fingerprint.py`
- `./.venv/bin/python -m pytest tests/themes/`

Decisions made / blockers hit:
- Regenerated Theme A build fingerprint after adding the new template to satisfy guardrail checks.
- No blockers.

Doc updates made:
- docs/dev/blocks-reference.md
