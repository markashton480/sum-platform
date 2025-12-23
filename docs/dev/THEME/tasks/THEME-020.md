# THEME-020: Rewrite Theme A TrustStripLogosBlock template

## Branch

- [ ] Checkout/create: `theme/theme-020-trust-strip-logos-block`
- [ ] Verify: `git branch --show-current`

## Context

We’re continuing the “rewrite existing blocks” push (Category A), staying aligned with `new-theme-plan.md`. TrustStripLogosBlock is used on the showroom HomePage and is a priority block to match Sage & Stone styling. :contentReference[oaicite:4]{index=4} :contentReference[oaicite:5]{index=5}

This block is also a good candidate for color-swap QA (no hardcoded colors; rely on theme tokens / semantic utilities). THEME work should follow the conversion workflow guidance in `THEME-GUIDE.md` (block conversion principles, tokens-first). :contentReference[oaicite:6]{index=6}

## Objective

Implement a Theme A override for `TrustStripLogosBlock` that matches the Sage & Stone compiled wireframe section styling (spacing, typography, logo row, responsive behavior), while:

- keeping everything token/utility driven (no hex),
- supporting optional logo links,
- remaining accessible (alt text, link focus styles),
- and covered by a Theme A rendering test.

## Key Files

- `core/sum_core/templates/sum_core/blocks/trust_strip_logos.html` – core fallback template (reference for context/fields)
- `themes/theme_a/templates/sum_core/blocks/trust_strip_logos.html` – **create/replace** Theme A override
- `docs/dev/design/wireframes/sage-and-stone/compiled/index.html` – reference markup source (trust strip section)
- `docs/dev/blocks-reference.md` – field contract for this block (don’t change fields in this ticket) :contentReference[oaicite:7]{index=7}
- `tests/themes/` – add a rendering test alongside other Theme A block tests
- (Pattern references) `tests/themes/test_theme_a_testimonials_rendering.py`, `tests/themes/test_theme_a_stats_rendering.py` – follow existing conventions

## Acceptance Criteria

- [ ] Theme A override exists at `themes/theme_a/templates/sum_core/blocks/trust_strip_logos.html`
- [ ] Template uses block fields exactly as documented:
  - `eyebrow` optional, `items` required
  - each item renders `logo`, `alt_text`, optional `url` :contentReference[oaicite:8]{index=8}
- [ ] Logos render as a responsive row (mobile wrap/scroll behavior is acceptable if it matches wireframe intent), with consistent sizing and alignment.
- [ ] If `item.url` exists, the logo is wrapped in a link; otherwise it is not.
- [ ] No hardcoded hex colors or inline styles; use Tailwind utilities + theme tokens.
- [ ] Accessibility:
  - valid `alt` text is used from `alt_text`
  - links have visible focus styles (Tailwind defaults or theme patterns)
- [ ] Add a Theme A rendering test proving:
  - template resolution uses Theme A override
  - rendered HTML contains expected marker structure/classes
  - alt text for at least one seeded item appears in output
- [ ] Tests pass per `test-strategy-post-mvp-v1.md` :contentReference[oaicite:9]{index=9}
- [ ] No regressions in existing theme blocks (don’t rebuild unrelated templates)

## Steps

1. Branch + verify branch name.
2. Inspect core contract:
   - Confirm template path and expected context keys for `trust_strip_logos`.
3. Pull reference markup:
   - Use the Sage & Stone compiled `index.html` trust strip section as the structural starting point.
   - Prefer copying the Tailwind structure, then binding to block fields.
4. Implement Theme A override template:
   - Use `{% load wagtailimages_tags %}` and render each logo via `{% image %}` with a sensible rendition (match other theme templates’ approach).
   - Use `alt=item.alt_text`.
   - Wrap in `<a>` when `item.url` is set.
   - Keep styling consistent with existing Theme A section header patterns (eyebrow styling).
5. Tailwind build note:
   - If you only use classes already present in compiled wireframes / existing theme templates, **do not** rebuild CSS.
   - If you introduce genuinely new classes not covered by scanning, rebuild Theme A CSS and commit output.
6. Add test: `tests/themes/test_theme_a_trust_strip_logos_rendering.py`
   - Follow the existing Theme A block rendering tests’ structure.
   - Assert template origin is from `themes/theme_a/...`.
   - Render a seeded homepage (or build a minimal page instance) containing the block and assert expected HTML markers and at least one known alt text.
7. Run tests + lint as required.

## Testing Requirements

- [ ] Run: `pytest -q tests/themes/test_theme_a_trust_strip_logos_rendering.py`
- [ ] Run: `pytest -q tests/themes`
- [ ] Run: `make test`
- [ ] Expected: all green (match CI baseline)

## Documentation Updates

Update if changes affect:

- [ ] `blocks-reference.md` (only if field contract changes — should be **no** for this ticket)
- [ ] `WIRING-INVENTORY.md` (only if template resolution order/paths change — should be **no**)
- [ ] `THEME-GUIDE.md` (only if you introduce a new repeatable pattern worth documenting)

## Deliverables

- [ ] Create `THEME-020_followup.md` (same directory as this ticket) containing:
  - Summary of changes
  - Files modified/created
  - Test results (paste outputs or concise summary)
  - Decisions made / blockers hit
  - Doc updates made (if any)

## Commit & Push

- [ ] Stage: `git add -A`
- [ ] Commit: `feat(THEME-020): rewrite Theme A TrustStripLogosBlock template`
  - **Must include both** `THEME-020.md` AND `THEME-020_followup.md`
- [ ] Push: `git push origin theme/theme-020-trust-strip-logos-block`

## Verification

- [ ] `git status --porcelain` → empty or documented untracked only

## Recommended Agent

- **Criteria Selection**: Standard features (template + tests) / Tailwind markup adherence
- **Model**: GPT-5.2 Codex
- **Thinking**: Standard
- **Rationale**: Reliable multi-file discipline + test hygiene; avoids the “blast radius” issues you hit with Gemini while still handling Tailwind-heavy HTML confidently.
