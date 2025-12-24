# Work Report — THEME-012: HeroImageBlock Rewrite

Theme A's `HeroImageBlock` template has been rewritten to strictly match the Task 5 wireframe requirements. A new rendering test suite was added to verify the visual markers and logic without requiring manual setup for every iteration.

## Changes

### Template: `themes/theme_a/templates/sum_core/blocks/hero_image.html`

- Removed the old `if self.layout == 'full'` branch in favour of a single, strict wireframe implementation.
- Implemented full-screen metrics: `h-screen min-h-[700px]`.
- Implemented background image with parallax-ready classes: `h-[120%] -translate-y-10 object-cover`.
- Map `overlay_opacity` to semantic Tailwind classes:
  - `none` -> `bg-black/0`
  - `light` -> `bg-black/30`
  - `medium` -> `bg-black/60`
  - `strong` -> `bg-black/75`
- Implemented centered content wrapper with specific spacing and typography.
- Standardized CTA logic:
  - Supports up to 2 CTAs.
  - Automatically styles CTA 1 as Primary (solid `bg-sage-terra`) and CTA 2 as Secondary (bordered `border-sage-linen/30`).
  - Respects `style` override if present (`primary` vs `secondary`/`outline`).
  - Supports `open_in_new_tab` safely.
- Added Floating Card support (render only if both label and value are present).

### Tests: `tests/themes/test_theme_a_hero_rendering.py` [NEW]

- Added `test_theme_a_hero_markers` to verify presence of specific Tailwind classes (`h-screen`, `bg-sage-terra`, etc.).
- Added `test_theme_a_hero_overlay_mapping` (parameterized) to ensure all opacity options map correctly.
- Added `test_theme_a_floating_card_logic` to verify conditional rendering.

## Verification Results

### Automated Tests

- **Rendering Tests**: `pytest tests/themes/test_theme_a_hero_rendering.py` passed (6 PASSED).
- **Full Suite**: `make test` passed (730 PASSED).

### Build Artifacts

- **CSS**: Rebuilt with `npm run build` in `themes/theme_a/tailwind`.
- **Fingerprint**: Regenerated via `themes/theme_a/build_fingerprint.py`.
- **New Hash**: `75ca25b6a271cf9586ae74b186eeea6158444b29f13387ef206ba6bb8811111a`

## Metadata

- **Task ID**: THEME-012
- **Module**: Theme A
- **Verification Date**: 2025-12-20
