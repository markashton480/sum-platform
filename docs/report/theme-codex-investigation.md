# Theme A Investigation Report (Codex)

Date: 2025-12-19

## Summary
Theme A is present and correctly wired in the theme system, but most blocks render with `.reveal` classes that default to `opacity: 0`. If the Theme A JS does not execute (static 404, JS error, or blocked scripts), the page collapses into “only background color blocks.” The system had no progressive enhancement fallback, so a missing JS file makes the UI look blank.

I implemented a progressive enhancement fix: content is visible by default and only hidden when Theme A JS explicitly activates reveal animations. This makes Theme A resilient even if JS fails. I rebuilt Theme A CSS + fingerprint and synced the updated assets into the two checked client themes.

## Investigation Notes
- Theme architecture is aligned with THEME-ARCHITECTURE-SPECv1 (copy into `theme/active/`, templates/static resolved from that directory).
- Theme A files exist in the new client install (`clients/test-project-2/theme/active/...`).
- `findstatic` confirms Theme A JS is discoverable:
  - `python manage.py findstatic theme_a/js/main.js` → `clients/test-project-2/theme/active/static/theme_a/js/main.js`
- Block templates in Theme A use `.reveal` extensively (e.g., `sum_core/blocks/hero_gradient.html`, `sum_core/blocks/service_cards.html`).
- Theme A CSS defines `.reveal { opacity: 0; }` and relies on JS to add `.active` via IntersectionObserver.
- If JS does not run, all reveal elements stay hidden, leaving only background containers visible. This matches the “only colour blocks” symptom.
- `input.css` had two separate reveal definitions; the later “SECTION 4: REVEAL ANIMATIONS” overrides earlier values.

## Root Cause
Theme A assumes JS always runs to reveal content. Any JS failure (missing static, error, blocked scripts) leaves `.reveal` elements hidden, so the page appears empty aside from background blocks. This is a stability issue in the theme, not in template discovery or Tailwind compilation.

## Additional Root Cause (Found After Page Source Review)
Theme A JS had a syntax error that stopped **all** Theme A JS from executing:

- `Uncaught SyntaxError: Unexpected token '}'` in `theme_a/js/main.js`
- The file contained a duplicated `})(); ... catch ... }` block at the end of the mega menu section.
- Result: no mobile menu, no reveal activation, and content stayed hidden.

## Fix Implemented (Progressive Enhancement)
- Default state: `.reveal` elements are visible.
- JS state: when Theme A JS loads, it adds a root class (`reveal-ready`) to enable reveal animation hiding and then activates visible elements.
- Result: if JS fails, content still renders (no animation). If JS works, animations still apply.

## Fix Implemented (JS Syntax Error)
- Removed the duplicate `})(); ... catch ... }` block in Theme A `main.js`.
- Re-synced the corrected JS into client theme copies.

## Files Updated
Core Theme A:
- `core/sum_core/themes/theme_a/static/theme_a/css/input.css`
- `core/sum_core/themes/theme_a/static/theme_a/js/main.js`
- `core/sum_core/themes/theme_a/static/theme_a/css/main.css` (rebuilt)
- `core/sum_core/themes/theme_a/static/theme_a/css/.build_fingerprint`

Synced to client theme copies:
- `clients/client-name/theme/active/static/theme_a/css/input.css`
- `clients/client-name/theme/active/static/theme_a/css/main.css`
- `clients/client-name/theme/active/static/theme_a/css/.build_fingerprint`
- `clients/client-name/theme/active/static/theme_a/js/main.js`
- `clients/test-project-2/theme/active/static/theme_a/css/input.css`
- `clients/test-project-2/theme/active/static/theme_a/css/main.css`
- `clients/test-project-2/theme/active/static/theme_a/css/.build_fingerprint`
- `clients/test-project-2/theme/active/static/theme_a/js/main.js`

## Verification Steps
1. Confirm static resolution:
   - `python manage.py findstatic theme_a/js/main.js`
   - `python manage.py findstatic theme_a/css/main.css`
2. Open a page and check in DevTools:
   - `document.documentElement.classList.contains('reveal-ready')` → `true` if Theme A JS loaded.
   - `document.querySelectorAll('.reveal.active').length` grows after scrolling.
3. Optional: simulate JS failure (block `/static/theme_a/js/main.js`) and confirm content still displays.

## If It Still Looks Blank
- Check network tab for 404/blocked `/static/theme_a/js/main.js`.
- Check console for JS errors before the reveal section.
- Confirm the page uses Theme A base template (look for `<!-- THEME: theme_a -->`).
- Confirm Tailwind CSS is loading (`theme_a/css/main.css` in HTML head).

## Follow-ups (if needed)
- Add a `sum check` validation step to assert Theme A JS + CSS are present in `theme/active/`.
- Consider adding a lightweight “theme health” panel in admin (template + static loaded check).
