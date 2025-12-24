# THEME-050 Follow-up

## Summary of changes
- Added optional portfolio item categories and server-side filtering support.
- Rendered Theme A filter navigation when multiple categories exist.
- Updated showroom seed data, block docs, and Theme A tests for filters.

## Files modified/created
- core/sum_core/blocks/content.py
- themes/theme_a/templates/sum_core/blocks/portfolio.html
- boilerplate/project_name/home/management/commands/seed_showroom.py
- docs/dev/blocks-reference.md
- docs/dev/SHOWROOM.md
- tests/themes/test_theme_a_portfolio_rendering.py
- docs/dev/THEME/tasks/THEME-050_followup.md

## Test results
- `./.venv/bin/python -m pytest tests/themes/ -v`
- `./.venv/bin/python -m pytest tests/ -v`

## Decisions made / blockers
- Filtering is handled in the PortfolioBlock context to keep the template lean.

## Doc updates
- `docs/dev/blocks-reference.md`
- `docs/dev/SHOWROOM.md`
