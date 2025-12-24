# THEME-029: Rewrite Theme A ImageBlock template (captioned images + full width)

## Branch
- [ ] Checkout/create: `theme/theme-029-image-block`
- [ ] Verify: `git branch --show-current`

## Context
Continuing the “rewrite existing blocks” track (Phase 2: content/editorial). ImageBlock is high-impact across blog/legal/content pages. This is a contained template rewrite + theme test.

Important: CI requires theme assets to be current, so if this ticket causes `main.css`/`.build_fingerprint` changes, they must be **regenerated after rebasing onto origin/develop** and committed as the final commit on the branch.

## Objective
Create/replace Theme A’s override for `ImageBlock`:
- semantic `<figure>` structure
- optional caption rendering
- `full_width` layout variant support
- reveal hooks (progressive enhancement)
- add a focused theme rendering test

## Key Files
- `themes/theme_a/templates/sum_core/blocks/content_image.html` – Theme A override (create/replace)
- `core/sum_core/templates/sum_core/blocks/content_image.html` – core fallback reference
- `docs/dev/design/wireframes/sage-and-stone/compiled/blog_article.html` – markup reference for editorial images
- `tests/themes/test_theme_a_image_block_rendering.py` – new test file (unique)

## Acceptance Criteria
- [ ] Preflight run at start (`/prompts:sum-preflight TICKET_ID=THEME-029` or `make preflight`)
- [ ] Theme override exists at `themes/theme_a/templates/sum_core/blocks/content_image.html`
- [ ] Semantic output:
  - [ ] `<figure>` wraps image + optional `<figcaption>`
  - [ ] `alt` uses `self.alt_text` (or equivalent contract field)
  - [ ] caption renders only if provided
- [ ] `full_width` variant:
  - [ ] full width uses wider/bleed layout compared to standard prose container
  - [ ] non-full width respects editorial max width
- [ ] Reveal hooks included; content visible by default
- [ ] Theme rendering test added and passing
- [ ] `make test` passes
- [ ] If CSS/fingerprint outputs change, they are:
  - [ ] regenerated after a rebase onto `origin/develop`
  - [ ] committed as the final commit on the branch

## Steps
1. Branch verification
   - [ ] Checkout/create `theme/theme-029-image-block`
   - [ ] Verify branch: `git branch --show-current`
   - [ ] Run preflight: `/prompts:sum-preflight TICKET_ID=THEME-029` (or `make preflight`)

2. Implement Theme A override template
   - [ ] Create/update `themes/theme_a/templates/sum_core/blocks/content_image.html`
   - [ ] Use Wagtail image rendering (`{% image %}`) consistent with other Theme A templates
   - [ ] Implement wrapper + width logic:
     - `full_width`: allow wider container / bleed
     - default: constrained editorial width
   - [ ] Render caption only if present
   - [ ] Add reveal classes (consistent with Theme A pattern)

3. Add tests
   - [ ] Create `tests/themes/test_theme_a_image_block_rendering.py`
   - [ ] Assert:
     - template origin resolves to Theme A override
     - alt text appears
     - caption is conditional
     - full_width toggles expected wrapper class/marker

4. Rebase + regenerate theme assets if required
   - [ ] `git fetch origin && git rebase origin/develop`
   - [ ] If `main.css` / `.build_fingerprint` are dirty and CI expects them:
     - rebuild theme CSS using canonical theme build command
     - regenerate fingerprint
     - commit those files as a separate final commit

5. Run full checks
   - [ ] `pytest -q tests/themes/test_theme_a_image_block_rendering.py`
   - [ ] `make test`

## Testing Requirements
- [ ] Run: `pytest -q tests/themes/test_theme_a_image_block_rendering.py`
- [ ] Run: `make test`
- [ ] Expected: all green

## Documentation Updates
Update if changes affect:
- [ ] `blocks-reference.md` (not expected)
- [ ] `WIRING-INVENTORY.md` (not expected)
- [ ] `page-types-reference.md` (not expected)

## Deliverables
- [ ] Create `THEME-029_followup.md` containing:
  - Summary
  - Files modified/created
  - Test results
  - Any conflicts + how resolved
  - Whether assets were regenerated (and when)

## Commit & Push
- [ ] Stage: `git add -A`
- [ ] Commit: `feat(THEME-029): rewrite Theme A ImageBlock template`
- [ ] If assets regenerated, final commit: `chore(THEME-029): regenerate theme_a css artifacts`
- [ ] Push: `git push origin theme/theme-029-image-block`

## Verification
- [ ] `git status --porcelain` → empty or documented untracked only

## Recommended Agent
CriteriaSelectionModel: GPT-5.2 Codex  
Thinking: Standard  
Rationale: Template + conditional rendering + layout variant + test; needs minimal-diff discipline.
