## THEME-014 Work Report

### Summary
- Synced Theme A Tailwind content scanning with the Sage & Stone compiled reference HTML and added the missing `ipad`/`desktop` breakpoints for parity.
- Consolidated bespoke CSS into Tailwind layers (base/components/utilities) and removed duplicate, out-of-layer rules.
- Updated reveal utilities to match reference behavior and rebuilt compiled CSS + fingerprint.
- Added guardrail tests for CSS discovery, sentinel utilities/palette output, and reference HTML inclusion.
- Documented content sources + named group variant pattern in Theme A README.

### Changes Implemented
- `themes/theme_a/tailwind/tailwind.config.js`: content glob now includes `docs/dev/design/wireframes/sage-and-stone/compiled/*.html`; added `ipad`/`desktop` screens to mirror the prototype.
- `themes/theme_a/static/theme_a/css/input.css`: moved bespoke CSS into `@layer base/components/utilities`, removed duplicated blocks, and aligned reveal utilities to the reference prototype.
- `themes/theme_a/static/theme_a/css/main.css`: rebuilt to include the expanded class universe and updated utilities.
- `themes/theme_a/static/theme_a/css/.build_fingerprint`: refreshed after Tailwind inputs changed.
- `tests/themes/test_theme_a_css_contract.py`: new tests for staticfiles discovery, sentinel selectors, and tailwind content globs.
- `themes/theme_a/README.md`: documented reference HTML content scanning and named group variant usage.

### Verification Notes
- Base template still injects branding variables after theme CSS and serves `theme_a/css/main.css` (Theme A remains wired correctly).
- Tailwind output now includes `ipad:` and `desktop:` variants plus named group selectors (`group/header` + `group-[.scrolled]/header:*`).

### Red Flags / Concerns
- Reveal behavior now matches the reference (hidden until `.active`), which means no-JS environments will keep reveal elements hidden. If that is undesirable, we should decide on a no-JS fallback strategy.
- `desktop` breakpoint changed from 1024px to 1200px (reference parity). This shifts layout behavior between 1024–1199px and should be validated against expected navigation behavior.

### Clarifications Needed
- Should the `document.documentElement.classList.add('reveal-ready')` line in `themes/theme_a/static/theme_a/js/main.js` be removed since the CSS no longer uses `.reveal-ready`?
- Is it acceptable that the Tailwind content glob includes **all** compiled reference HTML (`compiled/*.html`) rather than only `index.html`?

### Tests Run
- `npm run build` (Theme A Tailwind build)
- `python themes/theme_a/build_fingerprint.py`

### Follow-ups / Suggestions
- Run `make test` to ensure the new guardrail tests pass across the full suite.
- If no-JS fallback is required, add a documented strategy (e.g., a `no-js` class on `<html>` to keep `.reveal` visible).
