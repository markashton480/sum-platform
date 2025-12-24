# THEME-006 Followup: Restore ManifestoBlock Contract

**Date:** December 20, 2025  
**Task:** [THEME-006](file:///home/mark/workspaces/sum-platform/docs/dev/THEME/tasks/THEME-006.md)  
**Status:** Complete

## Changes Implemented

### 1. ManifestoBlock Definition

Updated `core/sum_core/blocks/content.py` to match the strict contract:

- **Heading**: Required, RichText (italic/bold).
- **Body**: Required, RichText.
- **Eyebrow**: Optional, CharBlock.
- **Quote**: Optional, TextBlock.
- **Removed**: `cta_label` and `cta_url`.

### 2. Templates

- **Theme A**: Updated `themes/theme_a/templates/sum_core/blocks/manifesto.html` to fully align with Tailwind wireframe specs (Sage & Stone rendering).
- **Core Fallback**: Updated `core/sum_core/templates/sum_core/blocks/manifesto.html` to remove CTA structure and match the new block schema.

### 3. Migrations

Created `sum_core_pages` migration `0008` to enforce the schema change (AlterField operations).

### 4. Tests

- Updated `tests/blocks/test_content_blocks.py` to enforce strict field presence/absence (asserting NO CTA fields).
- Added `tests/themes/test_theme_a_manifesto.py` to verify Theme A specific rendering (classes `bg-sage-linen`, `text-sage-terra`).

## Verification Results

### Automated Tests

- `pytest tests/blocks/test_content_blocks.py` → **PASS** (Schema valid)
- `pytest tests/themes/test_theme_a_manifesto.py` → **PASS** (Rendering valid)

## Troubleshooting

- **Template Syntax Error**: Encounted a `TemplateSyntaxError` on `themes/theme_a/templates/sum_core/blocks/manifesto.html` due to auto-formatter (djhtml) breaking Django tags across multiple lines weirdly.
- **Resolution**: Refactored the template to use standard indented block structure with single-line tags.

### Manual Verification Required

1. Run `make db-up` and `make migrate`.
2. Spin up the harness (`make run`).
3. Add a Manifesto block to a page.
4. Verify no CTA fields appear in form.
5. Verify rendering with Theme A active matches the design (centered, sage background).
