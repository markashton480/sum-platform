# Tailwind Hardcoded Values Investigation Report

**Date**: 2025-12-20  
**Author**: Claude (AI Agent)  
**Status**: ⚠️ CRITICAL ARCHITECTURE GAP IDENTIFIED  
**Severity**: High – Affects core theming capability promise from original design system

---

## Executive Summary

The transition from vanilla CSS to Tailwind CSS in Theme A has introduced a **fundamental break in the dynamic branding contract**. While the Tailwind configuration _does_ reference CSS variables for colour values, the **SiteSettings branding integration outputs different CSS variable names** (`--brand-h`, `--brand-s`, `--brand-l`) than those consumed by Theme A (`--color-sage-terra`, `--color-sage-black`, etc.).

**Bottom Line**: Changing colours in Wagtail SiteSettings will **NOT** affect Theme A's appearance. The values are effectively hardcoded via a naming mismatch.

---

## Detailed Findings

### 1. Original Design System Contract (Pre-Theme A)

The original CSS design system (`core/sum_core/static/sum_core/css/tokens.css`) was built around Wagtail-injectable design tokens:

```css
/* Original tokens.css approach */
:root {
  --brand-h: 30; /* Injected via {% branding_css %} from SiteSettings */
  --brand-s: 40%;
  --brand-l: 35%;

  /* Derived palette - calculated from brand values */
  --primary: var(--brand-h), var(--brand-s), var(--brand-l);
}

/* Components used: */
background-color: hsla(var(--primary), 1);
```

**How it worked:**

1. SiteSettings stores `primary_color` as hex (e.g., `#A0563B`)
2. `{% branding_css %}` template tag converts hex → HSL and injects:
   - `--brand-h: 160;`
   - `--brand-s: 46%;`
   - `--brand-l: 43%;`
3. CSS variables cascade and all components update automatically

### 2. Theme A Tailwind Configuration

The Theme A `tailwind.config.js` does use CSS variables, but with **theme-specific names**:

```javascript
// themes/theme_a/tailwind/tailwind.config.js
colors: {
  'sage': {
    'black': 'rgb(var(--color-sage-black, 26 47 35) / <alpha-value>)',
    'terra': 'rgb(var(--color-sage-terra, 160 86 59) / <alpha-value>)',
    'moss':  'rgb(var(--color-sage-moss, 85 111 97) / <alpha-value>)',
    // ... etc
  },
  'primary':   'rgb(var(--color-primary, 160 86 59) / <alpha-value>)',
  'secondary': 'rgb(var(--color-secondary, 85 111 97) / <alpha-value>)',
  'accent':    'rgb(var(--color-accent, 160 86 59) / <alpha-value>)',
}
```

The CSS variable defaults are also defined in `input.css`:

```css
/* themes/theme_a/static/theme_a/css/input.css */
:root {
  --color-sage-black: 26 47 35; /* #1A2F23 */
  --color-sage-terra: 160 86 59; /* #A0563B */
  --color-sage-moss: 85 111 97; /* #556F61 */
  /* ... */

  /* Semantic aliases */
  --color-primary: 160 86 59;
  --color-secondary: 85 111 97;
  --color-accent: 160 86 59;
}
```

### 3. What `{% branding_css %}` Actually Outputs

The branding template tag (`core/sum_core/branding/templatetags/branding_tags.py`) generates:

```css
:root {
  --brand-h: 160; /* From SiteSettings.primary_color hex → HSL */
  --brand-s: 46%;
  --brand-l: 43%;
  --color-secondary-custom: #556f61; /* If secondary_color set */
  --color-accent-custom: #a0563b; /* If accent_color set */
  --accent-h: ...; /* If accent_color set */
  --font-heading: "Playfair Display", system-ui, ...;
  --font-body: "Lato", system-ui, ...;
}
```

### 4. The Mismatch

| What Theme A Expects | What SiteSettings Provides | Result                              |
| -------------------- | -------------------------- | ----------------------------------- |
| `--color-sage-terra` | (nothing)                  | Falls back to hardcoded `160 86 59` |
| `--color-sage-black` | (nothing)                  | Falls back to hardcoded `26 47 35`  |
| `--color-primary`    | (nothing)                  | Falls back to hardcoded `160 86 59` |
| `--color-secondary`  | (nothing)                  | Falls back to hardcoded `85 111 97` |
| (not used)           | `--brand-h: xx;`           | Ignored – nothing consumes it       |
| (not used)           | `--color-secondary-custom` | Ignored – wrong name                |

**The branding_css tag and Theme A CSS variables speak completely different dialects.**

### 5. Evidence in Compiled CSS

The compiled `main.css` (minified, ~71KB) confirms the hardcoded fallback values are baked in:

```css
:root {
  --color-sage-black: 26 47 35;
  --color-sage-linen: 247 245 241;
  --color-sage-terra: 160 86 59;
  --color-primary: 160 86 59;
  /* etc. */
}
```

And all generated utility classes use these:

```css
.bg-sage-terra {
  --tw-bg-opacity: 1;
  background-color: rgb(
    var(--color-sage-terra, 160 86 59) / var(--tw-bg-opacity, 1)
  );
}
```

### 6. Hardcoded Values in Templates & CSS

Beyond the CSS variable mismatch, there are also **literal hardcoded hex values** in `input.css`:

```css
/* input.css - Section 2: Base Layer */
body {
  background-color: #f7f5f1; /* ← Hardcoded! */
  color: #1a2f23; /* ← Hardcoded! */
}

::-webkit-scrollbar-thumb {
  background: #e3ded4; /* ← Hardcoded! */
}

/* Section 12: Accessibility */
a:focus-visible {
  outline: 3px solid #a0563b; /* ← Hardcoded! */
  border-color: #a0563b;
}
```

These will **never** respond to SiteSettings changes.

### 7. Scope of Impact

| Component                | Uses CSS Variables?                 | Will Update from SiteSettings?            |
| ------------------------ | ----------------------------------- | ----------------------------------------- |
| `.bg-sage-terra` buttons | ✅ Yes (`--color-sage-terra`)       | ❌ **No** – wrong variable name           |
| `.text-sage-black`       | ✅ Yes (`--color-sage-black`)       | ❌ **No** – wrong variable name           |
| `body` background        | ❌ No (hardcoded `#F7F5F1`)         | ❌ **No**                                 |
| Focus outlines           | ❌ No (hardcoded `#A0563B`)         | ❌ **No**                                 |
| Hero gradients           | ✅ Yes (`--color-primary`)          | ❌ **No** – SiteSettings doesn't set this |
| Fonts                    | ✅ Yes (via `{% branding_fonts %}`) | ✅ **Yes** – this still works!            |

---

## Comparison with THEME-ARCHITECTURE-SPECv1

The spec explicitly anticipated this issue and recommended a hybrid approach (Section 7.1):

> **Recommendation (best of both worlds):**
>
> - Tailwind for structure, spacing, typography scale, layout, component composition.
> - **CSS variables for brand "slots"** (colour surfaces/text/accents), so a theme can be re-skinned without rewriting Tailwind classes.

And Section 7.2:

> **Brand preset** (optional) = initial CSS variable values (fonts/colours) **still editable in SiteSettings if you want**. The platform already injects branding vars via tags today.

**Current Implementation**: Theme A violates this contract. It is effectively "hardcoded at Tailwind build time" rather than "reskinnable at runtime".

---

## Root Cause Analysis

1. **Naming divergence**: The Theme A developer created new variable names (`--color-sage-*`) instead of consuming the existing branding system's outputs (`--brand-h/s/l`, `--primary`, etc.).

2. **No bridging layer**: There's no CSS that maps branding outputs to Theme A inputs, e.g.:

   ```css
   :root {
     --color-primary: var(--brand-h) var(--brand-s) var(--brand-l);
   }
   ```

3. **HSL vs RGB format difference**: Branding outputs HSL components (`--brand-h: 160`), but Theme A expects RGB triplets (`--color-sage-terra: 160 86 59`). These are fundamentally incompatible without conversion.

4. **Compiled CSS isolation**: Since `main.css` is pre-compiled by Tailwind (no Node.js at runtime), the only way to inject branding is via CSS variable cascade – but the names don't match.

---

## Recommendations

### Option A: Extend `branding_css` to Output Theme A Variables _(Quick Fix)_

Modify `_build_css_variables()` in `branding_tags.py` to also emit the Theme A variable names:

```python
def _build_css_variables(site_settings: SiteSettings) -> list[str]:
    variables = []

    if site_settings.primary_color:
        rgb = _hex_to_rgb(site_settings.primary_color)  # New helper
        if rgb:
            r, g, b = rgb
            variables.extend([
                # Existing HSL for legacy token system
                f"    --brand-h: {hue};",
                f"    --brand-s: {saturation}%;",
                f"    --brand-l: {lightness}%;",

                # NEW: Theme A RGB format
                f"    --color-primary: {r} {g} {b};",
                f"    --color-sage-terra: {r} {g} {b};",  # If terra = primary
            ])
```

**Pros**: Non-breaking, no Tailwind rebuild needed  
**Cons**: Couples branding tag to specific theme; naming feels hacky

### Option B: Define a Theme A "Branding Bridge" Partial _(Cleaner)_

Create a CSS file in Theme A that maps branding outputs to theme inputs:

```css
/* themes/theme_a/static/theme_a/css/branding-bridge.css */
:root {
  /* Map legacy branding HSL to Theme A RGB format */
  /* This requires JavaScript or server-side conversion – HSL != RGB */
}
```

**Problem**: CSS can't convert HSL to RGB. This would require either:

- Server-side rendering of the bridge CSS, or
- JavaScript at runtime

### Option C: Redesign Theme A to Use HSL Variables _(Breaking Change)_

Refactor Theme A's Tailwind config and templates to use HSL-based colour functions:

```javascript
// tailwind.config.js (hypothetical)
colors: {
  'primary': 'hsl(var(--brand-h), var(--brand-s), var(--brand-l))',
}
```

**Problem**: Tailwind's opacity modifiers (`bg-primary/50`) don't work with `hsl()` – they require the `rgb(... / <alpha-value>)` format.

### Option D: Accept Fixed Themes, Document Limitation _(Pragmatic)_

Per the spec (Section 2 Non-goals):

> - No Wagtail-admin theme switching.

If themes are truly "fixed at init-time", then dynamic SiteSettings branding is arguably out of scope. Document this clearly:

> ⚠️ Theme A colours are fixed. To change the palette, edit `themes/theme_a/static/theme_a/css/input.css` and rebuild with `npm run build`.

---

## Recommended Path Forward

Given the THEME-ARCHITECTURE-SPECv1's intent to support **brand presets editable in SiteSettings**, I recommend:

1. **Immediate (this sprint)**: Add a warning to Theme A README documenting that colours require CSS rebuild to change.

2. **Short-term (next milestone)**: Implement **Option A** with a generalised approach:

   - Add new SiteSettings fields for the theme's colour slots (e.g., `cta_color`, `text_color_dark`)
   - Have `branding_css` output these as `--color-primary`, `--color-sage-terra`, etc.
   - Use RGB format to maintain Tailwind compatibility

3. **Long-term (Theme v2)**: Design a proper theme ↔ branding interface:
   - Each theme declares which "slots" it exposes (in `theme.json`)
   - SiteSettings UI dynamically shows controls for those slots
   - Branding tag outputs the correct variables for the active theme

---

## Files Examined

| File                                                   | Relevance                                 |
| ------------------------------------------------------ | ----------------------------------------- |
| `themes/theme_a/tailwind/tailwind.config.js`           | Tailwind colour definitions               |
| `themes/theme_a/static/theme_a/css/input.css`          | CSS variable defaults, hardcoded values   |
| `themes/theme_a/static/theme_a/css/main.css`           | Compiled output (confirms hardcoding)     |
| `themes/theme_a/templates/theme/base.html`             | Loads `{% branding_css %}` AFTER main.css |
| `core/sum_core/branding/templatetags/branding_tags.py` | What SiteSettings actually outputs        |
| `core/sum_core/branding/models.py`                     | SiteSettings fields available             |
| `core/sum_core/static/sum_core/css/tokens.css`         | Original (working) token system           |
| `docs/dev/master-docs/THEME-ARCHITECTURE-SPECv1.md`    | Intended architecture                     |

---

## Conclusion

The theme system's promise of **"Tailwind-first with CSS variables for brand slots"** is **not yet implemented**. Theme A uses CSS variables internally, but those variables are not connected to SiteSettings. The result is a theme that looks great but cannot be rebranded through the Wagtail admin.

This is a fixable architectural gap, not a fundamental design flaw. The wiring is 90% there; it just needs the final bridge between `branding_css` output and Theme A's colour inputs.

---

_Report generated by Claude following investigation request._
