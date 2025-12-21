# Theme A (Sage & Stone)

Premium theme for SUM Platform featuring reveal animations, mega menu, and elegant typography for home improvement trades.

## Quick Reference

- **Name**: Sage & Stone
- **Version**: 1.0.0
- **Tailwind**: v3.4.x (authoring only)

## File Structure

```
theme_a/
├── tailwind/              # Tailwind build toolchain (maintainers only)
│   ├── package.json
│   ├── npm-shrinkwrap.json
│   ├── tailwind.config.js
│   └── postcss.config.js
├── theme.json             # Theme manifest
├── static/theme_a/
│   ├── css/
│   │   ├── input.css      # Tailwind source file (DO NOT EDIT main.css directly)
│   │   └── main.css       # GENERATED - compiled Tailwind output
│   └── js/
│       └── main.js        # Theme A JavaScript
└── templates/             # Theme templates (theme/* plus sum_core/* overrides)
```

## For Site Operators

**You don't need Node or npm to run a site using Theme A.**

The compiled CSS (`main.css`) is committed to the repository and ships with the theme. Simply run your Django/Wagtail site as normal.

## For Theme Maintainers

When modifying Theme A styles or templates that use new Tailwind classes:

### One-Time Setup

```bash
cd themes/theme_a/tailwind
npm install
```

### Build CSS

```bash
# Production build (minified)
npm run build

# Development (unminified, for debugging)
npm run dev

# Watch mode (auto-rebuild on file changes)
npm run watch
```

### Commit Changes

Always commit both source and compiled files:

```bash
git add static/theme_a/css/input.css static/theme_a/css/main.css
git commit -m "feature:theme_a - update styles"
```

### Tailwind Content Sources

Theme A scans both local templates and the Sage & Stone compiled reference HTML
to keep class coverage aligned with the prototype:

- `themes/theme_a/templates/**/*.html`
- `docs/dev/design/wireframes/sage-and-stone/compiled/*.html`

This is intentional: scanning all compiled reference pages preserves the full
class universe for template copy/paste. If you add new reference HTML files,
ensure the glob still matches them.

### Breakpoints

- `ipad` (970px): matches the reference mid-size breakpoint.
- `desktop` (1200px): reserved for the header/nav layout switch.

For general layout, prefer Tailwind defaults like `lg`/`xl` to avoid shifting
core grid behavior to 1200px.

## Branding Override System

Theme A uses CSS variables for colors, allowing client sites to override branding through SiteSettings without rebuilding CSS.

### CSS Variable Mapping

| Variable             | Default     | Purpose                        |
| -------------------- | ----------- | ------------------------------ |
| `--color-sage-black` | 26 47 35    | Primary text (#1A2F23)         |
| `--color-sage-linen` | 247 245 241 | Background (#F7F5F1)           |
| `--color-sage-oat`   | 227 222 212 | Secondary background (#E3DED4) |
| `--color-sage-moss`  | 85 111 97   | Secondary accent (#556F61)     |
| `--color-sage-terra` | 160 86 59   | Primary accent (#A0563B)       |
| `--color-sage-stone` | 143 141 136 | Neutral (#8F8D88)              |

### How It Works

Colors in Tailwind config use the format:

```js
'sage-terra': 'rgb(var(--color-sage-terra, 160 86 59) / <alpha-value>)'
```

This means:

1. Default values are embedded (160 86 59)
2. CSS variables can override at runtime
3. Tailwind opacity modifiers work (e.g., `bg-sage-terra/50`)

## Custom Components

Theme A includes these custom CSS components beyond Tailwind utilities:

- **Reveal Animations**: `.reveal`, `.reveal.active`, `.reveal.delay-*`
- **Mega Menu**: `.mega-panel`, `.mega-panel[data-open="true"]`
- **Banner Grid**: `.banner-grid-wrapper`, `.banner-inner`
- **Accordion**: `.accordion-grid-wrapper`, `.accordion-inner`
- **Mobile Menu**: `.menu-level`

## Button System

Use the shared button classes instead of per-template utility stacks:

- **Primary**: `btn btn-primary`
- **Secondary (light surface)**: `btn btn-outline`
- **Secondary (dark/hero/header)**: `btn btn-outline-inverse`
- **Header sizing**: `btn-header` and `btn-header--compact`
- **Icon treatment**: add an SVG with `btn__icon` inside the button

This keeps CTAs consistent across the header, hero, and content blocks.

## Reveal Behavior

Reveal animations are progressive enhancement: `.reveal` content is visible by
default, and Theme A JS adds `reveal-ready` to `<html>` to enable the hide-then-
animate behavior when JS is available.

## Named Group Variants

Theme A uses Tailwind named groups for header state styling:

- Wrapper: `group/header`
- Variants: `group-[.scrolled]/header:*`

Keep this pattern consistent to avoid drift in compiled CSS output.

## Core Shell Notes

- **Header**: CTA uses the shared button system (`btn-outline-inverse` plus `btn-header` sizing).
- **Footer**: 4-column grid layout and `text-sage-footer-*` tokens are used to match the reference.

## Technical Notes

### Why Tailwind v3.x?

Tailwind v4 has a different architecture that doesn't support the CSS variable pattern we use for runtime branding. We use v3.4.x for full compatibility.

### Why Shrinkwrap?

We use `npm-shrinkwrap.json` instead of `package-lock.json` because shrinkwrap is published with the package and ensures reproducible builds across all environments.

---

**Theme Toolchain v1 Contract** | M6-A-001 | SUM v0.6
