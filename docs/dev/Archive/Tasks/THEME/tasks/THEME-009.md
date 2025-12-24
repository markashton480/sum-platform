# THEME-009 — Fix Theme A `HeroImageBlock` template to match wireframe (Task 5)

**_ THIS TASK DID NOT RUN!! DIVERTED TO THEME-010 _**

## Mission

Update Theme A’s `HeroImageBlock` template so it matches the homepage hero wireframe spec in `new-theme-plan.md` Task 5.

This is **Theme A template + guardrails** work:

- NO block/model/schema changes
- NO migrations
- Keep core template as fallback only (do not “theme” core)

## Source of truth

- `new-theme-plan.md` → Part 5 → Task 5: Fix HeroImageBlock Template (wireframe lines 317–353)
- `docs/dev/WIRING-INVENTORY.md` → Theme wiring & canonical theme location
- `docs/dev/blocks-reference.md` → HeroImageBlock fields contract (overlay_opacity, floating card fields, etc.)

## Scope

IN SCOPE:

1. Update `themes/theme_a/templates/sum_core/blocks/hero_image.html` to meet the exact requirements in Task 5.
2. Add/adjust a Theme A template test that asserts the required class markers are present (so we can’t drift).
3. Rebuild Theme A compiled CSS and regenerate `.build_fingerprint` (because templates are Tailwind inputs).

OUT OF SCOPE:

- Editing block Python definitions
- Editing `core/sum_core/templates/...` except if you are fixing a _syntax error_ (should be unnecessary)
- Any other block templates (Stats/Portfolio/etc.) — those get their own tickets

## Implementation details

### 1) Update Theme A template (the actual deliverable)

**File:** `themes/theme_a/templates/sum_core/blocks/hero_image.html`

Implement requirements exactly (do not “interpret” them):

#### Layout + background

- Full screen: `h-screen min-h-[700px]`
- Background container: `absolute inset-0`
- Background image: render at `120%` height with `-translate-y-10`
- Overlay: `bg-black/60` (OR map from `self.overlay_opacity`, see below)

#### Content

- Content wrapper: `relative z-10 text-center max-w-5xl mt-20` (centered horizontally)
- Status: `font-accent text-sage-oat text-xl italic`
- Headline: `font-display text-5xl md:text-7xl lg:text-8xl text-sage-linen`
- Subheadline: `text-sage-linen max-w-lg mx-auto text-base md:text-lg`

#### CTAs

- CTA wrapper: `flex flex-col sm:flex-row gap-6`
- Primary CTA: `bg-sage-terra text-white px-12 py-5 uppercase`
- Secondary CTA: `border border-sage-linen/30` and includes an arrow icon

CTA logic:

- Render up to 2 CTAs from `self.ctas`.
- Style via `cta.style` if available; otherwise default first CTA to primary, second to secondary.
- Respect `cta.open_in_new_tab`.

#### Overlay opacity mapping (must respect the block contract)

If `self.overlay_opacity` is present, map:

- none -> `bg-black/0` (or hidden)
- light -> `bg-black/30`
- medium -> `bg-black/60`
- strong -> `bg-black/75`

Default should behave as “medium” if unset.

#### Accessibility

- Always use `self.image_alt` for the hero image alt text.
- Ensure CTAs are real `<a>` elements with sensible focus styles (Tailwind focus ring is fine, but don’t omit focus visibility).

#### Floating card fields (do not break existing contract)

HeroImageBlock has optional `floating_card_label` / `floating_card_value`.

- Keep rendering support for them if they currently exist in the Theme A template.
- If not currently rendered, add a minimal implementation:
  - Only render if BOTH label and value provided
  - Desktop-only (hidden on mobile)
  - Must not break the wireframe layout

(If you add it, keep it visually subordinate and avoid changing the main hero composition.)

### 2) Tests (lock behaviour)

Add or update a test that renders a page with HeroImageBlock and asserts key wireframe markers exist in output HTML:

Must assert presence of:

- `h-screen`
- `min-h-[700px]`
- `bg-black/60` OR the mapped overlay class when overlay_opacity set
- CTA wrapper classes `flex` + `sm:flex-row` + `gap-6`
- Primary CTA token `bg-sage-terra`
- Secondary CTA token `border-sage-linen/30`

Prefer a dedicated test module:

- `tests/themes/test_theme_a_hero_image.py` (or extend an existing Theme A hero test if present)

### 3) Rebuild CSS + fingerprint (required)

Because templates changed, you MUST:

- Rebuild Tailwind CSS for Theme A
- Regenerate `.build_fingerprint`

Commands (from repo root, adjust paths as needed):

```bash
cd themes/theme_a/tailwind
npm ci || npm install
npm run build
cd ..
python build_fingerprint.py
```

### 4) Verification

Automated:

- `make test`

Manual (harness):

- In Wagtail admin (test_project or a client project), add HeroImageBlock
- Fill status, headline (with italic word), subheadline, 2 CTAs, image, alt text
- Confirm: full screen hero, overlay, typography, CTAs, and background image positioning match Task 5.

## Acceptance criteria

- Theme A `hero_image.html` matches `new-theme-plan.md` Task 5 requirements precisely.
- Tests cover the key wireframe class markers and pass.
- Theme A CSS rebuilt and `.build_fingerprint` updated (guardrails satisfied).
- `make test` passes.

## Audit trail / outputs

- Do NOT edit historical task artifacts.
- Create `docs/dev/THEME/tasks/THEME-009_followup.md` describing:

  - files changed
  - test(s) added/updated
  - exact commands run
  - any deviations (should be none)
