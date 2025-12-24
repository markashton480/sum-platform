# THEME-035 Followup

Summary of changes:
- Replaced Theme A ProcessStepsBlock template with a two-column layout and sticky header.
- Added Theme A tests to enforce process_steps template resolution and rendering.
- Updated process/FAQ rendering expectations for the new layout.
- Rebuilt Theme A CSS artifacts and refreshed the build fingerprint.

Files modified/created:
- themes/theme_a/templates/sum_core/blocks/process_steps.html
- themes/theme_a/static/theme_a/css/main.css
- themes/theme_a/static/theme_a/css/.build_fingerprint
- tests/themes/test_theme_a_process_steps_rendering.py
- tests/themes/test_theme_a_rendering.py
- tests/themes/test_theme_block_contracts.py
- tests/templates/test_process_faq_rendering.py
- docs/dev/THEME/tasks/THEME-035.md
- docs/dev/THEME/tasks/THEME-035_followup.md

Test results:
- Not run (not requested).

Decisions made / blockers hit:
- Rebuilt Theme A CSS artifacts after the template change because guardrail tests require a fresh fingerprint.

Doc updates made:
- None.
