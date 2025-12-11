---
description: How to implement a design using the SUM Platform design token system
---

# Design Implementation Workflow

Use this workflow when given a reference design (HTML file, Figma, screenshot) to implement as a Wagtail block or page template.

## Prerequisites

Before starting, confirm you have read:

- `core/sum_core/static/sum_core/css/tokens.css` (all available tokens)
- `core/sum_core/static/sum_core/css/typography.css` (typography classes)
- `docs/dev/design/css-architecture-and-tokens.md` (architecture overview)

---

## Step 1: Identify Typography Roles

For every text element in the design, assign a role from this table:

| Design Element             | Role        | CSS Class(es)                     |
| -------------------------- | ----------- | --------------------------------- |
| Hero headline (largest)    | Display     | `.heading-display`                |
| Page/section title (large) | Heading XL  | `.heading-xl`                     |
| Section heading (standard) | Heading LG  | `.heading-lg`                     |
| Card/item title            | Heading MD  | `.heading-md`                     |
| Minor heading              | Heading SM  | `.heading-sm`                     |
| Lead paragraph / intro     | Text Large  | `.text-lg`                        |
| Body copy                  | Body        | `.text-body`                      |
| Small text / captions      | Small       | `.text-sm`                        |
| Meta / timestamps          | Extra Small | `.text-xs`                        |
| Eyebrow / kicker label     | Eyebrow     | `.section__eyebrow` or `.eyebrow` |
| Secondary / muted text     | Modifier    | Add `.text-muted`                 |

**DO NOT** create custom font-size values. Pick the closest role.

---

## Step 2: Use Section Structure

Wrap blocks in the standard section pattern:

```html
<section class="section [modifiers]">
  <div class="container">
    <header class="section__header">
      <span class="section__eyebrow">Label</span>
      <div class="section__heading">{{ heading|richtext }}</div>
      <p class="section__intro">{{ intro }}</p>
    </header>

    <!-- Content here -->
  </div>
</section>
```

**Section modifiers:**

- `.section--dark` — dark background with inverted text
- `.section--muted` — subtle background tint

---

## Step 3: Use Token Values Only

**Spacing:** Always use `var(--space-*)` tokens:

- `--space-1` (4px) through `--space-24` (96px)

**Colors:** Always use HSL token references:

- `hsla(var(--primary), 1)` — brand primary
- `hsla(var(--text-main), 1)` — main text
- `hsla(var(--text-muted), 1)` — secondary text
- `hsla(var(--accent-pop), 1)` — accent/highlight
- `hsla(var(--surface-tint), 1)` — light surface
- `hsla(var(--color-success), 1)` — success green
- `hsla(var(--color-error), 1)` — error red

**Radii:** Use `var(--radius-*)`:

- `--radius-sm` (4px) through `--radius-full` (pill)

**Shadows:** Use `var(--shadow-*)`:

- `--shadow-sm`, `--shadow-md`, `--shadow-lg`, `--shadow-xl`

---

## Step 4: Write Component CSS

Create or update `components.<block>.css`:

```css
/* ==========================================================================
   Name: Component Name
   Path: core/sum_core/static/sum_core/css/components.<block>.css
   Purpose: [description]
   Family: SUM Platform Design System – Components
   Dependencies: tokens.css, typography.css
   ========================================================================== */

.block-name__element {
  /* ✅ Correct: use tokens */
  padding: var(--space-6);
  background: hsla(var(--surface-tint), 1);
  border-radius: var(--radius-lg);

  /* ❌ NEVER do this: */
  /* padding: 24px; */
  /* background: #f5f5f5; */
  /* font-size: 1.2rem; */
}
```

---

## Step 5: Pre-Flight Checklist

Before considering work complete, verify:

**Templates:**

- [ ] No inline `style=""` attributes
- [ ] Uses `.section` + `.container` structure
- [ ] Headings use typography classes, not custom sizes
- [ ] Body text uses `.text-body` or `.text-lg`

**CSS:**

- [ ] No hex colors (`#abc123`)
- [ ] No `font-family:` declarations
- [ ] No `font-size:` with raw values
- [ ] All spacing uses `var(--space-*)`
- [ ] All colors use `hsla(var(--*), 1)` format
- [ ] File has standard header comment

---

## Forbidden Patterns

**DO NOT:**

- Use `font-family:` in component CSS (fonts come from tokens/branding)
- Use `font-size: 1.2rem` or any raw size (use typography classes)
- Use `#ff0000` or any hex color (use token references)
- Use `margin: 23px` (use spacing scale)
- Add `style=""` inline attributes in templates
- Create new tokens without updating `tokens.css`

**IF you need a value that doesn't exist:**

1. Check if a close-enough token exists
2. If truly new, add it to `tokens.css` first
3. Document why in a comment
