## SUM CSS & Design System Guide

### 1. Goals

- **Single source of truth for design values** (tokens).
- **Consistent implementation** across all blocks (typography, spacing, layout).
- **Modular CSS** that's easy to navigate and extend.
- **Branding-controlled**: changing fonts/colours in Wagtail SiteSettings updates the whole site.

---

### 2. CSS Architecture

All CSS lives under:

`core/sum_core/static/sum_core/css/`

#### 2.1 File Structure

```text
css/
  main.css                    # Public entrypoint (ONLY file referenced in templates)

  # Foundation Layer
  tokens.css                  # Design tokens: colours, type scale, spacing, shadows
  reset.css                   # Normalize/reset + html/body basics
  layout.css                  # Layout shell, .section, .container, grid helpers
  utilities.css               # Reveal animations, transitions, helper classes

  # Component Layer
  components.buttons.css      # Button variants (primary, outline, link)
  components.header.css       # Site header and navigation
  components.hero.css         # Hero sections and variants
  components.trust-strip.css  # Marquee/trust badges
  components.features.css     # Feature cards grid
  components.comparison.css   # Before/after slider
  components.portfolio.css    # Portfolio grid
  components.mobile-fab.css   # Mobile floating action button
  components.cards.css        # Base card patterns
  components.services.css     # Service cards block
  components.testimonials.css # Testimonials block
  components.forms.css        # Form elements
  components.footer.css       # Site footer
```

#### 2.2 Import Order (in main.css)

The cascade order is critical for CSS specificity:

1. **Tokens** (`tokens.css`) – CSS custom properties
2. **Reset** (`reset.css`) – Browser normalization
3. **Layout** (`layout.css`) – Structural helpers
4. **Utilities** (`utilities.css`) – Animation and helper classes
5. **Components** – All component files

**Important:**

- Templates and HTML must **only** link to `main.css`.
- `main.css` is responsible for `@import`-ing everything else.
- No build step is required – uses native CSS `@import`.

---

### 3. Tokens: Single Source of Truth

`tokens.css` is the **only place** where raw design values live:

- Type scale: `--text-xs`, `--text-sm`, …, `--text-display`
- Spacing: `--space-1`, `--space-2`, …, `--space-24`
- Colours: `--primary`, `--surface-tint`, `--text-main`, etc. (derived from branding HSL tokens)
- Font families: `--font-heading`, `--font-body`, `--font-display`
- Font weights: `--font-light`, `--font-normal`, `--font-medium`, `--font-semibold`, `--font-bold`
- Shadows, radii, borders, animation easings

All other CSS files **must only refer to tokens**, e.g.:

```css
padding: var(--space-8);
background-color: hsla(var(--surface-pure), 1);
box-shadow: var(--shadow-lg);
font-family: var(--font-body);
```

**No new colours, font sizes, line-heights, or magic numbers in component/layout CSS.**

---

### 4. Typography Roles → Classes

We don't design per-block typography; we use **roles** mapped to fixed classes.

**Roles and mappings:**

- **Hero H1** → Uses `--text-display` token
- **Section heading (big)** → `clamp(2rem, 5vw, 3.5rem)` via component heading
- **Card / block heading (minor)** → Uses `--text-xl` token
- **Eyebrow / kicker** → Uses `--text-xs` with uppercase styling
- **Section intro / lead** → Uses `--text-lg` with muted colour
- **Body copy** → Uses `--text-base` token
- **Tiny meta / caption** → Uses `--text-xs` with muted colour

Rules:

- Every piece of text in a new block must use tokens for sizing.
- Do **not** set `font-family`, `font-size`, `line-height`, or `letter-spacing` with hardcoded values.
- Fonts come from **branding** (SiteSettings + `branding_fonts` tag) and the tokens in `tokens.css`.

---

### 5. Layout & Components

#### 5.1 Sections & containers

- Every major content block is:

  ```html
  <section class="section [section--dark]">
    <div class="container">…</div>
  </section>
  ```

- Use `.section--dark` for dark background sections (like testimonials).

#### 5.2 Grids

We follow a consistent grid pattern for cards:

- Mobile: Horizontal scroll with snap
- Tablet: 2 columns or 45vw cards
- Desktop: 3 columns

Example pattern in services/testimonials:

```css
.services__grid {
  display: flex;
  gap: var(--space-6);
  overflow-x: auto;
  scroll-snap-type: x mandatory;
}

@media (min-width: 1024px) {
  .services__grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    overflow: visible;
  }
}
```

New grids should copy this pattern with their own namespaced class.

#### 5.3 Cards & components

- Service cards → `components.services.css`
- Testimonial cards → `components.testimonials.css`
- Generic cards → `components.cards.css`

Component-specific styles go into `components.<name>.css` files.

---

### 6. Adding New Components

When implementing a new block or component:

1. **Create the CSS file**

   - Create `components.<block-name>.css` in the css directory.
   - Add a header comment following the project pattern:

   ```css
   /* ==========================================================================
      Name: [Component Name]
      Path: core/sum_core/static/sum_core/css/components.<name>.css
      Purpose: [Brief description]
      Family: SUM Platform Design System – Component: [Name]
      Dependencies: [e.g. tokens.css, layout.css]
      ========================================================================== */
   ```

2. **Register in main.css**

   - Add `@import "components.<block-name>.css";` to `main.css` in the appropriate section.

3. **Use only tokens**

   - ✅ Use tokens via `var(--...)` for colours, spacing, shadows.
   - ✅ Use font tokens: `--font-heading`, `--font-body`, `--font-display`.
   - ✅ Use size tokens: `--text-xs` through `--text-display`.
   - ❌ No inline `style="..."` in templates.
   - ❌ No new hardcoded `font-family`, `font-size`, `line-height`, `letter-spacing`.
   - ❌ No raw hex or RGB colours.

4. **Follow layout patterns**

   - Wrap the block in `.section` + `.container`.
   - Use the mobile-scroll → desktop-grid pattern for card grids.
   - Use spacing tokens (`--space-*`) for margins/gaps/paddings.

---

### 7. Token Compliance Checklist

Before merging any design/block change:

- [ ] No `style="..."` in templates.
- [ ] No hardcoded `font-family`, `font-size`, `line-height`, or `letter-spacing` (use tokens).
- [ ] No raw hex or RGB values in new CSS (outside `tokens.css`).
- [ ] All new spacing uses `var(--space-*)`.
- [ ] All new colours use HSL token patterns.
- [ ] New sections use `.section` + `.container`.
- [ ] New grids follow the mobile-scroll/desktop-grid pattern.
- [ ] New component file has proper header comment.
- [ ] Component is imported in `main.css`.
- [ ] `make test` passes and existing tests weren't just deleted to make it green.

---

### 8. File Header Template

Every CSS partial should include this header:

```css
/* ==========================================================================
   Name: [File Name / Purpose]
   Path: core/sum_core/static/sum_core/css/[file]
   Purpose: [Brief description]
   Family: SUM Platform Design System – [Tokens/Layout/Component: X]
   Dependencies: [e.g. requires tokens.css, layout.css, etc.]
   ========================================================================== */
```

---

### 9. TODO Comments

If you must leave any hardcoded value in place (because no suitable token exists yet), add a **`TODO`** comment explaining why:

```css
/* TODO: Introduce token for status indicator color (green for "available") */
background-color: #10b981;
```

These TODOs signal future token work without blocking current development.
