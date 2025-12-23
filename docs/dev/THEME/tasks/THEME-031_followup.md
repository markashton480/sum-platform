# THEME-031 Followup

Summary of changes:
- Replaced Theme A ProcessStepsBlock template with Sage and Stone timeline markup.
- Added Theme A rendering test for ProcessStepsBlock template origin and key markers.

Files modified/created:
- themes/theme_a/templates/sum_core/blocks/process_steps.html
- tests/themes/test_theme_a_process_steps_rendering.py
- tests/templates/test_process_faq_rendering.py
- themes/theme_a/static/theme_a/css/main.css
- themes/theme_a/static/theme_a/css/.build_fingerprint
- docs/dev/THEME/tasks/THEME-031_followup.md

Test results:
- `./.venv/bin/python -m pytest tests/themes/ -v`
- `PATH="/home/codex_b/workspaces/sum-platform/.venv/bin:$PATH" make test`

Decisions made / blockers hit:
- Applied compiled timeline layout and highlighted the third step to mirror the reference example.
- Rebuilt Theme A CSS + fingerprint to satisfy guardrail checks after template change.

Doc updates made:
- None.
