# THEME-013 — Fix PortfolioBlock Template (Theme A)

**ID:** THEME-013
**Area:** Theme A templates (homepage)
**Primary source of truth:** `docs/dev/master-docs/new-theme-plan.md` → Task 6 requirements (wireframe lines 527–591)
**Secondary source of truth (block contract):** `PortfolioBlock` + `PortfolioItemBlock` field definitions (code excerpt captured in THEME-004 transcript).

---

### Goal

Rewrite Theme A’s `PortfolioBlock` template so it **matches the wireframe behaviour**:

- Mobile: horizontal scroll carousel with right-edge fade
- Desktop: 3-column grid
- Card image: `aspect-[4/3]`
- Metadata grid: prefers `constraint/material/outcome`, but gracefully falls back to `location/services`
- Hover: image scales to 105%

(Exactly as described in Task 6.)

---

### Important constraints

1. **Theme override only:** Make changes in Theme A template. Do not “fix” this by changing core rendering logic.
2. **No hardcoded branding values:** Use theme classes/tokens (e.g. `text-sage-terra`) — no hex literals.
3. **Preserve the existing block API:** especially `view_all_label` / `view_all_link` which are present in the actual block definition and showroom seed content.
4. **Tests required:** Rendering tests similar to THEME-012 (assert key Tailwind markers + fallback behaviour).

---

### Files to change

1. **Theme A template (main work)**

   - `themes/theme_a/templates/sum_core/blocks/portfolio.html`

2. **New tests**

   - `tests/themes/test_theme_a_portfolio_rendering.py` (new)

3. **Theme artifacts**

   - `themes/theme_a/tailwind/` build output (run `npm run build`)
   - `themes/theme_a/build_fingerprint.py` (regenerate fingerprint)

4. **Docs update (small, targeted)**

   - `docs/dev/blocks-reference.md`: PortfolioBlock fields should include `view_all_link` and `view_all_label` (these exist in code but are missing/unclear in the reference doc). Keep the edit minimal: just adjust the PortfolioBlock field table.

---

### Template requirements (copy/paste into implementation)

Implement these behaviours explicitly:

#### Section + header

- Wrap in `<section>` with the same general spacing conventions as other Theme A blocks (consistent `py-*` rhythm).
- Header must render:

  - `self.eyebrow` as italic accent: `font-accent italic text-sage-terra`
  - `self.heading` richtext (allow `<em>` styling to flow naturally)
  - `self.intro` under heading if present

- If both `view_all_label` and `view_all_link` are present, render a “View all” link aligned to the header (desktop) or below header (mobile). Keep it visually secondary (underlined / border-b style is fine, but don’t invent new branding).

Task 6 doesn’t mention “View all”, but the block contract **does** include it, and the showroom seed uses it.

#### Layout

- **Mobile (default):**

  - Use `flex` + `overflow-x-auto` + spacing between cards.
  - Each card uses `min-w-[85vw]` so it feels like a carousel.
  - Add a **right-edge gradient fade overlay**:

    - Implement as an absolutely positioned overlay div on the container (e.g. `pointer-events-none absolute inset-y-0 right-0 w-16 bg-gradient-to-l ...`).
    - Fade should visually suggest “more content” without blocking scrolling.

- **Desktop (`md:`):**

  - Switch to `md:grid md:grid-cols-3` and remove the forced min-width behaviour.

#### Card

Each item card should include:

- Image area:

  - `aspect-[4/3]`
  - `overflow-hidden` so hover scale stays clipped
  - Hover: `group-hover:scale-105 transition-transform duration-500` on the `<img>`

- Title (`item.title`) prominently (but not absurdly large).
- Metadata area:

  - If _any_ of `constraint/material/outcome` are present, render them in a `grid grid-cols-2` pattern (you may need to decide how to handle 3 values in 2 cols: e.g. two on first row + one spanning 2 cols, or allow wrapping).
  - If **none** of those are present, fall back to showing `location` and `services` (still in a tidy grid).

- Linking:

  - If `item.link_url` exists, card should link (either wrap whole card with `<a>` or provide a clear CTA).
  - If no link, render as non-clickable content (no fake hrefs).

Block fields available on items (confirm you’re using these exact names): `image`, `alt_text`, `title`, `location`, `services`, `constraint`, `material`, `outcome`, `link_url`.

---

### Tests

Create `tests/themes/test_theme_a_portfolio_rendering.py` with tests that:

1. **Markers test (structure/classes)**

   - Render the block and assert presence of:

     - `overflow-x-auto` (mobile behaviour marker)
     - `min-w-[85vw]` (carousel card width marker)
     - `md:grid-cols-3` (desktop marker)
     - `aspect-[4/3]` (image marker)
     - `group-hover:scale-105` or equivalent (hover marker)

2. **Metadata fallback test**

   - Case A: item has constraint/material/outcome → assert those labels/values appear
   - Case B: item lacks all three → assert location/services appear instead

3. **View-all conditional test**

   - If both `view_all_label` and `view_all_link` are present → renders link
   - If one missing → does not render partial UI

Pattern it after THEME-012’s “rendering tests with Tailwind markers + logic assertions”.

---

### Build + fingerprint

After updating the template:

- `cd themes/theme_a/tailwind && npm run build`
- `python themes/theme_a/build_fingerprint.py` (or whatever the documented invocation is in-repo)
- Commit updated outputs + new fingerprint hash.

(Exactly like THEME-012 did.)

---

### Acceptance checklist

- [ ] Portfolio block visually matches wireframe intent (lines 527–591): mobile carousel + fade, desktop 3-col, hover zoom.
- [ ] New metadata fields display when present; fallback works when not.
- [ ] No hardcoded hex colours introduced.
- [ ] `pytest tests/themes/test_theme_a_portfolio_rendering.py` passes.
- [ ] `make test` passes.
- [ ] Theme CSS rebuilt and fingerprint updated.
- [ ] `docs/dev/blocks-reference.md` updated _minimally_ to reflect `view_all_link` / `view_all_label` on PortfolioBlock (so the docs match reality).
