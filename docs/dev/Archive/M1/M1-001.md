**[MILESTONE-001] Implement Core CSS Token System (`main.css`)**

---

### Context (from PRD & Init Packet)

* Milestone 1’s goal is to “implement the token-based CSS design system and base HTML templates, establishing the visual foundation for all client sites.” 
* Design System overview mandates a **token-driven architecture**: all visual properties (colour, typography, spacing) are defined as CSS custom properties, populated from each client’s SiteSettings. 
* Appendix C provides **canonical token names and scales** for colours, typography, spacing, radii, and shadows. These definitions are the source of truth for implementation.
* The design system document (SolarCraft) stresses that premium feel comes from **structure, spacing, and depth**, not hardcoded colours. Tokens + rules like the “Pinky” rule and “Breath” rule enforce this.

**Relevant user stories / epics**

* **US-BR02: Dynamic CSS Generation** – all component styles must use CSS variables, no hardcoded colours. This task lays the groundwork by defining the token system that those components will consume. 
* **Design Specifications 6.3 (Design System Overview)** – defines required token categories (colour, typography, spacing, etc.) and insists all components use them exclusively. 

---

### Technical Requirements (from Implementation Plan & Design System)

From Implementation Plan, Milestone 1 core deliverables:

* “CSS token system in `sum_core/static/sum_core/css/` with colour, typography, spacing, shadow, and radius tokens.” 

From PRD Appendix C + Design System:

* Token categories to implement in CSS:

  * **Colour tokens (names only in this task)**: `--color-primary`, `--color-secondary`, `--color-accent`, `--color-background`, `--color-surface`, `--color-surface-elevated`, `--color-text`, `--color-text-light`, `--color-text-inverse`, `--color-success`, `--color-warning`, `--color-error`, `--color-info`, `--color-border`, `--color-border-dark`. 
  * **Typography tokens**: font-size scale `--text-xs` … `--text-6xl`, font weights `--font-normal`, `--font-medium`, `--font-semibold`, `--font-bold`, and line heights `--leading-tight`, `--leading-normal`, `--leading-relaxed`.
  * **Spacing tokens**: `--space-1` … `--space-24` (4px scale) as per Appendix C. 
  * **Radius tokens**: e.g. `--radius-none`, `--radius-sm`, `--radius-md`, `--radius-lg`, `--radius-full`. 
  * **Shadow tokens**: e.g. `--shadow-xs`, `--shadow-sm`, `--shadow-md`, `--shadow-lg`. 

* **Separation of concerns**:

  * This task implements the **canonical token definitions and base layout/typography utilities** in `main.css`.
  * **Dynamic population** of colour and font family values from `SiteSettings` via `{% branding_css %}` will be implemented in a **later Milestone 1 task** (US-BR01/BR02). For now, we may include sensible default/fallback values but must not wire any Django/Wagtail template tags.

* **Architecture / patterns**

  * Tokens live under `:root { ... }` and are **referenced everywhere via `var(--token-name)`**.
  * Any base utility classes must follow **kebab-case BEM** naming (`block__element--modifier`) as per Initiation Packet naming conventions. 
  * No JS, no Django/Wagtail Python changes in this task.

---

### Design Specifications (from PRD, Design System & Reference Design)

* **Visual baseline** should align with `premium-trade-website-v3-final.html` in terms of spacing, typography hierarchy, and section rhythm (not necessarily exact colours yet). 

* Design guardrails:

  * All spacing should be expressed in terms of `--space-*` tokens.
  * All border radii via `--radius-*`.
  * All shadows via `--shadow-*`.
  * No fixed pixel values for colours or spacing in component-level styles; only tokens. (Exceptions: very-low-level resets and browser-normalising styles, kept minimal.) 

* Layout rules from design_system / PRD:

  * **“Pinky” rule**: interactive elements must have at least ~12px padding; our spacing scale must make that easy (e.g. `--space-3` = 12px). 
  * **“Breath” rule**: section padding roughly 4rem mobile / 8rem desktop, implemented via tokens like `--space-section-y-mobile` and `--space-section-y-desktop` that map to the 4px scale (e.g. 64px/128px).

---

### Implementation Guidelines

**Scope of this task**

* Implement **one canonical CSS file** at:
  `core/sum_core/static/sum_core/css/main.css`
* This task covers:

  1. Global CSS variables (tokens) under `:root`
  2. Minimal base/reset and typography defaults
  3. A handful of **structural utilities** that will be reused by base templates and blocks (e.g. `.container`, `.section`, typography helpers)
* This task explicitly **does NOT**:

  * Implement Django/Wagtail templates or template tags
  * Implement component-specific CSS (buttons, forms, cards, nav) – that’s a separate Milestone 1 task
  * Implement `{% branding_css %}` or SiteSettings model

---

#### Files to Create / Modify

1. **Create** `core/sum_core/static/sum_core/css/main.css` if it does not exist.
2. Ensure `core/sum_core/static/sum_core/` is present and matches PRD path expectations.

Inside `main.css`, structure the file into clear sections with comment headers, for example:

```css
/* ==========================================================================
   1. Design Tokens
   ========================================================================== */

/* 1.1 Colour Tokens */
/* 1.2 Typography Tokens */
/* 1.3 Spacing Tokens */
/* 1.4 Radius Tokens */
/* 1.5 Shadow Tokens */

/* ==========================================================================
   2. Base / Reset
   ========================================================================== */

/* ==========================================================================
   3. Typography & Layout Utilities
   ========================================================================== */

/* ==========================================================================
   4. Containers & Sections
   ========================================================================== */
```

(Exact comment format is up to you, but keep it structured and consistent.)

---

#### Token Definitions

**1. Design Tokens (`:root`)**

* Implement the **exact token names and semantic groupings** from Appendix C; do not invent new token names unless needed, and if added, keep them clearly namespaced and aligned with PRD semantics.

* **Colour tokens**

  * Declare all colour tokens in `:root`, using the canonical names:

    * `--color-primary`
    * `--color-secondary`
    * `--color-accent`
    * `--color-background`
    * `--color-surface`
    * `--color-surface-elevated`
    * `--color-text`
    * `--color-text-light`
    * `--color-text-inverse`
    * `--color-success`
    * `--color-warning`
    * `--color-error`
    * `--color-info`
    * `--color-border`
    * `--color-border-dark`

  * For this task, it’s acceptable to provide **sensible defaults** approximating the “Premium Trade” preset table (using the PRD values) so that styles work before dynamic branding is implemented. 

  * Include a short comment block noting that these values will be **overridden by dynamic CSS** generated from SiteSettings in a later task (US-BR02).

* **Typography tokens**

  * Implement font-size, weight, and line-height tokens exactly as in Appendix C.

  * For `--font-heading` and `--font-body`, either:

    * Provide neutral defaults (e.g. system-ui stacks) **and** note they are overridden later, **or**
    * Omit explicit values and rely on `var(--font-heading, system-ui, sans-serif)` in usage sites.

  * Ensure the scale is consistent with Appendix C (e.g. base 16px, increasing scale to `--text-6xl`).

* **Spacing tokens**

  * Implement `--space-1` … `--space-24` as a 4px scale (e.g. `--space-1: 0.25rem;` for 4px, etc.), matching Appendix C. 
  * Optionally define aliases like `--space-section-y-mobile` and `--space-section-y-desktop` referencing scale values for “Breath” rule; these must still be built on the 4px scale.

* **Radius tokens**

  * Implement radius tokens for none, small, medium, large, and full. Names should match Appendix C (e.g. `--radius-sm`, `--radius-md`, `--radius-lg`, `--radius-full`). 

* **Shadow tokens**

  * Implement shadow tokens (`--shadow-xs`, `--shadow-sm`, `--shadow-md`, `--shadow-lg`) as box-shadow values that feel “premium” and soft (as per design_system’s coloured/elevated feel). We don’t need to replicate the exact HSL-shadow formulas now, but they should be tuned for the “luxury” aesthetic.

---

#### Base / Reset

* Add a minimal reset/normalisation layer:

  * Use `box-sizing: border-box` on all elements.
  * Reset margin on `body`, set background to `var(--color-background)` and text colour to `var(--color-text)`.
  * Set `font-family` on `body` using `var(--font-body, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif);`.

* Do **not** include a full CSS reset library; keep it lean and opinionated for our platform.

---

#### Typography & Layout Utilities

* Implement utility classes that will be reused in templates and blocks:

  * Heading utilities (e.g. `.heading-xl`, `.heading-lg`, `.heading-md`) mapping to `--text-4xl`, `--text-3xl`, `--text-2xl`, using `var(--font-heading)`.
  * Body text utility (e.g. `.text-body`) mapping to `--text-base` and `var(--font-body)`.
  * Muted text class (e.g. `.text-muted`) using `var(--color-text-light)`.

* All font sizes should use the token scale; no raw pixel values.

---

#### Containers & Sections

* Implement generic structural classes matching Appendix C’s examples for containers and section headings. 

  * `.container` – width 100%, max-width 1280px, centered, horizontal padding using spacing tokens (`--space-4` base, `--space-6` at `sm` breakpoint).
  * `.section` – vertical padding using the “Breath” rule via spacing tokens (mobile vs desktop).
  * `.section__header`, `.section__title`, `.section__subtitle` – as per Appendix C, referencing typography and colour tokens (no raw values).

* Use mobile-first media queries aligned with the breakpoint system (`sm`, `md`, `lg`, `xl`, `2xl`). 

---

### Acceptance Criteria

For this task to be considered complete:

1. **Token definitions**

   * `core/sum_core/static/sum_core/css/main.css` exists and contains a `:root` block defining all token names required by Appendix C for typography, spacing, radii, and shadows.
   * Colour tokens (`--color-*`) are declared in `:root` with safe defaults and clearly marked as overrideable via dynamic branding CSS in a later task.

2. **Usage rules**

   * All utility classes in `main.css` reference tokens via `var(--...)`.
   * There are **no hardcoded hex colours** or magic pixel values for spacing/border-radius/shadows in these utilities (except where absolutely necessary for reset/baseline behaviour, which should be minimal and justified).

3. **Structure & naming**

   * CSS follows **kebab-case BEM-style** naming for any structural classes (`section__header`, `section__title`, etc.). 
   * File is logically organised into sections (tokens, base, utilities, containers/sections) with clear comments.

4. **Compatibility**

   * `make lint` and `make test` still pass (no Python changes in this task; CSS is not yet wired into tests).
   * No changes are made to templates or Python modules in this ticket.

---



### Testing Requirements

**Automated**

* Ensure existing `make lint` / `make test` targets pass after CSS addition.

**Manual / Developer Checks**

1. After adding `main.css`, run:

   * `make lint`
   * `make test`

2. Open the file and verify:

   * All required tokens from Appendix C are present.
   * Utilities use `var(--token-name)` exclusively for colours, spacing, radii, and shadows.
   * There are clear comments indicating that colour and font tokens will be driven by future dynamic CSS from `SiteSettings`.

Later tasks will:

* Wire `main.css` into base templates
* Implement `SiteSettings`, `{% branding_css %}` / `{% branding_fonts %}`
* Add visual regression / snapshot tests once the design is wired into Wagtail templates.

---


The main risks here are **inconsistency with PRD token names** and **accidental hardcoded values**; both are mitigated by aligning strictly with Appendix C and the naming conventions above.
