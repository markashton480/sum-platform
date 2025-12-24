# THEME-012 — Rewrite Theme A HeroImageBlock template to match wireframe (Task 5)

### Mission

Rewrite **Theme A**’s `HeroImageBlock` template so it matches `new-theme-plan.md` Task 5 / wireframe lines 317–353, including overlay opacity behaviour and CTA styling.

### Source of truth

- `new-theme-plan.md` → Task 5 requirements (exact class/layout requirements)
- `docs/dev/blocks-reference.md` → HeroImageBlock fields + overlay/floating card contract
- `docs/dev/WIRING-INVENTORY.md` → theme template location and resolution order

### Scope

**In scope**

1. Rewrite Theme A template: `themes/theme_a/templates/sum_core/blocks/hero_image.html`
2. Update/add tests to lock in the wireframe markers + overlay mapping.
3. Rebuild Theme A CSS + regenerate `.build_fingerprint` (template changes are Tailwind inputs).

**Out of scope**

- No block/schema/model changes (no migrations).
- No changes to core fallback template except fixing a _syntax error_ if discovered.
- No other block templates.

---

## Implementation requirements

### 1) Template rewrite

**File:** `themes/theme_a/templates/sum_core/blocks/hero_image.html`

Implement the requirements **exactly** as stated in the plan:

- Full screen: `h-screen min-h-[700px]`
- Background container: `absolute inset-0`
- Background image: `h-[120%] -translate-y-10` + `object-cover w-full`
- Overlay: `bg-black/60` **or mapped from** `self.overlay_opacity` (see below)
- Content wrapper: `relative z-10 text-center max-w-5xl mt-20`
- Status: `font-accent text-sage-oat text-xl italic`
- Headline: `font-display text-5xl md:text-7xl lg:text-8xl text-sage-linen`
- Subheadline: `text-sage-linen max-w-lg mx-auto text-base md:text-lg`
- CTAs wrapper: `flex flex-col sm:flex-row gap-6`
- Primary CTA: `bg-sage-terra text-white px-12 py-5 uppercase`
- Secondary CTA: `border border-sage-linen/30` **with arrow icon**

**Overlay opacity mapping (must respect block contract):**
HeroImageBlock contract includes `overlay_opacity` options: `none/light/medium/strong`, default `medium`.
Map to:

- `none` → `bg-black/0`
- `light` → `bg-black/30`
- `medium` → `bg-black/60`
- `strong` → `bg-black/75`

### 2) CTA logic and constraints

HeroImageBlock `ctas` is a list with max 2.

Rules:

- Render at most 2 CTAs.
- If a CTA has a `style` field, respect it.
- If style is absent, treat CTA[0] as primary and CTA[1] as secondary.
- Respect `open_in_new_tab` (`target="_blank"` + `rel="noopener noreferrer"`).

### 3) Accessibility requirements

- Background image must use `self.image_alt` for alt text (it’s required).
- Ensure focus styles are visible on both CTAs.
- Don’t hide text behind overlays for screen readers (normal DOM order is fine).

### 4) Floating card support (do not break existing field contract)

HeroImageBlock has optional:

- `floating_card_label`
- `floating_card_value`

Rules:

- Render only if **both** are present.
- Desktop-only (hidden on mobile).
- Must not disrupt the wireframe layout (treat it as a positioned accessory element).

---

## Tests (guardrails)

Add/update tests so we don’t drift again.

Minimum test coverage:

1. **Wireframe marker test**: render hero block and assert HTML contains:

   - `h-screen`
   - `min-h-[700px]`
   - CTA wrapper `sm:flex-row gap-6`
   - primary CTA token `bg-sage-terra`
   - secondary CTA token `border-sage-linen/30`

2. **Overlay mapping test** (parameterized): for each `overlay_opacity` value, assert correct overlay class appears.

3. **Floating card conditional**: ensure it renders only when both label+value exist.

(Use the existing Theme A test pattern already in the suite—don’t invent a new harness.)

---

## Rebuild Theme A CSS + fingerprint (required)

Because this is a template rewrite:

- rebuild Tailwind output and regenerate `.build_fingerprint`
- commit `themes/theme_a/static/theme_a/css/main.css` and `.build_fingerprint`

Follow the established Theme A maintainer workflow.

---

## Manual verification

In Wagtail admin (test_project or a client project using Theme A):

- Add a **HeroImageBlock** with:

  - status text
  - headline with italic word
  - subheadline
  - 2 CTAs
  - background image + alt
  - try overlay_opacity values

Expected: full-screen hero, centered text, 2 buttons styled as per plan, overlay behaves exactly as mapping above, matches wireframe 317–353.

---

## Acceptance criteria

- Theme A `hero_image.html` matches Task 5 requirements exactly.
- Overlay opacity mapping correct and tested.
- CTA rules correct (max 2, style respected, new-tab safe).
- Floating card renders correctly when both fields present.
- Theme A CSS rebuilt + fingerprint updated.
- `make test` passes.

---

## Guardrails

- Do not edit historical task artifacts.
- Create only:
  - `docs/dev/THEME/tasks/THEME-012_followup.md`
  - plus the code/tests/CSS build artifacts required.
