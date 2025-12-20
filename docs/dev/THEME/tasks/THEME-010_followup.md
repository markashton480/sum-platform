# THEME-010 — Branding contract bridge for Theme A

## Status: COMPLETE

## Inventory of Branding Output

The `{% branding_css %}` tag now emits the following CSS variables, ensuring full coverage for Theme A:

| Variable                                             | Description                  | Source                          |
| :--------------------------------------------------- | :--------------------------- | :------------------------------ |
| `--brand-h`, `--brand-s`, `--brand-l`                | Primary brand colour (HSL)   | `SiteSettings.primary_color`    |
| `--secondary-h`, `--secondary-s`, `--secondary-l`    | Secondary brand colour (HSL) | `SiteSettings.secondary_color`  |
| `--accent-h`, `--accent-s`, `--accent-l`             | Accent brand colour (HSL)    | `SiteSettings.accent_color`     |
| `--background-h`, `--background-s`, `--background-l` | Page background (HSL)        | `SiteSettings.background_color` |
| `--text-h`, `--text-s`, `--text-l`                   | Body text colour (HSL)       | `SiteSettings.text_color`       |
| `--surface-h`, `--surface-s`, `--surface-l`          | Surface/Card colour (HSL)    | `SiteSettings.surface_color`    |
| `--font-heading`                                     | Heading font family          | `SiteSettings.heading_font`     |
| `--font-body`                                        | Body font family             | `SiteSettings.body_font`        |

> **Note**: Hex variables (`--color-secondary-custom`) are still emitted for backward compatibility but Theme A now relies exclusively on the HSL components.

## Implementation Details

### 1. Tailwind Config (`themes/theme_a/tailwind/tailwind.config.js`)

- Mapped `primary` and `sage.terra` to `--brand-*` HSL vars.
- Mapped `secondary` and `sage.moss` to `--secondary-*` HSL vars.
- Mapped `accent` to `--accent-*` HSL vars.
- Mapped `sage.linen` (background defaults) to `--background-*` HSL vars (fallback #F7F5F1).
- Mapped `sage.oat` (surface defaults) to `--surface-*` HSL vars (fallback #E3DED4).
- Mapped `sage.black` (text defaults) to `--text-*` HSL vars (fallback #1A2F23).
- Mapped `fontFamily.display` and `body` to `--font-heading` and `--font-body`.

### 2. Input CSS (`themes/theme_a/static/theme_a/css/input.css`)

- Replaced hardcoded hex values in `@layer base` and Accessibility sections with `theme('colors.sage.*')` or `theme('colors.primary')` references.
- This ensures that if the Tailwind config changes (via branding vars), the generated CSS automatically reflects those changes.

### 3. Tests

- **`tests/branding/test_branding_css_output.py`**: Verifies that `branding_css` correctly emits all semantic HSL variables.
- **`tests/themes/test_theme_a_contract.py`**: Verifies `tailwind.config.js` references the branding variables and `input.css` does not contain prohibited hardcoded hex values.

### 4. Build & Fingerprint

- Rebuilt Theme A CSS (`npm run build`).
- Regenerated build fingerprint (`python themes/theme_a/build_fingerprint.py`).

## Verification

- `make test` passes (including new tests).
- Guardrails confirm fingerprint matches the new code.
