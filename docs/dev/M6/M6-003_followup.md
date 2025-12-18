# M6-003: Theme A (Sage & Stone) — Work Report

**Completed:** 2025-12-17  
**Status:** ✅ Complete (pending manual verification)

---

## Summary

Implemented Theme A as the first production-ready theme for SUM Platform by translating the compiled Sage & Stone HTML artifacts into a Wagtail/Django theme structure. All 684 tests pass.

---

## Files Created

### Static Assets

| File                                                       | Lines | Purpose                                                                                  |
| ---------------------------------------------------------- | ----- | ---------------------------------------------------------------------------------------- |
| `core/sum_core/themes/theme_a/static/theme_a/css/main.css` | 230   | Reveal animations, mega menu panels, accordion physics, focus-visible, reduced-motion    |
| `core/sum_core/themes/theme_a/static/theme_a/js/main.js`   | 340   | Header scroll, mobile menu, mega menu intent, reveal animations, parallax, FAQ accordion |

### Tests

| File                                     | Tests | Purpose                                                      |
| ---------------------------------------- | ----- | ------------------------------------------------------------ |
| `tests/themes/test_theme_a_rendering.py` | 12    | HomePage DOM hooks, CSS/JS loading, skip link, scroll-smooth |

---

## Files Modified

### Templates

| File                                                                  | Changes                                                                                                         |
| --------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| `core/sum_core/themes/theme_a/templates/theme_a/base.html`            | Added Google Fonts preconnect, skip link for a11y, scroll-smooth class, theme_a JS loading                      |
| `core/sum_core/themes/theme_a/templates/theme_a/includes/header.html` | Complete rewrite with Sage & Stone structure, mega menu IDs, mobile menu with slide transitions, banner support |

### Theme Manifest

| File                                      | Changes                                                  |
| ----------------------------------------- | -------------------------------------------------------- |
| `core/sum_core/themes/theme_a/theme.json` | Updated name from "Theme A (Skeleton)" to "Sage & Stone" |

### Test Project Configuration

| File                                                  | Changes                                                                              |
| ----------------------------------------------------- | ------------------------------------------------------------------------------------ |
| `core/sum_core/test_project/test_project/settings.py` | Added `_THEME_A_TEMPLATES` to TEMPLATES DIRS, `_THEME_A_STATIC` to STATICFILES_DIRS  |
| `core/sum_core/test_project/home/models.py`           | Changed HomePage template from `sum_core/home_page.html` to `theme_a/home_page.html` |

### Test Assertions

| File                                   | Changes                                                                    |
| -------------------------------------- | -------------------------------------------------------------------------- |
| `tests/themes/test_theme_discovery.py` | Updated assertion to expect "Sage & Stone" instead of "Theme A (Skeleton)" |
| `cli/tests/test_themes_command.py`     | Updated assertion to expect "Sage & Stone" in CLI output                   |

---

## DOM Hooks Implemented

The following IDs are required by `main.js` for JavaScript interactions:

| ID                      | Element    | Purpose                                                |
| ----------------------- | ---------- | ------------------------------------------------------ |
| `main-header`           | `<header>` | Header scroll effect (adds `scrolled` class on scroll) |
| `mobile-menu`           | `<div>`    | Mobile navigation overlay                              |
| `mobile-menu-btn`       | `<button>` | Hamburger menu toggle                                  |
| `mobile-menu-close-btn` | `<button>` | Close button inside mobile menu                        |
| `mobile-menu-slider`    | `<div>`    | Multi-level menu container                             |
| `kitchens-nav`          | `<div>`    | Mega menu wrapper (first nav item with children)       |
| `kitchens-trigger`      | `<button>` | Mega menu trigger button                               |
| `mega-menu-kitchens`    | `<div>`    | Mega menu panel                                        |
| `banner-wrapper`        | `<div>`    | Dismissible alert banner                               |
| `banner-close-btn`      | `<button>` | Banner close button                                    |

---

## CSS Features

| Feature           | Implementation                                                               |
| ----------------- | ---------------------------------------------------------------------------- |
| Reveal animations | `.reveal` class with IntersectionObserver, `.reveal.active` state            |
| Mega menu         | `.mega-panel` with `[data-open="true"]` state, opacity/transform transitions |
| Banner animation  | `.banner-grid-wrapper` with `grid-template-rows` transition                  |
| Accordion         | `.accordion-grid-wrapper` with `grid-template-rows: 0fr/1fr`                 |
| Reduced motion    | `@media (prefers-reduced-motion: reduce)` disables animations                |
| Focus indicators  | `:focus-visible` with `outline: 2px solid #A0563B`                           |
| Form validation   | `[aria-invalid="true"]` styling                                              |

---

## JavaScript Features

| Feature           | Implementation                                             |
| ----------------- | ---------------------------------------------------------- |
| Scroll lock       | `lockScroll()`/`unlockScroll()` for modals and menus       |
| Header scroll     | Adds/removes classes at 10px scroll threshold              |
| Mobile menu       | Multi-level sliding panels with CSS variable `--menu-x`    |
| Mega menu         | Hover intent with delay, keyboard support, escape handling |
| Reveal animations | IntersectionObserver with 0.1 threshold                    |
| Parallax          | Hero image translateY based on scroll position             |
| FAQ accordion     | Grid-based open/close with `toggleAccordion(id)`           |

---

## Test Results

```
684 passed, 45 warnings in 209.80s
```

New tests added:

- `TestThemeAHomePage` (9 tests) — DOM hooks, CSS/JS loading, accessibility
- `TestThemeAStandardPage` (2 tests) — Rendering verification
- `TestThemeAMegaMenu` (1 test) — Mobile menu presence

---

## Manual Verification Checklist

Run the dev server and verify in browser:

```bash
cd core/sum_core/test_project
python manage.py runserver
```

- [ ] Header becomes sticky with light background on scroll
- [ ] Mobile menu opens/closes with hamburger button (resize to mobile width)
- [ ] Mega menu appears on hover over nav items with children (if configured)
- [ ] Reveal animations fade in content on scroll (add `.reveal` class to elements)
- [ ] Skip link appears on Tab focus

---

## Architecture Notes

### Copy-into-Client Model

Theme A templates and static files are **source-of-truth** in `core/sum_core/themes/theme_a/`. The `sum init` command copies these to client projects at `theme/active/`.

For testing, the test_project simulates client configuration by adding theme paths to TEMPLATES and STATICFILES_DIRS.

### Template Resolution

- HomePage uses `template = "theme_a/home_page.html"` → extends `theme_a/base.html`
- StandardPage uses `template = "sum_core/standard_page.html"` → uses core templates
- Client projects override via TEMPLATES DIRS priority

### Future Work

1. **Footer styling** — Footer uses existing sum_core structure; could adopt Sage & Stone styling
2. **ServicePage/ServiceIndexPage** — Need theme_a templates for full coverage
3. **Reveal classes** — Page templates could auto-add `.reveal` to sections
4. **Blog templates** — Scaffolding exists but not fully styled

---

## Related Documents

- [M6-003.md](./M6-003.md) — Original task specification
- [THEME-ARCHITECTURE-SPECv1.md](../design/THEME-ARCHITECTURE-SPECv1.md) — Theme system architecture
- [Compiled artifacts](../design/wireframes/sage-and-stone/compiled/) — Source HTML/CSS/JS
