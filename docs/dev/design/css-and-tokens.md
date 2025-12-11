## SUM CSS & Design System Guide

### 1. Goals

* **Single source of truth for design values** (tokens).
* **Consistent implementation** across all blocks (typography, spacing, layout).
* **Modular CSS** that’s easy to navigate and extend.
* **Branding-controlled**: changing fonts/colours in Wagtail SiteSettings updates the whole site.

---

### 2. CSS Architecture

All CSS lives under:

`core/sum_core/static/sum_core/css/`

Structure:

```text
css/
  tokens.css        # Design tokens: colours, type scale, spacing, shadows
  base.css          # Reset, html/body, base typography, links
  layout.css        # Layout shell, .section, .container, grid helpers
  utilities.css     # Small utilities (.visually-hidden, text helpers, etc.)
  animations.css    # Reveal animations, transitions

  components/
    buttons.css
    forms.css
    cards.css
    header.css
    footer.css
    hero.css
    services.css
    testimonials.css
    # future: trust-strip.css, cta-section.css, faq.css, etc.

  main.css          # The bundled entry file Wagtail actually loads
```

**Important:**

* Templates and HTML must **only** link to `main.css`.
* `main.css` is responsible for `@import`-ing everything else (or being built from them).

---

### 3. Tokens: Single Source of Truth

`tokens.css` is the **only place** where raw design values live:

* Type scale: `--text-xs`, `--text-sm`, …, `--text-4xl`
* Spacing: `--space-xs`, `--space-sm`, …, `--space-6`
* Colours: `--color-primary`, `--color-surface`, etc. (derived from branding HSL tokens)
* Shadows, radii, borders, etc.

All other CSS files **must only refer to tokens**, e.g.:

```css
padding: var(--space-md);
background-color: var(--color-surface);
box-shadow: var(--shadow-sm);
```

No new colours, font sizes, line-heights, or magic numbers in component/layout CSS.

---

### 4. Typography Roles → Classes

We don’t design per-block typography; we use **roles** mapped to fixed classes.

**Roles and mappings:**

* **Hero H1** → `.heading-xl` (or `.heading-display` if you use that)
* **Section heading (big)** → `.heading-lg`
* **Card / block heading (minor)** → `.heading-md`
* **Eyebrow / kicker** → `.text-sm .text-muted`
* **Section intro / lead** → `.text-body .text-muted`
* **Body copy** → `.text-body`
* **Tiny meta / caption** → `.text-xs .text-muted`

Rules:

* Every piece of text in a new block must be assigned one of these roles and use the mapped class.
* Do **not** set `font-family`, `font-size`, `line-height`, or `letter-spacing` in block-specific CSS.
* Fonts come from **branding** (SiteSettings + `branding_fonts` tag) and the base type scale in `tokens.css`.

---

### 5. Layout & Components

#### 5.1 Sections & containers

* Every major content block is:

  ```html
  <section class="section [section--muted|section--inset]">
    <div class="container">
      …
    </div>
  </section>
  ```

* Use `.section--muted` for subtle background emphasis.

* Use `.section--inset` for reduced vertical padding.

#### 5.2 Grids

We follow a consistent grid pattern for cards:

* Mobile: 1 column
* Tablet: 2 columns
* Desktop: 3 columns

Example:

```css
.services__grid,
.testimonials__grid {
    display: grid;
    gap: var(--space-6);
    grid-template-columns: 1fr;
}

@media (min-width: 768px) {
    .services__grid,
    .testimonials__grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }
}

@media (min-width: 1024px) {
    .services__grid,
    .testimonials__grid {
        grid-template-columns: repeat(3, minmax(0, 1fr));
    }
}
```

New grids (e.g. trust strip, FAQs) should copy this pattern with their own namespaced class (e.g. `.trust-strip__grid`).

#### 5.3 Cards & components

* Use `.card` as the base for any card-like block.
* Component-specific styles go into `components/<component>.css`:

  * Buttons → `components/buttons.css`
  * Hero → `components/hero.css`
  * Services → `components/services.css`
  * Testimonials → `components/testimonials.css`
  * Etc.

No component should redefine generic card padding/borders; extend `.card` instead.

---

### 6. Rules for New Work (for humans & agents)

When you implement a new block or tweak design:

1. **Where to put CSS**

   * Add styles in `components/<block-name>.css`.
   * Add an `@import "components/<block-name>.css";` entry in `main.css` (if not already present).
   * Do **not** put new CSS rules in templates.

2. **What you’re allowed to write**

   * ✅ Use classes from this guide (`.section`, `.container`, `.heading-*`, `.text-*`, `.card`, etc.).
   * ✅ Use tokens via `var(--...)` for colours, spacing, shadows.
   * ❌ No inline `style="..."`.
   * ❌ No new `font-family`, `font-size`, `line-height`, `letter-spacing` in component CSS.
   * ❌ No raw hex or RGB colours.

3. **How to design text**

   * Decide the role: section heading, card title, eyebrow, body, meta.
   * Apply the corresponding class from the typography roles table.
   * Don’t invent a block-specific heading size.

4. **How to design layout**

   * Wrap the block in `.section` + `.container`.
   * If you need a grid, follow the 1/2/3 column pattern used in services/testimonials.
   * Use spacing tokens (`--space-*`) for margins/gaps/paddings.

---

### 7. Token Compliance Checklist

Before merging any design/block change:

* [ ] No `style="..."` in templates.
* [ ] No `font-family`, `font-size`, `line-height`, or `letter-spacing` in component CSS.
* [ ] No raw hex or RGB values in new CSS (outside `tokens.css`).
* [ ] All new spacing uses `var(--space-*)`.
* [ ] All new colours use `var(--color-*)` or branding HSL tokens.
* [ ] All headings use the appropriate `.heading-*` class from the roles table.
* [ ] New sections use `.section` + `.container`.
* [ ] New grids follow the 1/2/3 column pattern.
* [ ] `make test` passes and existing tests weren’t just deleted to make it green.
