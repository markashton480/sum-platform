# Showroom management command follow-up (SQ-002)

Date: 2025-12-20

## Summary
We fixed the StreamField “double conversion” bug in the `seed_showroom` management command (SQ-002) and then validated the command end-to-end inside the showroom client project. While validating, two additional real runtime issues were discovered (branding + navigation seeding) and fixed so `seed_showroom --clear` completes successfully.

## Root cause (SQ-002)
The Kitchen Sink builder combined already-converted StreamField values (iterating a `StreamValue` yields `StreamChild` objects) and then called `StreamBlock.to_python()` again.

This caused:
- `TypeError: cannot unpack non-iterable StreamChild object`

## Fix implemented (SQ-002)
In `_build_kitchen_sink_stream()` we now merge *raw* stream data (via `get_prep_value()` on the returned `StreamValue`) and call `to_python()` exactly once.

Updated in all copies:
- [boilerplate/project_name/home/management/commands/seed_showroom.py](../../../boilerplate/project_name/home/management/commands/seed_showroom.py)
- [cli/sum_cli/boilerplate/project_name/home/management/commands/seed_showroom.py](../../../cli/sum_cli/boilerplate/project_name/home/management/commands/seed_showroom.py)
- [clients/showroom/showroom/home/management/commands/seed_showroom.py](../../../clients/showroom/showroom/home/management/commands/seed_showroom.py)

## Additional runtime fixes found during validation

### 1) Branding seeding field mismatch
`sum_core.branding.models.SiteSettings` uses `company_name`, `header_logo`, `footer_logo`, `favicon`, etc. The command previously assigned non-existent fields and attempted to assign integer IDs into FK fields.

Fix:
- Use correct fields and set FK IDs via `header_logo_id`, `footer_logo_id`, `favicon_id`.

### 2) Navigation seeding API mismatch
`sum_core.navigation.models.HeaderNavigation` and `FooterNavigation` are StreamField-based (`menu_items`, `header_cta_link`, `link_sections`, etc.). The command previously used an older relational API (`header.items.create(...)`, `sub_items`, `footer.items`).

Fix:
- Seed navigation via raw StreamField JSON structures that match `MenuItemBlock` and `FooterLinkSectionBlock`.
- Added a “Home” menu item to the header.
- Kept `FooterNavigation.social_*` blank to demonstrate the intended effective-settings fallback to branding.

## Verification

### CLI scaffolding test
Updated the CLI init test to assert the generated `seed_showroom.py` includes:
- SQ-002 regression safety (`get_prep_value()` merge; no double-`to_python()` pattern).
- StreamField-based navigation seeding (`header.menu_items`, `footer.link_sections`) and no legacy `.items`/`sub_items` usage.
- Correct branding field usage (`company_name`, `*_logo_id`, `favicon_id`).

Test touched:
- [cli/tests/test_theme_init.py](../../../cli/tests/test_theme_init.py)

### End-to-end run
Ran the command successfully in the showroom client:
- `clients/showroom/manage.py seed_showroom --clear`

Observed outcome:
- Seeded pages created and published.
- Command completes with `✓ Showroom seeded`.

## Documentation updates
Updated showroom docs to reflect the StreamField-based navigation seeding and to document the SQ-002 StreamField gotcha/fix:
- [docs/dev/SHOWROOM.md](../SHOWROOM.md)

## Notes / follow-ups
- The workspace test runner tool didn’t discover pytest tests via the `runTests` tool for the `cli/tests` path, but running pytest directly works. If we want, we can later investigate the `runTests` integration configuration.
- There’s a recurring coverage DB warning (`.coverage` SQLite schema mismatch) during test runs; unrelated to this change set.
