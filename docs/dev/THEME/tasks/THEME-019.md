# THEME-019: Rewrite TestimonialsBlock template (Theme A)

## Branch

- [x] Checkout/create: `theme/theme-019-testimonials-block`
- [x] Verify: `git branch --show-current`

## Context

We’re continuing the “rewrite existing blocks” track. Testimonials are a core, reusable section block and are explicitly defined in `blocks-reference.md` with some non-trivial behavior: dark section styling, mobile horizontal scroll, desktop 3-col grid, optional photo fallback to initials, optional 1–5 rating stars.

This ticket should be _template-only_ (plus theme tests), with minimal churn. Do **not** run any sync tooling (e.g. CLI boilerplate sync) in this branch.

## Objective

Implement Theme A’s override for `TestimonialsBlock` to match the Sage & Stone wireframe:

- Dark-themed section
- Mobile: horizontal scroll (nice touch: snap + optional gradient edge fade)
- Desktop: 3-column grid (up to 12 items)
- Card presentation includes quote, author, optional company, optional photo fallback, optional rating stars
- Preserve accessibility and keep “frame not paint” (tokens/classes, no hardcoded hex).

## Key Files

- `themes/theme_a/templates/sum_core/blocks/testimonials.html` – Theme A override to create/update
- `core/sum_core/templates/sum_core/blocks/testimonials.html` – reference for existing semantics/fallback logic
- `docs/dev/design/wireframes/sage-and-stone/compiled/index.html` – copy the testimonials section markup/classes as baseline (bind fields after)
- `tests/themes/test_theme_a_testimonials_rendering.py` – add theme contract tests

## Acceptance Criteria

- [x] Theme A renders `TestimonialsBlock` using `themes/theme_a/templates/sum_core/blocks/testimonials.html` (verify template origin in test).
- [x] Layout matches wireframe intent:
  - [x] Mobile: overflow-x scroll (cards sized consistently; no broken wrapping)
  - [x] Desktop: 3-column grid
- [x] Field contract respected (no schema changes):
  - [x] `eyebrow` optional
  - [x] `heading` RichText (bold/italic) rendered safely
  - [x] `testimonials` list 1–12
- [x] Child testimonial behavior:
  - [x] Quote renders with safe line breaks (TextBlock)
  - [x] If `photo` missing, show initials fallback derived from `author_name`
  - [x] If `rating` present, render 1–5 stars with an accessible label (e.g. `aria-label="Rated 4 out of 5"`)
- [x] No hardcoded “Sage & Stone” strings, no hardcoded hex colors.
- [ ] Tests pass per `test-strategy-post-mvp-v1.md` and `make test` remains green.
- [x] Diff scope stays tight (no unrelated files touched).

## Steps

1. Branch verification

   - [x] Checkout/create `theme/theme-019-testimonials-block`
   - [x] Confirm with `git branch --show-current`

2. Inspect core template for semantics + fallbacks

   - [x] Open `core/sum_core/templates/sum_core/blocks/testimonials.html`
   - [x] Note: how images are rendered (renditions), and any existing star rendering approach.

3. Extract wireframe markup

   - [ ] From `docs/dev/design/wireframes/sage-and-stone/compiled/index.html`, copy the testimonials section structure/classes into the Theme A template.
   - [ ] Then bind block fields:
     - eyebrow/heading
     - loop through `self.testimonials`

4. Implement Theme A template override

   - [x] Create/update `themes/theme_a/templates/sum_core/blocks/testimonials.html`
   - [x] Implement cards:
     - quote (TextBlock): render with `|linebreaksbr` (or equivalent) so multi-line quotes don’t collapse.
     - author line (name + optional company)
     - photo (if present) else initials fallback
     - rating (if present): render 5 icons, with filled count = rating
   - [x] Mobile scroll:
     - `overflow-x-auto` container
     - consistent card width (`min-w-*`)
     - optional `snap-x snap-mandatory` if it matches wireframe feel
     - optional right-edge gradient fade (same pattern as portfolio) if present in wireframe

5. Add theme rendering tests

   - [x] Add `tests/themes/test_theme_a_testimonials_rendering.py`
   - [x] Assert:
     - template origin is Theme A override
     - eyebrow and heading render (heading via richtext)
     - initials fallback appears when no photo
     - rating markup appears when rating provided (and includes accessible label)

6. Run full validation
   - [x] `pytest -q tests/themes/test_theme_a_testimonials_rendering.py`
   - [ ] `make test`

## Testing Requirements

- [x] Run: `pytest -q tests/themes/test_theme_a_testimonials_rendering.py`
- [ ] Run: `make test`
- [ ] Expected: all green

## Documentation Updates

Update if changes affect:

- [ ] `blocks-reference.md` (not expected; only if you discover mismatch)
- [ ] `page-types-reference.md` (not expected)
- [ ] `WIRING-INVENTORY.md` (not expected)

## Deliverables

- [x] Create `THEME-019_followup.md` (same directory as this ticket) containing:
  - Summary of changes
  - Files modified/created
  - Test results
  - Decisions made / blockers hit
  - Doc updates made (if any)

## Commit & Push

- [ ] Stage: `git add -A`
- [ ] Commit: `feat(THEME-019): rewrite Theme A TestimonialsBlock template`
  - **Must include both** `THEME-019.md` AND `THEME-019_followup.md`
- [ ] Push: `git push origin theme/theme-019-testimonials-block`

## Verification

- [ ] `git status --porcelain` → empty or documented untracked only

---

## Recommended Agent

### Criteria Selection

- **Model:** GPT-5.2 Codex
- **Thinking:** Standard
- **Rationale:** UI/Tailwind-heavy template rewrite with a couple of behavioral edge cases (photo fallback, star rating, mobile scroll). Needs careful, minimal-diff execution and solid theme tests.
