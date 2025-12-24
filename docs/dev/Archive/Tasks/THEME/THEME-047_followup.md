THEME-047 Followup

Summary of changes:
- Added Terms and Privacy StandardPages to `seed_showroom`, including legal-styled content streams and footer navigation links.
- Synced CLI boilerplate so generated projects seed the same legal pages and updated footer sections.
- Updated showroom docs to list the new legal pages and their content/navigation coverage.
- Added regression tests covering seed command idempotency, HTTP 200s for `/terms/` and `/privacy/`, and footer legal links.

Files modified/created:
- boilerplate/project_name/home/management/commands/seed_showroom.py
- cli/sum_cli/boilerplate/project_name/home/management/commands/seed_showroom.py
- cli/sum_cli/boilerplate/project_name/home/management/commands/populate_demo_content.py
- cli/sum_cli/boilerplate/project_name/home/models.py
- cli/sum_cli/boilerplate/project_name/settings/base.py
- docs/dev/SHOWROOM.md
- tests/test_seed_showroom_command.py
- THEME-047_followup.md

Test results:
- `./.venv/bin/python -m pytest tests/ -v`
- `./.venv/bin/python -m pytest tests/themes/ -v`

Decisions made / blockers hit:
- CLI boilerplate sync pulled in small upstream canonical deltas (Faker import simplification, minor guard tweaks); kept to maintain parity. No blockers remaining.
