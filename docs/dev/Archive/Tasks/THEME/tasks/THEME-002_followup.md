# THEME-002 Follow-up

## Summary
- Added optional PortfolioItem metadata fields (constraint, material, outcome) to support Theme A templates.
- Added `established_year` to SiteSettings and exposed it in the Wagtail admin panel.
- Documented the new fields and added focused tests plus a migration.

## Files changed
- `core/sum_core/blocks/content.py`
- `core/sum_core/branding/models.py`
- `core/sum_core/migrations/0007_sitesettings_established_year.py`
- `tests/blocks/test_content_blocks.py`
- `tests/branding/test_site_settings_model.py`
- `docs/dev/blocks-reference.md`
- `docs/dev/WIRING-INVENTORY.md`

## Notes
- Migration was generated via `core/sum_core/test_project/manage.py makemigrations sum_core` and emitted a warning about a bad DB connection; the migration file itself was created successfully.

## Testing
- Not run (not requested).
