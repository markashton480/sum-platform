# THEME-021: Theme A – EditorialHeaderBlock template rewrite

## Branch
- [ ] Checkout/create: `theme/theme-021-editorial-header-block`
- [ ] Verify: `git branch --show-current`

## Context
We’re now into **Phase 2: Content Blocks** from `new-theme-plan.md` (Day 1–2: editorial/content templates). The next “existing block rewrite” in the planned order is **EditorialHeaderBlock** (#10 in Category A). :contentReference[oaicite:0]{index=0}

This block is already seeded into the Showroom and Contact pages, so it’s a high-leverage template: once it matches the Sage & Stone wireframe styling, interior pages start feeling “real” immediately. :contentReference[oaicite:1]{index=1}

Implementation guidance (tokens, semantic colors, and block conversion patterns) lives in `THEME-GUIDE.md` Phase 6. :contentReference[oaicite:2]{index=2}

## Objective
Create a Theme A override for `EditorialHeaderBlock` that matches the Sage & Stone editorial/page header styling, using **semantic theme classes** (no hardcoded client branding) and supporting the block’s `align` option.

## Key Files
- `themes/theme_a/templates/sum_core/blocks/content_editorial_header.html` – **create/replace** the Theme A override for the block template (must mirror the core template path). :contentReference[oaicite:3]{index=3}
- `docs/dev/design/wireframes/sage-and-stone/compiled/blog_article.html` – visual reference for editorial header layout (article header). :contentReference[oaicite:4]{index=4}
- `docs/dev/design/wireframes/sage-and-stone/compiled/terms.html` – visual reference for simple legal page header. :contentReference[oaicite:5]{index=5}
- `docs/dev/blocks-reference.md` – contract for fields (`align`, `eyebrow`, `heading`) and canonical template name. :contentReference[oaicite:6]{index=6}
- `tests/themes/…` (existing theme rendering tests) – follow the established “render + assert key classes/content” pattern (see prior block rendering tests as precedent).

## Acceptance Criteria
- [ ] Theme override exists at: `themes/theme_a/templates/sum_core/blocks/content_editorial_header.html` :contentReference[oaicite:7]{index=7}
- [ ] Output matches Sage & Stone header styling patterns:
  - [ ] Eyebrow (optional): accent/italic treatment; omitted cleanly if empty
  - [ ] Heading: uses `{{ self.heading|richtext }}` and theme typography hierarchy
  - [ ] Spacing/container width consistent with the wireframes (blog article + terms page headers) :contentReference[oaicite:8]{index=8}
- [ ] Alignment behavior:
  - [ ] `align="center"` renders centered header layout
  - [ ] `align="left"` renders left-aligned layout
- [ ] No hardcoded site/client branding strings; color usage is via theme/semantic classes (per `THEME-GUIDE.md` philosophy). :contentReference[oaicite:9]{index=9}
- [ ] Tests added for this block and passing.
- [ ] Tests pass per `test-strategy-post-mvp-v1.md`
- [ ] No regressions in existing functionality

## Steps
1. Verify you’re on the correct branch (`theme/theme-021-editorial-header-block`).
2. Create the Theme A override template:
   - File: `themes/theme_a/templates/sum_core/blocks/content_editorial_header.html` :contentReference[oaicite:10]{index=10}
   - Use the established Theme A structure conventions:
     - Container: `max-w-7xl mx-auto px-6` (or the narrower editorial container if the wireframe calls for it)
     - Spacing: prefer existing “section” conventions rather than inventing one-off padding
     - Eyebrow:
       - Only render if `self.eyebrow` is set
       - Use accent/italic styling consistent with other Theme A headers
     - Heading:
       - Render via `{{ self.heading|richtext }}`
       - Ensure richtext elements inherit the desired typography (no surprise default margins)
     - Alignment:
       - Map `self.align` (`left`/`center`) to wrapper classes (e.g., `text-center` vs `text-left`, and any layout differences)
3. Add a focused theme rendering test:
   - Create: `tests/themes/test_theme_a_editorial_header_rendering.py`
   - Assert:
     - Template resolves from Theme A (origin contains `themes/theme_a/…` or theme templates dir)
     - Eyebrow conditional rendering works
     - Alignment toggles expected classes
     - Heading richtext renders expected markup
4. Quick manual verification (local):
   - Run the showroom seed (if you use it in your flow) and open `/showroom/` and `/contact/` to spot-check the header visually. Showroom includes `editorial_header` by design. :contentReference[oaicite:11]{index=11}
5. Keep changes scoped:
   - No Tailwind config edits unless absolutely required (if required, document why in the followup).

## Testing Requirements
- [ ] Run: `pytest -q tests/themes/test_theme_a_editorial_header_rendering.py`
- [ ] Run: `make test` (or the repo’s standard CI-equivalent test command per `test-strategy-post-mvp-v1.md`)
- [ ] Expected: all green

## Documentation Updates
Update if changes affect:
- [ ] `blocks-reference.md` (only if block contract/template name changes — unlikely here) :contentReference[oaicite:12]{index=12}
- [ ] `page-types-reference.md` (only if page composition changes — unlikely) :contentReference[oaicite:13]{index=13}
- [ ] `WIRING-INVENTORY.md` (only if template resolution order or theme wiring changes — should not) :contentReference[oaicite:14]{index=14}

## Deliverables
- [ ] Create `THEME-021_followup.md` (same directory as this ticket) containing:
  - Summary of changes
  - Files modified/created
  - Test results (copy/paste outputs)
  - Decisions made / blockers hit
  - Doc updates made (if any)

## Commit & Push
- [ ] Stage: `git add -A`
- [ ] Commit: `feat(THEME-021): theme a editorial header block template`
  - **Must include both** `THEME-021.md` AND `THEME-021_followup.md`
- [ ] Push: `git push origin theme/theme-021-editorial-header-block`

## Verification
- [ ] `git status --porcelain` → empty or documented untracked only

---

## Recommended Agent
**Criteria:** Standard feature (template rewrite + focused tests)  
**Selection Model:** GPT-5.1 Codex Max  
**Thinking:** Standard  
**Rationale:** Straightforward block conversion work with test additions; prioritize clean diffs and adherence to existing Theme A patterns.
