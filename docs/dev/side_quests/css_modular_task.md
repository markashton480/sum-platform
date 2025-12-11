## [M1.5-001] Modularise Design System CSS & Establish CSS Architecture

**Milestone:** 1.5 – Design System Hygiene & Token Discipline

---

### Context (from PRD / Review)

* The PRD defines a **token-based design system** (typography scale, spacing scale, colour tokens, radius, shadows, animation easings) that must be **brandable via Wagtail SiteSettings** and stable across multiple client sites.
* The current implementation has a **single `main.css` (~1400+ lines)** with all tokens, base, utilities, layout, and component styles mixed together. This makes it hard to navigate, extend, or safely override, and risks “CSS specificity wars” as client sites grow.
* Code review explicitly recommends **modularising CSS into component files** (tokens, reset, utilities, header, hero, services, testimonials, footer) while keeping a single public entrypoint for templates.

**Business Requirement Excerpt (summarised)**

* The SUM core platform should provide a **reusable, themeable design system** that multiple trade sites can share without each project inventing its own CSS architecture.
* The design system must be **easy to extend** for new content blocks, with consistent styling and predictable overrides.

**Relevant User Story (summarised)**

> As a developer or AI agent implementing new blocks, I want a **clear CSS architecture and token usage guide** so that when I build or tweak components, typography and colours stay in sync with the Wagtail branding settings and don’t require hand-coded fonts or hex values.

---

### Technical Requirements (from Tech Spec / Architecture)

* **Single public stylesheet:**

  * `base.html` must continue to load a single stylesheet at `sum_core/css/main.css`. No template changes should be required for client projects.

* **Internal modular structure:**

  * Internally, split the current `main.css` into **logical partials** under the same static path. Suggested structure (can be refined, but stick to this spirit):

    ```text
    core/sum_core/static/sum_core/css/
    ├── main.css              # Public entrypoint (only file referenced in templates)
    ├── _tokens.css           # Design tokens only (variables, scales)
    ├── _reset.css            # Normalize/reset + html/body basics
    ├── _utilities.css        # Utility classes (spacing, typography helpers, reveals, etc.)
    ├── _layout.css           # Layout shell .layout*, .container, .section, grid helpers
    ├── _components.header.css
    ├── _components.hero.css
    ├── _components.services.css
    ├── _components.testimonials.css
    ├── _components.cards.css
    ├── _components.forms.css
    └── _components.footer.css
    ```

* **Load order must preserve cascade:**

  In `main.css` (top-to-bottom):

  1. Tokens (`_tokens.css`)
  2. Reset (`_reset.css`)
  3. Base/layout (`_layout.css`)
  4. Utilities (`_utilities.css`)
  5. Components (header, hero, services, testimonials, cards, forms, footer…)

* **No change to branding integration:**

  * `{% branding_css %}` continues to inject dynamic CSS variables in `<head>`; modularisation must **not** change variable names or usage patterns. Tests around `branding_css` must continue to pass.

* **Token discipline:**

  * All component partials must **only** use design tokens (CSS variables, typography utilities, spacing utilities) for colour, type, and spacing.
  * No new hard-coded hex values or font families are allowed in partials (existing ones should be refactored to tokens where feasible).

* **No new build step:**

  * Do **not** introduce PostCSS, Sass, or other build tools in this task. Use plain CSS with `@import` (or similar) so the existing staticfiles pipeline still works.

---

### Design Specifications (from Design References)

* **Visual behaviour unchanged:**

  * Hero, trust strip, service cards, testimonials, header, and footer must all **look and behave the same** before and after modularisation on the Premium Trade test site (layout, spacing, typography, buttons, hover states, reveal animations).

* **Responsiveness:**

  * Existing breakpoints (mobile-first with ~768px and ~1024px breakpoints) must remain intact and continue to drive the same layout adaptations.

* **Accessibility:**

  * Do not remove or break any classes used for focus-visible, skip links, or reveal animations tied to intersection observer JS.

---

### Implementation Guidelines

#### 1. Plan the CSS Architecture

* Read existing `core/sum_core/static/sum_core/css/main.css` end-to-end and sketch a mapping from **sections → partial files**.
* Proposed mapping (fine to tweak, but document any changes in the new guide):

  * Tokens & scales → `_tokens.css`
  * Reset & base HTML/body → `_reset.css`
  * Typography base (global font-family, body text defaults), `.heading-*`, `.text-*` helpers → `_layout.css` or a small `_typography.css` if you prefer (but keep file count reasonable).
  * Layout shell `.layout*`, `.container`, `.section*`, grid helpers → `_layout.css`
  * Utilities (`.u-*` helpers, reveal-text, spacing helpers) → `_utilities.css`
  * Header/navigation styles → `_components.header.css`
  * Hero-specific styles → `_components.hero.css`
  * Service cards → `_components.services.css`
  * Testimonials → `_components.testimonials.css`
  * Generic cards → `_components.cards.css`
  * Forms → `_components.forms.css`
  * Footer → `_components.footer.css`

#### 2. Create Partial Files & Header Comments

For each new CSS file, include a header comment using the project’s documentation pattern (adapted for CSS):

```css
/* ==========================================================================
   Name: [File Name / Purpose]
   Path: core/sum_core/static/sum_core/css/[file]
   Purpose: [Brief description]
   Family: SUM Platform Design System – [Tokens/Layout/Component: X]
   Dependencies: [e.g. requires _tokens.css, _layout.css, etc.]
   ========================================================================== */
```

* Update the existing `main.css` header to reference **“SUM Platform Design System”** instead of the legacy “SolarCraft Premium” naming.

#### 3. Refactor `main.css` into Partials

* **Non-destructive approach:**

  1. Copy `main.css` to a temporary file (`main.working.css`) while refactoring.
  2. Create partials and **move** corresponding rule blocks from the working file into the appropriate partial.
  3. Keep selectors and declarations identical; do not “improve” design in this task—this is a structural refactor only.
  4. When all sections are moved, replace `main.css` content with:

     ```css
     /* SUM Platform Design System – CSS Entrypoint */
     @import "tokens.css";
     @import "reset.css";
     @import "layout.css";
     @import "utilities.css";
     @import "components.header.css";
     @import "components.hero.css";
     @import "components.services.css";
     @import "components.testimonials.css";
     @import "components.cards.css";
     @import "components.forms.css";
     @import "components.footer.css";
     ```

     > Note: The underscore-prefix in file names is for developer clarity only; the actual filenames referenced in `@import` should **not** include `_` unless you choose to keep them. Just ensure the imports map to real static file names.

* Double-check relative paths so that, after `collectstatic`, `main.css` can still find sibling CSS files.

#### 4. Token Clean-Up Pass

* While moving rules, **scan for:**

  * Hard-coded hex colours (`#…`) that are not part of the token definitions.
  * Hard-coded font families (e.g. `"Playfair Display"` directly in a component file).
  * Spacing values that do not align with the documented scale (e.g. `13px`, `23px`).

* Where safe and obvious, refactor to use:

  * Colour variables: `var(--color-primary)`, `var(--color-text)`, etc.
  * Typography utilities: `.heading-xl`, `.heading-md`, `.text-body`, etc.
  * Spacing tokens: `var(--space-*)`, or layout utilities already defined.

* If you must leave any hard-coded value in place (because no suitable token exists yet), add a **`TODO`** comment explaining why and referencing the future token work, e.g.:

  ```css
  /* TODO: Introduce token for subtle border colour, PRD doesn’t define this yet. */
  border-color: rgba(255, 255, 255, 0.08);
  ```

#### 5. Documentation Touchpoint (Lightweight for This Task)

* Add or update a short section in `docs/design/css-architecture-and-tokens.md` (or create this file if it doesn’t exist yet) describing:

  * The new partial structure (`main.css` + partials).
  * The rule: “**Only tokens + utilities** for type/colour/spacing in block CSS.”
  * Where to add new component styles (e.g. `components.*.css`) and how to hook new files into `main.css`.

  Keep this relatively brief; a deeper token-implementation guide can be its own later task.

---

### Acceptance Criteria

* **Architecture:**

  * `core/sum_core/static/sum_core/css/main.css` remains the **only** stylesheet referenced in templates. No other template or Python change is required.
  * New CSS partial files exist, and `main.css` imports them in a **sensible cascade order**: tokens → reset → layout → utilities → components.

* **Behaviour:**

  * No visual regressions on the test project homepage:

    * Header & nav still styled correctly.
    * Hero section looks and behaves as before (including reveal animations).
    * Service cards and testimonials still align with existing design.
    * Footer is unchanged visually.
  * All reveal animations, layout breakpoints, and hover states still work exactly as before.

* **Token Usage:**

  * No **new** hard-coded font families or colour hex values appear in component partials.
  * Most obvious legacy hard-coded values are replaced with tokens or utilities where feasible, without changing intent.

* **Documentation:**

  * `main.css` header updated to “SUM Platform Design System”.
  * A brief CSS architecture section exists in `docs/design/css-architecture-and-tokens.md` (or equivalent docs file) explaining:

    * Partial structure
    * Import order
    * Where to put new component styles
    * The “tokens only” rule for colour/typography/spacing

* **Tests & Tooling:**

  * `make lint` and `make test` both pass with no modifications to Python tests needed.

---

### Dependencies & Prerequisites

* Existing design system and token definitions in `main.css` are already PRD-aligned and tested.
* Branding tags (`branding_css`, `branding_fonts`) and SiteSettings are fully implemented and tested; this task **must not** alter their APIs or outputs.
* Milestone 1 (base layout, design system, branding) and Milestone 2 initial blocks are already in place.

---

### Testing Requirements

**Automated**

* Run full test suite:

  * `make lint`
  * `make test`

* Ensure no tests that depend on template structure or CSS variable names break (branding tests, template tests, block tests).

**Manual**

On the local dev site (Premium Trade reference):

1. Visit `/` (HomePage) and confirm:

   * Header and nav render and remain sticky/behave as before.
   * Hero, service cards, and testimonials look the same at:

     * ~360px width (mobile)
     * ~768px width (tablet)
     * ~1200px+ (desktop)
2. Temporarily change fonts and colours via SiteSettings:

   * Confirm typography & colours update across hero, service cards, and testimonials as before.
3. Use browser DevTools:

   * Verify that `main.css` is loaded and that partial CSS files are fetched (or inlined via imports) with no 404s.

---

### Estimated Complexity

* **Time:** M (roughly in the 6–10 hour range from the code review estimate).
* **Risk:** Medium

  * Structural change to a central file can cause regressions if order is wrong; mitigated by careful mapping and full test + manual pass.
