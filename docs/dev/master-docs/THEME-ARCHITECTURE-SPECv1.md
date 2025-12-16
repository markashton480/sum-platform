# Theme Architecture Spec v1

**Status:** Proposed (post-M5)
**Audience:** Platform maintainers + AI agents implementing themes & scaffolding
**Purpose:** Enable 4–5 fixed, swappable base themes per client site, chosen at init-time, with an AI-friendly build workflow (Tailwind-first), while keeping `sum_core` presentation-agnostic.

## 1. Goals

### 1.1 Primary goals

* **Theme is fixed per site** and selected during scaffolding (not in Wagtail admin).
* Support **4–5 base themes** that differ in:

  * layout conventions (header/hero/sections)
  * typography pairing and scale
  * colour “vibe”
  * component styling patterns
* **AI-friendly styling**: theme development should be faster and more consistent than token-only bespoke CSS.

### 1.2 Secondary goals

* Theme development can start as a “static” prototype (Django templates + Tailwind) and then be progressively “Wagtailified”.
* Keep `sum_core` reusable and stable across many client sites.

## 2. Non-goals

* No per-page theme switching.
* No Wagtail-admin theme switching.
* No “theme marketplace”, no remote theme fetching.
* No requirement to rewrite `sum_core` internals as part of theme adoption (keep changes minimal and isolated).

---

## 3. Definitions

### 3.1 Platform vs Client vs Theme

* **`sum_core`**: backend capabilities, models, blocks, ops, SEO/analytics, forms, navigation tags, health endpoint. Should avoid assuming a specific theme structure.
* **Client project**: a consumer of `sum_core` created via `sum init`, with its own settings split and its own HomePage/content layer.
* **Theme**: a curated set of templates + static assets + Tailwind configuration + design tokens (as CSS variables), bundled as files and copied into the client project at init-time.

---

## 4. Theme contract

A theme **MUST** provide:

### 4.1 Templates

* A **base template** (one per theme) that defines the global HTML structure and required extension blocks.
* Page templates for the canonical page types used in client projects (at minimum Home, Standard page).
* Component partials used by those page templates.

### 4.2 Static assets

* A theme CSS build (Tailwind output) and optional lightweight JS.
* Font strategy (local or provider links) must be explicit and consistent.

### 4.3 Theme metadata

* A `theme.json` that declares:

  * `slug`, `name`, `version`
  * intended “vibe”
  * supported features flags (e.g. “has fancy hero”, “supports dark mode”)
  * recommended font pairing
  * optional screenshot paths for future docs

### 4.4 Accessibility baseline

Themes must meet the platform testing posture: accessibility is a first-class risk area. 
At minimum:

* visible focus states
* keyboard navigable menus
* skip link support
* reasonable touch target sizes
* semantic landmarks

---

## 5. Directory layout

### 5.1 Canonical repo layout

Add a top-level directory:

```
themes/
  theme_<slug>/
    theme.json
    templates/
      theme/
        base.html
        includes/
        pages/
    static/
      theme_<slug>/
        css/
          main.css            (Tailwind input)
          built.css           (Tailwind output, committed or built—decide per workflow)
        js/
        img/
    tailwind/
      tailwind.config.js
      postcss.config.js       (if needed)
    README.md                 (how to dev/build this theme)
```

### 5.2 Client project layout after init

When a client chooses a theme, `sum init` copies it into:

```
clients/<client>/
  theme/
    active/                   (copied theme root)
      theme.json
      templates/...
      static/...
      tailwind/...
```

Why “theme/active/”? It makes later “theme swap” operations mechanically simple (replace the folder) without encouraging runtime switching.

---

## 6. Template block contract

All themes must implement these blocks in `base.html`:

* `{% block html_head %}`

  * title/meta hooks
  * `{% seo_tags %}` integration belongs here (sum_core provides)
* `{% block analytics_head %}` / `{% block analytics_body %}`

  * injection points for analytics tags (sum_core provides template tags)
* `{% block body %}`

  * main layout, header/footer skeleton
* `{% block main %}`

  * page content insertion point
* `{% block extra_js %}` and `{% block extra_css %}`

  * allow client-specific overrides without editing theme core
* Include required accessibility elements:

  * skip link
  * `main` landmark

**Theme base template must include “hook points” used by `sum_core` tags** (SEO, analytics, branding variables if retained). The core already expects branding injection via template tags today.

---

## 7. Styling strategy

### 7.1 Tailwind-first, variables for brand slots

**Recommendation (best of both worlds):**

* Tailwind for structure, spacing, typography scale, layout, component composition.
* CSS variables for brand “slots” (colour surfaces/text/accents), so a theme can be re-skinned without rewriting Tailwind classes.

Example variables:

* `--color-bg`, `--color-surface`, `--color-text`, `--color-muted`
* `--color-primary`, `--color-primary-contrast`
* `--color-accent`, `--color-border`

Tailwind config maps to variables:

* `colors.primary: "rgb(var(--color-primary) / <alpha-value>)"` style mapping, etc.

### 7.2 Theme preset vs fixed theme (reconcile with PRD)

The PRD’s “5 preset themes applied via SiteSettings” is effectively “starting palette + fonts, editable after”. 
Your proposed approach is “fixed theme per site, chosen at init.”

You can support both by reframing:

* **Fixed theme** = layout + component system + typography scale.
* **Brand preset** (optional) = initial CSS variable values (fonts/colours) still editable in SiteSettings if you want. The platform already injects branding vars via tags today.

So:

* Theme selection remains init-time and fixed.
* Brand presets remain an internal shortcut for setting the variable values for a given client.

If you later want to remove SiteSettings-driven styling entirely, that becomes a deliberate “Theme v2” milestone.

### 7.3 AI agent ergonomics rules

To make agents effective:

* Prefer “semantic component partials” over massive templates.
* Avoid bespoke CSS unless absolutely needed.
* Any bespoke CSS must live in `static/theme_<slug>/css/components/*.css` and be imported into Tailwind build.
* Do not hand-edit generated Tailwind output.

---

## 8. How theme development fits your workflow

### 8.1 Recommended workflow (minimum friction)

1. **Gemini outputs**:

   * layout decisions (header/hero/sections)
   * typography pairing + sizes
   * palette guidance + vibe
2. Build as **Django templates + Tailwind** from the start (avoid a Jinja→Django conversion step if possible).
3. Create “static prototype data” using dummy context in templates.
4. Gradually Wagtailify:

   * replace hardcoded content with context fields / StreamField rendering
   * wire navigation + forms from `sum_core`

This keeps one canonical source of templates (Django), reduces translation churn, and aligns with your platform.

---

## 9. `sum init --theme` behavior spec

### 9.1 CLI interface

Extend `sum init` to accept:

* `--theme <slug>` (required once themes exist)
* `--list-themes` (prints available slugs + names)

### 9.2 Theme resolution order

When resolving `<slug>`, CLI searches:

1. `SUM_THEME_PATH` (dev override): `SUM_THEME_PATH=/path/to/themes/theme_lintel`
2. repo-local canonical: `./themes/theme_<slug>/`
3. bundled themes inside CLI package (optional, later)

If theme cannot be found: fail loudly with a list of available themes.

### 9.3 Copy + wiring behavior

On init:

* Copy selected theme into `clients/<client>/theme/active/`
* Ensure Django template loaders are configured to include:

  * `clients/<client>/theme/active/templates/` first
  * then client overrides
  * then `sum_core` templates last

This guarantees theme templates win, while core remains fallback.

### 9.4 Validation additions (future)

Optionally add to `sum check`:

* confirm `theme/active/theme.json` exists
* confirm template root contains `theme/base.html`

Keep runtime checks cheap—`sum check` is still structural validation, not full rendering. 

---

## 10. Decision matrix for maintainers

When adding a new theme, decide:

### 10.1 Where should logic live?

* If it’s **business logic / content modeling / ops** → `sum_core`
* If it’s **layout / styling / HTML structure** → theme
* If it’s **client-specific quirks** → client overrides

### 10.2 Tailwind vs bespoke CSS?

* Default to Tailwind utilities + components.
* Use bespoke CSS only for:

  * complex animations
  * rare layout hacks not expressible cleanly
  * third-party widget integration

### 10.3 Should this be a “theme feature flag”?

If a component varies meaningfully across themes, keep it in theme partials rather than peppering conditional logic into core templates.

---

## 11. Testing guidance (theme-level)

Given testing risks include branding breakage and template regressions. 
For each theme:

* Maintain a tiny set of “reference pages” for manual smoke:

  * Home, Service, Contact
* Add automated checks later (axe + Lighthouse) once the theme system stabilizes.

---

## 12. Migration plan from token CSS to Tailwind

### 12.1 Minimal-change approach (recommended)

* Keep existing CSS variable injection (branding tags) initially.
* Replace `main.css` token-based styling with Tailwind build output that *consumes* variables.
* Themes introduce Tailwind without requiring immediate deletion of token docs.

### 12.2 “Hard switch” approach (defer)

* Remove token CSS system entirely.
* All styling becomes Tailwind + theme bundles.
  This is cleaner long-term but higher-risk during transition.

