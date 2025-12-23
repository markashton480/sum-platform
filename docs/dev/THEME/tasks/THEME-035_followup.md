# THEME-035 Followup

Summary of changes:
- Replaced Theme A ProcessStepsBlock template with a two-column layout and sticky header.
- Added Theme A tests to enforce process_steps template resolution and rendering.
- Added a Theme A block contract check for process_steps template presence.

Files modified/created:
- themes/theme_a/templates/sum_core/blocks/process_steps.html
- tests/themes/test_theme_a_process_steps_rendering.py
- tests/themes/test_theme_a_rendering.py
- tests/themes/test_theme_block_contracts.py
- docs/dev/THEME/tasks/THEME-035.md
- docs/dev/THEME/tasks/THEME-035_followup.md

Test results:
- Not run (not requested).

Decisions made / blockers hit:
- Kept the update template-only to avoid regenerating Theme A CSS artifacts.

Doc updates made:
- None.
