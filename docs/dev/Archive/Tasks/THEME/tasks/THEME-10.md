# THEME-010 — Branding contract bridge for Theme A (SiteSettings actually changes Theme A colours + fonts)

## Mission

Make **Theme A** consume the **existing branding contract** provided by `SiteSettings` via `{% branding_css %}` / `{% branding_fonts %}`, so:

- changing SiteSettings _actually_ changes Theme A (at runtime, no Tailwind rebuild),
- Theme A stops relying on its private `--color-sage-*` / `--color-primary` RGB dialect,
- and we remove the remaining literal hardcoded hex values that bypass branding.

This is the foundation fix identified in the investigation: Theme A currently expects `--color-sage-*` + RGB triplets, but branding outputs `--brand-h/s/l` + “\*-custom” vars, so SiteSettings is effectively ignored.

## Source of truth

- **Branding contract + tokens rules (legacy system, still authoritative for SiteSettings outputs):** `docs/dev/design/css-architecture-and-tokens.md`
- **Theme system expectation: Tailwind-first, but brand slots via CSS vars:** `docs/dev/master-docs/THEME-ARCHITECTURE-SPECv1.md` §7.1
- **Current mismatch report:** `tailwind-hardcoded-values-claude.md`
- **Theme A current palette + font hardcoding:** THEME-005 theme notes / config snippets
- **Template wiring contract:** `WIRING-INVENTORY.md` Theme wiring + branding section

## Scope

### In scope

1. **Inventory & confirm** exactly what variables `{% branding_css %}` currently outputs (don’t assume).
2. Update Theme A Tailwind config to consume **branding-provided variables** (HSL-based) in a way that still supports Tailwind opacity modifiers (using `<alpha-value>`). ([tailwind-search.barvian.me][1])
3. Update Theme A fonts to consume `--font-heading` / `--font-body` variables (instead of hardcoded font stacks).
4. Remove/replace the remaining **literal hex** values in Theme A `input.css` that bypass the branding system.
5. Add tests/guardrails to prevent this drifting back.
6. Rebuild Theme A compiled CSS and update `.build_fingerprint`.

### Out of scope

- No template rewrites / wireframe matching (that starts immediately after this ticket).
- No new blocks / migrations.
- No audit trail rewrites.

## Required approach (no hacks, no coupling core to Theme A)

We do **not** add Theme-A-specific variable names to `branding_css` (e.g. no emitting `--color-sage-terra`). That would couple core to a theme and becomes a maintenance trap.

Instead:

- Theme A must consume the variables branding already emits (or extend branding in a **semantic, theme-agnostic** way if genuinely missing).

## Implementation steps

### 0) Inventory what branding emits (mandatory first step)

Locate and inspect:

- `core/sum_core/branding/templatetags/branding_tags.py` (or wherever `{% branding_css %}` is implemented)
- The generated CSS variable list in that tag

In the follow-up report, include:

- the list of variables emitted for **primary**, **secondary**, **accent**, **background**, **text**, **surface** (whatever exists),
- and their formats (HSL components, hex, strings, etc.).

### 1) Update Theme A Tailwind colours to consume branding HSL variables

**File:** `themes/theme_a/tailwind/tailwind.config.js`

Replace Theme A’s current RGB mapping (e.g. `rgb(var(--color-sage-terra, ...) / <alpha-value>)`)
with HSL mappings driven by branding variables.

**⚠️ CRITICAL: HSL + Tailwind Opacity Modifier Compatibility**

Tailwind's `<alpha-value>` interpolation works best with **space-separated colour channels**. The current branding outputs HSL as separate vars (`--brand-h: 160; --brand-s: 46%; --brand-l: 43%;`), which requires a specific format:

```javascript
// In tailwind.config.js colors:
'primary': 'hsl(var(--brand-h) var(--brand-s) var(--brand-l) / <alpha-value>)',
```

**Note:** This syntax (`hsl(h s l / a)`) requires modern CSS (Space-separated HSL). If browser support issues arise, alternatives include:

- Using `hsla()` with fallback: `hsla(var(--brand-h), var(--brand-s), var(--brand-l), <alpha-value>)` (but this may not interpolate correctly)
- Updating branding to output a single HSL triplet variable (e.g., `--brand-hsl: 160 46% 43%`)

**Hard requirements:**

- Must use modern space-separated HSL syntax with `<alpha-value>` so opacity modifiers work
- Keep existing class names used by the plan/templates (`sage-terra`, `sage-moss`, `sage-linen`, etc.) as **aliases** so we don't need to rewrite everything twice

**Minimum mapping target (must be dynamic after this ticket):**

- `sage-terra` + `primary` → SiteSettings **primary colour** (`--brand-h/s/l`)
- `secondary` (and preferably `sage-moss`) → SiteSettings **secondary colour** (need `--secondary-h/s/l`)
- `accent` → SiteSettings **accent colour** (`--accent-h/s/l` partially exists per investigation)

**Known current branding output (from investigation):**

```css
:root {
  --brand-h: 160; /* primary HSL hue */
  --brand-s: 46%; /* primary HSL saturation */
  --brand-l: 43%; /* primary HSL lightness */
  --color-secondary-custom: #556f61; /* secondary as HEX (not usable!) */
  --color-accent-custom: #a0563b; /* accent as HEX (not usable!) */
  --accent-h: 160; /* accent HSL hue (exists!) */
  --accent-s: 46%; /* accent HSL sat (exists!) */
  --accent-l: 43%; /* accent HSL light (exists!) */
  --font-heading: "Playfair Display", ...; /* heading font (works!) */
  --font-body: "Lato", ...; /* body font (works!) */
}
```

**Gap:** Secondary colour has no HSL output – only hex. This must be fixed in step 2.

**🎨 Design Decision: Which colours should be dynamic?**

Not all Theme A colours should be branding-driven. The theme has an identity (Sage & Stone) that includes fixed neutrals:

| Colour                    | Should be dynamic? | Reason                                   |
| ------------------------- | ------------------ | ---------------------------------------- |
| `sage-terra` / `primary`  | ✅ **Yes**         | CTA buttons, accents – core brand colour |
| `sage-moss` / `secondary` | ✅ **Yes**         | Secondary accents, links                 |
| `accent`                  | ✅ **Yes**         | Tertiary emphasis                        |
| `sage-linen` (background) | ⚠️ **Optional**    | Could remain theme-fixed as "warm white" |
| `sage-oat` (surface)      | ⚠️ **Optional**    | Could remain theme-fixed                 |
| `sage-black` (text)       | ⚠️ **Optional**    | Could remain theme-fixed as "near-black" |
| `sage-stone` (muted)      | ❌ **No**          | Purely decorative neutral                |

**Recommendation:** Focus on making `primary`, `secondary`, and `accent` dynamic. The neutrals (linen, oat, stone, black) can remain as fixed defaults that define the theme's "warm organic" feel. This matches real-world branding where clients change their brand colours but keep a consistent neutral palette.

If branding does **not** currently emit HSL components for secondary/background/text/surface, you must **extend branding output semantically** (next step).

### 2) If needed: extend branding output _semantically_ (theme-agnostic, additive)

Only do this if step (0) confirms the necessary semantic values do not exist in HSL-component form.

Update `{% branding_css %}` to emit additional **semantic** HSL component variables (not Theme A names), for example:

- `--secondary-h`, `--secondary-s`, `--secondary-l`
- `--accent-h`, `--accent-s`, `--accent-l`
- `--background-h`, `--background-s`, `--background-l`
- `--text-h`, `--text-s`, `--text-l`
- `--surface-h`, `--surface-s`, `--surface-l`

Rules:

- Additive only — do not remove or rename existing variables (`--brand-h/s/l` etc.).
- Derive them from existing SiteSettings fields (hex → HSL conversion is already done for primary per the investigation).
- Write unit tests for this output (see Tests section).

### 3) Update Theme A Tailwind fonts to consume branding font variables

**File:** `themes/theme_a/tailwind/tailwind.config.js`

Replace hardcoded font stacks like:

- `Playfair Display`, `Lato`, etc.

With CSS variable driven families:

- `display` → `var(--font-heading)`
- `body` → `var(--font-body)`
- `accent` → prefer `var(--font-accent, var(--font-heading))` if you have an accent font var; otherwise just use heading or body consistently.

This aligns with the branding system’s “fonts come from branding\_\* tags”.

### 4) Remove literal hex values in Theme A input.css (must not bypass branding)

**File:** `themes/theme_a/static/theme_a/css/input.css`

Claude identified literal hex usage for:

- body background/text
- focus outline
- scrollbar thumb

Replace these with variable-driven values consistent with the branding contract:

- use HSL vars and `hsl()` / `hsla()` (preferred given branding is HSL-driven), OR
- use existing semantic vars if already available.

**Goal:** after this ticket, Theme A should have **no literal `#xxxxxx`** in its base layer for brand-driven surfaces/text/focus.

### 5) Ensure theme base template includes branding hook points (quick confirm)

Confirm Theme A base template still loads:

- `{% branding_fonts %}`
- `{% branding_css %}`
  in the canonical theme tree (`themes/theme_a/templates/theme/base.html`).

(You don’t need to change ordering unless it’s broken; later injected `:root` is fine.)

### 6) Tests (non-negotiable guardrails)

Add/extend tests so this doesn’t regress:

1. **Branding output test**

   - Given SiteSettings with known hex colours, render `{% branding_css %}` and assert it contains:

     - `--brand-h/s/l` (existing)
     - any new semantic vars you added (secondary/accent/background/text/surface) in the format Theme A expects.

2. **Theme A tailwind contract test**

   - Assert `themes/theme_a/tailwind/tailwind.config.js` references branding vars (e.g. contains `--brand-h` and uses `hsl(` with `<alpha-value>`). ([tailwind-search.barvian.me][1])

3. **Theme A CSS hardcode test**

   - Assert `themes/theme_a/static/theme_a/css/input.css` contains **no** hex literals matching `#` patterns (or at least none for the known problematic ones).
   - Known offenders to check: `#F7F5F1` (linen), `#1A2F23` (black), `#E3DED4` (oat), `#A0563B` (terra in focus), `#8F8D88` (stone).

### 7) Rebuild Theme A CSS + fingerprint (required)

Because tailwind config + input.css change:

- rebuild compiled CSS
- regenerate `.build_fingerprint`

Use the documented workflow in Theme A maintainer notes.

## Manual verification

1. Set SiteSettings **primary** to an obvious colour (e.g. bright red), **secondary** to a different colour, **accent** to another.
2. Load a page using Theme A where you can see:

   - primary buttons (`bg-sage-terra` in plan templates like Featured Case Study / Hero)
   - secondary accents (if used)
   - focus outlines

3. Confirm UI changes **without rebuilding Tailwind** after changing SiteSettings.

## Acceptance criteria

- Theme A primary colour utilities are driven by SiteSettings branding vars (not hardcoded fallbacks).
- Theme A fonts are driven by branding font vars (`--font-heading`, `--font-body`).
- No literal hex values remain in Theme A `input.css` for brand-driven surfaces/text/focus.
- Tests added and passing.
- Theme A CSS rebuilt and `.build_fingerprint` updated.

## Known Risks

| Risk                                                       | Mitigation                                                               |
| ---------------------------------------------------------- | ------------------------------------------------------------------------ |
| HSL space-separated syntax not supported in older browsers | Modern browsers (2020+) support it. If issue, add PostCSS fallback.      |
| Opacity modifiers may not work with `hsla()` comma syntax  | Use space-separated HSL: `hsl(h s l / a)` which Tailwind can interpolate |
| Secondary colour currently outputs hex only, not HSL       | Step 2 explicitly addresses this by extending branding output            |
| Removing hardcoded hex may break unknown dependencies      | Tests + manual verification will catch; changes are scoped to input.css  |
| Tailwind rebuild required after config change              | Expected; fingerprint update handles this                                |

## Audit trail guardrails

- Do **not** modify any historical task docs, transcripts, or follow-ups.
- Create only:

  - `docs/dev/THEME/tasks/THEME-010_followup.md` (work report)
  - plus code changes needed for this mission.

---
